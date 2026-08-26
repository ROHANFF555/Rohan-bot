"""Phase 1 — Browser Search ফিচারের টেস্ট (আসল main.py কোড চালিয়ে, বাইরের API mock করে)।

যা যাচাই করা হয়:

  A. DuckDuckGo Instant Answer লেয়ার (`_browse_duckduckgo`)
     - AbstractText / Answer / Definition / RelatedTopics থেকে তথ্য তোলা
     - খালি পে-লোড, HTTP এরর, টাইমআউট, ভাঙা JSON → নিরাপদে None
     - ১৮০০ অক্ষরের বেশি লেখা কাটা

  B. Wikipedia লেয়ার (`_browse_wikipedia`)
     - opensearch → summary দুই ধাপ
     - টাইটেল না পাওয়া / summary এরর → None

  C. `browse_web_search()` অর্কেস্ট্রেশন
     - খালি/শুধু-স্পেস কুয়েরি → সাথে সাথে None (কোনো HTTP কল নয়)
     - DuckDuckGo পেলে Wikipedia-তে যায় না
     - ভাষা অনুযায়ী Wikipedia (bn/en) ও bn ব্যর্থ হলে en fallback
     - `tried_sources`-এ চেক করা সোর্সের ক্রম
     - রেট-লিমিট (429) / নেটওয়ার্ক টাইমআউট / সব সোর্স ব্যর্থ
     - খুব লম্বা (৫০০+ অক্ষর) ও ইমোজি/বিশেষ-চিহ্নযুক্ত কুয়েরি

  D. `/search` কমান্ড (Phase 47)
     - আর্গুমেন্ট ছাড়া ব্যবহার-নির্দেশিকা
     - সফল সার্চে উত্তর + উৎস-ব্যাজ + মূল লিংক
     - বাংলা কুয়েরিতে বাংলা ব্যাজ
     - ওয়েবে না পেলে 🔵 AI fallback, No-API-Mode-এ "পাওয়া যায়নি"
     - হ্যান্ডলার রেজিস্ট্রেশন

main.py একক-file application, তাই test-টি সেটাকে (এবং rohan_bot/ প্যাকেজটা) অস্থায়ী
ডিরেক্টরিতে কপি করে আলাদা module হিসেবে import করে — repository-তে bot_data.db বা
logs/ তৈরি হয় না।

চালানো যায়:
    python3 tests/test_browser_search_feature.py
    python3 -m unittest tests.test_browser_search_feature -v
    python3 -m pytest tests/test_browser_search_feature.py
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
from unittest.mock import AsyncMock, patch

import httpx

ADMIN_ID = 111
USER_ID = 661001
BROWSE_USER_ID = 661002

DDG_URL = "api.duckduckgo.com"
WIKI_API = "/w/api.php"
WIKI_SUMMARY = "/api/rest_v1/page/summary/"


# ---------------------------------------------------------------------------
# হালকা ফেক Telegram অবজেক্ট — শুধু যতটুকু handler-গুলোর দরকার।
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
    def __init__(self, user_id: int):
        self.from_user = FakeUser(user_id)
        self.reply_to_message = None
        self.text = ""
        self.sent: list[str] = []

    async def reply_text(self, text: str, **_kwargs):
        self.sent.append(text)
        return _SentMessage(self.sent)

    async def delete(self):
        return None


class FakeUpdate:
    def __init__(self, user_id: int):
        self.effective_user = FakeUser(user_id)
        self.effective_chat = FakeChat()
        self.message = FakeMessage(user_id)
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
# ফেক HTTP লেয়ার — DuckDuckGo/Wikipedia কল আটকে নিয়ন্ত্রিত উত্তর দেয়।
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
    """`httpx.AsyncClient`-এর জায়গায় বসে; URL দেখে আগে থেকে ঠিক করা উত্তর দেয়।

    প্রতিটা রুটে তিন রকম জিনিস বসানো যায়: FakeResponse, Exception, অথবা
    ``(FakeResponse, সেকেন্ড-দেরি)`` টাপল — দেরি `timeout`-এর বেশি হলে
    `httpx.TimeoutException` তোলা হয় (উচ্চ-লেটেন্সি পরিস্থিতি সিমুলেট করতে)।
    """

    def __init__(self, ddg=None, wiki_search=None, wiki_summary=None):
        self.ddg = ddg
        self.wiki_search = wiki_search
        self.wiki_summary = wiki_summary
        self.calls: list[dict] = []

    def _route(self, url: str, params):
        if DDG_URL in url:
            return self.ddg
        if WIKI_SUMMARY in url:
            return self.wiki_summary
        if WIKI_API in url or (params or {}).get("action") == "opensearch":
            return self.wiki_search
        return FakeResponse(404, {})

    async def get(self, url, params=None, timeout=None):
        self.calls.append(
            {"url": url, "params": dict(params or {}), "timeout": timeout}
        )
        entry = self._route(url, params)
        if entry is None:  # রুট সেট না করা থাকলে 404 — বাস্তব আচরণের মতোই
            return FakeResponse(404, {})
        delay = 0.0
        if isinstance(entry, tuple):
            entry, delay = entry
        if callable(entry):  # রুটে ফাংশন বসালে (url, params) দিয়ে ডাকা হয়
            entry = entry(url, params)
        if delay:
            if timeout is not None and delay > timeout:
                await asyncio.sleep(min(delay, 0.2))
                raise httpx.TimeoutException(
                    f"simulated {delay}s latency exceeds {timeout}s timeout"
                )
            await asyncio.sleep(delay)
        if isinstance(entry, Exception):
            raise entry
        if asyncio.iscoroutine(entry):
            entry = await entry
        return entry

    # ---------------- assertions helpers ----------------
    def urls(self) -> list[str]:
        return [call["url"] for call in self.calls]

    def hit(self, needle: str) -> bool:
        return any(needle in call["url"] for call in self.calls)

    def query_sent(self, needle: str = DDG_URL) -> str:
        for call in self.calls:
            if needle in call["url"]:
                return call["params"].get("q") or call["params"].get("search") or ""
        return ""


# ---------------------------------------------------------------------------
# রেডিমেড পে-লোড
# ---------------------------------------------------------------------------
def ddg_ok(
    text="ঢাকা বাংলাদেশের রাজধানী ও বৃহত্তম শহর।",
    source="Wikipedia",
    url="https://bn.wikipedia.org/wiki/ঢাকা",
):
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


def wiki_summary(
    extract="ঢাকা বাংলাদেশের রাজধানী।", url="https://bn.wikipedia.org/wiki/ঢাকা"
):
    return FakeResponse(
        200, {"extract": extract, "content_urls": {"desktop": {"page": url}}}
    )


class BrowserSearchFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-browse-test-")
        shutil.copyfile(
            os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py")
        )
        # rohan_bot/ প্যাকেজটাও কপি করা হয় — নাহলে Phase 47 source attribution বন্ধ থাকবে।
        shutil.copytree(
            os.path.join(repo_root, "rohan_bot"),
            os.path.join(cls.workdir, "rohan_bot"),
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", str(ADMIN_ID))
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        os.environ.pop("SOURCE_ATTRIBUTION_ENABLED", None)

        logging.disable(logging.CRITICAL)

        # একই প্রসেসে অন্য test module আগে rohan_bot import করলে পুরনো (মুছে যাওয়া) path
        # থেকে লোড হতে পারে — তাই প্রতিবার ক্লাস শুরুর আগে ক্যাশ পরিষ্কার করা হয়।
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)
        if cls.workdir not in sys.path:
            sys.path.insert(0, cls.workdir)

        module_name = "rohan_browser_search_test_main"
        spec = importlib.util.spec_from_file_location(
            module_name, os.path.join(cls.workdir, "main.py")
        )
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        for uid in (USER_ID, BROWSE_USER_ID):
            cls.main.register_user(uid)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_browser_search_test_main", None)
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    # ---------------- helpers ----------------
    def install_http(self, **routes) -> FakeHTTPClient:
        client = FakeHTTPClient(**routes)
        patcher = patch.object(
            self.main, "get_http_client", new=AsyncMock(return_value=client)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        return client

    def browse(self, query: str, lang_hint: str = ""):
        return run(self.main.browse_web_search(query, lang_hint=lang_hint))

    def call_search(self, *args, user_id: int = USER_ID):
        update = FakeUpdate(user_id)
        ctx = FakeContext(list(args))
        quota = patch.object(self.main, "quota_guard", new=AsyncMock(return_value=True))
        with quota:
            run(self.main.search_command(update, ctx))
        return update, "\n".join(update.message.sent)

    # ================= A. DuckDuckGo লেয়ার =================
    def test_duckduckgo_valid_query_returns_abstract(self):
        self.install_http(ddg=ddg_ok())
        result = run(self.main._browse_duckduckgo("বাংলাদেশের রাজধানী"))
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "ঢাকা বাংলাদেশের রাজধানী ও বৃহত্তম শহর।")
        self.assertEqual(result["source"], "Wikipedia")
        self.assertEqual(result["url"], "https://bn.wikipedia.org/wiki/ঢাকা")

    def test_duckduckgo_uses_answer_field(self):
        self.install_http(ddg=ddg_answer("42"))
        result = run(self.main._browse_duckduckgo("6 * 7"))
        self.assertEqual(result["text"], "42")
        self.assertEqual(
            result["source"], "DuckDuckGo"
        )  # AbstractSource না থাকলে ডিফল্ট

    def test_duckduckgo_falls_back_to_related_topics(self):
        self.install_http(ddg=ddg_related())
        result = run(self.main._browse_duckduckgo("অচেনা প্রশ্ন"))
        self.assertEqual(result["text"], "সংশ্লিষ্ট টপিক থেকে পাওয়া তথ্য।")

    def test_duckduckgo_empty_payload_returns_none(self):
        self.install_http(ddg=ddg_empty())
        self.assertIsNone(run(self.main._browse_duckduckgo("খালি ফলাফল")))

    def test_duckduckgo_http_error_returns_none(self):
        self.install_http(ddg=FakeResponse(500, {}))
        self.assertIsNone(run(self.main._browse_duckduckgo("সার্ভার এরর")))

    def test_duckduckgo_rate_limit_429_returns_none(self):
        self.install_http(ddg=FakeResponse(429, {}))
        self.assertIsNone(run(self.main._browse_duckduckgo("রেট লিমিট")))

    def test_duckduckgo_timeout_returns_none(self):
        self.install_http(ddg=httpx.TimeoutException("timed out"))
        self.assertIsNone(run(self.main._browse_duckduckgo("টাইমআউট")))

    def test_duckduckgo_malformed_json_returns_none(self):
        self.install_http(ddg=FakeResponse(200, broken_json=True))
        self.assertIsNone(run(self.main._browse_duckduckgo("ভাঙা JSON")))

    def test_duckduckgo_truncates_very_long_text(self):
        self.install_http(ddg=ddg_ok(text="ক" * 5000))
        result = run(self.main._browse_duckduckgo("বড় লেখা"))
        self.assertEqual(len(result["text"]), 1800)

    # ================= B. Wikipedia লেয়ার =================
    def test_wikipedia_opensearch_then_summary(self):
        client = self.install_http(
            wiki_search=wiki_titles("ঢাকা"), wiki_summary=wiki_summary()
        )
        result = run(self.main._browse_wikipedia("ঢাকা", lang="bn"))
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "ঢাকা বাংলাদেশের রাজধানী।")
        self.assertEqual(result["source"], "Wikipedia (bn)")
        self.assertEqual(result["url"], "https://bn.wikipedia.org/wiki/ঢাকা")
        self.assertEqual(len(client.calls), 2)
        self.assertIn(WIKI_API, client.calls[0]["url"])
        self.assertIn(WIKI_SUMMARY, client.calls[1]["url"])

    def test_wikipedia_no_titles_returns_none(self):
        self.install_http(wiki_search=wiki_no_titles(), wiki_summary=wiki_summary())
        self.assertIsNone(
            run(self.main._browse_wikipedia("অস্তিত্বহীন পাতা", lang="bn"))
        )

    def test_wikipedia_summary_error_returns_none(self):
        self.install_http(
            wiki_search=wiki_titles("ঢাকা"), wiki_summary=FakeResponse(404, {})
        )
        self.assertIsNone(run(self.main._browse_wikipedia("ঢাকা", lang="bn")))

    # ================= C. browse_web_search অর্কেস্ট্রেশন =================
    def test_empty_query_returns_none_without_http_call(self):
        client = self.install_http(
            ddg=ddg_ok(), wiki_search=wiki_titles(), wiki_summary=wiki_summary()
        )
        self.assertIsNone(self.browse(""))
        self.assertEqual(
            client.calls, []
        )  # খালি কুয়েরিতে একটাও নেটওয়ার্ক কল হওয়া যাবে না

    def test_whitespace_only_query_returns_none(self):
        client = self.install_http(
            ddg=ddg_ok(), wiki_search=wiki_titles(), wiki_summary=wiki_summary()
        )
        self.assertIsNone(self.browse("   \n\t  "))
        self.assertEqual(client.calls, [])

    def test_duckduckgo_hit_skips_wikipedia(self):
        client = self.install_http(
            ddg=ddg_ok(), wiki_search=wiki_titles(), wiki_summary=wiki_summary()
        )
        result = self.browse("বাংলাদেশের রাজধানী")
        self.assertIsNotNone(result)
        self.assertEqual(result["matched_source"], "DuckDuckGo Instant Answer")
        self.assertEqual(result["tried_sources"], ["DuckDuckGo Instant Answer"])
        self.assertFalse(client.hit("wikipedia.org"))

    def test_bengali_hint_uses_bengali_wikipedia(self):
        client = self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_titles(), wiki_summary=wiki_summary()
        )
        result = self.browse("বাংলাদেশের ইতিহাস", lang_hint="Bengali")
        self.assertIsNotNone(result)
        self.assertEqual(result["matched_source"], "Wikipedia (bn)")
        self.assertTrue(any("bn.wikipedia.org" in url for url in client.urls()))
        self.assertFalse(
            client.hit("en.wikipedia.org")
        )  # bn-এ পেয়ে গেলে en-এ যাওয়ার দরকার নেই

    def test_english_hint_uses_english_wikipedia(self):
        client = self.install_http(
            ddg=ddg_empty(),
            wiki_search=wiki_titles("Dhaka"),
            wiki_summary=wiki_summary(),
        )
        result = self.browse("capital of Bangladesh", lang_hint="English")
        self.assertEqual(result["matched_source"], "Wikipedia (en)")
        self.assertTrue(any("en.wikipedia.org" in url for url in client.urls()))

    def test_bengali_wikipedia_failure_falls_back_to_english(self):
        """bn Wikipedia-তে টাইটেল না মিললে en Wikipedia-তে আরেকবার চেষ্টা হবে।"""
        calls = {"bn": 0, "en": 0}

        def search_route(url, _params):
            lang = "bn" if url.startswith("https://bn.") else "en"
            calls[lang] += 1
            return wiki_no_titles() if lang == "bn" else wiki_titles("Dhaka")

        client = self.install_http(
            ddg=ddg_empty(), wiki_search=search_route, wiki_summary=wiki_summary()
        )
        result = self.browse("Dhaka history", lang_hint="bangla")

        self.assertIsNotNone(result)
        self.assertEqual(result["matched_source"], "Wikipedia (en)")
        self.assertEqual(
            result["tried_sources"],
            [
                "DuckDuckGo Instant Answer",
                "Wikipedia (bn)",
                "Wikipedia (en)",
            ],
        )
        self.assertEqual(calls, {"bn": 1, "en": 1})
        self.assertTrue(client.hit("en.wikipedia.org"))

    def test_tried_sources_recorded_when_everything_fails(self):
        client = self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        self.assertIsNone(self.browse("এমন কিছু যা কোথাও নেই", lang_hint="বাংলা"))
        self.assertEqual(len(client.calls), 3)  # DDG + bn wiki + en wiki
        self.assertTrue(client.hit(DDG_URL))

    def test_high_latency_triggers_timeout_and_moves_on(self):
        """DDG ৫ সেকেন্ড আটকে থাকলে (timeout ৮s) কল হয়, কিন্তু ধীর হলেও ফলাফল সামলানো যায়।"""
        client = self.install_http(
            ddg=(ddg_ok("ধীর কিন্তু সফল উত্তর।"), 0.05),
            wiki_search=wiki_titles(),
            wiki_summary=wiki_summary(),
        )
        result = self.browse("ধীর সার্চ")
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "ধীর কিন্তু সফল উত্তর।")
        self.assertEqual(client.calls[0]["timeout"], self.main.BROWSE_SEARCH_TIMEOUT)

    def test_timeout_beyond_limit_falls_back_to_wikipedia(self):
        """DDG-র কল সীমা ছাড়িয়ে আটকে গেলে সেটা বাদ দিয়ে Wikipedia চেষ্টা হবে।"""
        client = self.install_http(
            ddg=(ddg_ok("এটা কখনো আসবে না"), self.main.BROWSE_SEARCH_TIMEOUT + 5),
            wiki_search=wiki_titles(),
            wiki_summary=wiki_summary("Wikipedia থেকে পাওয়া উত্তর।"),
        )
        patcher = patch.object(self.main, "BROWSE_SEARCH_TIMEOUT", 0.05)
        with patcher:
            result = self.browse("টাইমআউট পরীক্ষা")
        self.assertIsNotNone(result)
        self.assertEqual(result["matched_source"], "Wikipedia (en)")
        self.assertEqual(result["text"], "Wikipedia থেকে পাওয়া উত্তর।")

    def test_all_sources_rate_limited_returns_none(self):
        client = self.install_http(
            ddg=FakeResponse(429, {}),
            wiki_search=FakeResponse(429, {}),
            wiki_summary=FakeResponse(429, {}),
        )
        self.assertIsNone(self.browse("রেট লিমিট পরীক্ষা"))
        self.assertEqual(
            len(client.calls), 2
        )  # DDG + en wiki (wiki_search ব্যর্থ → summary কল হয় না)

    def test_very_long_query_is_sent_intact(self):
        query = "ক" * 520 + " শেষ"
        client = self.install_http(ddg=ddg_ok())
        self.assertIsNotNone(self.browse(query))
        self.assertEqual(client.query_sent(), query)
        self.assertGreater(len(client.query_sent()), 500)

    def test_special_characters_and_emoji_query(self):
        query = "🔥 Python 3.12 <new> features? 'quotes' & \"symbols\" #tag $100 ✅"
        client = self.install_http(ddg=ddg_ok("ইমোজি ও বিশেষ চিহ্নসহ কুয়েরির উত্তর।"))
        result = self.browse(query)
        self.assertIsNotNone(result)
        self.assertEqual(client.query_sent(), query)

    def test_malformed_none_query_is_safe(self):
        self.assertIsNone(self.browse(None))  # type: ignore[arg-type]

    def test_browse_result_shape(self):
        self.install_http(ddg=ddg_ok())
        result = self.browse("গঠন পরীক্ষা")
        self.assertEqual(
            set(result.keys()),
            {"text", "source", "url", "tried_sources", "matched_source"},
        )
        self.assertIsInstance(result["tried_sources"], list)

    # ================= D. /search কমান্ড =================
    def test_search_command_registered(self):
        self.assertTrue(hasattr(self.main, "search_command"))
        self.assertTrue(callable(self.main.search_command))

    def test_search_command_without_args_shows_usage(self):
        _update, text = self.call_search()
        self.assertIn("/search", text)
        self.assertIn("উদাহরণ", text)

    def test_search_command_happy_path_has_answer_and_source_badge(self):
        self.install_http(ddg=ddg_ok())
        organize = patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="ঢাকা বাংলাদেশের রাজধানী।")
        )
        with organize:
            _update, text = self.call_search("বাংলাদেশের", "রাজধানী", "কোনটি?")
        self.assertIn("🔎 সার্চ ফলাফল", text)
        self.assertIn("ঢাকা বাংলাদেশের রাজধানী।", text)
        # Phase 47 source badge
        self.assertIn("উৎস", text)
        self.assertIn("🌐 ব্রাউজার সার্চ", text)
        self.assertIn("🔵 Groq API", text)  # AI দিয়ে গুছানো → 🔄 Hybrid
        self.assertIn("https://bn.wikipedia.org/wiki/ঢাকা", text)
        self.assertIn("নির্ভুলতা", text)
        self.assertGreaterEqual(self.main.brain_os_metrics["search_answers"], 1)

    def test_search_command_bengali_badge_language(self):
        """/search-এর ব্যাজ বাংলায় আসে (config-এ /search-এর ফরম্যাট "full")।"""
        self.install_http(ddg=ddg_ok())
        organize = patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="সংক্ষিপ্ত উত্তর।")
        )
        with organize:
            _update, text = self.call_search("বাংলাদেশের মুদ্রা", user_id=USER_ID)
        self.assertIn("📊 উৎস তথ্য", text)
        self.assertIn("মূল উৎস: 🌐 ব্রাউজার সার্চ", text)
        self.assertIn("অন্য উৎস: 🔵 Groq API", text)
        self.assertIn("ধরন: 🔄 সম্মিলিত", text)
        self.assertIn("নির্ভুলতা: 🟢", text)
        # ইংরেজি ফুল-ফরম্যাটের লেবেল যেন না থাকে (ভাষা সত্যিই bn আছে কিনা)
        self.assertNotIn("Primary Source:", text)
        self.assertNotIn("_Source:", text)

    def test_search_command_no_api_mode_returns_raw_browser_text(self):
        """No API Call Mode চালু থাকলে AI কল হবে না — কাঁচা ওয়েব-তথ্যই 🌐 ব্যাজসহ যাবে।"""
        self.main.set_no_api_mode(BROWSE_USER_ID, True)
        self.addCleanup(self.main.set_no_api_mode, BROWSE_USER_ID, False)
        self.install_http(ddg=ddg_ok("কাঁচা ওয়েব তথ্য।"))
        ask_ai = AsyncMock()
        with patch.object(self.main, "ask_ai", new=ask_ai):
            _update, text = self.call_search("কাঁচা", "তথ্য", user_id=BROWSE_USER_ID)
        ask_ai.assert_not_awaited()
        self.assertIn("কাঁচা ওয়েব তথ্য।", text)
        self.assertIn("🌐 ব্রাউজার সার্চ", text)
        self.assertNotIn("🔵 Groq API", text)  # AI ব্যবহার হয়নি → Hybrid নয়

    def test_search_command_falls_back_to_groq_when_web_has_nothing(self):
        self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        decide = patch.object(
            self.main,
            "_phase17_decide",
            new=AsyncMock(return_value={"strategy": "ai", "stage": "ai"}),
        )
        ask_ai = AsyncMock(return_value="AI-এর তৈরি উত্তর।")
        with decide, patch.object(self.main, "ask_ai", new=ask_ai):
            _update, text = self.call_search("এমন প্রশ্ন যা ওয়েবে নেই")
        ask_ai.assert_awaited()
        self.assertIn("AI-এর তৈরি উত্তর।", text)
        self.assertIn("🔵 Groq API", text)
        self.assertNotIn("🌐 ব্রাউজার সার্চ", text)

    def test_search_command_uses_database_when_brain_os_knows(self):
        self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.93,
            "payload": {"content": "ডাটাবেজে সংরক্ষিত উত্তর।"},
        }
        ask_ai = AsyncMock()
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value=decision)
        ), patch.object(self.main, "ask_ai", new=ask_ai):
            _update, text = self.call_search("ডাটাবেজের প্রশ্ন")
        ask_ai.assert_not_awaited()
        self.assertIn("💾 ডাটাবেজ", text)
        self.assertIn("ক্যাশ", text)  # cache hit হিসেবে চিহ্নিত

    def test_search_command_reports_nothing_found_in_no_api_mode(self):
        self.main.set_no_api_mode(BROWSE_USER_ID, True)
        self.addCleanup(self.main.set_no_api_mode, BROWSE_USER_ID, False)
        self.install_http(
            ddg=FakeResponse(429, {}),
            wiki_search=FakeResponse(429, {}),
            wiki_summary=FakeResponse(429, {}),
        )
        decide = patch.object(
            self.main,
            "_phase17_decide",
            new=AsyncMock(return_value={"strategy": "ai", "stage": "ai"}),
        )
        ask_ai = AsyncMock()
        with decide, patch.object(self.main, "ask_ai", new=ask_ai):
            _update, text = self.call_search(
                "কিছুই", "পাওয়া", "যাবে", "না", user_id=BROWSE_USER_ID
            )
        ask_ai.assert_not_awaited()
        self.assertIn("কোনো নির্ভরযোগ্য তথ্য পাওয়া যায়নি", text)
        self.assertNotIn("🔎 সার্চ ফলাফল", text)

    def test_search_command_survives_network_failure(self):
        """সব নেটওয়ার্ক কল exception ছুঁড়লেও হ্যান্ডলার crash করবে না।"""
        self.install_http(
            ddg=httpx.ConnectError("connection refused"),
            wiki_search=httpx.ConnectError("connection refused"),
            wiki_summary=httpx.ConnectError("connection refused"),
        )
        decide = patch.object(
            self.main,
            "_phase17_decide",
            new=AsyncMock(return_value={"strategy": "ai", "stage": "ai"}),
        )
        ask_ai = AsyncMock(return_value="নেটওয়ার্ক বিকল, তবু AI উত্তর দিল।")
        with decide, patch.object(self.main, "ask_ai", new=ask_ai):
            _update, text = self.call_search("নেটওয়ার্ক বিকল")
        self.assertIn("AI উত্তর" if "AI উত্তর" in text else "AI", text)

    def test_search_command_special_characters_do_not_crash(self):
        self.install_http(ddg=ddg_ok("বিশেষ চিহ্নের উত্তর।"))
        organize = patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="বিশেষ চিহ্নের উত্তর।")
        )
        with organize:
            _update, text = self.call_search("🔥 <b>&'\"</b> ✅ #tag")
        self.assertIn("🔎 সার্চ ফলাফল", text)
        self.assertIn("🌐 ব্রাউজার সার্চ", text)


class RunBrowserSearchTests(unittest.TestCase):
    """`run_browser_search()` / `_browse_and_organize()` / `_phase44_browse_and_answer()`-এর
    ফলব্যাক-চেইন ও এরর-পথের টেস্ট — এগুলোই /search ও সাধারণ চ্যাটের মূল লজিক।"""

    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="rohan-runsearch-test-")
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shutil.copyfile(
            os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py")
        )
        shutil.copytree(
            os.path.join(repo_root, "rohan_bot"),
            os.path.join(cls.workdir, "rohan_bot"),
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", str(ADMIN_ID))
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        logging.disable(logging.CRITICAL)
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)
        # ইচ্ছে করেই sys.path-এ workdir যোগ করা হচ্ছে না — যাতে main.py-এর নিজের
        # _load_source_tracker() প্যাকেজটা খুঁজে sys.path-এ বসায় (সেই শাখাও টেস্ট হয়)।
        sys.path[:] = [p for p in sys.path if p != cls.workdir]

        module_name = "rohan_run_search_test_main"
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
        sys.modules.pop("rohan_run_search_test_main", None)
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    # ---------------- helpers ----------------
    def install_http(self, **routes) -> FakeHTTPClient:
        client = FakeHTTPClient(**routes)
        patcher = patch.object(
            self.main, "get_http_client", new=AsyncMock(return_value=client)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        return client

    def call_search(self, *args, user_id: int = USER_ID, quota_ok: bool = True):
        update = FakeUpdate(user_id)
        ctx = FakeContext(list(args))
        with patch.object(
            self.main, "quota_guard", new=AsyncMock(return_value=quota_ok)
        ):
            run(self.main.search_command(update, ctx))
        return update, "\n".join(update.message.sent)

    # ---------------- run_browser_search ----------------
    def test_empty_query_returns_immediately(self):
        self.install_http(ddg=ddg_ok())
        answer, meta = run(self.main.run_browser_search(USER_ID, "   "))
        self.assertEqual(answer, "")
        self.assertIsNone(meta)

    def test_browse_and_organize_empty_query(self):
        answer, meta, found = run(
            self.main._browse_and_organize(USER_ID, "", "বাংলা", False)
        )
        self.assertEqual((answer, meta, found), ("", None, None))

    def test_organize_failure_falls_back_to_raw_text(self):
        """AI দিয়ে গুছাতে ব্যর্থ হলে কাঁচা ওয়েব-তথ্যই 🌐 ব্যাজসহ যাবে (Hybrid নয়)।"""
        self.install_http(ddg=ddg_ok("কাঁচা তথ্য।"))
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(side_effect=RuntimeError("AI down"))
        ):
            answer, meta, found = run(
                self.main._browse_and_organize(USER_ID, "প্রশ্ন", "বাংলা", False)
            )
        self.assertEqual(answer, "কাঁচা তথ্য।")
        self.assertIsNotNone(found)
        self.assertFalse(meta.is_hybrid)

    def test_decide_error_still_reaches_ai_fallback(self):
        """Brain OS Decision Engine exception ছুঁড়লেও সেটা উপেক্ষা করে AI fallback চলবে।"""
        self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        with patch.object(
            self.main,
            "_phase17_decide",
            new=AsyncMock(side_effect=RuntimeError("db gone")),
        ), patch.object(self.main, "ask_ai", new=AsyncMock(return_value="AI উত্তর।")):
            answer, meta = run(self.main.run_browser_search(USER_ID, "প্রশ্ন"))
        self.assertEqual(answer, "AI উত্তর।")
        self.assertIs(meta.primary_source.name, "GROQ")

    def test_ai_fallback_failure_returns_empty(self):
        self.install_http(
            ddg=FakeResponse(500, {}),
            wiki_search=FakeResponse(500, {}),
            wiki_summary=FakeResponse(500, {}),
        )
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value={"strategy": "ai"})
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(side_effect=RuntimeError("AI down"))
        ):
            answer, meta = run(self.main.run_browser_search(USER_ID, "প্রশ্ন"))
        self.assertEqual((answer, meta), ("", None))

    def test_ai_fallback_empty_answer_returns_empty(self):
        self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        with patch.object(
            self.main, "_phase17_decide", new=AsyncMock(return_value={"strategy": "ai"})
        ), patch.object(self.main, "ask_ai", new=AsyncMock(return_value="   ")):
            answer, meta = run(self.main.run_browser_search(USER_ID, "প্রশ্ন"))
        self.assertEqual((answer, meta), ("", None))

    # ---------------- _phase44_browse_and_answer ----------------
    def test_phase44_returns_empty_when_nothing_found(self):
        self.install_http(
            ddg=ddg_empty(), wiki_search=wiki_no_titles(), wiki_summary=wiki_summary()
        )
        self.assertEqual(
            run(
                self.main._phase44_browse_and_answer(USER_ID, "প্রশ্ন", "বাংলা", False)
            ),
            "",
        )

    def test_phase44_swallows_unexpected_errors(self):
        with patch.object(
            self.main,
            "_browse_and_organize",
            new=AsyncMock(side_effect=RuntimeError("boom")),
        ):
            self.assertEqual(
                run(
                    self.main._phase44_browse_and_answer(
                        USER_ID, "প্রশ্ন", "বাংলা", False
                    )
                ),
                "",
            )

    def test_phase44_answer_carries_hybrid_badge(self):
        self.install_http(ddg=ddg_ok("কাঁচা তথ্য।"))
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="গুছানো উত্তর।")
        ):
            answer = run(
                self.main._phase44_browse_and_answer(USER_ID, "প্রশ্ন", "বাংলা", False)
            )
        self.assertIn("গুছানো উত্তর।", answer)
        self.assertIn("_উৎস: 🌐 ব্রাউজার সার্চ | 🔵 Groq API_", answer)

    # ---------------- /search হ্যান্ডলারের বাকি পথ ----------------
    def test_search_command_quota_denied_sends_nothing(self):
        update, text = self.call_search("কিছু", quota_ok=False)
        self.assertEqual(text, "")
        self.assertEqual(update.message.sent, [])

    def test_search_command_uses_manual_language_setting(self):
        self.main.set_user_language(USER_ID, "en")
        self.addCleanup(self.main.set_user_language_auto, USER_ID)
        client = self.install_http(
            ddg=ddg_empty(),
            wiki_search=wiki_titles("Dhaka"),
            wiki_summary=wiki_summary("Answer from Wikipedia."),
        )
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="Organized answer.")
        ):
            _update, text = self.call_search("capital", "of", "Bangladesh")
        self.assertTrue(any("en.wikipedia.org" in url for url in client.urls()))
        self.assertIn(
            "📊 Source Information", text
        )  # ইংরেজি ব্যাজ (ইউজার en বেছে নিয়েছেন)
        self.assertIn("Primary Source: 🌐 Browser Search", text)

    def test_search_command_error_path_shows_friendly_message(self):
        self.install_http(ddg=ddg_ok())
        with patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="উত্তর।")
        ), patch.object(
            self.main, "attach_source_badge", side_effect=RuntimeError("badge boom")
        ):
            _update, text = self.call_search("এরর", "টেস্ট")
        self.assertIn("সার্চ করতে সমস্যা হয়েছে", text)


class SourceAttributionFallbackTests(unittest.TestCase):
    """rohan_bot/ প্যাকেজ না থাকলে বট ভাঙবে না, শুধু ব্যাজ বন্ধ থাকবে — তার যাচাই।"""

    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-browse-noattr-")
        shutil.copyfile(
            os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py")
        )
        cls.old_cwd = os.getcwd()
        cls.old_path = list(sys.path)
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", str(ADMIN_ID))
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        logging.disable(logging.CRITICAL)
        sys.path[:] = [
            p for p in sys.path if "rohan" not in p.lower() or p == cls.workdir
        ]
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)

        module_name = "rohan_browser_noattr_test_main"
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
        sys.path[:] = cls.old_path
        sys.modules.pop("rohan_browser_noattr_test_main", None)
        for name in [
            m for m in sys.modules if m == "rohan_bot" or m.startswith("rohan_bot.")
        ]:
            sys.modules.pop(name, None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def test_attribution_disabled_when_package_missing(self):
        self.assertFalse(self.main.SOURCE_ATTRIBUTION_AVAILABLE)
        self.assertFalse(self.main.source_attribution_enabled("chat"))
        self.assertIsNone(self.main.make_source_metadata("groq"))

    def test_attach_source_badge_is_a_noop(self):
        metadata = self.main.make_source_metadata("groq", confidence=0.9)
        self.assertEqual(
            self.main.attach_source_badge("মূল উত্তর", metadata, "chat"), "মূল উত্তর"
        )
        self.assertEqual(
            self.main.attach_source_badge("মূল উত্তর", None, "chat"), "মূল উত্তর"
        )

    def test_all_metadata_helpers_are_noops(self):
        found = {
            "text": "উত্তর",
            "source": "Wikipedia",
            "url": "https://a",
            "tried_sources": ["x"],
        }
        self.assertIsNone(self.main.metadata_from_browse_result(found))
        self.assertIsNone(
            self.main.metadata_from_decision({"strategy": "direct", "confidence": 0.9})
        )
        self.assertFalse(self.main.source_attribution_enabled("search"))
        self.assertEqual(self.main.source_attribution_settings()["enabled"], False)

    def test_browse_answer_still_shows_legacy_source_footer(self):
        client = FakeHTTPClient(
            ddg=ddg_ok("কাঁচা তথ্য।"),
            wiki_search=wiki_titles(),
            wiki_summary=wiki_summary(),
        )
        ask_ai = AsyncMock(return_value="গুছানো উত্তর।")
        with patch.object(
            self.main, "get_http_client", new=AsyncMock(return_value=client)
        ), patch.object(self.main, "ask_ai", new=ask_ai):
            answer = run(
                self.main._phase44_browse_and_answer(USER_ID, "প্রশ্ন", "বাংলা", False)
            )
        self.assertIn("গুছানো উত্তর।", answer)
        self.assertIn(
            "🔗 উৎস: https://bn.wikipedia.org/wiki/ঢাকা", answer
        )  # পুরোনো ফুটার
        self.assertIn("🔎 চেক করা হয়েছে:", answer)

    def test_search_command_still_works_without_attribution(self):
        client = FakeHTTPClient(
            ddg=ddg_ok("ব্যাজ ছাড়া উত্তর।"),
            wiki_search=wiki_titles(),
            wiki_summary=wiki_summary(),
        )
        update = FakeUpdate(USER_ID)
        ctx = FakeContext(["ব্যাজ", "ছাড়া"])
        with patch.object(
            self.main, "get_http_client", new=AsyncMock(return_value=client)
        ), patch.object(
            self.main, "ask_ai", new=AsyncMock(return_value="ব্যাজ ছাড়া উত্তর।")
        ), patch.object(
            self.main, "quota_guard", new=AsyncMock(return_value=True)
        ):
            run(self.main.search_command(update, ctx))
        text = "\n".join(update.message.sent)
        self.assertIn("🔎 সার্চ ফলাফল", text)
        self.assertIn("ব্যাজ ছাড়া উত্তর।", text)
        self.assertNotIn("📊 উৎস তথ্য", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
