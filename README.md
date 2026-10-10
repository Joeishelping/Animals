# World Animals v3.0

A cleaned-up rebuild of the World Animals add-on (originally by ArathNido): animals only, sorted by type, with
smarter hunting, and tamed animals that fight on your side in [War Engine](https://github.com/Joeishelping/Minecraft-War-Mod).

Install `dist/World_Animals_v3_0.mcaddon`. It needs Minecraft Bedrock 1.21.90 or newer. In an existing world it
replaces the old version, because it keeps the same pack IDs. Remove the old **[Structure generation]** pack from
the world: it's gone.

## Spawn eggs, by type

102 animals in the creative menu's **Nature** tab (after Minecraft's own groups), in 12 collapsible groups.
**Essentials** comes first:

| Group | Animals |
|---|---|
| Essentials | African Elephant, Brown Bear, Buffalo, Crocodile, Deer, Eagle, Emperor Penguin, Giraffe, Gorilla, Great White Shark, Hippopotamus, Lion, Moose, Orca, Rhino, Tiger, Zebra |
| Dogs | Airedale Terrier, Beagle, Border Collie, Chihuahua, Dachshund, Dalmatian, Doberman, German Shepherd, Golden Retriever, Korean Jindo, Labrador Retriever, Rottweiler, Shiba Inu, Siberian Husky, Toy Poodle |
| Big & Wild Cats | Caracal, Cheetah, Cougar, Leopard, Pallas's Cat (Manul), Panther, Snow Leopard, White Lion, White Tiger |
| Bears, Wild Dogs & Hyenas | Black Bear, Coyote, Fennec Fox, Hyena |
| Hoofed Animals & Giants | American Bison, Asian Elephant, Kangaroo, Mammoth, Okapi, Przewalski's Horse, Warthog, Wild Boar |
| Small Mammals & Primates | Capuchin Monkey, Chimpanzee, Hedgehog, Opossum (Tlacuache), Platypus, Raccoon, Rat, Red Panda, Skunk, Squirrel |
| Water Birds & Penguins | African Penguin, Blue Penguin, Duck, Flamingo, Pelican, Red-crowned Crane, Seagull, Stork |
| Land Birds & Birds of Prey | Blue Jay, Dove, Indian Peafowl (Peacock), Kiwi, Ostrich, Saker Falcon, Toucan, Turkey, Vulture |
| Crocodiles, Lizards & Turtles | American Alligator, Hermann's Tortoise, Iguana, Komodo Dragon |
| Snakes | Coral Snake, King Cobra, Rattlesnake, Scarlet Kingsnake, Snake |
| Sea Life | Beluga Whale, Crab, Hammerhead Shark, Jellyfish, Manta Ray, Seal, Stingray, Swordfish, Tiger Shark, Whale, Whale Shark |
| Insects & Bugs | Butterfly, Firefly |

**No natural spawning**: animals only come from eggs, breeding and hatching (`NATURAL_SPAWNING` in
`tools/animals.py`).

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

## New in v3

### New animals

Built on the closest model of the original pack, with their own colors, markings, size, sounds and behavior, and
only kept where they look like their own animal next to the original:

| Animal | From | Behavior |
|---|---|---|
| American Alligator | USA | hunts, attacks people |
| American Bison | USA, Canada | defensive |
| Beluga Whale | Canada, Russia, Arctic | passive |
| Cheetah | Africa, Iran | hunts |
| Coyote | USA, Mexico, Canada | hunts |
| Fennec Fox | Middle East, North Africa | passive |
| Hermann's Tortoise | Greece, Italy, Balkans | passive |
| Indian Peafowl (Peacock) | India (national bird) | passive |
| King Cobra | India, Southeast Asia | hunts, attacks people |
| Manta Ray | Mexico, Dominican Republic, Indian Ocean | passive |
| Moose | Canada, USA, Russia, Northern Europe | defensive |
| Okapi | Africa (Congo) | passive |
| Opossum (Tlacuache) | Mexico, USA | passive |
| Pallas's Cat (Manul) | Mongolia, Russia | hunts |
| Przewalski's Horse | Mongolia | defensive |
| Rattlesnake | USA, Mexico | hunts, attacks people |
| Red-crowned Crane | Korea, Mongolia, Russia, Japan | passive |
| Saker Falcon | Mongolia (national bird), Middle East | hunts |
| Skunk | USA, Canada, Mexico | defensive |
| Warthog | Africa | defensive |
| Whale Shark | Mexico, India, Middle East seas | passive |

The **Moose** has its own antlers (flat palms), a long heavy muzzle and a dewlap; the **Peacock** a full
eye-spotted tail fan.

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
| Dalmatian | Croatia |
| Border Collie | Scotland / England |
| Rottweiler | Germany |
| Korean Jindo | Korea |
| Doberman | Germany |

What they do (tamed):

- **All dogs bark at danger**: a monster or an enemy soldier within 16 blocks, and you get told what and where.
- **Guard dogs** (German Shepherd, Rottweiler, Doberman, Airedale, Husky, Jindo, Labrador, Golden, Dalmatian)
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

- **Dangerous predators** hunt prey **and** attack people (players, villagers, illagers) who come close. They
  leave War Engine soldiers alone unless a soldier hurts them: Lion, White Lion, Tiger, White Tiger, Leopard, Panther, Brown Bear, Hyena, Hippopotamus, Crocodile,
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
| apple | Deer, Giraffe, Okapi, Przewalski's Horse |
| beef | Cheetah, Cougar, Hyena, Leopard, Lion, Panther, Tiger, White Lion, White Tiger |
| bone | Airedale Terrier, Beagle, Border Collie, Chihuahua, Dachshund, Dalmatian, Doberman, German Shepherd, Golden Retriever, Korean Jindo, Labrador Retriever, Rottweiler, Shiba Inu, Siberian Husky, Toy Poodle |
| carrot | Warthog, Wild Boar |
| chicken | American Alligator, Caracal, Coyote, Crocodile, Eagle, Komodo Dragon |
| cod | African Penguin, Beluga Whale, Blue Penguin, Emperor Penguin, Flamingo, Great White Shark, Hammerhead Shark, Jellyfish, Pelican, Platypus, Red-crowned Crane, Seagull, Seal, Stingray, Stork, Swordfish, Tiger Shark, Whale |
| dandelion | Hermann's Tortoise |
| egg | Opossum (Tlacuache) |
| hay block | African Elephant, Asian Elephant, Mammoth |
| kelp | Crab, Manta Ray, Whale Shark |
| melon slice | Capuchin Monkey, Chimpanzee, Gorilla, Hippopotamus, Toucan |
| mutton | Snow Leopard |
| rabbit | Coral Snake, King Cobra, Pallas's Cat (Manul), Rattlesnake, Saker Falcon, Scarlet Kingsnake, Snake |
| rotten flesh | Vulture |
| salmon | Brown Bear, Orca |
| sugar | Butterfly, Firefly |
| sweet berries | Black Bear, Fennec Fox, Hedgehog, Iguana, Raccoon, Red Panda, Skunk |
| wheat | American Bison, Buffalo, Kangaroo, Moose, Ostrich, Rhino, Zebra |
| wheat seeds | Blue Jay, Dove, Duck, Indian Peafowl (Peacock), Kiwi, Rat, Squirrel, Turkey |

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
| `World Animals BP/scripts/falconry.js` | The falcon on the glove: perch, strike, scout, recall |
| `World Animals BP/scripts/dogs.js` | Dog jobs: barking at danger, herding, retrieving |
| `tools/species.py`, `tools/species_build.py`, `tools/recolor.py` | New species: recipes, model tweaks, the recolor engine |
| `tools/dogs.py` | The dog model, coats, animations and behavior |
| `tools/render_preview.py` | Renders models with their textures (the `previews/` sheets) |
| `tools/animals.py` | The roster: group, role, prey, taming food |
| `tools/rebuild.py` | The one-off rebuild from the original .mcaddon (kept for the record) |
| `tools/validate.py` | Checks every cross-reference (groups, loot tables, items, models, textures, icons) |
| `tools/build_mcaddon.py` | Builds `dist/World_Animals_vX_Y.mcaddon` |
