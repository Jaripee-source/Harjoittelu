"""Procedural crocodile skin wrap for Tesla Model Y Premium (2025+) template.

Usage: python3 -I make_skin.py <template.png> <out.png>
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd
from scipy.spatial import cKDTree

rng = np.random.default_rng(7)
W = H = 1024
CX = 511.5

tpl = np.array(Image.open(sys.argv[1]).convert("RGBA"))
a = tpl[..., 3]
lum = tpl[..., :3].mean(-1)
lab, n = nd.label((a > 200) & (lum > 200))
# include outline pixels: assign them to nearest panel so panels are fully painted
paint = a > 10
_, (iy, ix) = nd.distance_transform_edt(lab == 0, return_indices=True)
lab_full = np.where(paint, lab[iy, ix], 0)

HEAD = {1, 2, 3, 4, 9, 10}
SIDE = {6, 8, 11, 12, 13, 14, 18, 19}
RIDGE = {5, 7, 15, 16}
TAIL = {17, 20}

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
uu = np.abs(xx - CX)


def fbm(octaves, base, seed, size=W):
    r = np.random.default_rng(seed)
    out = np.zeros((size, size), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        g = max(2, int(base * 2 ** o))
        a_ = r.random((g, g)).astype(np.float32)
        im = Image.fromarray(a_, mode="F").resize((size, size), Image.BICUBIC)
        out += amp * np.array(im)
        tot += amp
        amp *= 0.5
    return out / tot


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- points
pts, spc, keel, kind = [], [], [], []


def add(px, py, s, k, kd):
    pts.append((px, py)); spc.append(s); keel.append(k); kind.append(kd)


panel_points = {}
for pid in range(1, n + 1):
    m = lab_full == pid
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    start = len(pts)
    dil = nd.binary_dilation(m, iterations=12)
    if pid in HEAD:
        s = 12.0 if pid != 2 else 12.5
        for gy in np.arange(y0 - 14, y1 + 14, s):
            for gx in np.arange(x0 - 14, x1 + 14, s):
                px = gx + (rng.random() - .5) * s * .9
                py = gy + (rng.random() - .5) * s * .9
                add(px, py, s, False, 0)
    elif pid in SIDE:
        u = uu[m]
        umin, umax = u.min(), u.max()
        sgn = -1 if xs.mean() < CX else 1
        uc, col = umin - 12, 0
        while uc < umax + 12:
            t = np.clip((uc - umin) / (umax - umin), 0, 1)
            su = 25 - 10 * t
            sv = 31 - 14 * t
            off = (col % 2) * sv * .5
            for gy in np.arange(y0 - 16 + off, y1 + 16, sv):
                px = CX + sgn * (uc + (rng.random() - .5) * su * .4)
                py = gy + (rng.random() - .5) * sv * .4
                add(px, py, min(su, sv), t < 0.38, 1)
            uc += su
            col += 1
    elif pid in RIDGE:
        su, sv = 15.0, 22.0
        for gx in np.arange(x0 - 10, x1 + 10, su):
            col = int((gx - x0) / su)
            for gy in np.arange(y0 - 12 + (col % 2) * sv / 2, y1 + 12, sv):
                add(gx + (rng.random() - .5) * 3, gy + (rng.random() - .5) * 4, su, True, 2)
    else:  # TAIL
        su, sv = 27.0, 19.0
        for gy in np.arange(y0 - 10, y1 + 10, sv):
            row = int((gy - y0) / sv)
            for gx in np.arange(x0 - 14 + (row % 2) * su / 2, x1 + 14, su):
                add(gx + (rng.random() - .5) * 4, gy + (rng.random() - .5) * 3, sv, True, 3)
    # keep points near the panel
    sel = []
    for i in range(start, len(pts)):
        px, py = int(round(pts[i][0])), int(round(pts[i][1]))
        if 0 <= px < W and 0 <= py < H and dil[py, px]:
            sel.append(i)
    panel_points[pid] = np.array(sel)

pts = np.array(pts, np.float32)
spc = np.array(spc, np.float32)
keel = np.array(keel)
kind = np.array(kind)
cell_rand = rng.random(len(pts)).astype(np.float32)
cell_rand2 = rng.random(len(pts)).astype(np.float32)

# ---------------------------------------------------------------- voronoi
WX = (fbm(3, 12, 41) - .5) * 20
WY = (fbm(3, 12, 42) - .5) * 20
cell = np.full((H, W), -1, np.int64)
edge = np.zeros((H, W), np.float32)
for pid, idx in panel_points.items():
    m = lab_full == pid
    q = np.stack([xx[m] + WX[m], yy[m] + WY[m]], -1)
    tree = cKDTree(pts[idx])
    d, j = tree.query(q, k=2)
    cell[m] = idx[j[:, 0]]
    edge[m] = (d[:, 1] - d[:, 0])

valid = cell >= 0
ci = np.where(valid, cell, 0)
S = spc[ci]
cx_, cy_ = pts[ci, 0], pts[ci, 1]
dome = np.clip(edge / (0.55 * S), 0, 1)
plateau = smooth(0.0, 0.3, dome)
h = (0.45 * plateau + 0.55 * np.sqrt(dome)) * 0.13 * S
h *= 0.85 + 0.3 * cell_rand2[ci]
# keels (bony ridges along car length)
kmask = keel[ci]
ridge = np.exp(-((xx - cx_) / (0.15 * S)) ** 2) * np.clip(1 - ((yy - cy_) / (0.75 * S)) ** 2, 0, 1)
h += np.where(kmask, 0.32 * S * ridge * dome ** .5, 0)
# skin pores & micro bumps
pores = fbm(3, 180, 11)
micro = fbm(4, 40, 12)
wrink = fbm(3, 90, 13)
h += (pores - .5) * 1.6 * plateau + (micro - .5) * 2.4 + (wrink - .5) * 1.2 * (1 - plateau)

# per-pixel vertical coordinate t on sides (0 = beltline, 1 = rocker)
tmap = np.zeros((H, W), np.float32)
for pid in SIDE | {3, 4, 1}:
    m = lab_full == pid
    for y in range(H):
        row = m[y]
        if row.any():
            u = uu[y, row]
            lo, hi = u.min(), u.max()
            tmap[y, row] = (u - lo) / max(hi - lo, 1)

# ---------------------------------------------------------------- albedo
C = lambda *c: np.array(c, np.float32) / 255
crev = C(6, 20, 10)
greens = [C(20, 74, 38), C(23, 82, 41), C(27, 90, 44), C(32, 98, 47)]
yellow = C(226, 186, 34)
belly = C(200, 186, 92)

g_idx = (cell_rand * 3.999).astype(int)
gstack = np.stack(greens)
cellcol = gstack[g_idx[ci]]
# subtle hue drift (teal <-> olive) over the body
drift = fbm(2, 3, 21)[..., None]
cellcol = cellcol * (0.88 + 0.24 * np.concatenate([drift, np.ones_like(drift) * .6, 1 - drift], -1))
# large soft mottling + dark crocodile crossbands
mott = fbm(4, 6, 22)[..., None]
cellcol *= 0.78 + 0.45 * mott
bandn = fbm(2, 5, 23)

lid = lab_full
is_side = np.isin(lid, list(SIDE))
is_head = np.isin(lid, list(HEAD))
is_tail = np.isin(lid, list(TAIL))
is_ridge = np.isin(lid, list(RIDGE))

blob = fbm(3, 7, 31)
cell_blob = blob[np.clip(cy_.astype(int), 0, H - 1), np.clip(cx_.astype(int), 0, W - 1)]
cell_t = tmap[np.clip(cy_.astype(int), 0, H - 1), np.clip(cx_.astype(int), 0, W - 1)]

ymix = np.zeros((H, W), np.float32)
cyi = np.clip(cy_.astype(int), 0, H - 1); cxi = np.clip(cx_.astype(int), 0, W - 1)
# crossband phase along the car length (bands are perpendicular to the body axis)
phase = np.sin(cy_ / 46.0 + bandn[cyi, cxi] * 5.0)
# 1) lower flanks fade into golden belly scales, mottled cell by cell
p_low = smooth(0.55, 1.0, cell_t + (cell_blob - .5) * .3)
ymix = np.where(is_side & (cell_rand2[ci] < p_low), 0.35 + 0.35 * cell_rand[ci], ymix)
# 2) yellow scales picking out the crossband edges on mid/upper flanks
yb = (np.abs(phase - 0.55) < 0.22) & (cell_rand2[ci] > 0.45)
ymix = np.where((is_side | is_tail) & yb & (cell_t < .8), np.maximum(ymix, 0.55 + 0.3 * cell_rand[ci]), ymix)
# 3) sparse yellow speckles on head / ridges / tail
ymix = np.where((is_head | is_ridge | is_tail) & (cell_rand2[ci] > 0.972), 0.5, ymix)
# dark crossbands
darkband = np.where((is_side | is_tail | is_ridge), 1 - 0.38 * smooth(-0.1, -0.7, phase), 1.0)

inner = fbm(3, 60, 24)[..., None]
cellcol = cellcol * (0.85 + 0.3 * inner) * (0.85 + 0.25 * np.sqrt(dome))[..., None]
cellcol = cellcol * smooth(0, .1, dome)[..., None] + crev * (1 - smooth(0, .1, dome))[..., None]
ymix = ymix * (0.7 + 0.5 * inner[..., 0])
base = cellcol * (1 - ymix[..., None]) + (yellow * 0.75 + belly * .25) * ymix[..., None]
# ridges & upper back darker for depth
dark = np.where(is_ridge, 0.72, 1.0) * np.where(is_side, 0.85 + 0.15 * smooth(0, .4, tmap), 1.0)
base *= (dark * np.where(ymix > 0, 1.0, darkband))[..., None]

# ---------------------------------------------------------------- crocodile head features
override = np.zeros((H, W, 3), np.float32)   # direct colour (already shaded)
ov_a = np.zeros((H, W), np.float32)


def polyline_dist(points, step=1.0):
    p = np.array(points, np.float32)
    # Catmull-Rom smoothing
    dense = []
    P = np.vstack([p[0], p, p[-1]])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, 30, endpoint=False):
            t2, t3 = t * t, t * t * t
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense.append(p[-1])
    dense = np.array(dense)
    tree = cKDTree(dense)
    d, j = tree.query(np.stack([xx.ravel(), yy.ravel()], -1))
    return d.reshape(H, W), j.reshape(H, W), dense


def mirror(points):
    return [(1023 - x, y) for x, y in points]


# Smile: across the front bumper and back along both front fenders, ending under the eyes
bump_mouth = [(262, 86), (300, 72), (360, 60), (430, 53), (512, 50), (594, 53), (664, 60), (724, 72), (762, 86)]
fend_mouth = [(292, 168), (277, 208), (266, 245), (262, 272), (266, 292), (276, 301), (284, 292)]
mouth_lines = [bump_mouth, fend_mouth, mirror(fend_mouth)]
# "down" direction (towards ground) for each line in template space
downs = [np.array([0, -1.0]), np.array([-1.0, 0]), np.array([1.0, 0])]
panels_for = [{1}, {3}, {4}]

jaw = np.zeros((H, W), np.float32)
for line, dn, pset in zip(mouth_lines, downs, panels_for):
    d, j, dense = polyline_dist(line)
    pm = np.isin(lid, list(pset))
    groove = smooth(5.5, 3.0, d)
    lip = np.exp(-((d - 8) / 3.5) ** 2)
    h += np.where(pm, -6.0 * groove + 3.0 * lip, 0)
    base = np.where((pm & (groove > 0))[..., None], base * (1 - groove[..., None]) + C(40, 8, 10) * groove[..., None], base)
    # which side is the lower jaw: sign of (p - closest) . down
    cl = dense[j]
    side = (xx - cl[..., 0]) * dn[0] + (yy - cl[..., 1]) * dn[1]
    lower = pm & (side > 0)
    jaw = np.maximum(jaw, np.where(lower, smooth(0, 6, d) * (1 - smooth(18, 40, d)) * 0.6, 0))
    # teeth: rounded nubs hanging from the upper jaw
    arclen = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))])
    total = arclen[-1]
    spacing = 30.0
    for s_ in np.arange(spacing * .6, total - spacing * (1.6 if pset != {1} else .6), spacing):
        k = np.searchsorted(arclen, s_)
        c = dense[k] + dn * 2.0
        tan = dense[min(k + 1, len(dense) - 1)] - dense[max(k - 1, 0)]
        tan /= np.linalg.norm(tan) + 1e-6
        rx = (xx - c[0]) * tan[0] + (yy - c[1]) * tan[1]
        ry = (xx - c[0]) * dn[0] + (yy - c[1]) * dn[1]
        e = (rx / 6.0) ** 2 + (np.maximum(ry, 0) / 11.0) ** 2 + (np.minimum(ry, 0) / 3.5) ** 2
        tooth = np.clip(1 - e, 0, 1)
        tm = (tooth > 0) & pm
        h += np.where(tm, np.sqrt(tooth) * 6.0, 0)
        tw = smooth(0, .15, tooth)[..., None]
        base = np.where(tm[..., None], base * (1 - tw) + C(250, 244, 222) * tw, base)

# lower jaw: paler yellow-green, like a real croc's jaw, plus a cheerful yellow cheek
base = base * (1 - jaw[..., None]) + (belly * .8 + C(120, 150, 60) * .2) * jaw[..., None]

# snout: lighter central band on hood, nostrils at the front
hood = lid == 2
snout = np.exp(-((xx - CX) / 70) ** 2) * smooth(330, 140, yy)
base *= np.where(hood, 1 + 0.18 * snout, 1)[..., None]
for nxc in (CX - 26, CX + 26):
    r = np.hypot((xx - nxc) / 20, (yy - 148) / 16)
    bump = np.clip(1 - r ** 2, 0, 1)
    h += np.where(hood, bump * 8, 0)
    hole = np.hypot((xx - nxc - np.sign(nxc - CX) * 3) / 9, (yy - 144) / 5)
    hm = hood & (hole < 1)
    h += np.where(hm, -(1 - hole ** 2) * 6, 0)
    base = np.where(hm[..., None], C(8, 14, 8), base)

for k_, (sx_, ex_) in enumerate([(CX - 40, CX - 22), (CX + 40, CX + 22)]):
    d_, _, _ = polyline_dist([(sx_ + (-14 if k_ == 0 else 14), 222), (sx_, 195), ((sx_ + ex_) / 2, 170)])
    h += np.where(hood, np.exp(-(d_ / 5) ** 2) * 4, 0)
    base *= np.where(hood, 1 + 0.12 * np.exp(-(d_ / 6) ** 2), 1)[..., None]
# brow ridges behind each eye (bumpy ridge of scutes)
EYES = [(CX - 66, 258), (CX + 66, 258)]
R = 35.0
for ex, ey in EYES:
    r = np.hypot(xx - ex, yy - ey)
    ring = np.exp(-((r - R - 8) / 8) ** 2)
    h += np.where(hood, ring * 10, 0)
    base = np.where((hood & (r < R + 14))[..., None], base * 1.05 + C(30, 30, 0) * ring[..., None], base)

# ---------------------------------------------------------------- lighting
gx = nd.sobel(nd.gaussian_filter(h, .7), axis=1) / 8
gy = nd.sobel(nd.gaussian_filter(h, .7), axis=0) / 8
N = np.stack([-gx, -gy, np.ones_like(h)], -1)
N /= np.linalg.norm(N, axis=-1, keepdims=True)
L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
V = np.array([0, 0, 1.0])
Hh = (L + V); Hh /= np.linalg.norm(Hh)
diff = np.clip(N @ L, 0, 1)
spec = np.clip(N @ Hh, 0, 1) ** 28
spec2 = np.clip(N @ Hh, 0, 1) ** 8
ao = 0.55 + 0.45 * smooth(0, 0.2, dome)
ao = np.where(np.isin(lid, list(TAIL | SIDE | RIDGE | HEAD)), ao, 1)
shade = (0.38 + 0.8 * diff) * ao
gloss = 0.6 + 0.8 * fbm(3, 8, 51)
col = base * shade[..., None] + (gloss * (0.18 * spec + 0.04 * spec2))[..., None] * C(235, 250, 220)

# ---------------------------------------------------------------- eyes (rendered directly)
for k, (ex, ey) in enumerate(EYES):
    dx, dy = (xx - ex) / R, (yy - ey) / R
    rr = np.sqrt(dx * dx + dy * dy)
    m = (rr < 1) & hood
    nz = np.sqrt(np.clip(1 - rr * rr, 0, 1))
    # pupil/iris look forward (towards the car's nose) and slightly outward
    lx, ly = dx - (-0.10 if k == 0 else 0.10), dy + 0.22
    ir = np.sqrt(lx * lx + ly * ly)
    ang = np.arctan2(ly, lx)
    streak = 0.85 + 0.15 * np.sin(ang * 23 + np.sin(ang * 7) * 2)
    iris = (C(250, 214, 60) * (1 - smooth(0.15, 0.68, ir))[..., None] + C(178, 150, 30) * smooth(0.15, 0.68, ir)[..., None])
    iris *= streak[..., None]
    eye = np.where((ir < 0.68)[..., None], iris, C(236, 232, 210))
    limbal = np.exp(-((ir - 0.68) / 0.05) ** 2)
    eye *= (1 - 0.6 * limbal)[..., None]
    pupil = ir < 0.40
    eye = np.where(pupil[..., None], C(6, 8, 6), eye)
    # sphere shading + upper lid shadow on the back side
    sh = 0.55 + 0.45 * np.clip(-0.45 * dx - 0.55 * dy + 0.7 * nz, 0, 1) / 1.0
    lidshadow = 1 - 0.45 * smooth(0.35, 1.0, dy)
    eye *= (sh * lidshadow)[..., None]
    # catch-lights: friendly sparkle
    hl1 = np.hypot((dx + 0.30) / 0.22, (dy + 0.32) / 0.16) < 1
    hl2 = np.hypot((dx - 0.22) / 0.09, (dy - 0.05) / 0.09) < 1
    eye = np.where((hl1 | hl2)[..., None], C(255, 255, 255), eye)
    # dark edge where eyeball meets lid
    eye *= (1 - 0.7 * smooth(0.86, 1.0, rr))[..., None]
    col = np.where(m[..., None], eye, col)

# ---------------------------------------------------------------- output
col = np.clip(col, 0, 1)
out = np.zeros((H, W, 4), np.uint8)
out[..., :3] = (col * 255 + .5).astype(np.uint8)
out[..., 3] = np.where(paint, 255, 0).astype(np.uint8)
out[~paint, :3] = 0
img = Image.fromarray(out, "RGBA")
img.save(sys.argv[2], optimize=True)
# palette-quantise to keep the file under Tesla's 1 MB limit
q = img.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
pal = q.getpalette()[:255 * 3] + [0, 0, 0]
qa = np.array(q, np.uint8)
qa[~paint] = 255
qi = Image.fromarray(qa, "P")
qi.putpalette(pal)
qi.info["transparency"] = 255
qi.save(sys.argv[2].replace(".png", "_pieni.png"), optimize=True, transparency=255)
import os
print("saved", sys.argv[2], os.path.getsize(sys.argv[2]), "bytes")
