# -*- coding: utf-8 -*-
# ora.py - minute clock for the Kindle 4 Non-Touch
# Redraws only the clock and date, reusing meteo.py's settings.
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
# Aggiorna solo l'orologio della centralina, una volta al minuto.
# Riusa le impostazioni e le funzioni di meteo.py, quindi se sposti
# o ridimensioni la banda dell'ora li' dentro, cambia anche qui.
#
# Uso:  python /mnt/us/meteo/ora.py

import sys
import time

sys.path.insert(0, "/mnt/us/meteo")
import meteo


def main():
    adesso = time.localtime()

    # Nel minuto in cui gira meteo.py non facciamo nulla: ci pensa
    # lui a ridisegnare anche l'orologio, e cosi' evitiamo che i due
    # script si pestino i piedi.
    if adesso.tm_min % 10 == 0:
        return

    # Il Kindle vive in UTC: l'ora locale si ricava dallo scostamento
    # che meteo.py ha salvato l'ultima volta che ha interrogato l'API.
    try:
        scost = int(open(meteo.FILE_FUSO).read().strip())
    except Exception:
        scost = 3600      # ripiego: ora solare italiana

    locale = time.gmtime(time.time() + scost)

    meteo.fb(meteo.ORA_SIZE, meteo.ORA_Y, time.strftime("%H:%M", locale))

    # La cella dell'orologio e' alta e arriva a mordere il bordo
    # superiore della data: la ridisegniamo subito dopo.
    iso = time.strftime("%Y-%m-%dT%H:%M", locale)
    meteo.fb(meteo.DATA_SIZE, meteo.DATA_Y, meteo.data_estesa(iso))


if __name__ == "__main__":
    main()
