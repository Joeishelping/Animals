#!/usr/bin/env python3
"""Packs World Animals BP + RP into one .mcaddon (two pack folders inside). usage: python3 tools/build_mcaddon.py [out]"""
import json
import os
import sys
import zipfile

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ver = json.load(open(os.path.join(root, "World Animals BP", "manifest.json")))["header"]["version"]
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    root, "dist", f"World_Animals_v{ver[0]}_{ver[1]}" + (f"_{ver[2]}" if ver[2] else "") + ".mcaddon")
os.makedirs(os.path.dirname(out), exist_ok=True)
# the pack names in Minecraft's menus carry the version: keep them in step with it
label = f"v{ver[0]}.{ver[1]}" + (f".{ver[2]}" if ver[2] else "")
for pack, tag in (("World Animals BP", "BP"), ("World Animals RP", "RP")):
    mp = os.path.join(root, pack, "manifest.json")
    m = json.load(open(mp))
    m["header"]["name"] = f"World Animals {tag} {label}"
    with open(mp, "w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for pack in ("World Animals BP", "World Animals RP"):
        for dp, _, files in sorted(os.walk(os.path.join(root, pack))):
            for f in sorted(files):
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, root))
print(out)
