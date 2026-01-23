import argparse
import sys
from pathlib import Path

from tabby.database import SafariDatabase
from tabby.exporters import export_csv, export_html


def _get_db_path(stp: bool) -> Path:
    app = "SafariTechnologyPreview" if stp else "Safari"
    return (
        Path.home() / "Library" / "Containers" / f"com.apple.{app}"
        / "Data" / "Library" / app / "SafariTabs.db"
    )


def _collect_profiles(db: SafariDatabase) -> list[tuple[str, list]]:
    personal_groups = db.get_personal_groups()
    profiles = [("Personal", personal_groups)]

    for profile in db.get_profiles():
        groups = db.get_profile_groups(profile.id)
        profiles.append((profile.title, groups))

    return profiles


def _run_export(args: argparse.Namespace) -> None:
    base = Path(args.path).expanduser().resolve() / "tabgroups"
    base.mkdir(parents=True, exist_ok=True)

    with SafariDatabase(_get_db_path(args.stp)) as db:
        profiles = _collect_profiles(db)

        for profile_name, groups in profiles:
            profile_dir = base / profile_name.lower()
            profile_dir.mkdir(parents=True, exist_ok=True)

            export_csv(profile_dir, groups, db)
            export_html(profile_dir, groups, db, profile_name.lower())


def _run_save(args: argparse.Namespace) -> None:
    from tabby.bookmarks import BOOKMARKS_PLIST, save_to_bookmarks

    with SafariDatabase(_get_db_path(args.stp)) as db:
        profiles = _collect_profiles(db)
        save_to_bookmarks(BOOKMARKS_PLIST, profiles, db, dry_run=args.dry_run)


def main():
    # Backward compat: if first arg isn't a known subcommand, default to export
    subcommands = {"export", "save"}
    if len(sys.argv) < 2 or sys.argv[1] not in subcommands | {"-h", "--help"}:
        sys.argv.insert(1, "export")

    parser = argparse.ArgumentParser(description="Backup your Safari tab groups")
    subparsers = parser.add_subparsers(dest="command")

    # export subcommand
    export_parser = subparsers.add_parser("export", help="Export tab groups to files")
    export_parser.add_argument(
        "path",
        nargs="?",
        default=str(Path.home() / "Desktop"),
        help="Export location (default: ~/Desktop)",
    )
    export_parser.add_argument(
        "--stp", action="store_true", help="Use Safari Technology Preview"
    )

    # save subcommand
    save_parser = subparsers.add_parser("save", help="Save tab groups to Safari bookmarks")
    save_parser.add_argument(
        "--stp", action="store_true", help="Use Safari Technology Preview"
    )
    save_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be saved without modifying the plist"
    )

    args = parser.parse_args()

    if args.command == "save":
        _run_save(args)
    else:
        _run_export(args)
