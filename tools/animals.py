"""The animal roster: creative-menu group, behaviour role, what each one hunts and how it is tamed.

Roles
  passive    never attacks anything
  defensive  fights back when hurt (and protects its owner when tamed)
  hunter     hunts the prey listed, fights back when hurt
  apex       hunts the prey listed and attacks people (players, villagers, soldiers) within `humans` blocks
  egg        a laid egg that hatches; not in the creative menu
"""

NS = "worldanimals"

GROUPS = {
    "birds": "Birds",
    "big_cats": "Big Cats",
    "large_mammals": "Large Mammals",
    "small_mammals": "Small Mammals",
    "primates": "Primates",
    "reptiles": "Reptiles",
    "sea_life": "Sea Life",
    "bugs": "Insects & Bugs",
}

# prey sets (type families: vanilla ones plus the short names this pack gives its own animals)
SMALL = ["chicken", "rabbit", "frog", "parrot", "rat", "squirrel", "duck", "turkey", "kiwi", "raccoon", "erizo",
         "dove", "cyanocitta_cristata", "tucan"]
MID = ["sheep", "pig", "goat", "deer", "wild_boar", "kangaroo", "capuchin_monkeys", "flamingo"]
BIG = ["cow", "horse", "donkey", "mule", "llama", "camel", "zebra", "buffalo", "giraffe", "ostrich"]
FISH = ["fish", "squid", "lantern_fish", "shrimp"]
MARINE = ["seal", "dolphin", "turtle", "emperor_penguin", "penguin_african", "blue_penguin"]
SHARKS = ["shark", "white_shark", "tiger_shark", "hammerhead_shark"]
SNAKES = ["snake", "snake_coral"]
HUMANS = ["player", "villager", "wandering_trader", "illager", "war_soldier"]

# id: (group, role, prey, humans range, attack damage, tame food, display name)
ROSTER = {
    # ---- birds
    "dove": ("birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Dove"),
    "eagle": ("birds", "hunter", ["rabbit", "rat", "squirrel", "fish"], 0, 4, "minecraft:chicken", "Eagle"),
    "seagull": ("birds", "hunter", ["fish", "shrimp"], 0, 2, "minecraft:cod", "Seagull"),
    "pelican": ("birds", "hunter", ["fish"], 0, 2, "minecraft:cod", "Pelican"),
    "stork": ("birds", "passive", [], 0, 0, "minecraft:cod", "Stork"),
    "turkey": ("birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Turkey"),
    "vulture": ("birds", "passive", [], 0, 0, "minecraft:rotten_flesh", "Vulture"),
    "cyanocitta_cristata": ("birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Blue Jay"),
    "tucan": ("birds", "passive", [], 0, 0, "minecraft:melon_slice", "Toucan"),
    "flamingo": ("birds", "passive", [], 0, 0, "minecraft:cod", "Flamingo"),
    "duck": ("birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Duck"),
    "kiwi": ("birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Kiwi"),
    "ostrich": ("birds", "defensive", [], 0, 5, "minecraft:wheat", "Ostrich"),
    "emperor_penguin": ("birds", "passive", [], 0, 0, "minecraft:cod", "Emperor Penguin"),
    "penguin_african": ("birds", "passive", [], 0, 0, "minecraft:cod", "African Penguin"),
    "blue_penguin": ("birds", "passive", [], 0, 0, "minecraft:cod", "Blue Penguin"),
    # ---- big cats
    "lion": ("big_cats", "apex", SMALL + MID + BIG, 10, 8, "minecraft:beef", "Lion"),
    "white_lion": ("big_cats", "apex", SMALL + MID + BIG, 10, 8, "minecraft:beef", "White Lion"),
    "tiger": ("big_cats", "apex", SMALL + MID + BIG, 10, 9, "minecraft:beef", "Tiger"),
    "white_tiger": ("big_cats", "apex", SMALL + MID + BIG, 10, 9, "minecraft:beef", "White Tiger"),
    "leopard": ("big_cats", "apex", SMALL + MID, 8, 6, "minecraft:beef", "Leopard"),
    "panther": ("big_cats", "apex", SMALL + MID, 8, 6, "minecraft:beef", "Panther"),
    "cougar": ("big_cats", "hunter", SMALL + MID, 0, 6, "minecraft:beef", "Cougar"),
    "snow_leopard": ("big_cats", "hunter", SMALL + MID, 0, 6, "minecraft:mutton", "Snow Leopard"),
    "caracal": ("big_cats", "hunter", SMALL, 0, 4, "minecraft:chicken", "Caracal"),
    # ---- large mammals
    "african_elephant": ("large_mammals", "defensive", [], 0, 10, "minecraft:hay_block", "African Elephant"),
    "asian_elephant": ("large_mammals", "defensive", [], 0, 10, "minecraft:hay_block", "Asian Elephant"),
    "mammoth": ("large_mammals", "defensive", [], 0, 12, "minecraft:hay_block", "Mammoth"),
    "giraffe": ("large_mammals", "defensive", [], 0, 4, "minecraft:apple", "Giraffe"),
    "zebra": ("large_mammals", "defensive", [], 0, 3, "minecraft:wheat", "Zebra"),
    "buffalo": ("large_mammals", "defensive", [], 0, 6, "minecraft:wheat", "Buffalo"),
    "rhinoceros": ("large_mammals", "defensive", [], 0, 9, "minecraft:wheat", "Rhino"),
    "deer": ("large_mammals", "passive", [], 0, 0, "minecraft:apple", "Deer"),
    "kangaroo": ("large_mammals", "defensive", [], 0, 4, "minecraft:wheat", "Kangaroo"),
    "wild_boar": ("large_mammals", "defensive", [], 0, 4, "minecraft:carrot", "Wild Boar"),
    "hippopotamus": ("large_mammals", "apex", [], 8, 9, "minecraft:melon_slice", "Hippopotamus"),
    "bear": ("large_mammals", "apex", ["fish", "deer", "wild_boar", "sheep", "pig", "rabbit"], 8, 7, "minecraft:salmon", "Brown Bear"),
    "black_bear": ("large_mammals", "hunter", ["fish", "rabbit", "rat", "squirrel"], 0, 5, "minecraft:sweet_berries", "Black Bear"),
    "hyenas": ("large_mammals", "apex", SMALL + MID + ["zebra"], 8, 5, "minecraft:beef", "Hyena"),
    # ---- small mammals
    "red_panda": ("small_mammals", "passive", [], 0, 0, "minecraft:sweet_berries", "Red Panda"),
    "raccoon": ("small_mammals", "passive", [], 0, 0, "minecraft:sweet_berries", "Raccoon"),
    "squirrel": ("small_mammals", "passive", [], 0, 0, "minecraft:wheat_seeds", "Squirrel"),
    "rat": ("small_mammals", "passive", [], 0, 0, "minecraft:wheat_seeds", "Rat"),
    "erizo": ("small_mammals", "defensive", [], 0, 2, "minecraft:sweet_berries", "Hedgehog"),
    "ornitorrinco_original": ("small_mammals", "defensive", [], 0, 2, "minecraft:cod", "Platypus"),
    # ---- primates
    "gorilla": ("primates", "defensive", [], 0, 9, "minecraft:melon_slice", "Gorilla"),
    "chimpanzee": ("primates", "hunter", ["capuchin_monkeys", "rabbit"], 0, 5, "minecraft:melon_slice", "Chimpanzee"),
    "capuchin_monkeys": ("primates", "passive", [], 0, 0, "minecraft:melon_slice", "Capuchin Monkey"),
    # ---- reptiles
    "crocodile": ("reptiles", "apex", MID + BIG + FISH, 12, 9, "minecraft:chicken", "Crocodile"),
    "komodo_dragon": ("reptiles", "apex", SMALL + MID + ["buffalo"], 10, 7, "minecraft:chicken", "Komodo Dragon"),
    "iguana": ("reptiles", "passive", [], 0, 0, "minecraft:sweet_berries", "Iguana"),
    "snake": ("reptiles", "apex", SMALL, 4, 3, "minecraft:rabbit", "Snake"),
    "snake_coral": ("reptiles", "apex", SMALL, 4, 3, "minecraft:rabbit", "Coral Snake"),
    "snake_scarlet": ("reptiles", "hunter", SNAKES + ["rat", "frog"], 0, 2, "minecraft:rabbit", "Scarlet Kingsnake"),
    # ---- sea life
    "shark": ("sea_life", "apex", FISH + ["seal", "dolphin", "turtle"], 12, 7, "minecraft:cod", "Shark"),
    "white_shark": ("sea_life", "apex", FISH + MARINE, 14, 9, "minecraft:cod", "Great White Shark"),
    "tiger_shark": ("sea_life", "apex", FISH + ["seal", "dolphin", "turtle"], 12, 8, "minecraft:cod", "Tiger Shark"),
    "hammerhead_shark": ("sea_life", "hunter", FISH + ["stingray"], 0, 6, "minecraft:cod", "Hammerhead Shark"),
    "orca": ("sea_life", "hunter", FISH + MARINE + SHARKS, 0, 10, "minecraft:salmon", "Orca"),
    "ballena": ("sea_life", "passive", [], 0, 0, "minecraft:cod", "Whale"),
    "swordfish": ("sea_life", "hunter", FISH, 0, 5, "minecraft:cod", "Swordfish"),
    "stingray": ("sea_life", "defensive", [], 0, 3, "minecraft:cod", "Stingray"),
    "jellyfish_wa": ("sea_life", "defensive", [], 0, 2, "minecraft:cod", "Jellyfish"),
    "lantern_fish": ("sea_life", "passive", [], 0, 0, "minecraft:cod", "Lanternfish"),
    "shrimp": ("sea_life", "passive", [], 0, 0, "minecraft:kelp", "Shrimp"),
    "clam": ("sea_life", "passive", [], 0, 0, "minecraft:kelp", "Clam"),
    "crab": ("sea_life", "defensive", [], 0, 2, "minecraft:kelp", "Crab"),
    "seal": ("sea_life", "hunter", FISH, 0, 3, "minecraft:cod", "Seal"),
    # ---- insects & bugs
    "ant": ("bugs", "defensive", [], 0, 1, "minecraft:sugar", "Ant"),
    "butterfly": ("bugs", "passive", [], 0, 0, "minecraft:sugar", "Butterfly"),
    "lucienaga": ("bugs", "passive", [], 0, 0, "minecraft:sugar", "Firefly"),
    "snail": ("bugs", "passive", [], 0, 0, "minecraft:kelp", "Snail"),
    # ---- laid eggs (hatch into the animal; given by the parents, not in the creative menu)
    "duck_egg": (None, "egg", [], 0, 0, None, "Duck Egg"),
    "turkey_egg": (None, "egg", [], 0, 0, None, "Turkey Egg"),
    "ostrich_egg": (None, "egg", [], 0, 0, None, "Ostrich Egg"),
    "african_penguin_egg": (None, "egg", [], 0, 0, None, "African Penguin Egg"),
    "blue_penguin_egg": (None, "egg", [], 0, 0, None, "Blue Penguin Egg"),
    "emperor_penguin_egg": (None, "egg", [], 0, 0, None, "Emperor Penguin Egg"),
}

# removed on purpose
REMOVED_ENTITIES = {
    "camel": "removed by request",
    "pink_dolphin": "vanilla has the Dolphin",
    "land_turtle": "vanilla has the Turtle",
    "penguin": "generic scarf penguin; the three real penguin species stay",
    "real_penguin_egg": "egg of the removed generic penguin",
    "village_ice": "not an animal (trader village)",
    "village_wild": "not an animal (trader village)",
    "bag_items": "the stork's loot bag (dropped diamonds/netherite)",
}

# which parent lays which egg item
LAID_EGGS = {
    "duck_egg": "duck",
    "turkey_egg": "turkey",
    "ostrich_egg": "ostrich",
    "african_penguin_egg": "penguin_african",
    "blue_penguin_egg": "blue_penguin",
    "emperor_penguin_egg": "emperor_penguin",
}

# custom items of the old pack -> vanilla item (anything else custom is dropped)
ITEM_MAP = {
    "big_cat_saddle": "minecraft:saddle",
    "elephant_saddle": "minecraft:saddle",
    "giraffe_saddle": "minecraft:saddle",
    "ostrich_saddle": "minecraft:saddle",
    "iron_rhinoceros_saddle": "minecraft:saddle",
    "gold_bone_meal": "minecraft:bone_meal",
    "sugar_cubes": "minecraft:sugar",
    "raw_crab": "minecraft:cod",
    "shrimp_raw": "minecraft:cod",
    "lantern_fish_item": "minecraft:cod",
    "raw_duck": "minecraft:chicken",
    "raw_turkey": "minecraft:chicken",
    "raw_ostrich_leg": "minecraft:chicken",
    "raw_rat": "minecraft:rabbit",
    "reptil_skin": "minecraft:leather",
    "zebra_skin": "minecraft:leather",
    "shark_tooth": "minecraft:bone",
    "cheese": "minecraft:bread",
}
