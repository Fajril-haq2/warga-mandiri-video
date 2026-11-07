#!/usr/bin/env python3
"""Pembuat video stickman gaya B1 (Minimal Line Art) untuk @mulaimandiri_.

  python stickman/build_video.py --day 3 --out out/video.mp4
  python stickman/build_video.py --id c01 --out out/video.mp4
  python stickman/build_video.py --id c01 --frames 0,3,8     (frame uji ke ./test)
"""
import argparse, datetime, json, math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import tts  # noqa: E402

W, H, FPS = 720, 1280, 24
SS = int(os.environ.get("STICK_SS", "3"))
SR = 44100
INK = (24, 24, 28)
PAPER = (244, 243, 239)
WHITE = (253, 253, 251)
BLUE = (47, 111, 237)
ORANGE = (244, 140, 40)
GREEN = (72, 187, 120)
YELLOW = (255, 208, 70)
RED = (226, 76, 76)
PINK = (255, 150, 175)
BEIGE = (226, 200, 150)
GRAY = (120, 120, 126)
BROWN = (150, 98, 60)
SKY = (120, 190, 255)
COLORS = dict(blue=BLUE, orange=ORANGE, green=GREEN, yellow=YELLOW, red=RED, pink=PINK, beige=BEIGE,
              gray=GRAY, brown=BROWN, ink=INK)


def _first(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[-1]


FONT_POP = _first(os.path.join(ROOT, "fonts", "Poppins-Bold.ttf"),
                  "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FONT_INT = _first(os.path.join(ROOT, "fonts", "Inter-SemiBold.otf"),
                  "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def ease_out_back(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def pop(ts, t0, d=0.35):
    if ts < t0:
        return 0.0
    return max(0.0, ease_out_back(min(1.0, (ts - t0) / d)))


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def cut_poly(P, frac):
    if frac >= 1:
        return P
    L = [math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)]
    goal = sum(L) * max(0.0, frac)
    out, acc = [P[0]], 0
    for i, l in enumerate(L):
        if acc + l >= goal:
            k = (goal - acc) / l if l else 0
            out.append((P[i][0] + (P[i + 1][0] - P[i][0]) * k, P[i][1] + (P[i + 1][1] - P[i][1]) * k))
            return out
        acc += l
        out.append(P[i + 1])
    return out


# ---------------------------------------------------------------- pena
class Pen:
    def __init__(self, img, seed):
        self.img, self.d, self.seed, self.n = img, ImageDraw.Draw(img), seed, 0

    def rng(self):
        self.n += 1
        return random.Random(self.seed * 7919 + self.n * 31)

    def S(self, p):
        return (p[0] * SS, p[1] * SS)

    def line(self, pts, w=5, col=INK, wob=0.0, frac=1.0):
        P = list(pts)
        if wob:
            r = self.rng()
            P = [(x + r.uniform(-wob, wob), y + r.uniform(-wob, wob)) for x, y in P]
        if frac < 1.0:
            P = cut_poly(P, frac)
        if len(P) < 2:
            return
        Q = [self.S(p) for p in P]
        self.d.line(Q, fill=col, width=max(1, int(w * SS)), joint="curve")
        rr = w * SS / 2
        for q in (Q[0], Q[-1]):
            self.d.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], fill=col)

    def poly(self, pts, fill=None, col=INK, w=5):
        Q = [self.S(p) for p in pts]
        if fill is not None:
            self.d.polygon(Q, fill=fill)
        if col is not None:
            self.d.line(Q + [Q[0]], fill=col, width=max(1, int(w * SS)), joint="curve")
            rr = w * SS / 2
            for q in Q:
                self.d.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], fill=col)

    def circle(self, c, r, fill=None, col=INK, w=5, wob=0.0):
        pts = []
        ph = self.rng().uniform(0, 6.28) if wob else 0
        for i in range(72):
            a = 2 * math.pi * i / 72
            rr = r + (wob * math.sin(3 * a + ph) if wob else 0)
            pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        Q = [self.S(p) for p in pts]
        if fill is not None:
            self.d.polygon(Q, fill=fill)
        if col is not None:
            self.d.line(Q + [Q[0]], fill=col, width=max(1, int(w * SS)), joint="curve")

    def ell(self, c, rx, ry, fill=None, col=INK, w=4):
        b = [(c[0] - rx) * SS, (c[1] - ry) * SS, (c[0] + rx) * SS, (c[1] + ry) * SS]
        self.d.ellipse(b, fill=fill, outline=col, width=max(1, int(w * SS)) if col else 0)

    def rrect(self, box, rad, fill=None, col=INK, w=5):
        b = [box[0] * SS, box[1] * SS, box[2] * SS, box[3] * SS]
        self.d.rounded_rectangle(b, radius=rad * SS, fill=fill, outline=col,
                                 width=max(1, int(w * SS)) if col else 0)

    def arc(self, c, rx, ry, a0, a1, w=5, col=INK, n=24, frac=1.0):
        pts = []
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)))
        self.line(pts, w, col, frac=frac)

    def text(self, s, p, size, col=INK, f=None, anchor="mm"):
        self.d.text((p[0] * SS, p[1] * SS), s, font=font(f or FONT_INT, int(size * SS)), fill=col, anchor=anchor)


# -------------------------------------------------------------- tokoh
POSES = {
    "stand": dict(L=(-14, -8), R=(14, 8)),
    "phone": dict(R=(100, 172), L=(-16, -10), lean=-3),
    "head": dict(L=(-100, -190), R=(100, 190)),
    "think": dict(R=(54, 218), L=(-18, -10), lean=2),
    "present": dict(L=(-62, -80), R=(62, 80)),
    "point_r": dict(R=(96, 96), L=(-14, -8)),
    "point_l": dict(L=(-96, -96), R=(14, 8)),
    "cheer": dict(L=(-150, -172), R=(150, 172)),
    "up_r": dict(R=(90, 155), L=(-14, -8), lean=3),
    "shrug": dict(L=(-62, -160), R=(62, 160)),
    "slump": dict(L=(-6, -3), R=(6, 3), lean=7),
    "walk": dict(L=(-14, -8), R=(14, 8), walk=1),
}


def person(pen, x, y, s, expr, pose, t, talk=0.0, look=(0, 0), dry=False):
    P = dict(L=(-14, -8), R=(14, 8), LL=(-7, -3), RL=(7, 3), lean=0, walk=0)
    P.update(POSES.get(pose, POSES["stand"]))
    sway = math.sin(t * 2.2) * 3.0
    g = math.sin(t * 9.0) * 7.0 * talk
    LA, RA = list(P["L"]), list(P["R"])
    LA[0] += sway
    LA[1] += sway * 0.6
    RA[0] -= sway
    RA[1] -= sway * 0.6 - g
    LL, RL = P["LL"], P["RL"]
    if P["walk"]:
        w = math.sin(t * 7.0)
        a = 22 * w
        LL, RL = (a, a - 10), (-a, -a - 10)
        LA[0] += 10 * w
        RA[0] += 10 * w
    R = 44 * s
    neck, torso = 6 * s, 108 * s
    ua, la = 60 * s, 56 * s
    ul, ll = 74 * s, 72 * s
    bob = math.sin(t * 5.0) * 1.4 * s + (abs(math.sin(t * 7.0)) * 4 * s if P["walk"] else 0)
    lean = math.radians(P["lean"])
    hip = (x, y - (ul + ll) * 0.97 + bob)
    d = (math.sin(lean), -math.cos(lean))
    neck_pt = (hip[0] + d[0] * torso, hip[1] + d[1] * torso)
    head = (neck_pt[0] + d[0] * (neck + R), neck_pt[1] + d[1] * (neck + R))
    sh = (hip[0] + d[0] * torso * 0.9, hip[1] + d[1] * torso * 0.9)

    def limb(st, a1, a2, l1, l2):
        a1, a2 = math.radians(a1), math.radians(a2)
        p1 = (st[0] + l1 * math.sin(a1), st[1] + l1 * math.cos(a1))
        return p1, (p1[0] + l2 * math.sin(a2), p1[1] + l2 * math.cos(a2))

    l1, l2 = limb(sh, LA[0], LA[1], ua, la)
    r1, r2 = limb(sh, RA[0], RA[1], ua, la)
    a1, a2 = limb(hip, LL[0], LL[1], ul, ll)
    b1, b2 = limb(hip, RL[0], RL[1], ul, ll)
    J = dict(head=head, hand_l=l2, hand_r=r2, hip=hip, neck=neck_pt, R=R, sh=sh)
    if dry:
        return J
    lw = 7.5 * s
    pen.line([hip, a1, a2], lw)
    pen.line([hip, b1, b2], lw)
    for a, ang in ((a2, LL[1]), (b2, RL[1])):
        k = -1 if ang < -2 else 1
        pen.ell((a[0] + k * 6 * s, a[1] + 1.5 * s), 13 * s, 6 * s, fill=INK, col=None)
    pen.line([hip, neck_pt], lw * 1.3)
    pen.line([sh, l1, l2], lw)
    pen.line([sh, r1, r2], lw)
    for hnd in (l2, r2):
        pen.circle(hnd, 5.6 * s, fill=INK, col=None)
    pen.circle(head, R, fill=WHITE, w=lw * 0.9)
    top = (head[0] + d[0] * R, head[1] + d[1] * R)
    pen.line([(top[0] - 1 * s, top[1] + 1 * s), (top[0] + 2 * s, top[1] - 10 * s), (top[0] + 9 * s, top[1] - 15 * s)],
             lw * 0.6)
    face(pen, head, R, expr, t, look, s, talk)
    return J


def face(pen, hc, R, expr, t, look, s, talk):
    lx, ly = look
    ex, ey = 0.36 * R, -0.04 * R
    L = (hc[0] - ex + lx, hc[1] + ey + ly)
    Rr = (hc[0] + ex + lx, hc[1] + ey + ly)
    blink = (t % 3.4) < 0.12
    ew = 4.6 * s
    dot = 3.9 * s
    my = hc[1] + 0.52 * R
    open_m = talk > 0.12 and expr != "shock"

    def dots(half=False):
        for c in (L, Rr):
            if blink or half:
                pen.line([(c[0] - dot, c[1]), (c[0] + dot, c[1])], ew * 0.9)
            else:
                pen.circle(c, dot, fill=INK, col=None)

    def brow(c, dx0, dy0, dx1, dy1):
        pen.line([(c[0] + dx0 * R, c[1] + dy0 * R), (c[0] + dx1 * R, c[1] + dy1 * R)], ew * 0.9)

    def mouth_open(cx, cy, w=0.17):
        h = (0.04 + 0.2 * min(1.0, talk)) * R
        pen.ell((cx, cy + h * 0.4), w * R, h, fill=INK, col=None)

    if expr == "neutral":
        dots()
        if open_m:
            mouth_open(hc[0], my)
        else:
            pen.line([(hc[0] - 0.18 * R, my), (hc[0] + 0.18 * R, my)], ew)
    elif expr == "sad":
        dots()
        brow(L, -0.24, -0.20, 0.14, -0.32)
        brow(Rr, 0.24, -0.20, -0.14, -0.32)
        if open_m:
            mouth_open(hc[0], my + 0.12 * R, 0.15)
        else:
            pen.arc((hc[0], my + 0.28 * R), 0.26 * R, 0.2 * R, 200, 340, ew)
        k = (t * 1.3) % 1.0
        pen.ell((L[0] - 0.06 * R, L[1] + 0.22 * R + k * 0.8 * R), 0.07 * R, 0.1 * R, fill=SKY, col=None)
    elif expr == "shock":
        for c in (L, Rr):
            pen.circle(c, 0.15 * R, fill=WHITE, w=ew * 0.8)
            pen.circle((c[0] + lx * 0.2, c[1]), 2.4 * s, fill=INK, col=None)
        pen.arc((L[0], L[1] - 0.28 * R), 0.2 * R, 0.1 * R, 190, 350, ew * 0.9)
        pen.arc((Rr[0], Rr[1] - 0.28 * R), 0.2 * R, 0.1 * R, 190, 350, ew * 0.9)
        pen.ell((hc[0], my + 0.1 * R), 0.13 * R, (0.15 + 0.1 * talk) * R, fill=INK, col=None)
        k = (t * 1.6) % 1.0
        pen.ell((hc[0] + R * 0.95, hc[1] - 0.45 * R + k * 0.5 * R), 0.08 * R, 0.12 * R, fill=SKY, col=None)
    elif expr == "think":
        dots()
        brow(L, -0.2, -0.22, 0.16, -0.26)
        brow(Rr, -0.16, -0.30, 0.22, -0.40)
        if open_m:
            mouth_open(hc[0] + 0.04 * R, my, 0.13)
        else:
            pen.line([(hc[0] - 0.14 * R, my + 0.04 * R), (hc[0] + 0.2 * R, my - 0.02 * R)], ew)
    elif expr == "happy":
        for c in (L, Rr):
            if blink:
                pen.line([(c[0] - dot, c[1]), (c[0] + dot, c[1])], ew * 0.9)
            else:
                pen.arc((c[0], c[1] + 0.05 * R), 0.16 * R, 0.14 * R, 200, 340, ew)
        if open_m:
            mouth_open(hc[0], my - 0.02 * R, 0.2)
        else:
            pen.arc((hc[0], my - 0.12 * R), 0.3 * R, 0.26 * R, 20, 160, ew)
        for c, k in ((L, -1), (Rr, 1)):
            pen.ell((c[0] + k * 0.12 * R, c[1] + 0.3 * R), 0.13 * R, 0.08 * R, fill=PINK, col=None)
    elif expr == "smirk":
        dots()
        brow(Rr, -0.16, -0.30, 0.2, -0.38)
        if open_m:
            mouth_open(hc[0] + 0.05 * R, my, 0.16)
        else:
            pen.arc((hc[0] + 0.06 * R, my - 0.1 * R), 0.26 * R, 0.2 * R, 20, 150, ew)
    elif expr == "sleepy":
        dots(half=True)
        brow(L, -0.22, -0.18, 0.16, -0.22)
        brow(Rr, 0.22, -0.18, -0.16, -0.22)
        if open_m:
            mouth_open(hc[0], my + 0.04 * R, 0.13)
        else:
            pen.ell((hc[0], my + 0.04 * R), 0.07 * R, 0.06 * R, fill=INK, col=None)
    else:
        dots()


# ---------------------------------------------------------- properti
HEIGHT = dict(bag=112, sack=120, bulb=130, bill=112, cup=150, boba=150, coin=50, jar=230, calendar=160,
              clock=140, book=70, laptop=90, house=150, plant=140, piggy=100, heart=90, card=80, sign=70,
              pot=100, phone=300)
JAR_DROPS = (0.9, 2.0, 3.1)
JAR_DUR = 0.35


def p_bag(pen, x, by, sc, arg, ts):
    w, h = 96 * sc, 112 * sc
    col = COLORS.get(arg or "orange", ORANGE)
    pen.poly([(x - w * 0.44, by - h), (x + w * 0.44, by - h), (x + w * 0.5, by), (x - w * 0.5, by)], fill=col, w=5)
    pen.arc((x, by - h), w * 0.22, h * 0.34, 180, 360, 5)
    pen.rrect((x - w * 0.17, by - h * 0.62, x + w * 0.17, by - h * 0.36), 5, fill=WHITE, w=3)


def p_sack(pen, x, by, sc, arg, ts):
    w, h = 96 * sc, 104 * sc
    pen.poly([(x - w * 0.38, by - h), (x + w * 0.38, by - h), (x + w * 0.5, by - h * 0.55), (x + w * 0.46, by),
              (x - w * 0.46, by), (x - w * 0.5, by - h * 0.55)], fill=BEIGE, w=5)
    pen.line([(x - w * 0.3, by - h), (x - w * 0.15, by - h * 1.18), (x + w * 0.15, by - h * 1.18),
              (x + w * 0.3, by - h)], 5)
    pen.text((arg or "BERAS")[:7], (x, by - h * 0.42), max(8, int(18 * sc)), INK, FONT_POP)


def p_bulb(pen, x, by, sc, arg, ts):
    r = 40 * sc
    c = (x, by - 62 * sc - r * 0.2)
    pen.circle(c, r, fill=YELLOW, w=5)
    pen.rrect((x - 18 * sc, by - 36 * sc, x + 18 * sc, by - 6 * sc), 6, fill=(190, 190, 195), w=5)
    pen.line([(x - 10 * sc, c[1] + 6 * sc), (x - 4 * sc, c[1] - 10 * sc), (x + 4 * sc, c[1] + 6 * sc),
              (x + 10 * sc, c[1] - 10 * sc)], 4)
    for a in (-60, -20, 20, 60):
        ar = math.radians(a - 90)
        pen.line([(c[0] + math.cos(ar) * (r + 8), c[1] + math.sin(ar) * (r + 8)),
                  (c[0] + math.cos(ar) * (r + 20), c[1] + math.sin(ar) * (r + 20))], 4)


def p_bill(pen, x, by, sc, arg, ts):
    w, h = 100 * sc, 112 * sc
    pen.poly([(x - w / 2, by - h), (x + w * 0.5 - 18 * sc, by - h), (x + w / 2, by - h + 18 * sc), (x + w / 2, by),
              (x - w / 2, by)], fill=WHITE, w=5)
    for i in range(3):
        pen.line([(x - w * 0.32, by - h * 0.72 + i * 17 * sc), (x + w * 0.3 - (i == 2) * 18 * sc,
                                                                  by - h * 0.72 + i * 17 * sc)], 4, GRAY)
    pen.text(arg or "Rp", (x, by - h * 0.2), max(8, int(26 * sc)), RED, FONT_POP)


def p_cup(pen, x, by, sc, arg, ts, boba=False):
    w, h = 78 * sc, 104 * sc
    pen.poly([(x - w * 0.5, by - h), (x + w * 0.5, by - h), (x + w * 0.36, by), (x - w * 0.36, by)],
             fill=(250, 232, 210) if not boba else (236, 214, 238), w=5)
    pen.rrect((x - w * 0.56, by - h - 12 * sc, x + w * 0.56, by - h + 2), 5, fill=WHITE, w=5)
    pen.line([(x + 8 * sc, by - h - 10 * sc), (x + 20 * sc, by - h - 46 * sc)], 6, RED)
    if boba:
        for dx, dy in [(-14, -10), (4, -8), (18, -12), (-4, -24), (10, -26)]:
            pen.circle((x + dx * sc, by + dy * sc), 6 * sc, fill=BROWN, col=None)
    else:
        pen.poly([(x - w * 0.44, by - h * 0.5), (x + w * 0.44, by - h * 0.5), (x + w * 0.34, by - 3),
                  (x - w * 0.34, by - 3)], fill=BROWN, col=None)


def p_boba(pen, x, by, sc, arg, ts):
    p_cup(pen, x, by, sc, arg, ts, True)


def p_coin(pen, x, by, sc, arg, ts):
    r = 24 * sc
    pen.circle((x, by - r), r, fill=YELLOW, w=5)
    pen.text((arg or "Rp")[:3], (x, by - r), max(8, int(r * 0.9)), INK, FONT_POP)


def p_jar(pen, x, by, sc, arg, ts):
    w, h = 180 * sc, 230 * sc
    a, b = (arg or "DANA|DARURAT").split("|") if "|" in (arg or "DANA|DARURAT") else (arg, "")
    landed = sum(1 for d in JAR_DROPS if ts >= d + JAR_DUR)
    pen.rrect((x - w / 2, by - h, x + w / 2, by), 26 * sc, fill=(236, 246, 255), w=6)
    pen.rrect((x - w * 0.38, by - h - 22 * sc, x + w * 0.38, by - h + 4), 8, fill=(200, 200, 206), w=6)
    for k in range(landed):
        pen.ell((x, by - 16 * sc - k * 15 * sc), w * 0.30, 9 * sc, fill=YELLOW, col=INK, w=3)
    pen.rrect((x - w * 0.38, by - h * 0.62, x + w * 0.38, by - h * 0.28), 8, fill=BLUE, w=4)
    pen.text(a, (x, by - h * (0.52 if b else 0.45)), max(8, int(20 * sc)), WHITE, FONT_POP)
    if b:
        pen.text(b, (x, by - h * 0.37), max(8, int(18 * sc)), WHITE, FONT_POP)
    for i, d in enumerate(JAR_DROPS):
        if d <= ts < d + JAR_DUR:
            k = (ts - d) / JAR_DUR
            y0, y1 = by - h - 110 * sc, by - 16 * sc - i * 15 * sc
            pen.circle((x, y0 + (y1 - y0) * k * k), 20 * sc, fill=YELLOW, w=4)
            pen.text("Rp", (x, y0 + (y1 - y0) * k * k), int(16 * sc), INK, FONT_POP)
        if d + JAR_DUR <= ts < d + JAR_DUR + 0.35:
            k = (ts - d - JAR_DUR) / 0.35
            for q in range(6):
                ar = q * math.pi / 3 + 0.3
                c = (x, by - h - 30 * sc)
                pen.line([(c[0] + (40 + 20 * k) * math.cos(ar), c[1] + (40 + 20 * k) * math.sin(ar) * 0.7),
                          (c[0] + (52 + 28 * k) * math.cos(ar), c[1] + (52 + 28 * k) * math.sin(ar) * 0.7)],
                         5, YELLOW)


def p_calendar(pen, x, by, sc, arg, ts):
    w = 150 * sc
    h = w * 1.05
    top = by - h
    pen.rrect((x - w / 2, top, x + w / 2, by), 14, fill=WHITE, w=6)
    pen.rrect((x - w / 2, top, x + w / 2, top + h * 0.28), 14, fill=RED, w=6)
    for dx in (-0.25, 0.25):
        pen.line([(x + dx * w, top - 12), (x + dx * w, top + 8)], 6)
    pen.text((arg or "25")[:5], (x, top + h * 0.64), int(w * (0.5 if len(arg or "25") <= 2 else 0.3)), INK, FONT_POP)


def p_clock(pen, x, by, sc, arg, ts):
    r = 56 * sc
    c = (x, by - r - 10 * sc)
    pen.circle(c, r, fill=WHITE, w=6)
    hh, mm = 3, 0
    try:
        a, b = (arg or "03.00").replace(":", ".").split(".")[:2]
        hh, mm = int(a), int(b)
    except Exception:  # noqa
        pass
    for k in range(12):
        ar = math.radians(k * 30)
        pen.line([(c[0] + math.sin(ar) * r * 0.82, c[1] - math.cos(ar) * r * 0.82),
                  (c[0] + math.sin(ar) * r * 0.92, c[1] - math.cos(ar) * r * 0.92)], 3)
    ah = math.radians((hh % 12) * 30 + mm * 0.5)
    am = math.radians(mm * 6)
    pen.line([c, (c[0] + math.sin(ah) * r * 0.5, c[1] - math.cos(ah) * r * 0.5)], 6)
    pen.line([c, (c[0] + math.sin(am) * r * 0.75, c[1] - math.cos(am) * r * 0.75)], 4)
    pen.circle(c, 4, fill=INK, col=None)
    pen.text(arg or "03.00", (x, by + 4 * sc), max(8, int(22 * sc)), GRAY, FONT_INT)


def p_book(pen, x, by, sc, arg, ts):
    w, h = 110 * sc, 70 * sc
    pen.poly([(x - w / 2, by - h), (x, by - h + 8 * sc), (x + w / 2, by - h), (x + w / 2, by - 6 * sc), (x, by),
              (x - w / 2, by - 6 * sc)], fill=WHITE, w=5)
    pen.line([(x, by - h + 8 * sc), (x, by)], 4)
    for i in range(3):
        pen.line([(x - w * 0.4, by - h * 0.7 + i * 12 * sc), (x - w * 0.1, by - h * 0.62 + i * 12 * sc)], 3, GRAY)
        pen.line([(x + w * 0.1, by - h * 0.62 + i * 12 * sc), (x + w * 0.4, by - h * 0.7 + i * 12 * sc)], 3, GRAY)


def p_laptop(pen, x, by, sc, arg, ts):
    w, h = 140 * sc, 90 * sc
    pen.rrect((x - w * 0.42, by - h, x + w * 0.42, by - 14 * sc), 8, fill=WHITE, w=5)
    pen.poly([(x - w * 0.5, by - 14 * sc), (x + w * 0.5, by - 14 * sc), (x + w * 0.56, by), (x - w * 0.56, by)],
             fill=(205, 205, 210), w=5)
    pen.text((arg or ":)")[:8], (x, by - h * 0.55), max(8, int(24 * sc)), BLUE, FONT_POP)


def p_house(pen, x, by, sc, arg, ts):
    w, h = 130 * sc, 100 * sc
    pen.poly([(x - w / 2, by - h), (x + w / 2, by - h), (x + w / 2, by), (x - w / 2, by)], fill=WHITE, w=5)
    pen.poly([(x - w * 0.62, by - h), (x, by - h - 56 * sc), (x + w * 0.62, by - h)], fill=RED, w=5)
    pen.rrect((x - 16 * sc, by - 52 * sc, x + 16 * sc, by), 4, fill=BROWN, w=4)
    pen.rrect((x + 26 * sc, by - 74 * sc, x + 52 * sc, by - 48 * sc), 3, fill=SKY, w=4)


def p_plant(pen, x, by, sc, arg, ts):
    pen.poly([(x - 34 * sc, by - 52 * sc), (x + 34 * sc, by - 52 * sc), (x + 24 * sc, by), (x - 24 * sc, by)],
             fill=(214, 140, 100), w=5)
    pen.line([(x, by - 52 * sc), (x, by - 110 * sc)], 5, (60, 140, 80))
    for dx, dy, a in [(-30, -96, 1), (30, -104, -1), (-22, -76, 1), (24, -80, -1)]:
        c = (x + dx * sc, by + dy * sc)
        pen.poly([(x, by - 70 * sc), (c[0], c[1] - 14 * sc), (c[0] + a * 18 * sc, c[1] + 6 * sc)], fill=GREEN, w=4)


def p_piggy(pen, x, by, sc, arg, ts):
    pen.ell((x, by - 44 * sc), 56 * sc, 40 * sc, fill=PINK, w=5)
    pen.ell((x + 58 * sc, by - 42 * sc), 14 * sc, 12 * sc, fill=PINK, w=5)
    pen.poly([(x + 20 * sc, by - 80 * sc), (x + 36 * sc, by - 98 * sc), (x + 42 * sc, by - 74 * sc)], fill=PINK, w=4)
    pen.line([(x - 18 * sc, by - 84 * sc), (x + 6 * sc, by - 84 * sc)], 6)
    for dx in (-30, 24):
        pen.line([(x + dx * sc, by - 10 * sc), (x + dx * sc, by)], 8)
    pen.circle((x + 34 * sc, by - 52 * sc), 3.5 * sc, fill=INK, col=None)


def p_heart(pen, x, by, sc, arg, ts):
    beat = 1 + 0.06 * math.sin(ts * 7)
    s = sc * beat
    c = (x, by - 40 * s)
    pts = []
    for i in range(60):
        a = 2 * math.pi * i / 60
        px = 16 * math.sin(a) ** 3
        py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((c[0] + px * 2.2 * s, c[1] + py * 2.2 * s))
    pen.poly(pts, fill=RED, w=4)


def p_card(pen, x, by, sc, arg, ts):
    w, h = 120 * sc, 76 * sc
    pen.rrect((x - w / 2, by - h, x + w / 2, by), 10, fill=BLUE, w=5)
    pen.rrect((x - w * 0.42, by - h * 0.72, x - w * 0.2, by - h * 0.5), 3, fill=YELLOW, w=3)
    pen.line([(x - w * 0.4, by - h * 0.22), (x + w * 0.1, by - h * 0.22)], 4, WHITE)
    pen.text((arg or "")[:10], (x + w * 0.2, by - h * 0.62), max(8, int(14 * sc)), WHITE, FONT_POP)


def p_sign(pen, x, by, sc, arg, ts):
    txt, col = (arg or "...|blue").split("|") if "|" in (arg or "") else (arg or "...", "blue")
    w, h = 190 * sc, 66 * sc
    pen.rrect((x - w / 2, by - h, x + w / 2, by), 16, fill=COLORS.get(col, BLUE), w=5)
    size = 34 if len(txt) <= 7 else (26 if len(txt) <= 11 else 20)
    pen.text(txt, (x, by - h / 2 + 1), max(8, int(size * sc)), WHITE, FONT_POP)


def p_pot(pen, x, by, sc, arg, ts):
    pen.poly([(x - 50 * sc, by - 70 * sc), (x + 50 * sc, by - 70 * sc), (x + 44 * sc, by), (x - 44 * sc, by)],
             fill=(190, 190, 196), w=5)
    pen.line([(x - 64 * sc, by - 56 * sc), (x - 50 * sc, by - 56 * sc)], 6)
    pen.line([(x + 50 * sc, by - 56 * sc), (x + 64 * sc, by - 56 * sc)], 6)
    pen.rrect((x - 54 * sc, by - 82 * sc, x + 54 * sc, by - 68 * sc), 6, fill=(150, 150, 158), w=5)
    for dx in (-18, 4, 24):
        k = (ts * 1.2 + dx) % 1.0
        pen.arc((x + dx * sc, by - 100 * sc - k * 20 * sc), 7 * sc, 12 * sc, 270, 450, 4, GRAY, frac=1 - k * 0.4)


def p_phone(pen, x, by, sc, arg, ts):
    w, h = 190 * sc, 300 * sc
    cy = by - h / 2
    parts = (arg or "").split("|")
    lab = parts[0] if parts else ""
    val = parts[1] if len(parts) > 1 else ""
    colr = COLORS.get(parts[2], INK) if len(parts) > 2 else INK
    trend = parts[3] if len(parts) > 3 else ""
    pen.rrect((x - w / 2, cy - h / 2, x + w / 2, cy + h / 2), 22 * sc, fill=WHITE, w=6)
    pen.line([(x - 20 * sc, cy - h / 2 + 18 * sc), (x + 20 * sc, cy - h / 2 + 18 * sc)], 5)
    if lab:
        pen.text(lab[:16], (x, cy - h / 2 + 62 * sc), max(8, int(24 * sc)), GRAY)
    if val:
        pen.text(val[:11], (x, cy - h / 2 + 108 * sc), max(8, int((30 if len(val) <= 9 else 24) * sc)), colr, FONT_POP)
    if trend in ("down", "up"):
        gx, gy = x - w / 2 + 28 * sc, cy + 20 * sc
        pts = [(gx, gy), (gx + 35 * sc, gy + 8 * sc), (gx + 62 * sc, gy + 4 * sc), (gx + 92 * sc, gy + 42 * sc),
               (gx + 116 * sc, gy + 62 * sc)]
        if trend == "up":
            pts = [(px, 2 * gy + 62 * sc - py) for px, py in pts]
        pen.line(pts, 6, colr if colr != INK else RED, frac=min(1, 0.5 + ts / 3))


PROPS = dict(bag=p_bag, sack=p_sack, bulb=p_bulb, bill=p_bill, cup=p_cup, boba=p_boba, coin=p_coin, jar=p_jar,
             calendar=p_calendar, clock=p_clock, book=p_book, laptop=p_laptop, house=p_house, plant=p_plant,
             piggy=p_piggy, heart=p_heart, card=p_card, sign=p_sign, pot=p_pot, phone=p_phone)
SLOTS = {"gl1": (130, "g"), "gl2": (250, "g"), "gr1": (590, "g"), "gr2": (470, "g"),
         "ml": (125, "m"), "mr": (595, "m"), "tl": (140, "t"), "tr": (580, "t")}
SLOT_Y = {"g": 1020, "m": 790, "t": 640}


def top_symbol(pen, kind, head, R, ts, idx):
    bob = math.sin(ts * 4 + idx) * 6
    if kind == "q":
        pen.text("?", (head[0] + R * 2.2, head[1] - R * 1.1 + bob), 96, ORANGE, FONT_POP)
        pen.text("?", (head[0] - R * 2.2, head[1] - R * 0.7 - bob), 66, BLUE, FONT_POP)
    elif kind == "excl":
        pen.text("!!", (head[0] + R * 2.0, head[1] - R * 1.2 + math.sin(ts * 14) * 3), 64, RED, FONT_POP)
    elif kind == "idea":
        c = (head[0] + R * 0.2, head[1] - R * 1.9 + bob)
        pen.circle(c, 26, fill=YELLOW, w=5)
        pen.rrect((c[0] - 11, c[1] + 24, c[0] + 11, c[1] + 40), 4, fill=(190, 190, 195), w=4)
        for a in (-70, -35, 0, 35, 70):
            ar = math.radians(a - 90)
            pen.line([(c[0] + math.cos(ar) * 36, c[1] + math.sin(ar) * 36),
                      (c[0] + math.cos(ar) * 50, c[1] + math.sin(ar) * 50)], 4)
    elif kind == "heart":
        p_heart(pen, head[0] + R * 2.0, head[1] - R * 0.8 + bob, 0.55, "", ts)
    elif kind == "zzz":
        for i, (dx, dy, sz) in enumerate([(1.7, -0.9, 50), (2.3, -1.6, 38), (2.8, -2.2, 28)]):
            pen.text("Z", (head[0] + R * dx, head[1] + R * dy + math.sin(ts * 3 + i) * 5), sz, BLUE, FONT_POP)


def hand_prop(pen, kind, arg, J, s, sc, ts):
    f = s / 1.42
    hr = J["hand_r"]
    if kind == "phone":
        p_phone(pen, hr[0] + 52 * f, hr[1] - 86 * f + 150 * sc * f + 0, sc * f * 1.0, arg, ts)
    elif kind == "coin":
        p_coin(pen, hr[0], hr[1] - 2, sc * f * 1.0, arg, ts)
    elif kind == "book":
        p_book(pen, hr[0] + 10 * f, hr[1] + 16 * f, sc * f * 1.1, arg, ts)
    elif kind == "cup":
        p_cup(pen, hr[0], hr[1] + 36 * f, sc * f * 0.75, arg, ts)
    elif kind == "heart":
        p_heart(pen, hr[0], hr[1] - 8 * f, sc * f * 0.6, arg, ts)
    elif kind == "bag":
        p_bag(pen, hr[0], hr[1] + 100 * f, sc * f * 0.9, arg, ts)
    elif kind == "laptop":
        p_laptop(pen, hr[0], hr[1] + 12 * f, sc * f * 0.7, arg, ts)
    else:
        PROPS[kind](pen, hr[0], hr[1] + 20 * f, sc * f * 0.8, arg, ts)


def ground(pen, y=1020, x0=70, x1=650):
    r = random.Random(5)
    pts = [(x0 + (x1 - x0) * i / 24, y + r.uniform(-1.0, 1.0)) for i in range(25)]
    pen.line(pts, 4, (160, 160, 165))


def prop_pop_time(i):
    return 0.35 + 0.4 * i


def draw_scene(pen, sc, ts, talk, seed_t):
    ground(pen)
    if sc.get("card"):
        draw_card(pen, sc, ts, talk)
        return
    s = sc.get("ps", 1.5)
    px = sc.get("px", 360)
    props = sc.get("p", [])
    J0 = person(pen, px, 1020, s, sc.get("e", "neutral"), sc.get("pose", "stand"), 0.0, dry=True)
    # properti tanah / dinding dulu (di belakang tokoh)
    behind = [(i, p) for i, p in enumerate(props) if p[1] in SLOTS]
    front = [(i, p) for i, p in enumerate(props) if p[1] == "hand"]
    tops = [(i, p) for i, p in enumerate(props) if p[1] == "top"]
    for i, (kind, slot, arg) in behind:
        k = pop(ts, prop_pop_time(i))
        if k <= 0.02:
            continue
        x, mode = SLOTS[slot]
        if kind == "jar" and slot.startswith("g"):
            x = J0["hand_r"][0] + 24 if sc.get("pose") in ("up_r", "present") else x
        h = HEIGHT.get(kind, 100) * k
        by = SLOT_Y[mode] if mode == "g" else SLOT_Y[mode] + h / 2
        PROPS[kind](pen, x, by, k, arg, ts)
    J = person(pen, px, 1020, s, sc.get("e", "neutral"), sc.get("pose", "stand"), ts, talk=talk)
    for i, (kind, slot, arg) in front:
        k = pop(ts, prop_pop_time(i), 0.3)
        if k > 0.02:
            hand_prop(pen, kind, arg, J, s, k, ts)
    for i, (kind, slot, arg) in tops:
        if ts > prop_pop_time(i):
            top_symbol(pen, kind, J["head"], J["R"], ts, i)


def draw_card(pen, sc, ts, talk):
    c = sc["card"]
    cx, top, bot = 360, 420, 770
    k = ease(ts / 0.4)
    off = (1 - k) * 40
    pen.rrect((60, top + off, 660, bot + off), 28, fill=WHITE, col=BLUE, w=7)
    pen.rrect((100, top - 22 + off, 330, top + 26 + off), 24, fill=BLUE, col=BLUE, w=2)
    pen.text("LANGKAH KECIL", (215, top + 2 + off), 25, WHITE, FONT_POP)
    pen.text(c["l1"], (cx, top + 82 + off), 30, INK)
    pen.text(c["l2"], (cx, top + 124 + off), 30, INK)
    for i, (name, ok) in enumerate(c.get("rows", [])[:3]):
        t0 = 0.9 + 0.6 * i
        y = top + 176 + i * 54 + off
        if ts < t0 - 0.2:
            continue
        pen.rrect((150, y, 186, y + 36), 6, fill=WHITE, w=4)
        if ok:
            f = ease((ts - t0 - 0.2) / 0.3)
            if f > 0:
                pen.line([(157, y + 20), (166, y + 29), (181, y + 8)], 6, GREEN, frac=f)
        strike = (not ok) and ts > 3.2
        pen.text(name[:24], (205, y + 19), 30, GRAY if strike else INK, anchor="lm")
        if not ok:
            f = ease((ts - 3.2) / 0.5)
            if f > 0:
                wd = 24 + 15 * len(name[:24])
                pen.line([(198, y + 20), (198 + wd * 0.3, y + 12), (198 + wd * 0.6, y + 27), (198 + wd, y + 15)],
                         7, RED, wob=0.8, frac=f)
    person(pen, 360, 1020, 0.62, "happy", "present", ts, talk=talk)


# ----------------------------------------------------------- teks
def headline(img, text, ts, first):
    lay = Image.new("RGBA", (W, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    clean = text.replace("*", "").replace("^", "")
    size = 54 if len(clean) <= 36 else (50 if len(clean) <= 52 else 44)
    f = font(FONT_POP, size)
    toks, cur = [], INK
    for w_ in text.split(" "):
        if w_.startswith("*"):
            cur = BLUE
        elif w_.startswith("^"):
            cur = ORANGE
        end = w_.endswith("*") or w_.endswith("^")
        toks.append((w_.strip("*^"), cur))
        if end:
            cur = INK
    lines, row = [], []
    for w_, col in toks:
        trial = " ".join(x[0] for x in row + [(w_, col)])
        if f.getlength(trial) > 640 and row:
            lines.append(row)
            row = [(w_, col)]
        else:
            row.append((w_, col))
    lines.append(row)
    y = 28
    for ln in lines[:4]:
        total = f.getlength(" ".join(x[0] for x in ln))
        x = (W - total) / 2
        for w_, col in ln:
            d.text((x, y + int(size * 0.92)), w_, font=f, fill=col, anchor="ls")
            x += f.getlength(w_ + " ")
        y += int(size * 1.28)
    a = 1.0 if first else ease(ts / 0.3)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    dy = 0 if first else int((1 - ease(ts / 0.3)) * 18)
    img.paste(lay, (0, 150 + dy), lay)


def watermark(img):
    d = ImageDraw.Draw(img)
    d.text((36, 62), "@mulaimandiri_", font=font(FONT_INT, 27), fill=(96, 96, 104), anchor="lm")
    d.text((W - 36, 62), "#wargamandiri", font=font(FONT_INT, 27), fill=(96, 96, 104), anchor="rm")


_grain = None


def grain():
    global _grain
    if _grain is None:
        _grain = np.random.default_rng(3).normal(0, 2.0, (H, W, 1)).astype(np.float32)
    return _grain


# ------------------------------------------------------------ konten
def load_contents(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["contents"]


VOICE_DIR = os.path.join(ROOT, "voice")


def recorded_ids():
    if not os.path.isdir(VOICE_DIR):
        return set()
    out = set()
    for f in os.listdir(VOICE_DIR):
        n = tts.rec_stem(f)
        if n and n[:1] == "c" and n[1:].isdigit():
            out.add(n)
    return out


def voice_source():
    src = os.environ.get("STICK_VOICE_SOURCE", "auto").strip().lower()
    if src == "auto":
        src = "klon" if tts.clone_ready() else ("rekaman" if recorded_ids() else "tts")
    return src


def pick(contents, args):
    if voice_source() == "rekaman" and not args.id:
        have = recorded_ids()
        contents = [c for c in contents if c["id"] in have]
        if not contents:
            raise SystemExit("STICK_VOICE_SOURCE=rekaman tetapi belum ada file rekaman di stickman/voice/")
    if args.id:
        for c in contents:
            if c["id"] == args.id:
                return c
        raise SystemExit(f"id {args.id} tidak ada")
    if args.day:
        return contents[(args.day - 1) % len(contents)]
    start = datetime.date.fromisoformat(os.environ.get("STICK_START_DATE", "2026-11-08"))
    wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).date()
    return contents[(wib - start).days % len(contents)]


def est_len(text):
    return max(1.8, len(text.split()) / 2.5 + 0.4)


def plan(content, workdir, use_voice=True):
    """Susun linimasa: durasi tiap adegan mengikuti panjang suara."""
    scenes, t = [], 0.0
    voice_parts = []
    engines = set()
    os.makedirs(workdir, exist_ok=True)
    rec_parts = None
    src = voice_source()
    if use_voice and src in ("rekaman", "klon"):
        rp = tts.find_recording(VOICE_DIR, content["id"])
        if rp:
            try:
                rec_parts = tts.split_recording(rp, len(content["scenes"]), workdir)
            except RuntimeError as e:
                if src == "rekaman":
                    raise                                   # error jelas; main mencoba konten berekaman lain
                print(f"::warning::{e} -> {content['id']} memakai suara klon", flush=True)
        elif src == "rekaman" and os.environ.get("STICK_REQUIRE_VOICE") == "1":
            raise SystemExit(f"rekaman {content['id']} tidak ada")
    for i, sc in enumerate(content["scenes"]):
        lead = 0.12 if i == 0 else 0.22
        tail = 0.65
        a = None
        if rec_parts is not None:
            a = rec_parts[i]
            engines.add("rekaman")
        elif use_voice:
            try:
                a, eng = tts.synth(sc["say"], workdir, f"s{i}")
                engines.add(eng)
            except Exception as e:  # noqa
                print(f"::warning::suara adegan {i + 1} gagal: {e}")
                if os.environ.get("STICK_REQUIRE_VOICE") == "1":
                    raise
        vlen = len(a) / SR if a is not None else est_len(sc["say"])
        dur = max(3.0, lead + vlen + tail)
        if sc.get("card"):
            dur = max(dur, 6.8)
        scenes.append(dict(sc, start=t, dur=dur, lead=lead, vlen=vlen))
        voice_parts.append((t + lead, a))
        t += dur
    total = t
    track = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
    for at, a in voice_parts:
        if a is not None:
            i = int(at * SR)
            track[i:i + len(a)] += a[: len(track) - i]
    return scenes, total, track, engines


def talk_curve(track, total):
    n = int(total * FPS) + 2
    raw = np.zeros(n, dtype=np.float32)
    w = SR // FPS
    for i in range(n):
        seg = track[i * w:(i + 1) * w]
        raw[i] = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    nz = raw[raw > 0.01]
    p = np.percentile(nz, 90) if len(nz) else 1.0
    raw = np.clip(raw / (p + 1e-6), 0, 1.2)
    out = np.zeros_like(raw)
    for i in range(n):
        out[i] = max(raw[i], out[i - 1] * 0.55 if i else 0)
    return np.clip(out, 0, 1)


# ------------------------------------------------------------- audio
def mhz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def movavg(x, k):
    c = np.cumsum(np.insert(x, 0, 0))
    y = (c[k:] - c[:-k]) / k
    pad = np.concatenate([np.full(k // 2, y[0]), y, np.full(k - k // 2 - 1, y[-1])])
    return pad[: len(x)]


def _pluck(f, dur, vol):
    n = int(SR * dur)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.38 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 12)
    return s * np.exp(-t * 5.5) * np.minimum(1, t / 0.004) * vol


def _pad(freqs, dur, vol):
    n = int(SR * dur)
    t = np.arange(n) / SR
    e = np.clip(np.minimum(t / 0.5, 1) * np.minimum((dur - t) / 0.6, 1), 0, 1)
    return sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs) * e * vol


def _bass(f, dur, vol):
    n = int(SR * dur)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)) * np.minimum(t / 0.01, 1) * np.exp(-t * 2.2) * vol


def _kick(vol):
    n = int(SR * 0.22)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-t * 28)) / SR) * np.exp(-t * 16) * vol


def _shaker(rg, vol):
    n = int(SR * 0.06)
    x = np.diff(rg.normal(0, 1, n), prepend=0)
    return x * np.exp(-np.arange(n) / SR * 60) * vol


def sfx_pop(vol=0.2):
    n = int(SR * 0.12)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(500 + 900 * (t / 0.12)) / SR) * np.exp(-t * 28) * vol


def sfx_ding(vol=0.22):
    n = int(SR * 0.7)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 6) * vol


PROGS = [  # (nama, bpm, [(midi_akar, minor)])
    ("ceria", 96, [(48, 0), (45, 1), (41, 0), (43, 0)]),
    ("tenang", 84, [(45, 1), (41, 0), (48, 0), (43, 0)]),
    ("harapan", 92, [(41, 0), (43, 0), (45, 1), (48, 0)]),
    ("santai", 88, [(48, 0), (43, 0), (45, 1), (41, 0)]),
]


def build_audio(path, scenes, total, voice, mood):
    rg = np.random.default_rng(11 + mood)
    rest = random.Random(4 + mood)
    name, bpm, prog = PROGS[mood % len(PROGS)]
    beat = 60 / bpm
    bar = beat * 4
    N = int((total + 0.5) * SR)
    music = np.zeros(N, dtype=np.float32)

    def put(buf, x, at):
        i = int(at * SR)
        if 0 <= i < len(buf):
            j = min(len(buf), i + len(x))
            buf[i:j] += x[: j - i].astype(np.float32)

    pat = [0, 2, 1, 3, 2, 1, 2, 1]
    for b in range(int(math.ceil(total / bar)) + 1):
        r, minor = prog[b % 4]
        iv = [0, 3 if minor else 4, 7, 12]
        tones = [mhz(r + 12 + k) for k in iv]
        at = b * bar
        put(music, _pad(tones[:3], bar + 0.4, 0.05), at)
        put(music, _bass(mhz(r), beat * 2, 0.2), at)
        put(music, _bass(mhz(r), beat * 2, 0.14), at + beat * 2)
        put(music, _kick(0.2), at)
        put(music, _kick(0.12), at + beat * 2)
        for i, p in enumerate(pat):
            if rest.random() < 0.18 or (i == 7 and rest.random() < 0.5):
                continue
            tt = at + i * beat / 2
            put(music, _pluck(tones[p] * 2, 0.5, 0.17 if i % 2 == 0 else 0.11), tt)
            put(music, _shaker(rg, 0.035 if i % 2 else 0.02), tt)
    vt = np.zeros(N, dtype=np.float32)
    vt[: min(N, len(voice))] = voice[:N]
    env = movavg(np.abs(vt), int(SR * 0.12))
    duck = 1 - 0.72 * np.clip(env / 0.09, 0, 1)
    duck = movavg(duck.astype(np.float32), int(SR * 0.25))
    mix = music * 0.7 * duck
    fx = np.zeros(N, dtype=np.float32)
    for sc in scenes:
        put(fx, sfx_pop(0.16), sc["start"])
        for i, p in enumerate(sc.get("p", [])):
            if p[1] != "top":
                put(fx, sfx_pop(0.1), sc["start"] + prop_pop_time(i))
            if p[0] == "jar":
                for d in JAR_DROPS:
                    if d + 0.4 < sc["dur"]:
                        put(fx, sfx_ding(0.18), sc["start"] + d + JAR_DUR)
        if sc.get("card"):
            for k, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
                put(fx, _pluck(f, 0.6, 0.18), sc["start"] + 3.3 + k * 0.08)
    out = mix + fx + vt * 1.0
    out = out[: int(total * SR)]
    out = out / max(1e-6, float(np.max(np.abs(out)))) * 0.9
    fo = int(SR * 1.2)
    out[-fo:] *= np.linspace(1, 0, fo)
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ------------------------------------------------------------ render
class Film:
    def __init__(self, scenes, total, talk):
        self.scenes, self.total, self.talk = scenes, total, talk

    def frame(self, t):
        t = min(t, self.total - 1e-3)
        sc = next(s for s in self.scenes if s["start"] <= t < s["start"] + s["dur"])
        ts = t - sc["start"]
        f = int(t * FPS)
        talk = float(self.talk[min(f, len(self.talk) - 1)])
        art = Image.new("RGB", (W * SS, H * SS), PAPER)
        pen = Pen(art, int(t * 8))
        draw_scene(pen, sc, ts, talk, t)
        zi = sc.get("zoom", 0)
        z0, z1 = ((1.0, 1.04), (1.04, 1.0))[zi % 2]
        z = z0 + (z1 - z0) * ts / sc["dur"]
        cw, ch = W / z, H / z
        l, tp = W / 2 - cw / 2, min(max(700 - ch / 2, 0), H - ch)
        img = art.crop((int(l * SS), int(tp * SS), int((l + cw) * SS), int((tp + ch) * SS))).resize((W, H), Image.LANCZOS)
        headline(img, sc["head"], ts, first=(sc is self.scenes[0]))
        watermark(img)
        arr = np.asarray(img).astype(np.float32) + grain()
        return np.clip(arr, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", default=os.path.join(ROOT, "content.json"))
    ap.add_argument("--id")
    ap.add_argument("--day", type=int)
    ap.add_argument("--out", default="out/video.mp4")
    ap.add_argument("--frames", default="")
    ap.add_argument("--no-voice", action="store_true")
    a = ap.parse_args()
    contents = load_contents(a.content)
    c = pick(contents, a)
    print(f"Konten: {c['id']} - {c['yt_title']}", flush=True)
    outdir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(outdir, exist_ok=True)
    work = os.path.join(outdir, "work")
    pool = [c]
    if voice_source() == "rekaman" and not a.id:
        have = recorded_ids()
        pool += [x for x in contents if x["id"] in have and x["id"] != c["id"]]
    for k, cand in enumerate(pool):
        try:
            scenes, total, track, engines = plan(cand, work, use_voice=not a.no_voice)
            c = cand
            break
        except RuntimeError as e:
            if k == len(pool) - 1:
                raise
            print(f"::warning::{cand['id']}: {e} -> mencoba konten berekaman berikutnya", flush=True)
    print(f"Durasi {total:.1f}s | mesin suara: {sorted(engines) or 'tanpa suara'}", flush=True)
    for i, s in enumerate(scenes):
        s["zoom"] = i
    film = Film(scenes, total, talk_curve(track, total))
    if a.frames:
        os.makedirs("test", exist_ok=True)
        for t in [float(x) for x in a.frames.split(",")]:
            Image.fromarray(film.frame(t)).save(f"test/{c['id']}_{t:05.2f}.png")
        return
    wav = os.path.join(work, "mix.wav")
    mood = int(c["id"][1:]) % 4 if c["id"][1:].isdigit() else 0
    build_audio(wav, scenes, total, track, mood)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
           "-preset", "medium", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k",
           "-shortest", "-movflags", "+faststart", a.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(total * FPS)
    for i in range(nf):
        p.stdin.write(film.frame(i / FPS).tobytes())
        if i % 96 == 0:
            print(f"frame {i}/{nf}", flush=True)
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg gagal")
    with open(os.path.join(outdir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(dict(id=c["id"], duration=round(total, 1), voice=sorted(engines)), f)
    print("selesai", a.out, flush=True)


if __name__ == "__main__":
    main()
