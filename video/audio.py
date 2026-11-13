"""Génère la bande-son (musique + bruitages synthétisés) calée sur video.html.
Usage : python3 audio.py sortie.wav   (nécessite numpy)"""
import sys, wave
import numpy as np

SR, DUR, BEAT = 44100, 45.0, 0.5          # 120 BPM
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - max(0, pan)); R[i:i + len(sig)] += sig * (1 + min(0, pan))

def tt(d): return np.arange(int(d * SR)) / SR
def env(d, a=0.005, k=6.0):
    t = tt(d); return np.minimum(t / a, 1) * np.exp(-k * t / d)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, a):                                # passe-bas un pôle
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y

# --- instruments ---
def kick():
    t = tt(.32); f = 45 + 110 * np.exp(-t * 32)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
def clap():
    return np.diff(rng.standard_normal(int(.18 * SR) + 1)) * env(.18, .001, 7) * .5
def hat(d=.05):
    return np.diff(np.diff(rng.standard_normal(int(d * SR) + 2))) * env(d, .001, 5) * .12
def bass(m, d):
    t = tt(d); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t)) * env(d, .008, 3)
def pluck(m, d=.3):
    t = tt(d); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(4 * np.pi * f * t) + .15 * np.sin(6 * np.pi * f * t)) * env(d, .003, 7)
def pad(notes, d):
    t = tt(d); s = sum(np.sin(2 * np.pi * hz(m) * t * (1 + dt)) for m in notes for dt in (-.003, .003))
    return s / len(notes) * np.minimum(t / .4, 1) * np.minimum((d - t) / .5, 1)
def bell(m, d=1.2):
    t = tt(d); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)) * np.exp(-t * 4)
def pop(m=84):
    t = tt(.09); f = hz(m) * (1 + .6 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.09, .002, 6)
def whoosh(d=.7):
    n = lp(rng.standard_normal(int(d * SR)), .25); t = tt(d)
    return n * np.sin(np.pi * t / d) ** 2
def thud():
    t = tt(.2); return np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 40)) * t) * np.exp(-t * 20)
def crash(d=2.5):
    return np.diff(rng.standard_normal(int(d * SR) + 1)) * np.exp(-tt(d) * 2.2) * .25
def riser(d, m0, m1):
    t = tt(d); f = hz(m0) * (hz(m1) / hz(m0)) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2

# --- musique : Am – F – C – G, une mesure (2 s) par accord ---
CH = [(57, [57, 60, 64, 69]), (53, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (55, [55, 59, 62, 67])]
END = 41.5                                   # écran de fin : accord tenu
bar = 0; t0 = 0.5
while t0 < END - .01:
    root, notes = CH[bar % 4]; d = min(2.0, END - t0)
    add(pad([n + 12 for n in notes[:3]], d), t0, .09)
    for s in range(int(round(d / .25))):     # doubles croches
        t = t0 + s * .25
        if t >= 4.5:                         # la rythmique entre avec la scène 2
            if s % 2 == 0: add(kick(), t, .8)
            if s % 4 == 2: add(clap(), t, .5)
            if s % 2 == 1: add(hat(), t, .9, .3)
            add(bass(root - 12 + (12 if s % 4 == 3 else 0), .24), t, .32)
        if t >= 2.5:
            n = notes[[0, 2, 1, 3, 2, 3, 1, 2][s % 8]] + 12
            add(pluck(n), t, .11 if t < 10.5 else .15, -.4 if s % 2 else .4)
    t0 += 2.0; bar += 1
add(pad([60, 64, 67, 72, 76], 3.5), END, .22)        # accord final (Do majeur)
add(bass(36, 3.0), END, .4); add(kick(), END, .9); add(crash(), END, .8)
for i, m in enumerate([72, 76, 79, 84]): add(bell(m, 2.0), END + .6 + i * .12, .16)

# --- bruitages calés sur l'animation ---
for t, g in [(.86, .9), (1.4, .55), (1.63, .3)]: add(thud(), t, g)            # rebonds du ballon
for t in [4.5, 10.5, 18, 23.5, 31, 36.5, 41.5]: add(whoosh(), t - .45, .5)     # transitions
for t in [6.8, 7.3, 7.9]: add(pop(79), t, .35)                                 # saisie du score
for i, m in enumerate([79, 84, 88]): add(bell(m, .9), 8.6 + i * .07, .2)       # prono validé
for t, m in [(11.6, 88), (13.2, 84), (14.8, 76)]: add(bell(m, 1.0), t + .1, .22)  # cartes du barème
add(thud(), 19.4, 1.0); add(crash(1.5), 19.4, .5); add(bell(84), 19.45, .2)    # ×2
add(riser(4.6, 60, 84), 25.0, .05)                                             # course au classement
for i in range(8): add(pop(76 + [0, 2, 4, 7, 9, 12, 14, 16][i]), 32.1 + i * .2, .3, (i % 4 - 1.5) / 3)  # onglets
for t, m in [(37.3, 72), (37.6, 76), (37.9, 79)]: add(riser(.8, m - 12, m), t, .08)                     # podium
for t, m in [(38.0, 79), (38.3, 84), (38.6, 88)]: add(bell(m, 1.0), t, .2)

# --- mixage ---
mix = np.stack([L, R], 1)
f = np.ones(N); k = int(1.2 * SR); f[-k:] = np.linspace(1, 0, k) ** 1.5; f[: int(.02 * SR)] = np.linspace(0, 1, int(.02 * SR))
mix = np.tanh(mix * 1.1) * f[:, None]
mix = mix / np.abs(mix).max() * .89
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "mondial2026.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
