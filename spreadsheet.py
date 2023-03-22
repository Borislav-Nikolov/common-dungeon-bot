
import os.path
import magicshop
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

spreadsheet = '1nnB8VmIUtkYCIQXcaQIsEHj10K7OkELYRloSJmbK-Ow'
randomized_item_list_spreadsheet_range = 'Magic Shop'
full_item_list_spreadsheet_range = 'Magic Items'


def write_items_from_spreadsheet():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet,
                                    range=full_item_list_spreadsheet_range).execute()
        rows = result.get('values', [])

        if not rows:
            print('No data found.')

        write_items_to_json_file('items2.json', rows)
    except HttpError as err:
        print(err)


def write_items_to_json_file(json_file_name, rows):
    with open(json_file_name, 'w', encoding='utf-8') as items_file_write:
        items_file_write.write('{')
        item_id = 1
        for row in rows:
            if len(row) >= 6:
                items_file_write.write(f'"{item_id}":')
                items_file_write.write('{')
                attunement = 'true' if row[3].lower() == 'yes' else 'false'
                items_file_write.write(
                    f'"{magicshop.ITEM_FIELD_NAME}":"{row[0]}",'
                    f'"{magicshop.ITEM_FIELD_PRICE}":"{row[1]}",'
                    f'"{magicshop.ITEM_FIELD_RARITY}":"{row[2]}",'
                    f'"{magicshop.ITEM_FIELD_ATTUNEMENT}":{attunement},'
                    f'"{magicshop.ITEM_FIELD_RARITY_LEVEL}":"{row[5]}",'
                    f'"{magicshop.ITEM_FIELD_OFFICIAL}":true,'
                    f'"{magicshop.ITEM_FIELD_BANNED}":false'
                )
                if len(row) >= 9:
                    description = row[8].replace('\\', '')
                    description = description.replace('\n', '\\n')
                    description = description.replace('"', '\\"')
                    items_file_write.write(f',"{magicshop.ITEM_FIELD_DESCRIPTION}":"{description}"')
                items_file_write.write('}')
                if rows[len(rows) - 1] != row:
                    items_file_write.write(',')
                item_id += 1

        add_items_not_in_spreadsheet(items_file_write, item_id)
        items_file_write.write('}')


def add_items_not_in_spreadsheet(items_file_write, item_id: int):
    items_file_write.write(',')

    price_50 = "50 gp"
    price_25 = "25 gp"
    common_str = "Common"
    minor_str = "MINOR"
    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Potion of Healing",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="You regain 2d4 + 2 hit points when you drink this potion.\\n\\n"
                        "• The potion's red liquid glimmers when agitated.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Armor of Gleaming",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This armor never gets dirty.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Bead of Nourishment",
            price=price_25,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This spongy, flavorless, gelatinous bead dissolves on your tongue and provides as much nourishment as 1 day of rations.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Bead of Refreshment",
            price=price_25,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This spongy, flavorless, gelatinous bead dissolves in liquid, transforming up to a pint of the liquid into fresh, cold drinking water. The bead has no effect on magical liquids or harmful substances such as poison.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Boots of False Tracks",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="Only humanoids can wear these boots. While wearing the boots, you can choose to have them leave tracks like those of another kind of humanoid of your size.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Candle of the Deep",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="The flame of this candle is not extinguished when immersed in water. It gives off light and heat like a normal candle.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Cast-Off Armor",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="You can doff this armor as an action.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Charlatan's Die",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="Whenever you roll this six-sided die, you can control which number it rolls.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Cloak of Billowing",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While wearing this cloak, you can use a bonus action to make it billow dramatically.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Cloak of Many Fashions",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While wearing this cloak, you can use a bonus action to change the style, color, and apparent quality of the garment. The cloak's weight doesn't change. Regardless of its appearance, the cloak can't be anything but a cloak. Although it can duplicate the appearance of other magic cloaks, it doesn't gain their magical properties.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Clockwork Amulet",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This copper amulet contains tiny interlocking gears and is powered by magic from Mechanus, a plane of clockwork predictability. A creature that puts an ear to the amulet can hear faint ticking and whirring noises coming from within.\\n\\nWhen you make an attack roll while wearing the amulet, you can forgo rolling the d20 to get a 10 on the die. Once used, this property can't be used again until the next dawn.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Clothes of Mending",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This elegant outfit of traveler's clothes magically mends itself to counteract daily wear and tear. Pieces of the outfit that are destroyed can't be repaired in this way.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Dark Shard Amulet",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="This amulet is fashioned from a single shard of resilient extraplanar material originating from the realm of your warlock patron. While you are wearing it, you gain the following benefits:\\n\\n• You can use the amulet as a spellcasting focus for your warlock spells.\\n\\n• You can try to cast a cantrip that you don't know. The cantrip must be on the Warlock spell list, and you must make a DC 10 Intelligence (Arcana) check. If the check succeeds, you cast the spell. If the check fails, so does the spell, and the action used to cast the spell is wasted. In either case, you can't use this property again until you finish a long rest.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Dread Helm",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This fearsome steel helm makes your eyes glow red while you wear it.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Ear Horn of Hearing",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While held up to your ear, this horn suppresses the effects of the deafened condition on you, allowing you to hear normally.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Enduring Spellbook",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This spellbook, along with anything written on its pages, can't be damaged by fire or immersion in water. In addition, the spellbook doesn't deteriorate with age.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Ersatz Eye",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="This artificial eye replaces a real one that was lost or removed. While the ersatz eye is embedded in your eye socket, it can't be removed by anyone other than you, and you can see through the tiny orb as though it were a normal eye.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Hat of Vermin",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This hat has 3 charges. While holding the hat, you can use an action to expend 1 of its charges and speak a command word that summons your choice of a bat, a frog, or a rat (see the Player's Handbook or the Monster Manual for statistics). The summoned creature magically appears in the hat and tries to get away from you as quickly as possible. The creature is neither friendly nor hostile, and it isn't under your control. It behaves as an ordinary creature of its kind and disappears after 1 hour or when it drops to 0 hit points. The hat regains all expended charges daily at dawn.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Hat of Wizardry",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="This antiquated, cone-shaped hat is adorned with gold crescent moons and stars. While you are wearing it, you gain the following benefits:\\n\\n• You can use the hat as a spellcasting focus for your wizard spells.\\n\\n• You can try to cast a cantrip that you don't know. The cantrip must be on the Wizard spell list, and you must make a DC 10 Intelligence (Arcana) check. If the check succeeds, you cast the spell. If the check fails, so does the spell, and the action used to cast the spell is wasted. In either case, you can't use this property again until you finish a long rest.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Heward's Handy Spice Pouch",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This belt pouch appears empty and has 10 charges. While holding the pouch, you can use an action to expend 1 of its charges, speak the name of any nonmagical food seasoning (such as salt, pepper, saffron, or cilantro), and remove a pinch of the desired seasoning from the pouch. A pinch is enough to season a single meal. The pouch regains 1d6 + 4 expended charges daily at dawn.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Horn of Silent Alarm",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This horn has 4 charges. When you use an action to blow it, one creature of your choice can hear the horn's blare, provided the creature is within 600 feet of the horn and not deafened. No other creature hears sound coming from the horn. The horn regains 1d4 expended charges daily at dawn.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Instrument of Illusions",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="While you are playing this musical instrument, you can create harmless, illusory visual effects within a 5-foot-radius sphere centered on the instrument. If you are a bard, the radius increases to 15 feet. Sample visual effects include luminous musical notes, a spectral dancer, butterflies, and gently falling snow. The magical effects have neither substance nor sound, and they are obviously illusory. The effects end when you stop playing.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Instrument of Scribing",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="This musical instrument has 3 charges. While you are playing it, you can use an action to expend 1 charge from the instrument and write a magical message on a nonmagical object or surface that you can see within 30 feet of you. The message can be up to six words long and is written in a language you know. If you are a bard, you can scribe an additional seven words and choose to make the message glow faintly, allowing it to be seen in nonmagical darkness. Casting Dispel Magic on the message erases it. Otherwise, the message fades away after 24 hours.\\n\\nThe instrument regains all expended charges daily at dawn.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Lock of Trickery",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This lock appears to be an ordinary lock (of the type described in chapter 5 of the Player's Handbook) and comes with a single key. The tumblers in this lock magically adjust to thwart burglars. Dexterity checks made to pick the lock have disadvantage.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Moon-Touched Sword",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="In darkness, the unsheathed blade of this sword sheds moonlight, creating bright light in a 15-foot radius and dim light for an additional 15 feet.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Mystery Key",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="A question mark is worked into the head of this key. The key has a 5 percent chance of unlocking any lock into which it's inserted. Once it unlocks something, the key disappears.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Orb of Direction",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While holding this orb, you can use an action to determine which way is north. This property functions only on the Material Plane.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="Orb of Time",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While holding this orb, you can use an action to determine whether it is morning, afternoon, evening, or nighttime outside. This property functions only on the Material Plane.",
            last_item=False
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=
        )
    )
    item_id += 1

    items_file_write.write(
        create_json_item_string(
            item_id=item_id,
            name="",
            price="",
            rarity="",
            rarity_level="",
            attunement=,
            official=,
            banned=,
            description="",
            last_item=True
        )
    )
    item_id += 1


def create_json_item_string(
        item_id: int,
        name: str,
        price: str,
        rarity: str,
        rarity_level,
        attunement: bool,
        official: bool,
        banned: bool,
        description: str,
        last_item: bool
) -> str:
    return f'"{item_id}":' + '{' + f'"{magicshop.ITEM_FIELD_NAME}":"{name}",' \
                 f'"{magicshop.ITEM_FIELD_PRICE}":"{price}",' \
                 f'"{magicshop.ITEM_FIELD_RARITY}":"{rarity}",' \
                 f'"{magicshop.ITEM_FIELD_RARITY_LEVEL}":"{rarity_level}",' \
                 f'"{magicshop.ITEM_FIELD_ATTUNEMENT}":{"true" if attunement else "false"},' \
                 f'"{magicshop.ITEM_FIELD_OFFICIAL}":{"true" if official else "false"},' \
                 f'"{magicshop.ITEM_FIELD_BANNED}":{"true" if banned else "false"}' \
                 f',"{magicshop.ITEM_FIELD_DESCRIPTION}":"{description}"' \
                 '}' \
                 f'{"" if last_item else ","}'
