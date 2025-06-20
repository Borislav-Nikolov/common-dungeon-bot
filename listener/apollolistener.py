import discord
import re
import datetime
import aiohttp
from PIL import Image
import io

APOLLO_USER_ID = 475744554910351370

UNIX_RE = re.compile(r"<t:(\d+):")


def _extract_start_end(time_field_value: str) -> tuple[datetime.datetime, datetime.datetime]:
    unix = UNIX_RE.findall(time_field_value)
    if len(unix) < 1:
        raise ValueError(" No <t: > tokens found in Time field.")

    start_dt = datetime.datetime.fromtimestamp(int(unix[0]), tz=datetime.timezone.utc)
    end_dt = (datetime.datetime.fromtimestamp(int(unix[1]), tz=datetime.timezone.utc)
              if len(unix) > 1 else start_dt + datetime.timedelta(hours=2))

    return start_dt, end_dt


async def _fetch_image(url: str) -> bytes | None:
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            if r.status != 200:
                return None
            return await r.read()


def _prepare_cover(raw: bytes) -> bytes:
    with Image.open(io.BytesIO(raw)) as im:
        im = im.convert("RGBA")
        im.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        x = (1024 - im.width) // 2
        y = (1024 - im.height) // 2
        canvas.paste(im, (x, y))
        buff = io.BytesIO()
        canvas.save(buff, format="PNG")
        return buff.getvalue()


async def check_for_apollo_message(message: discord.Message) -> bool:
    print(message.author.id)
    if message.author.id != APOLLO_USER_ID or not message.embeds:
        print('not apollo or no embeds')
        return False

    embed = message.embeds[0]
    time_field_value = None
    for field in embed.fields:
        if field.name == "Time":
            time_field_value = field.value
            break

    if not time_field_value:
        raise ValueError("No Time field found in embed.")

    start_dt, end_dt = _extract_start_end(time_field_value)

    name = embed.title or "Next Adventure"
    description = embed.description or ""

    guild = message.guild

    cover_url = embed.image.url or embed.thumbnail.url
    image_bytes = None
    if cover_url:
        raw = await _fetch_image(cover_url)
        if raw:
            image_bytes = _prepare_cover(raw)

    await guild.create_scheduled_event(
        name=name[:100],
        description=description[:1000],
        start_time=start_dt,
        end_time=end_dt,
        location=str(message.jump_url),
        image=image_bytes,
        entity_type=discord.EntityType.external,
        privacy_level=discord.PrivacyLevel.guild_only   # type: ignore[arg-type]
    )

    return True
