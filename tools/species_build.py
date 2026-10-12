"""Resource-pack side of the new species: client entity, recolored textures, reshaped geometry, egg icon."""
import copy
import math
import os

from PIL import Image

import random

import numpy as np

from recolor import recolor, egg_icon, ramp_lookup
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


def free_rects(img, tw, th, sizes):
    """find empty (fully transparent) spots in the texture for new paint: {name: (w, h)} in UV units -> {name: (u, v)}"""
    a = np.array(img.convert("RGBA"))[..., 3] > 0
    px = img.width / tw
    used = np.zeros((th, tw), bool)
    for v in range(th):
        for u in range(tw):
            y0, x0 = int(v * px), int(u * px)
            used[v, u] = a[y0:int((v + 1) * px), x0:int((u + 1) * px)].any()
    out = {}
    for name, (w, h) in sorted(sizes.items(), key=lambda kv: -kv[1][0] * kv[1][1]):
        done = False
        for v in range(th - h + 1):
            for u in range(tw - w + 1):
                if not used[v:v + h, u:u + w].any():
                    used[v:v + h, u:u + w] = True
                    out[name] = (u, v)
                    done = True
                    break
            if done:
                break
        if not done:
            raise ValueError(f"no room in the texture for patch {name}")
    return out


def paint_patch(img, rect, size, spec, tw, seed):
    """paint a patch: a ramp with soft vertical shading, grain and darker edges (bone, horn, fur)"""
    px = img.width / tw
    u, v = rect
    w, h = size
    x0, y0, x1, y1 = int(u * px), int(v * px), int((u + w) * px), int((v + h) * px)
    rng = random.Random(seed)
    arr = np.array(img.convert("RGBA")).astype(float)
    for y in range(y0, y1):
        for x in range(x0, x1):
            ty = (y - y0 + .5) / (y1 - y0)
            edge = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            t = spec.get("base", 0.55) + 0.25 * (0.5 - ty) + rng.uniform(-1, 1) * spec.get("grain", 0.12)
            if edge < 1:
                t -= 0.22
            arr[y, x, :3] = ramp_lookup(spec["ramp"], np.array([t]))[0]
            arr[y, x, 3] = 255
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


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
        tex_default = desc["textures"].get("default") or next(iter(desc["textures"].values()))
        src_default = next((os.path.join(src_rp, tex_default + e) for e in (".png", ".tga")
                            if os.path.exists(os.path.join(src_rp, tex_default + e))), None)
        tweak = copy.deepcopy(sp.get("geo") or {})
        patch_at = {}
        if tweak.get("patches") and geo and src_default:
            tw = geo["description"].get("texture_width", 64)
            th = geo["description"].get("texture_height", 64)
            patch_at = free_rects(Image.open(src_default), tw, th,
                                  {k: tuple(p["size"]) for k, p in tweak["patches"].items()})
            for add in tweak.get("add", []):
                if "patch" in add:
                    add["uv"] = list(patch_at[add["patch"]])
                    add["uv_size"] = list(tweak["patches"][add["patch"]]["size"])
        if sp.get("geo") and geo:
            new_gid = f"geometry.wa_{sid}"
            g = reshape(geo, new_gid, tweak)
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
        single = rec.get("single")
        for key, path in desc["textures"].items():
            if single and key != "default" and not any(k in key.lower() or k in path.lower() for k in KEEP_TEXTURE):
                continue
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
            out_img = recolor(Image.open(src), rec, seed=hash(sid) & 0xffff)
            if patch_at:
                tw = geo["description"].get("texture_width", 64)
                for i, (name, pspec) in enumerate(tweak["patches"].items()):
                    out_img = paint_patch(out_img, patch_at[name], pspec["size"], pspec, tw, seed=i * 31 + len(sid))
            out_img.save(os.path.join(rp, out_rel + ".png"))
            new_tex[key] = out_rel
        if single:      # every coat variant shows the one recolored coat
            for key, path in desc["textures"].items():
                if key not in new_tex:
                    new_tex[key] = new_tex["default"]
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
