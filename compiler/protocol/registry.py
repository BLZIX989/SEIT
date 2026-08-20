"""Registries for Chainlink/Protocol records -- same id -> record,
duplicate-guarded, `to_list()`/`dump_json()` shape as
`compiler/ir/registry.py::Registry`, kept separate because Chainlink/
Protocol are not IRNodes (they carry no independent Status).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from compiler.protocol.schema import Chainlink, Protocol


class ChainlinkRegistry:
    def __init__(self):
        self._items: dict[str, Chainlink] = {}

    def add(self, link: Chainlink) -> Chainlink:
        if link.chainlink_id in self._items:
            raise ValueError(f"chainlink registry: duplicate id '{link.chainlink_id}'")
        self._items[link.chainlink_id] = link
        return link

    def get(self, chainlink_id: str) -> Chainlink:
        return self._items[chainlink_id]

    def __contains__(self, chainlink_id: str) -> bool:
        return chainlink_id in self._items

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def ids(self) -> Iterable[str]:
        return self._items.keys()

    def to_list(self) -> list[dict]:
        return [c.to_dict() for c in self._items.values()]

    def dump_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_list(), indent=2))


class ProtocolRegistry:
    def __init__(self):
        self._items: dict[str, Protocol] = {}

    def add(self, protocol: Protocol) -> Protocol:
        if protocol.protocol_id in self._items:
            raise ValueError(f"protocol registry: duplicate id '{protocol.protocol_id}'")
        self._items[protocol.protocol_id] = protocol
        return protocol

    def get(self, protocol_id: str) -> Protocol:
        return self._items[protocol_id]

    def __contains__(self, protocol_id: str) -> bool:
        return protocol_id in self._items

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def to_list(self) -> list[dict]:
        return [p.to_dict() for p in self._items.values()]

    def dump_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_list(), indent=2))
