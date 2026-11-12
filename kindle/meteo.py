# -*- coding: utf-8 -*-
# meteo.py - weather panel for the Kindle 4 Non-Touch
# Fetches data from Open-Meteo and draws the panel with FBInk.
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

#
# Centralina meteo per Kindle 4 NT
# Scarica i dati da Open-Meteo e li disegna con FBInk.
#
# Uso:  python /mnt/us/meteo/meteo.py
#
# I valori sotto la riga "REGOLAZIONI" sono quelli da ritoccare
# se il pannello non e' posizionato come vuoi.

import json
import os
import re
import ssl
import time
import urllib2
import subprocess

# ----------------------------------------------------------------
# REGOLAZIONI
# ----------------------------------------------------------------

LAT = 45.07          # Torino
LON = 7.69
FUSO = "Europe/Rome"

FONT = "ORP"
FBINK = "/usr/local/bin/fbink"     # percorso assoluto: cron non usa il PATH

# Qui viene salvato lo scostamento dal fuso UTC, cosi' ora.py
# puo' calcolare l'ora locale senza interrogare la rete.
FILE_FUSO = "/mnt/us/meteo/fuso.txt"

# Storico della batteria: una riga per ogni esecuzione.
# Per leggerlo:  cat /mnt/us/meteo/batteria.log
FILE_LOG = "/mnt/us/meteo/batteria.log"

# Ogni banda: (dimensione del carattere, altezza in PIXEL dall'alto).
# Lo schermo e' alto 800 pixel. Per spostare una banda cambia il
# secondo numero: piu' grande = piu' in basso.
ORA_SIZE,    ORA_Y    = 10, 45
DATA_SIZE,   DATA_Y   = 3,  150
TEMP_SIZE,   TEMP_Y   = 14, 255
DESC_SIZE,   DESC_Y   = 3,  415
MINMAX_SIZE, MINMAX_Y = 3,  460
ORE_H_SIZE,  ORE_H_Y  = 2,  545   # riga delle ore
ORE_T_SIZE,  ORE_T_Y  = 3,  580   # riga delle temperature, piu' grande
ORE_MARGINE  = 25                 # rientro laterale della striscia

CARTELLA_ICONE = "/mnt/us/meteo/icone"
ICONA_LATO     = 130   # le icone sono quadrate, 130x130
ICONA_STACCO   = 20    # spazio fra icona e temperatura
ICONA_ALZA     = 8     # quanto alzare l'icona: i glifi del font non
                       # sono centrati nella loro cella, hanno piu'
                       # spazio sotto che sopra
GRADO_LARG     = 0.55  # quanto della sua cella riempie davvero il "°":
                       # serve a centrare sul disegno, non sulle celle

DOM_SIZE,    DOM_Y    = 3,  665
SOLE_SIZE,   SOLE_Y   = 2,  715
AGG_SIZE,    AGG_Y    = 2,  760

# Linee separatrici: (altezza in pixel, spessore in pixel)
LINEA1_Y, LINEA1_H = 220, 3    # tra data e temperatura
LINEA2_Y, LINEA2_H = 505, 2    # tra meteo attuale e previsioni

LINEA_MARGINE = 70             # quanto rientra dai bordi
SCHERMO_L = 600                # larghezza dello schermo

ORE_AVANTI = 6       # quante ore mostrare nella striscia

# ----------------------------------------------------------------

WMO = {
    0:  "sereno",
    1:  "poco nuvoloso",
    2:  "parz. nuvoloso",
    3:  "coperto",
    45: "nebbia",
    48: "nebbia gelata",
    51: "pioviggine",
    53: "pioviggine",
    55: "pioviggine intensa",
    56: "pioviggine gelata",
    57: "pioviggine gelata",
    61: "pioggia debole",
    63: "pioggia",
    65: "pioggia forte",
    66: "pioggia gelata",
    67: "pioggia gelata",
    71: "neve debole",
    73: "neve",
    75: "neve forte",
    77: "nevischio",
    80: "rovesci",
    81: "rovesci",
    82: "rovesci forti",
    85: "rovesci di neve",
    86: "rovesci di neve",
    95: "temporale",
    96: "temporale",
    99: "temporale forte",
}

# Da codice WMO al nome del file in icone/.
# Dove ci sono due nomi, il secondo e' la versione notturna.
ICONE = {
    0:  ("sereno", "sereno_notte"),
    1:  ("poco_nuvoloso", "poco_nuvoloso_notte"),
    2:  ("parz_nuvoloso", "parz_nuvoloso_notte"),
    3:  ("coperto",),
    45: ("nebbia",),
    48: ("nebbia_gelata",),
    51: ("pioviggine",),
    53: ("pioviggine",),
    55: ("pioviggine_intensa",),
    56: ("pioviggine_gelata",),
    57: ("pioviggine_gelata",),
    61: ("pioggia_debole",),
    63: ("pioggia",),
    65: ("pioggia_forte",),
    66: ("pioggia_gelata",),
    67: ("pioggia_gelata",),
    71: ("neve_debole",),
    73: ("neve",),
    75: ("neve_forte",),
    77: ("nevischio",),
    80: ("rovesci",),
    81: ("rovesci",),
    82: ("rovesci_forti",),
    85: ("rovesci_neve",),
    86: ("rovesci_neve",),
    95: ("temporale",),
    96: ("temporale",),
    99: ("temporale_forte",),
}

GIORNI = ["lunedi", "martedi", "mercoledi", "giovedi",
          "venerdi", "sabato", "domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def scarica():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=%s&longitude=%s"
        "&current=temperature_2m,apparent_temperature,weather_code,is_day"
        "&hourly=temperature_2m,precipitation_probability,weather_code"
        "&daily=temperature_2m_max,temperature_2m_min,weather_code,sunrise,sunset"
        "&timezone=%s&forecast_days=2"
    ) % (LAT, LON, FUSO)
    ctx = ssl._create_unverified_context()
    return json.loads(urllib2.urlopen(url, context=ctx, timeout=30).read())


_celle = {}


def cella(size):
    """Chiede a FBInk quanto misura una cella a questa dimensione."""
    if size in _celle:
        return _celle[size]
    p = subprocess.Popen(
        [FBINK, "-F", FONT, "-S", str(size), "-v", "-y", "0", " "],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()[0]
    wh = (8 * size, 8 * size)
    m = re.search(r"Fontsize set to (\d+)x(\d+)", out)
    if m:
        wh = (int(m.group(1)), int(m.group(2)))
    _celle[size] = wh
    return wh


def altezza_cella(size):
    return cella(size)[1]


def fb(size, y_pixel, testo):
    """Disegna il testo centrato, all'altezza indicata in pixel."""
    riga = int(y_pixel / altezza_cella(size))
    subprocess.call([
        FBINK, "-F", FONT, "-S", str(size), "-y", str(riga), "-m", testo
    ])


_offset_ok = None    # FBInk accetta -X/-Y? Si scopre al primo uso.


def fb_px(size, x_pixel, y_pixel, testo):
    """Disegna il testo alla posizione data, in pixel.

    Solo l'orizzontale e' al pixel, con l'offset -X: a dimensione 14
    una cella e' larga oltre cento pixel, troppo per affiancare icona
    e testo con precisione. Il verticale resta per righe di cella,
    perche' le altezze del pannello sono tarate su quell'arrotondamento
    e passare al pixel le farebbe slittare tutte.
    """
    global _offset_ok
    w, h = cella(size)
    nulla = open("/dev/null", "w")

    if _offset_ok is not False:
        esito = subprocess.call(
            [FBINK, "-F", FONT, "-S", str(size),
             "-x", "0", "-X", str(int(round(x_pixel))),
             "-y", str(int(y_pixel / h)), testo],
            stdout=nulla, stderr=subprocess.STDOUT)
        if esito == 0:
            _offset_ok = True
            return
        _offset_ok = False

    subprocess.call([
        FBINK, "-F", FONT, "-S", str(size),
        "-x", str(max(0, int(round(x_pixel / float(w))))),
        "-y", str(int(y_pixel / h)), testo
    ])


def colonne(size, voci, y_pixel, centri=None):
    """Dispone le voci in colonne di uguale larghezza.

    Restituisce i centri effettivi usati, in pixel, cosi' una seconda
    riga puo' essere allineata esattamente sotto la prima.
    """
    w = cella(size)[0]
    if centri is None:
        utile = SCHERMO_L - 2 * ORE_MARGINE
        passo = utile / float(len(voci))
        centri = [ORE_MARGINE + passo * (i + 0.5) for i in range(len(voci))]
    effettivi = []
    for i, testo in enumerate(voci):
        x = centri[i] - (len(testo) * w) / 2.0
        col = max(0, int(round(x / float(w))))
        subprocess.call([
            FBINK, "-F", FONT, "-S", str(size), "-x", str(col),
            "-y", str(int(y_pixel / cella(size)[1])), testo
        ])
        effettivi.append(col * w + (len(testo) * w) / 2.0)
    return effettivi


def icona(nome, x, y):
    """Disegna una icona PNG. True se e' andata."""
    percorso = "%s/%s.png" % (CARTELLA_ICONE, nome)
    if not os.path.exists(percorso):
        return False
    esito = subprocess.call(
        [FBINK, "-g", "file=%s,x=%d,y=%d" % (percorso, int(x), int(y))],
        stdout=open("/dev/null", "w"), stderr=subprocess.STDOUT)
    return esito == 0


def nome_icona(codice, giorno):
    voci = ICONE.get(codice)
    if not voci:
        return None
    if len(voci) > 1 and not giorno:
        return voci[1]
    return voci[0]


def linea(y, spessore):
    """Riga orizzontale nera, disegnata riempiendo un rettangolo."""
    larg = SCHERMO_L - 2 * LINEA_MARGINE
    rect = "top=%d,left=%d,width=%d,height=%d" % (
        y, LINEA_MARGINE, larg, spessore)
    esito = subprocess.call(
        [FBINK, "-B", "BLACK", "-k", rect],
        stdout=open("/dev/null", "w"), stderr=subprocess.STDOUT)
    if esito != 0:
        # ripiego: una fila di trattini, se il riempimento non funziona
        fb(2, y, "-" * 34)


def data_estesa(iso):
    # iso = "2026-11-02T18:43"
    anno, mese, giorno = int(iso[0:4]), int(iso[5:7]), int(iso[8:10])
    # giorno della settimana, algoritmo di Zeller semplificato
    t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    a = anno - (1 if mese < 3 else 0)
    dow = (a + a // 4 - a // 100 + a // 400 + t[mese - 1] + giorno) % 7
    dow = (dow + 6) % 7  # 0 = lunedi
    return "%s %d %s" % (GIORNI[dow], giorno, MESI[mese - 1])


def tieni_sveglio():
    """Disattiva lo screensaver e tiene viva la Wi-Fi."""
    subprocess.call(
        ["lipc-set-prop", "--", "com.lab126.powerd", "preventScreenSaver", "1"],
        stdout=open("/dev/null", "w"), stderr=subprocess.STDOUT)


def prop(servizio, nome):
    """Legge una proprieta' lipc; None se non disponibile."""
    try:
        p = subprocess.Popen(["lipc-get-prop", servizio, nome],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = p.communicate()
        if p.returncode != 0:
            return None
        return int(out.strip())
    except Exception:
        return None


def batteria():
    """(livello in %, in carica) — None dove il dato manca."""
    return (prop("com.lab126.powerd", "battLevel"),
            prop("com.lab126.powerd", "isCharging"))


def ora_locale_iso():
    """Ora locale come stringa, dal fuso salvato l'ultima volta."""
    try:
        scost = int(open(FILE_FUSO).read().strip())
    except Exception:
        scost = 3600
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + scost))


def registra(liv, carica, quando):
    """Appende una riga allo storico: data, livello, in carica."""
    if liv is None:
        return
    try:
        f = open(FILE_LOG, "a")
        f.write("%s\t%d\t%d\n" % (quando, liv, carica or 0))
        f.close()
    except Exception:
        pass


def main():
    tieni_sveglio()

    # Lo storico della batteria si scrive comunque, anche se poi
    # la rete non risponde: serve a capire come si comporta la presa.
    liv, carica = batteria()
    registra(liv, carica, ora_locale_iso())

    # Se la rete non risponde, non si tocca lo schermo: resta
    # l'ultimo pannello buono invece di una pagina bianca.
    try:
        d = scarica()
    except Exception:
        return

    # salva lo scostamento dal fuso per l'orologio al minuto
    try:
        f = open(FILE_FUSO, "w")
        f.write(str(int(d["utc_offset_seconds"])))
        f.close()
    except Exception:
        pass

    cur = d["current"]
    ora_iso = cur["time"]                  # "2026-11-02T18:45"

    # L'orologio mostra l'ora di sistema, non quella dell'API:
    # Open-Meteo arrotonda current.time ai quindici minuti, e il
    # pannello resterebbe arretrato fino al giro di ora.py.
    adesso = ora_locale_iso()              # "2026-11-08 19:43"
    ora = adesso[11:16]
    temp = int(round(cur["temperature_2m"]))
    perc = int(round(cur["apparent_temperature"]))
    desc = WMO.get(cur["weather_code"], "")

    day = d["daily"]
    oggi_max = int(round(day["temperature_2m_max"][0]))
    oggi_min = int(round(day["temperature_2m_min"][0]))
    dom_max = int(round(day["temperature_2m_max"][1]))
    dom_min = int(round(day["temperature_2m_min"][1]))
    dom_desc = WMO.get(day["weather_code"][1], "")
    alba = day["sunrise"][1][11:16]
    tram = day["sunset"][1][11:16]

    # striscia delle prossime ore: trova l'indice dell'ora corrente
    ore = d["hourly"]["time"]
    idx = 0
    for i, t in enumerate(ore):
        if t[:13] == ora_iso[:13]:
            idx = i
            break
    ore_label = []
    ore_temp = []
    for i in range(idx + 1, min(idx + 1 + ORE_AVANTI, len(ore))):
        pp = d["hourly"]["precipitation_probability"][i]
        pp = 0 if pp is None else int(pp)
        ore_label.append("%s%s" % (ore[i][11:13], "*" if pp >= 40 else ""))
        ore_temp.append(u"%d\u00b0".encode("utf-8") %
                        int(round(d["hourly"]["temperature_2m"][i])))

    # misura i caratteri PRIMA di pulire, cosi' la pulizia
    # cancella gli spazi usati per la calibrazione
    for s in (ORA_SIZE, DATA_SIZE, TEMP_SIZE, DESC_SIZE, MINMAX_SIZE,
              ORE_H_SIZE, ORE_T_SIZE, DOM_SIZE, SOLE_SIZE, AGG_SIZE):
        cella(s)

    # disegno
    subprocess.call([FBINK, "-c", "-f"])
    fb(ORA_SIZE,    ORA_Y,    ora)
    fb(DATA_SIZE,   DATA_Y,   data_estesa(adesso))
    linea(LINEA1_Y, LINEA1_H)
    # Icona a sinistra e temperatura a destra, come blocco unico
    # centrato. Se l'icona manca o FBInk la rifiuta, la temperatura
    # torna al centro da sola.
    testo_u = u"%d\u00b0" % temp
    larg_w, alt_h = cella(TEMP_SIZE)

    # Larghezza di quel che si VEDE, non delle celle occupate: il "\u00b0"
    # ha una cella sua ma ne disegna poco piu' di meta', e centrando
    # sulle celle il blocco finisce spostato a sinistra.
    larg_vista = (len(testo_u) - 1 + GRADO_LARG) * larg_w

    ic = nome_icona(cur.get("weather_code"), cur.get("is_day", 1))
    disegnata = False

    if ic:
        blocco = ICONA_LATO + ICONA_STACCO + larg_vista
        x_ic = (SCHERMO_L - blocco) / 2.0
        y_ic = TEMP_Y + (alt_h - ICONA_LATO) / 2.0 - ICONA_ALZA
        if x_ic >= 0:
            disegnata = icona(ic, x_ic, max(0, y_ic))

    if disegnata:
        x_testo = x_ic + ICONA_LATO + ICONA_STACCO
    else:
        x_testo = (SCHERMO_L - larg_vista) / 2.0

    fb_px(TEMP_SIZE, x_testo, TEMP_Y, testo_u.encode("utf-8"))
    fb(DESC_SIZE,   DESC_Y,
       u"%s   perc %d\u00b0".encode("utf-8") % (desc, perc))
    fb(MINMAX_SIZE, MINMAX_Y,
       u"max %d\u00b0   min %d\u00b0".encode("utf-8") % (oggi_max, oggi_min))
    linea(LINEA2_Y, LINEA2_H)
    centri = colonne(ORE_H_SIZE, ore_label, ORE_H_Y)
    colonne(ORE_T_SIZE, ore_temp, ORE_T_Y, centri)
    fb(DOM_SIZE,    DOM_Y,
       u"DOMANI %s %d\u00b0/%d\u00b0".encode("utf-8") %
       (dom_desc, dom_max, dom_min))
    fb(SOLE_SIZE,   SOLE_Y,   "alba %s   tramonto %s" % (alba, tram))
    piede = "Torino - agg. %s" % ora
    if liv is not None:
        piede += "   batt %d%%%s" % (liv, "+" if carica else "")
    fb(AGG_SIZE,    AGG_Y,    piede)


if __name__ == "__main__":
    main()
