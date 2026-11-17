# Switch 2 Blacklist Patcher

> “Nintendo kept telling me to update my system for a game I'd already bought, wouldn't give me a refund, so I wrote a tool to remove the unnecessary blacklist entries so I could play again.” 😂

A tiny **offline, read-only-on-input** Python utility that creates a targeted `payload.json` for [s8n/blacklist-tool](https://github.com/s8n/blacklist-tool). It does **not** talk to your Switch, touch NAND, or install anything. It only reads your own exported JSON files and generates a new one.

## What it changes

Removes **only exact matches** for four `Launch` restrictions identified in a Switch 2 BCAT blacklist v13 on firmware 23.0.1:

| Game | Title ID | Rule removed |
| --- | --- | --- |
| Civilization VII | `0100C3601518C000` | `SystemUpdateRequired`, system 23.0.1 |
| Civilization VII | `0100C3601518C000` | `ApplicationUpdateRequired`, application version 1638400 |
| SmileBASIC 4 | `0100C9100B06A000` | `SystemUpdateRequired`, system 23.0.1 |
| SmileBASIC Japanese demo | `0100B4B00F9F6000` | `SystemUpdateRequired`, system 23.0.1 |

Every other record is preserved *as JSON data*, in its original order, including unknown records. Other top-level JSON fields are preserved. The generated `payload.json` increments the `version` above the input BCAT blacklist (and the system-data blacklist, if supplied). It won't delete newer rules with different version requirements or additional unexpected fields. **If it finds no exact matches, it writes nothing.**

## Requirements

- Windows, macOS or Linux, with **Python 3** (standard library only; no `pip` packages)
- Your own **BCAT blacklist dump** (for example `20261117-223416-bcat-blacklist.json`), exported by blacklist-tool's **Dump** feature
- Ideally your **system-data blacklist dump** (`*-sysdata-blacklist.json`) from the same Dump operation

## Easy Windows method

1. Download this project ZIP and extract it into a folder.
2. Drag your `*-bcat-blacklist.json` onto `patch-blacklist.bat`.
3. The script prints each removed restriction and creates `payload.json` **beside the `.bat` file**.
4. Read the output before doing anything on your console. If `payload.json` already exists, the script refuses to overwrite it.

**Important:** drag-and-drop uses BCAT version + 1, but cannot know the version of your installed system-data blacklist. For safest version selection, use the command below with `--system`.

## Recommended method (with both dumps)

Open a terminal in this project folder:

```sh
python patch_blacklist.py "/path/to/YOUR-bcat-blacklist.json" \
  --system "/path/to/YOUR-sysdata-blacklist.json" \
  --output payload.json
```

On Windows, you can type this on one line and substitute the real filenames:

```bat
py -3 patch_blacklist.py "C:\path\to\YOUR-bcat-blacklist.json" --system "C:\path\to\YOUR-sysdata-blacklist.json" --output payload.json
```

Example console output for the original v13 scenario:

```text
Input: ... (v13, 56 records)
System: ... (v10)
  REMOVE: Civilization VII: system update
  REMOVE: Civilization VII: application update
  REMOVE: SmileBASIC 4: system update
  REMOVE: SmileBASIC Japanese demo: system update
Wrote: payload.json (v14, 52 records; removed 4)
The original input file was not modified. The console has NOT been changed.
```

## Using the generated payload with blacklist-tool

1. **Keep backups on your PC** of both original JSON dumps, and your original BCAT save if you already have one.
2. Copy the generated `payload.json` to `sdmc:/switch/blacklist-tool/payload.json` on your Switch 2 SD card.
3. Open [blacklist-tool](https://github.com/s8n/blacklist-tool) in HBMenu; select **Write Empty (or payload from SD)**. With `payload.json` present, the tool uses it instead of an empty list.
4. **Check the displayed version and record count before approving.** The app should perform its full BCAT save backup first; cancel if anything looks wrong.
5. Follow blacklist-tool's instructions to reboot. Verify the active `pl:s` version and whether the target game launches.
6. If needed, follow blacklist-tool's **Restore Original** procedure using the backup it created; note that restoring requires access to homebrew again.

**Do not** replace the installed system-data archive manually. This script deliberately separates JSON generation from any on-console modifications.

## Safety / limitations

- This is an early community utility tested with **one console's version 13 BCAT dump** on firmware **23.0.1**. A successful SmileBASIC launch was observed after installing an equivalent custom v14 payload; no universal compatibility or stability guarantee is made.
- A higher `version` changes precedence. Changes made by blacklist-tool can persist across reboots and even factory resets, per its README.
- Writing a BCAT blacklist is a system modification with potential bugs, data loss, and account/console ban risk. DNS blocking tools such as 90DNS **do not guarantee** protection.
- The patcher does **not** validate whether a title is installed, whether the game will otherwise launch, or whether application updates are independently needed.
- Future Nintendo rules with new requirements intentionally do **not** match; review the output rather than assuming every restriction will disappear.
- The script preserves JSON values/records, but reformats JSON whitespace. Never upload dumps containing sensitive information without reviewing them.

## Credits

- [s8n/blacklist-tool](https://github.com/s8n/blacklist-tool) — reads, backs up, writes and restores the BCAT blacklist.
- [SwitchBrew FunctionBlackList documentation](https://switchbrew.org/wiki/Shared_Database_services#FunctionBlackList) — format and background.
- kaiHEN and Switch 2 homebrew contributors for making the research possible.

This is an independent companion script, **not** an official blacklist-tool release or a Nintendo product.
