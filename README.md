# World Animals v2.2 (cleaned up)

A cleaned-up rebuild of the World Animals add-on (originally by ArathNido): animals only, sorted by type, with
smarter hunting, and tamed animals that fight on your side in [War Engine](https://github.com/Joeishelping/Minecraft-War-Mod).

Install `dist/World_Animals_v2_2.mcaddon`. It needs Minecraft Bedrock 1.21.90 or newer. In an existing world it
replaces the old version, because it keeps the same pack IDs. Remove the old **[Structure generation]** pack from
the world: it's gone.

## Spawn eggs, by type

66 animals, in the creative menu's **Nature** tab, in 16 collapsible groups:

| Group | Animals |
|---|---|
| Birds of Prey | Eagle, Vulture |
| Water Birds | Duck, Flamingo, Pelican, Seagull, Stork |
| Land & Tropical Birds | Blue Jay, Dove, Toucan, Turkey |
| Penguins & Flightless Birds | African Penguin, Blue Penguin, Emperor Penguin, Kiwi, Ostrich |
| Big Cats | Caracal, Cougar, Leopard, Lion, Panther, Snow Leopard, Tiger, White Lion, White Tiger |
| Bears & Hyenas | Black Bear, Brown Bear, Hyena |
| Elephants & Giants | African Elephant, Asian Elephant, Giraffe, Hippopotamus, Mammoth, Rhino |
| Grazers & Hoofed Animals | Buffalo, Deer, Kangaroo, Wild Boar, Zebra |
| Small Mammals | Hedgehog, Platypus, Raccoon, Rat, Red Panda, Squirrel |
| Primates | Capuchin Monkey, Chimpanzee, Gorilla |
| Reptiles & Turtles | Crocodile, Iguana, Komodo Dragon |
| Snakes | Coral Snake, Scarlet Kingsnake, Snake |
| Sharks | Great White Shark, Hammerhead Shark, Tiger Shark |
| Whales, Dolphins & Seals | Orca, Seal, Whale |
| Fish, Rays, Crabs & Jellyfish | Crab, Jellyfish, Stingray, Swordfish |
| Insects & Bugs | Butterfly, Firefly |

Blue Crab and Blue Iguana are color variants of the Crab and Iguana. Laid eggs (duck, turkey, ostrich, penguins)
still drop from the parents and hatch, but they aren't in the menu.

### Cut as filler (say the word and any of them comes back)

| Animal | Why |
|---|---|
| Penguin | generic scarf penguin; African, Blue and Emperor penguins stay |
| Gray Hyena | Gray Hyena is a recolor of the Hyena |
| Pink Dolphin | vanilla has the Dolphin |
| Land Turtle | vanilla has the Turtle |
| Shark | generic shark; Great White, Tiger and Hammerhead stay |
| Clam | just sits there |
| Shrimp | tiny, does nothing |
| Snail | tiny, does nothing |
| Ant | tiny, does nothing |
| Lanternfish | tiny, does nothing |

## How they behave

- **Dangerous predators** hunt prey **and** attack people (players, villagers, illagers, War Engine soldiers) who
  come close: Lion, White Lion, Tiger, White Tiger, Leopard, Panther, Brown Bear, Hyena, Hippopotamus, Crocodile,
  Komodo Dragon, Snake, Coral Snake, Great White Shark, Tiger Shark.
- **Hunters** go after their prey but leave people alone unless hurt: Cougar, Snow Leopard, Caracal, Black Bear,
  Chimpanzee (hunts capuchins), Eagle, Pelican, Seagull, Seal, Orca, Hammerhead, Swordfish, Scarlet Kingsnake (eats
  other snakes).
- **Defensive animals** fight back when hurt: elephants, mammoth, rhino, buffalo, giraffe, zebra, kangaroo, wild
  boar, ostrich, gorilla, hedgehog, platypus, crab, stingray, jellyfish. Herd animals call the herd.
- Everything else is passive.
- **Soldiers fight back.** War Engine soldiers only react to mobs of the `monster` family, so an animal carries
  `monster` while it is attacking something (and soldiers within 9 blocks of it shoot), and drops it once it has
  no target. A tamed animal never has it, so your own soldiers never shoot your pets.
- Prey is real prey: zebras, deer, buffalo, sheep, pigs, cows, horses, rabbits, chickens, fish, squid, seals... by
  predator. Predators never hunt anyone's **tamed** animals, and babies don't hunt.

## Tamed animals and War Engine factions

**Every animal can be tamed**, with a vanilla item (the old collar and other custom items are gone). The ones the
original never let you tame take a few tries (1 in 3):

| Tame with | Animals |
|---|---|
| apple | Deer, Giraffe |
| beef | Cougar, Hyena, Leopard, Lion, Panther, Tiger, White Lion, White Tiger |
| carrot | Wild Boar |
| chicken | Caracal, Crocodile, Eagle, Komodo Dragon |
| cod | African Penguin, Blue Penguin, Emperor Penguin, Flamingo, Great White Shark, Hammerhead Shark, Jellyfish, Pelican, Platypus, Seagull, Seal, Stingray, Stork, Swordfish, Tiger Shark, Whale |
| hay block | African Elephant, Asian Elephant, Mammoth |
| kelp | Crab |
| melon slice | Capuchin Monkey, Chimpanzee, Gorilla, Hippopotamus, Toucan |
| mutton | Snow Leopard |
| rabbit | Coral Snake, Scarlet Kingsnake, Snake |
| rotten flesh | Vulture |
| salmon | Brown Bear, Orca |
| sugar | Butterfly, Firefly |
| sweet berries | Black Bear, Hedgehog, Iguana, Raccoon, Red Panda |
| wheat | Buffalo, Kangaroo, Ostrich, Rhino, Zebra |
| wheat seeds | Blue Jay, Dove, Duck, Kiwi, Rat, Squirrel, Turkey |

A tamed animal belongs to your War Engine faction (it takes the same `war_f<n>` tag as you, kept in sync while you
are online):

- It **never attacks** you, players of your faction, soldiers or war dogs of your faction, or soldiers of any
  faction that isn't hostile to yours. That holds even when one of them hits it by accident.
- It defends you, attacks what you attack, fights monsters, and goes after soldiers of factions hostile to yours.
- Your allied soldiers won't attack it. Enemy war dogs and melee soldiers count it as one of yours and may go for
  it; enemy gunners shoot it once it attacks their men.

## Riding

Elephants, mammoth, rhino, giraffe, ostrich and the big cats (Lion, White Lion, Tiger, White Tiger, Leopard,
Panther, Cougar, Snow Leopard) are ridden with a **vanilla saddle** once tamed. Soldiers can ride them too: they
carry the `war_mount` family, which **War Engine v9.3** treats like a horse (Mount up, followers riding off with you).

## What was removed

- Camels (only leftover names; the original had no camel model).
- The trader villages, the stork's loot bag (it dropped diamonds and netherite), and the structure pack (palms,
  bananas, ruby/citrine ores).
- Every item and block: gems, armour and tools, swordfish/shark/pearl weapons, scarves, astronaut suits, butterfly
  elytras, elephant/rhino/ostrich armour, flags, custom foods, DNA/syringe, sofa, carpet, cheese... Saddles are the
  vanilla saddle, and drops are vanilla (leather, feathers, meat, cod).

## Fixed along the way

- Gray Hyena had a model and textures but no behavior file, so it never existed in game. It now behaves like the
  Hyena.
- Cougar, Leopard, Panther, Snow Leopard, Tiger and White Tiger used the Lion's render controller, which only draws
  the body while `variant == 0`. They now have their own, which always draws it.

- White Lion never loaded (its file was missing a closing brace).
- Platypus never spawned naturally (its spawn rule named an entity that doesn't exist).
- African penguins tried to lay an egg entity that doesn't exist.
- Whales, dolphins, sharks, fish, seagulls, pelicans and kangaroos were tagged as monsters (some also as undead), so
  iron golems and War Engine soldiers shot them on sight and Smite hit them. Ants and hippos were tagged as polar
  bears, snakes as cave spiders.
- Copied AI: penguins, kiwis and monkeys hunted baby turtles and skeletons like wolves; whales hunted squirrels.
- Rats, snakes, ducks, squirrels and others had baby-zombie jockey seats.
- Legacy and foreign item names (`muttonRaw`, `clownfish`, `fortniteaddon:banana`...) that no longer matched.
- 22 animations the models asked for but the pack never had (now empty stand-ins, so no content-log errors).

## Repo layout

| Path | What |
|---|---|
| `World Animals BP/`, `World Animals RP/` | The packs (edit these) |
| `World Animals BP/scripts/main.js` | Copies the owner's War Engine faction tag onto their pets |
| `tools/animals.py` | The roster: group, role, prey, taming food |
| `tools/rebuild.py` | The one-off rebuild from the original .mcaddon (kept for the record) |
| `tools/validate.py` | Checks every cross-reference (groups, loot tables, items, models, textures, icons) |
| `tools/build_mcaddon.py` | Builds `dist/World_Animals_vX_Y.mcaddon` |
