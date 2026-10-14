# World Animals v3.5

A cleaned-up rebuild of the World Animals add-on (originally by ArathNido): animals only, sorted by type, with
smarter hunting, and tamed animals that fight on your side in [War Engine](https://github.com/Joeishelping/Minecraft-War-Mod).

Install `dist/World_Animals_v3_5.mcaddon`. It needs Minecraft Bedrock 1.21.90 or newer. In an existing world it
replaces the old version, because it keeps the same pack IDs. Remove the old **[Structure generation]** pack from
the world: it's gone.

## Spawn eggs, by type

70 animals in the creative menu's **Nature** tab (after Minecraft's own groups), in 11 collapsible groups.
**Essentials** comes first:

| Group | Animals |
|---|---|
| Essentials | African Elephant, Buffalo, Crocodile, Deer, Eagle, Emperor Penguin, Giraffe, Gorilla, Great White Shark, Hippopotamus, Lion, Moose, Orca, Rhino, Tiger, Zebra |
| Dogs | Airedale Terrier, Beagle, Border Collie, Chihuahua, Dachshund, German Shepherd, Golden Retriever, Labrador Retriever, Rottweiler, Shiba Inu, Siberian Husky, Toy Poodle |
| Cats, Bears & Hyenas | Black Bear, Cougar, Hyena, Snow Leopard |
| Hoofed Animals & Giants | Kangaroo, Mammoth, Wild Boar |
| Small Mammals & Primates | Capuchin Monkey, Chimpanzee, Opossum (Tlacuache), Raccoon, Rat, Squirrel |
| Water Birds | Duck, Flamingo, Pelican, Seagull |
| Land Birds & Birds of Prey | Dove, Indian Peafowl (Peacock), Ostrich, Saker Falcon, Toucan, Turkey, Vulture |
| Crocodiles, Lizards & Turtles | American Alligator, Hermann's Tortoise, Iguana, Komodo Dragon |
| Snakes | King Cobra, Rattlesnake, Snake |
| Sea Life | Crab, Hammerhead Shark, Jellyfish, Lobster, Manta Ray, Octopus, Seal, Stingray, Swordfish, Tiger Shark, Whale |

**No natural spawning**: animals only come from eggs, breeding and hatching (`NATURAL_SPAWNING` in
`tools/animals.py`).

Blue Crab, Blue Iguana and the blue Lobster are color variants of the Crab and Iguana. Laid eggs (duck, turkey, ostrich, emperor penguin)
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
| Asian Elephant, White Lion, White Tiger, Leopard, Panther, Brown Bear, Coral Snake, Scarlet Kingsnake, Caracal, Red Panda, Hedgehog, Platypus, African Penguin, Blue Penguin, Stork, Blue Jay, Kiwi, Butterfly, Firefly, American Bison, Przewalski's Horse, Warthog, Cheetah, Pallas's Cat (Manul), Coyote, Skunk, Okapi, Fennec Fox, Red-crowned Crane, Beluga Whale, Whale Shark, Doberman, Korean Jindo, Dalmatian | removed by request (v3.4) |

## New in v3

### New animals

Built on the closest model of the original pack, with their own colors, markings, size, sounds and behavior, and
only kept where they look like their own animal next to the original:

| Animal | From | Behavior |
|---|---|---|
| American Alligator | USA | hunts, attacks people |
| Hermann's Tortoise | Greece, Italy, Balkans | passive |
| Indian Peafowl (Peacock) | India (national bird) | passive |
| King Cobra | India, Southeast Asia | hunts, attacks people |
| Lobster | Canada, USA (Maine), Northern Europe, Mediterranean | defensive |
| Manta Ray | Mexico, Dominican Republic, Indian Ocean | passive |
| Moose | Canada, USA, Russia, Northern Europe | defensive |
| Octopus | Greece, Italy, Mediterranean, Korea, worldwide | defensive |
| Opossum (Tlacuache) | Mexico, USA | passive |
| Rattlesnake | USA, Mexico | hunts, attacks people |
| Saker Falcon | Mongolia (national bird), Middle East | hunts |

The **Moose** is its own model, not a reshaped deer: a shoulder hump, a long overhanging nose, the bell under the
throat, wide palmate antlers with tines, a near-black coat with grey-brown lower legs, and it lowers its head to
charge. It stands about 1.9 blocks at the
shoulder (a real moose next to Steve); the **Peacock** has a full eye-spotted tail fan. The **Octopus** and the
**Lobster** have models of their own: the octopus waves its eight arms and squirts ink when hurt (blinding whoever is
next to it for a moment and jetting away); the lobster walks on eight legs, works its claws and antennae, and is
rarely blue (1 in 8).

Tried and cut because they looked too much like an animal the pack already has: Jaguar (looked like the leopard), Bald Eagle (looked like the eagle), Eurasian Lynx (looked like the caracal), Moon Bear (looked like the black bear), Yak (looked like the bison), Snowy Owl (looked like the a white eagle), Atlantic Puffin (looked like the african penguin), Mute Swan (looked like the a white duck), European Badger (looked like the raccoon), Meerkat (looked like the squirrel), Olive Baboon (looked like the chimpanzee).

### Dogs (pets, never hostile)

Their own model with per-breed size, ears, muzzle and tail, and painted coats. Tame with a **bone**; they sit,
follow you, defend you and respect your War Engine faction like every other pet. Feed meat to heal and breed them.

| Breed | Origin |
|---|---|
| German Shepherd | Germany |
| Toy Poodle | France / Germany |
| Chihuahua | Mexico |
| Shiba Inu | Japan |
| Airedale Terrier | England |
| Golden Retriever | Scotland |
| Labrador Retriever | Canada |
| Siberian Husky | Russia (Siberia) |
| Beagle | England |
| Dachshund | Germany |
| Border Collie | Scotland / England |
| Rottweiler | Germany |

What they do (tamed):

- **All dogs bark at danger**: a monster or an enemy soldier within 16 blocks, and you get told what and where.
- **Guard dogs** (German Shepherd, Rottweiler, Airedale, Husky, Labrador, Golden Retriever)
  attack monsters and enemy soldiers on their own.
- **Border Collie herds**: sneak near it and the livestock around it is driven to you.
- **Retrievers** (Golden Retriever, Labrador, Beagle) fetch the drops of anything you kill near them.

### Falconry (Saker Falcon, Mongolia's national bird)

Tame a Saker Falcon with **rabbit**, and craft a **Falconry Glove** (leather `L L` / `LLL`, string in the middle of
the bottom row).

- **Right-click your falcon holding the glove**: it hops onto your arm.
- **Use the glove looking at a mob**: it dives on it at full speed. Small prey (rabbits, chickens, rats, squirrels,
  ducks, fish...) dies outright and the drops come back to you; anything bigger takes a heavy hit. It never strikes
  you, your animals, your faction or soldiers that aren't hostile to you.
- **Use the glove looking at the sky**: it scouts, circling high above you for 30 seconds and reporting monsters,
  enemy soldiers and enemy players within 64 blocks on your screen (how many, which way, how far), marking each
  one.
- **Sneak + use the glove**: recall it from anywhere; if it's on your arm, let it fly free.

## How they behave

- **Dangerous predators** hunt prey **and** attack people (players, villagers, illagers) **and War Engine
  soldiers and war dogs** who come close (wild ones only; a tamed one never goes for your side): Lion, Tiger, Hyena, Hippopotamus, Crocodile,
  Komodo Dragon, Snake, Great White Shark, Tiger Shark.
- **Hunters** go after their prey but leave people alone unless hurt: Cougar, Snow Leopard, Black Bear,
  Chimpanzee (hunts capuchins), Eagle, Pelican, Seagull, Seal, Orca, Hammerhead, Swordfish.
- **Defensive animals** fight back when hurt: elephants, mammoth, rhino, buffalo, giraffe, zebra, kangaroo, wild
  boar, ostrich, gorilla, moose, crab, lobster, octopus, stingray, jellyfish. Herd animals call the herd.
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
| beef | Cougar, Hyena, Lion, Tiger |
| bone | Airedale Terrier, Beagle, Border Collie, Chihuahua, Dachshund, German Shepherd, Golden Retriever, Labrador Retriever, Rottweiler, Shiba Inu, Siberian Husky, Toy Poodle |
| carrot | Wild Boar |
| chicken | American Alligator, Crocodile, Eagle, Komodo Dragon |
| cod | Emperor Penguin, Flamingo, Great White Shark, Hammerhead Shark, Jellyfish, Pelican, Seagull, Seal, Stingray, Swordfish, Tiger Shark, Whale |
| dandelion | Hermann's Tortoise |
| egg | Opossum (Tlacuache) |
| hay block | African Elephant, Mammoth |
| kelp | Crab, Manta Ray |
| melon slice | Capuchin Monkey, Chimpanzee, Gorilla, Hippopotamus, Toucan |
| mutton | Snow Leopard |
| rabbit | King Cobra, Rattlesnake, Saker Falcon, Snake |
| rotten flesh | Vulture |
| salmon | Orca |
| sweet berries | Black Bear, Iguana, Raccoon |
| wheat | Buffalo, Kangaroo, Moose, Ostrich, Rhino, Zebra |
| wheat seeds | Dove, Duck, Indian Peafowl (Peacock), Rat, Squirrel, Turkey |

A tamed animal belongs to your War Engine faction (it takes the same `war_f<n>` tag as you, kept in sync while you
are online):

- It **never attacks** you, players of your faction, soldiers or war dogs of your faction, or soldiers of any
  faction that isn't hostile to yours. That holds even when one of them hits it by accident.
- It defends you, attacks what you attack, fights monsters, and goes after soldiers of factions hostile to yours.
- Your allied soldiers won't attack it. Enemy war dogs and melee soldiers count it as one of yours and may go for
  it; enemy gunners shoot it once it attacks their men.

## Riding

The African Elephant, mammoth, rhino, giraffe, ostrich and the big cats (Lion, Tiger, Cougar, Snow Leopard) are ridden with a **vanilla saddle** once tamed. Soldiers can ride them too: they
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
| `World Animals BP/scripts/falconry.js` | The falcon on the glove: perch, strike, scout, recall |
| `World Animals BP/scripts/dogs.js` | Dog jobs: barking at danger, herding, retrieving |
| `tools/species.py`, `tools/species_build.py`, `tools/recolor.py` | New species: recipes, model tweaks, the recolor engine |
| `tools/dogs.py` | The dog model, coats, animations and behavior |
| `tools/render_preview.py` | Renders models with their textures (the `previews/` sheets) |
| `tools/animals.py` | The roster: group, role, prey, taming food |
| `tools/rebuild.py` | The one-off rebuild from the original .mcaddon (kept for the record) |
| `tools/validate.py` | Checks every cross-reference (groups, loot tables, items, models, textures, icons) |
| `tools/build_mcaddon.py` | Builds `dist/World_Animals_vX_Y.mcaddon` |
