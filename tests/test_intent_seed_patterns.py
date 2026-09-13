"""Brain OS seed — intent (সমার্থক-শব্দভিত্তিক) প্যাটার্নের টেস্ট।

পটভূমি: PR #27-এ `bangla_synonyms.py` আর `PatternEngine._score_pattern()`-এ synonym
expansion যোগ হয়, কিন্তু `BRAIN_OS_SEED_PATTERNS`-এ তখন শুধু `keyword` প্যাটার্ন ছিল —
তাই লাইভ বটে কোনো `intent` প্যাটার্নই ম্যাচ হতো না ("মোট বের করো" সাধারণ প্রশ্ন ধরে
সোজা ওয়েব-সার্চে চলে যেত)। এই টেস্ট সেই seed এন্ট্রিগুলো যাচাই করে।

যা যাচাই করা হয়:
  1. seed_brain_os_defaults()-এর পরে ডাটাবেজে intent প্যাটার্ন আছে (নাম/টাইপসহ), আর
     seed দুবার চালালেও ডুপ্লিকেট তৈরি হয় না।
  2. প্রতিটা intent প্যাটার্নের match_value-র প্রতিটা শব্দ bangla_synonyms.SYNONYM_GROUPS-এর
     কোনো-না-কোনো গ্রুপে আছে (অর্থাৎ seed আর synonym লাইব্রেরি সামঞ্জস্যপূর্ণ)।
  3. **মূল কেস** — seed-এর পর simulate_message("মোট বের করো") চালালে add_numbers intent
     প্যাটার্নটাই ম্যাচ করে এবং Decision Engine "direct" বলে — ফলে ওয়েব-সার্চ
     (_automatic_browse_answer) বা AI কল হয়ই না, সরাসরি প্যাটার্নের উত্তর ফেরে।
  4. ম্যাচটা সত্যিই সমার্থক-প্রসারণের ফল: synonym ছাড়া (পুরনো algorithm) একই প্যাটার্নের
     স্কোর direct-থ্রেশহোল্ডের (0.72) নিচে থাকত।
  5. রিগ্রেশন — সংখ্যা-সহ হিসাব ("৫ আর ৩ যোগ করো") ক্যান্ড উত্তরের কাছে আটকে না গিয়ে
     আগের মতোই AI-পথে যায়; "কমান্ড দেখাও"-তে পুরনো keyword প্যাটার্নই জেতে;
     অসম্পর্কিত টেক্সটে কোনো intent মেলে না।

চালানো যায়:
    python3 tests/test_intent_seed_patterns.py
    python3 -m unittest tests.test_intent_seed_patterns -v
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

MODULE_NAME = "rohan_intent_seed_test_main"
TEST_USER_ID = 990000077

# seed-এ যে intent প্যাটার্নগুলো আশা করা হচ্ছে (name -> প্রত্যাশিত category)
EXPECTED_INTENTS = {
    "add_numbers": "math",
    "subtract_numbers": "math",
    "multiply_numbers": "math",
    "divide_numbers": "math",
    "print_output": "bot_info",
    "help_support": "bot_info",
}

# Decision Engine-এ direct উত্তরের confidence-থ্রেশহোল্ড (main.py: DecisionEngine.execute)
DIRECT_CONFIDENCE_THRESHOLD = 0.72


def run(coro):
    # unittest-এ আগের কোনো মডিউল asyncio.run() ব্যবহার করলে গ্লোবাল loop None হয়ে যেতে
    # পারে (Python 3.11+) — তখন নতুন loop বানিয়ে নেওয়া হয়।
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def _legacy_intent_score(pattern, text):
    """synonym-expansion যোগ হওয়ার আগের original intent algorithm (রেফারেন্স)।"""
    intent_tokens = {t.strip().lower() for t in pattern.match_value.split(",") if t.strip()}
    text_tokens = set(re.findall(r"[\w\u0980-\u09FF]+", text.lower(), flags=re.UNICODE))
    if not intent_tokens or not text_tokens:
        return None
    overlap = len(intent_tokens & text_tokens)
    if overlap == 0:
        return None
    return (overlap / len(intent_tokens)) * pattern.confidence_score


class IntentSeedPatternTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # main.py + bangla_synonyms.py টেম্প-ডিরেক্টরিতে কপি করে চালানো হয় — রিপোতে
        # bot_data.db তৈরি না হওয়ার জন্য (অন্য টেস্ট ফাইলগুলোর একই প্যাটার্ন)।
        cls.workdir = tempfile.mkdtemp(prefix="rohan-intent-seed-")
        for fname in ("main.py", "bangla_synonyms.py"):
            shutil.copyfile(os.path.join(REPO_ROOT, fname), os.path.join(cls.workdir, fname))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)
        sys.path.insert(0, cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        os.environ.pop("TAVILY_API_KEY", None)  # টেস্ট নিজে নেটওয়ার্ক নিয়ন্ত্রণ করবে

        logging.disable(logging.CRITICAL)

        import bangla_synonyms  # noqa: E402  (workdir-এর কপি)

        cls.syn = bangla_synonyms

        spec = importlib.util.spec_from_file_location(MODULE_NAME, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[MODULE_NAME] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        cls.main.seed_brain_os_defaults()
        cls.main.register_user(TEST_USER_ID)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        sys.modules.pop(MODULE_NAME, None)
        if cls.workdir in sys.path:
            sys.path.remove(cls.workdir)
        os.chdir(cls.old_cwd)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def setUp(self):
        # প্রতিটা টেস্টে flood/quota/decision-cache স্টেট পরিষ্কার
        self.main._last_message_time.clear()
        self.main._flood_strikes.clear()
        self.main._flood_blocked_until.clear()
        self.main.decision_engine_service.clear_cache()

    # ------------------------------------------------------------------
    # হেল্পার
    # ------------------------------------------------------------------
    def engine(self):
        return self.main.PatternEngine()

    def intent_by_name(self, name: str):
        for pattern in self.engine().list_by_type("intent"):
            if pattern.name == name:
                return pattern
        return None

    def top_match(self, text: str):
        matches = self.engine().match(text, log_analytics=False)
        return matches[0]["pattern"] if matches else None

    def decide(self, text: str):
        return self.main.decision_engine_service.execute(
            text, user_id=TEST_USER_ID, session_key=str(TEST_USER_ID)
        )

    def simulate_offline(self, text: str):
        """simulate_message চালায় — ওয়েব-সার্চ/AI পথ মক করা, যাতে কোনটা কল হলো দেখা যায়।"""
        browse = AsyncMock(return_value="")
        ask = AsyncMock(return_value="টেস্ট AI উত্তর")
        ask_history = AsyncMock(return_value="টেস্ট AI উত্তর")
        with patch.object(self.main, "_automatic_browse_answer", new=browse), \
                patch.object(self.main, "ask_ai", new=ask), \
                patch.object(self.main, "ask_ai_with_history", new=ask_history), \
                patch.object(self.main, "should_show_own_key_hint", return_value=False):
            result = run(self.main.simulate_message(text, TEST_USER_ID))
        return result, browse, ask, ask_history

    # ------------------------------------------------------------------
    # 1. seed-এ intent প্যাটার্ন তৈরি হয় (আর idempotent)
    # ------------------------------------------------------------------
    def test_seed_creates_expected_intent_patterns(self):
        intents = {p.name: p for p in self.engine().list_by_type("intent")}
        self.assertEqual(set(intents), set(EXPECTED_INTENTS))
        for name, category in EXPECTED_INTENTS.items():
            with self.subTest(intent=name):
                self.assertEqual(intents[name].pattern_type, "intent")
                self.assertEqual(intents[name].category, category)
                self.assertTrue(intents[name].match_value.strip())
                self.assertTrue(intents[name].description.strip())

    def test_seed_is_idempotent(self):
        engine = self.engine()
        before_intent = len(engine.list_by_type("intent"))
        before_keyword = len(engine.list_by_type("keyword"))
        self.main.seed_brain_os_defaults()
        engine._invalidate_cache()
        self.assertEqual(len(engine.list_by_type("intent")), before_intent)
        self.assertEqual(len(engine.list_by_type("keyword")), before_keyword)

    # ------------------------------------------------------------------
    # 2. match_value ↔ SYNONYM_GROUPS সামঞ্জস্য
    # ------------------------------------------------------------------
    def test_match_values_are_synonym_group_members(self):
        for name in EXPECTED_INTENTS:
            pattern = self.intent_by_name(name)
            tokens = [t.strip() for t in pattern.match_value.split(",") if t.strip()]
            for token in tokens:
                with self.subTest(intent=name, token=token):
                    self.assertTrue(
                        any(token in group for group in self.syn.SYNONYM_GROUPS),
                        f"{token!r} কোনো SYNONYM_GROUPS গ্রুপে নেই",
                    )

    # ------------------------------------------------------------------
    # 3. মূল কেস — "মোট বের করো" → add_numbers intent, ওয়েব-সার্চ নয়
    # ------------------------------------------------------------------
    def test_total_request_matches_add_intent(self):
        pattern = self.top_match("মোট বের করো")
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.pattern_type, "intent")
        self.assertEqual(pattern.name, "add_numbers")

        decision = self.decide("মোট বের করো")
        self.assertEqual(decision["stage"], "pattern")
        self.assertEqual(decision["strategy"], "direct")
        self.assertEqual(decision["payload"]["pattern"].name, "add_numbers")

    def test_simulate_message_total_uses_intent_not_web_search(self):
        add_pattern = self.intent_by_name("add_numbers")
        result, browse, ask, ask_history = self.simulate_offline("মোট বের করো")

        self.assertEqual(result["status"], "ok")
        # ওয়েব-সার্চ বা AI — কোনোটাই ডাকা হয়নি
        browse.assert_not_awaited()
        ask.assert_not_awaited()
        ask_history.assert_not_awaited()
        # বটের উত্তর = intent প্যাটার্নের description (উৎস-ব্যাজসহ হতে পারে)
        reply = "\n".join(result["replies"])
        self.assertIn(add_pattern.description.splitlines()[0], reply)
        self.assertNotIn("ভাবছি...", reply[-1])  # শেষ রিপ্লাই আসল উত্তর, thinking-প্লেসহোল্ডার নয়

    # ------------------------------------------------------------------
    # 4. ম্যাচটা সমার্থক-প্রসারণের ফলেই (synonym ছাড়া direct হতো না)
    # ------------------------------------------------------------------
    def test_match_depends_on_synonym_expansion(self):
        pattern = self.intent_by_name("add_numbers")
        text = "মোট বের করো"

        score = self.engine()._score_pattern(pattern, text)
        self.assertIsNotNone(score)
        self.assertGreaterEqual(score, DIRECT_CONFIDENCE_THRESHOLD)

        legacy = _legacy_intent_score(pattern, text)
        self.assertTrue(
            legacy is None or legacy < DIRECT_CONFIDENCE_THRESHOLD,
            f"synonym ছাড়াও স্কোর {legacy} — ম্যাচটা সমার্থক-প্রসারণের ফল নয়",
        )

    # ------------------------------------------------------------------
    # 5. রিগ্রেশন — বিদ্যমান আচরণ অক্ষত
    # ------------------------------------------------------------------
    def test_arithmetic_with_numbers_still_goes_to_ai(self):
        add_pattern = self.intent_by_name("add_numbers")
        result, browse, ask, ask_history = self.simulate_offline("৫ আর ৩ যোগ করো")

        self.assertEqual(result["status"], "ok")
        reply = "\n".join(result["replies"])
        # ক্যান্ড intent-উত্তর ফেরেনি — সংখ্যা-সহ হিসাব AI-এর কাছেই যায়
        self.assertNotIn(add_pattern.description.splitlines()[0], reply)
        self.assertTrue(
            ask.await_count or ask_history.await_count or browse.await_count,
            "সংখ্যা-সহ হিসাবও সরাসরি প্যাটার্ন-উত্তরে আটকে গেছে",
        )

    def test_bare_operation_words_are_detected_as_intents(self):
        expected = {
            "যোগ করো": "add_numbers",
            "বিয়োগ করো": "subtract_numbers",
            "গুণ করো": "multiply_numbers",
            "ভাগ করো": "divide_numbers",
        }
        for text, name in expected.items():
            with self.subTest(text=text):
                pattern = self.top_match(text)
                self.assertIsNotNone(pattern, text)
                self.assertEqual(pattern.pattern_type, "intent")
                self.assertEqual(pattern.name, name)

    def test_existing_keyword_patterns_still_win(self):
        # print_output intent-এর priority কম — তাই "কমান্ড দেখাও"-তে পুরনো keyword প্যাটার্নই জেতে
        pattern = self.top_match("কমান্ড দেখাও")
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.pattern_type, "keyword")
        self.assertEqual(pattern.name, "commands_bn")
        self.assertEqual(self.decide("কমান্ড দেখাও")["strategy"], "direct")

        for text, name in (("হ্যালো", "greeting_hello_bn"), ("help", "help_en")):
            with self.subTest(text=text):
                self.assertEqual(self.top_match(text).name, name)

    def test_print_and_help_intents_answer_directly(self):
        for text, name in (("প্রিন্ট করো", "print_output"), ("সাহায্য করো", "help_support")):
            with self.subTest(text=text):
                decision = self.decide(text)
                self.assertEqual(decision["stage"], "pattern")
                self.assertEqual(decision["strategy"], "direct")
                self.assertEqual(decision["payload"]["pattern"].name, name)

    def test_generic_show_request_not_hijacked(self):
        # "দেখাও" print-গ্রুপের শব্দ হলেও match_value-তে নেই — তাই সাধারণ অনুরোধ
        # আগের মতোই AI/পরের ধাপে যায় (ক্যান্ড প্রিন্ট-উত্তর চাপে না)।
        self.assertNotEqual(self.decide("তালিকা দেখাও")["strategy"], "direct")

    def test_unrelated_text_has_no_intent_match(self):
        for text in ("আজকের আবহাওয়া কেমন", "আমার নাম রোহান"):
            with self.subTest(text=text):
                pattern = self.top_match(text)
                self.assertTrue(
                    pattern is None or pattern.pattern_type != "intent",
                    f"{text!r}-এ ভুলভাবে intent ম্যাচ করেছে",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
