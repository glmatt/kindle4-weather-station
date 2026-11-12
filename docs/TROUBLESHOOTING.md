# Troubleshooting

Every place this project got stuck, with the fix. Most of these cost an hour
each to work out.

*[In italiano](TROUBLESHOOTING.it.md)*

---

## Jailbreak and diagnostics

| Symptom | Cause and fix |
|---|---|
| No Settings entry in the menu | The menu is contextual: you must be on the Home screen, not inside a book or the browser |
| Diagnostics mode starts but the jailbreak never runs | In the submenu you must pick `R) Reboot System`, not `D) Disable Diags` |
| `Q) To continue` reappears endlessly | Confirm with the **left arrow** on the d-pad, not the centre button. That is what "FW Left" means |
| Every boot returns to diagnostics | `ENABLE_DIAGS` is still in the root. Delete it |
| Jailbreak appears to run but no "You are Jailbroken" book | You likely picked Disable Diags. Repeat — the jailbreak is safe to run multiple times |

---

## USBNetwork and SSH

| Symptom | Cause and fix |
|---|---|
| `;debugOn` gives no confirmation | Normal — debug commands are silent. The real test is whether the Kindle disappears from your file manager |
| Enter does nothing in the search bar | On the K4 the search bar sometimes needs the on-screen keyboard's own Enter key rather than the d-pad centre |
| The Kindle still mounts as a drive | usbnet is not active. Redo `;debugOn` then `~usbNetwork`, with the cable unplugged |
| Network interface shows "Not connected" | usbnet is in a half state. Reboot the Kindle and redo the sequence from scratch |
| Interface picks up `169.254.x.x` | It reverted to DHCP. Set it manually to `192.168.15.201`, netmask `255.255.255.0` |
| `ssh: connect to host ... Operation timed out` | Either the device left usbnet, or the computer lost its manual IP. Check both |
| `scp -r` fails with "path canonicalization failed" | Modern `scp` defaults to a protocol the old server mishandles. Add `-O`, or copy with a file manager in mass storage mode |
| `scp` command appears to split in two | Pasting a long command can introduce a newline. Type it, or `cd` to the folder first and use a short relative path |

---

## TLS and networking

| Symptom | Cause and fix |
|---|---|
| `curl: (35) ... tlsv1 alert protocol version` | The system OpenSSL is 0.9.8j and tops out at TLS 1.0. Not a certificate problem and not a network problem — use Python instead |
| `LD_LIBRARY_PATH` to a newer libssl changes nothing | The system `curl` links `libssl.so.0.9.8` by name; a `libssl.so.1.0.0` is a different library, never considered |
| The experimental browser cannot open any site | Its WebKit is from 2011 and the web is HTTPS now. Plain `http://` pages still load — `http://example.com` is a good test |
| SSH session drops when Wi-Fi is switched on | The device reconfigures its interfaces and takes down the USB one. It happens at the moment of the switch; the two coexist fine afterwards |

---

## FBInk and drawing

| Symptom | Cause and fix |
|---|---|
| The FBInk archive from GitHub has no executables | That is the source release. Binaries are the `-kindle` suffixed attachment in MobileRead thread 299620 |
| `fbink: command not found` under cron | cron does not load the shell profile. Use absolute paths — hence the `FBINK` constant in `meteo.py` |
| Text appears, then the Kindle interface paints over it | The Amazon framework is redrawing. `/etc/init.d/framework stop` silences it, `start` brings it back |
| Ghosting: the previous content shows through | e-ink needs a full refresh. `fbink -c -f`, or `eips -c` twice in a row |
| One band erases part of another | Writing with FBInk clears its cell background. Two bands too close together overlap — space them out |
| Everything shifts down after a change | You switched the vertical axis from rows to pixels. Vertical positions are calibrated against row rounding |

---

## Shell quirks

| Symptom | Cause and fix |
|---|---|
| `grep: invalid option -- 'E'` | It is the BusyBox build, minimal. No extended regular expressions |
| `wget --version` not recognised | Also BusyBox. It is not GNU wget and has no modern TLS |
| `ldd: not found` | Not present on this firmware. Use `strings` on the binary to guess its library dependencies |
| `mntroot: command not found` | You are typing in the wrong terminal window — that is your computer's shell, not the Kindle's. Check the prompt says `[root@kindle` |

---

## General

| Symptom | Cause and fix |
|---|---|
| Advice found online does not work | Most of it targets other models. A tip written for a DXG or a Paperwhite usually does not apply to a K4 — always check which device the author had |
| A guide references KUAL, launchpad or touch gestures | Those belong to 5.x firmware. The K4 is a separate world |

> **The K4 is an island.** Nearly every Kindle project and package of the last
> decade assumes a 5.x firmware with a touchscreen. Before following a guide,
> check that it is really talking about this model.

---

## Rules learned the hard way

**Delete only `.bin` files after installing.** Everything else that appears on
the device — the `usbnet` folder, for instance — is the result of the
installation and must stay.

**Never boot the Kindle while it is plugged into a computer.** Power it on
first, connect afterwards.

**Always `mntroot ro`** after making the system filesystem writable.

**Never factory reset.** Since 20 May 2026 a reset K4 cannot be registered
again.
