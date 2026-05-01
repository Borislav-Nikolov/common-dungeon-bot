# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Discord bot for a D&D server. Front-end of a two-tier system: this bot handles Discord I/O; persistence/business logic lives in a separate backend service (`common-dnd-backend`, hosted on Fly.io). No local DB — all state goes through HTTP + a Socket.IO channel to that backend.

## Run / develop

No `requirements.txt` or `pyproject.toml`. Dependencies are declared only in `Dockerfile`:

```
discord.py python-dotenv google-api-python-client google-auth-httplib2 \
google-auth-oauthlib firebase_admin requests python-socketio websocket-client pillow
```

Python 3.12. Entry point: `python main.py` (Docker `CMD python -u ./main.py`).

Required env vars (loaded via `python-dotenv`, see `main.py` + `api/base.py`):
- `TEST_TOKEN` — Discord bot token (currently always used; `is_test` is hardcoded `True` in `main.py`).
- `TEST_ALLOWED_GUILD_ID` — only this guild responds to messages/reactions.
- `BACKEND_SECRET` / `TEST_BACKEND_SECRET` — bearer token for backend (`api/base.py:get_secret`).
- `FIREBASE_PROJECT` — read in `main.py` but not currently consumed.

Backend endpoint is selected in `api/base.init_api(test, local)`. `main.py` calls it with `local=True`, pointing at `http://localhost:8081/`. Toggle to hit `common-dnd-backend-test.fly.dev` / `common-dnd-backend.fly.dev` by changing the call.

`fly.toml` deploys to Fly.io app `common-dungeon-app`.

No tests, no linter config.

## Architecture

Strict layering. Imports flow downward only — never up.

```
bot.py / main.py
  └── commands/        Discord command handlers ($cmd parsing) + reactions handlers
        └── controller/  Business logic / orchestration
              └── provider/  Domain-object assembly (dict ↔ model.* objects)
                    └── source/    Thin pass-through to api/ (the seam where remote vs. local could swap)
                          └── api/   HTTP requests to backend + Socket.IO client
  └── bridge/         Long-lived Discord state syncers (re-init messages on (re)connect, socket-driven refreshes)
  └── listener/       Passive message observers (e.g. Apollo bot output)
  └── ui/             discord.py Views / Buttons / Modals
  └── model/          Plain data classes (Player, Character, Item, Rarity, etc.)
  └── util/           Stateless helpers (botutils, itemutils, timeutils, requestutils)
```

Key flow patterns:

- **Commands**: `bot.on_message` dispatches `$`-prefixed messages through `handle_*` chains in `commands/` (see `bot.py:65-82`). Each handler returns `bool` indicating whether it consumed the message — order matters, first match wins.
- **Reactions**: `bot.on_raw_reaction_add` routes by channel id (shop / static shop / DM / posts section) to the matching `*reactions.py` module.
- **Backend calls**: every `api/*requests.py` module wraps `requests.{get,post,...}` with `api.base.api_url(...)` + `get_bearer_token_headers()`. Source layer (`source/`) exists so providers don't import `api/` directly.
- **Real-time updates**: `api/sockets.py` exposes a global `socketio.Client` `sio`. Bridges register `@sio.on(...)` handlers (e.g. `charactersbridge.on_refresh_player_messages_event`) and bounce work onto the bot loop via `asyncio.run_coroutine_threadsafe(..., bot.client.loop)` because the socket fires from a non-asyncio thread.
- **Bridges restore Discord-side state**: on `on_ready` / `on_resumed`, `consolebridge.reinitialize_console_messages` and `charactersbridge.reinitialize_character_messages` re-attach views/messages. Anything that needs to survive a reconnect goes here.

## Conventions specific to this repo

- `model/` classes are dumb data holders. Field-name strings live in `source/sourcefields.py` — use those constants (e.g. `PLAYER_FIELD_COMMON_TOKENS`) when building dicts for backend payloads, never raw strings.
- Permission checks: `util/botutils.py` — `is_admin_message`, `is_moderator_or_admin_message`, `is_shop_channel`, etc. Gate admin commands with these, not by hand-rolling role checks.
- `bot.client` is a module-level global imported by bridges (e.g. `import bot; bot.client.loop`). Keep it that way for socket-thread → bot-loop dispatch.
- Guild allowlist: `bot.on_message` / `on_raw_reaction_add` early-return if `guild.id != allowed_guild_id`. New event handlers must do the same.
- Local JSON files at the root (`items.json`, `characters.json`, `new_items.json`, `filtered_items.json`, `items_update.json`, `items2.json`) are scratch/migration data, not runtime state. `credentials.json` / `serviceAccountKey.json` / `token.json` are secrets — do not commit edits to them.
