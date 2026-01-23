import shutil
import sqlite3
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TabGroup:
    id: int
    title: str


@dataclass
class Bookmark:
    title: str
    url: str


@dataclass
class Profile:
    id: int
    title: str


class SafariDatabase:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        shutil.copy2(self._db_path, self._tmp.name)
        self._tmp.close()
        self._conn = sqlite3.connect(self._tmp.name)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._conn.close()
        Path(self._tmp.name).unlink(missing_ok=True)

    def get_personal_groups(self) -> list[TabGroup]:
        cursor = self._conn.execute(
            "SELECT id, title FROM bookmarks "
            "WHERE type = 1 AND parent = 0 AND subtype = 0 "
            "AND num_children > 0 AND hidden = 0 "
            "ORDER BY id DESC"
        )
        return [TabGroup(id=row[0], title=row[1]) for row in cursor]

    def get_profiles(self) -> list[Profile]:
        cursor = self._conn.execute(
            "SELECT id, title FROM bookmarks WHERE subtype = 2 AND title != ''"
        )
        return [Profile(id=row[0], title=row[1]) for row in cursor]

    def get_profile_groups(self, profile_id: int) -> list[TabGroup]:
        cursor = self._conn.execute(
            "SELECT id, title FROM bookmarks "
            "WHERE parent = ? AND subtype = 0 AND num_children > 0 "
            "ORDER BY id DESC",
            (profile_id,),
        )
        return [TabGroup(id=row[0], title=row[1]) for row in cursor]

    def get_bookmarks(self, group_id: int) -> list[Bookmark]:
        cursor = self._conn.execute(
            "SELECT title, url FROM bookmarks "
            "WHERE parent = ? "
            "AND title NOT IN ('TopScopedBookmarkList', 'Untitled', 'Start Page') "
            "ORDER BY order_index ASC",
            (group_id,),
        )
        return [Bookmark(title=row[0], url=row[1]) for row in cursor]
