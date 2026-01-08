from __future__ import annotations
from typing import Dict
from app.adapters.contract import BookmakerAdapter

_registry: Dict[str, BookmakerAdapter] = {}

def register(adapter: BookmakerAdapter) -> None:
    _registry[adapter.bookmaker] = adapter

def get(bookmaker: str) -> BookmakerAdapter:
    if bookmaker not in _registry:
        raise KeyError(f"unsupported bookmaker: {bookmaker}")
    return _registry[bookmaker]

def list_bookmakers() -> list[str]:
    return sorted(_registry.keys())
