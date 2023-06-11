from __future__ import annotations

from dataclasses import InitVar, dataclass
from pathlib import Path
from typing import Any

from common.composition import WithBook
from common.deserialize import FromJson
from common.formatting import FormatTree
from minecraft.i18n import LocalizedStr
from minecraft.resource import ItemStack, ResourceLocation
from patchouli.entry import Entry, parse_entry
from serde import deserialize


@deserialize
class RawCategory(FromJson):
    """Direct representation of a Category json file.

    See: https://vazkiimods.github.io/Patchouli/docs/reference/category-json
    """

    # required
    name: str
    description: str
    icon: ItemStack = ItemStack.field()

    # optional
    parent: ResourceLocation | None = ResourceLocation.field(default=None)
    flag: str | None = None
    sortnum: int = 0
    secret: bool = False


@dataclass
class Category(WithBook):
    """Category with pages and localizations."""

    path: InitVar[Path]

    def __post_init__(self, path: Path):
        self.raw: RawCategory = RawCategory.load(path)

        # category id
        id_resource_path = path.relative_to(self.dir).with_suffix("").as_posix()
        self.id = ResourceLocation(self.modid, id_resource_path)

        # localized strings
        self.name: LocalizedStr = self.i18n.localize(self.raw.name)
        self.description: FormatTree = self.book.format(self.raw.description)

        # entries
        # TODO: make not bad
        self.entries: list[Entry] = []
        entry_dir = self.book.entries_dir / self.id.path
        for entry_path in entry_dir.glob("*.json"):
            basename = entry_path.stem
            self.entries.append(
                parse_entry(
                    self.book, entry_path.as_posix(), self.id.path + "/" + basename
                )
            )
        self.entries.sort(
            key=lambda ent: (
                not ent.get("priority", False),
                ent.get("sortnum", 0),
                ent["name"],
            )
        )

    @property
    def dir(self) -> Path:
        """Directory containing this category's json file."""
        return self.book.categories_dir

    @property
    def parent(self) -> Category | None:
        if self.raw.parent is None:
            return None
        return self.book.categories[self.raw.parent]

    @property
    def href(self) -> str:
        return f"#{self.id.path}"

    @property
    def sortnum(self) -> tuple[int, ...]:
        if self.parent:
            return self.parent.sortnum + (self.raw.sortnum,)
        return (self.raw.sortnum,)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Category):
            return self.sortnum < other.sortnum
        return NotImplemented
