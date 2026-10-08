"""One-off rebuild of the original World Animals add-on into the cleaned packs in this repo.

usage: python3 -I tools/rebuild.py <extracted original BP> <extracted original RP> <repo root>

Kept for the record (and to redo the cleanup if the original pack is updated). After this ran, the packs in the
repo are the source of truth; edit them directly.
"""
import copy
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wa_common import load, dump  # noqa: E402
from animals import (NS, GROUPS, ROSTER, REMOVED_ENTITIES, LAID_EGGS, ITEM_MAP, HUMANS)  # noqa: E402

NF = 40  # War Engine factions: tags war_f1..war_f40 (member), war_h1..war_h40 (soldier is hostile to faction i)
SRC_BP, SRC_RP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
BP = os.path.join(OUT, "World Animals BP")
RP = os.path.join(OUT, "World Animals RP")
log = []

KEPT = set(ROSTER)
JUNK_FAMILIES = {"monster", "undead", "polarbear", "polarsnail", "cavespider", "arthropod", "pig", "zombie", "animal",
                 "shark", "skeleton", "lightweight"}

# ------------------------------------------------------------------ filters
def t(test, subject, value, op=None):
    d = {"test": test, "subject": subject, "value": value}
    if op:
        d["operator"] = op
    return d


def fam_any(fams, subject="other"):
    fams = list(dict.fromkeys(fams))
    if len(fams) == 1:
        return t("is_family", subject, fams[0])
    return {"any_of": [t("is_family", subject, f) for f in fams]}


SOLDIERISH = {"any_of": [t("is_family", "other", "war_soldier"), t("is_family", "other", "war_hound")]}
# "other" is on our side: same War Engine faction as this animal (its owner's), or a soldier / war dog whose
# faction is not hostile to ours
SAME_FACTION = {"any_of": [{"all_of": [t("has_tag", "self", f"war_f{i}"), t("has_tag", "other", f"war_f{i}")]}
                           for i in range(1, NF + 1)]}
NOT_HOSTILE_TO_US = {"any_of": [{"all_of": [t("has_tag", "self", f"war_f{i}"), t("has_tag", "other", f"war_h{i}", "!=")]}
                                for i in range(1, NF + 1)]}
ALLY = {"any_of": [SAME_FACTION, {"all_of": [SOLDIERISH, NOT_HOSTILE_TO_US]}]}
NOT_ALLY = {"none_of": [ALLY]}
# soldiers / war dogs hostile to this animal's faction
ENEMY_SOLDIER = {"any_of": [
    {"all_of": [t("has_tag", "self", f"war_f{i}"), t("has_tag", "other", f"war_h{i}")]} for i in range(1, NF + 1)]}


def wild_targets(role, prey, humans):
    types = []
    adult = {"all_of": [t("is_baby", "self", False), t("has_component", "self", "minecraft:is_tamed", "!=")]}
    if role == "apex" and humans:
        types.append({"filters": {"all_of": [adult, fam_any(HUMANS)]}, "max_dist": humans})
    if prey:
        types.append({"filters": {"all_of": [adult, fam_any(prey),
                                             t("has_component", "other", "minecraft:is_tamed", "!="),
                                             t("is_family", "other", "worldanimals_pet", "!=")]},
                      "max_dist": 16})
    if not types:
        return None
    return {"priority": 3, "must_see": True, "reselect_targets": True, "attack_interval": 8 if role == "hunter" else 4,
            "must_see_forget_duration": 6.0, "entity_types": types}


def tame_targets():
    return {"priority": 4, "must_see": True, "reselect_targets": True, "entity_types": [
        {"filters": {"all_of": [t("is_family", "other", "monster"), t("is_family", "other", "creeper", "!="),
                                NOT_ALLY]}, "max_dist": 16},
        {"filters": {"all_of": [SOLDIERISH, ENEMY_SOLDIER]}, "max_dist": 16},
    ]}


# ------------------------------------------------------------------ item / id cleanup
REMOVE = object()


def egg_item(e):
    return f"{NS}:laid_{e}"


def map_id(s):
    """returns a replacement string, the same string, or REMOVE"""
    if not s.startswith(NS + ":"):
        return s
    name = s.split(":", 1)[1]
    if name in KEPT:
        return s
    if name in ITEM_MAP:
        return ITEM_MAP[name]
    if name.endswith("_spawn_egg"):
        base = name[: -len("_spawn_egg")]
        if base in LAID_EGGS:
            return egg_item(base)
        if base in KEPT and base not in LAID_EGGS:
            return f"{NS}:spawn_{base}"
        return REMOVE
    if name == "penguin_african_egg":
        return f"{NS}:african_penguin_egg"
    return REMOVE


CONTAINERS = {"components", "component_groups", "events", "description", "minecraft:entity"}


def clean(o, tame_food, parent=None):
    """Swap/drop references to things that no longer exist. Returns REMOVE when `o` itself must go.
    Inside the entity's containers (components, groups, events) only the affected key is dropped."""
    if isinstance(o, str):
        if o == f"{NS}:collar":
            return tame_food or REMOVE
        return map_id(o)
    if isinstance(o, list):
        out = []
        for v in o:
            c = clean(v, tame_food, parent)
            if c is not REMOVE:
                out.append(c)
        return out
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            c = clean(v, tame_food, k)
            if c is REMOVE:
                if parent in CONTAINERS or parent is None and k in CONTAINERS or ":" in k and parent != "filters":
                    log.append(f"dropped {k}")
                    continue
                return REMOVE
            if k == "all_of" and isinstance(v, list) and len(c) != len(v):
                return REMOVE          # a required test can no longer pass
            if k == "any_of" and isinstance(v, list) and v and not c:
                return REMOVE          # nothing left that could pass
            if k in ("interactions", "entities") and isinstance(v, list) and v and not c:
                return REMOVE
            out[k] = c
        return out
    return o


# ------------------------------------------------------------------ behaviour pack entities
TARGET_KEYS = ["minecraft:behavior.nearest_attackable_target", "minecraft:behavior.nearest_prioritized_attackable_target",
               "minecraft:behavior.hurt_by_target", "minecraft:behavior.owner_hurt_by_target",
               "minecraft:behavior.owner_hurt_target", "minecraft:behavior.defend_trusted_target"]
JOCKEY = {"zombie", "baby_zombie", "husk", "drowned", "skeleton", "baby_undead", "zombie_pigman"}


def anywhere(ent, key):
    if key in ent.get("components", {}):
        return True
    return any(key in g for g in ent.get("component_groups", {}).values())


def blocks(ent):
    yield ent.setdefault("components", {})
    yield from ent.get("component_groups", {}).values()


def fix_families(fams, short, group, mount):
    keep = [f for f in fams if f not in JUNK_FAMILIES and (f == "mob" or f.startswith(short) or f == short)]
    extra = [short, NS]
    if group:
        extra.append(f"wa_{group}")
    if mount:
        extra.append("war_mount")
    out = []
    for f in extra + keep + ["mob"]:
        if f not in out:
            out.append(f)
    return out


LEGACY_ITEMS = {
    "appleenchanted": "enchanted_golden_apple", "clownfish": "tropical_fish", "cooked_fish": "cooked_cod",
    "fish": "cod", "melon": "melon_slice", "muttoncooked": "cooked_mutton", "muttonraw": "mutton",
    "horsearmordiamond": "diamond_horse_armor", "horsearmorgold": "golden_horse_armor",
    "horsearmoriron": "iron_horse_armor", "horsearmorleather": "leather_horse_armor",
    "fortniteaddon:banana": "melon_slice", "fortniteaddon:sweet_berries": "sweet_berries",
}
ITEM_KEYS = {"item", "items", "tame_items", "breed_items", "feed_items", "spawn_item"}


def item_name(v):
    low = v.lower()
    bare = low[len("minecraft:"):] if low.startswith("minecraft:") else low
    if low in LEGACY_ITEMS:
        return "minecraft:" + LEGACY_ITEMS[low]
    if bare in LEGACY_ITEMS:
        return "minecraft:" + LEGACY_ITEMS[bare]
    return v if ":" in v else "minecraft:" + v


def fix_item_names(o, key=None):
    """legacy / foreign item names -> current namespaced vanilla ids (in item fields and has_equipment tests)"""
    if isinstance(o, dict):
        equip = o.get("test") == "has_equipment"
        for k, v in o.items():
            if isinstance(v, str) and (k in ITEM_KEYS or (equip and k == "value")):
                o[k] = item_name(v)
            else:
                fix_item_names(v, k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, str) and key in ITEM_KEYS:
                o[i] = item_name(v)
            else:
                fix_item_names(v, key)


def repair_structure(ent, short):
    """white_lion.json lost a closing brace after its wild group: the tame group, the components and the events
    all ended up nested inside it. Put them back where they belong."""
    groups = ent.setdefault("component_groups", {})
    for k in ("components", "events"):
        if k in groups:
            ent[k] = groups.pop(k)
            log.append(f"{short}: repaired: {k} was inside component_groups")
    for gname, g in list(groups.items()):
        for k, v in list(g.items()):
            if isinstance(v, dict) and k in ("components", "events"):
                ent[k] = g.pop(k)
                log.append(f"{short}: repaired: {k} was inside {gname}")
            elif isinstance(v, dict) and v and all(":" in kk for kk in v) and any(
                    kk in ("minecraft:is_tamed", "minecraft:is_baby", "minecraft:variant") for kk in v):
                groups[k] = g.pop(k)
                log.append(f"{short}: repaired: group {k} was inside {gname}")


def prune_events(ent):
    """drop references to component groups that no longer exist"""
    have = set(ent.get("component_groups", {}))

    def fix(o):
        if isinstance(o, dict):
            for k in ("add", "remove"):
                if isinstance(o.get(k), dict) and "component_groups" in o[k]:
                    o[k]["component_groups"] = [g for g in o[k]["component_groups"] if g in have]
            for v in o.values():
                fix(v)
        elif isinstance(o, list):
            for v in o:
                fix(v)
    fix(ent.get("events", {}))


def build_entity(path, short):
    d = load(path)
    group, role, prey, humans, dmg, tame_food, _name = ROSTER[short]
    d = clean(d, tame_food)
    fix_item_names(d)
    ent = d["minecraft:entity"]
    repair_structure(ent, short)
    desc = ent["description"]
    desc["is_spawnable"] = False       # the auto spawn egg is replaced by the grouped one
    desc["is_summonable"] = True
    groups = ent.setdefault("component_groups", {})
    base = ent.setdefault("components", {})

    # rideables: keep the real mounts (players can ride), drop copied baby-zombie jockey seats
    mount = False
    for blk in list(blocks(ent)):
        rd = blk.get("minecraft:rideable")
        if not rd:
            continue
        fams = set(rd.get("family_types", []))
        if "player" in fams:
            mount = True
            rd["family_types"] = sorted(fams | {"war_soldier"})
            if "minecraft:input_ground_controlled" in blk:
                blk.setdefault("minecraft:is_saddled", {})
        elif fams and fams <= JOCKEY:
            del blk["minecraft:rideable"]
            log.append(f"{short}: removed zombie-jockey seat")

    # families
    for blk in blocks(ent):
        tf = blk.get("minecraft:type_family")
        if tf is not None:
            tf["family"] = fix_families(tf.get("family", []), short, group, mount)
    if "minecraft:type_family" not in base:
        base["minecraft:type_family"] = {"family": fix_families([], short, group, mount)}

    # tamed state gets an extra family so wild predators leave pets alone
    tame_groups = [g for g in groups.values() if "minecraft:is_tamed" in g]
    for g in tame_groups:
        fams = (g.get("minecraft:type_family") or base["minecraft:type_family"])["family"]
        g["minecraft:type_family"] = {"family": fams + ([] if "worldanimals_pet" in fams else ["worldanimals_pet"])}

    if role == "egg":
        return d, mount

    # targeting: wipe whatever was copied in, then add what this animal really does
    for blk in blocks(ent):
        for k in TARGET_KEYS:
            blk.pop(k, None)
    fights = role in ("defensive", "hunter", "apex")
    if fights:
        if not anywhere(ent, "minecraft:attack"):
            base["minecraft:attack"] = {"damage": dmg}
        if not anywhere(ent, "minecraft:behavior.melee_attack"):
            base["minecraft:behavior.melee_attack"] = {"priority": 3, "speed_multiplier": 1.2, "track_target": True}
        base["minecraft:behavior.hurt_by_target"] = {
            "priority": 1,
            "alert_same_type": group in ("large_mammals", "primates") and role == "defensive",
            "entity_types": [{"filters": NOT_ALLY, "max_dist": 32}],
        }
    wild_groups = [g for g in groups.values() if "minecraft:tameable" in g]
    nat = wild_targets(role, prey, humans)
    if nat:
        for g in (wild_groups or [base]):
            g["minecraft:behavior.nearest_attackable_target"] = copy.deepcopy(nat)
    for g in tame_groups:
        if fights:
            g["minecraft:behavior.owner_hurt_by_target"] = {"priority": 1, "entity_types": [{"filters": NOT_ALLY}]}
            g["minecraft:behavior.owner_hurt_target"] = {"priority": 2, "entity_types": [{"filters": NOT_ALLY}]}
            if dmg >= 4:
                g["minecraft:behavior.nearest_attackable_target"] = tame_targets()

    # ostrich flags (decor items, removed): the groups and the events that add them
    for gname in [g for g in groups if g.endswith("_flag")]:
        del groups[gname]
    for ename in [e for e in ent.get("events", {}) if e.endswith("_flag")]:
        del ent["events"][ename]
    prune_events(ent)

    # loot: point missing tables at a simple one for the group
    for blk in blocks(ent):
        lt = blk.get("minecraft:loot")
        if lt and not os.path.exists(os.path.join(SRC_BP, lt.get("table", ""))):
            lt["table"] = f"loot_tables/entities/wa_{group}.json"
    return d, mount


# ------------------------------------------------------------------ main
def rel(p, root):
    return os.path.relpath(p, root).replace(os.sep, "/")


def main():
    # hand-written files (manifests, scripts) are kept; everything generated is rebuilt
    for p in (BP, RP):
        os.makedirs(p, exist_ok=True)
        for f in os.listdir(p):
            if f in ("manifest.json", "scripts"):
                continue
            q = os.path.join(p, f)
            shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    shutil.copy2(os.path.join(SRC_BP, "pack_icon.png"), os.path.join(BP, "pack_icon.png"))

    # ---- entities
    ent_src = {}
    for root, _, files in os.walk(os.path.join(SRC_BP, "entities")):
        for f in files:
            d = load(os.path.join(root, f))
            ident = d["minecraft:entity"]["description"]["identifier"].split(":", 1)[1]
            ent_src[ident] = os.path.join(root, f)
    missing = KEPT - set(ent_src)
    assert not missing, missing
    mounts = set()
    os.makedirs(os.path.join(BP, "entities"))
    for short in sorted(KEPT):
        d, mount = build_entity(ent_src[short], short)
        if mount:
            mounts.add(short)
        sub = ROSTER[short][0] or "eggs"
        os.makedirs(os.path.join(BP, "entities", sub), exist_ok=True)
        dump(os.path.join(BP, "entities", sub, f"{short}.json"), d)
    log.append("mounts: " + ", ".join(sorted(mounts)))

    # ---- spawn rules
    os.makedirs(os.path.join(BP, "spawn_rules"))
    for f in sorted(os.listdir(os.path.join(SRC_BP, "spawn_rules"))):
        d = load(os.path.join(SRC_BP, "spawn_rules", f))
        ident = d["minecraft:spawn_rules"]["description"]["identifier"].split(":", 1)[1]
        if ident == "ornitorrinco":            # the old rule named an entity that doesn't exist: platypus never spawned
            ident = "ornitorrinco_original"
            d["minecraft:spawn_rules"]["description"]["identifier"] = f"{NS}:{ident}"
        if ident in KEPT:
            dump(os.path.join(BP, "spawn_rules", f"{ident}.json"), d)
        else:
            log.append(f"spawn rule dropped: {ident}")

    # ---- loot tables actually used
    used = set()
    for root, _, files in os.walk(os.path.join(BP, "entities")):
        for f in files:
            for m in re.finditer(r'"(loot_tables/[^"]+\.json)"', open(os.path.join(root, f)).read()):
                used.add(m.group(1))
    generic = {
        "birds": [("minecraft:feather", 0, 2), ("minecraft:chicken", 0, 1)],
        "big_cats": [("minecraft:leather", 0, 2)],
        "large_mammals": [("minecraft:leather", 0, 2), ("minecraft:beef", 1, 2)],
        "small_mammals": [("minecraft:rabbit_hide", 0, 1)],
        "primates": [("minecraft:leather", 0, 1)],
        "reptiles": [("minecraft:leather", 0, 1)],
        "sea_life": [("minecraft:cod", 0, 2)],
        "bugs": [],
    }
    for lt in sorted(used):
        out = os.path.join(BP, lt)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        src = os.path.join(SRC_BP, lt)
        if os.path.exists(src):
            d = clean(load(src), None)
            pools = []
            for pool in (d if d is not REMOVE else {}).get("pools", []):
                if pool.get("entries"):
                    pools.append(pool)
            dump(out, {"pools": pools})
        else:
            m = re.match(r"loot_tables/entities/wa_(\w+)\.json", lt)
            if not m:
                log.append(f"MISSING loot table {lt}")
                continue
            g = m.group(1)
            dump(out, {"pools": [{"rolls": 1, "entries": [{"type": "item", "name": n, "weight": 1, "functions": [
                {"function": "set_count", "count": {"min": a, "max": b}},
                {"function": "looting_enchant", "count": {"min": 0, "max": 1}}]}]} for n, a, b in generic[g]]})

    # ---- BP animations (Molang driven sounds etc.)
    shutil.copytree(os.path.join(SRC_BP, "animations"), os.path.join(BP, "animations"))

    # ---- RP
    build_rp(mounts)
    build_items_and_catalog()
    print("\n".join(log))


def walk_strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for v in o:
            yield from walk_strings(v)
    elif isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from walk_strings(v)


EGG_ICONS = {}


def build_rp(mounts):
    # client entities
    os.makedirs(os.path.join(RP, "entity"))
    refs = set()
    for f in sorted(os.listdir(os.path.join(SRC_RP, "entity"))):
        d = load(os.path.join(SRC_RP, "entity", f))
        desc = d["minecraft:client_entity"]["description"]
        short = desc["identifier"].split(":", 1)[1]
        if short not in KEPT:
            log.append(f"client entity dropped: {short}")
            continue
        if "spawn_egg" in desc and "texture" in desc["spawn_egg"]:
            EGG_ICONS[short] = desc["spawn_egg"]["texture"]
        refs |= set(walk_strings(desc))
        dump(os.path.join(RP, "entity", f"{short}.json"), d)

    def keep_json_dir(sub, top_key):
        """copy files from `sub` that define something referenced by the kept client entities"""
        src = os.path.join(SRC_RP, sub)
        kept = 0
        for root, _, files in os.walk(src):
            for f in files:
                p = os.path.join(root, f)
                try:
                    d = load(p)
                except Exception:
                    continue
                names = set()
                if top_key == "geometry":
                    for k, v in d.items():
                        if k.startswith("geometry."):
                            names.add(k.split(":")[0])
                    for g in d.get("minecraft:geometry", []):
                        names.add(g.get("description", {}).get("identifier", ""))
                else:
                    names = set(d.get(top_key, {}))
                if names & refs:
                    out = os.path.join(RP, rel(p, SRC_RP))
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    shutil.copy2(p, out)
                    kept += 1
                    refs.update(walk_strings(d))
        return kept

    keep_json_dir("animation_controllers", "animation_controllers")
    keep_json_dir("render_controllers", "render_controllers")
    keep_json_dir("animations", "animations")
    keep_json_dir("models", "geometry")

    # animations the original pack references but never defined (they only threw content-log errors): empty stubs
    have = set()
    for root, _, fs in os.walk(os.path.join(RP, "animations")):
        for f in fs:
            have |= set(load(os.path.join(root, f)).get("animations", {}))
    vanilla = re.compile(r"animation\.(common|llama|polarbear|quadruped|parrot|wolf|horse|chicken|cat|ocelot|dolphin|pig|"
                         r"cow|sheep|panda|fox|squid|turtle|bat|rabbit|bee|fish|cod|salmon)\.")
    stubs = {}
    for f in os.listdir(os.path.join(RP, "entity")):
        for a in load(os.path.join(RP, "entity", f))["minecraft:client_entity"]["description"].get("animations", {}).values():
            if a.startswith("animation.") and a not in have and not vanilla.match(a):
                stubs[a] = {"loop": True, "bones": {}}
    if stubs:
        dump(os.path.join(RP, "animations", "wa_missing_stubs.animation.json"),
             {"format_version": "1.8.0", "animations": dict(sorted(stubs.items()))})
        log.append(f"stubbed {len(stubs)} undefined animations")

    # textures referenced by kept client entities (and anything below textures/entity they point into)
    for s in list(refs):
        if s.startswith("textures/"):
            for ext in (".png", ".tga", ".jpg"):
                p = os.path.join(SRC_RP, s + ext)
                if os.path.exists(p):
                    out = os.path.join(RP, s + ext)
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    shutil.copy2(p, out)

    # particles referenced anywhere kept
    blob = "\n".join(refs)
    for f in os.listdir(os.path.join(SRC_RP, "particles")):
        pid = load(os.path.join(SRC_RP, "particles", f))["particle_effect"]["description"]["identifier"]
        if pid in blob:
            os.makedirs(os.path.join(RP, "particles"), exist_ok=True)
            shutil.copy2(os.path.join(SRC_RP, "particles", f), os.path.join(RP, "particles", f))

    # sounds: entity sound events of kept animals; every sound file referenced by the kept definitions
    snd = load(os.path.join(SRC_RP, "sounds.json"))
    ents = snd.get("entity_sounds", {}).get("entities", {})
    for k in list(ents):
        if k.startswith(NS + ":") and k.split(":", 1)[1] not in KEPT:
            del ents[k]
    dump(os.path.join(RP, "sounds.json"), snd)
    sd = load(os.path.join(SRC_RP, "sounds", "sound_definitions.json"))
    os.makedirs(os.path.join(RP, "sounds"), exist_ok=True)
    defs = sd.get("sound_definitions", sd)
    used_events = set(walk_strings(snd)) | set(walk_strings({"a": list(refs)}))
    for root, _, files in os.walk(os.path.join(SRC_BP, "animations")):
        for f in files:
            used_events |= set(re.findall(r"[a-z0-9_.]+", open(os.path.join(root, f)).read()))
    for k in list(defs):
        if k == "format_version":
            continue
        if k not in used_events:
            del defs[k]
    dump(os.path.join(RP, "sounds", "sound_definitions.json"), sd)
    for name in set(walk_strings(defs)):
        if name.startswith("sounds/"):
            for ext in (".ogg", ".fsb", ".wav"):
                p = os.path.join(SRC_RP, name + ext)
                if os.path.exists(p):
                    out = os.path.join(RP, name + ext)
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    shutil.copy2(p, out)

    # item atlas: only the egg icons
    it = load(os.path.join(SRC_RP, "textures", "item_texture.json"))
    data = {}
    for short, key in EGG_ICONS.items():
        if key in it["texture_data"]:
            data[key] = it["texture_data"][key]
            tex = data[key]["textures"]
            tex = tex if isinstance(tex, str) else tex[0]
            for ext in (".png", ".tga"):
                p = os.path.join(SRC_RP, tex + ext)
                if os.path.exists(p):
                    os.makedirs(os.path.dirname(os.path.join(RP, tex + ext)), exist_ok=True)
                    shutil.copy2(p, os.path.join(RP, tex + ext))
        else:
            log.append(f"no egg icon for {short} ({key})")
    dump(os.path.join(RP, "textures", "item_texture.json"),
         {"resource_pack_name": "World Animals", "texture_name": "atlas.items", "texture_data": data})

    # language files: names of the kept animals only
    os.makedirs(os.path.join(RP, "texts"))
    langs = []
    for f in sorted(os.listdir(os.path.join(SRC_RP, "texts"))):
        if not f.endswith(".lang"):
            continue
        lines = []
        for line in open(os.path.join(SRC_RP, "texts", f), encoding="utf-8-sig"):
            m = re.match(r"entity\.worldanimals:([a-z0-9_]+)\.name=", line)
            if m and m.group(1) in KEPT and f != "en_US.lang":
                lines.append(line.rstrip("\n"))
        if f == "en_US.lang":
            lines = [f"entity.{NS}:{s}.name={ROSTER[s][6]}" for s in sorted(KEPT)]
        for g, name in GROUPS.items():
            lines.append(f"{NS}:itemGroup.name.{g}={name}" if f == "en_US.lang" else f"{NS}:itemGroup.name.{g}={name}")
        open(os.path.join(RP, "texts", f), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
        langs.append(f[:-5])
    dump(os.path.join(RP, "texts", "languages.json"), langs)
    shutil.copy2(os.path.join(SRC_RP, "pack_icon.png"), os.path.join(RP, "pack_icon.png"))


def build_items_and_catalog():
    os.makedirs(os.path.join(BP, "items", "spawn_eggs"))
    os.makedirs(os.path.join(BP, "items", "laid_eggs"))
    by_group = {g: [] for g in GROUPS}
    for short in sorted(KEPT, key=lambda s: ROSTER[s][6]):
        group, role, *_rest, name = ROSTER[short]
        icon = EGG_ICONS.get(short)
        if role == "egg":
            ident, sub, label = egg_item(short), "laid_eggs", name
            menu = {"category": "none"}
        else:
            ident, sub, label = f"{NS}:spawn_{short}", "spawn_eggs", f"{name} Spawn Egg"
            menu = {"category": "nature", "group": f"{NS}:itemGroup.name.{group}"}
            by_group[group].append(ident)
        comps = {
            "minecraft:display_name": {"value": label},
            "minecraft:entity_placer": {"entity": f"{NS}:{short}"},
            "minecraft:max_stack_size": 64 if role != "egg" else 16,
        }
        if icon:
            comps["minecraft:icon"] = {"textures": {"default": icon}}
        dump(os.path.join(BP, "items", sub, f"{ident.split(':')[1]}.json"), {
            "format_version": "1.21.60",
            "minecraft:item": {"description": {"identifier": ident, "menu_category": menu}, "components": comps},
        })
    os.makedirs(os.path.join(BP, "item_catalog"))
    dump(os.path.join(BP, "item_catalog", "crafting_item_catalog.json"), {
        "format_version": "1.21.60",
        "minecraft:crafting_items_catalog": {"categories": [{"category_name": "nature", "groups": [
            {"group_identifier": {"icon": items[0], "name": f"{NS}:itemGroup.name.{g}"}, "items": items}
            for g, items in by_group.items() if items]}]},
    })


if __name__ == "__main__":
    main()
