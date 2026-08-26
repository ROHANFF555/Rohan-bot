"""Phase 48 — Real Web Search (Tavily) + time-sensitive query + ক্যাশ-পয়জনিং প্রতিরোধ টেস্ট।

যা যাচাই করা হয়:

  1. **_is_time_sensitive_query** — "বর্তমান প্রধানমন্ত্রী কে", "রাষ্ট্রপতি কে", "CEO কে",
     "দাম কত", "স্কোর", "কবে" জাতীয় প্রশ্ন ধরা পড়ে; সাধারণ/ইতিহাস-প্রশ্ন ("তুমি কে",
     "রবীন্দ্রনাথ কে ছিলেন") ধরা পড়ে না।

  2. **Real Search Chain** — TAVILY_API_KEY থাকলে `browse_web_search()` সবার আগে Tavily
     Real Web Search চালায় (মক API রেসপন্স থেকে সঠিক current উত্তর ফেরে, DDG/Wikipedia
     কল হয়ই না); Key না থাকলে ধাপটা নিঃশব্দে স্কিপ; Tavily ডাউন/এরর হলে DuckDuckGo →
     Wikipedia → (caller-এর Groq) চেইনে আগের মতোই ফেলব্যাক।

  3. **ক্যাশ-পয়জনিং প্রতিরোধ** — time-sensitive উত্তর সেভ করলে metadata-তে expires_at
     (এখন + ৭ দিন) বসে; read path (KnowledgeEngine.search / Step 1) মেয়াদোত্তীর্ণ
     এন্ট্রি স্কিপ করে ফলে TTL শেষে একই প্রশ্ন নতুন করে সার্চ হয়; time-sensitive
     প্রশ্নে Step 1 (Database cache) পুরোপুরি স্কিপ হয় (_phase17_decide)।

চালানো যায়:
    python3 tests/test_real_search_integration.py
    python3 -m unittest tests.test_real_search_integration -v
    python3 -m pytest tests/test_real_search_integration.py -q
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

ADMIN_ID = 111
USER_ID = 448899

PM_QUESTION = "বাংলাদেশের প্রধানমন্ত্রী কে"
PM_CORRECT = "বাংলাদেশের বর্তমান প্রধানমন্ত্রী/প্রধান উপদেষ্টা ড. মোহাম্মদ ইউনূস।"
PM_WRONG_STALE = "খালেদা জিয়া (পুরোনো/ভুল cached উত্তর)।"


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def knowledge_metadata(main, knowledge_id) -> dict:
    """Knowledge entry-র metadata (JSON স্ট্রিং) পার্স করে dict হিসেবে দেয়।"""
    import json

    entry = main.KnowledgeEngine().get(knowledge_id)
    assert entry is not None, f"knowledge id={knowledge_id} পাওয়া যায়নি"
    try:
        data = json.loads(entry.metadata or "{}")
    except Exception:
        data = {}
    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------------------
# হালকা ফেক Telegram অবজেক্ট (chat_general হ্যান্ডলার-টেস্টের জন্য)
# ---------------------------------------------------------------------------
class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id
        self.first_name = "Test"
        self.username = "test_user"


class _SentMessage:
    def __init__(self, sink: list):
        self._sink = sink

    async def reply_text(self, text: str, **_kw):
        self._sink.append(text)


class FakeMessage:
    def __init__(self, user_id: int, text: str = ""):
        self.from_user = FakeUser(user_id)
        self.text = text
        self.sent: list = []

    async def reply_text(self, text: str, **_kw):
        self.sent.append(text)
        return _SentMessage(self.sent)


class FakeUpdate:
    def __init__(self, user_id: int, text: str = ""):
        self.effective_user = FakeUser(user_id)
        self.message = FakeMessage(user_id, text)


class FakeContext:
    args = []


# ---------------------------------------------------------------------------
# ফেক HTTP লেয়ার — Tavily (POST) + DuckDuckGo/Wikipedia (GET) কল আটকে নেয়
# ---------------------------------------------------------------------------
class FakeResponse:
    def __init__(self, status_code: int = 200, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeHTTPClient:
    """GET/POST দুটোই রাউট করে — Phase 48-এর Tavily POST + পুরোনো GET-সোর্সগুলো।"""

    TAVILY = "api.tavily.com"
    DDG = "api.duckduckgo.com"
    WIKI_API = "/w/api.php"
    WIKI_SUMMARY = "/api/rest_v1/page/summary/"

    def __init__(self, tavily=None, ddg=None, wiki_search=None, wiki_summary=None):
        self.tavily = tavily
        self.ddg = ddg
        self.wiki_search = wiki_search
        self.wiki_summary = wiki_summary
        self.calls: list = []

    def _route(self, url: str, params):
        if self.TAVILY in url:
            return self.tavily
        if self.DDG in url:
            return self.ddg
        if self.WIKI_SUMMARY in url:
            return self.wiki_summary
        if self.WIKI_API in url or (params or {}).get("action") == "opensearch":
            return self.wiki_search
        return None

    async def _handle(self, method: str, url: str, params=None):
        self.calls.append({"method": method, "url": url, "params": dict(params or {})})
        entry = self._route(url, params)
        if entry is None:
            return FakeResponse(404, {})
        if callable(entry):
            entry = entry(url, params)
        if isinstance(entry, Exception):
            raise entry
        return entry

    async def get(self, url, params=None, timeout=None):
        return await self._handle("GET", url, params)

    async def post(self, url, json=None, timeout=None):
        return await self._handle("POST", url, json)

    # ---- সহায়ক ----
    def hit(self, needle: str) -> bool:
        return any(needle in call["url"] for call in self.calls)

    def tavily_query(self) -> str:
        for call in self.calls:
            if self.TAVILY in call["url"]:
                return (call["params"] or {}).get("query", "")
        return ""


def tavily_ok(answer: str = PM_CORRECT, url: str = "https://example.com/bd-pm"):
    """Tavily-র সফল রেসপন্স — synthesized answer + শীর্ষ রেজাল্ট।"""
    return FakeResponse(
        200,
        {
            "answer": answer,
            "results": [
                {"title": "প্রধান উপদেষ্টা", "url": url, "content": answer},
                {"title": "বাংলাদেশ সরকার", "url": "https://example.gov.bd", "content": "সরকার সংক্রান্ত তথ্য।"},
            ],
        },
    )


def tavily_empty():
    return FakeResponse(200, {"answer": "", "results": []})


def wiki_no_titles():
    return FakeResponse(200, ["", [], [], []])


def ddg_empty():
    return FakeResponse(200, {"AbstractText": "", "Answer": "", "Definition": "", "RelatedTopics": []})


def ddg_ok(text=PM_WRONG_STALE, url="https://old.example/bd-pm"):
    return FakeResponse(200, {"AbstractText": text, "AbstractSource": "Wikipedia", "AbstractURL": url})


def wiki_titles(title="বাংলাদেশ"):
    return FakeResponse(200, [title, [title], ["https://bn.wikipedia.org/wiki/x"], [""]])


def wiki_summary(extract="বাংলাদেশ দক্ষিণ এশিয়ার একটি দেশ।"):
    return FakeResponse(
        200,
        {"extract": extract, "content_urls": {"desktop": {"page": "https://bn.wikipedia.org/wiki/x"}}},
    )


# ===========================================================================
# মূল মডিউল লোডার — প্রতিটা ক্লাস নিজের টেম্প-ডিরেক্টরিতে main.py চালায়
# ===========================================================================
class _MainModuleTestCase(unittest.TestCase):
    """main.py-কে টেম্প-ডিরেক্টরিতে কপি করে মডিউল হিসেবে লোড করে (রিপোর অন্য
    ইন্টিগ্রেশন-টেস্টগুলোর মতোই) — আসল DB/সিঙ্গেলটন নষ্ট না করে।"""

    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="rohan-real-search-")
        shutil.copyfile(os.path.join(REPO_ROOT, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", str(ADMIN_ID))
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        # টেস্ট নিজে নিয়ন্ত্রণ করবে — বাইরের env থেকে Key আসা যাবে না।
        os.environ.pop("TAVILY_API_KEY", None)

        logging.disable(logging.CRITICAL)

        module_name = "rohan_real_search_test_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
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
        sys.modules.pop("rohan_real_search_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def setUp(self):
        self.main.decision_engine_service.clear_cache()
        os.environ.pop("TAVILY_API_KEY", None)
        # টেস্টগুলো একই টেম্প-DB শেয়ার করে — ক্রম-নিরপেক্ষ রাখতে Knowledge Engine
        # খালি করে নেওয়া হয় (FTS-ও ট্রিগারের মাধ্যমে সমসঞ্চালিত থাকে)।
        try:
            conn = self.main.get_brain_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM brain_knowledge")
            conn.commit()
            conn.close()
        except Exception:  # noqa: BLE001
            pass

    def with_api_key(self):
        return patch.dict(os.environ, {"TAVILY_API_KEY": "tvly_test_key_for_unit_tests"})

    def install_http(self, **routes) -> FakeHTTPClient:
        """main.py-এর `get_http_client()`-কে ফেক ক্লায়েন্ট দিয়ে প্রতিস্থাপন করে।"""
        client = FakeHTTPClient(**routes)
        patcher = patch.object(self.main, "get_http_client", new=AsyncMock(return_value=client))
        patcher.start()
        self.addCleanup(patcher.stop)
        return client


# ===========================================================================
# 1. Time-sensitive query detection
# ===========================================================================
class TimeSensitiveQueryTests(_MainModuleTestCase):
    def test_bangla_holder_questions(self):
        self.assertTrue(self.main._is_time_sensitive_query("বাংলাদেশের বর্তমান প্রধানমন্ত্রী কে"))
        # "বর্তমান" শব্দ ছাড়াও পদবি + "কে" প্রশ্ন ধরা পড়ে।
        self.assertTrue(self.main._is_time_sensitive_query(PM_QUESTION))
        self.assertTrue(self.main._is_time_sensitive_query("রাষ্ট্রপতি কে"))
        self.assertTrue(self.main._is_time_sensitive_query("অর্থ মন্ত্রী কে?"))

    def test_english_holder_questions(self):
        self.assertTrue(self.main._is_time_sensitive_query("who is the current CEO of Google"))
        self.assertTrue(self.main._is_time_sensitive_query("Google CEO কে"))
        self.assertTrue(self.main._is_time_sensitive_query("who is the prime minister of UK"))

    def test_price_score_when_questions(self):
        self.assertTrue(self.main._is_time_sensitive_query("সোনার দাম কত"))
        self.assertTrue(self.main._is_time_sensitive_query("ইংল্যান্ড বনাম ভারত ম্যাচের স্কোর কত?"))
        self.assertTrue(self.main._is_time_sensitive_query("জাতীয় নির্বাচন কবে হবে"))
        self.assertTrue(self.main._is_time_sensitive_query("bitcoin price now"))

    def test_general_questions_not_sensitive(self):
        self.assertFalse(self.main._is_time_sensitive_query("তুমি কে"))
        # ইতিহাস-প্রশ্ন — পদবি থাকলেও "এখন/কে" নির্দেশক নেই ("ছিলেন" অতীত)।
        self.assertFalse(self.main._is_time_sensitive_query("রবীন্দ্রনাথ ঠাকুর কে ছিলেন"))
        self.assertFalse(self.main._is_time_sensitive_query("ঢাকা কোথায় অবস্থিত"))
        self.assertFalse(self.main._is_time_sensitive_query("একটা জোকস বলো"))
        # "আজাদ"-এর ভেতরের "আজ" মিলবে না (whole-token ম্যাচ)।
        self.assertFalse(self.main._is_time_sensitive_query("আজাদীর ইতিহাস বলো"))
        self.assertFalse(self.main._is_time_sensitive_query(""))

    def test_detection_never_raises(self):
        self.assertFalse(self.main._is_time_sensitive_query(None))  # type: ignore[arg-type]


# ===========================================================================
# 2. Real Search Chain (Tavily → DDG → Wikipedia ফেলব্যাক)
# ===========================================================================
class RealSearchChainTests(_MainModuleTestCase):
    def test_pm_question_answered_by_real_search(self):
        """স্পেক কেস ১ — mock real-search API থেকে সঠিক current নাম ফেরে; DDG/Wikipedia
        আর কল হয়ই না (তাদের পুরোনো/খালি ফলে যেতে দেওয়া হয় না)।"""
        client = self.install_http(
            tavily=tavily_ok(),
            ddg=ddg_ok(PM_WRONG_STALE),  # ইচ্ছে করে ভুল উত্তর — এটা ব্যবহার হওয়া যাবে না
            wiki_search=wiki_titles(),
            wiki_summary=wiki_summary(),
        )
        with self.with_api_key():
            result = run(self.main.browse_web_search(PM_QUESTION, lang_hint="বাংলা"))

        self.assertIsNotNone(result)
        self.assertIn("মোহাম্মদ ইউনূস", result["text"])
        self.assertEqual(result["matched_source"], "Tavily Web Search")
        self.assertEqual(result["tried_sources"][0], "Tavily Web Search")
        self.assertIn("Tavily Web Search", result["source"])
        self.assertEqual(client.tavily_query(), PM_QUESTION)
        # ফেলব্যাক সোর্সগুলো কলই হয়নি।
        self.assertFalse(client.hit(FakeHTTPClient.DDG))
        self.assertFalse(client.hit(FakeHTTPClient.WIKI_API))

    def test_real_search_down_falls_back_to_ddg_then_wikipedia(self):
        """স্পেক কেস ৩ — Tavily ডাউন হলে DuckDuckGo → Wikipedia চেইনে আগের মতো ফেলব্যাক।"""
        client = self.install_http(
            tavily=FakeResponse(500, {}),
            ddg=ddg_empty(),
            wiki_search=wiki_titles(),
            wiki_summary=wiki_summary("বাংলাদেশ দক্ষিণ এশিয়ার একটি দেশ।"),
        )
        with self.with_api_key():
            result = run(self.main.browse_web_search(PM_QUESTION, lang_hint="বাংলা"))

        self.assertIsNotNone(result)
        self.assertEqual(result["matched_source"], "Wikipedia (bn)")
        self.assertIn("দক্ষিণ এশিয়ার", result["text"])
        self.assertEqual(
            result["tried_sources"],
            ["Tavily Web Search", "DuckDuckGo Instant Answer", "Wikipedia (bn)"],
        )
        self.assertTrue(client.hit(FakeHTTPClient.DDG))

    def test_real_search_error_falls_back_to_ddg_answer(self):
        """Tavily এক্সেপশন (নেটওয়ার্ক ডাউন) → DDG কাজ করলে DDG-র উত্তরই ফেরে।"""
        client = self.install_http(
            tavily=RuntimeError("connection refused"),
            ddg=ddg_ok("DDG থেকে আসা উত্তর।"),
            wiki_search=wiki_no_titles(),
        )
        with self.with_api_key():
            result = run(self.main.browse_web_search("ঢাকা সম্পর্কে তথ্য", lang_hint="বাংলা"))

        self.assertIsNotNone(result)
        self.assertIn("DDG থেকে আসা উত্তর।", result["text"])
        self.assertEqual(result["matched_source"], "DuckDuckGo Instant Answer")
        self.assertEqual(result["tried_sources"], ["Tavily Web Search", "DuckDuckGo Instant Answer"])

    def test_missing_key_skips_real_search_silently(self):
        """TAVILY_API_KEY না থাকলে ধাপটা নিঃশব্দে স্কিপ — tried_sources-এও নাম নেই,
        কোনো POST কলও হয় না, আগের চেইন (DDG → Wikipedia) অক্ষত।"""
        client = self.install_http(
            ddg=ddg_ok("Key ছাড়া DDG উত্তর।"),
            wiki_search=wiki_no_titles(),
        )
        self.assertFalse(self.main._real_search_configured())
        result = run(self.main.browse_web_search("ঢাকা সম্পর্কে তথ্য", lang_hint="বাংলা"))

        self.assertIsNotNone(result)
        self.assertEqual(result["matched_source"], "DuckDuckGo Instant Answer")
        self.assertEqual(result["tried_sources"], ["DuckDuckGo Instant Answer"])
        self.assertFalse(client.hit(FakeHTTPClient.TAVILY))
        self.assertFalse(any(call["method"] == "POST" for call in client.calls))

    def test_real_search_empty_payload_falls_back(self):
        """Tavily 200 কিন্তু খালি answer/results → None → পুরোনো চেইনে ফেলব্যাক।"""
        self.install_http(tavily=tavily_empty(), ddg=ddg_ok("DDG ফেলব্যাক উত্তর।"))
        with self.with_api_key():
            result = run(self.main.browse_web_search("ঢাকা সম্পর্কে তথ্য", lang_hint="বাংলা"))
        self.assertIsNotNone(result)
        self.assertIn("DDG ফেলব্যাক উত্তর।", result["text"])

    def test_real_search_result_shape(self):
        """_browse_real_search সরাসরি — answer + শীর্ষ রেজাল্টের snippet, url, source।"""
        self.install_http(tavily=tavily_ok())
        with self.with_api_key():
            result = run(self.main._browse_real_search(PM_QUESTION, "বাংলা"))
        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "Tavily Web Search")
        self.assertEqual(result["url"], "https://example.com/bd-pm")
        self.assertIn("মোহাম্মদ ইউনূস", result["text"])
        # Key ছাড়া None — কোনো এক্সেপশন নয়।
        result_no_key = run(self.main._browse_real_search(PM_QUESTION, "বাংলা"))
        self.assertIsNone(result_no_key)


# ===========================================================================
# 3. ক্যাশ-পয়জনিং প্রতিরোধ (expires_at + read-path স্কিপ + Step 1 স্কিপ)
# ===========================================================================
class CachePoisoningGuardTests(_MainModuleTestCase):
    # ---------------- সেভ-পথ (metadata expires_at) ----------------
    def test_time_sensitive_browse_save_sets_expires_at(self):
        self.main._phase44_save_browsed_knowledge(PM_QUESTION, PM_CORRECT, "Tavily Web Search", "https://x")
        rows = self.main.KnowledgeEngine().search(PM_QUESTION, limit=5)
        self.assertTrue(rows, "time-sensitive এন্ট্রি সেভ/সার্চ হয়নি")
        meta = knowledge_metadata(self.main, rows[0]["id"])
        self.assertIn("expires_at", meta)
        expiry = datetime.fromisoformat(meta["expires_at"])
        remaining = expiry - datetime.now(timezone.utc)
        self.assertAlmostEqual(remaining.total_seconds(), 7 * 86400, delta=3600)

    def test_general_browse_save_has_no_expiry(self):
        self.main._phase44_save_browsed_knowledge("ঢাকা সম্পর্কে তথ্য দাও", "ঢাকা বাংলাদেশের রাজধানী।", "Wikipedia (bn)", "")
        rows = self.main.KnowledgeEngine().search("ঢাকা সম্পর্কে তথ্য দাও", limit=5)
        self.assertTrue(rows)
        meta = knowledge_metadata(self.main, rows[0]["id"])
        self.assertNotIn("expires_at", meta)

    def test_time_sensitive_ai_save_sets_expires_at(self):
        self.main._phase44_save_ai_knowledge("বর্তমান রাষ্ট্রপতি কে", "AI-এর দেওয়া উত্তর।")
        rows = self.main.KnowledgeEngine().search("বর্তমান রাষ্ট্রপতি কে", limit=5)
        self.assertTrue(rows)
        meta = knowledge_metadata(self.main, rows[0]["id"])
        self.assertIn("expires_at", meta)

    def test_duplicate_save_refreshes_expiry(self):
        """একই উত্তর আবার সেভ হলে ডুপ্লিকেট এন্ট্রির মেয়াদ নতুন করে বসে (জম্বি-এন্ট্রি নয়)।"""
        self.main._phase44_save_browsed_knowledge(PM_QUESTION, PM_CORRECT, "Tavily Web Search", "")
        rows = self.main.KnowledgeEngine().search(PM_QUESTION, limit=5)
        self.assertEqual(len(rows), 1)
        old_expiry = knowledge_metadata(self.main, rows[0]["id"])["expires_at"]
        # ৬ দিন পরের দৃশ্য — আবার একই উত্তর সেভ হলো।
        with patch.object(
            self.main, "_phase48_knowledge_expires_at", return_value="2099-01-01T00:00:00+00:00"
        ):
            self.main._phase44_save_browsed_knowledge(PM_QUESTION, PM_CORRECT, "Tavily Web Search", "")
        rows2 = self.main.KnowledgeEngine().search(PM_QUESTION, limit=5)
        self.assertEqual(len(rows2), 1, "ডুপ্লিকেটে নতুন রো হওয়া যাবে না")
        self.assertEqual(knowledge_metadata(self.main, rows2[0]["id"])["expires_at"], "2099-01-01T00:00:00+00:00")
        self.assertNotEqual(old_expiry, "2099-01-01T00:00:00+00:00")

    # ---------------- read-path (Step 1) মেয়াদ স্কিপ ----------------
    def test_expired_entry_skipped_in_knowledge_search(self):
        engine = self.main.KnowledgeEngine()
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(timespec="seconds")
        future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(timespec="seconds")
        expired = engine.create(
            category="browse_search", title="বাংলাদেশের পুরোনো প্রধানমন্ত্রী কে",
            content="মেয়াদ পেরোনো উত্তর।", metadata={"origin": "browse_search", "expires_at": past},
        )
        fresh = engine.create(
            category="browse_search", title="বাংলাদেশের নতুন প্রধানমন্ত্রী কে",
            content="তাজা উত্তর।", metadata={"origin": "browse_search", "expires_at": future},
        )
        self.assertIsNotNone(expired)
        self.assertIsNotNone(fresh)
        rows = self.main.KnowledgeEngine().search("বাংলাদেশের পুরোনো প্রধানমন্ত্রী কে", limit=5)
        self.assertEqual([r["id"] for r in rows if r["id"] == expired.id], [], "মেয়াদোত্তীর্ণ এন্ট্রি ফেরে না")
        rows = self.main.KnowledgeEngine().search("বাংলাদেশের নতুন প্রধানমন্ত্রী কে", limit=5)
        self.assertTrue(any(r["id"] == fresh.id for r in rows), "মেয়াদের ভেতরের এন্ট্রি ফেরে")

    # ---------------- Step 1 স্কিপ (time-sensitive প্রশ্নে) ----------------
    def _direct_decision(self):
        """DecisionEngine-এর "direct" সিদ্ধান্তের নমুনা (execute_async-কে মক করতে ব্যবহার
        হয় — নিচের টেস্টগুলো Phase 48-এর wrapper-লজিকই যাচাই করে, BM25 স্কোরিং নয়)।"""
        return {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.94,
            "score": 90.0,
            "payload": {"content": PM_WRONG_STALE},
        }

    def test_step1_skips_time_sensitive_cache_even_if_fresh(self):
        """স্পেক কেস ২ (অংশ ১) — cache-এ ভুল উত্তর থাকলেও time-sensitive প্রশ্নে Step 1
        স্কিপ হয় (strategy "direct" → "ai"), ফলে ফ্লো re-search-এ যায়।"""
        self.main._phase44_save_browsed_knowledge(PM_QUESTION, PM_WRONG_STALE, "DuckDuckGo", "")
        found = self.main.KnowledgeEngine().search(PM_QUESTION, limit=5)
        self.assertTrue(found, "প্রিকন্ডিশন: ভুল উত্তরটা ক্যাশে আছে")
        self.assertIn(PM_WRONG_STALE, found[0]["content"])
        execute = AsyncMock(return_value=self._direct_decision())
        with patch.object(self.main.decision_engine_service, "execute_async", new=execute):
            decision = run(self.main._phase17_decide(USER_ID, PM_QUESTION))
        execute.assert_awaited()
        self.assertNotEqual(decision.get("strategy"), "direct", "cached ভুল উত্তর সরাসরি দেওয়া যাবে না")
        self.assertEqual(decision.get("strategy"), "ai")
        self.assertTrue(decision.get("time_sensitive"))
        self.assertGreaterEqual(self.main.brain_os_metrics["time_sensitive_skips"], 1)

    def test_step1_still_serves_cache_for_normal_question(self):
        """কন্ট্রোল — সাধারণ (অতীত-নির্দেশক) প্রশ্নে আগের মতোই direct উত্তর চলে।"""
        execute = AsyncMock(return_value=self._direct_decision())
        with patch.object(self.main.decision_engine_service, "execute_async", new=execute):
            decision = run(self.main._phase17_decide(USER_ID, "রবীন্দ্রনাথ ঠাকুর কে ছিলেন"))
        self.assertEqual(decision.get("strategy"), "direct")
        self.assertNotIn("time_sensitive", decision)

    # ---------------- TTL শেষে re-search ----------------
    def test_research_happens_after_ttl_expiry(self):
        """স্পেক কেস ২ (সম্পূর্ণ) — একই কোয়েরি দুইবার: প্রথমবার ভুল উত্তর cache-এ গেলেও
        TTL এক্সপায়ার হলে সেটা আর সার্ভ হয় না, নতুন করে real search হয়।"""
        engine = self.main.KnowledgeEngine()
        past = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(timespec="seconds")
        # "৮ দিন আগে" সেভ হওয়া ভুল/পুরোনো উত্তর — মেয়াদ পেরিয়ে গেছে।
        engine.create(
            category="browse_search", title=PM_QUESTION, content=PM_WRONG_STALE,
            tags="auto,browse_search", source="browse_search",
            metadata={"origin": "browse_search", "expires_at": past},
        )
        # Step 1 থেকে এখন আর ওই ভুল উত্তর আসবে না।
        decision = run(self.main._phase17_decide(USER_ID, PM_QUESTION))
        self.assertNotEqual(decision.get("strategy"), "direct")
        # Step 2 — mock real search সঠিক নাম দেয়; উত্তরে নতুন নামই থাকে।
        client = self.install_http(
            tavily=tavily_ok(),
            ddg=ddg_ok(PM_WRONG_STALE),
            wiki_search=wiki_titles(),
            wiki_summary=wiki_summary(),
        )
        with self.with_api_key():
            answer = run(
                self.main._automatic_browse_answer(USER_ID, PM_QUESTION, "বাংলা", no_api_mode=True)
            )
        self.assertIn("মোহাম্মদ ইউনূস", answer)
        self.assertNotIn(PM_WRONG_STALE, answer)
        self.assertEqual(client.tavily_query(), PM_QUESTION)
        self.assertFalse(client.hit(FakeHTTPClient.DDG), "Tavily কাজ করলে DDG-তে যাওয়ার দরকার নেই")

    # ---------------- হ্যান্ডলার-লেভেল ইন্টিগ্রেশন ----------------
    def test_chat_returns_current_answer_from_mocked_real_search(self):
        """সম্পূর্ণ ফ্লো (💾 skip → 🌐 Tavily হিট): chat_general সঠিক current নাম দেয়,
        ক্যাশের ভুল নাম নয়।"""
        self.main._phase44_save_browsed_knowledge(PM_QUESTION, PM_WRONG_STALE, "DuckDuckGo", "")
        client = self.install_http(tavily=tavily_ok(), ddg=ddg_ok(PM_WRONG_STALE))
        update = FakeUpdate(USER_ID, PM_QUESTION)
        with self.with_api_key(), patch.object(
            self.main, "quota_guard", new=AsyncMock(return_value=True)
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="গুছানো: " + PM_CORRECT)
        ), patch.object(
            self.main, "ask_ai_with_history", new=AsyncMock(return_value="ইতিহাস-উত্তর (পৌঁছানো উচিত নয়)")
        ), patch.object(
            self.main, "should_show_own_key_hint", return_value=False
        ):
            run(self.main.chat_general(update, FakeContext()))
        text = "\n".join(update.message.sent)
        self.assertIn("মোহাম্মদ ইউনূস", text)
        self.assertNotIn(PM_WRONG_STALE, text)
        self.assertEqual(client.tavily_query(), PM_QUESTION)

    def test_all_sources_down_step2_empty_groq_fallback_intact(self):
        """স্পেক কেস ৩ (শেষ ধাপ) — সব সোর্স ফেল করলে Step 2 খালি স্ট্রিং দেয়, যাতে
        caller আগের মতোই Step 3 (Groq API)-এ চলে যায়।"""
        self.install_http(
            tavily=RuntimeError("down"), ddg=ddg_empty(),
            wiki_search=wiki_no_titles(), wiki_summary=FakeResponse(404, {}),
        )
        with self.with_api_key():
            self.assertIsNone(run(self.main.browse_web_search(PM_QUESTION, lang_hint="বাংলা")))
            answer = run(self.main._automatic_browse_answer(USER_ID, PM_QUESTION, "বাংলা", no_api_mode=True))
        self.assertEqual(answer, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
