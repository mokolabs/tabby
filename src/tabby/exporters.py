import csv
from html import escape
from pathlib import Path

from tabby.database import SafariDatabase, TabGroup


def export_csv(path: Path, groups: list[TabGroup], db: SafariDatabase) -> None:
    with open(path / "bookmarks.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tab Group", "Bookmark", "URL"])

        for group in groups:
            for bookmark in db.get_bookmarks(group.id):
                writer.writerow([group.title, bookmark.title, bookmark.url])


def export_html(path: Path, groups: list[TabGroup], db: SafariDatabase, profile_name: str) -> None:
    title = f"{profile_name.capitalize()} Bookmarks"
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        f"<TITLE>{title}</TITLE>",
        f"<H1>{title}</H1>",
        "<DL><p>",
    ]

    for group in groups:
        bookmarks = db.get_bookmarks(group.id)
        lines.append(f"  <DT><H3>{escape(group.title)}</H3>")
        lines.append("  <DD><DL><p>")
        for bookmark in bookmarks:
            lines.append(f'    <DT><A HREF="{escape(bookmark.url)}">{escape(bookmark.title)}</A>')
        lines.append("  </DL><p>")

    lines.append("</DL><p>")

    with open(path / "bookmarks.html", "w") as f:
        f.write("\n".join(lines) + "\n")
