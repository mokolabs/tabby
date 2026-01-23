import os
import plistlib
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

from tabby.database import SafariDatabase, TabGroup

BOOKMARKS_PLIST = Path.home() / "Library" / "Safari" / "Bookmarks.plist"
TABBY_FOLDER_TITLE = "Tabby"


def generate_uuid() -> str:
    return str(uuid.uuid4()).upper()


def make_folder(title: str, children: list[dict]) -> dict:
    return {
        "WebBookmarkUUID": generate_uuid(),
        "WebBookmarkType": "WebBookmarkTypeList",
        "Title": title,
        "Children": children,
    }


def make_leaf(title: str, url: str) -> dict:
    return {
        "WebBookmarkUUID": generate_uuid(),
        "WebBookmarkType": "WebBookmarkTypeLeaf",
        "URLString": url,
        "URIDictionary": {"title": title},
    }


def backup_plist(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_suffix(f".plist.tabby-backup-{stamp}")
    shutil.copy2(path, backup)
    return backup


def is_safari_running() -> bool:
    result = subprocess.run(
        ["pgrep", "-x", "Safari"], capture_output=True, text=True
    )
    return result.returncode == 0


def find_tabby_folder(children: list[dict]) -> int | None:
    for i, child in enumerate(children):
        if (
            child.get("WebBookmarkType") == "WebBookmarkTypeList"
            and child.get("Title") == TABBY_FOLDER_TITLE
        ):
            return i
    return None


def build_tabby_tree(
    profiles: list[tuple[str, list[TabGroup]]], db: SafariDatabase
) -> dict:
    profile_folders = []
    for profile_name, groups in profiles:
        group_folders = []
        for group in groups:
            bookmarks = db.get_bookmarks(group.id)
            leaves = [make_leaf(b.title, b.url) for b in bookmarks]
            if leaves:
                group_folders.append(make_folder(group.title, leaves))
        if group_folders:
            profile_folders.append(make_folder(profile_name, group_folders))
    return make_folder(TABBY_FOLDER_TITLE, profile_folders)


def save_to_bookmarks(
    plist_path: Path,
    profiles: list[tuple[str, list[TabGroup]]],
    db: SafariDatabase,
    dry_run: bool = False,
) -> None:
    try:
        with open(plist_path, "rb") as f:
            plist = plistlib.load(f)
    except FileNotFoundError:
        print(f"Error: {plist_path} not found.")
        print("Grant Full Disk Access to your terminal in System Settings > Privacy & Security > Full Disk Access.")
        raise SystemExit(1)
    except PermissionError:
        print(f"Error: Permission denied reading {plist_path}.")
        print("Grant Full Disk Access to your terminal in System Settings > Privacy & Security > Full Disk Access.")
        raise SystemExit(1)

    if not isinstance(plist.get("Children"), list):
        print("Error: Unexpected Bookmarks.plist structure (missing root Children array).")
        raise SystemExit(1)

    tabby_tree = build_tabby_tree(profiles, db)

    if dry_run:
        _print_tree(tabby_tree, indent=0)
        return

    if is_safari_running():
        print("Warning: Safari is running. Restart Safari to see changes.\n")

    backup = backup_plist(plist_path)
    print(f"Backing up to: {backup}\n")

    children = plist["Children"]
    existing = find_tabby_folder(children)
    if existing is not None:
        children[existing] = tabby_tree
    else:
        children.append(tabby_tree)

    tmp_path = plist_path.with_suffix(".plist.tmp")
    try:
        with open(tmp_path, "wb") as f:
            plistlib.dump(plist, f, fmt=plistlib.FMT_BINARY)
        os.replace(tmp_path, plist_path)
    except PermissionError:
        tmp_path.unlink(missing_ok=True)
        print(f"Error: Permission denied writing {plist_path}.")
        print("Grant Full Disk Access to your terminal in System Settings > Privacy & Security > Full Disk Access.")
        raise SystemExit(1)

    total_groups = 0
    total_bookmarks = 0
    print("Saved to Safari bookmarks:")
    print(f"  {TABBY_FOLDER_TITLE}/")
    for profile_folder in tabby_tree["Children"]:
        print(f"    {profile_folder['Title']}/")
        for group_folder in profile_folder["Children"]:
            count = len(group_folder["Children"])
            total_groups += 1
            total_bookmarks += count
            print(f"      {group_folder['Title']} ({count} bookmarks)")

    print(f"\nDone. {total_groups} tab groups ({total_bookmarks} bookmarks) saved.")


def _print_tree(node: dict, indent: int) -> None:
    prefix = "  " * indent
    if node["WebBookmarkType"] == "WebBookmarkTypeList":
        suffix = f" ({len(node['Children'])} bookmarks)" if all(
            c["WebBookmarkType"] == "WebBookmarkTypeLeaf" for c in node["Children"]
        ) else "/"
        if suffix == "/":
            print(f"{prefix}{node['Title']}/")
        else:
            print(f"{prefix}{node['Title']}{suffix}")
        if suffix == "/":
            for child in node["Children"]:
                _print_tree(child, indent + 1)
    else:
        print(f"{prefix}{node.get('URIDictionary', {}).get('title', '(untitled)')}")
