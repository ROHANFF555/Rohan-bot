"""Phase 47: Source Attribution — configuration (single source of truth).

বটের প্রতিটা উত্তরে "তথ্যটা কোথা থেকে এলো" (Groq API / Browser Search / Database /
Hybrid) দেখানোর ফিচারটার সব সেটিংস এখানে। `main.py` এই ফাইলটা import করে, তাই
কোনো কমান্ডের badge চালু/বন্ধ বা ফরম্যাট বদলাতে হলে শুধু এখানে (অথবা নিচের
environment variable দিয়ে) বদলালেই হবে — handler কোডে হাত দিতে হয় না।

Environment overrides (Render/Replit Secrets):
    SOURCE_ATTRIBUTION_ENABLED             "0"/"false"/"no" দিলে পুরো ফিচার বন্ধ
    SOURCE_ATTRIBUTION_FORMAT              minimal | compact | full | detailed
    SOURCE_ATTRIBUTION_LANG                bn (ডিফল্ট) | en
    SOURCE_ATTRIBUTION_DISABLED_COMMANDS   কমা দিয়ে কমান্ডের নাম, যেগুলোর badge বন্ধ হবে
    SOURCE_ATTRIBUTION_ENABLED_COMMANDS    কমা দিয়ে কমান্ডের নাম, যেগুলো ডিফল্টে বন্ধ কিন্তু চালু করতে হবে
"""

from __future__ import annotations

import os
from typing import Any, Dict

# এই ফিচারের নিজস্ব সংস্করণ — লগ/ডায়াগনস্টিকে দেখানোর জন্য।
SOURCE_ATTRIBUTION_VERSION = "1.0.0"

#: ব্যাজের সমর্থিত ফরম্যাট।
SUPPORTED_BADGE_FORMATS = ("minimal", "compact", "full", "detailed")

#: ডিফল্ট ফরম্যাট — ছোট, তাই সাধারণ উত্তরগুলো clutter করে না।
DEFAULT_BADGE_FORMAT = "compact"

#: ডিফল্ট UI ভাষা।
DEFAULT_BADGE_LANG = "bn"

#: সোর্স ধরনভেদে ডিফল্ট confidence (0.0 – 1.0)। কলার নিজের মান দিলে সেটাই ব্যবহার হয়।
DEFAULT_CONFIDENCE: Dict[str, float] = {
    "groq": 0.90,  # LLM-এর তৈরি লেখা — ভালো, কিন্তু verify করা নয়
    "browser": 0.85,  # লাইভ ওয়েব সোর্স, তবে সার্চ রেজাল্ট
    "database": 0.90,  # নিজের Knowledge/Pattern Engine — আগে যাচাই হয়ে সেভ হয়েছে
    "hybrid": 0.88,  # একাধিক সোর্স মিলে তৈরি
}

#: প্রতিটা কমান্ডের জন্য আলাদা সেটিংস — enable/disable + ফরম্যাট।
#: এখানে নেই এমন কমান্ড `format_with_source(..., command=...)` দিলে গ্লোবাল
#: ডিফল্ট (চালু, DEFAULT_BADGE_FORMAT) পাবে।
COMMAND_SETTINGS: Dict[str, Dict[str, Any]] = {
    # /search — ইচ্ছে করেই পুরো বিস্তারিত ব্যাজ: এটাই ওয়েব-সোর্স দেখানোর মূল কমান্ড।
    "search": {"enabled": True, "format": "full"},
    # সাধারণ চ্যাট — ছোট ব্যাজ, প্রতি মেসেজে বড় বক্স বিরক্তিকর হতো।
    "chat": {"enabled": True, "format": "compact"},
    "joke": {"enabled": True, "format": "compact"},
    "quote": {"enabled": True, "format": "compact"},
    "translate": {"enabled": True, "format": "compact"},
    "grammar": {"enabled": True, "format": "compact"},
    "rewrite": {"enabled": True, "format": "compact"},
    "tone": {"enabled": True, "format": "compact"},
    "summarize": {"enabled": True, "format": "compact"},
    # /askpdf ও ডকুমেন্ট-সারসংক্ষেপ — একই নিয়ম।
    "askpdf": {"enabled": True, "format": "compact"},
}

#: Confidence সীমা (spec অনুযায়ী): 🟢 High ৮৫–১০০%, 🟡 Medium ৬০–৮৫%, 🔴 Low < ৬০%।
CONFIDENCE_HIGH_MIN = 0.85
CONFIDENCE_MEDIUM_MIN = 0.60

_TRUTHY = {"1", "true", "yes", "on", "y"}
_FALSY = {"0", "false", "no", "off", "n", ""}


def env_bool(name: str, default: bool) -> bool:
    """Environment variable থেকে bool পড়ে; অচেনা মান এলে `default`-ই থাকে।"""
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in _TRUTHY:
        return True
    if value in _FALSY:
        return False
    return default


def env_choice(name: str, choices, default: str) -> str:
    """Environment variable থেকে শুধু বৈধ মান নেয়; অন্য কিছু লেখা থাকলে `default`।"""
    raw = (os.getenv(name) or "").strip().lower()
    return raw if raw in choices else default


def _command_list(name: str) -> set:
    """কমা-বিচ্ছিন্ন কমান্ডের তালিকা পড়ে lowercase set হিসেবে ফেরত দেয়।"""
    raw = os.getenv(name) or ""
    return {item.strip().lower().lstrip("/") for item in raw.split(",") if item.strip()}


def load_settings() -> Dict[str, Any]:
    """কমান্ড-সেটিংস + environment override মিলিয়ে চূড়ান্ত কনফিগ dict বানায়।

    Returns:
        dict: ``{"enabled": bool, "format": str, "lang": str, "commands": {...},
        "confidence": {...}}`` — `commands`-এর ভেতরে প্রতিটা কমান্ডের
        ``{"enabled": bool, "format": str}`` থাকে।
    """
    commands: Dict[str, Dict[str, Any]] = {
        name: dict(settings) for name, settings in COMMAND_SETTINGS.items()
    }

    disabled = _command_list("SOURCE_ATTRIBUTION_DISABLED_COMMANDS")
    for name in disabled:
        commands.setdefault(name, {"enabled": True, "format": DEFAULT_BADGE_FORMAT})
        commands[name]["enabled"] = False

    for name in _command_list("SOURCE_ATTRIBUTION_ENABLED_COMMANDS"):
        commands.setdefault(name, {"enabled": True, "format": DEFAULT_BADGE_FORMAT})
        commands[name]["enabled"] = True

    return {
        "enabled": env_bool("SOURCE_ATTRIBUTION_ENABLED", True),
        "format": env_choice(
            "SOURCE_ATTRIBUTION_FORMAT", SUPPORTED_BADGE_FORMATS, DEFAULT_BADGE_FORMAT
        ),
        "lang": (os.getenv("SOURCE_ATTRIBUTION_LANG") or DEFAULT_BADGE_LANG)
        .strip()
        .lower()
        or DEFAULT_BADGE_LANG,
        "commands": commands,
        "confidence": dict(DEFAULT_CONFIDENCE),
    }


def resolve_command_settings(
    command: str | None, settings: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """একটা কমান্ডের কার্যকর সেটিংস ফেরত দেয় (কমান্ড-specific না থাকলে গ্লোবাল ডিফল্ট)।

    Args:
        command: কমান্ডের নাম, স্ল্যাশসহ বা স্ল্যাশ ছাড়া দুটোই চলে (``"search"``/``"/search"``)।
        settings: `load_settings()`-এর ফলাফল; না দিলে নিজেই লোড করে।

    Returns:
        dict: ``{"enabled": bool, "format": str}``।
    """
    settings = settings or load_settings()
    key = (command or "").strip().lower().lstrip("/")
    configured = settings.get("commands", {}).get(key)
    if configured is None:
        return {"enabled": True, "format": settings.get("format", DEFAULT_BADGE_FORMAT)}
    return {
        "enabled": bool(configured.get("enabled", True)),
        "format": configured.get("format")
        or settings.get("format", DEFAULT_BADGE_FORMAT),
    }
