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
    "essentials": "Essentials",
    "birds_of_prey": "Birds of Prey",
    "water_birds": "Water Birds",
    "land_birds": "Land & Tropical Birds",
    "flightless_birds": "Penguins & Flightless Birds",
    "big_cats": "Big Cats",
    "bears_hyenas": "Bears & Hyenas",
    "giants": "Elephants & Giants",
    "grazers": "Grazers & Hoofed Animals",
    "small_mammals": "Small Mammals",
    "primates": "Primates",
    "reptiles": "Reptiles & Turtles",
    "snakes": "Snakes",
    "sharks": "Sharks",
    "marine_mammals": "Whales, Dolphins & Seals",
    "fish": "Fish, Rays, Crabs & Jellyfish",
    "shellfish": "Crabs & Shellfish",
    "bugs": "Insects & Bugs",
}

# prey sets (type families: vanilla ones plus the short names this pack gives its own animals)
SMALL = ["chicken", "rabbit", "frog", "parrot", "rat", "squirrel", "duck", "turkey", "kiwi", "raccoon", "erizo",
         "dove", "cyanocitta_cristata", "tucan"]
MID = ["sheep", "pig", "goat", "deer", "wild_boar", "kangaroo", "capuchin_monkeys", "flamingo"]
BIG = ["cow", "horse", "donkey", "mule", "llama", "camel", "zebra", "buffalo", "giraffe", "ostrich"]
FISH = ["fish", "squid", "lantern_fish", "shrimp"]
MARINE = ["seal", "dolphin", "pink_dolphin", "penguin", "turtle", "emperor_penguin", "penguin_african", "blue_penguin"]
SHARKS = ["shark", "white_shark", "tiger_shark", "hammerhead_shark"]
SNAKES = ["snake", "snake_coral"]
# wild animals go for people, not War Engine soldiers (they still fight back if a soldier hurts them)
HUMANS = ["player", "villager", "wandering_trader", "illager"]

# the first group in the creative menu: the animals you reach for most
ESSENTIALS = ["lion", "moose", "tiger", "african_elephant", "gorilla", "white_shark", "bear", "crocodile", "rhinoceros",
              "giraffe", "zebra", "hippopotamus", "orca", "eagle", "emperor_penguin", "deer", "buffalo"]

# creative menu groups (after Essentials): the roster groups folded into a few categories
MENU_GROUPS = {
    "essentials": "Essentials",
    "dogs": "Dogs",
    "big_cats": "Big & Wild Cats",
    "bears_canids": "Bears, Wild Dogs & Hyenas",
    "grazers": "Hoofed Animals & Giants",
    "small_mammals": "Small Mammals & Primates",
    "water_birds": "Water Birds & Penguins",
    "land_birds": "Land Birds & Birds of Prey",
    "reptiles": "Crocodiles, Lizards & Turtles",
    "snakes": "Snakes",
    "sea_life": "Sea Life",
    "bugs": "Insects & Bugs",
}
MENU_OF = {
    "birds_of_prey": "land_birds", "water_birds": "water_birds", "land_birds": "land_birds",
    "flightless_birds": "water_birds", "seabirds": "water_birds", "songbirds": "land_birds", "game_birds": "land_birds",
    "big_cats": "big_cats", "wild_cats": "big_cats",
    "bears_hyenas": "bears_canids", "bears": "bears_canids", "wild_canids": "bears_canids",
    "giants": "grazers", "grazers": "grazers", "cattle": "grazers", "horses": "grazers", "pigs": "grazers",
    "deer": "grazers", "antelopes": "grazers",
    "small_mammals": "small_mammals", "primates": "small_mammals",
    "reptiles": "reptiles", "crocodilians": "reptiles", "lizards": "reptiles", "snakes": "snakes",
    "sharks": "sea_life", "fish": "sea_life", "shellfish": "sea_life",
    "marine_mammals": "sea_life", "whales": "sea_life",
    "bugs": "bugs", "dogs": "dogs",
}
MENU_FOR = {"kiwi": "land_birds", "ostrich": "land_birds"}

# natural spawning: off. Spawn them from the eggs.
NATURAL_SPAWNING = False

# id: (group, role, prey, humans range, attack damage, tame food, display name)
ROSTER = {
    # ---- birds
    "dove": ("land_birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Dove"),
    "eagle": ("birds_of_prey", "hunter", ["rabbit", "rat", "squirrel", "fish"], 0, 4, "minecraft:chicken", "Eagle"),
    "seagull": ("water_birds", "hunter", ["fish", "shrimp"], 0, 2, "minecraft:cod", "Seagull"),
    "pelican": ("water_birds", "hunter", ["fish"], 0, 2, "minecraft:cod", "Pelican"),
    "stork": ("water_birds", "passive", [], 0, 0, "minecraft:cod", "Stork"),
    "turkey": ("land_birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Turkey"),
    "vulture": ("birds_of_prey", "passive", [], 0, 0, "minecraft:rotten_flesh", "Vulture"),
    "cyanocitta_cristata": ("land_birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Blue Jay"),
    "tucan": ("land_birds", "passive", [], 0, 0, "minecraft:melon_slice", "Toucan"),
    "flamingo": ("water_birds", "passive", [], 0, 0, "minecraft:cod", "Flamingo"),
    "duck": ("water_birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Duck"),
    "kiwi": ("flightless_birds", "passive", [], 0, 0, "minecraft:wheat_seeds", "Kiwi"),
    "ostrich": ("flightless_birds", "defensive", [], 0, 5, "minecraft:wheat", "Ostrich"),
    "emperor_penguin": ("flightless_birds", "passive", [], 0, 0, "minecraft:cod", "Emperor Penguin"),
    "penguin_african": ("flightless_birds", "passive", [], 0, 0, "minecraft:cod", "African Penguin"),
    "blue_penguin": ("flightless_birds", "passive", [], 0, 0, "minecraft:cod", "Blue Penguin"),
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
    "african_elephant": ("giants", "defensive", [], 0, 10, "minecraft:hay_block", "African Elephant"),
    "asian_elephant": ("giants", "defensive", [], 0, 10, "minecraft:hay_block", "Asian Elephant"),
    "mammoth": ("giants", "defensive", [], 0, 12, "minecraft:hay_block", "Mammoth"),
    "giraffe": ("giants", "defensive", [], 0, 4, "minecraft:apple", "Giraffe"),
    "zebra": ("grazers", "defensive", [], 0, 3, "minecraft:wheat", "Zebra"),
    "buffalo": ("grazers", "defensive", [], 0, 6, "minecraft:wheat", "Buffalo"),
    "rhinoceros": ("giants", "defensive", [], 0, 9, "minecraft:wheat", "Rhino"),
    "deer": ("grazers", "passive", [], 0, 0, "minecraft:apple", "Deer"),
    "kangaroo": ("grazers", "defensive", [], 0, 4, "minecraft:wheat", "Kangaroo"),
    "wild_boar": ("grazers", "defensive", [], 0, 4, "minecraft:carrot", "Wild Boar"),
    "hippopotamus": ("giants", "apex", [], 8, 9, "minecraft:melon_slice", "Hippopotamus"),
    "bear": ("bears_hyenas", "apex", ["fish", "deer", "wild_boar", "sheep", "pig", "rabbit"], 8, 7, "minecraft:salmon", "Brown Bear"),
    "black_bear": ("bears_hyenas", "hunter", ["fish", "rabbit", "rat", "squirrel"], 0, 5, "minecraft:sweet_berries", "Black Bear"),
    "hyenas": ("bears_hyenas", "apex", SMALL + MID + ["zebra"], 8, 5, "minecraft:beef", "Hyena"),
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
    "snake": ("snakes", "apex", SMALL, 4, 3, "minecraft:rabbit", "Snake"),
    "snake_coral": ("snakes", "apex", SMALL, 4, 3, "minecraft:rabbit", "Coral Snake"),
    "snake_scarlet": ("snakes", "hunter", SNAKES + ["rat", "frog"], 0, 2, "minecraft:rabbit", "Scarlet Kingsnake"),
    # ---- sea life
    "shark": ("sharks", "apex", FISH + ["seal", "dolphin", "turtle"], 12, 7, "minecraft:cod", "Shark"),
    "white_shark": ("sharks", "apex", FISH + MARINE, 14, 9, "minecraft:cod", "Great White Shark"),
    "tiger_shark": ("sharks", "apex", FISH + ["seal", "dolphin", "turtle"], 12, 8, "minecraft:cod", "Tiger Shark"),
    "hammerhead_shark": ("sharks", "hunter", FISH + ["stingray"], 0, 6, "minecraft:cod", "Hammerhead Shark"),
    "orca": ("marine_mammals", "hunter", FISH + MARINE + SHARKS, 0, 10, "minecraft:salmon", "Orca"),
    "ballena": ("marine_mammals", "passive", [], 0, 0, "minecraft:cod", "Whale"),
    "swordfish": ("fish", "hunter", FISH, 0, 5, "minecraft:cod", "Swordfish"),
    "stingray": ("fish", "defensive", [], 0, 3, "minecraft:cod", "Stingray"),
    "jellyfish_wa": ("fish", "defensive", [], 0, 2, "minecraft:cod", "Jellyfish"),
    "lantern_fish": ("fish", "passive", [], 0, 0, "minecraft:cod", "Lanternfish"),
    "shrimp": ("shellfish", "passive", [], 0, 0, "minecraft:kelp", "Shrimp"),
    "clam": ("shellfish", "passive", [], 0, 0, "minecraft:kelp", "Clam"),
    "crab": ("fish", "defensive", [], 0, 2, "minecraft:kelp", "Crab"),
    "seal": ("marine_mammals", "hunter", FISH, 0, 3, "minecraft:cod", "Seal"),
    # ---- insects & bugs
    "ant": ("bugs", "defensive", [], 0, 1, "minecraft:sugar", "Ant"),
    "butterfly": ("bugs", "passive", [], 0, 0, "minecraft:sugar", "Butterfly"),
    "lucienaga": ("bugs", "passive", [], 0, 0, "minecraft:sugar", "Firefly"),
    "snail": ("bugs", "passive", [], 0, 0, "minecraft:kelp", "Snail"),
    # ---- restored: in the original pack
    "penguin": ("flightless_birds", "passive", [], 0, 0, "minecraft:cod", "Penguin"),
    "hyenas_2": ("bears_hyenas", "apex", SMALL + MID + ["zebra"], 8, 5, "minecraft:beef", "Gray Hyena"),
    "land_turtle": ("reptiles", "passive", [], 0, 0, "minecraft:melon_slice", "Land Turtle"),
    "pink_dolphin": ("marine_mammals", "hunter", FISH, 0, 3, "minecraft:cod", "Pink Dolphin"),
    # ---- laid eggs (hatch into the animal; given by the parents, not in the creative menu)
    "duck_egg": (None, "egg", [], 0, 0, None, "Duck Egg"),
    "turkey_egg": (None, "egg", [], 0, 0, None, "Turkey Egg"),
    "ostrich_egg": (None, "egg", [], 0, 0, None, "Ostrich Egg"),
    "african_penguin_egg": (None, "egg", [], 0, 0, None, "African Penguin Egg"),
    "blue_penguin_egg": (None, "egg", [], 0, 0, None, "Blue Penguin Egg"),
    "emperor_penguin_egg": (None, "egg", [], 0, 0, None, "Emperor Penguin Egg"),
    "real_penguin_egg": (None, "egg", [], 0, 0, None, "Penguin Egg"),
}

# cut as filler (they stay in ROSTER so putting one back is just deleting its line here)
CUT = {
    "penguin": "generic scarf penguin; African, Blue and Emperor penguins stay",
    "real_penguin_egg": "egg of the generic penguin",
    "hyenas_2": "Gray Hyena is a recolor of the Hyena",
    "pink_dolphin": "vanilla has the Dolphin",
    "land_turtle": "vanilla has the Turtle",
    "shark": "generic shark; Great White, Tiger and Hammerhead stay",
    "clam": "just sits there",
    "shrimp": "tiny, does nothing",
    "snail": "tiny, does nothing",
    "ant": "tiny, does nothing",
    "lantern_fish": "tiny, does nothing",
}

# removed on purpose
REMOVED_ENTITIES = {
    "camel": "removed by request",
    "village_ice": "not an animal (trader village)",
    "village_wild": "not an animal (trader village)",
    "bag_items": "the stork's loot bag (dropped diamonds/netherite)",
}

# animals the original pack had a model and textures for but no behaviour file: built from a sibling
CLONES = {"hyenas_2": "hyenas"}

# which parent lays which egg item
LAID_EGGS = {
    "duck_egg": "duck",
    "turkey_egg": "turkey",
    "ostrich_egg": "ostrich",
    "african_penguin_egg": "penguin_african",
    "blue_penguin_egg": "blue_penguin",
    "emperor_penguin_egg": "emperor_penguin",
    "real_penguin_egg": "penguin",
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
