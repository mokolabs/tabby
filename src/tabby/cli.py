import argparse
from pathlib import Path

from tabby.database import SafariDatabase
from tabby.exporters import export_csv, export_html


def main():
    parser = argparse.ArgumentParser(description="Backup your Safari tab groups")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(Path.home() / "Desktop"),
        help="Export location (default: ~/Desktop)",
    )
    parser.add_argument(
        "--stp",
        action="store_true",
        help="Use Safari Technology Preview",
    )
    args = parser.parse_args()

    base = Path(args.path).expanduser().resolve() / "tabgroups"
    base.mkdir(parents=True, exist_ok=True)

    app = "SafariTechnologyPreview" if args.stp else "Safari"
    db_path = Path.home() / "Library" / "Containers" / f"com.apple.{app}" / "Data" / "Library" / app / "SafariTabs.db"

    with SafariDatabase(db_path) as db:
        # Personal profile tab groups
        personal_groups = db.get_personal_groups()
        profiles = [("personal", personal_groups)]

        # Other profiles
        for profile in db.get_profiles():
            groups = db.get_profile_groups(profile.id)
            profiles.append((profile.title.lower(), groups))

        for profile_name, groups in profiles:
            profile_dir = base / profile_name
            profile_dir.mkdir(parents=True, exist_ok=True)

            export_csv(profile_dir, groups, db)
            export_html(profile_dir, groups, db, profile_name)
