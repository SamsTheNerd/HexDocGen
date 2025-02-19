from typing import Any, Literal

from pydantic import model_validator

from hexdoc.core.compat import HexVersion
from hexdoc.core.resource import ResourceLocation
from hexdoc.minecraft import LocalizedItem, Recipe
from hexdoc.minecraft.assets.textures import ItemWithTexture
from hexdoc.minecraft.recipe import ItemIngredient, ItemIngredientList
from hexdoc.model import HexdocModel
from hexdoc.model.tagged_union import NoValue, TypeTaggedUnion

# ingredients


class BrainsweepeeIngredient(TypeTaggedUnion, type=None):
    pass


# lol, lmao
class VillagerIngredient(BrainsweepeeIngredient, type="villager"):
    minLevel: int
    profession: ResourceLocation | None = None
    biome: ResourceLocation | None = None


class VillagerIngredient_0_10(VillagerIngredient, type=NoValue):
    pass


class EntityTypeIngredient(BrainsweepeeIngredient, type="entity_type"):
    entityType: ResourceLocation

    @model_validator(mode="after")
    def _check_version(self):
        HexVersion.check(HexVersion.v0_11_x, type(self))
        return self


class EntityTagIngredient(BrainsweepeeIngredient, type="entity_tag"):
    tag: ResourceLocation

    @model_validator(mode="after")
    def _check_version(self):
        HexVersion.check(HexVersion.v0_11_x, type(self))
        return self


class BlockStateIngredient(HexdocModel):
    # TODO: tagged union
    type: Literal["block"]
    block: ItemWithTexture


class ModConditionalIngredient(ItemIngredient, type="hexcasting:mod_conditional"):
    default: ItemIngredientList
    if_loaded: ItemIngredientList
    modid: str


# results


class BlockState(HexdocModel):
    name: ItemWithTexture
    properties: dict[str, Any] | None = None


# recipes


class BrainsweepRecipe(Recipe, type=None):
    blockIn: BlockStateIngredient
    result: BlockState


class BrainsweepRecipe_0_11(BrainsweepRecipe, type="hexcasting:brainsweep"):
    cost: int
    entityIn: BrainsweepeeIngredient

    @model_validator(mode="after")
    def _check_version(self):
        HexVersion.check(HexVersion.v0_11_x, type(self))
        return self


class BrainsweepRecipe_0_10(BrainsweepRecipe, type="hexcasting:brainsweep"):
    villagerIn: VillagerIngredient_0_10

    @model_validator(mode="after")
    def _check_version(self):
        HexVersion.check(lambda v: v <= HexVersion.v0_10_x, type(self))
        return self
