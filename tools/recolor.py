"""Texture recolor engine for new species built on existing models.

A recipe repaints a base texture:
  ramp      colors dark -> light; every "fur" pixel's brightness (relative to the texture's own range) is mapped
            onto this ramp, so the original shading and fur detail survive in the new colors
  keep      fraction of the texture below which a color cluster counts as a feature (eyes, mouth, nose, teeth)
            and is left as it is (default 0.025)
  areas     [(x0, y0, x1, y1, ramp)] in texture fractions: a different ramp inside a rectangle (white head...)
  pattern   [{"type": spots|rosettes|stripes|bands|speckle, "color", ...}] painted over the fur
"""
import colorsys
import math
import random

import numpy as np
from PIL import Image


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def ramp_lookup(ramp, t):
    """t in [0,1] (array) -> rgb along the ramp stops"""
    stops = np.array([hex_rgb(c) for c in ramp])
    n = len(stops) - 1
    x = np.clip(t, 0, 1) * n
    i = np.minimum(np.floor(x).astype(int), n - 1)
    f = (x - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f


def kmeans(px, k, iters=12, seed=1):
    rng = np.random.default_rng(seed)
    c = px[rng.choice(len(px), size=min(k, len(px)), replace=False)].astype(float)
    for _ in range(iters):
        d = ((px[:, None, :] - c[None, :, :]) ** 2).sum(-1)
        lab = d.argmin(1)
        for j in range(len(c)):
            m = px[lab == j]
            if len(m):
                c[j] = m.mean(0)
    d = ((px[:, None, :] - c[None, :, :]) ** 2).sum(-1)
    return d.argmin(1), c


def lum(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def recolor(img, recipe, seed=7):
    a = np.array(img.convert("RGBA")).astype(float)
    H, W = a.shape[:2]
    rgb, alpha = a[..., :3], a[..., 3]
    opaque = alpha > 10
    ys, xs = np.nonzero(opaque)
    px = rgb[opaque]
    if len(px) == 0:
        return img
    lab, cent = kmeans(px, 8)
    share = np.bincount(lab, minlength=len(cent)) / len(px)
    keep_frac = recipe.get("keep", 0.025)
    feature = np.zeros(len(px), bool)
    for j, s in enumerate(share):
        r, g, b = cent[j] / 255
        h, sat, v = colorsys.rgb_to_hsv(r, g, b)
        reddish = (h < 0.05 or h > 0.9) and sat > 0.35          # mouths, tongues, noses
        if recipe.get("no_features"):
            continue
        if s < keep_frac or reddish:
            feature |= lab == j
    fur = ~feature
    if fur.sum() < 0.2 * len(px):            # tiny or one-color texture: everything is fur
        fur = np.ones(len(px), bool)
    L = lum(px)
    lo, hi = np.percentile(L[fur], 2), np.percentile(L[fur], 98)
    t = (L - lo) / max(hi - lo, 1e-6)
    t = np.clip((t - 0.5) * recipe.get("contrast", 1.0) + 0.5 + recipe.get("lift", 0.0), 0, 1)
    out = px.copy()
    out[fur] = ramp_lookup(recipe["ramp"], t[fur])
    for (x0, y0, x1, y1, ramp) in recipe.get("areas", []):
        inside = fur & (xs >= x0 * W) & (xs < x1 * W) & (ys >= y0 * H) & (ys < y1 * H)
        out[inside] = ramp_lookup(ramp, t[inside])
    res = rgb.copy()
    res[opaque] = out
    res = paint_patterns(res, opaque, fur, ys, xs, t, recipe.get("pattern", []), W, H, seed)
    final = np.dstack([np.clip(res, 0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(final, "RGBA")


def paint_patterns(res, opaque, fur, ys, xs, t, patterns, W, H, seed):
    if not patterns:
        return res
    furmask = np.zeros((H, W), bool)
    furmask[ys[fur], xs[fur]] = True
    tmap = np.zeros((H, W))
    tmap[ys, xs] = t
    rng = random.Random(seed)
    scale = W / 128.0                       # patterns are sized for 128px textures and scale up
    for p in patterns:
        col = hex_rgb(p["color"])
        kind = p["type"]
        only_dark = p.get("max_t", 1.0)     # don't paint on the lightest parts (bellies) unless asked
        region = p.get("area")              # optional (x0,y0,x1,y1) fractions
        mask = np.zeros((H, W), bool)
        if kind in ("spots", "rosettes", "speckle"):
            n = int(p.get("density", 0.004) * W * H / (scale * scale) * (0.25 if kind == "speckle" else 1))
            r = max(p.get("size", 1.2) * scale, 0.8)       # never smaller than a pixel on small textures
            yy, xx = np.mgrid[0:H, 0:W]
            for _ in range(n):
                cx, cy = rng.uniform(0, W), rng.uniform(0, H)
                rr = r * rng.uniform(0.7, 1.3) * (0.5 if kind == "speckle" else 1)
                y0, y1 = max(int(cy - rr - 2), 0), min(int(cy + rr + 2), H)
                x0, x1 = max(int(cx - rr - 2), 0), min(int(cx + rr + 2), W)
                d = np.hypot(yy[y0:y1, x0:x1] - cy, xx[y0:y1, x0:x1] - cx)
                if kind == "rosettes":
                    ring = (d <= rr) & (d >= rr * 0.55)
                    gap = np.arctan2(yy[y0:y1, x0:x1] - cy, xx[y0:y1, x0:x1] - cx)
                    ring &= ~((gap > rng.uniform(-3, 3)) & (gap < rng.uniform(-3, 3) + 0.9))
                    mask[y0:y1, x0:x1] |= ring
                    if p.get("center"):
                        inner = d < rr * 0.5
                        res[y0:y1, x0:x1][inner & furmask[y0:y1, x0:x1]] = (
                            res[y0:y1, x0:x1][inner & furmask[y0:y1, x0:x1]] * 0.85 + hex_rgb(p["center"]) * 0.15)
                else:
                    mask[y0:y1, x0:x1] |= d <= rr
        elif kind in ("stripes", "bands"):
            period = p.get("period", 6) * scale
            width = p.get("width", 0.35)
            yy, xx = np.mgrid[0:H, 0:W]
            coord = xx if p.get("axis", "x") == "x" else yy
            wob = np.sin(yy / (3.0 * scale) + rng.uniform(0, 6)) * p.get("wobble", 1.0) * scale
            if kind == "bands":
                wob = 0
            mask = ((coord + wob) % period) < period * width
        mask &= furmask & (tmap <= only_dark)
        if region:
            x0, y0, x1, y1 = region
            box = np.zeros((H, W), bool)
            box[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)] = True
            mask &= box
        shade = (0.75 + 0.5 * tmap[mask])[:, None]       # keep a little of the shading inside the marks
        res[mask] = np.clip(col * shade, 0, 255) * p.get("opacity", 1.0) + res[mask] * (1 - p.get("opacity", 1.0))
    return res


def egg_icon(base_hex, spot_hex, seed=3):
    """16x16 spawn egg in the vanilla style: base color, darker outline, spots"""
    base, spot = hex_rgb(base_hex), hex_rgb(spot_hex)
    rng = random.Random(seed)
    img = np.zeros((16, 16, 4), np.uint8)
    shape = ["......####......", ".....######.....", "....########....", "...##########...",
             "...##########...", "..############..", "..############..", "..############..",
             ".##############.", ".##############.", ".##############.", ".##############.",
             "..############..", "..############..", "...##########...", ".....######....."]
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c != "#":
                continue
            edge = any(not (0 <= y + dy < 16 and 0 <= x + dx < 16 and shape[y + dy][x + dx] == "#")
                       for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            col = base * (0.55 if edge else 1.0 - 0.18 * (x + y) / 30 + (0.12 if (x < 7 and y < 6) else 0))
            img[y, x] = list(np.clip(col, 0, 255).astype(int)) + [255]
    for _ in range(7):
        x, y = rng.randint(3, 12), rng.randint(3, 13)
        if shape[y][x] == "#" and shape[y][x + 1] == "#":
            for dx in (0, 1):
                img[y, x + dx] = list(np.clip(spot * rng.uniform(0.9, 1.05), 0, 255).astype(int)) + [255]
    return Image.fromarray(img, "RGBA")
