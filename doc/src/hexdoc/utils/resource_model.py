from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Self, dataclass_transform

from pydantic import ValidationInfo, model_validator
from pydantic.functional_validators import ModelWrapValidatorHandler

from .deserialize import JSONDict, cast_or_raise
from .model import HexdocModel, ValidationContext
from .resource import ItemStack, PathResourceDir, ResourceLocation
from .resource_loader import LoaderContext, ModResourceLoader


@dataclass_transform()
class IDModel(HexdocModel):
    id: ResourceLocation
    resource_dir: PathResourceDir

    @classmethod
    def load(
        cls,
        resource_dir: PathResourceDir,
        id: ResourceLocation,
        data: JSONDict,
        context: ValidationContext,
    ) -> Self:
        logging.getLogger(__name__).debug(f"Load {cls} at {id}")
        return cls.model_validate(
            data | {"id": id, "resource_dir": resource_dir},
            context=context,
        )


@dataclass_transform()
class InlineModel(HexdocModel, ABC):
    @classmethod
    @abstractmethod
    def load_id(cls, id: ResourceLocation, context: Any) -> Self:
        ...

    @model_validator(mode="wrap")
    @classmethod
    def _wrap_root_load_from_id(
        cls,
        value: Any,
        handler: ModelWrapValidatorHandler[Self],
        info: ValidationInfo,
    ) -> Self:
        """Loads the recipe from json if the actual value is a resource location str.

        Uses a wrap validator so we load the file *before* resolving the tagged union.
        """
        # if necessary, convert the id to a ResourceLocation
        match value:
            case str():
                id = ResourceLocation.from_str(value)
            case ResourceLocation() as id:
                pass
            case _:
                return handler(value)

        # load the data
        context = cast_or_raise(info.context, ValidationContext)
        return cls.load_id(id, context)


@dataclass_transform()
class InlineItemModel(HexdocModel, ABC):
    @classmethod
    @abstractmethod
    def load_id(cls, item: ItemStack, context: Any) -> Self:
        ...

    @model_validator(mode="wrap")
    @classmethod
    def _wrap_root_load_from_id(
        cls,
        value: Any,
        handler: ModelWrapValidatorHandler[Self],
        info: ValidationInfo,
    ) -> Self:
        """Loads the recipe from json if the actual value is a resource location str.

        Uses a wrap validator so we load the file *before* resolving the tagged union.
        """
        # if necessary, convert the id to a ItemStack
        match value:
            case str():
                item = ItemStack.from_str(value)
            case ItemStack() as item:
                pass
            case ResourceLocation() as id:
                item = ItemStack(namespace=id.namespace, path=id.path)
            case _:
                return handler(value)

        # load the data
        context = cast_or_raise(info.context, ValidationContext)
        return cls.load_id(item, context)


@dataclass_transform()
class InlineIDModel(IDModel, InlineModel, ABC):
    @classmethod
    def load_id(cls, id: ResourceLocation, context: LoaderContext):
        resource_dir, data = cls.load_resource(id, context.loader)
        return cls.load(resource_dir, id, data, context)

    @classmethod
    @abstractmethod
    def load_resource(
        cls,
        id: ResourceLocation,
        loader: ModResourceLoader,
    ) -> tuple[PathResourceDir, JSONDict]:
        ...
