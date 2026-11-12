# Quando qualcosa non va

Ogni punto in cui questo progetto si è bloccato, con la soluzione. Quasi tutti
sono costati un'ora a testa.

*[In English](TROUBLESHOOTING.md)*

---

## Jailbreak e diagnostica

| Sintomo | Causa e rimedio |
|---|---|
| Nel menu non c'è la voce Impostazioni | Il menu è contestuale: bisogna essere nella schermata Home, non dentro un libro o nel browser |
| La modalità diagnostica parte ma il jailbreak non viene eseguito | Nel sottomenu va scelto `R) Reboot System`, non `D) Disable Diags` |
| `Q) To continue` ricompare all'infinito | Si conferma con la **freccia sinistra** del d-pad, non col tasto centrale. È quello che significa "FW Left" |
| Ogni avvio riporta in diagnostica | `ENABLE_DIAGS` è rimasto nella radice. Va cancellato |
| Il jailbreak sembra eseguito ma manca il libro "You are Jailbroken" | Probabilmente hai scelto Disable Diags. Ripeti: il jailbreak si può eseguire più volte senza rischi |

---

## USBNetwork e SSH

| Sintomo | Causa e rimedio |
|---|---|
| `;debugOn` non dà conferma | È normale, i comandi di debug sono silenziosi. La verifica vera è che il Kindle sparisca dal gestore file |
| Nella barra di ricerca Invio non fa nulla | Sul K4 la barra a volte richiede il tasto Invio della tastiera a schermo, non il centro del d-pad |
| Il Kindle compare ancora come disco | usbnet non è attivo. Rifai `;debugOn` e poi `~usbNetwork`, con il cavo scollegato |
| L'interfaccia di rete risulta "Non connesso" | usbnet è in uno stato intermedio. Riavvia il Kindle e rifai la sequenza da capo |
| L'interfaccia prende `169.254.x.x` | È tornata in DHCP. Impostala manualmente su `192.168.15.201`, maschera `255.255.255.0` |
| `ssh: connect to host ... Operation timed out` | O il dispositivo è uscito da usbnet, o il computer ha perso l'IP manuale. Controlla entrambi |
| `scp -r` fallisce con "path canonicalization failed" | Lo `scp` moderno usa un protocollo che il vecchio server gestisce male. Aggiungi `-O`, oppure copia col gestore file in modalità disco |
| Il comando `scp` sembra spezzarsi in due | Incollare un comando lungo può introdurre un a capo. Digitalo, oppure fai `cd` nella cartella e usa un percorso relativo corto |

---

## TLS e rete

| Sintomo | Causa e rimedio |
|---|---|
| `curl: (35) ... tlsv1 alert protocol version` | L'OpenSSL di sistema è 0.9.8j e arriva al massimo a TLS 1.0. Non è un problema di certificati né di rete: si usa Python |
| `LD_LIBRARY_PATH` verso una libssl più recente non cambia nulla | Il `curl` di sistema è linkato a `libssl.so.0.9.8` per nome; una `libssl.so.1.0.0` è un'altra libreria, non viene nemmeno considerata |
| Il browser sperimentale non apre nessun sito | Il suo WebKit è del 2011 e il web ormai è HTTPS. Le pagine in `http://` in chiaro si aprono ancora: `http://example.com` è un buon test |
| La sessione SSH cade accendendo la Wi-Fi | Il dispositivo riconfigura le interfacce e abbatte quella USB. Succede nel momento del passaggio; dopo le due convivono senza problemi |

---

## FBInk e disegno

| Sintomo | Causa e rimedio |
|---|---|
| L'archivio FBInk da GitHub non contiene eseguibili | È la release del sorgente. I binari sono l'allegato con suffisso `-kindle` nel thread MobileRead 299620 |
| `fbink: command not found` sotto cron | cron non carica il profilo della shell. Servono percorsi assoluti: per questo `meteo.py` ha la costante `FBINK` |
| Il testo compare, poi l'interfaccia Kindle ci disegna sopra | Il framework Amazon sta ridisegnando. `/etc/init.d/framework stop` lo zittisce, `start` lo riaccende |
| Ghosting: traspare il contenuto precedente | L'e-ink ha bisogno di un refresh completo. `fbink -c -f`, oppure `eips -c` due volte di fila |
| Una banda cancella parte di un'altra | Scrivere con FBInk ripulisce lo sfondo della sua cella. Due bande troppo vicine si sovrappongono: vanno distanziate |
| Dopo una modifica tutto slitta verso il basso | Hai passato l'asse verticale da righe a pixel. Le posizioni verticali sono tarate sull'arrotondamento per righe |

---

## Stranezze della shell

| Sintomo | Causa e rimedio |
|---|---|
| `grep: invalid option -- 'E'` | È la versione BusyBox, minimale. Niente espressioni regolari estese |
| `wget --version` non riconosciuto | Anche questo è BusyBox. Non è GNU wget e non ha TLS moderno |
| `ldd: not found` | Non è presente su questo firmware. Si può usare `strings` sul binario per intuire le dipendenze |
| `mntroot: command not found` | Stai scrivendo nella finestra sbagliata: quella è la shell del tuo computer, non del Kindle. Controlla che il prompt dica `[root@kindle` |

---

## In generale

| Sintomo | Causa e rimedio |
|---|---|
| I consigli trovati online non funzionano | Quasi tutti riguardano altri modelli. Un suggerimento scritto per un DXG o un Paperwhite di solito non vale per un K4: controlla sempre che dispositivo aveva chi scrive |
| Una guida parla di KUAL, launchpad o gesti touch | Appartengono ai firmware 5.x. Il K4 è un mondo a parte |

> **Il K4 è un'isola.** Quasi tutti i progetti e i pacchetti Kindle degli ultimi
> dieci anni presuppongono un firmware 5.x con touch. Prima di seguire una
> guida, verifica che parli davvero di questo modello.

---

## Regole imparate sul campo

**Si cancellano solo i file `.bin` dopo l'installazione.** Tutto il resto che
compare sul dispositivo — la cartella `usbnet`, per esempio — è il risultato
dell'installazione e va lasciato dov'è.

**Non accendere mai il Kindle mentre è collegato al computer.** Prima lo
accendi, poi lo colleghi.

**Dai sempre `mntroot ro`** dopo aver reso scrivibile il filesystem di sistema.

**Non fare mai un reset di fabbrica.** Dal 20 maggio 2026 un K4 resettato non
può più essere registrato.
