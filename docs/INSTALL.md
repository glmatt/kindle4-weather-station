# Installation

From a stock Kindle 4 Non-Touch to a running weather panel. Allow an evening
for the first three stages; the rest is quick.

*[Istruzioni in italiano](INSTALL.it.md)*

---

## Before you start

**Put the Kindle in airplane mode and leave it there** until stage 5. It must
not fetch a firmware update mid-procedure.

**Check your firmware**: Menu → Settings → Menu → Device Info. The jailbreak
works on 4.0.0 through 4.1.4. If you are on 4.1.4 you are on the last firmware
ever released for this model, so nothing can break the jailbreak later.

**Never factory reset.** Since 20 May 2026 a reset K4 can no longer be
registered.

All packages come from NiLuJe's threads on MobileRead and **require a free
forum account** to download attachments.

---

## 1. Jailbreak

Download `kindle-jailbreak-k4-X.Y.N.zip` from
[thread 191158](https://www.mobileread.com/forums/showthread.php?t=191158).
Take the newest version attached to the thread — older copies carry expired
developer certificates.

1. Connect the Kindle over USB and copy to the **root** of its drive:
   - the file `data.tar.gz`
   - a file named `ENABLE_DIAGS` (empty, **no extension**)
   - the folder `diagnostic_logs`
2. Eject and unplug, then restart: **Menu → Settings → Menu → Restart**
3. The device boots into diagnostics mode — a text screen. Using the d-pad,
   choose `D) Exit, Reboot or Disable Diags`
4. In the submenu choose `R) Reboot System` — **not** `D) Disable Diags`, which
   leaves without running the jailbreak
5. Confirm with `Q) To continue`. When the screen says **"FW Left"** it means
   **left on the d-pad**, not the centre button. This is where most people get
   stuck.
6. Wait about 20 seconds. A jailbreak screen appears, then the device restarts.
7. A book titled **"You are Jailbroken"** appears in your library.

Now plug in again and delete `ENABLE_DIAGS`, `data.tar.gz` and
`diagnostic_logs` from the root — otherwise every boot returns to diagnostics.

> On Windows, make sure file extensions are visible before creating
> `ENABLE_DIAGS`. A hidden `.txt` suffix makes the jailbreak fail silently.

The jailbreak only installs a developer key. It modifies no existing files, has
no effect on battery or stability, and can be run more than once safely.

---

## 2. USBNetwork (SSH)

Download `kindle-usbnetwork-0.XX.N-k4.zip` from
[thread 88004](https://www.mobileread.com/forums/showthread.php?t=88004) — mind
the **`k4`** suffix, there are builds for every model.

1. Copy the `..._k4_install.bin` file to the root of the Kindle drive
2. Eject, **unplug the cable**, then: **Menu → Settings → Menu → Update Your
   Kindle**
3. The device restarts on its own. Plug in again and delete the `.bin`.

> Never reboot with a custom `.bin` sitting in the root, and never launch an
> update while in usbnet mode.

### Connecting

With the cable **unplugged**, from the Home screen search bar:

```
;debugOn
```

```
~usbNetwork
```

Neither command gives any confirmation — that is normal. Then plug the cable
in: the Kindle must **disappear** from your file manager. If it still mounts as
a drive, the commands did not go through.

Network settings, fixed for the K4:

| | |
|---|---|
| Your computer | `192.168.15.201`, netmask `255.255.255.0`, no router |
| The Kindle | `192.168.15.244`, user `root` |

On macOS: System Settings → Network → RNDIS/Ethernet Gadget → Details → TCP/IP
→ Manually. The interface tends to revert to DHCP when reconnected, so check it
each time.

```sh
ssh root@192.168.15.244
```

In USB mode the password is not checked — press Enter on an empty prompt. Over
Wi-Fi it is checked, and derives from the device serial (there is a calculator
at [sven.de/kindle](http://www.sven.de/kindle/)).

`~usbNetwork` is a toggle: entering it again returns the device to mass storage
mode, which is handy for copying files with a file manager. `;debugOff` leaves
debug mode when you are done.

---

## 3. Back up

Do this now, before installing anything else. From your computer, in a terminal
window separate from the SSH session:

```sh
ssh root@192.168.15.244 "dd if=/dev/mmcblk0 bs=1M" | gzip -c > kindle-k4-backup.img.gz
```

Around ten minutes, with no progress indication — it looks frozen but is not.
The result is roughly 1 GB. Copy it somewhere other than the machine you made
it on.

If a later experiment goes wrong,
[Kubrick](https://www.mobileread.com/forums/showthread.php?t=206064) is a Linux
live CD built specifically to unbrick a K4.

---

## 4. Python and FBInk

### Python

`kindle-python-0.XX.N-k4.zip`, same
[thread 88004](https://www.mobileread.com/forums/showthread.php?t=88004).
Install exactly like USBNetwork: copy the `.bin` to the root, then Update Your
Kindle. It takes a few minutes — the package is large.

Verify:

```sh
python --version                                    # 2.7.10
python -c "import ssl; print(ssl.OPENSSL_VERSION)"  # OpenSSL 1.0.2d
```

**OpenSSL 1.0.x is the whole point.** Without it nothing else works.

### FBInk

`FBInk-vX.Y.Z-kindle.tar.gz` from
[thread 299620](https://www.mobileread.com/forums/showthread.php?t=299620).
Note the **`-kindle`** suffix: the GitHub release holds source only, which
would need a cross-compilation toolchain.

Copy the **K3** folder to the device — it is the correct build for the K4:

```sh
scp -O -r K3 root@192.168.15.244:/mnt/us/fbink
```

> `scp` on recent macOS defaults to a protocol the old server mishandles for
> directories. The `-O` flag forces the classic SCP protocol.

Then, on the Kindle, link the binaries so they are on the path:

```sh
cd /usr/local/bin
mntroot rw
ln -s /mnt/us/fbink/bin/fbink fbink
ln -s /mnt/us/fbink/bin/fbdepth fbdepth
mntroot ro
```

**Always `mntroot ro` when done** — leaving the system filesystem writable
invites corruption on an unexpected reboot.

Test:

```sh
fbink -c -f
fbink -F ORP -S 10 -y 3 -m "12:34"
```

---

## 5. The panel

Copy the project files:

```sh
ssh root@192.168.15.244 "mkdir -p /mnt/us/meteo"
scp -O meteo.py ora.py root@192.168.15.244:/mnt/us/meteo/
scp -O -r icone root@192.168.15.244:/mnt/us/meteo/
```

Set your location at the top of `meteo.py`:

```python
LAT = 45.07          # your latitude
LON = 7.69           # your longitude
FUSO = "Europe/Rome" # your IANA time zone
```

Now turn Wi-Fi **on** (leave airplane mode) and connect to your network. This
may drop the USB session the first time; if so, redo `;debugOn` and
`~usbNetwork` with the cable unplugged. Wi-Fi and usbnet do coexist once
settled.

Run it:

```sh
python /mnt/us/meteo/meteo.py
```

---

## 6. Automation

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

This backs up the existing crontab, strips any previous lines of ours and
writes the new ones. It can be re-run without duplicating anything.

**Adjust the hours** to match your own smart plug schedule — the ranges above
assume power from 05:00 to 09:00 and 17:00 to 23:30.

Paths must be absolute: cron does not load the shell profile.

---

## 7. Mounting

Pick a spot with ambient light — the K4 has no front light.

**Do not leave the device permanently on charge.** A fifteen-year-old lithium
cell swells under constant trickle charging. A smart plug on a schedule solves
it; alternatively the device can be opened and the battery disconnected, with
power from USB only.

---

## When you need to get back in

```
;debugOn
~usbNetwork
```

then plug in the cable and `ssh root@192.168.15.244`. Check your computer's
network interface still has the manual IP — it often reverts to DHCP.
