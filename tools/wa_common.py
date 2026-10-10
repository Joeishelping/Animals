"""Shared helpers for the World Animals tooling: a lenient JSON reader (the original
pack has comments, trailing commas and one file with a missing brace) and a stable writer."""
import json
import os
import re


def _strip_comments(text):
    out, i, n = [], 0, len(text)
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def loads_lenient(text):
    text = text.lstrip("﻿")
    text = _strip_comments(text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # balance braces/brackets that were left open at the end of the file
        stack, in_str, esc = [], False, False
        for c in text:
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                continue
            if c == '"':
                in_str = True
            elif c in "{[":
                stack.append("}" if c == "{" else "]")
            elif c in "}]" and stack:
                stack.pop()
        return json.loads(text.rstrip() + "".join(reversed(stack)))


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        return loads_lenient(f.read())


def dump(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1 if len(json.dumps(data)) > 40000 else 2, ensure_ascii=False)
        f.write("\n")
