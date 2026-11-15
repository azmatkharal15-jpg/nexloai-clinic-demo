"""Clinic configuration loading with safe path and enabled checks."""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
CLINICS_DIR = BASE / "clinics"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

class ClinicNotFound(Exception):
    pass

def load_clinic(slug: str, *, require_enabled: bool = True) -> dict:
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise ClinicNotFound(slug)
    path = CLINICS_DIR / slug / "config.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise ClinicNotFound(slug) from None
    if config.get("id") != slug or (require_enabled and not config.get("enabled", False)):
        raise ClinicNotFound(slug)
    for key in ("prompt_file", "knowledge_base_file"):
        candidate = (BASE / config[key]).resolve()
        if BASE.resolve() not in candidate.parents:
            raise ValueError(f"Unsafe path in clinic config: {key}")
        if not candidate.is_file():
            raise ValueError(f"Missing clinic file: {key}")
    return config

def public_config(config: dict) -> dict:
    return {k: config.get(k, "") for k in ("id", "name", "subtitle", "welcome", "primary_color", "accent_color", "phone", "email", "website")}
