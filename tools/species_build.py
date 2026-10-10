"""Resource-pack side of the new species: client entity, recolored textures, reshaped geometry, egg icon."""
import copy
import math
import os

from PIL import Image

from recolor import recolor, egg_icon
from render_preview import geometries
from wa_common import dump

NS = "worldanimals"
KEEP_TEXTURE = ("saddle", "armor", "scarf", "bufanda", "astronaut", "flag", "demo", "chest")


def _box_to_faces(c):
    """box UV -> explicit per-face UV (so a resized cube keeps sampling the same texture area)"""
    uv = c.get("uv", [0, 0])
    if isinstance(uv, dict):
        return
    w, h, d = (math.floor(v) for v in c["size"])
    u, v = uv
    faces = {"north": ([u + d, v + d], [w, h]), "east": ([u, v + d], [d, h]), "south": ([u + 2 * d + w, v + d], [w, h]),
             "west": ([u + d + w, v + d], [d, h]), "up": ([u + d + w, v + d], [-w, -d]),
             "down": ([u + 2 * d + w, v], [-w, d])}
    faces["up"] = ([u + d + w, v + d], [-w, -d])
    faces["down"] = ([u + 2 * d + w, v], [-w, d])
    if c.get("mirror"):
        faces["east"], faces["west"] = faces["west"], faces["east"]
    c["uv"] = {k: {"uv": a, "uv_size": b} for k, (a, b) in faces.items()}
    c.pop("mirror", None)


def reshape(geo, new_id, tweak):
    """scale_bones: {bone: [x, y, z]} scales a bone and everything under it about that bone's pivot
    hide: [bones] drops their cubes (and their children's)
    horns: {"bone", "length", "spread", "tilt", "uv"} replaces antlers with two straight horns on that bone"""
    g = copy.deepcopy(geo)
    g["description"]["identifier"] = new_id
    bones = {b["name"]: b for b in g.get("bones", [])}

    def ancestors(b):
        out = []
        while b is not None:
            out.append(b)
            b = bones.get(b.get("parent"))
        return out

    hide = set(tweak.get("hide", []))
    scales = tweak.get("scale_bones", {})
    for b in g.get("bones", []):
        chain = ancestors(b)
        if any(x["name"] in hide for x in chain):
            b["cubes"] = []
            continue
        owner = next((x for x in chain if x["name"] in scales), None)
        if not owner:
            continue
        s = scales[owner["name"]]
        piv = owner.get("pivot", [0, 0, 0])
        sc = lambda p: [piv[i] + (p[i] - piv[i]) * s[i] for i in range(3)]
        if b is not owner and "pivot" in b:
            b["pivot"] = sc(b["pivot"])
        for c in b.get("cubes", []):
            _box_to_faces(c)
            c["origin"] = sc(c["origin"])
            c["size"] = [c["size"][i] * s[i] for i in range(3)]
            if "pivot" in c:
                c["pivot"] = sc(c["pivot"])
    for add in tweak.get("add", []):               # extra cubes: {bone, origin, size, rotation?, pivot?, uv: [u, v]}
        u, v = add.get("uv", [24, 48])
        face = {f: {"uv": [u, v], "uv_size": add.get("uv_size", [1, 1])}
                for f in ("north", "south", "east", "west", "up", "down")}
        cube = {"origin": add["origin"], "size": add["size"], "uv": face}
        if "rotation" in add:
            cube["rotation"] = add["rotation"]
            cube["pivot"] = add.get("pivot", add["origin"])
        bones[add["bone"]].setdefault("cubes", []).append(cube)
    h = tweak.get("horns")
    if h:
        hb = bones[h.get("bone", "cuernos")]
        px, py, pz = hb.get("pivot", [0, 0, 0])
        u, v = h.get("uv", [24, 48])
        face = {f: {"uv": [u, v], "uv_size": [1, 1]} for f in ("north", "south", "east", "west", "up", "down")}
        L, sp, tilt = h.get("length", 4), h.get("spread", 1.2), h.get("tilt", -25)
        for side in (1, -1):
            x = px + side * sp
            hb.setdefault("cubes", []).append({"origin": [x - 0.5, py - 0.5, pz - 0.5], "size": [1, L, 1],
                                               "pivot": [x, py, pz], "rotation": [tilt, 0, -side * h.get("splay", 8)],
                                               "uv": copy.deepcopy(face)})
    return g


def bone_areas(geo, prefixes, tw, th):
    """texture rectangles (fractions) used by the bones whose names start with any prefix"""
    out = []
    for b in geo.get("bones", []):
        if not any(b["name"].startswith(p) for p in prefixes):
            continue
        for c in b.get("cubes", []):
            uv = c.get("uv", [0, 0])
            if isinstance(uv, dict):
                for f in uv.values():
                    (u, v), (w, h) = f["uv"], f.get("uv_size", [0, 0])
                    u0, u1 = sorted((u, u + w)); v0, v1 = sorted((v, v + h))
                    out.append((u0 / tw, v0 / th, u1 / tw, v1 / th))
            else:
                w, h, d = (math.floor(x) for x in c["size"])
                out.append((uv[0] / tw, uv[1] / th, (uv[0] + 2 * (w + d)) / tw, (uv[1] + d + h) / th))
    return out


def build_species_rp(species, src_rp, rp, base_descs, refs, egg_icons, extra_item_tex, log):
    geos = geometries(src_rp)
    for sid, sp in sorted(species.items()):
        if sp.get("dog"):
            continue
        base = base_descs[sp["base"]]
        d = copy.deepcopy(base)
        desc = d["minecraft:client_entity"]["description"]
        desc["identifier"] = f"{NS}:{sid}"
        rec = dict(sp["recipe"])
        # geometry: reshaped copy if asked
        gid = desc["geometry"].get("default")
        geo = geos.get(gid)
        if sp.get("geo") and geo:
            new_gid = f"geometry.wa_{sid}"
            g = reshape(geo, new_gid, sp["geo"])
            dump(os.path.join(rp, "models", "entity", "wa_species", f"{sid}.geo.json"),
                 {"format_version": "1.12.0", "minecraft:geometry": [g]})
            desc["geometry"] = {k: (new_gid if v == gid else v) for k, v in desc["geometry"].items()}
        # body-part ramps -> texture areas
        if rec.get("bones") and geo:
            tw = geo["description"].get("texture_width", 64)
            th = geo["description"].get("texture_height", 64)
            areas = list(rec.get("areas", []))
            for prefixes, ramp in rec["bones"].items():
                for a in bone_areas(geo, prefixes, tw, th):
                    areas.append((*a, ramp))
            rec["areas"] = areas
        # textures
        new_tex = {}
        for key, path in desc["textures"].items():
            if any(k in key.lower() or k in path.lower() for k in KEEP_TEXTURE):
                new_tex[key] = path
                continue
            src = next((os.path.join(src_rp, path + e) for e in (".png", ".tga")
                        if os.path.exists(os.path.join(src_rp, path + e))), None)
            if not src:
                new_tex[key] = path
                continue
            out_rel = f"textures/entity/wa_species/{sid}/{key}"
            os.makedirs(os.path.dirname(os.path.join(rp, out_rel)), exist_ok=True)
            recolor(Image.open(src), rec, seed=hash(sid) & 0xffff).save(os.path.join(rp, out_rel + ".png"))
            new_tex[key] = out_rel
        desc["textures"] = new_tex
        # size: render scale (the behaviour file scales the hitbox)
        scale = sp.get("scale", 1.0)
        if abs(scale - 1.0) > 1e-3:
            scripts = desc.setdefault("scripts", {})
            old = scripts.get("scale")
            scripts["scale"] = f"({old}) * {scale}" if old else str(scale)
        # egg icon
        ramp = rec["ramp"]
        key = f"wa_egg_{sid}"
        egg_rel = f"textures/items/wa_eggs/{sid}"
        os.makedirs(os.path.dirname(os.path.join(rp, egg_rel)), exist_ok=True)
        egg_icon(ramp[2], ramp[0] if sum(int(ramp[2][i:i + 2], 16) for i in (1, 3, 5)) > 300 else ramp[-1],
                 seed=hash(sid) & 0xff).save(os.path.join(rp, egg_rel + ".png"))
        extra_item_tex[key] = {"textures": egg_rel}
        desc["spawn_egg"] = {"texture": key, "texture_index": 0}
        egg_icons[sid] = key
        refs |= set(_walk(desc))
        dump(os.path.join(rp, "entity", f"{sid}.json"), d)
    log.append(f"species client entities: {sum(1 for s in species.values() if not s.get('dog'))}")


def _walk(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)
    elif isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from _walk(v)
