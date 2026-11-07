#!/usr/bin/env python3
"""Membuat stickman/voice/NASKAH.md dari content.json (kalimat yang dibaca untuk rekaman)."""
import json, os
R = os.path.dirname(os.path.abspath(__file__))
cs = json.load(open(os.path.join(R, "content.json"), encoding="utf-8"))["contents"]
out = []
for c in cs:
    out.append(f"## {c['id']}  |  {c['yt_title'].replace(' #Shorts', '')}")
    for i, s in enumerate(c["scenes"], 1):
        out.append(f"{i}. {s['say']}")
    out.append("")
open(os.path.join(R, "voice", "NASKAH.md"), "w", encoding="utf-8").write("\n".join(out))
words = sum(len(s["say"].split()) for c in cs for s in c["scenes"])
lines = sum(len(c["scenes"]) for c in cs)
print(f"{len(cs)} konten, {lines} kalimat, {words} kata (~{words/2.6/60:.0f} menit bicara)")
