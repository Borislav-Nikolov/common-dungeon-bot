
import os.path
from controller import magicshop
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
        items_file_write.write('[')
        for row in rows:
            if len(row) >= 6:
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

        add_items_not_in_spreadsheet(items_file_write)
        items_file_write.write(']')


def add_items_not_in_spreadsheet(items_file_write):
    items_file_write.write(',')

    price_50 = "50 gp"
    price_25 = "25 gp"
    common_str = "Common"
    minor_str = "MINOR"
    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
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

    items_file_write.write(
        create_json_item_string(
            name="Perfume of Bewitching",
            price=price_25,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This tiny vial contains magic perfume, enough for one use. You can use an action to apply the perfume to yourself, and its effect lasts 1 hour. For the duration, you have advantage on all Charisma checks directed at humanoids of challenge rating 1 or lower. Those subjected to the perfume's effect are not aware that they've been influenced by magic.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Pipe of Smoke Monsters",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While smoking this pipe, you can use an action to exhale a puff of smoke that takes the form of a single creature, such as a dragon, a flumph, or a froghemoth. The form must be small enough to fit in a 1-foot cube and loses its shape after a few seconds, becoming an ordinary puff of smoke.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Pole of Angling",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While holding this 10-foot pole, you can speak a command word and transform it into a fishing pole with a hook, a line, and a reel. Speaking the command word again changes the fishing pole back into a normal 10-foot pole.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Pole of Collapsing",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="While holding this 10-foot pole, you can use an action to speak a command word and cause it to collapse into a 1-foot-long rod, for ease of storage. The pole's weight doesn't change. You can use an action to speak a different command word and cause the rod to revert to a pole; however, the rod will elongate only as far as the surrounding space allows.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Pot of Awakening",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="If you plant an ordinary shrub in this 10-pound clay pot and let it grow for 30 days, the shrub magically transforms into an awakened shrub (see the Monster Manual for statistics) at the end of that time. When the shrub awakens, its roots break the pot, destroying it.\\n\\nThe awakened shrub is friendly toward you. Absent commands from you, it does nothing.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Rope of Mending",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="You can cut this 50-foot coil of hempen rope into any number of smaller pieces, and then use an action to speak a command word and cause the pieces to knit back together. The pieces must be in contact with each other and not otherwise in use. A rope of mending is forever shortened if a section of it is lost or destroyed.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Ruby of the War Mage",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="Etched with eldritch runes, this 1-inch-diameter ruby allows you to use a simple or martial weapon as a spellcasting focus for your spells. For this property to work, you must attach the ruby to the weapon by pressing the ruby against it for at least 10 minutes. Thereafter, the ruby can't be removed unless you detach it as an action or the weapon is destroyed. Not even an Antimagic Field causes it to fall off. The ruby does fall off the weapon if your attunement to the ruby ends.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Shield of Expression",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="The front of this shield is shaped in the likeness of a face. While bearing the shield, you can use a bonus action to alter the face's expression.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Smoldering Armor",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="Wisps of harmless, odorless smoke rise from this armor while it is worn.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Staff of Adornment",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="If you place an object weighing no more than 1 pound (such as a shard of crystal, an egg, or a stone) above the tip of the staff while holding it, the object floats an inch from the staff's tip and remains there until it is removed or until the staff is no longer in your possession. The staff can have up to three such objects floating over its tip at any given time. While holding the staff, you can make one or more of the objects slowly spin or turn in place.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Staff of Birdcalls",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This wooden staff is decorated with bird carvings. It has 10 charges. While holding it, you can use an action to expend 1 charge from the staff and cause it to create one of the following sounds out to a range of 60 feet: a finch's chirp, a raven's caw, a duck's quack, a chicken's cluck, a goose's honk, a loon's call, a turkey's gobble, a seagull's cry, an owl's hoot, or an eagle's shriek.\\n\\nThe staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff explodes in a harmless cloud of bird feathers and is lost forever.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Staff of Flowers",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This wooden staff has 10 charges. While holding it, you can use an action to expend 1 charge from the staff and cause a flower to sprout from a patch of earth or soil within 5 feet of you, or from the staff itself. Unless you choose a specific kind of flower, the staff creates a mild-scented daisy. The flower is harmless and nonmagical, and it grows or withers as a normal flower would.\\n\\nThe staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff turns into flower petals and is lost forever.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Talking Doll",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=True,
            official=True,
            banned=False,
            description="While this stuffed doll is within 5 feet of you, you can spend a short rest telling it to say up to six phrases, none of which can be more than six words long, and set a condition under which the doll speaks each phrase. You can also replace old phrases with new ones. Whatever the condition, it must occur within 5 feet of the doll to make it speak. For example, whenever someone picks up the doll, it might say, 'I want a piece of candy.' The doll's phrases are lost when your attunement to the doll ends.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Tankard of Sobriety",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This tankard has a stern face sculpted into one side. You can drink ale, wine, or any other nonmagical alcoholic beverage poured into it without becoming inebriated. The tankard has no effect on magical liquids or harmful substances such as poison.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Unbreakable Arrow",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This arrow can't be broken, except when it is within an Antimagic Field.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Veteran's Cane",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="When you grasp this walking cane and use a bonus action to speak the command word, it transforms into an ordinary longsword and ceases to be magical.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Walloping Ammunition",
            price=price_25,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This ammunition packs a wallop. A creature hit by the ammunition must succeed on a DC 10 Strength saving throw or be knocked prone.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Wand of Conducting",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This wand has 3 charges. While holding it, you can use an action to expend 1 of its charges and create orchestral music by waving it around. The music can be heard out to a range of 60 feet and ends when you stop waving the wand.\\n\\nThe wand regains all expended charges daily at dawn. If you expend the wand's last charge, roll a d20. On a 1, a sad tuba sound plays as the wand crumbles to dust and is destroyed.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Wand of Pyrotechnics",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This wand has 7 charges. While holding it, you can use an action to expend 1 of its charges and create a harmless burst of multicolored light at a point you can see up to 60 feet away. The burst of light is accompanied by a crackling noise that can be heard up to 300 feet away. The light is as bright as a torch flame but lasts only a second.\\n\\nThe wand regains 1d6 + 1 expended charges daily at dawn. If you expend the wand's last charge, roll a d20. On a 1, the wand erupts in a harmless pyrotechnic display and is destroyed.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Wand of Scowls",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This wand has 3 charges. While holding it, you can use an action to expend 1 of its charges and target a humanoid you can see within 30 feet of you. The target must succeed on a DC 10 Charisma saving throw or be forced to scowl for 1 minute.\\n\\nThe wand regains all expended charges daily at dawn. If you expend the wand's last charge, roll a d20. On a 1, the wand transforms into a Wand of Smiles.",
            last_item=False
        )
    )

    items_file_write.write(
        create_json_item_string(
            name="Wand of Smiles",
            price=price_50,
            rarity=common_str,
            rarity_level=minor_str,
            attunement=False,
            official=True,
            banned=False,
            description="This wand has 3 charges. While holding it, you can use an action to expend 1 of its charges and target a humanoid you can see within 30 feet of you. The target must succeed on a DC 10 Charisma saving throw or be forced to smile for 1 minute.\\n\\nThe wand regains all expended charges daily at dawn. If you expend the wand's last charge, roll a d20. On a 1, the wand transforms into a Wand of Scowls.",
            last_item=True
        )
    )


def create_json_item_string(
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
    return '{' + f'"{magicshop.ITEM_FIELD_NAME}":"{name}",' \
                 f'"{magicshop.ITEM_FIELD_PRICE}":"{price}",' \
                 f'"{magicshop.ITEM_FIELD_RARITY}":"{rarity}",' \
                 f'"{magicshop.ITEM_FIELD_RARITY_LEVEL}":"{rarity_level}",' \
                 f'"{magicshop.ITEM_FIELD_ATTUNEMENT}":{"true" if attunement else "false"},' \
                 f'"{magicshop.ITEM_FIELD_OFFICIAL}":{"true" if official else "false"},' \
                 f'"{magicshop.ITEM_FIELD_BANNED}":{"true" if banned else "false"}' \
                 f',"{magicshop.ITEM_FIELD_DESCRIPTION}":"{description}"' \
                 '}' \
                 f'{"" if last_item else ","}'
