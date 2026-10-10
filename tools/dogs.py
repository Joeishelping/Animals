"""Dogs (and the wild dogs) on a model of their own: geometry from breed proportions, coats painted from breed
markings, own animations, and a pet behaviour file that the main rebuild then runs through the usual pipeline.

Coordinates: pixels (1/16 block), the dog faces -Z, feet at y = 0.
"""
import copy
import math
import os
import random

import numpy as np
from PIL import Image

from wa_common import dump

NS = "worldanimals"
TEX = 128          # UV space (the image is TEX * RES pixels)

# ------------------------------------------------------------------ breeds
# leg: leg height; body: [width, height, length]; head: [w, h, d]; snout: [w, h, length]
# ears: pointy | tall | bat | floppy | fold | long ; tail: up | down | curl | stub | fluffy | sickle
BREEDS = {
    "german_shepherd": dict(name="German Shepherd", origin="Germany", leg=8, body=[6, 6, 12], head=[6, 6, 5],
                            snout=[3, 3, 4], ears="tall", tail="down", scale=1.0, dmg=5, coat="gsd"),
    "toy_poodle": dict(name="Toy Poodle", origin="France / Germany", leg=7, body=[5, 5, 8], head=[5, 5, 4],
                       snout=[2, 2, 3], ears="long", tail="pompom", scale=0.55, dmg=1, coat="poodle", puffs=True),
    "chihuahua": dict(name="Chihuahua", origin="Mexico", leg=5, body=[5, 5, 7], head=[6, 5, 5], snout=[2, 2, 2],
                      ears="bat", tail="sickle", scale=0.45, dmg=1, coat="chihuahua"),
    "shiba_inu": dict(name="Shiba Inu", origin="Japan", leg=6, body=[6, 6, 10], head=[6, 5, 5], snout=[3, 2, 3],
                      ears="pointy", tail="curl", scale=0.75, dmg=3, coat="shiba"),
    "airedale_terrier": dict(name="Airedale Terrier", origin="England", leg=8, body=[5, 6, 11], head=[5, 6, 5],
                             snout=[4, 4, 5], ears="fold", tail="up", scale=0.9, dmg=4, coat="airedale"),
    "golden_retriever": dict(name="Golden Retriever", origin="Scotland", leg=7, body=[6, 6, 12], head=[6, 6, 5],
                             snout=[3, 3, 4], ears="floppy", tail="fluffy", scale=1.0, dmg=4, coat="golden"),
    "labrador": dict(name="Labrador Retriever", origin="Canada", leg=7, body=[6, 6, 12], head=[6, 6, 5],
                     snout=[3, 3, 4], ears="floppy", tail="down", scale=1.0, dmg=4, coat="lab"),
    "siberian_husky": dict(name="Siberian Husky", origin="Russia (Siberia)", leg=7, body=[6, 6, 11], head=[6, 6, 5],
                           snout=[3, 3, 4], ears="pointy", tail="curl", scale=0.95, dmg=4, coat="husky"),
    "beagle": dict(name="Beagle", origin="England", leg=5, body=[5, 5, 9], head=[5, 5, 4], snout=[3, 3, 3],
                   ears="long", tail="up", scale=0.7, dmg=2, coat="beagle"),
    "dachshund": dict(name="Dachshund", origin="Germany", leg=3, body=[5, 5, 13], head=[5, 5, 4], snout=[2, 2, 4],
                      ears="long", tail="down", scale=0.6, dmg=2, coat="dachshund"),
    "dalmatian": dict(name="Dalmatian", origin="Croatia", leg=8, body=[6, 6, 12], head=[6, 6, 5], snout=[3, 3, 4],
                      ears="floppy", tail="down", scale=1.0, dmg=4, coat="dalmatian"),
    "border_collie": dict(name="Border Collie", origin="Scotland / England", leg=7, body=[5, 6, 11], head=[5, 5, 5],
                          snout=[3, 3, 4], ears="fold", tail="fluffy", scale=0.9, dmg=3, coat="collie"),
    "rottweiler": dict(name="Rottweiler", origin="Germany", leg=8, body=[7, 7, 12], head=[7, 6, 5], snout=[4, 4, 3],
                       ears="floppy", tail="stub", scale=1.1, dmg=6, coat="rottweiler"),
    "korean_jindo": dict(name="Korean Jindo", origin="Korea", leg=7, body=[6, 6, 11], head=[6, 5, 5], snout=[3, 3, 3],
                         ears="pointy", tail="curl", scale=0.85, dmg=4, coat="jindo"),
    "doberman": dict(name="Doberman", origin="Germany", leg=9, body=[5, 6, 12], head=[5, 5, 5], snout=[3, 3, 5],
                     ears="tall", tail="stub", scale=1.05, dmg=5, coat="doberman"),
    # wild dogs (same model)
    "coyote": dict(name="Coyote", leg=8, body=[5, 6, 11], head=[5, 5, 5], snout=[3, 3, 5], ears="tall", tail="fluffy_down",
                   scale=0.85, coat="coyote", wild=True),
    "fennec": dict(name="Fennec Fox", leg=5, body=[5, 5, 8], head=[5, 4, 4], snout=[2, 2, 3], ears="huge",
                   tail="fluffy_down", scale=0.45, coat="fennec", wild=True),
    "dhole": dict(name="Dhole", leg=7, body=[6, 6, 11], head=[6, 5, 5], snout=[3, 3, 4], ears="pointy",
                  tail="fluffy_down", scale=0.85, coat="dhole", wild=True),
    "wild_dog": dict(name="African Wild Dog", leg=9, body=[6, 6, 11], head=[6, 5, 5], snout=[3, 3, 4], ears="round",
                     tail="fluffy_down", scale=0.9, coat="wild_dog", wild=True),
}


# ------------------------------------------------------------------ geometry
class Packer:
    """allocates box-UV rectangles in a TEX x TEX atlas (shelf packing)"""

    def __init__(self):
        self.x = self.y = self.shelf = 0

    def place(self, w, h, d):
        rw, rh = 2 * (w + d), d + h
        if self.x + rw > TEX:
            self.x, self.y, self.shelf = 0, self.y + self.shelf, 0
        u, v = self.x, self.y
        self.x += rw
        self.shelf = max(self.shelf, rh)
        if self.y + rh > TEX:
            raise ValueError("dog atlas full")
        return [u, v]


def geometry(bid, b):
    P = Packer()
    cubes = []          # (bone, part, origin, size, uv, extra)

    def cube(bone, part, origin, size, **kw):
        size = [max(1, int(round(s))) for s in size]
        uv = P.place(*size)
        cubes.append(dict(bone=bone, part=part, origin=[round(o, 3) for o in origin], size=size, uv=uv, **kw))

    L = b["leg"]
    bw, bh, bl = b["body"]
    hw, hh, hd = b["head"]
    sw, sh, sl = b["snout"]
    top = L + bh
    z0 = -bl / 2
    # body: horizontal; chest a bit taller than the hips
    cube("body", "body", [-bw / 2, L, z0], [bw, bh, bl])
    cube("upperBody", "chest", [-bw / 2 - 0.5, L - 0.5, z0 - 0.5], [bw + 1, bh + 1, max(4, bl // 2 - 1)])
    # neck and head, the head set forward and a little above the back
    hy = top - 2
    hz = z0 - hd + 1
    cube("upperBody", "neck", [-(bw - 2) / 2, top - 3, z0 - 1.5], [max(2, bw - 2), 4, 3])
    cube("head", "head", [-hw / 2, hy, hz], [hw, hh, hd])
    cube("head", "snout", [-sw / 2, hy + 1, hz - sl], [sw, max(1, sh - 1), sl])
    cube("head", "jaw", [-(sw - 1) / 2, hy, hz - sl + 0.5], [max(1, sw - 1), 1, sl - 0.5])
    cube("head", "nose", [-1, hy + sh - 1, hz - sl - 0.5], [2, 1, 1])
    ears = b["ears"]
    ey = hy + hh
    if ears in ("pointy", "tall", "huge", "bat", "round"):
        size = {"pointy": [2, 2, 1], "tall": [2, 3, 1], "huge": [3, 5, 1], "bat": [3, 4, 1], "round": [3, 3, 1]}[ears]
        for sx in (-1, 1):
            x = sx * (hw / 2 - size[0] / 2) - size[0] / 2
            if ears == "bat":
                x = sx * (hw / 2) - size[0] / 2
            cube("head", "ear", [x, ey, hz + hd - 2], size)
    elif ears in ("floppy", "long", "fold"):
        h = {"floppy": 4, "long": 5, "fold": 2}[ears]
        for sx in (-1, 1):
            x = sx * (hw / 2 + 0.5) - 0.5
            y = ey - h if ears != "fold" else ey - 1
            cube("head", "ear", [x, y, hz + 1], [1, h, 2 if ears != "long" else 3])
    # legs
    for i, (lx, lz) in enumerate([(-bw / 2 + 0.5, bl / 2 - 2.5), (bw / 2 - 2.5, bl / 2 - 2.5),
                                  (-bw / 2 + 0.5, z0 + 0.5), (bw / 2 - 2.5, z0 + 0.5)]):
        cube(f"leg{i}", "leg", [lx, 1, lz], [2, L - 1, 2])
        cube(f"leg{i}", "paw", [lx - 0.25, 0, lz - 0.5], [2, 1, 3] if L > 3 else [2, 1, 2])
        if b.get("puffs"):
            cube(f"leg{i}", "puff", [lx - 0.5, 0, lz - 0.5], [3, 2, 3])
    # tail
    t = b["tail"]
    tz = bl / 2
    if t == "stub":
        cube("tail", "tail", [-1, top - 2, tz], [2, 2, 2])
    elif t == "curl":
        cube("tail", "tail", [-1, top, tz - 2], [2, 2, 3])
        cube("tail", "tail", [-1, top + 2, tz - 3], [2, 2, 2])
    elif t == "pompom":
        cube("tail", "tail", [-0.5, top - 1, tz], [1, 3, 1])
        cube("tail", "puff", [-1.5, top + 2, tz - 0.5], [3, 3, 3])
    elif t in ("fluffy", "fluffy_down"):
        cube("tail", "tail", [-1, top - 3, tz], [2, 3, 2])
        cube("tail", "tailtip", [-1.5, top - 8, tz - 0.5], [3, 5, 3])
    elif t == "up":
        cube("tail", "tail", [-1, top - 1, tz], [2, 3, 2])
        cube("tail", "tailtip", [-0.5, top + 2, tz + 0.5], [1, 3, 1])
    elif t == "sickle":
        cube("tail", "tail", [-0.5, top - 1, tz], [1, 5, 1])
    else:   # down
        cube("tail", "tail", [-1, top - 4, tz], [2, 4, 2])
        cube("tail", "tailtip", [-0.5, top - 8, tz + 0.5], [1, 4, 1])
    if b.get("puffs"):
        cube("head", "puff", [-hw / 2 + 0.5, ey - 1, hz + 1], [hw - 1, 2, hd - 2])

    pivots = {
        "body": [0, top, 0], "upperBody": [0, top, z0], "head": [0, hy + hh / 2, hz + hd],
        "leg0": [-bw / 2 + 1.5, L, bl / 2 - 1.5], "leg1": [bw / 2 - 1.5, L, bl / 2 - 1.5],
        "leg2": [-bw / 2 + 1.5, L, z0 + 1.5], "leg3": [bw / 2 - 1.5, L, z0 + 1.5],
        "tail": [0, top - 1, tz],
    }
    bones = [{"name": "root", "pivot": [0, 0, 0]}]
    for name in ("body", "upperBody", "head", "leg0", "leg1", "leg2", "leg3", "tail"):
        bone = {"name": name, "parent": "root" if name != "upperBody" else "body", "pivot": pivots[name], "cubes": []}
        if name == "head":
            bone["locators"] = {"lead": pivots["head"]}
        for c in cubes:
            if c["bone"] == name:
                e = {"origin": c["origin"], "size": c["size"], "uv": c["uv"]}
                if c["part"] == "puff":
                    e["inflate"] = 0.4
                bone["cubes"].append(e)
        if name == "tail" and t == "curl":
            bone["rotation"] = [-30, 0, 0]
        elif name == "tail" and t in ("up", "sickle"):
            bone["rotation"] = [-35, 0, 0]
        elif name == "tail" and t == "fluffy":
            bone["rotation"] = [25, 0, 0]
        elif name == "tail" and t in ("down", "fluffy_down"):
            bone["rotation"] = [15, 0, 0]
        bones.append(bone)
    geo = {"description": {"identifier": f"geometry.wa_dog_{bid}", "texture_width": TEX, "texture_height": TEX,
                           "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0, 0.75, 0]},
           "bones": bones}
    return geo, cubes, dict(L=L, top=top, z0=z0, bl=bl, hy=hy, hz=hz, hd=hd, hh=hh, sl=sl)


# ------------------------------------------------------------------ coats
def hx(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def coat(name):
    """returns f(part, face, nx, ny, nz, world) -> rgb ; nx/ny/nz are 0..1 inside the cube, ny=1 top"""
    C = {k: hx(v) for k, v in dict(
        black="#1b1a1a", dark="#2a2420", tan="#b8783a", cream="#efe2c8", white="#f2f0ea", gold="#d9a24a",
        red="#b8582a", grey="#7c7c80", fawn="#d6b07a", choc="#5a3a24", liver="#6a3a22", apricot="#e8b882",
        rust="#a84a1e", sand="#d8c4a0", tawny="#a8885e").items()}

    def mix(a, b, t):
        return a * (1 - t) + b * t

    def f(part, face, nx, ny, nz, w):
        under = face == "down" or (part in ("body", "chest") and ny < 0.3)
        front = face == "north"
        if name == "gsd":
            if part in ("body", "chest") and ny > 0.45 and face != "down":
                return C["black"]
            if part == "snout" or part == "ear":
                return C["black"]
            if part == "tail":
                return C["black"] if ny > 0.4 else C["tan"]
            if part == "head" and ny > 0.6:
                return mix(C["tan"], C["black"], 0.5)
            return C["tan"]
        if name == "poodle":
            return C["white"] if part != "nose" else C["black"]
        if name == "chihuahua":
            if part in ("body", "chest") and under:
                return C["cream"]
            return C["fawn"]
        if name == "shiba":
            if part == "snout" or (part == "head" and front and ny < 0.45) or under or \
                    (part == "chest" and front) or (part == "tail" and face == "up") or \
                    (part == "leg" and ny < 0.35):
                return C["cream"]
            return C["red"]
        if name == "airedale":
            if part in ("body", "chest") and ny > 0.5 and face != "down":
                return C["black"]
            if part == "tail":
                return C["black"]
            return C["tan"]
        if name == "golden":
            return mix(C["gold"], C["cream"], 0.25 if under else 0.0)
        if name == "lab":
            return hx("#1c1a19") if w["v"] == 0 else (hx("#e2c38e") if w["v"] == 1 else C["choc"])
        if name == "husky":
            if part == "snout" or under or (part == "head" and front and ny < 0.6) or (part == "leg") or \
                    (part == "chest" and front) or (part == "tail" and face == "down"):
                return C["white"]
            return C["grey"] if w["v"] == 0 else C["dark"]
        if name == "beagle":
            if part in ("body",) and ny > 0.5 and face != "down":
                return C["black"]
            if part == "leg" or under or part == "snout" or (part == "tail" and ny > 0.7) or \
                    (part == "chest" and front):
                return C["white"]
            return C["tan"]
        if name == "dachshund":
            return C["rust"] if w["v"] == 0 else (C["black"] if part not in ("snout", "leg") else C["tan"])
        if name == "dalmatian":
            return C["white"]
        if name == "collie":
            if (part == "snout") or (part == "head" and front and 0.35 < nx < 0.65) or (part == "chest") or \
                    (part == "leg" and ny < 0.5) or (part == "tail" and ny < 0.25) or under:
                return C["white"]
            return C["black"]
        if name in ("rottweiler", "doberman"):
            if part == "snout" or (part == "leg" and ny < 0.4) or (part == "chest" and front and ny < 0.6) or \
                    (part == "head" and front and ny > 0.55 and (nx < 0.3 or nx > 0.7)):
                return hx("#9a5a28")
            return C["black"] if name == "rottweiler" or w["v"] == 0 else hx("#5a2e1a")
        if name == "jindo":
            if w["v"] == 0:
                return C["white"]
            if part == "snout" or under or (part == "leg" and ny < 0.4):
                return C["cream"]
            return hx("#c87a3c")
        if name == "coyote":
            if under or part == "snout" and face == "down":
                return C["cream"]
            if part in ("body", "chest") and ny > 0.6:
                return mix(C["tawny"], C["grey"], 0.5)
            return C["tawny"]
        if name == "fennec":
            return C["cream"] if not (part == "tail" and ny < 0.2) else C["dark"]
        if name == "dhole":
            if under or (part == "snout" and face == "down"):
                return C["cream"]
            if part == "tail" and ny < 0.6:
                return C["dark"]
            return C["rust"]
        if name == "wild_dog":
            return w["blotch"]
        return C["tan"]
    return f


RES = 2            # texture pixels per model pixel
ALIAS = {"neck": "chest", "jaw": "snout", "paw": "leg", "tailtip": "tail", "puff": "puff"}


def _hash(x, y, z, seed):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(z) * 2147483647 + seed * 1442695041) & 0xffffffff
    h = (h ^ (h >> 13)) * 1274126177 & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffff) / 65535.0


def noise3(x, y, z, seed):
    """smooth value noise"""
    xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    sm = lambda t: t * t * (3 - 2 * t)
    u, v, w = sm(xf), sm(yf), sm(zf)
    acc = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                wt = (u if dx else 1 - u) * (v if dy else 1 - v) * (w if dz else 1 - w)
                acc += wt * _hash(xi + dx, yi + dy, zi + dz, seed)
    return acc


def paint(bid, b, cubes, variant=0, seed=1):
    rng = random.Random(seed * 7919 + variant)
    R = RES
    img = np.zeros((TEX * R, TEX * R, 4), float)
    f = coat(b["coat"])
    blotch_cols = [hx("#1a1714"), hx("#c89a4a"), hx("#efe6d2"), hx("#6a4a2a")]
    for c in cubes:
        w, h, d = c["size"]
        u, v = c["uv"]
        ox, oy, oz = c["origin"]
        part = ALIAS.get(c["part"], c["part"])
        faces = {
            "up": (u + d, v, w, d, lambda i, j: (i / w, 1.0, j / d)),
            "down": (u + d + w, v, w, d, lambda i, j: (i / w, 0.0, j / d)),
            "east": (u, v + d, d, h, lambda i, j: (0.0, 1 - j / h, i / d)),
            "north": (u + d, v + d, w, h, lambda i, j: (1 - i / w, 1 - j / h, 0.0)),
            "west": (u + d + w, v + d, d, h, lambda i, j: (1.0, 1 - j / h, 1 - i / d)),
            "south": (u + 2 * d + w, v + d, w, h, lambda i, j: (i / w, 1 - j / h, 1.0)),
        }
        for fname, (fu, fv, fw, fh, m) in faces.items():
            for j in range(fh * R):
                for i in range(fw * R):
                    nx, ny, nz = m((i + .5) / R, (j + .5) / R)
                    wx, wy, wz = ox + nx * w, oy + ny * h, oz + nz * d
                    # jitter the marking lookup a little: soft, furry boundaries
                    jx = (_hash(i, j, 1, seed) - .5) * 0.18
                    jy = (_hash(i, j, 2, seed) - .5) * 0.18
                    pny = ny
                    if c["part"] == "paw":
                        pny = 0.05
                    elif c["part"] == "tailtip":
                        pny = ny * 0.35
                    world = {"v": variant}
                    if b["coat"] == "wild_dog":
                        n = noise3(wx / 2.6, wy / 2.6, wz / 2.6, seed)
                        world["blotch"] = blotch_cols[min(3, int(n * 4.4))]
                    col = f(part, fname, min(1, max(0, nx + jx)), min(1, max(0, pny + jy)), nz, world).copy()
                    if b["coat"] == "dalmatian" and part not in ("nose",):
                        if noise3(wx / 1.6, wy / 1.6, wz / 1.6, seed + 5) > 0.68:
                            col = hx("#1d1b1b")
                    if part == "nose":
                        col = hx("#1a1716")
                    # shading: light from above, darker underneath and towards the face edges (ambient occlusion)
                    if fname == "up":
                        shade = 1.06
                    elif fname == "down":
                        shade = 0.78
                    else:
                        shade = 0.84 + 0.2 * ny
                    ex = min(i + .5, fw * R - i - .5) / R
                    ey = min(j + .5, fh * R - j - .5) / R
                    shade *= 0.9 + 0.1 * min(1.0, min(ex, ey) / 1.2)
                    # fur: vertical streaks on the sides, fine grain everywhere
                    streak = noise3(i * 0.9 / R + c["uv"][0], j * 0.25 / R, c["uv"][1], seed + 9) - .5
                    grain = (_hash(i, j, c["uv"][0] * 31 + c["uv"][1], seed) - .5) * 0.08
                    fur = streak * (0.16 if fname not in ("up", "down") else 0.08) + grain
                    if b["coat"] == "poodle" or c["part"] == "puff":
                        fur += (noise3(i * 0.7, j * 0.7, c["uv"][0], seed + 3) - .5) * 0.22
                    img[(fv * R) + j, (fu * R) + i, :3] = np.clip(col * (shade + fur), 0, 255)
                    img[(fv * R) + j, (fu * R) + i, 3] = 255
        X = lambda x: x * R
        if c["part"] == "head":                 # eyes with a glint, brows
            fu, fv = u + d, v + d
            eye_y = X(fv) + max(1, int(h * R * 0.38))
            for left in (True, False):
                ex = X(fu) + (int(R * 0.6) if left else X(w) - int(R * 0.6) - R)
                iris = (34, 22, 14) if not (b["coat"] == "husky" and variant == 0) else (70, 130, 210)
                img[eye_y:eye_y + R, ex:ex + R, :3] = iris
                img[eye_y, ex + (0 if left else R - 1), :3] = (235, 235, 230)
                img[eye_y - 1, ex - 1:ex + R + 1, :3] *= 0.8
        if c["part"] == "nose":                 # nostrils
            fu, fv = u + d, v + d
            img[X(fv) + R // 2, X(fu) + 1, :3] = (70, 62, 58)
            img[X(fv) + R // 2, X(fu) + X(2) - 2, :3] = (70, 62, 58)
        if c["part"] == "snout":                # mouth line along the bottom of the muzzle
            for fu, fv, fw in ((u + d, v + d, w), (u, v + d, d), (u + d + w, v + d, d)):
                row = X(fv) + X(h) - 1
                img[row, X(fu):X(fu + fw), :3] *= 0.55
        if c["part"] == "ear" and b["ears"] in ("pointy", "tall", "huge", "bat", "round"):
            fu, fv = u + d, v + d               # inner ear on the front
            img[X(fv) + 1:X(fv + h), X(fu) + 1:X(fu + w) - 1, :3] = \
                img[X(fv) + 1:X(fv + h), X(fu) + 1:X(fu + w) - 1, :3] * 0.5 + np.array([200, 140, 130]) * 0.5
        if c["part"] == "paw":                  # toes
            fu, fv = u + d, v + d
            for k in range(1, X(w), R):
                img[X(fv):X(fv + h), X(fu) + k, :3] *= 0.7
    return Image.fromarray(img.astype(np.uint8), "RGBA")


VARIANTS = {"lab": 3, "husky": 2, "dachshund": 2, "doberman": 2, "jindo": 2}


# ------------------------------------------------------------------ animations / client entity
ANIMS = {
    "format_version": "1.8.0",
    "animations": {
        "animation.wa_dog.walk": {"loop": True, "bones": {
            "leg0": {"rotation": ["math.cos(query.modified_distance_moved * 38.17) * 70 * query.modified_move_speed", 0, 0]},
            "leg1": {"rotation": ["math.cos(query.modified_distance_moved * 38.17 + 180) * 70 * query.modified_move_speed", 0, 0]},
            "leg2": {"rotation": ["math.cos(query.modified_distance_moved * 38.17 + 180) * 70 * query.modified_move_speed", 0, 0]},
            "leg3": {"rotation": ["math.cos(query.modified_distance_moved * 38.17) * 70 * query.modified_move_speed", 0, 0]}}},
        "animation.wa_dog.wag": {"loop": True, "bones": {
            "tail": {"rotation": [0, "math.sin(query.life_time * (query.is_tamed ? 900 : 300)) * (query.is_tamed ? 25 : 8)", 0]}}},
        "animation.wa_dog.sit": {"loop": True, "bones": {
            "body": {"rotation": [-20, 0, 0], "position": [0, -2, 0]},
            "upperBody": {"rotation": [0, 0, 0]},
            "head": {"position": [0, 1, 0]},
            "leg0": {"rotation": [-80, 0, 0], "position": [0, -2, -2]},
            "leg1": {"rotation": [-80, 0, 0], "position": [0, -2, -2]},
            "tail": {"rotation": [45, 0, 0], "position": [0, -3, 0]}}},
        "animation.wa_dog.baby": {"loop": True, "bones": {"head": {"scale": 1.35}}},
    },
}
CONTROLLERS = {
    "format_version": "1.10.0",
    "animation_controllers": {
        "controller.animation.wa_dog.move": {"initial_state": "default", "states": {
            "default": {"animations": ["walk", "wag"], "transitions": [{"sitting": "query.is_sitting"}]},
            "sitting": {"animations": ["sit", "wag"], "transitions": [{"default": "!query.is_sitting"}]}}},
        "controller.animation.wa_dog.look": {"initial_state": "default", "states": {
            "default": {"animations": ["look_at_target", {"baby": "query.is_baby"}]}}},
    },
}


N_MAX = max(VARIANTS.values())


def client_entity(bid, b, n_var):
    tex = {"default": f"textures/entity/wa_dogs/{bid}_0"}
    arr = []
    for i in range(N_MAX):                       # every slot the shared render controller can ask for
        tex[f"v{i}"] = f"textures/entity/wa_dogs/{bid}_{min(i, n_var - 1)}"
        arr.append(f"Texture.v{i}")
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"{NS}:{b['id']}",
        "materials": {"default": "wolf"},
        "textures": tex,
        "geometry": {"default": f"geometry.wa_dog_{bid}"},
        "scripts": {"scale": str(b["scale"]), "animate": ["move", "look"]},
        "animations": {"walk": "animation.wa_dog.walk", "wag": "animation.wa_dog.wag", "sit": "animation.wa_dog.sit",
                       "baby": "animation.wa_dog.baby", "look_at_target": "animation.common.look_at_target",
                       "move": "controller.animation.wa_dog.move", "look": "controller.animation.wa_dog.look"},
        "render_controllers": ["controller.render.wa_dog"],
        "spawn_egg": {"texture": f"wa_egg_{b['id']}", "texture_index": 0},
        "enable_attachables": False}}}, arr


def render_controller(n_max):
    return {"format_version": "1.8.0", "render_controllers": {"controller.render.wa_dog": {
        "arrays": {"textures": {"Array.coat": [f"Texture.v{i}" for i in range(n_max)]}},
        "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
        "textures": ["Array.coat[query.variant]"]}}}


# ------------------------------------------------------------------ behaviour (the rebuild's pipeline adds the rest)
def behavior(b, n_var):
    s = b["scale"]
    hp_tame = max(8, round(20 * (0.6 + 0.4 * s)))
    wild = b.get("wild")
    variants = [{"weight": 1, "add": {"component_groups": [f"wa:v{i}"]}} for i in range(n_var)]
    groups = {f"wa:v{i}": {"minecraft:variant": {"value": i}} for i in range(n_var)}
    groups.update({
        "wa:baby": {"minecraft:is_baby": {}, "minecraft:scale": {"value": 0.5},
                    "minecraft:ageable": {"duration": 1200, "feed_items": ["minecraft:beef", "minecraft:chicken",
                                                                           "minecraft:porkchop", "minecraft:mutton"],
                                          "grow_up": {"event": "minecraft:ageable_grow_up", "target": "self"}},
                    "minecraft:behavior.follow_parent": {"priority": 6, "speed_multiplier": 1.1}},
        "wa:adult": {"minecraft:behavior.breed": {"priority": 5, "speed_multiplier": 1.0},
                     "minecraft:breedable": {"require_tame": True, "breeds_with": {
                         "mate_type": f"{NS}:{b['id']}", "baby_type": f"{NS}:{b['id']}",
                         "breed_event": {"event": "minecraft:entity_born", "target": "baby"}},
                         "breed_items": ["minecraft:beef", "minecraft:chicken", "minecraft:porkchop",
                                         "minecraft:mutton", "minecraft:cooked_beef", "minecraft:cooked_chicken"]}},
        "wa:wild": {"minecraft:tameable": {"probability": 0.33 if not wild else 0.2, "tame_items": b["tame"],
                                           "tame_event": {"event": "minecraft:on_tame", "target": "self"}},
                    "minecraft:behavior.avoid_mob_type": {"priority": 4, "entity_types": [
                        {"filters": {"test": "is_family", "subject": "other", "value": "wolf"}, "max_dist": 8,
                         "walk_speed_multiplier": 1.2, "sprint_speed_multiplier": 1.4}]} if not wild else {
                        "priority": 9, "entity_types": []}},
        "wa:tame": {"minecraft:is_tamed": {},
                    "minecraft:health": {"value": hp_tame, "max": hp_tame},
                    "minecraft:attack": {"damage": b.get("dmg", 3)},
                    "minecraft:sittable": {},
                    "minecraft:behavior.follow_owner": {"priority": 6, "speed_multiplier": 1.1, "start_distance": 10,
                                                        "stop_distance": 2},
                    "minecraft:behavior.beg": {"priority": 9, "look_distance": 8, "look_time": [2, 4],
                                               "items": ["minecraft:bone", "minecraft:beef", "minecraft:cooked_beef",
                                                         "minecraft:chicken", "minecraft:cooked_chicken"]}},
    })
    if wild:
        groups["wa:wild"].pop("minecraft:behavior.avoid_mob_type", None)
    hp = max(6, round(12 * (0.5 + 0.5 * s)))
    return {"format_version": "1.20.0", "minecraft:entity": {
        "description": {"identifier": f"{NS}:{b['id']}", "is_spawnable": True, "is_summonable": True},
        "component_groups": groups,
        "components": {
            "minecraft:type_family": {"family": [b["id"], "dog" if not wild else "wild_canid", "mob"]},
            "minecraft:health": {"value": hp, "max": hp},
            "minecraft:collision_box": {"width": round(0.6 * s, 3), "height": round(0.85 * s, 3)},
            "minecraft:movement": {"value": 0.3},
            "minecraft:navigation.walk": {"can_path_over_water": True, "avoid_damage_blocks": True},
            "minecraft:movement.basic": {}, "minecraft:jump.static": {}, "minecraft:can_climb": {},
            "minecraft:physics": {}, "minecraft:pushable": {"is_pushable": True, "is_pushable_by_piston": True},
            "minecraft:breathable": {"total_supply": 15, "suffocate_time": 0},
            "minecraft:nameable": {},
            "minecraft:leashable": {"soft_distance": 4.0, "hard_distance": 6.0, "max_distance": 10.0},
            "minecraft:balloonable": {},
            "minecraft:ambient_sound_interval": {"value": 10.0, "range": 20.0, "event_name": "ambient"},
            "minecraft:attack": {"damage": b.get("dmg", 3)},
            "minecraft:healable": {"items": [{"item": i, "heal_amount": a} for i, a in (
                ("minecraft:beef", 3), ("minecraft:cooked_beef", 8), ("minecraft:chicken", 2),
                ("minecraft:cooked_chicken", 6), ("minecraft:porkchop", 3), ("minecraft:cooked_porkchop", 8),
                ("minecraft:mutton", 2), ("minecraft:cooked_mutton", 6), ("minecraft:rabbit", 3),
                ("minecraft:cooked_rabbit", 5), ("minecraft:rotten_flesh", 4))]},
            "minecraft:loot": {"table": "loot_tables/entities/wa_none.json"},
            "minecraft:behavior.float": {"priority": 0},
            "minecraft:behavior.stay_while_sitting": {"priority": 3},
            "minecraft:behavior.leap_at_target": {"priority": 4, "target_dist": 0.4},
            "minecraft:behavior.melee_attack": {"priority": 5},
            "minecraft:behavior.random_stroll": {"priority": 8, "speed_multiplier": 1.0},
            "minecraft:behavior.look_at_player": {"priority": 9, "look_distance": 6, "probability": 0.02},
            "minecraft:behavior.random_look_around": {"priority": 10},
            "minecraft:behavior.panic": {"priority": 2, "speed_multiplier": 1.25} if not wild else
            {"priority": 12, "speed_multiplier": 1.0},
        },
        "events": {
            "minecraft:entity_spawned": {"sequence": [
                {"randomize": [{"weight": 9, "add": {"component_groups": ["wa:adult", "wa:wild"]}},
                               {"weight": 1, "add": {"component_groups": ["wa:baby", "wa:wild"]}}]},
                {"randomize": variants}]},
            "minecraft:entity_born": {"sequence": [{"add": {"component_groups": ["wa:baby", "wa:tame"]}},
                                                   {"randomize": variants}]},
            "minecraft:ageable_grow_up": {"remove": {"component_groups": ["wa:baby"]},
                                          "add": {"component_groups": ["wa:adult"]}},
            "minecraft:on_tame": {"remove": {"component_groups": ["wa:wild"]},
                                  "add": {"component_groups": ["wa:tame"]}},
        }}}


# ------------------------------------------------------------------ build everything
def build(dogs, rp, src_dir, egg_icons, extra_item_tex, log, egg_icon_fn):
    """dogs: {entity id: breed key, ...} with roster info merged. Writes RP files, and behaviour source files into
    src_dir for the main pipeline. Returns {entity id: source path}."""
    out = {}
    n_max = 1
    for eid, b in dogs.items():
        b = dict(b, id=eid)
        bid = b["breed"]
        geo, cubes, _ = geometry(bid, b)
        dump(os.path.join(rp, "models", "entity", "wa_dogs", f"{bid}.geo.json"),
             {"format_version": "1.12.0", "minecraft:geometry": [geo]})
        n_var = VARIANTS.get(b["coat"], 1)
        n_max = max(n_max, n_var)
        os.makedirs(os.path.join(rp, "textures", "entity", "wa_dogs"), exist_ok=True)
        imgs = []
        for i in range(n_var):
            im = paint(bid, b, cubes, i, seed=sum(map(ord, bid)))
            im.save(os.path.join(rp, "textures", "entity", "wa_dogs", f"{bid}_{i}.png"))
            imgs.append(im)
        ce, _ = client_entity(bid, b, n_var)
        dump(os.path.join(rp, "entity", f"{eid}.json"), ce)
        # egg: coat colors
        a = np.array(imgs[0])[..., :3][np.array(imgs[0])[..., 3] > 0]
        cols = sorted({tuple(x) for x in (a // 32 * 32).tolist()}, key=lambda c: -sum(1 for y in a if tuple(y // 32 * 32) == c))
        base = "#%02x%02x%02x" % tuple(int(x) for x in np.median(a, axis=0))
        dark = "#%02x%02x%02x" % tuple(int(x) for x in np.percentile(a, 10, axis=0))
        rel = f"textures/items/wa_eggs/{eid}"
        os.makedirs(os.path.dirname(os.path.join(rp, rel)), exist_ok=True)
        egg_icon_fn(base, dark, seed=len(eid)).save(os.path.join(rp, rel + ".png"))
        extra_item_tex[f"wa_egg_{eid}"] = {"textures": rel}
        egg_icons[eid] = f"wa_egg_{eid}"
        p = os.path.join(src_dir, f"{eid}.json")
        dump(p, behavior(dict(b, id=eid), n_var))
        out[eid] = p
    dump(os.path.join(rp, "animations", "wa_dog.animation.json"), ANIMS)
    dump(os.path.join(rp, "animation_controllers", "wa_dog.animation_controllers.json"), CONTROLLERS)
    dump(os.path.join(rp, "render_controllers", "wa_dog.render_controllers.json"), render_controller(N_MAX))
    log.append(f"dogs: {len(dogs)}")
    return out
