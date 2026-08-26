"""Phase 2 — Data Source Attribution ফিচারের টেস্ট।

তিন অংশ:

  1. **Unit** — `rohan_bot/utils/source_tracker.py` ও `rohan_bot/config.py` সরাসরি import
     করে (এগুলো Telegram/AI/DB থেকে স্বাধীন): DataSource enum, coerce_source,
     confidence level/percent, SourceMetadata (url/secondary/cache/breakdown/timestamp),
     চারটে ব্যাজ ফরম্যাট (minimal/compact/full/detailed), বাংলা-ইংরেজি লেবেল,
     to_dict/from_dict, browse/decision রূপান্তর, `format_with_source`, env override।

  2. **Integration (handlers)** — আসল main.py কপি করে চালিয়ে দেখা হয় প্রতিটা হ্যান্ডলার
     (chat/joke/quote/translate/grammar/rewrite/tone/summarize) **DB → Browser → API**
     priority মেনে চলছে কিনা, এবং সোর্স-ব্যাজ সঠিক উৎস দেখাচ্ছে কিনা।

  3. **Integration (browse layer)** — DuckDuckGo/Wikipedia লেয়ার + স্বয়ংক্রিয়
     (automatic) Browse Search (`_automatic_browse_answer`) — কোনো আলাদা /search কমান্ড
     ছাড়াই — এর ফেক-HTTP টেস্ট।

চালানো যায়:
    python3 tests/test_source_attribution.py
    python3 -m unittest tests.test_source_attribution -v
    python3 -m pytest tests/test_source_attribution.py
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import os
import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import httpx

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from rohan_bot import config as attribution_config  # noqa: E402
from rohan_bot.utils import source_tracker as st  # noqa: E402

ADMIN_ID = 111
USER_ID = 770001


# ---------------------------------------------------------------------------
# হালকা ফেক Telegram অবজেক্ট
# ---------------------------------------------------------------------------
class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id
        self.first_name = "Test"
        self.username = "test_user"


class FakeChat:
    type = "private"
    id = 1


class _SentMessage:
    def __init__(self, sink: list):
        self._sink = sink

    async def edit_text(self, text: str, **_kw):
        self._sink.append(text)

    async def delete(self):
        return None


class FakeMessage:
    def __init__(self, user_id: int, text: str = ""):
        self.from_user = FakeUser(user_id)
        self.reply_to_message = None
        self.text = text
        self.sent: list[str] = []

    async def reply_text(self, text: str, **_kwargs):
        self.sent.append(text)
        return _SentMessage(self.sent)

    async def delete(self):
        return None


class FakeUpdate:
    def __init__(self, user_id: int, text: str = ""):
        self.effective_user = FakeUser(user_id)
        self.effective_chat = FakeChat()
        self.message = FakeMessage(user_id, text)
        self.effective_message = self.message


class FakeBot:
    username = "test_bot"


class FakeContext:
    def __init__(self, args=None):
        self.bot = FakeBot()
        self.args = list(args or [])
        self.user_data: dict = {}
        self.bot_data: dict = {}


def run(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# ফেক HTTP লেয়ার — DuckDuckGo/Wikipedia কল আটকে নিয়ন্ত্রিত উত্তর দেয়
# (automatic Browse Search লেয়ারের integration টেস্টের জন্য)।
# ---------------------------------------------------------------------------
class FakeResponse:
    def __init__(self, status_code: int = 200, payload=None, broken_json: bool = False):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self._broken = broken_json

    def json(self):
        if self._broken:
            raise ValueError("Expecting value: line 1 column 1 (char 0)")
        return self._payload


class FakeHTTPClient:
    DDG_URL = "api.duckduckgo.com"
    WIKI_API = "/w/api.php"
    WIKI_SUMMARY = "/api/rest_v1/page/summary/"

    def __init__(self, ddg=None, wiki_search=None, wiki_summary=None):
        self.ddg = ddg
        self.wiki_search = wiki_search
        self.wiki_summary = wiki_summary
        self.calls: list = []

    def _route(self, url: str, params):
        if self.DDG_URL in url:
            return self.ddg
        if self.WIKI_SUMMARY in url:
            return self.wiki_summary
        if self.WIKI_API in url or (params or {}).get("action") == "opensearch":
            return self.wiki_search
        return FakeResponse(404, {})

    async def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": dict(params or {}), "timeout": timeout})
        entry = self._route(url, params)
        if entry is None:
            return FakeResponse(404, {})
        if callable(entry):
            entry = entry(url, params)
        if isinstance(entry, Exception):
            raise entry
        if asyncio.iscoroutine(entry):
            entry = await entry
        return entry

    def urls(self) -> list:
        return [call["url"] for call in self.calls]

    def hit(self, needle: str) -> bool:
        return any(needle in call["url"] for call in self.calls)

    def query_sent(self, needle: str = DDG_URL) -> str:
        for call in self.calls:
            if needle in call["url"]:
                return call["params"].get("q") or call["params"].get("search") or ""
        return ""


def ddg_ok(text="ঢাকা বাংলাদেশের রাজধানী ও বৃহত্তম শহর।", source="Wikipedia",
           url="https://bn.wikipedia.org/wiki/ঢাকা"):
    return FakeResponse(
        200, {"AbstractText": text, "AbstractSource": source, "AbstractURL": url}
    )


def ddg_empty():
    return FakeResponse(
        200, {"AbstractText": "", "Answer": "", "Definition": "", "RelatedTopics": []}
    )


def ddg_answer(value="42"):
    return FakeResponse(200, {"AbstractText": "", "Answer": value})


def ddg_related(text="সংশ্লিষ্ট টপিক থেকে পাওয়া তথ্য।"):
    return FakeResponse(200, {"AbstractText": "", "RelatedTopics": [{"Text": text}]})


def wiki_titles(title="ঢাকা"):
    return FakeResponse(
        200, [title, [title], ["https://bn.wikipedia.org/wiki/ঢাকা"], [""]]
    )


def wiki_no_titles():
    return FakeResponse(200, ["", [], [], []])


def wiki_summary(extract="ঢাকা বাংলাদেশের রাজধানী।", url="https://bn.wikipedia.org/wiki/ঢাকা"):
    return FakeResponse(
        200, {"extract": extract, "content_urls": {"desktop": {"page": url}}}
    )


# ===========================================================================
# 1. Unit tests
# ===========================================================================
class DataSourceEnumTests(unittest.TestCase):
    def test_enum_has_four_sources(self):
        self.assertEqual(
            {m.name for m in st.DataSource}, {"GROQ", "BROWSER", "DATABASE", "HYBRID"}
        )

    def test_enum_display_values(self):
        self.assertEqual(st.DataSource.GROQ.value, "🔵 Groq API")
        self.assertEqual(st.DataSource.BROWSER.value, "🌐 Browser Search")
        self.assertEqual(st.DataSource.DATABASE.value, "💾 Database")
        self.assertEqual(st.DataSource.HYBRID.value, "🔄 Hybrid")

    def test_bengali_labels(self):
        self.assertEqual(
            st.SOURCE_BN_LABELS[st.DataSource.BROWSER], "🌐 ব্রাউজার সার্চ"
        )
        self.assertEqual(st.SOURCE_BN_LABELS[st.DataSource.DATABASE], "💾 ডাটাবেজ")
        self.assertEqual(st.SOURCE_BN_LABELS[st.DataSource.HYBRID], "🔄 সম্মিলিত")
        self.assertEqual(st.SOURCE_BN_LABELS[st.DataSource.GROQ], "🔵 Groq API")
        self.assertEqual(len(st.SOURCE_BN_LABELS), 4)

    def test_coerce_source_accepts_many_shapes(self):
        cases = {
            "groq": st.DataSource.GROQ,
            "ai": st.DataSource.GROQ,
            "GROQ": st.DataSource.GROQ,
            "🔵 Groq API": st.DataSource.GROQ,
            "browser": st.DataSource.BROWSER,
            "web": st.DataSource.BROWSER,
            "search": st.DataSource.BROWSER,
            "🌐 Browser Search": st.DataSource.BROWSER,
            "database": st.DataSource.DATABASE,
            "db": st.DataSource.DATABASE,
            "brain": st.DataSource.DATABASE,
            "hybrid": st.DataSource.HYBRID,
            "mixed": st.DataSource.HYBRID,
            st.DataSource.BROWSER: st.DataSource.BROWSER,
        }
        for raw, expected in cases.items():
            self.assertIs(st.coerce_source(raw), expected, msg=f"input={raw!r}")

    def test_coerce_source_rejects_unknown(self):
        for bad in ("wikipedia", "", None, 123):
            with self.assertRaises(ValueError):
                st.coerce_source(bad)

    def test_coerce_source_finds_source_by_emoji(self):
        self.assertIs(st.coerce_source("উত্তর এসেছে 🌐 থেকে"), st.DataSource.BROWSER)


class ConfidenceTests(unittest.TestCase):
    def test_high_medium_low_boundaries(self):
        self.assertEqual(st.confidence_level(1.00)[0], "🟢")
        self.assertEqual(st.confidence_level(0.85)[0], "🟢")
        self.assertEqual(st.confidence_level(0.8499)[0], "🟡")
        self.assertEqual(st.confidence_level(0.60)[0], "🟡")
        self.assertEqual(st.confidence_level(0.5999)[0], "🔴")
        self.assertEqual(st.confidence_level(0.0)[0], "🔴")

    def test_confidence_labels_are_localized(self):
        self.assertEqual(st.confidence_level(0.95, "bn"), ("🟢", "উচ্চ"))
        self.assertEqual(st.confidence_level(0.95, "en"), ("🟢", "High"))
        self.assertEqual(st.confidence_level(0.70, "en"), ("🟡", "Medium"))
        self.assertEqual(st.confidence_level(0.10, "en"), ("🔴", "Low"))

    def test_confidence_handles_bad_input(self):
        self.assertEqual(st.confidence_level("না")[0], "🔴")
        self.assertEqual(st.confidence_level(None)[0], "🔴")
        self.assertEqual(st.confidence_level(float("nan"))[0], "🔴")
        self.assertEqual(st.confidence_level(5.0)[0], "🟢")  # সীমার বাইরে → clip
        self.assertEqual(st.confidence_level(-1.0)[0], "🔴")

    def test_confidence_percent_clamps(self):
        self.assertEqual(st.confidence_percent(0.95), 95)
        self.assertEqual(st.confidence_percent(0.855), 86)  # round
        self.assertEqual(st.confidence_percent(2.0), 100)
        self.assertEqual(st.confidence_percent(-0.5), 0)
        self.assertEqual(st.confidence_percent("x"), 0)


class SourceMetadataTests(unittest.TestCase):
    def test_default_confidence_per_source(self):
        self.assertAlmostEqual(
            st.SourceMetadata(st.DataSource.GROQ).confidence_score,
            attribution_config.DEFAULT_CONFIDENCE["groq"],
        )
        self.assertAlmostEqual(
            st.SourceMetadata(st.DataSource.BROWSER).confidence_score,
            attribution_config.DEFAULT_CONFIDENCE["browser"],
        )

    def test_confidence_is_clamped_and_bad_value_replaced(self):
        self.assertEqual(
            st.SourceMetadata("groq", confidence_score=1.9).confidence_score, 1.0
        )
        self.assertEqual(
            st.SourceMetadata("groq", confidence_score=-3).confidence_score, 0.0
        )
        self.assertEqual(
            st.SourceMetadata("groq", confidence_score="oops").confidence_score, 0.8
        )

    def test_timestamp_defaults_to_utc_now_and_accepts_naive(self):
        before = datetime.now(timezone.utc)
        meta = st.SourceMetadata("groq")
        after = datetime.now(timezone.utc)
        self.assertIsNotNone(meta.timestamp.tzinfo)
        self.assertGreaterEqual(meta.timestamp, before.replace(microsecond=0))
        self.assertLessEqual(meta.timestamp, after)

        naive = datetime(2026, 1, 2, 3, 4, 5)
        self.assertEqual(
            st.SourceMetadata("groq", timestamp=naive).timestamp,
            datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        )

    def test_timestamp_rejects_non_datetime(self):
        with self.assertRaises(TypeError):
            st.SourceMetadata("groq", timestamp="2026-08-26")

    def test_add_url_dedupes_and_skips_empty(self):
        meta = st.SourceMetadata("browser")
        meta.add_url("https://a.example")
        meta.add_url("https://a.example")
        meta.add_url("   ")
        meta.add_url(None)  # type: ignore[arg-type]
        meta.add_urls(["https://b.example", "https://a.example"])
        self.assertEqual(meta.urls, ["https://a.example", "https://b.example"])

    def test_add_secondary_ignores_duplicate_primary_and_hybrid(self):
        meta = st.SourceMetadata("browser")
        meta.add_secondary("browser")  # প্রাইমারির সাথে মিল → বাদ
        meta.add_secondary("hybrid")  # HYBRID সেকেন্ডারি হতে পারে না
        meta.add_secondary("groq")
        meta.add_secondary("groq")  # ডুপ্লিকেট → বাদ
        self.assertEqual(meta.secondary_sources, [st.DataSource.GROQ])

    def test_hybrid_detection(self):
        single = st.SourceMetadata("groq")
        self.assertFalse(single.is_hybrid)
        self.assertIs(single.effective_source, st.DataSource.GROQ)

        meta = st.SourceMetadata("browser", secondary_sources=["groq"])
        self.assertTrue(meta.is_hybrid)
        self.assertIs(meta.effective_source, st.DataSource.HYBRID)
        self.assertEqual(meta.all_sources, [st.DataSource.BROWSER, st.DataSource.GROQ])

    def test_checked_sources_dedupe(self):
        meta = st.SourceMetadata(
            "browser", checked_sources=["DuckDuckGo Instant Answer", "", "  "]
        )
        meta.add_checked_source("Wikipedia (bn)")
        meta.add_checked_source("Wikipedia (bn)")
        self.assertEqual(
            meta.checked_sources, ["DuckDuckGo Instant Answer", "Wikipedia (bn)"]
        )

    def test_badge_minimal_is_just_the_source(self):
        self.assertEqual(st.SourceMetadata("groq").to_badge("minimal"), "🔵 Groq API")
        self.assertEqual(
            st.SourceMetadata("browser", secondary_sources=["groq"]).to_badge(
                "minimal", "bn"
            ),
            "🔄 সম্মিলিত",
        )

    def test_badge_compact_bengali_and_english(self):
        meta = st.SourceMetadata(
            "browser", confidence_score=0.85, secondary_sources=["groq"]
        )
        meta.add_url("https://example.com")
        bn = meta.to_badge("compact", "bn")
        en = meta.to_badge("compact", "en")

        self.assertTrue(bn.startswith("_উৎস: 🌐 ব্রাউজার সার্চ | 🔵 Groq API_"))
        self.assertIn("🔗 1 লিংক", bn)
        self.assertIn("নির্ভুলতা: 🟢 উচ্চ", bn)
        self.assertIn("UTC", bn)

        self.assertTrue(en.startswith("_Source: 🌐 Browser Search | 🔵 Groq API_"))
        self.assertIn("🔗 1 links", en)
        self.assertIn("Confidence: 🟢 High", en)

    def test_badge_compact_marks_cache_hit(self):
        badge = st.SourceMetadata("database", cache_hit=True).to_badge("compact", "bn")
        self.assertIn("💾 ক্যাশ", badge)
        self.assertNotIn(
            "💾 ক্যাশ", st.SourceMetadata("database").to_badge("compact", "bn")
        )

    def test_badge_full_contains_all_rows(self):
        meta = st.SourceMetadata(
            "browser",
            confidence_score=0.85,
            secondary_sources=["groq"],
            urls=["https://bn.wikipedia.org/wiki/ঢাকা"],
            checked_sources=["DuckDuckGo Instant Answer", "Wikipedia (bn)"],
            note="কাঁচা তথ্য AI দিয়ে গুছানো",
        )
        bn = meta.to_badge("full", "bn")
        for expected in (
            "📊 উৎস তথ্য",
            "মূল উৎস: 🌐 ব্রাউজার সার্চ",
            "অন্য উৎস: 🔵 Groq API",
            "ধরন: 🔄 সম্মিলিত",
            "চেক করা হয়েছে: DuckDuckGo Instant Answer → Wikipedia (bn)",
            "নোট: কাঁচা তথ্য AI দিয়ে গুছানো",
            "নির্ভুলতা: 🟢 উচ্চ (85%)",
            "🔗 মূল সোর্স:",
            "https://bn.wikipedia.org/wiki/ঢাকা",
            "[আরও জানুন] [যাচাই করুন] [সমস্যা জানান]",
            st.RULE,
        ):
            self.assertIn(expected, bn, msg=f"missing: {expected}")

        en = meta.to_badge("full", "en")
        for expected in (
            "📊 Source Information",
            "Primary Source: 🌐 Browser Search",
            "Also Used: 🔵 Groq API",
            "Result Type: 🔄 Hybrid",
            "Timestamp:",
            "Confidence: 🟢 High (85%)",
            "[Learn More] [Verify] [Report Issue]",
        ):
            self.assertIn(expected, en, msg=f"missing: {expected}")

    def test_badge_detailed_shows_breakdown(self):
        meta = st.SourceMetadata(
            "groq",
            confidence_score=0.7,
            secondary_sources=["browser", "database"],
            breakdown={"groq": 0.5, "browser": 0.3, "database": 0.2},
        )
        badge = meta.to_badge("detailed", "en")
        self.assertIn("📊 Data Sources Breakdown:", badge)
        self.assertIn("50% - 🔵 Groq API", badge)
        self.assertIn("30% - 🌐 Browser Search", badge)
        self.assertIn("20% - 💾 Database", badge)
        self.assertIn("Accuracy Note", badge)
        self.assertIn("🟡 Medium", badge)  # 0.70 → মাঝারি (৬০–৮৫%)
        self.assertIn("none recorded", badge)

    def test_badge_detailed_auto_breakdown_when_not_given(self):
        meta = st.SourceMetadata("browser", secondary_sources=["groq"])
        badge = meta.to_badge("detailed", "en")
        self.assertIn("70% - 🌐 Browser Search", badge)
        self.assertIn("30% - 🔵 Groq API", badge)

    def test_unknown_format_falls_back_to_compact(self):
        meta = st.SourceMetadata("groq")
        self.assertEqual(meta.to_badge("no-such-format"), meta.to_badge("compact"))
        self.assertEqual(meta.to_badge(None), meta.to_badge("compact"))

    def test_to_dict_and_back(self):
        meta = st.SourceMetadata(
            "browser",
            confidence_score=0.85,
            secondary_sources=["groq"],
            urls=["https://example.com"],
            cache_hit=True,
            note="নোট",
            checked_sources=["DuckDuckGo Instant Answer"],
            query="প্রশ্ন",
        )
        payload = meta.to_dict()
        self.assertEqual(payload["primary_source"], "BROWSER")
        self.assertEqual(payload["effective_source"], "HYBRID")
        self.assertEqual(payload["secondary_sources"], ["GROQ"])
        self.assertTrue(payload["cache_hit"])
        self.assertEqual(payload["query"], "প্রশ্ন")

        restored = st.SourceMetadata.from_dict(payload)
        self.assertIs(restored.primary_source, st.DataSource.BROWSER)
        self.assertEqual(restored.urls, ["https://example.com"])
        self.assertEqual(restored.checked_sources, ["DuckDuckGo Instant Answer"])
        self.assertAlmostEqual(restored.confidence_score, 0.85, places=3)
        self.assertEqual(
            restored.to_badge("compact", "en"), meta.to_badge("compact", "en")
        )

    def test_from_dict_tolerates_empty_payload(self):
        restored = st.SourceMetadata.from_dict({})
        self.assertIs(restored.primary_source, st.DataSource.HYBRID)

    def test_badge_overhead_is_small(self):
        """Spec লক্ষ্য: source tracking যেন ১০ ms-এর বেশি overhead না যোগ করে।"""
        meta = st.SourceMetadata(
            "browser", secondary_sources=["groq"], urls=["https://example.com"]
        )
        started = time.perf_counter()
        for _ in range(500):
            st.format_with_source("উত্তর", meta, command="chat")
        per_call_ms = (time.perf_counter() - started) / 500 * 1000
        self.assertLess(per_call_ms, 10.0, f"per-call overhead {per_call_ms:.3f} ms")


class BadgeCoverageTests(unittest.TestCase):
    """ব্যাজ/সিরিয়ালাইজেশনের বাকি শাখাগুলো — edge case + ভাষা-সংমিশ্রণ।"""

    def test_bad_breakdown_entries_are_skipped(self):
        meta = st.SourceMetadata(
            "groq", breakdown={"browser": 0.3, "wikipedia": 0.5, "database": "abc"}
        )
        self.assertEqual(sorted(meta.breakdown), ["BROWSER"])
        self.assertAlmostEqual(meta.breakdown["BROWSER"], 0.3)

    def test_explicit_hybrid_primary(self):
        meta = st.SourceMetadata("hybrid")
        self.assertIs(meta.effective_source, st.DataSource.HYBRID)
        self.assertFalse(meta.is_hybrid)  # সেকেন্ডারি নেই
        self.assertEqual(meta.to_badge("minimal", "en"), "🔄 Hybrid")

    def test_single_source_detailed_badge_is_100_percent(self):
        badge = st.SourceMetadata("groq").to_badge("detailed", "en")
        self.assertIn("100% - 🔵 Groq API", badge)

    def test_full_badge_shows_cache_row(self):
        bn = st.SourceMetadata("database", cache_hit=True).to_badge("full", "bn")
        en = st.SourceMetadata("database", cache_hit=True).to_badge("full", "en")
        self.assertIn("ক্যাশ: হিট 💾", bn)
        self.assertIn("Cache: hit 💾", en)

    def test_detailed_badge_bengali_with_urls(self):
        meta = st.SourceMetadata(
            "browser", confidence_score=0.9, urls=["https://bn.wikipedia.org/wiki/ঢাকা"]
        )
        badge = meta.to_badge("detailed", "bn")
        self.assertIn("📊 উৎসের ভাঙন:", badge)
        self.assertIn("⚠️ নির্ভুলতা নোট: তথ্যটি", badge)
        self.assertIn("🟢 উচ্চ", badge)
        self.assertIn("🔗 মূল সোর্স:", badge)
        self.assertIn("https://bn.wikipedia.org/wiki/ঢাকা", badge)

    def test_detailed_badge_bengali_without_urls(self):
        badge = st.SourceMetadata("database").to_badge("detailed", "bn")
        self.assertIn("🔗 মূল সোর্স: সংরক্ষিত নেই", badge)

    def test_detailed_badge_caps_url_list(self):
        meta = st.SourceMetadata(
            "browser", urls=[f"https://example.com/{i}" for i in range(20)]
        )
        badge = meta.to_badge("detailed", "en")
        self.assertEqual(badge.count("https://example.com/"), 8)

    def test_from_dict_accepts_datetime_object(self):
        stamp = datetime(2026, 8, 26, 10, 0, 0, tzinfo=timezone.utc)
        meta = st.SourceMetadata.from_dict(
            {"primary_source": "GROQ", "timestamp": stamp}
        )
        self.assertEqual(meta.timestamp, stamp)

    def test_from_dict_ignores_bad_timestamp_string(self):
        meta = st.SourceMetadata.from_dict(
            {"primary_source": "GROQ", "timestamp": "not-a-date"}
        )
        self.assertIsNotNone(meta.timestamp)
        self.assertNotEqual(meta.timestamp.year, 1900)

    def test_from_dict_ignores_unknown_source_key_in_breakdown(self):
        meta = st.SourceMetadata.from_dict(
            {"primary_source": "BROWSER", "breakdown": {"nope": 0.5, "groq": 0.5}}
        )
        self.assertEqual(sorted(meta.breakdown), ["GROQ"])

    def test_confidence_percent_and_level_bad_input(self):
        self.assertEqual(st.confidence_percent(None), 0)
        self.assertEqual(st.confidence_percent(float("nan")), 0)
        self.assertEqual(st.confidence_level({"a": 1})[0], "🔴")

    def test_repr_is_informative(self):
        text = repr(
            st.SourceMetadata("browser", secondary_sources=["groq"], urls=["https://a"])
        )
        self.assertIn("SourceMetadata(", text)
        self.assertIn("BROWSER", text)

    def test_add_secondary_accepts_enum_and_string_mixed(self):
        meta = st.SourceMetadata(
            "groq", secondary_sources=[st.DataSource.BROWSER, "database", "GROQ"]
        )
        self.assertEqual(
            meta.secondary_sources, [st.DataSource.BROWSER, st.DataSource.DATABASE]
        )

    def test_add_secondary_rejects_unknown_source(self):
        meta = st.SourceMetadata("groq")
        with self.assertRaises(ValueError):
            meta.add_secondary("wikipedia")

    def test_format_with_source_lang_falls_back_to_english(self):
        """bn ছাড়া অন্য ভাষা কোড (hi/ar/es) দিলে ব্যাজ ইংরেজিতে যায়।"""
        settings = {
            "enabled": True,
            "format": "compact",
            "lang": "bn",
            "commands": {},
            "confidence": {},
        }
        out = st.format_with_source(
            "উত্তর", st.SourceMetadata("groq"), lang="hi", settings=settings
        )
        self.assertIn("_Source: 🔵 Groq API_", out)

    def test_format_with_source_uses_settings_lang_when_lang_missing(self):
        settings = {
            "enabled": True,
            "format": "compact",
            "lang": "en",
            "commands": {},
            "confidence": {},
        }
        out = st.format_with_source(
            "উত্তর", st.SourceMetadata("groq"), lang="", settings=settings
        )
        self.assertIn("_Source:", out)

    def test_all_supported_formats_are_known(self):
        meta = st.SourceMetadata("browser")
        for fmt in attribution_config.SUPPORTED_BADGE_FORMATS:
            self.assertTrue(meta.to_badge(fmt).strip(), msg=fmt)


class MetadataBuilderTests(unittest.TestCase):
    def test_build_metadata_shortcut(self):
        meta = st.build_metadata(
            "groq", confidence_score=0.95, urls=["https://a"], query="q"
        )
        self.assertIs(meta.primary_source, st.DataSource.GROQ)
        self.assertEqual(meta.confidence_score, 0.95)
        self.assertEqual(meta.urls, ["https://a"])

    def test_metadata_from_browse_result(self):
        found = {
            "text": "ঢাকা বাংলাদেশের রাজধানী।",
            "source": "Wikipedia",
            "url": "https://bn.wikipedia.org/wiki/ঢাকা",
            "tried_sources": ["DuckDuckGo Instant Answer", "Wikipedia (bn)"],
            "matched_source": "Wikipedia (bn)",
        }
        meta = st.metadata_from_browse_result(found, query="রাজধানী")
        self.assertIs(meta.primary_source, st.DataSource.BROWSER)
        self.assertFalse(meta.is_hybrid)
        self.assertEqual(meta.urls, ["https://bn.wikipedia.org/wiki/ঢাকা"])
        self.assertIn("Wikipedia (bn)", meta.checked_sources)

        hybrid = st.metadata_from_browse_result(found, organized_by_ai=True)
        self.assertTrue(hybrid.is_hybrid)
        self.assertIs(hybrid.effective_source, st.DataSource.HYBRID)
        self.assertIn("AI", hybrid.note)

    def test_metadata_from_browse_result_rejects_empty(self):
        self.assertIsNone(st.metadata_from_browse_result(None))
        self.assertIsNone(st.metadata_from_browse_result({}))
        self.assertIsNone(st.metadata_from_browse_result({"text": "   "}))

    def test_metadata_from_decision(self):
        meta = st.metadata_from_decision(
            {"strategy": "direct", "stage": "knowledge", "confidence": 0.93}, query="q"
        )
        self.assertIs(meta.primary_source, st.DataSource.DATABASE)
        self.assertTrue(meta.cache_hit)
        self.assertAlmostEqual(meta.confidence_score, 0.93)
        self.assertEqual(meta.note, "knowledge")

    def test_metadata_from_decision_ignores_non_direct(self):
        self.assertIsNone(st.metadata_from_decision(None))
        self.assertIsNone(st.metadata_from_decision({}))
        self.assertIsNone(
            st.metadata_from_decision({"strategy": "ai", "confidence": 0.9})
        )

    def test_metadata_from_decision_handles_bad_confidence(self):
        meta = st.metadata_from_decision(
            {"strategy": "direct", "confidence": "not-a-number"}
        )
        self.assertAlmostEqual(
            meta.confidence_score, attribution_config.DEFAULT_CONFIDENCE["database"]
        )


class FormatWithSourceTests(unittest.TestCase):
    SETTINGS = {
        "enabled": True,
        "format": "compact",
        "lang": "bn",
        "commands": {
            "detail": {"enabled": True, "format": "full"},
            "joke": {"enabled": True, "format": "compact"},
            "quiet": {"enabled": False, "format": "compact"},
        },
        "confidence": {},
    }

    def test_appends_compact_badge(self):
        out = st.format_with_source(
            "মূল উত্তর",
            st.SourceMetadata("groq"),
            command="joke",
            settings=self.SETTINGS,
        )
        self.assertTrue(out.startswith("মূল উত্তর\n\n_উৎস: 🔵 Groq API_"))

    def test_command_specific_format_is_used(self):
        out = st.format_with_source(
            "ফলাফল",
            st.SourceMetadata("browser"),
            command="detail",
            settings=self.SETTINGS,
        )
        self.assertIn("📊 উৎস তথ্য", out)

    def test_explicit_format_overrides_command_setting(self):
        out = st.format_with_source(
            "ফলাফল",
            st.SourceMetadata("browser"),
            format_type="minimal",
            command="detail",
            settings=self.SETTINGS,
        )
        self.assertEqual(
            out, "ফলাফল\n\n🌐 ব্রাউজার সার্চ"
        )  # "full" নয়, minimal-ই চলল

    def test_disabled_command_returns_text_unchanged(self):
        meta = st.SourceMetadata("groq")
        self.assertEqual(
            st.format_with_source(
                "শুধু উত্তর", meta, command="quiet", settings=self.SETTINGS
            ),
            "শুধু উত্তর",
        )

    def test_globally_disabled_returns_text_unchanged(self):
        settings = dict(self.SETTINGS, enabled=False)
        self.assertEqual(
            st.format_with_source(
                "শুধু উত্তর",
                st.SourceMetadata("groq"),
                command="joke",
                settings=settings,
            ),
            "শুধু উত্তর",
        )

    def test_none_metadata_returns_text(self):
        self.assertEqual(
            st.format_with_source(
                "শুধু উত্তর", None, command="joke", settings=self.SETTINGS
            ),
            "শুধু উত্তর",
        )

    def test_empty_text_returns_only_badge(self):
        out = st.format_with_source(
            "", st.SourceMetadata("groq"), command="joke", settings=self.SETTINGS
        )
        self.assertTrue(out.startswith("_উৎস: 🔵 Groq API_"))

    def test_language_switches_badge_language(self):
        bn = st.format_with_source(
            "উত্তর",
            st.SourceMetadata("database"),
            lang="bn",
            command="joke",
            settings=self.SETTINGS,
        )
        en = st.format_with_source(
            "উত্তর",
            st.SourceMetadata("database"),
            lang="en",
            command="joke",
            settings=self.SETTINGS,
        )
        self.assertIn("💾 ডাটাবেজ", bn)
        self.assertIn("💾 Database", en)
        self.assertIn("_Source:", en)

    def test_broken_metadata_never_breaks_the_answer(self):
        """ব্যাজ তৈরিতে exception এলেও মূল উত্তরটাই ফেরত যাবে (চ্যাট-ফ্লো ভাঙবে না)।"""

        class Boom:
            def to_badge(self, *args, **kwargs):
                raise RuntimeError("badge explosion")

        self.assertEqual(
            st.format_with_source(
                "মূল উত্তর", Boom(), command="joke", settings=self.SETTINGS
            ),
            "মূল উত্তর",
        )

    def test_empty_badge_returns_answer_only(self):
        """to_badge() খালি স্ট্রিং দিলেও শুধু মূল উত্তরটাই যাবে।"""

        class Silent:
            def to_badge(self, *args, **kwargs):
                return ""

        self.assertEqual(
            st.format_with_source(
                "মূল উত্তর", Silent(), command="joke", settings=self.SETTINGS
            ),
            "মূল উত্তর",
        )

    def test_unknown_command_uses_global_default(self):
        out = st.format_with_source(
            "উত্তর",
            st.SourceMetadata("groq"),
            command="brandnew",
            settings=self.SETTINGS,
        )
        self.assertIn("_উৎস: 🔵 Groq API_", out)


class ConfigOverrideTests(unittest.TestCase):
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=False):
            for key in (
                "SOURCE_ATTRIBUTION_ENABLED",
                "SOURCE_ATTRIBUTION_FORMAT",
                "SOURCE_ATTRIBUTION_DISABLED_COMMANDS",
                "SOURCE_ATTRIBUTION_ENABLED_COMMANDS",
            ):
                os.environ.pop(key, None)
            settings = attribution_config.load_settings()
        self.assertTrue(settings["enabled"])
        self.assertEqual(settings["format"], "compact")
        self.assertEqual(settings["lang"], "bn")
        self.assertTrue(settings["commands"]["chat"]["enabled"])
        self.assertEqual(settings["commands"]["chat"]["format"], "compact")

    def test_global_disable_via_env(self):
        with patch.dict(os.environ, {"SOURCE_ATTRIBUTION_ENABLED": "false"}):
            self.assertFalse(attribution_config.load_settings()["enabled"])

    def test_invalid_format_falls_back_to_default(self):
        with patch.dict(os.environ, {"SOURCE_ATTRIBUTION_FORMAT": "sparkly"}):
            self.assertEqual(attribution_config.load_settings()["format"], "compact")

    def test_valid_format_override(self):
        with patch.dict(os.environ, {"SOURCE_ATTRIBUTION_FORMAT": "detailed"}):
            self.assertEqual(attribution_config.load_settings()["format"], "detailed")

    def test_disable_and_enable_specific_commands(self):
        with patch.dict(
            os.environ,
            {
                "SOURCE_ATTRIBUTION_DISABLED_COMMANDS": "joke, /quote",
                "SOURCE_ATTRIBUTION_ENABLED_COMMANDS": "ocr",
            },
        ):
            settings = attribution_config.load_settings()
        self.assertFalse(settings["commands"]["joke"]["enabled"])
        self.assertFalse(
            settings["commands"]["quote"]["enabled"]
        )  # স্ল্যাশ নিজে থেকেই বাদ
        self.assertTrue(settings["commands"]["ocr"]["enabled"])
        self.assertTrue(settings["commands"]["chat"]["enabled"])

    def test_env_bool_parsing(self):
        for raw, expected in (
            ("1", True),
            ("true", True),
            ("YES", True),
            ("on", True),
            ("0", False),
            ("false", False),
            ("no", False),
            ("", False),
            ("maybe", True),
        ):
            with patch.dict(os.environ, {"SOME_FLAG": raw}):
                self.assertEqual(
                    attribution_config.env_bool("SOME_FLAG", True), expected, msg=raw
                )

    def test_resolve_command_settings_unknown_command(self):
        settings = attribution_config.load_settings()
        resolved = attribution_config.resolve_command_settings("never-seen", settings)
        self.assertTrue(resolved["enabled"])
        self.assertEqual(resolved["format"], settings["format"])

    def test_resolve_command_settings_accepts_slash(self):
        settings = attribution_config.load_settings()
        self.assertEqual(
            attribution_config.resolve_command_settings("/joke", settings),
            attribution_config.resolve_command_settings("joke", settings),
        )


# ===========================================================================
# 2. Integration tests (আসল main.py)
# ===========================================================================
class HandlerAttributionIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="rohan-attribution-test-")
        shutil.copyfile(
            os.path.join(REPO_ROOT, "main.py"), os.path.join(cls.workdir, "main.py")
        )
        shutil.copytree(
            os.path.join(REPO_ROOT, "rohan_bot"),
            os.path.join(cls.workdir, "rohan_bot"),
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", str(ADMIN_ID))
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        for key in (
            "SOURCE_ATTRIBUTION_ENABLED",
            "SOURCE_ATTRIBUTION_DISABLED_COMMANDS",
            "SOURCE_ATTRIBUTION_FORMAT",
            "SOURCE_ATTRIBUTION_LANG",
        ):
            os.environ.pop(key, None)

        logging.disable(logging.CRITICAL)
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)
        if cls.workdir not in sys.path:
            sys.path.insert(0, cls.workdir)

        module_name = "rohan_source_attribution_test_main"
        spec = importlib.util.spec_from_file_location(
            module_name, os.path.join(cls.workdir, "main.py")
        )
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        cls.main.register_user(USER_ID)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_source_attribution_test_main", None)
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    # ---------------- helpers ----------------
    def setUp(self):
        self.assertTrue(self.main.SOURCE_ATTRIBUTION_AVAILABLE)
        self.main.ai_response_cache._store.clear()

    def call(self, handler, args=None, user_id=USER_ID, message_text=""):
        """হ্যান্ডলার চালায় — ডিফল্টে Browse Search অফ (নেটওয়ার্ক-মুক্ত, deterministic)।"""
        update = FakeUpdate(user_id, message_text)
        ctx = FakeContext(args)
        with patch.object(self.main, "quota_guard", new=AsyncMock(return_value=True)), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ):
            run(handler(update, ctx))
        return update, "\n".join(update.message.sent)

    def call_raw(self, handler, args=None, user_id=USER_ID):
        """Browse Search নিজে নিয়ন্ত্রণ করতে চাইলে এই হেল্পার (auto-mock করে না)।"""
        update = FakeUpdate(user_id)
        ctx = FakeContext(args)
        with patch.object(self.main, "quota_guard", new=AsyncMock(return_value=True)):
            run(handler(update, ctx))
        return update, "\n".join(update.message.sent)

    def install_http(self, **routes) -> FakeHTTPClient:
        """main.py-এর `get_http_client()`-কে ফেক HTTP ক্লায়েন্ট দিয়ে প্রতিস্থাপন করে।"""
        client = FakeHTTPClient(**routes)
        patcher = patch.object(
            self.main, "get_http_client", new=AsyncMock(return_value=client)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        return client

    def browse(self, query: str, lang_hint: str = ""):
        return run(self.main.browse_web_search(query, lang_hint=lang_hint))

    # ---------------- /joke, /quote ----------------
    def test_joke_shows_groq_badge(self):
        with patch.object(
            self.main,
            "ask_ai",
            new=AsyncMock(return_value="প্রোগ্রামার কেন চাকরি ছাড়ল?"),
        ):
            _update, text = self.call(self.main.joke_command)
        self.assertIn("প্রোগ্রামার কেন চাকরি ছাড়ল?", text)
        self.assertIn("_উৎস: 🔵 Groq API_", text)
        self.assertIn("নির্ভুলতা: 🟢", text)

    def test_joke_failure_shows_no_badge(self):
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(side_effect=RuntimeError("AI down"))
        ):
            _update, text = self.call(self.main.joke_command)
        self.assertIn("জোক আনতে পারলাম না", text)
        self.assertNotIn("_উৎস:", text)  # এরর-মেসেজে ভুয়া উৎস দেখানো যাবে না

    def test_quote_shows_groq_badge(self):
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="চেষ্টা করে যাও।")
        ):
            _update, text = self.call(self.main.quote_command)
        self.assertIn("চেষ্টা করে যাও।", text)
        self.assertIn("🔵 Groq API", text)

    # ---------------- cache-aware commands ----------------
    def test_translate_cache_miss_shows_groq(self):
        with patch.object(self.main, "ask_ai", new=AsyncMock(return_value="I am fine")):
            _update, text = self.call(
                self.main.translate_command, ["english", "আমি", "ভালো", "আছি"]
            )
        self.assertIn("I am fine", text)
        self.assertIn("🔵 Groq API", text)
        self.assertNotIn("💾 ডাটাবেজ", text)

    def test_translate_cache_hit_shows_database(self):
        system_prompt = (
            "তুমি একজন অনুবাদক। ইউজারের লেখাটা english ভাষায় অনুবাদ করো। "
            "শুধু অনুবাদটাই লিখবে, অন্য কিছু লিখবে না।"
        )
        run(
            self.main.ai_response_cache.set(
                system_prompt, "আমি ভালো আছি", "cached translation"
            )
        )
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="cached translation")
        ):
            _update, text = self.call(
                self.main.translate_command, ["english", "আমি", "ভালো", "আছি"]
            )
        self.assertIn("💾 ডাটাবেজ", text)
        self.assertIn("💾 ক্যাশ", text)
        self.assertNotIn("🔵 Groq API", text)

    def test_summarize_shows_source_badge(self):
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="সংক্ষিপ্ত সারমর্ম।")
        ):
            _update, text = self.call(self.main.summarize_command, ["বড়", "লেখা"])
        self.assertIn("সংক্ষিপ্ত সারমর্ম।", text)
        self.assertIn("_উৎস:", text)

    def test_grammar_shows_source_badge(self):
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="ঠিক করা লেখা।")
        ):
            _update, text = self.call(self.main.grammar_command, ["ভুল", "লেখা"])
        self.assertIn("ঠিক করা লেখা।", text)
        self.assertIn("🔵 Groq API", text)

    def test_usage_error_message_has_no_badge(self):
        _update, text = self.call(self.main.grammar_command, [])
        self.assertIn("/grammar", text)
        self.assertNotIn("_উৎস:", text)

    def test_rewrite_shows_source_badge(self):
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="নতুন করে লেখা।")
        ):
            _update, text = self.call(self.main.rewrite_command, ["পুরোনো", "লেখা"])
        self.assertIn("নতুন করে লেখা।", text)
        self.assertIn("🔵 Groq API", text)

    def test_tone_shows_source_badge(self):
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="আনুষ্ঠানিক লেখা।")
        ):
            _update, text = self.call(
                self.main.tone_command, ["formal", "আপনার", "লেখা"]
            )
        self.assertIn("আনুষ্ঠানিক লেখা।", text)
        self.assertIn("_উৎস:", text)

    def test_rewrite_usage_message_has_no_badge(self):
        _update, text = self.call(self.main.rewrite_command, [])
        self.assertIn("/rewrite", text)
        self.assertNotIn("_উৎস:", text)

    def test_tone_usage_message_has_no_badge(self):
        _update, text = self.call(self.main.tone_command, ["formal"])
        self.assertIn("/tone", text)
        self.assertNotIn("_উৎস:", text)

    def test_summarize_usage_message_has_no_badge(self):
        _update, text = self.call(self.main.summarize_command, [])
        self.assertIn("/summarize", text)
        self.assertNotIn("_উৎস:", text)

    def test_translate_usage_message_has_no_badge(self):
        _update, text = self.call(self.main.translate_command, ["english"])
        self.assertIn("/translate", text)
        self.assertNotIn("_উৎস:", text)

    # ---------------- chat_general ----------------
    def chat(self, text="প্রশ্ন", user_id=USER_ID):
        update = FakeUpdate(user_id, text)
        ctx = FakeContext()
        # anti-flood কুলডাউন যেন পরপর চলা চ্যাট-টেস্টগুলোকে আটকে না দেয়
        with patch.object(self.main, "quota_guard", new=AsyncMock(return_value=True)):
            run(self.main.chat_general(update, ctx))
        return "\n".join(update.message.sent)

    def test_chat_direct_brain_answer_shows_database_badge(self):
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.94,
            "payload": {"content": "ডাটাবেজ থেকে সরাসরি উত্তর।"},
        }
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ):
            text = self.chat("ডাটাবেজ প্রশ্ন")
        self.assertIn("ডাটাবেজ থেকে সরাসরি উত্তর।", text)
        self.assertIn("💾 ডাটাবেজ", text)
        self.assertIn("💾 ক্যাশ", text)
        self.assertNotIn("🔵 Groq API", text)

    def test_chat_ai_answer_shows_groq_badge(self):
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.2}
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="AI-এর উত্তর।")
        ), patch.object(
            self.main, "ask_ai_with_history", new=AsyncMock(return_value="AI-এর উত্তর।")
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("AI প্রশ্ন")
        self.assertIn("AI-এর উত্তর।", text)
        self.assertIn("🔵 Groq API", text)

    def test_chat_general_cache_hit_shows_database_badge(self):
        """Memory বন্ধ + আগে ক্যাশে থাকা উত্তর → 💾 Database (cache hit), AI কল নয়।"""
        self.main.update_field(USER_ID, "memory_enabled", 0)
        self.addCleanup(self.main.update_field, USER_ID, "memory_enabled", 1)
        run(self.main.general_chat_cache.set("বাংলা", "ক্যাশ প্রশ্ন", "ক্যাশের উত্তর।"))
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        ask_ai = AsyncMock()
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ), patch.object(
            self.main, "ask_ai", new=ask_ai
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("ক্যাশ প্রশ্ন")
        ask_ai.assert_not_awaited()
        self.assertIn("ক্যাশের উত্তর।", text)
        self.assertIn("💾 ডাটাবেজ", text)

    def test_chat_memory_disabled_ai_path_shows_groq_badge(self):
        """Memory বন্ধ + ক্যাশ miss → সরাসরি ask_ai + 🔵 ব্যাজ।"""
        self.main.update_field(USER_ID, "memory_enabled", 0)
        self.addCleanup(self.main.update_field, USER_ID, "memory_enabled", 1)
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        ask_ai = AsyncMock(return_value="স্বনির্ভর উত্তর।")
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ), patch.object(
            self.main, "ask_ai", new=ask_ai
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("স্বনির্ভর প্রশ্ন")
        ask_ai.assert_awaited()
        self.assertIn("স্বনির্ভর উত্তর।", text)
        self.assertIn("🔵 Groq API", text)

    def test_chat_browse_answer_has_hybrid_badge_once(self):
        """Browse পথের ব্যাজ (_automatic_browse_answer-এর ভেতরে) যেন দুইবার না বসে।"""
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        browse_answer = (
            "ওয়েব থেকে পাওয়া উত্তর।\n\n_উৎস: 🌐 ব্রাউজার সার্চ | 🔵 Groq API_\n"
            "_[🕐 2026-08-26 00:00 UTC] [🔗 1 লিংক] [নির্ভুলতা: 🟢 উচ্চ]_"
        )
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main,
            "_automatic_browse_answer",
            new=AsyncMock(return_value=browse_answer),
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("ওয়েব প্রশ্ন")
        self.assertEqual(text.count("📊 উৎস তথ্য"), 0)
        self.assertEqual(text.count("_উৎস:"), 1)

    def test_chat_memory_history_is_saved_without_badge(self):
        self.main.clear_memory(USER_ID)  # আগের টেস্টের কথোপকথন ইতিহাস যেন মিশে না যায়
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            "payload": {"content": "মেমরিতে যা সেভ হবে।"},
        }
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ):
            text = self.chat("মেমরি প্রশ্ন")
        history = self.main.get_recent_history(USER_ID, limit=6)
        saved = [row["content"] for row in history if row["role"] == "assistant"]
        self.assertIn("_উৎস:", text)  # ইউজারকে ব্যাজসহ উত্তরই গেছে
        self.assertIn(
            "মেমরি প্রশ্ন", [row["content"] for row in history if row["role"] == "user"]
        )
        self.assertTrue(any("মেমরিতে যা সেভ হবে।" in item for item in saved))
        self.assertFalse(
            any("_উৎস:" in item for item in saved)
        )  # ...কিন্তু মেমরিতে ব্যাজ ছাড়াই সেভ

    # ---------------- ফিচার বন্ধ করলে ----------------
    def test_disabled_command_has_no_badge(self):
        with patch.dict(
            os.environ, {"SOURCE_ATTRIBUTION_DISABLED_COMMANDS": "joke"}
        ), patch.object(self.main, "ask_ai", new=AsyncMock(return_value="জোক।")):
            _update, text = self.call(self.main.joke_command)
        self.assertIn("জোক।", text)
        self.assertNotIn("_উৎস:", text)

    def test_globally_disabled_has_no_badge(self):
        with patch.dict(os.environ, {"SOURCE_ATTRIBUTION_ENABLED": "0"}), patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="জোক।")
        ):
            _update, text = self.call(self.main.joke_command)
        self.assertEqual(text.strip(), "জোক।")

    def test_attribution_lang_follows_manual_language(self):
        self.main.set_user_language(USER_ID, "en")
        try:
            self.assertEqual(self.main.attribution_lang(USER_ID), "en")
        finally:
            self.main.set_user_language_auto(USER_ID)
        self.assertEqual(self.main.attribution_lang(USER_ID), "bn")

    def test_attribution_lang_survives_db_error(self):
        with patch.object(
            self.main, "get_effective_language", side_effect=RuntimeError("db gone")
        ):
            self.assertEqual(self.main.attribution_lang(USER_ID), "bn")

    def test_make_source_metadata_rejects_unknown_source(self):
        self.assertIsNone(self.main.make_source_metadata("wikipedia"))

    def test_metadata_helpers_handle_empty_input(self):
        self.assertIsNone(self.main.metadata_from_browse_result(None))
        self.assertIsNone(self.main.metadata_from_decision(None))

    def test_legacy_browse_footer_variants(self):
        with_url = self.main.legacy_browse_footer(
            "Wikipedia", "https://a.example", ["DuckDuckGo"]
        )
        self.assertEqual(
            with_url, "\n\n🔗 উৎস: https://a.example\n🔎 চেক করা হয়েছে: DuckDuckGo"
        )

        only_source = self.main.legacy_browse_footer("DuckDuckGo", "")
        self.assertEqual(only_source, "\n\n📚 উৎস: DuckDuckGo")

        self.assertEqual(self.main.legacy_browse_footer("", "", None), "")

    def test_cache_hit_marker_detects_state(self):
        self.assertFalse(self.main._cache_hit_marker("prompt", "text"))
        run(self.main.ai_response_cache.set("prompt", "text", "উত্তর"))
        self.assertTrue(self.main._cache_hit_marker("prompt", "text"))

    def test_ai_source_metadata_switches_on_cache_state(self):
        miss = self.main._ai_source_metadata("p", "t", confidence=0.9)
        self.assertIs(miss.primary_source.name, "GROQ")

        run(self.main.ai_response_cache.set("p", "t", "উত্তর"))
        hit = self.main._ai_source_metadata("p", "t", confidence=0.5)
        self.assertIs(hit.primary_source.name, "DATABASE")
        self.assertTrue(hit.cache_hit)
        self.assertGreaterEqual(hit.confidence_score, 0.6)  # ক্যাশ-হিট কখনো 🔴 নয়

    def test_attribution_helpers_report_state(self):
        self.assertTrue(self.main.source_attribution_enabled("chat"))
        self.assertTrue(self.main.source_attribution_enabled("joke"))
        self.assertEqual(self.main.attribution_lang(USER_ID), "bn")
        self.assertIn(
            self.main.source_attribution_settings()["format"],
            ("minimal", "compact", "full", "detailed"),
        )

    def test_attach_source_badge_never_raises(self):
        """metadata ভাঙা/অচেনা হলেও মূল উত্তরটাই ফেরত যাবে।"""

        class Boom:
            def to_badge(self, *a, **kw):
                raise RuntimeError("badge explosion")

        self.assertEqual(
            self.main.attach_source_badge("মূল উত্তর", Boom(), "chat"), "মূল উত্তর"
        )

    def test_metadata_helpers_survive_broken_tracker(self):
        """source_tracker মডিউল নিজেই এরর দিলেও main.py-এর হেল্পারগুলো None/মূল-লেখা ফেরত দেবে।"""

        class BrokenTracker:
            def metadata_from_browse_result(self, *a, **kw):
                raise RuntimeError("tracker boom")

            def metadata_from_decision(self, *a, **kw):
                raise RuntimeError("tracker boom")

            def build_metadata(self, *a, **kw):
                raise RuntimeError("tracker boom")

            def load_settings(self):
                raise RuntimeError("tracker boom")

        original = self.main._source_tracker
        try:
            self.main._source_tracker = BrokenTracker()
            self.assertIsNone(self.main.metadata_from_browse_result({"text": "উত্তর"}))
            self.assertIsNone(self.main.metadata_from_decision({"strategy": "direct"}))
            self.assertIsNone(self.main.make_source_metadata("groq"))
            self.assertFalse(self.main.source_attribution_enabled("chat"))
            self.assertEqual(self.main.source_attribution_settings()["enabled"], False)
        finally:
            self.main._source_tracker = original

    def test_source_attribution_enabled_survives_broken_resolver(self):
        class BrokenResolver:
            def load_settings(self):
                return {
                    "enabled": True,
                    "format": "compact",
                    "lang": "bn",
                    "commands": {},
                    "confidence": {},
                }

            def resolve_command_settings(self, command, settings=None):
                raise RuntimeError("resolver boom")

        original = self.main._source_tracker
        try:
            self.main._source_tracker = BrokenResolver()
            self.assertFalse(self.main.source_attribution_enabled("chat"))
        finally:
            self.main._source_tracker = original

    def test_attach_source_badge_survives_broken_formatter(self):
        class BrokenFormatter:
            def load_settings(self):
                return {
                    "enabled": True,
                    "format": "compact",
                    "lang": "bn",
                    "commands": {},
                    "confidence": {},
                }

            def resolve_command_settings(self, command, settings=None):
                return {"enabled": True, "format": "compact"}

            def format_with_source(self, *a, **kw):
                raise RuntimeError("formatter boom")

        original = self.main._source_tracker
        try:
            self.main._source_tracker = BrokenFormatter()
            self.assertEqual(
                self.main.attach_source_badge("মূল উত্তর", object(), "chat"),
                "মূল উত্তর",
            )
        finally:
            self.main._source_tracker = original

    def test_cache_hit_marker_survives_broken_cache(self):
        with patch.object(
            self.main.ai_response_cache,
            "make_key",
            side_effect=RuntimeError("cache boom"),
        ):
            self.assertFalse(self.main._cache_hit_marker("p", "t"))

    def test_brain_status_reports_attribution_state(self):
        status = self.main.build_brain_status_text()
        self.assertIn("Source Attribution", status)
        self.assertIn("Browse Search", status)
        self.assertNotIn("/search", status)

    # ---------------- quota / এরর-পথ: কোথাও ভুয়া ব্যাজ বসবে না ----------------
    QUOTA_COMMANDS = (
        ("joke_command", []),
        ("quote_command", []),
        ("translate_command", ["english", "লেখা"]),
        ("grammar_command", ["লেখা"]),
        ("rewrite_command", ["লেখা"]),
        ("tone_command", ["formal", "লেখা"]),
        ("summarize_command", ["লেখা"]),
    )

    def test_quota_denied_sends_nothing(self):
        for name, args in self.QUOTA_COMMANDS:
            update = FakeUpdate(USER_ID)
            ctx = FakeContext(args)
            with patch.object(
                self.main, "quota_guard", new=AsyncMock(return_value=False)
            ):
                run(getattr(self.main, name)(update, ctx))
            self.assertEqual(update.message.sent, [], msg=name)

    def test_ai_failure_messages_have_no_badge(self):
        cases = (
            ("joke_command", [], "জোক আনতে পারলাম না"),
            ("quote_command", [], "উক্তি আনতে পারলাম না"),
            ("translate_command", ["english", "লেখা"], "অনুবাদ করতে সমস্যা"),
            ("grammar_command", ["লেখা"], "সমস্যা হয়েছে"),
            ("rewrite_command", ["লেখা"], "সমস্যা হয়েছে"),
            ("tone_command", ["formal", "লেখা"], "সমস্যা হয়েছে"),
            ("summarize_command", ["লেখা"], "সমস্যা হয়েছে"),
        )
        for name, args, needle in cases:
            with patch.object(
                self.main, "ask_ai", new=AsyncMock(side_effect=RuntimeError("AI down"))
            ):
                _update, text = self.call(getattr(self.main, name), args)
            self.assertIn(needle, text, msg=name)
            self.assertNotIn("_উৎস:", text, msg=f"{name}-এ এরর মেসেজে ব্যাজ বসে গেছে")

    def test_summarize_reads_replied_message(self):
        update = FakeUpdate(USER_ID)
        update.message.reply_to_message = FakeMessage(USER_ID, "রিপ্লাই করা বড় লেখা")
        with patch.object(
            self.main, "quota_guard", new=AsyncMock(return_value=True)
        ), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="রিপ্লাইয়ের সারমর্ম।")
        ):
            run(self.main.summarize_command(update, FakeContext([])))
        text = "\n".join(update.message.sent)
        self.assertIn("রিপ্লাইয়ের সারমর্ম।", text)
        self.assertIn("_উৎস:", text)

    # ---------------- chat_general-এর বাকি শাখা ----------------
    def test_chat_auto_reply_off_sends_nothing(self):
        self.main.update_field(USER_ID, "auto_reply", 0)
        try:
            self.assertEqual(self.chat("কিছু লিখলাম"), "")
        finally:
            self.main.update_field(USER_ID, "auto_reply", 1)

    def test_chat_quota_denied_sends_nothing(self):
        update = FakeUpdate(USER_ID, "প্রশ্ন")
        with patch.object(self.main, "quota_guard", new=AsyncMock(return_value=False)):
            run(self.main.chat_general(update, FakeContext()))
        self.assertEqual(update.message.sent, [])

    def test_chat_direct_failure_falls_back_to_ai(self):
        """Decision direct বললেও পে-লোড ফাঁকা → direct_failures, তারপর 🔵 AI রুট।"""
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.5,
            "payload": {},
        }
        before = self.main.brain_os_metrics["direct_failures"]
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ), patch.object(
            self.main, "ask_ai_with_history", new=AsyncMock(return_value="AI উত্তর।")
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("ফাঁকা পে-লোড প্রশ্ন")
        self.assertGreater(self.main.brain_os_metrics["direct_failures"], before)
        self.assertIn("AI উত্তর।", text)
        self.assertIn("🔵 Groq API", text)

    def test_chat_no_api_stuck_message_has_no_badge(self):
        self.main.set_no_api_mode(USER_ID, True)
        self.addCleanup(self.main.set_no_api_mode, USER_ID, False)
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.0}
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ):
            text = self.chat("No API প্রশ্ন")
        self.assertTrue(text.strip())
        self.assertNotIn("_উৎস:", text)  # "আটকে গেছে" মেসেজে উৎস দেখানোর কিছু নেই

    def test_chat_legacy_fallback_after_crash_shows_groq_badge(self):
        """মূল ফ্লো exception দিলে legacy AI fallback চলবে এবং 🔵 ব্যাজ পাবে।"""
        with patch.object(
            self.main,
            "_phase17_decide",
            new=AsyncMock(side_effect=RuntimeError("decision boom")),
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="Legacy AI উত্তর।")
        ), patch.object(
            self.main, "is_no_api_mode", return_value=False
        ):
            text = self.chat("ক্র্যাশ প্রশ্ন")
        self.assertIn("Legacy AI উত্তর।", text)
        self.assertIn("🔵 Groq API", text)

    def test_chat_manual_language_prompt_path(self):
        """ইউজার /setlang দিয়ে ভাষা বেছে নিলে সেই শাখাও ব্যাজসহ ঠিকভাবে চলে।"""
        self.main.set_user_language(USER_ID, "en")
        try:
            decision = {
                "strategy": "direct",
                "stage": "knowledge",
                "confidence": 0.9,
                "payload": {"content": "Direct answer."},
            }
            with patch.object(
                self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
            ):
                text = self.chat("english question")
        finally:
            self.main.set_user_language_auto(USER_ID)
        self.assertIn("Direct answer.", text)
        self.assertIn("💾 Database", text)  # manual en → ইংরেজি ব্যাজ

    def test_chat_exception_in_no_api_mode_shows_stuck_message(self):
        self.main.set_no_api_mode(USER_ID, True)
        self.addCleanup(self.main.set_no_api_mode, USER_ID, False)
        with patch.object(
            self.main,
            "_phase17_decide",
            new=AsyncMock(side_effect=RuntimeError("boom")),
        ):
            text = self.chat("No API ক্র্যাশ প্রশ্ন")
        self.assertTrue(text.strip())
        self.assertNotIn("_উৎস:", text)

    def test_chat_legacy_fallback_failure_shows_generic_error(self):
        with patch.object(
            self.main,
            "_phase17_decide",
            new=AsyncMock(side_effect=RuntimeError("boom")),
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(side_effect=RuntimeError("AI down too"))
        ), patch.object(
            self.main, "is_no_api_mode", return_value=False
        ):
            text = self.chat("সব ভাঙা প্রশ্ন")
        self.assertIn("উত্তর দিতে সমস্যা হয়েছে", text)
        self.assertNotIn("_উৎস:", text)

    def test_thinking_message_delete_failure_is_swallowed(self):
        """'ভাবছি...' মেসেজ মুছতে ব্যর্থ হলেও উত্তর ঠিকই যাবে (badge-সহ)।"""

        class StickySent:
            async def delete(self):
                raise RuntimeError("cannot delete")

        class StickyMessage(FakeMessage):
            async def reply_text(self, text, **kwargs):
                self.sent.append(text)
                return StickySent()

        update = FakeUpdate(USER_ID)
        update.message = StickyMessage(USER_ID, "স্টিকি প্রশ্ন")
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            "payload": {"content": "স্টিকি উত্তর।"},
        }
        with patch.object(
            self.main, "quota_guard", new=AsyncMock(return_value=True)
        ), patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ):
            run(self.main.chat_general(update, FakeContext()))
        text = "\n".join(update.message.sent)
        self.assertIn("স্টিকি উত্তর।", text)
        self.assertIn("💾 ডাটাবেজ", text)

    def test_chat_own_key_hint_comes_before_source_badge(self):
        """নিজস্ব Key-র অনুস্মারক আগে, উৎস-ব্যাজ সবার শেষে (বিশ্বাসযোগ্যতার ফুটার)।"""
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
        ), patch.object(
            self.main, "ask_ai_with_history", new=AsyncMock(return_value="AI উত্তর।")
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=True
        ), patch.object(
            self.main, "build_own_api_key_hint", return_value="\n\n🔑 Key যোগ করুন।"
        ):
            text = self.chat("Key hint প্রশ্ন")
        self.assertIn("🔑 Key যোগ করুন।", text)
        self.assertLess(text.index("🔑 Key যোগ করুন।"), text.index("_উৎস:"))

    # ================= DB → Browser → API priority (Phase 47) =================
    def test_chat_database_first_priority(self):
        """DB-তে সরাসরি উত্তর থাকলে Browser/API কাউকেই ডাকা হবে না।"""
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            "payload": {"content": "ডাটাবেজের উত্তর।"},
        }
        browse = AsyncMock(return_value="ব্রাউজারের উত্তর।")
        ask_ai = AsyncMock(return_value="AI-এর উত্তর।")
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(self.main, "_automatic_browse_answer", new=browse), patch.object(
            self.main, "ask_ai", new=ask_ai
        ), patch.object(
            self.main, "ask_ai_with_history", new=AsyncMock()
        ):
            text = self.chat("ডাটাবেজ প্রশ্ন")
        self.assertIn("ডাটাবেজের উত্তর।", text)
        self.assertIn("💾 ডাটাবেজ", text)
        browse.assert_not_awaited()
        ask_ai.assert_not_awaited()

    def test_chat_browser_second_priority(self):
        """DB-তে না পেলে (automatic) Browser Search দ্বিতীয় ধাপে চলে, API-তে যাবে না।"""
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        browse = AsyncMock(return_value="ব্রাউজারের উত্তর।")
        ask_ai = AsyncMock(return_value="AI-এর উত্তর।")
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(self.main, "_automatic_browse_answer", new=browse), patch.object(
            self.main, "ask_ai", new=ask_ai
        ), patch.object(
            self.main, "ask_ai_with_history", new=AsyncMock()
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("ব্রাউজার প্রশ্ন")
        self.assertIn("ব্রাউজারের উত্তর।", text)
        ask_ai.assert_not_awaited()

    def test_chat_api_fallback_third(self):
        """DB ও Browser দুটোই খালি হলে তবেই 🔵 Groq API (তৃতীয় ধাপ)।"""
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        browse = AsyncMock(return_value="")
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(self.main, "_automatic_browse_answer", new=browse), patch.object(
            self.main,
            "ask_ai_with_history",
            new=AsyncMock(return_value="AI-এর উত্তর।"),
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("API প্রশ্ন")
        self.assertIn("AI-এর উত্তর।", text)
        self.assertIn("🔵 Groq API", text)

    def test_all_handlers_same_priority_db_browser_api(self):
        """chat-এর মতোই joke/quote/translate/grammar/rewrite/tone/summarize — সবার
        priority একই: 💾 DB (cache) → 🌐 Browser → 🔵 Groq API।"""
        handlers = (
            ("joke_command", []),
            ("quote_command", []),
            ("translate_command", ["english", "লেখা"]),
            ("grammar_command", ["লেখা"]),
            ("rewrite_command", ["লেখা"]),
            ("tone_command", ["formal", "লেখা"]),
            ("summarize_command", ["লেখা"]),
        )
        for name, args in handlers:
            handler = getattr(self.main, name)
            # Step 1: DB (cache hit) আগে
            with patch.object(
                self.main.ai_response_cache, "get", new=AsyncMock(return_value="ক্যাশ উত্তর।")
            ), patch.object(
                self.main, "_automatic_browse_answer", new=AsyncMock(return_value="ব্রাউজার উত্তর।")
            ), patch.object(
                self.main, "ask_ai", new=AsyncMock(return_value="AI উত্তর।")
            ):
                _update, text = self.call_raw(handler, list(args))
            self.assertIn("ক্যাশ উত্তর।", text, msg=name)
            self.assertIn("💾 ডাটাবেজ", text, msg=name)

            # Step 2: Browser দ্বিতীয় (cache miss হলে)
            with patch.object(
                self.main.ai_response_cache, "get", new=AsyncMock(return_value=None)
            ), patch.object(
                self.main, "_automatic_browse_answer", new=AsyncMock(return_value="ব্রাউজার উত্তর।")
            ), patch.object(
                self.main, "ask_ai", new=AsyncMock()
            ):
                _update, text = self.call_raw(handler, list(args))
            self.assertIn("ব্রাউজার উত্তর।", text, msg=name)

            # Step 3: Groq API শেষ (DB ও Browser খালি হলে)
            with patch.object(
                self.main.ai_response_cache, "get", new=AsyncMock(return_value=None)
            ), patch.object(
                self.main, "_automatic_browse_answer", new=AsyncMock(return_value="")
            ), patch.object(
                self.main, "ask_ai", new=AsyncMock(return_value="AI উত্তর।")
            ):
                _update, text = self.call_raw(handler, list(args))
            self.assertIn("AI উত্তর।", text, msg=name)
            self.assertIn("🔵 Groq API", text, msg=name)

    def test_browser_search_automatic_no_command_needed(self):
        """কোনো /search কমান্ড ছাড়াই DB miss-এ Browser Search স্বয়ংক্রিয়ভাবে চলে।"""
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        client = self.install_http(ddg=ddg_ok("স্বয়ংক্রিয় ওয়েব তথ্য।"))
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="গুছানো ওয়েব উত্তর।")
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("স্বয়ংক্রিয় প্রশ্ন")
        self.assertIn("গুছানো ওয়েব উত্তর।", text)
        self.assertIn("🌐 ব্রাউজার সার্চ", text)
        self.assertTrue(client.hit("duckduckgo.com"))

    def test_no_api_mode_skips_browser_and_api(self):
        """No API Call Mode: DB miss-এ কোনো AI (ব্রাউজার-গুছানো/API) কল হয় না —
        শুধু ফ্রি Browser Search চেষ্টা হয়; কিছু না পেলে 'আটকে গেছে' মেসেজ যায়।"""
        self.main.set_no_api_mode(USER_ID, True)
        self.addCleanup(self.main.set_no_api_mode, USER_ID, False)
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.0}
        browse = AsyncMock(return_value="")
        ask_ai = AsyncMock(return_value="AI-এর উত্তর।")
        ask_ai_history = AsyncMock(return_value="AI-এর উত্তর।")
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(self.main, "_automatic_browse_answer", new=browse), patch.object(
            self.main, "ask_ai", new=ask_ai
        ), patch.object(
            self.main, "ask_ai_with_history", new=ask_ai_history
        ):
            text = self.chat("No API প্রশ্ন")
        self.assertTrue(text.strip())
        self.assertIn("No API Call Mode চালু", text)
        ask_ai.assert_not_awaited()
        ask_ai_history.assert_not_awaited()
        self.assertNotIn("_উৎস:", text)

    def test_source_badges_correct_for_each_priority(self):
        """প্রতিটা priority-র উৎস-ব্যাজ সঠিক: 💾 Database / 🌐 Browser / 🔵 Groq।"""
        # DB → 💾
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            "payload": {"content": "ডাটাবেজের উত্তর।"},
        }
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ):
            text = self.chat("ডাটাবেজ প্রশ্ন")
        self.assertIn("💾 ডাটাবেজ", text)
        self.assertNotIn("🌐 ব্রাউজার সার্চ", text)
        self.assertNotIn("🔵 Groq API", text)

        # Browser → 🌐
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        browse = AsyncMock(return_value="ব্রাউজারের উত্তর।\n\n_উৎস: 🌐 ব্রাউজার সার্চ_")
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(self.main, "_automatic_browse_answer", new=browse), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("ব্রাউজার প্রশ্ন")
        self.assertIn("🌐 ব্রাউজার সার্চ", text)
        self.assertNotIn("💾 ডাটাবেজ", text)

        # API → 🔵
        decision = {"strategy": "ai", "stage": "ai", "confidence": 0.1}
        browse = AsyncMock(return_value="")
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(self.main, "_automatic_browse_answer", new=browse), patch.object(
            self.main,
            "ask_ai_with_history",
            new=AsyncMock(return_value="AI-এর উত্তর।"),
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            text = self.chat("API প্রশ্ন")
        self.assertIn("🔵 Groq API", text)
        self.assertNotIn("🌐 ব্রাউজার সার্চ", text)

    # ================= automatic Browse Search লেয়ার =================
    def test_browse_duckduckgo_valid_query_returns_abstract(self):
        self.install_http(ddg=ddg_ok())
        result = run(self.main._browse_duckduckgo("বাংলাদেশের রাজধানী"))
        self.assertEqual(result["text"], "ঢাকা বাংলাদেশের রাজধানী ও বৃহত্তম শহর।")
        self.assertEqual(result["url"], "https://bn.wikipedia.org/wiki/ঢাকা")

    def test_browse_duckduckgo_answer_and_related_fields(self):
        self.install_http(ddg=ddg_answer("42"))
        self.assertEqual(run(self.main._browse_duckduckgo("6 * 7"))["text"], "42")

        self.install_http(ddg=ddg_related())
        result = run(self.main._browse_duckduckgo("অচেনা প্রশ্ন"))
        self.assertEqual(result["text"], "সংশ্লিষ্ট টপিক থেকে পাওয়া তথ্য।")

    def test_browse_duckduckgo_failures_return_none(self):
        self.install_http(ddg=ddg_empty())
        self.assertIsNone(run(self.main._browse_duckduckgo("খালি ফলাফল")))

        self.install_http(ddg=FakeResponse(500, {}))
        self.assertIsNone(run(self.main._browse_duckduckgo("সার্ভার এরর")))

        self.install_http(ddg=FakeResponse(429, {}))
        self.assertIsNone(run(self.main._browse_duckduckgo("রেট লিমিট")))

        self.install_http(ddg=httpx.TimeoutException("timed out"))
        self.assertIsNone(run(self.main._browse_duckduckgo("টাইমআউট")))

        self.install_http(ddg=FakeResponse(200, broken_json=True))
        self.assertIsNone(run(self.main._browse_duckduckgo("ভাঙা JSON")))

    def test_browse_duckduckgo_truncates_long_text(self):
        self.install_http(ddg=ddg_ok(text="ক" * 5000))
        result = run(self.main._browse_duckduckgo("বড় লেখা"))
        self.assertEqual(len(result["text"]), 1800)

    def test_browse_wikipedia_opensearch_then_summary(self):
        client = self.install_http(
            wiki_search=wiki_titles("ঢাকা"), wiki_summary=wiki_summary()
        )
        result = run(self.main._browse_wikipedia("ঢাকা", lang="bn"))
        self.assertEqual(result["text"], "ঢাকা বাংলাদেশের রাজধানী।")
        self.assertEqual(result["url"], "https://bn.wikipedia.org/wiki/ঢাকা")
        self.assertEqual(len(client.calls), 2)

    def test_browse_wikipedia_failures_return_none(self):
        self.install_http(wiki_search=wiki_no_titles(), wiki_summary=wiki_summary())
        self.assertIsNone(run(self.main._browse_wikipedia("অস্তিত্বহীন", lang="bn")))

        self.install_http(
            wiki_search=wiki_titles("ঢাকা"), wiki_summary=FakeResponse(404, {})
        )
        self.assertIsNone(run(self.main._browse_wikipedia("ঢাকা", lang="bn")))

    def test_browse_web_search_empty_query_no_http(self):
        client = self.install_http(
            ddg=ddg_ok(), wiki_search=wiki_titles(), wiki_summary=wiki_summary()
        )
        self.assertIsNone(self.browse(""))
        self.assertIsNone(self.browse("   \n\t  "))
        self.assertEqual(client.calls, [])

    def test_browse_web_search_duckduckgo_hit_skips_wikipedia(self):
        client = self.install_http(
            ddg=ddg_ok(), wiki_search=wiki_titles(), wiki_summary=wiki_summary()
        )
        result = self.browse("বাংলাদেশের রাজধানী")
        self.assertEqual(result["matched_source"], "DuckDuckGo Instant Answer")
        self.assertFalse(client.hit("wikipedia.org"))

    def test_browse_web_search_language_hints(self):
        bn_client = self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_titles(), wiki_summary=wiki_summary()
        )
        result = self.browse("ইতিহাস", lang_hint="Bengali")
        self.assertEqual(result["matched_source"], "Wikipedia (bn)")
        self.assertTrue(any("bn.wikipedia.org" in u for u in bn_client.urls()))

        en_client = self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_titles("Dhaka"), wiki_summary=wiki_summary()
        )
        result = self.browse("capital of Bangladesh", lang_hint="English")
        self.assertEqual(result["matched_source"], "Wikipedia (en)")
        self.assertTrue(any("en.wikipedia.org" in u for u in en_client.urls()))

    def test_browse_web_search_bn_falls_back_to_en(self):
        calls = {"bn": 0, "en": 0}

        def search_route(url, _params):
            lang = "bn" if url.startswith("https://bn.") else "en"
            calls[lang] += 1
            return wiki_no_titles() if lang == "bn" else wiki_titles("Dhaka")

        self.install_http(
            ddg=ddg_empty(), wiki_search=search_route, wiki_summary=wiki_summary()
        )
        result = self.browse("Dhaka history", lang_hint="bangla")
        self.assertEqual(result["matched_source"], "Wikipedia (en)")
        self.assertEqual(calls, {"bn": 1, "en": 1})

    def test_browse_web_search_records_tried_sources_on_failure(self):
        client = self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        self.assertIsNone(self.browse("এমন কিছু যা কোথাও নেই", lang_hint="বাংলা"))
        self.assertEqual(len(client.calls), 3)

    def test_automatic_browse_empty_when_nothing_found(self):
        self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        self.assertEqual(
            run(self.main._automatic_browse_answer(USER_ID, "প্রশ্ন", "বাংলা", False)), ""
        )

    def test_automatic_browse_hybrid_badge_when_ai_organizes(self):
        self.install_http(ddg=ddg_ok("কাঁচা তথ্য।"))
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="গুছানো উত্তর।")
        ):
            answer = run(
                self.main._automatic_browse_answer(USER_ID, "প্রশ্ন", "বাংলা", False)
            )
        self.assertIn("গুছানো উত্তর।", answer)
        self.assertIn("🌐 ব্রাউজার সার্চ | 🔵 Groq API", answer)

    def test_automatic_browse_raw_when_no_api_mode(self):
        self.main.set_no_api_mode(USER_ID, True)
        self.addCleanup(self.main.set_no_api_mode, USER_ID, False)
        self.install_http(ddg=ddg_ok("কাঁচা তথ্য।"))
        ask_ai = AsyncMock()
        with patch.object(self.main, "ask_ai", new=ask_ai):
            answer = run(
                self.main._automatic_browse_answer(USER_ID, "প্রশ্ন", "বাংলা", True)
            )
        ask_ai.assert_not_awaited()
        self.assertIn("কাঁচা তথ্য।", answer)
        self.assertIn("🌐 ব্রাউজার সার্চ", answer)
        self.assertNotIn("🔵 Groq API", answer)

    def test_automatic_browse_swallows_errors(self):
        with patch.object(
            self.main, "browse_web_search", new=AsyncMock(side_effect=RuntimeError("boom"))
        ):
            self.assertEqual(
                run(self.main._automatic_browse_answer(USER_ID, "প্রশ্ন", "বাংলা", False)),
                "",
            )

    def test_automatic_browse_legacy_footer_when_attribution_disabled(self):
        with patch.dict(os.environ, {"SOURCE_ATTRIBUTION_ENABLED": "0"}):
            self.install_http(ddg=ddg_ok("কাঁচা তথ্য।"))
            with patch.object(
                self.main, "ask_ai", new=AsyncMock(return_value="গুছানো উত্তর।")
            ):
                answer = run(
                    self.main._automatic_browse_answer(USER_ID, "প্রশ্ন", "বাংলা", False)
                )
        self.assertIn("গুছানো উত্তর।", answer)
        self.assertIn("🔗 উৎস: https://bn.wikipedia.org/wiki/ঢাকা", answer)
        self.assertIn("🔎 চেক করা হয়েছে:", answer)
        self.assertNotIn("📊 উৎস তথ্য", answer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
