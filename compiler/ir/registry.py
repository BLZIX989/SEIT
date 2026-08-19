"""Object / Type / Transformation / Equation registries (spec section 8, 29).

Registries are the in-memory source of truth; `dump_json` serializes each
to the top-level *_registry.json artifacts required by spec section 37.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from compiler.core.ir import Equation, Object, Transformation
from compiler.core.status import Status


@dataclass
class TypeDef:
    name: str
    description: str
    parent: str | None = None

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description, "parent": self.parent}


class Registry:
    """Generic id -> node registry with duplicate/consistency guards."""

    def __init__(self, kind: str):
        self.kind = kind
        self._items: dict[str, object] = {}

    def add(self, node) -> None:
        if node.id in self._items:
            raise ValueError(f"{self.kind} registry: duplicate id '{node.id}'")
        self._items[node.id] = node

    def get(self, node_id: str):
        return self._items[node_id]

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._items

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def ids(self) -> Iterable[str]:
        return self._items.keys()

    def to_list(self) -> list[dict]:
        return [n.to_dict() for n in self._items.values()]

    def dump_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_list(), indent=2, sort_keys=False))


class TypeRegistry(Registry):
    def __init__(self):
        super().__init__("type")

    def add_type(self, name: str, description: str, parent: str | None = None) -> TypeDef:
        t = TypeDef(name=name, description=description, parent=parent)
        if name in self._items:
            raise ValueError(f"type registry: duplicate type '{name}'")
        self._items[name] = t
        return t

    def to_list(self) -> list[dict]:
        return [t.to_dict() for t in self._items.values()]


class ObjectRegistry(Registry):
    def __init__(self):
        super().__init__("object")

    def add_object(self, obj: Object) -> Object:
        self.add(obj)
        return obj


class TransformationRegistry(Registry):
    def __init__(self):
        super().__init__("transformation")

    def add_transformation(self, t: Transformation) -> Transformation:
        self.add(t)
        return t


class EquationRegistry(Registry):
    def __init__(self):
        super().__init__("equation")

    def add_equation(self, eq: Equation) -> Equation:
        self.add(eq)
        return eq


@dataclass
class MDCLRegistries:
    """Bundle of the four registries plus convenience status-matrix export."""
    types: TypeRegistry = field(default_factory=TypeRegistry)
    objects: ObjectRegistry = field(default_factory=ObjectRegistry)
    transformations: TransformationRegistry = field(default_factory=TransformationRegistry)
    equations: EquationRegistry = field(default_factory=EquationRegistry)

    def all_nodes(self):
        yield from self.objects
        yield from self.transformations
        yield from self.equations

    def status_matrix(self) -> list[dict]:
        rows = []
        for n in self.all_nodes():
            kind = type(n).__name__
            status = n.status.value if isinstance(n.status, Status) else n.status
            rows.append({"id": n.id, "kind": kind, "status": status,
                         "dependencies": list(n.dependencies)})
        return rows

    def dump_all(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        self.types.dump_json(out_dir / "type_registry.json")
        self.objects.dump_json(out_dir / "object_registry.json")
        self.transformations.dump_json(out_dir / "transformation_registry.json")
        self.equations.dump_json(out_dir / "equation_registry.json")
        (out_dir / "status_matrix.json").write_text(
            json.dumps(self.status_matrix(), indent=2)
        )
