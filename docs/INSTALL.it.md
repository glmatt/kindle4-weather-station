# Installazione

Da un Kindle 4 Non-Touch di serie a un pannello meteo funzionante. Per le prime
tre tappe conviene mettere in conto una serata; il resto è rapido.

*[Instructions in English](INSTALL.md)*

---

## Prima di cominciare

**Metti il Kindle in modalità aereo e lascialo così** fino alla tappa 5. Non
deve scaricare un aggiornamento firmware a metà procedura.

**Controlla il firmware**: Menu → Impostazioni → Menu → Info dispositivo. Il
jailbreak funziona dalla 4.0.0 alla 4.1.4. Se sei sulla 4.1.4 hai l'ultimo
firmware mai rilasciato per questo modello, quindi niente potrà rompere il
jailbreak in futuro.

**Non fare mai un reset di fabbrica.** Dal 20 maggio 2026 un K4 resettato non
può più essere registrato.

Tutti i pacchetti vengono dai thread di NiLuJe su MobileRead e **richiedono un
account gratuito del forum** per scaricare gli allegati.

---

## 1. Jailbreak

Scarica `kindle-jailbreak-k4-X.Y.N.zip` dal
[thread 191158](https://www.mobileread.com/forums/showthread.php?t=191158).
Prendi la versione più recente allegata al thread: le copie vecchie hanno
certificati di sviluppo scaduti.

1. Collega il Kindle via USB e copia nella **radice** del suo disco:
   - il file `data.tar.gz`
   - un file chiamato `ENABLE_DIAGS` (vuoto, **senza estensione**)
   - la cartella `diagnostic_logs`
2. Espelli e scollega, poi riavvia: **Menu → Impostazioni → Menu → Riavvia**
3. Il dispositivo parte in modalità diagnostica, una schermata testuale. Col
   d-pad scegli `D) Exit, Reboot or Disable Diags`
4. Nel sottomenu scegli `R) Reboot System` — **non** `D) Disable Diags`, che
   esce senza eseguire il jailbreak
5. Conferma con `Q) To continue`. Quando lo schermo dice **"FW Left"** intende
   **sinistra sul d-pad**, non il tasto centrale. È il punto dove si bloccano
   tutti.
6. Aspetta una ventina di secondi: compare la schermata del jailbreak, poi il
   dispositivo si riavvia.
7. In libreria compare un libro intitolato **"You are Jailbroken"**.

Ricollega e cancella `ENABLE_DIAGS`, `data.tar.gz` e `diagnostic_logs` dalla
radice, altrimenti ogni avvio riporta in diagnostica.

> Su Windows, assicurati che le estensioni dei file siano visibili prima di
> creare `ENABLE_DIAGS`. Un `.txt` nascosto fa fallire il jailbreak senza dire
> perché.

Il jailbreak si limita a installare una chiave di sviluppo. Non modifica
nessun file esistente, non ha effetti su batteria o stabilità, e si può
eseguire più volte senza rischi.

---

## 2. USBNetwork (SSH)

Scarica `kindle-usbnetwork-0.XX.N-k4.zip` dal
[thread 88004](https://www.mobileread.com/forums/showthread.php?t=88004) —
attenzione al suffisso **`k4`**, ci sono versioni per ogni modello.

1. Copia il file `..._k4_install.bin` nella radice del disco del Kindle
2. Espelli, **scollega il cavo**, poi: **Menu → Impostazioni → Menu → Aggiorna
   Kindle**
3. Il dispositivo si riavvia da solo. Ricollega e cancella il `.bin`.

> Non riavviare mai con un `.bin` personalizzato nella radice, e non lanciare
> aggiornamenti mentre sei in modalità usbnet.

### Collegarsi

Con il cavo **scollegato**, dalla barra di ricerca della schermata Home:

```
;debugOn
```

```
~usbNetwork
```

Nessuno dei due comandi dà conferma: è normale. Poi collega il cavo: il Kindle
deve **sparire** dal gestore file. Se compare ancora come disco, i comandi non
sono passati.

Impostazioni di rete, fisse per il K4:

| | |
|---|---|
| Il tuo computer | `192.168.15.201`, maschera `255.255.255.0`, router vuoto |
| Il Kindle | `192.168.15.244`, utente `root` |

Su macOS: Impostazioni di Sistema → Rete → RNDIS/Ethernet Gadget → Dettagli →
TCP/IP → Manualmente. L'interfaccia tende a tornare in DHCP quando si
ricollega, quindi conviene ricontrollarla ogni volta.

```sh
ssh root@192.168.15.244
```

In modalità USB la password non viene verificata: basta premere Invio a vuoto.
Via Wi-Fi invece viene verificata, e si ricava dal numero di serie del
dispositivo (c'è un calcolatore su
[sven.de/kindle](http://www.sven.de/kindle/)).

`~usbNetwork` fa da interruttore: ridandolo il dispositivo torna in modalità
disco, comodo per copiare file col gestore file. `;debugOff` esce dalla
modalità debug quando hai finito.

---

## 3. Backup

Fallo adesso, prima di installare altro. Dal tuo computer, in una finestra di
terminale diversa da quella con la sessione SSH:

```sh
ssh root@192.168.15.244 "dd if=/dev/mmcblk0 bs=1M" | gzip -c > kindle-k4-backup.img.gz
```

Una decina di minuti, senza alcuna indicazione di avanzamento: sembra bloccato
ma non lo è. Il risultato è circa 1 GB. Copialo da qualche parte che non sia la
macchina su cui l'hai creato.

Se un esperimento futuro va storto,
[Kubrick](https://www.mobileread.com/forums/showthread.php?t=206064) è una live
CD Linux fatta apposta per recuperare un K4.

---

## 4. Python e FBInk

### Python

`kindle-python-0.XX.N-k4.zip`, stesso
[thread 88004](https://www.mobileread.com/forums/showthread.php?t=88004).
L'installazione è identica a USBNetwork: copi il `.bin` nella radice, poi
Aggiorna Kindle. Richiede qualche minuto, il pacchetto è grosso.

Verifica:

```sh
python --version                                    # 2.7.10
python -c "import ssl; print(ssl.OPENSSL_VERSION)"  # OpenSSL 1.0.2d
```

**OpenSSL 1.0.x è tutto il punto.** Senza quello, niente altro funziona.

### FBInk

`FBInk-vX.Y.Z-kindle.tar.gz` dal
[thread 299620](https://www.mobileread.com/forums/showthread.php?t=299620).
Occhio al suffisso **`-kindle`**: la release su GitHub contiene solo il
sorgente, che richiederebbe una toolchain di cross-compilazione.

Copia la cartella **K3** sul dispositivo, che è la build giusta per il K4:

```sh
scp -O -r K3 root@192.168.15.244:/mnt/us/fbink
```

> Su macOS recenti `scp` usa di default un protocollo che il vecchio server
> gestisce male con le cartelle. L'opzione `-O` forza il protocollo SCP
> classico.

Poi, sul Kindle, collega i binari perché siano richiamabili ovunque:

```sh
cd /usr/local/bin
mntroot rw
ln -s /mnt/us/fbink/bin/fbink fbink
ln -s /mnt/us/fbink/bin/fbdepth fbdepth
mntroot ro
```

**Dai sempre `mntroot ro` alla fine**: lasciare il filesystem di sistema
scrivibile invita alla corruzione al primo riavvio imprevisto.

Prova:

```sh
fbink -c -f
fbink -F ORP -S 10 -y 3 -m "12:34"
```

---

## 5. Il pannello

Copia i file del progetto:

```sh
ssh root@192.168.15.244 "mkdir -p /mnt/us/meteo"
scp -O meteo.py ora.py root@192.168.15.244:/mnt/us/meteo/
scp -O -r icone root@192.168.15.244:/mnt/us/meteo/
```

Imposta la tua località in cima a `meteo.py`:

```python
LAT = 45.07          # la tua latitudine
LON = 7.69           # la tua longitudine
FUSO = "Europe/Rome" # il tuo fuso IANA
```

Adesso accendi la **Wi-Fi** (esci dalla modalità aereo) e collegati alla tua
rete. La prima volta questo può far cadere la sessione USB; in tal caso rifai
`;debugOn` e `~usbNetwork` con il cavo scollegato. Wi-Fi e usbnet convivono,
una volta stabilizzate.

Lancia:

```sh
python /mnt/us/meteo/meteo.py
```

---

## 6. Automazione

```sh
mntroot rw
cp /etc/crontab/root /mnt/us/meteo/crontab.bak
grep -v "/mnt/us/meteo/" /etc/crontab/root | grep -v wirelessEnable > /tmp/ct
cat >> /tmp/ct <<'EOF'
*/10 5-8,17-23 * * * /usr/bin/python /mnt/us/meteo/meteo.py >/dev/null 2>&1
* 5-8,17-23 * * * /usr/bin/python /mnt/us/meteo/ora.py >/dev/null 2>&1
55 4,16 * * * lipc-set-prop com.lab126.cmd wirelessEnable 1
1 9 * * * lipc-set-prop com.lab126.cmd wirelessEnable 0
25 23 * * * lipc-set-prop com.lab126.cmd wirelessEnable 0
EOF
cp /tmp/ct /etc/crontab/root
mntroot ro
/etc/init.d/cron restart
cat /etc/crontab/root
```

Il blocco fa un backup del crontab esistente, toglie eventuali righe nostre
precedenti e scrive le nuove. Si può rilanciare senza duplicare nulla.

**Adatta gli orari** alla pianificazione della tua presa smart: le fasce qui
sopra presuppongono corrente dalle 5:00 alle 9:00 e dalle 17:00 alle 23:30.

I percorsi devono essere assoluti: cron non carica il profilo della shell.

---

## 7. Montaggio

Scegli un punto con luce ambientale: il K4 non ha retroilluminazione.

**Non lasciare il dispositivo sempre in carica.** Una cella al litio di quindici
anni si gonfia sotto carica mantenuta continua. Una presa smart con fasce
orarie risolve; in alternativa si può aprire il dispositivo e scollegare la
batteria, alimentandolo solo da USB.

---

## Per rientrare in futuro

```
;debugOn
~usbNetwork
```

poi collega il cavo e `ssh root@192.168.15.244`. Controlla che l'interfaccia di
rete del computer abbia ancora l'IP manuale: tende a tornare in DHCP.
