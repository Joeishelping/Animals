"""Moose: a model of its own, built at real size (1 block = 16 px, shoulder ~30 px, Steve is 32 px).
Humped shoulders, long overhanging nose, the bell under the throat, wide palmate antlers, long pale-stockinged legs.
Coordinates in pixels, facing -Z, feet at y = 0."""
import math

import numpy as np

from dogs import noise3, hx

TEX = 256


class Packer:
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
            raise ValueError("moose atlas full")
        return [u, v]


def moose(Model):
    M = Model("geometry.wa_moose", tex=TEX, packer=Packer(), bounds=(4, 3.5, [0, 1.5, 0]))
    M.bone("root", [0, 0, 0])
    M.bone("body", [0, 20, 0], "root")
    # barrel: deep chest, high withers, sloping rump
    M.cube("body", "coat", [-6, 15, -12], [12, 13, 14])                      # chest and shoulders
    M.cube("body", "coat", [-5.5, 16, 2], [11, 11, 11])                      # hindquarters, lower
    M.cube("body", "hump", [-4.5, 27, -12], [9, 4, 10])                      # the shoulder hump
    M.cube("body", "coat", [-4, 26.5, 1], [8, 1.5, 9])                       # back line to the rump
    M.bone("tail", [0, 25, 13], "body", rotation=[30, 0, 0])
    M.cube("tail", "coat", [-1, 22, 13], [2, 3, 1])
    # neck: short and thick, carrying the head low and forward
    M.bone("neck", [0, 25, -11], "body", rotation=[-22, 0, 0])
    M.cube("neck", "hump", [-3.5, 20, -17], [7, 9, 7])
    M.cube("neck", "mane", [-1, 28, -17], [2, 2, 6])
    # head
    M.bone("head", [0, 25.5, -17], "neck", rotation=[22, 0, 0])
    M.cube("head", "face", [-3.5, 21.5, -24], [7, 7, 7])                     # brow and cheeks
    M.cube("head", "face", [-3, 19.5, -32], [6, 6, 8])                       # long muzzle
    M.cube("head", "nose", [-3.5, 18.5, -36], [7, 6.5, 4])                   # the bulbous overhanging nose
    M.cube("head", "lip", [-3, 17.5, -35.5], [6, 1.5, 3])                    # drooping upper lip
    M.cube("head", "chin", [-2, 18, -31], [4, 1.5, 5])                       # lower jaw, tucked under
    M.cube("head", "eye", [-3.7, 25, -23], [1, 1.5, 1.5])
    M.cube("head", "eye", [2.7, 25, -23], [1, 1.5, 1.5])
    M.bone("bell", [0, 21.5, -20], "head", rotation=[8, 0, 0])
    M.cube("bell", "mane", [-1, 14, -21], [2, 7.5, 3])                       # the dewlap
    for side, name in ((-1, "ear0"), (1, "ear1")):
        M.bone(name, [side * 3, 27.5, -19], "head", rotation=[0, 0, side * 50])
        M.cube(name, "ear", [side * 3 - 1 if side > 0 else side * 3 - 1, 27.5, -19.5], [2, 5, 1])
    # antlers: a short beam out of each side, then a broad palm sweeping out and up with tines on the rim
    M.bone("antlers", [0, 28.5, -20], "head")
    for side in (-1, 1):
        s = side
        b = f"antler{0 if s < 0 else 1}"
        M.bone(b, [s * 3, 28.5, -20], "antlers", rotation=[-10, s * -12, s * -22])
        M.cube(b, "beam", [s * 3 - 1 if s > 0 else s * 3 - 4 + 1, 28, -21], [4, 2, 2])     # beam out of the skull
        x_in, x_out = (s * 5.5, s * 15.5)
        lo = min(x_in, x_out)
        M.cube(b, "palm", [lo, 28.5, -25], [10, 1.5, 9])                    # the palm
        M.cube(b, "palm", [lo + (1 if s > 0 else 2), 28.5, -16], [7, 1.5, 2])   # rear lobe
        for k in range(6):                                                    # tines along the outer and front rim
            if k < 4:
                tx, tz = (x_out - s * 1.0 - (0 if s > 0 else 1)), -24.5 + k * 2.6
            else:
                tx, tz = x_in + s * (2.5 + (k - 4) * 3.5) - (0 if s > 0 else 1), -26.5
            M.cube(b, "tine", [tx, 30, tz], [1, [3.5, 5, 4, 2.5, 3, 4][k], 1])
        M.cube(b, "tine", [s * 6.0 - (0 if s > 0 else 2), 28.8, -28], [2, 1.2, 3.5])   # brow tine, forward
    # legs: long, knobbly knees, pale stockings below
    for name, x, z in (("leg_fl", -3.5, -8), ("leg_fr", 3.5, -8), ("leg_bl", -3.5, 9), ("leg_br", 3.5, 9)):
        hind = name.startswith("leg_b")
        M.bone(name, [x, 17, z], "root")
        M.cube(name, "coat", [x - 2, 9, z - 2], [4, 8 if not hind else 9, 4] if not hind else [4.5, 9, 4.5])
        M.bone(name + "_low", [x, 9.5, z], name)
        M.cube(name + "_low", "knee", [x - 1.75, 8, z - 1.75], [3.5, 2, 3.5])
        M.cube(name + "_low", "stocking", [x - 1.5, 2, z - 1.5], [3, 6.5, 3])
        M.cube(name + "_low", "hoof", [x - 1.75, 0, z - 2], [3.5, 2, 3.5])

    coat = [hx("#120c08"), hx("#22160e"), hx("#342216"), hx("#4a3220"), hx("#5e4430")]

    def ramp(t):
        t = min(max(t, 0.0), 0.999) * (len(coat) - 1)
        i = int(t)
        return coat[i] * (1 - (t - i)) + coat[i + 1] * (t - i)

    def col(part, face, nx, ny, nz, wx, wy, wz, v):
        fur = noise3(wx / 1.3, wy / 2.4, wz / 1.3, 7) - 0.5                    # streaky hair grain
        big = noise3(wx / 5, wy / 5, wz / 5, 3) - 0.5
        if part == "eye":
            return hx("#0c0806") if face in ("east", "west") and ny > 0.3 else hx("#3a2818")
        if part == "hoof":
            return hx("#16120e") * (0.9 + 0.2 * ny)
        if part == "stocking":                                               # grey-brown lower legs
            base = hx("#4a3f33") * (1 - ny * 0.35) + hx("#3a2c20") * ny * 0.35 + fur * 18
            return base
        if part == "knee":
            return hx("#3e3024") + fur * 20
        if part in ("palm", "beam", "tine"):
            a = hx("#4a3420") * 0.6 + hx("#7a5e40") * 0.4
            g = noise3(wx / 0.8, wy / 3, wz / 0.8, 19) - 0.5
            c = a + g * 30
            if part == "tine":
                c = c * 0.5 + hx("#c8b48e") * 0.5 if wy > 32 or face == "up" else c   # pale worn tips
            if part == "palm" and face == "up":
                c = c * 1.08
            if part == "palm" and face == "down":
                c = c * 0.8
            return c
        if part == "nose":
            c = ramp(0.22 + big * 0.2) + fur * 14
            if face == "north" and 0.25 < ny < 0.7 and (0.12 < nx < 0.36 or 0.64 < nx < 0.88):
                c = hx("#060403")                                           # nostrils
            return c
        if part in ("lip", "chin"):
            return ramp(0.12) + fur * 10
        if part == "face":
            t = 0.42 + 0.25 * ny + big * 0.25                                # lighter brow, dark muzzle
            if wz < -27:
                t -= 0.12
            return ramp(t) + fur * 16
        if part == "ear":
            return ramp(0.45 + ny * 0.2) + fur * 12 if face != "north" else hx("#2a1e14")
        if part == "mane":
            return ramp(0.1 + fur * 0.4)
        # coat and hump: dark, grizzled over the shoulders, darkest on the belly
        t = 0.45 + big * 0.3 + fur * 0.35
        if part == "hump":
            t += 0.14
        if face == "down" or wy < 17:
            t -= 0.3
        t += (wy - 22) * 0.012
        return ramp(t)

    walk = "query.modified_distance_moved * 22"
    sw = "query.modified_move_speed"
    leg = lambda ph: {"rotation": [f"math.sin({walk} + {ph}) * 26 * {sw}", 0, 0]}
    low = lambda ph: {"rotation": [f"math.max(0, math.sin({walk} + {ph} + 60)) * 26 * {sw}", 0, 0]}
    anims = {"format_version": "1.8.0", "animations": {
        "animation.wa_moose.walk": {"loop": True, "bones": {
            "leg_fl": leg(0), "leg_br": leg(20), "leg_fr": leg(180), "leg_bl": leg(200),
            "leg_fl_low": low(0), "leg_br_low": low(20), "leg_fr_low": low(180), "leg_bl_low": low(200),
            "neck": {"rotation": [f"math.sin({walk} * 2) * 2.5 * {sw}", 0, 0]},
            "body": {"position": [0, f"math.abs(math.sin({walk})) * 0.5 * {sw}", 0]}}},
        "animation.wa_moose.idle": {"loop": True, "bones": {
            "ear0": {"rotation": [0, 0, "math.max(0, math.sin(query.life_time * 40) - 0.9) * -180"]},
            "ear1": {"rotation": [0, 0, "math.max(0, math.sin(query.life_time * 37 + 90) - 0.9) * 180"]},
            "tail": {"rotation": [0, "math.sin(query.life_time * 120) * 8", 0]},
            "bell": {"rotation": ["math.sin(query.life_time * 60) * 3", 0, "math.sin(query.life_time * 45) * 4"]},
            "head": {"rotation": ["math.sin(query.life_time * 20) * 2", 0, 0]}}},
        "animation.wa_moose.look": {"loop": True, "bones": {
            "head": {"rotation": [0, "math.clamp(query.target_y_rotation, -40, 40) * 0.7", 0]}}},
        "animation.wa_moose.charge": {"loop": True, "bones": {                # head down, antlers first
            "neck": {"rotation": ["math.sin(variable.attack_time * 180) * 30", 0, 0]},
            "head": {"rotation": ["math.sin(variable.attack_time * 180) * 15", 0, 0]}}},
        "animation.wa_moose.baby": {"loop": True, "bones": {
            "antlers": {"scale": 0},
            "head": {"scale": 1.35}, "body": {"scale": [1, 0.9, 0.9]}}}}}
    animate = ["walk", "idle", "look", {"charge": "variable.attack_time > 0"}, {"baby": "query.is_baby"}]
    return M, col, anims, animate, 1
