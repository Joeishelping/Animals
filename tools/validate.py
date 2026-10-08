"""Checks the packs for broken references. usage: python3 -I tools/validate.py [repo root]"""
import json
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "World Animals BP")
RP = os.path.join(ROOT, "World Animals RP")
NS = "worldanimals:"
errors, notes = [], []


def files(root, ext=".json"):
    for r, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(ext):
                yield os.path.join(r, f)


def load(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        errors.append(f"{os.path.relpath(p, ROOT)}: not valid JSON ({e})")
        return None


def walk(o, path=()):
    if isinstance(o, dict):
        for k, v in o.items():
            yield path + (k,), v
            yield from walk(v, path + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield path + (i,), v
            yield from walk(v, path + (i,))


# ---- definitions
entities, items, client = {}, {}, {}
for p in files(os.path.join(BP, "entities")):
    d = load(p)
    if d:
        entities[d["minecraft:entity"]["description"]["identifier"]] = (p, d)
for p in files(os.path.join(BP, "items")):
    d = load(p)
    if d:
        items[d["minecraft:item"]["description"]["identifier"]] = (p, d)
for p in files(os.path.join(RP, "entity")):
    d = load(p)
    if d:
        client[d["minecraft:client_entity"]["description"]["identifier"]] = (p, d)


def defined(sub, key):
    out = set()
    for p in files(os.path.join(RP, sub)):
        d = load(p)
        if not d:
            continue
        if key == "geometry":
            for k in d:
                if k.startswith("geometry."):
                    out.add(k.split(":")[0])
            for g in d.get("minecraft:geometry", []):
                out.add(g["description"]["identifier"])
        else:
            out |= set(d.get(key, {}))
    return out


geos = defined("models", "geometry")
anims = defined("animations", "animations")
ctrls = defined("animation_controllers", "animation_controllers")
rctrls = defined("render_controllers", "render_controllers")
item_tex = load(os.path.join(RP, "textures", "item_texture.json"))["texture_data"]

# ---- behaviour entities
for ident, (p, d) in entities.items():
    rp = os.path.relpath(p, ROOT)
    ent = d["minecraft:entity"]
    groups = set(ent.get("component_groups", {}))
    for path, v in walk(ent.get("events", {})):
        if path and path[-1] == "component_groups" and isinstance(v, list):
            for g in v:
                if g not in groups:
                    errors.append(f"{rp}: event uses missing group {g}")
    for path, v in walk(ent):
        if not isinstance(v, str):
            continue
        if v.startswith("loot_tables/") and not os.path.exists(os.path.join(BP, v)):
            errors.append(f"{rp}: missing loot table {v}")
        if v.startswith(NS) and v not in entities and v not in items:
            errors.append(f"{rp}: unknown id {v} at {'/'.join(map(str, path))}")
    if ident not in client:
        errors.append(f"{rp}: no client entity for {ident}")
    if ident.replace(NS, NS + "spawn_") not in items and not any(
            i[1]["minecraft:item"]["components"].get("minecraft:entity_placer", {}).get("entity") == ident for i in items.values()):
        errors.append(f"{rp}: no egg item places {ident}")
    for path, v in walk(ent):
        if path and path[-1] == "family" and isinstance(v, list) and "monster" in v and "wa:hostile" not in path:
            errors.append(f"{rp}: monster family outside wa:hostile (War Engine soldiers would shoot it on sight)")
    gs = ent.get("component_groups", {})
    tames = any(b.get("minecraft:tameable", {}).get("probability", 1) > 0
                for b in [ent.get("components", {})] + list(gs.values()) if "minecraft:tameable" in b)
    if "/eggs/" not in rp and not (tames and any("minecraft:is_tamed" in g for g in gs.values())):
        errors.append(f"{rp}: cannot be tamed")

# ---- loot tables
for p in files(os.path.join(BP, "loot_tables")):
    d = load(p)
    for path, v in walk(d or {}):
        if path and path[-1] == "name" and isinstance(v, str) and v.startswith(NS) and v not in items:
            errors.append(f"{os.path.relpath(p, ROOT)}: unknown item {v}")

# ---- items and catalog
for ident, (p, d) in items.items():
    c = d["minecraft:item"]["components"]
    ic = c.get("minecraft:icon", {}).get("textures", {}).get("default")
    if ic and ic not in item_tex:
        errors.append(f"{os.path.relpath(p, ROOT)}: icon {ic} not in item_texture.json")
    if not ic:
        notes.append(f"{ident}: no icon")
    if c.get("minecraft:entity_placer", {}).get("entity") not in entities:
        errors.append(f"{os.path.relpath(p, ROOT)}: places unknown entity")
for k, v in item_tex.items():
    tex = v["textures"] if isinstance(v["textures"], str) else v["textures"][0]
    if not any(os.path.exists(os.path.join(RP, tex + e)) for e in (".png", ".tga")):
        errors.append(f"item_texture {k}: missing {tex}")
cat = load(os.path.join(BP, "item_catalog", "crafting_item_catalog.json"))
listed = [i for c in cat["minecraft:crafting_items_catalog"]["categories"] for g in c["groups"] for i in g["items"]]
for i in listed:
    if i not in items:
        errors.append(f"catalog lists unknown item {i}")
if len(listed) != len(set(listed)):
    errors.append("catalog lists an item twice")

# ---- spawn rules
for p in files(os.path.join(BP, "spawn_rules")):
    d = load(p)
    if d and d["minecraft:spawn_rules"]["description"]["identifier"] not in entities:
        errors.append(f"{os.path.relpath(p, ROOT)}: spawn rule for unknown entity")

# ---- client entities
VANILLA_PREFIX = ("controller.animation.wolf", "controller.animation.llama", "controller.animation.horse",
                  "controller.animation.parrot", "controller.animation.chicken", "controller.animation.dolphin",
                  "controller.animation.cat", "controller.animation.fox", "controller.animation.sheep",
                  "controller.animation.pig", "controller.animation.cow", "controller.animation.panda",
                  "controller.animation.polarbear", "controller.animation.ocelot", "controller.animation.bat",
                  "controller.animation.turtle", "controller.animation.squid", "controller.animation.rabbit",
                  "controller.animation.zombie", "controller.animation.humanoid", "controller.animation.bee",
                  "controller.animation.fish", "controller.animation.spider", "controller.animation.ghast")
for ident, (p, d) in client.items():
    rp = os.path.relpath(p, ROOT)
    desc = d["minecraft:client_entity"]["description"]
    for g in desc.get("geometry", {}).values():
        if g not in geos:
            errors.append(f"{rp}: geometry {g} not defined")
    for t in desc.get("textures", {}).values():
        if not any(os.path.exists(os.path.join(RP, t + e)) for e in (".png", ".tga", ".jpg")):
            errors.append(f"{rp}: texture {t} missing")
    for a in desc.get("animations", {}).values():
        if a.startswith("controller.animation."):
            if a not in ctrls and not a.startswith(VANILLA_PREFIX):
                notes.append(f"{rp}: controller {a} (vanilla?)")
        elif a not in anims and not a.startswith("animation.common") and not a.startswith("animation."):
            errors.append(f"{rp}: animation {a} not defined")
        elif a not in anims:
            notes.append(f"{rp}: animation {a} not in pack (vanilla?)")
    for rc in desc.get("render_controllers", []):
        name = rc if isinstance(rc, str) else list(rc)[0]
        if name not in rctrls and not name.startswith("controller.render.default"):
            notes.append(f"{rp}: render controller {name} not in pack (vanilla?)")

for n in sorted(set(notes)):
    print("note:", n)
for e in errors:
    print("ERROR:", e)
print(f"{len(entities)} entities, {len(items)} items, {len(client)} client entities, {len(errors)} errors")
sys.exit(1 if errors else 0)
