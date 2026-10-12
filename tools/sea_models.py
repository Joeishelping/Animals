"""Octopus, lobster and moose: models, painted textures and animations of their own (no base model fits them).
Coordinates in pixels, facing -Z, feet at y = 0."""
import math
import os
import random

import numpy as np
from PIL import Image

from dogs import Packer, noise3, _hash, hx
from wa_common import dump
import moose_model

NS = "worldanimals"
TEX = 128          # same UV space as the shared packer
RES = 2


class Model:
    def __init__(self, gid, tex=TEX, packer=None, bounds=(3, 2, [0, 0.5, 0])):
        self.gid, self.bones, self.cubes, self.P = gid, [], [], packer or Packer()
        self.tex, self.bounds = tex, bounds

    def bone(self, name, pivot, parent=None, rotation=None):
        b = {"name": name, "pivot": pivot, "cubes": []}
        if parent:
            b["parent"] = parent
        if rotation:
            b["rotation"] = rotation
        self.bones.append(b)
        return b

    def cube(self, bone, part, origin, size, inflate=0.0, rotation=None, pivot=None):
        isz = [max(1, int(math.ceil(s))) for s in size]
        uv = self.P.place(*isz)
        c = {"origin": [round(o, 3) for o in origin], "size": [round(s, 3) for s in size], "uv": uv}
        if inflate:
            c["inflate"] = inflate
        if rotation:
            c["rotation"], c["pivot"] = rotation, pivot or origin
        next(b for b in self.bones if b["name"] == bone)["cubes"].append(c)
        self.cubes.append(dict(part=part, uv=uv, size=isz, origin=origin))

    def geometry(self):
        return {"description": {"identifier": self.gid, "texture_width": self.tex, "texture_height": self.tex,
                                "visible_bounds_width": self.bounds[0], "visible_bounds_height": self.bounds[1],
                                "visible_bounds_offset": self.bounds[2]},
                "bones": self.bones}


def paint(model, color_fn, seed, variant=0):
    """color_fn(part, face, nx, ny, nz, wx, wy, wz, variant) -> rgb"""
    R = RES
    img = np.zeros((model.tex * R, model.tex * R, 4), float)
    for c in model.cubes:
        w, h, d = c["size"]
        u, v = c["uv"]
        ox, oy, oz = c["origin"]
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
                    col = np.array(color_fn(c["part"], fname, nx, ny, nz, wx, wy, wz, variant), float)
                    shade = {"up": 1.06, "down": 0.78}.get(fname, 0.86 + 0.18 * ny)
                    ex = min(i + .5, fw * R - i - .5) / R
                    ey = min(j + .5, fh * R - j - .5) / R
                    shade *= 0.9 + 0.1 * min(1.0, min(ex, ey) / 1.0)
                    shade += (_hash(i, j, u * 31 + v, seed) - .5) * 0.08
                    img[fv * R + j, fu * R + i, :3] = np.clip(col * shade, 0, 255)
                    img[fv * R + j, fu * R + i, 3] = 255
    return Image.fromarray(img.astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ octopus
def octopus():
    M = Model("geometry.wa_octopus")
    M.bone("root", [0, 0, 0])
    M.bone("body", [0, 4, 0], "root")
    M.bone("mantle", [0, 7, 1], "body")
    M.cube("body", "skin", [-3.5, 2.5, -3.5], [7, 3, 7])                      # where the arms meet
    M.cube("mantle", "skin", [-4, 5.5, -2], [8, 7, 8])                        # the head bulb, behind
    M.cube("mantle", "skin", [-3, 12.5, -1], [6, 2, 6])
    M.cube("body", "eye", [-3.8, 5.0, -3.9], [2, 2, 1])
    M.cube("body", "eye", [1.8, 5.0, -3.9], [2, 2, 1])
    for i in range(8):
        a = i * 45 + 22.5
        rad = math.radians(a)
        px, pz = math.sin(rad) * 2.6, -math.cos(rad) * 2.6
        M.bone(f"arm{i}", [round(px, 2), 3, round(pz, 2)], "body", rotation=[12, -a, 0])
        M.cube(f"arm{i}", "arm", [px - 1, 2, pz - 7], [2, 2, 7])
        M.bone(f"arm{i}b", [round(px, 2), 3, round(pz - 7, 2)], f"arm{i}", rotation=[-30, 0, 0])
        M.cube(f"arm{i}b", "arm", [px - 0.75, 2.25, pz - 12], [1.5, 1.5, 5])
        M.bone(f"arm{i}c", [round(px, 2), 3, round(pz - 12, 2)], f"arm{i}b", rotation=[-45, 0, 0])
        M.cube(f"arm{i}c", "arm", [px - 0.5, 2.5, pz - 14.5], [1, 1, 2.5])
    base = [hx("#5a1608"), hx("#9a2e12"), hx("#c8562a"), hx("#e08a54")]

    def col(part, face, nx, ny, nz, wx, wy, wz, v):
        if part == "eye":
            if face == "north":
                if 0.25 < ny < 0.6:
                    return hx("#151010")                              # the slit pupil
                return hx("#e8c040")
            return base[1]
        n = noise3(wx / 2.2, wy / 2.2, wz / 2.2, 11)
        c = base[0] * (1 - n) + base[2] * n
        if part == "arm" and face == "down":                           # suckers along the underside
            c = hx("#efc0a8") if (int(wz * 2) % 3 == 0) else hx("#d89a80")
        if noise3(wx / 0.9, wy / 0.9, wz / 0.9, 23) > 0.72:
            c = base[3]                                                # pale spots
        return c
    anims = {"format_version": "1.8.0", "animations": {
        "animation.wa_octopus.swim": {"loop": True, "bones": dict(
            {f"arm{i}": {"rotation": [f"math.sin(query.life_time * 120 + {i * 45}) * 10", 0, 0]} for i in range(8)},
            **{f"arm{i}b": {"rotation": [f"math.sin(query.life_time * 120 + {i * 45 + 60}) * 14", 0, 0]} for i in range(8)},
            mantle={"rotation": ["math.sin(query.life_time * 90) * 6", 0, 0],
                    "scale": [1, "1 + math.sin(query.life_time * 180) * 0.04", 1]})}}}
    return M, col, anims, ["swim"], 1


# ------------------------------------------------------------------ lobster
def lobster():
    M = Model("geometry.wa_lobster")
    M.bone("root", [0, 0, 0])
    M.bone("body", [0, 3, 0], "root")
    M.cube("body", "shell", [-2.5, 2, -4], [5, 3.5, 7])                       # carapace
    M.cube("body", "shell", [-1.5, 2.5, -6], [3, 2.5, 2])                     # head
    M.cube("body", "spike", [-0.5, 4.2, -7.5], [1, 1, 2])                     # rostrum
    M.cube("body", "eye", [-1.6, 4.8, -5.8], [1, 1, 1])
    M.cube("body", "eye", [0.6, 4.8, -5.8], [1, 1, 1])
    for side, name in ((-1, "antenna0"), (1, "antenna1")):
        M.bone(name, [side * 0.8, 4, -6], "body", rotation=[-18, side * 18, 0])
        M.cube(name, "antenna", [side * 0.8 - 0.25, 3.75, -21], [0.5, 0.5, 15])
    prev = "body"
    z = 3
    for k, (w, h, l) in enumerate([(4.4, 3.0, 2.6), (4.0, 2.7, 2.4), (3.6, 2.4, 2.2), (3.0, 2.0, 2.0)]):
        name = f"tail{k}"
        M.bone(name, [0, 3, z], prev)
        M.cube(name, "shell", [-w / 2, 2.1, z], [w, h, l])
        prev, z = name, z + l
    M.bone("fan", [0, 3, z], prev)
    M.cube("fan", "fan", [-3.5, 2.3, z], [7, 0.8, 3])
    for side, name in ((-1, "claw0"), (1, "claw1")):
        M.bone(name, [side * 2.4, 3.2, -4.5], "body", rotation=[-8, side * -38, 0])   # held out to the sides
        M.cube(name, "limb", [side * 2.4 - 1, 2.4, -10.5], [2, 2, 6])                  # arm
        M.cube(name, "claw", [side * 2.4 - 2, 1.6, -17.5], [4, 3.2, 7])                # pincer
        M.cube(name, "claw", [side * 2.4 - (0.4 if side < 0 else 1.6), 1.9, -20.5], [2, 2, 3])   # finger
    for side in (-1, 1):
        for k in range(4):
            name = f"leg{'l' if side < 0 else 'r'}{k}"
            M.bone(name, [side * 2.5, 2.8, -2.5 + k * 1.8], "body", rotation=[0, side * (k - 1.5) * -12, side * 28])
            x0 = side * 2.5 if side > 0 else side * 2.5 - 5.5
            M.cube(name, "limb", [x0, 2.3, -3 + k * 1.8], [5.5, 1, 1])

    def col(part, face, nx, ny, nz, wx, wy, wz, v):
        if v == 1:                                                     # the rare blue lobster
            dark, mid, light = hx("#0e2a5a"), hx("#1e4f9a"), hx("#4a86d0")
        else:
            dark, mid, light = hx("#2a1a14"), hx("#4a2c1e"), hx("#7a3a22")
        if part == "eye":
            return hx("#101010")
        if part == "antenna":
            return hx("#b8442a") if v == 0 else light
        n = noise3(wx / 1.6, wy / 1.6, wz / 1.6, 5)
        c = dark * (1 - n) + mid * n
        if face == "down":
            c = hx("#c8703a") if v == 0 else hx("#8ab0e0")              # paler underside
        if part in ("claw", "spike") and (ny > 0.6 or part == "spike"):
            c = c * 0.6 + hx("#c8402a") * 0.4 if v == 0 else c * 0.6 + light * 0.4
        if part == "limb":
            c = c * 0.5 + (hx("#a8482a") if v == 0 else light) * 0.5
        if noise3(wx / 0.6, wy / 0.6, wz / 0.6, 9) > 0.78:
            c = c * 0.55 + (hx("#d88a4a") if v == 0 else hx("#9ac4f0")) * 0.45   # speckles
        return c
    leg_anim = {f"leg{s}{k}": {"rotation": [0, f"math.sin(query.modified_distance_moved * 60 + {k * 90 + (0 if s == 'l' else 180)}) * 18 * query.modified_move_speed", 0]}
                for s in ("l", "r") for k in range(4)}
    anims = {"format_version": "1.8.0", "animations": {
        "animation.wa_lobster.walk": {"loop": True, "bones": leg_anim},
        "animation.wa_lobster.idle": {"loop": True, "bones": {
            "antenna0": {"rotation": ["math.sin(query.life_time * 80) * 6", "math.cos(query.life_time * 60) * 6", 0]},
            "antenna1": {"rotation": ["math.cos(query.life_time * 70) * 6", "math.sin(query.life_time * 55) * 6", 0]},
            "claw0": {"rotation": [0, "math.sin(query.life_time * 50) * 5", 0]},
            "claw1": {"rotation": [0, "-math.sin(query.life_time * 50 + 40) * 5", 0]},
            "tail2": {"rotation": ["math.sin(query.life_time * 40) * 4", 0, 0]},
            "fan": {"rotation": ["math.sin(query.life_time * 40 + 30) * 8", 0, 0]}}}}}
    return M, col, anims, ["walk", "idle"], 2


MODELS = {"octopus": octopus, "lobster": lobster, "moose": lambda: moose_model.moose(Model)}


def build(sid, sp, rp):
    """writes geometry, textures, animations and the client entity; returns the client entity dict"""
    M, col, anims, anim_names, n_var = MODELS[sp["model"]]()
    dump(os.path.join(rp, "models", "entity", "wa_species", f"{sid}.geo.json"),
         {"format_version": "1.12.0", "minecraft:geometry": [M.geometry()]})
    tex = {}
    for v in range(n_var):
        rel = f"textures/entity/wa_species/{sid}/v{v}"
        os.makedirs(os.path.dirname(os.path.join(rp, rel)), exist_ok=True)
        paint(M, col, seed=len(sid) * 17 + v, variant=v).save(os.path.join(rp, rel + ".png"))
        tex[f"v{v}"] = rel
    tex["default"] = tex["v0"]
    dump(os.path.join(rp, "animations", f"wa_{sid}.animation.json"), anims)
    rc = f"controller.render.wa_{sid}"
    dump(os.path.join(rp, "render_controllers", f"wa_{sid}.render_controllers.json"), {
        "format_version": "1.8.0", "render_controllers": {rc: {
            "arrays": {"textures": {"Array.skin": [f"Texture.v{v}" for v in range(n_var)]}},
            "geometry": "Geometry.default", "materials": [{"*": "Material.default"}],
            "textures": ["Array.skin[query.variant]" if n_var > 1 else "Texture.default"]}}})
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"{NS}:{sid}",
        "materials": {"default": "entity_alphatest"},
        "textures": tex,
        "geometry": {"default": M.gid},
        "animations": {(n if isinstance(n, str) else next(iter(n))): f"animation.wa_{sid}.{n if isinstance(n, str) else next(iter(n))}"
                       for n in anim_names},
        "scripts": {"animate": anim_names, "scale": str(sp.get("render_scale", sp.get("scale", 1.0)))},
        "render_controllers": [rc],
        "spawn_egg": {"texture": f"wa_egg_{sid}", "texture_index": 0}}}}
