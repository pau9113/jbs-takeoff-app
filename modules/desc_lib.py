import json
import os

LIB_PATH = os.path.join("data", "desc_library.json")

def _load():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(LIB_PATH):
        return {}
    with open(LIB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(lib):
    os.makedirs("data", exist_ok=True)
    with open(LIB_PATH, "w", encoding="utf-8") as f:
        json.dump(lib, f, indent=2)

def make_key(style: str, height_ft: int, finish: str, category: str) -> str:
    # style example: "chainlink", "ornamental", etc.
    return f"{style}|{height_ft}|{finish}|{category}"

def get_suggestions(style: str, height_ft: int, finish: str, category: str):
    lib = _load()
    key = make_key(style, height_ft, finish, category)
    return lib.get(key, [])

def add_entry(style: str, height_ft: int, finish: str, category: str, description: str, max_entries=25):
    description = (description or "").strip()
    if not description:
        return

    lib = _load()
    key = make_key(style, height_ft, finish, category)

    existing = lib.get(key, [])
    # keep unique, newest first
    if description in existing:
        existing.remove(description)
    existing.insert(0, description)

    lib[key] = existing[:max_entries]
    _save(lib)
