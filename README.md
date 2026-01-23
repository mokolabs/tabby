Tabby
======
Backup your Safari tab groups with Tabby.

Safari tab groups are an awesome way to manage your bookmarks. But, unfortunately at the moment, Safari does not provide a way to backup bookmarks stored within tab groups.

So let's fix that.

Tabby can:
- Export tab groups as HTML and CSV files
- Save tab groups directly into Safari's bookmarks sidebar
- Export tab groups from default profile and all other profiles
- Export tab groups in current order (including tab order within groups)

## Installation

### 1. Install uv
If you don't have `uv` installed, follow the instructions at:
https://docs.astral.sh/uv/getting-started/installation/

### 2. Enable full disk permissions for Terminal app
1. Open System Settings.
2. Select Privacy & Security settings.
3. Select Full Disk Access.
4. Add Terminal app if not listed.
5. Enable Full Disk Access for Terminal app.

### 3. Install script
1. `git clone git@github.com:mokolabs/tabby.git ~/Desktop/tabby`
2. Open your terminal app.
3. Run `cd ~/Desktop/tabby` to open the tabby directory.
4. Run `uv sync` to install dependencies.
5. Run `uv run tabby` to export your tab groups to the desktop.

## Usage

### Export tab groups to files (default)
```
uv run tabby                          # export to ~/Desktop/tabgroups
uv run tabby export ~/Library/Backup  # export to custom location
```

### Save tab groups to Safari bookmarks
```
uv run tabby save                   # save to Bookmarks.plist
uv run tabby save --dry-run         # preview without modifying
```

This creates a "Tabby" folder in Safari's bookmarks sidebar containing your tab groups organized by profile. Re-running replaces the existing folder (a timestamped backup is created automatically).

Your tab groups are not modified or removed — restart Safari, confirm the bookmarks appear in the sidebar, then close the tab groups manually.

### Options
- `--stp` — Use Safari Technology Preview instead of Safari
- Custom export path: `uv run tabby ~/Library/Backup`

### Tips
- The script should work in any location within your home directory.
- Need to backup your tab groups on a daily basis? Just write a cron task that runs the tabby command!

## Feedback
Have a suggestion? Your feedback is welcome! Feel free to open an issue or PR.

(Tabby is brought to you by Sebbie.)

![Sebbie](sebbie.jpg)
