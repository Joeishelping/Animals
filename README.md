# World Animals v2.1 (cleaned up)

A cleaned-up rebuild of the World Animals add-on (originally by ArathNido): animals only, sorted by type, with
smarter hunting, and tamed animals that fight on your side in [War Engine](https://github.com/Joeishelping/Minecraft-War-Mod).

Install `dist/World_Animals_v2_1.mcaddon`. It needs Minecraft Bedrock 1.21.90 or newer. In an existing world it
replaces the old version, because it keeps the same pack IDs. Remove the old **[Structure generation]** pack from
the world: it's gone.

## Spawn eggs, by type

All 76 animals from the original pack are in. Their eggs are in the creative menu's **Nature** tab, in 17
collapsible groups:

| Group | Animals |
|---|---|
| Birds of Prey | Eagle, Vulture |
| Water Birds | Duck, Flamingo, Pelican, Seagull, Stork |
| Land & Tropical Birds | Blue Jay, Dove, Toucan, Turkey |
| Penguins & Flightless Birds | African Penguin, Blue Penguin, Emperor Penguin, Kiwi, Ostrich, Penguin |
| Big Cats | Caracal, Cougar, Leopard, Lion, Panther, Snow Leopard, Tiger, White Lion, White Tiger |
| Bears & Hyenas | Black Bear, Brown Bear, Gray Hyena, Hyena |
| Elephants & Giants | African Elephant, Asian Elephant, Giraffe, Hippopotamus, Mammoth, Rhino |
| Grazers & Hoofed Animals | Buffalo, Deer, Kangaroo, Wild Boar, Zebra |
| Small Mammals | Hedgehog, Platypus, Raccoon, Rat, Red Panda, Squirrel |
| Primates | Capuchin Monkey, Chimpanzee, Gorilla |
| Reptiles & Turtles | Crocodile, Iguana, Komodo Dragon, Land Turtle |
| Snakes | Coral Snake, Scarlet Kingsnake, Snake |
| Sharks | Great White Shark, Hammerhead Shark, Shark, Tiger Shark |
| Whales, Dolphins & Seals | Orca, Pink Dolphin, Seal, Whale |
| Fish, Rays & Jellyfish | Jellyfish, Lanternfish, Stingray, Swordfish |
| Crabs & Shellfish | Clam, Crab, Shrimp |
| Insects & Bugs | Ant, Butterfly, Firefly, Snail |

Blue Crab and Blue Iguana are color variants of the Crab and Iguana. Laid eggs (duck, turkey, ostrich, penguins)
still drop from the parents and hatch, but they aren't in the menu.

## How they behave

- **Dangerous predators** hunt prey **and** attack people (players, villagers, illagers, War Engine soldiers) who
  come close: Lion, White Lion, Tiger, White Tiger, Leopard, Panther, Brown Bear, Hyena, Hippopotamus, Crocodile,
  Komodo Dragon, Snake, Coral Snake, Shark, Great White Shark, Tiger Shark.
- **Hunters** go after their prey but leave people alone unless hurt: Cougar, Snow Leopard, Caracal, Black Bear,
  Chimpanzee (hunts capuchins), Eagle, Pelican, Seagull, Seal, Orca, Hammerhead, Swordfish, Scarlet Kingsnake (eats
  other snakes).
- **Defensive animals** fight back when hurt: elephants, mammoth, rhino, buffalo, giraffe, zebra, kangaroo, wild
  boar, ostrich, gorilla, hedgehog, platypus, crab, stingray, jellyfish, ant. Herd animals call the herd.
- Everything else is passive.
- Prey is real prey: zebras, deer, buffalo, sheep, pigs, cows, horses, rabbits, chickens, fish, squid, seals... by
  predator. Predators never hunt anyone's **tamed** animals, and babies don't hunt.

## Tamed animals and War Engine factions

Tame with a vanilla item (the old collar and other custom items are gone):

| Animal | Tame with |
|---|---|
| Lion, White Lion, Tiger, White Tiger, Leopard, Panther, Cougar | beef |
| Snow Leopard | mutton |
| Caracal, Crocodile, Komodo Dragon | chicken |
| African / Asian Elephant, Mammoth | hay bale |
| Rhino, Ostrich | wheat |
| Giraffe | apple |
| Gorilla, Chimpanzee, Capuchin Monkey, Toucan | melon slice |
| Penguins, Seal, Platypus | cod |
| Hedgehog, Iguana, Raccoon, Red Panda | sweet berries |
| Blue Jay, Dove, Kiwi, Rat | wheat seeds |
| Scarlet Kingsnake | rabbit |

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
