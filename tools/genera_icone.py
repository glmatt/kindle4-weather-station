# -*- coding: utf-8 -*-
# genera_icone.py - weather icon generator
# Runs on a desktop with Python 3 + Pillow, not on the Kindle.
#
# Copyright (C) 2026  Gianluca Matteucci
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Genera le icone meteo per la centralina Kindle.

Metodo: ogni forma viene disegnata PIENA su una maschera, poi il
contorno si ricava per erosione. Cosi' l'unione di piu' cerchi
produce una sagoma sola, senza linee interne da ripulire a mano.

Tutto a 4x e poi ridotto: su e-ink i bordi curvi devono essere
netti, e il sovracampionamento e' l'unico modo per ottenerli.
"""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

LATO = 130           # dimensione finale, in pixel
MARGINE = 2          # bordo bianco lasciato attorno al disegno
SS = 4               # sovracampionamento
L = LATO * SS
TRATTO = 5 * SS      # spessore del contorno
OUT = "/home/claude/icone"

NERO, BIANCO = 0, 255
C = L // 2


# ---------------------------------------------------------------
# infrastruttura
# ---------------------------------------------------------------

def tela():
    img = Image.new("L", (L, L), BIANCO)
    return img, ImageDraw.Draw(img)


def contorna(piena, spessore=TRATTO):
    """Da una sagoma piena ricava il suo contorno."""
    k = spessore if spessore % 2 else spessore + 1
    erosa = piena.filter(ImageFilter.MaxFilter(min(k, 25)))
    bordo = ImageChops.subtract(erosa, piena)
    return ImageChops.invert(bordo)


def fondi(base, strato):
    """Sovrappone un disegno nero su bianco a un altro."""
    return ImageChops.darker(base, strato)


def salva(img, nome):
    """Ritaglia al contenuto, riscala e centra nel riquadro finale.

    Serve a dare a tutte le icone la stessa estensione visiva: senza
    questo passaggio un sole tondo e una nuvola con la pioggia hanno
    margini interni diversi e sembrano di dimensioni diverse.
    Le proporzioni restano quelle originali, cosi' niente si deforma.
    """
    bbox = ImageChops.invert(img).getbbox()
    if bbox:
        img = img.crop(bbox)

    utile = LATO - 2 * MARGINE
    w, h = img.size
    scala = float(utile) / max(w, h)
    nw, nh = max(1, int(round(w * scala))), max(1, int(round(h * scala)))
    img = img.resize((nw, nh), Image.LANCZOS)

    tela_fin = Image.new("L", (LATO, LATO), BIANCO)
    tela_fin.paste(img, ((LATO - nw) // 2, (LATO - nh) // 2))
    tela_fin.convert("L").save(os.path.join(OUT, nome + ".png"))


# ---------------------------------------------------------------
# elementi
# ---------------------------------------------------------------

def sagoma_nuvola(cx, cy, w):
    """Nuvola come unione di tre gobbe su una base."""
    m = Image.new("L", (L, L), BIANCO)
    d = ImageDraw.Draw(m)
    for dx, dy, rr in ((-0.34, 0.02, 0.30), (-0.02, -0.16, 0.38),
                       (0.34, 0.06, 0.26)):
        x, y, r = cx + w * dx, cy + w * dy, w * rr
        d.ellipse([x - r, y - r, x + r, y + r], fill=NERO)
    d.rounded_rectangle(
        [cx - w * 0.54, cy + w * 0.02, cx + w * 0.54, cy + w * 0.34],
        radius=w * 0.16, fill=NERO)
    return m


def nuvola(img, cx, cy, w):
    return fondi(img, contorna(sagoma_nuvola(cx, cy, w)))


def sole(img, cx, cy, r, raggi=True):
    m = Image.new("L", (L, L), BIANCO)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NERO)
    out = fondi(img, contorna(m))
    if raggi:
        d2 = ImageDraw.Draw(out)
        for i in range(8):
            a = math.radians(i * 45 + 22)
            d2.line([cx + math.cos(a) * (r + 8 * SS),
                     cy + math.sin(a) * (r + 8 * SS),
                     cx + math.cos(a) * (r + 20 * SS),
                     cy + math.sin(a) * (r + 20 * SS)],
                    fill=NERO, width=TRATTO)
    return out


def luna(img, cx, cy, r):
    m = Image.new("L", (L, L), BIANCO)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NERO)
    d.ellipse([cx - r + r * 0.58, cy - r - r * 0.22,
               cx + r + r * 0.58, cy + r - r * 0.22], fill=BIANCO)
    return fondi(img, contorna(m))


def gocce(img, cx, y, n, passo=None, lung=20 * SS):
    d = ImageDraw.Draw(img)
    passo = passo or int(L * 0.15)
    x0 = cx - passo * (n - 1) / 2.0
    for i in range(n):
        x = x0 + i * passo
        d.line([x + lung * 0.28, y, x - lung * 0.20, y + lung],
               fill=NERO, width=TRATTO)
    return img


def fiocchi(img, cx, y, n, passo=None, r=8 * SS):
    d = ImageDraw.Draw(img)
    passo = passo or int(L * 0.17)
    x0 = cx - passo * (n - 1) / 2.0
    for i in range(n):
        x, yy = x0 + i * passo, y + (7 * SS if i % 2 else 0)
        for a in (0, 60, 120):
            rad = math.radians(a)
            d.line([x - math.cos(rad) * r, yy - math.sin(rad) * r,
                    x + math.cos(rad) * r, yy + math.sin(rad) * r],
                   fill=NERO, width=int(TRATTO * 0.8))
    return img


def pallini(img, cx, y, n, passo=None, r=5 * SS):
    d = ImageDraw.Draw(img)
    passo = passo or int(L * 0.14)
    x0 = cx - passo * (n - 1) / 2.0
    for i in range(n):
        x, yy = x0 + i * passo, y + (7 * SS if i % 2 else 0)
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=NERO)
    return img


def cristallo(img, cx, y, r=10 * SS):
    """Marchio del gelo: un asterisco a sei punte."""
    d = ImageDraw.Draw(img)
    for a in (0, 60, 120):
        rad = math.radians(a)
        d.line([cx - math.cos(rad) * r, y - math.sin(rad) * r,
                cx + math.cos(rad) * r, y + math.sin(rad) * r],
               fill=NERO, width=int(TRATTO * 0.8))
    return img


def fulmine(img, cx, y, s=14 * SS):
    d = ImageDraw.Draw(img)
    d.polygon([(cx + s * 0.28, y), (cx - s * 0.58, y + s * 1.2),
               (cx + s * 0.02, y + s * 1.2), (cx - s * 0.34, y + s * 2.4),
               (cx + s * 0.78, y + s * 1.0), (cx + s * 0.06, y + s * 1.0)],
              fill=NERO)
    return img


def righe_nebbia(img, y0, n=3):
    d = ImageDraw.Draw(img)
    for i in range(n):
        marg = int(L * (0.16 if i % 2 == 0 else 0.26))
        d.line([marg, y0 + i * 11 * SS, L - marg, y0 + i * 11 * SS],
               fill=NERO, width=TRATTO)
    return img


# ---------------------------------------------------------------
# le icone
# ---------------------------------------------------------------

def disegna(nome):
    img, _ = tela()
    w = L * 0.46                       # larghezza nuvola standard
    cy_n = L * 0.36                    # centro nuvola quando c'e' roba sotto

    if nome == "sereno":
        img = sole(img, C, C, L * 0.20)

    elif nome == "sereno_notte":
        img = luna(img, C, C, L * 0.28)

    elif nome == "poco_nuvoloso":
        img = sole(img, L * 0.34, L * 0.32, L * 0.16)
        img = nuvola(img, L * 0.56, L * 0.62, L * 0.40)

    elif nome == "poco_nuvoloso_notte":
        img = luna(img, L * 0.34, L * 0.31, L * 0.19)
        img = nuvola(img, L * 0.56, L * 0.62, L * 0.40)

    elif nome == "parz_nuvoloso":
        img = sole(img, L * 0.28, L * 0.28, L * 0.13)
        img = nuvola(img, L * 0.54, L * 0.56, L * 0.50)

    elif nome == "parz_nuvoloso_notte":
        img = luna(img, L * 0.28, L * 0.27, L * 0.16)
        img = nuvola(img, L * 0.54, L * 0.56, L * 0.50)

    elif nome == "coperto":
        img = nuvola(img, L * 0.56, L * 0.56, L * 0.46)
        img = nuvola(img, L * 0.40, L * 0.38, L * 0.34)

    elif nome == "nebbia":
        img = nuvola(img, C, L * 0.34, w)
        img = righe_nebbia(img, int(L * 0.66))

    elif nome == "nebbia_gelata":
        img = nuvola(img, C, L * 0.32, w)
        img = righe_nebbia(img, int(L * 0.62), 2)
        img = cristallo(img, C, int(L * 0.88))

    elif nome == "pioviggine":
        img = nuvola(img, C, cy_n, w)
        img = gocce(img, C, int(L * 0.66), 2, lung=13 * SS)

    elif nome == "pioviggine_intensa":
        img = nuvola(img, C, cy_n, w)
        img = gocce(img, C, int(L * 0.64), 4, passo=int(L * 0.12),
                    lung=13 * SS)

    elif nome == "pioviggine_gelata":
        img = nuvola(img, C, L * 0.32, w)
        img = gocce(img, C, int(L * 0.60), 2, lung=12 * SS)
        img = cristallo(img, C, int(L * 0.88))

    elif nome == "pioggia_debole":
        img = nuvola(img, C, cy_n, w)
        img = gocce(img, C, int(L * 0.64), 2)

    elif nome == "pioggia":
        img = nuvola(img, C, cy_n, w)
        img = gocce(img, C, int(L * 0.64), 3)

    elif nome == "pioggia_forte":
        img = nuvola(img, C, L * 0.32, w)
        img = gocce(img, C, int(L * 0.58), 3)
        img = gocce(img, C, int(L * 0.76), 2, passo=int(L * 0.18))

    elif nome == "pioggia_gelata":
        img = nuvola(img, C, L * 0.32, w)
        img = gocce(img, C, int(L * 0.60), 3)
        img = cristallo(img, C, int(L * 0.90))

    elif nome == "neve_debole":
        img = nuvola(img, C, cy_n, w)
        img = fiocchi(img, C, int(L * 0.72), 2)

    elif nome == "neve":
        img = nuvola(img, C, cy_n, w)
        img = fiocchi(img, C, int(L * 0.72), 3)

    elif nome == "neve_forte":
        img = nuvola(img, C, L * 0.32, w)
        img = fiocchi(img, C, int(L * 0.64), 3)
        img = fiocchi(img, C, int(L * 0.84), 2, passo=int(L * 0.20))

    elif nome == "nevischio":
        img = nuvola(img, C, cy_n, w)
        img = pallini(img, C, int(L * 0.70), 4)

    elif nome == "rovesci":
        img = sole(img, L * 0.28, L * 0.24, L * 0.12)
        img = nuvola(img, L * 0.54, L * 0.44, L * 0.44)
        img = gocce(img, int(L * 0.54), int(L * 0.74), 3)

    elif nome == "rovesci_forti":
        img = sole(img, L * 0.28, L * 0.22, L * 0.12)
        img = nuvola(img, L * 0.54, L * 0.42, L * 0.44)
        img = gocce(img, int(L * 0.54), int(L * 0.68), 3)
        img = gocce(img, int(L * 0.54), int(L * 0.84), 2, passo=int(L * 0.18))

    elif nome == "rovesci_neve":
        img = sole(img, L * 0.28, L * 0.24, L * 0.12)
        img = nuvola(img, L * 0.54, L * 0.44, L * 0.44)
        img = fiocchi(img, int(L * 0.54), int(L * 0.78), 3)

    elif nome == "temporale":
        img = nuvola(img, C, L * 0.34, w)
        img = fulmine(img, C, int(L * 0.58))

    elif nome == "temporale_forte":
        img = nuvola(img, C, L * 0.32, w)
        img = fulmine(img, int(L * 0.40), int(L * 0.56))
        img = gocce(img, int(L * 0.68), int(L * 0.62), 2,
                    passo=int(L * 0.13))

    else:
        raise ValueError(nome)

    return img


NOMI = [
    "sereno", "sereno_notte",
    "poco_nuvoloso", "poco_nuvoloso_notte",
    "parz_nuvoloso", "parz_nuvoloso_notte",
    "coperto",
    "nebbia", "nebbia_gelata",
    "pioviggine", "pioviggine_intensa", "pioviggine_gelata",
    "pioggia_debole", "pioggia", "pioggia_forte", "pioggia_gelata",
    "neve_debole", "neve", "neve_forte", "nevischio",
    "rovesci", "rovesci_forti", "rovesci_neve",
    "temporale", "temporale_forte",
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for n in NOMI:
        salva(disegna(n), n)
    print("generate %d icone" % len(NOMI))
