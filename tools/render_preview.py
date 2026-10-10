"""Renders Bedrock entity models with their textures to PNG, so textures can be checked without the game.

usage: python3 -I tools/render_preview.py <out.png> <RP dir> <client entity id or file> [more ...]
       (several entities are laid out side by side, two views each)
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wa_common import load  # noqa: E402

FACES = ("north", "south", "east", "west", "up", "down")


def geometries(rp):
    out = {}
    for root, _, fs in os.walk(os.path.join(rp, "models")):
        for f in fs:
            try:
                d = load(os.path.join(root, f))
            except Exception:
                continue
            for g in d.get("minecraft:geometry", []):
                out[g["description"]["identifier"]] = g
            for k, v in d.items():
                if k.startswith("geometry."):
                    out[k.split(":")[0]] = {"description": {"texture_width": v.get("texturewidth", 64),
                                                            "texture_height": v.get("textureheight", 64)},
                                            "bones": v.get("bones", [])}
    return out


def rot_matrix(r):
    x, y, z = (math.radians(a) for a in r)
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    return rz @ ry @ rx


def box_uv(u, v, w, h, d):
    # Bedrock box UV layout -> per-face (u, v, uw, vh)
    return {
        "up": (u + d, v, w, d), "down": (u + d + w, v, w, d),
        "east": (u, v + d, d, h), "north": (u + d, v + d, w, h),
        "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h),
    }


def cube_faces(c):
    ox, oy, oz = c["origin"]
    w, h, d = c["size"]
    inf = c.get("inflate", 0)
    x0, y0, z0 = ox - inf, oy - inf, oz - inf
    x1, y1, z1 = ox + w + inf, oy + h + inf, oz + d + inf
    P = lambda x, y, z: np.array([x, y, z], float)
    quads = {   # corners: top-left, top-right, bottom-right, bottom-left (as seen from outside)
        "north": [P(x1, y1, z0), P(x0, y1, z0), P(x0, y0, z0), P(x1, y0, z0)],
        "south": [P(x0, y1, z1), P(x1, y1, z1), P(x1, y0, z1), P(x0, y0, z1)],
        "east": [P(x0, y1, z0), P(x0, y1, z1), P(x0, y0, z1), P(x0, y0, z0)],
        "west": [P(x1, y1, z1), P(x1, y1, z0), P(x1, y0, z0), P(x1, y0, z1)],
        "up": [P(x1, y1, z1), P(x0, y1, z1), P(x0, y1, z0), P(x1, y1, z0)],
        "down": [P(x1, y0, z0), P(x0, y0, z0), P(x0, y0, z1), P(x1, y0, z1)],
    }
    uv = c.get("uv", [0, 0])
    if isinstance(uv, dict):
        fuv = {}
        for f in FACES:
            if f in uv:
                a, b = uv[f]["uv"]
                s = uv[f].get("uv_size", [0, 0])
                fuv[f] = (a, b, s[0], s[1])
    else:
        fuv = box_uv(uv[0], uv[1], math.floor(w), math.floor(h), math.floor(d))
        if c.get("mirror"):
            fuv["east"], fuv["west"] = fuv["west"], fuv["east"]
    return [(quads[f], fuv[f], f) for f in FACES if f in fuv]


def world_faces(geo):
    bones = {b["name"]: b for b in geo.get("bones", [])}

    def chain(b):
        out = []
        while b is not None:
            out.append(b)
            b = bones.get(b.get("parent"))
        return out

    faces = []
    for b in geo.get("bones", []):
        if b.get("neverRender"):
            continue
        for c in b.get("cubes", []):
            for quad, uv, fname in cube_faces(c):
                pts = [p.copy() for p in quad]
                if "rotation" in c:
                    piv = np.array(c.get("pivot", [0, 0, 0]), float)
                    R = rot_matrix([-c["rotation"][0], -c["rotation"][1], c["rotation"][2]])
                    pts = [R @ (p - piv) + piv for p in pts]
                for bb in chain(b):
                    if "rotation" in bb:
                        piv = np.array(bb.get("pivot", [0, 0, 0]), float)
                        R = rot_matrix([-bb["rotation"][0], -bb["rotation"][1], bb["rotation"][2]])
                        pts = [R @ (p - piv) + piv for p in pts]
                faces.append((pts, uv, fname))
    return faces


def perspective_coeffs(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    try:
        return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()
    except np.linalg.LinAlgError:
        return None


def render(geo, tex, yaw, pitch=22, size=360):
    tw, th = geo["description"].get("texture_width", 64), geo["description"].get("texture_height", 64)
    sx, sy = tex.width / tw, tex.height / th
    faces = world_faces(geo)
    if not faces:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    R = rot_matrix([pitch, yaw, 0])
    allp = np.array([p for f in faces for p in f[0]])
    centre = (allp.min(0) + allp.max(0)) / 2
    proj = []
    for pts, uv, fname in faces:
        q = [R @ (p - centre) for p in pts]
        n = np.cross(q[1] - q[0], q[3] - q[0])
        proj.append((q, uv, fname, n))
    span = max(np.ptp(np.array([p for f in proj for p in f[0]])[:, :2], axis=0).max(), 1)
    k = size * 0.85 / span
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    light = {"up": 1.0, "north": 0.85, "south": 0.85, "east": 0.72, "west": 0.72, "down": 0.5}
    for q, uv, fname, n in sorted(proj, key=lambda f: sum(p[2] for p in f[0]) / 4, reverse=True):
        if n[2] > 0:          # facing away
            continue
        u, v, uw, vh = uv
        if abs(uw) < 1e-6 or abs(vh) < 1e-6:
            continue
        src = [(u * sx, v * sy), ((u + uw) * sx, v * sy), ((u + uw) * sx, (v + vh) * sy), (u * sx, (v + vh) * sy)]
        dst = [(size / 2 + p[0] * k, size / 2 - p[1] * k) for p in q]
        co = perspective_coeffs(dst, src)
        if not co:
            continue
        layer = tex.transform((size, size), Image.PERSPECTIVE, co, Image.NEAREST)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).polygon(dst, fill=255)
        a = np.array(layer)
        a[..., :3] = (a[..., :3] * light[fname]).astype(np.uint8)
        layer = Image.fromarray(a)
        m = np.minimum(np.array(mask), np.array(layer)[..., 3])
        layer.putalpha(Image.fromarray(m.astype(np.uint8)))
        canvas.alpha_composite(layer)
    return canvas


def client_entity(rp, ref):
    p = ref if ref.endswith(".json") else os.path.join(rp, "entity", ref.split(":")[-1] + ".json")
    return load(p)["minecraft:client_entity"]["description"]


def main():
    out, rp, refs = sys.argv[1], sys.argv[2], sys.argv[3:]
    geos = geometries(rp)
    tiles = []
    for ref in refs:
        desc = client_entity(rp, ref)
        gid = desc["geometry"].get("default") or list(desc["geometry"].values())[0]
        tpath = desc["textures"].get("default") or list(desc["textures"].values())[0]
        tex = None
        for ext in (".png", ".tga"):
            if os.path.exists(os.path.join(rp, tpath + ext)):
                tex = Image.open(os.path.join(rp, tpath + ext)).convert("RGBA")
        if tex is None or gid not in geos:
            print("skip", ref, gid, tpath)
            continue
        a = render(geos[gid], tex, yaw=-35)
        b = render(geos[gid], tex, yaw=145)
        tile = Image.new("RGBA", (720, 390), (236, 236, 230, 255))
        tile.alpha_composite(a, (0, 0)); tile.alpha_composite(b, (360, 0))
        ImageDraw.Draw(tile).text((8, 372), desc["identifier"].split(":")[-1], fill=(20, 20, 20, 255))
        tiles.append(tile)
    cols = 2
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (720 * cols, 390 * rows), (255, 255, 255, 255))
    for i, t in enumerate(tiles):
        sheet.alpha_composite(t, ((i % cols) * 720, (i // cols) * 390))
    sheet.convert("RGB").save(out)
    print(out)


if __name__ == "__main__":
    main()


def contact_sheet(out, rp, ids, cols=5, tile=300):
    """one 3/4 view per entity, labelled, in a grid"""
    geos = geometries(rp)
    tiles = []
    for ref in ids:
        try:
            desc = client_entity(rp, ref)
        except Exception:
            continue
        gid = desc["geometry"].get("default") or list(desc["geometry"].values())[0]
        tpath = desc["textures"].get("default") or list(desc["textures"].values())[0]
        tex = next((Image.open(os.path.join(rp, tpath + e)).convert("RGBA") for e in (".png", ".tga")
                    if os.path.exists(os.path.join(rp, tpath + e))), None)
        t = Image.new("RGBA", (tile, tile + 18), (236, 236, 230, 255))
        if tex is not None and gid in geos:
            t.alpha_composite(render(geos[gid], tex, yaw=-35, size=tile))
        ImageDraw.Draw(t).text((6, tile + 3), ref, fill=(20, 20, 20, 255))
        tiles.append(t)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (tile * cols, (tile + 18) * rows), (255, 255, 255, 255))
    for i, t in enumerate(tiles):
        sheet.alpha_composite(t, ((i % cols) * tile, (i // cols) * (tile + 18)))
    sheet.convert("RGB").save(out)
    return out
