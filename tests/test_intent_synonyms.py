"""Intent matching — synonym (সমার্থক শব্দ) expansion regression tests.

যা যাচাই করা হয়:
  1. expand_with_synonyms({"যোগ"}) — "add", "মোট", "মোট বের করো" ইত্যাদি
     একই-অর্থের শব্দও ফেরত আসে; অন্য গ্রুপের শব্দ ঢোকে না।
  2. "মোট বের করো" — "যোগ"/"add" কীওয়ার্ডের intent প্যাটার্নের সাথে কোনো সরাসরি
     টোকেন-মিল ছাড়াই (সমার্থক গ্রুপের মাধ্যমে) score হয়; পরিবর্তনের আগের
     algorithm-এ এটা None হতো।
  3. সম্পূর্ণ আলাদা অর্থের শব্দে (বা অন্য synonym গ্রুপের শব্দে) ভুলভাবে match হয় না।
  4. সমার্থক ছাড়া সরাসরি টোকেন-মিল আগের মতোই — পুরনো formula-এর সাথে একই স্কোর।

main.py-কে অস্থায়ী ডিরেক্টরিতে কপি করে import করা হয় (রিপোতে bot_data.db তৈরি
না হওয়ার জন্য), আর `bangla_synonyms.py`-র কপিও সেই ডিরেক্টরিতে রাখা হয় —
main.py-র ভেতরের `from bangla_synonyms import ...` যেন ঠিক সেই কপিটাই ধরে।

চালানো যায়:
    python3 tests/test_intent_synonyms.py
    python3 -m unittest tests.test_intent_synonyms -v
"""

from __future__ import annotations

import importlib.util
import logging
import os
import re
import shutil
import sys
import tempfile
import unittest


MODULE_NAME = "rohan_intent_synonym_test_main"


def _legacy_intent_score(pattern, text):
    """পরিবর্তনের আগের original intent algorithm — comparison-এর রেফারেন্স।"""
    intent_tokens = {t.strip().lower() for t in pattern.match_value.split(",") if t.strip()}
    text_tokens = set(re.findall(r"[\w\u0980-\u09FF]+", text.lower(), flags=re.UNICODE))
    if not intent_tokens or not text_tokens:
        return None
    overlap = len(intent_tokens & text_tokens)
    if overlap == 0:
        return None
    return (overlap / len(intent_tokens)) * pattern.confidence_score


class IntentSynonymTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-intent-synonym-")
        # main.py + bangla_synonyms.py — দুটোই workdir-এ, workdir sys.path-এর শুরুতে।
        for fname in ("main.py", "bangla_synonyms.py"):
            shutil.copyfile(os.path.join(repo_root, fname), os.path.join(cls.workdir, fname))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)
        sys.path.insert(0, cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        logging.disable(logging.CRITICAL)

        import bangla_synonyms  # noqa: E402  (workdir-এর কপি)

        cls.syn = bangla_synonyms

        spec = importlib.util.spec_from_file_location(MODULE_NAME, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[MODULE_NAME] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        sys.modules.pop(MODULE_NAME, None)
        sys.path.remove(cls.workdir)
        os.chdir(cls.old_cwd)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def make_pattern(self, match_value: str, confidence_score: float = 0.9):
        return self.main.BrainPattern(
            pattern_type="intent",
            match_value=match_value,
            category="test",
            confidence_score=confidence_score,
        )

    # ------------------------------------------------------------------
    # 1. expand_with_synonyms — বেসিক behavior
    # ------------------------------------------------------------------
    def test_synonym_expand_basic(self):
        expanded = self.syn.expand_with_synonyms({"যোগ"})
        for token in ("যোগ", "যোগ করো", "মোট", "মোট বের করো", "যুক্ত", "add", "addition", "সাম"):
            self.assertIn(token, expanded)
        # অন্য গ্রুপের শব্দ ঢুকবে না
        self.assertNotIn("delete", expanded)
        self.assertNotIn("help", expanded)
        # গ্রুপে না থাকলে সেট অপরিবর্তিত; খালি সেট-ও ভেঙে যায় না
        self.assertEqual(self.syn.expand_with_synonyms({"অজানাশব্দ"}), {"অজানাশব্দ"})
        self.assertEqual(self.syn.expand_with_synonyms(set()), set())

    # ------------------------------------------------------------------
    # 2. "মোট বের করো" → "যোগ" intent প্যাটার্ন (সমার্থক-মাধ্যমে মিল)
    # ------------------------------------------------------------------
    def test_intent_match_with_synonym(self):
        engine = self.main.PatternEngine()
        add_pat = self.make_pattern("যোগ, add")
        text = "মোট বের করো"

        # মেসেজের কোনো শব্দ match_value-এর সাথে সরাসরি মেলে না — মিলটা
        # শুধুই সমার্থক-গ্রুপের ফলে
        raw_tokens = set(re.findall(r"[\w\u0980-\u09FF]+", text.lower(), flags=re.UNICODE))
        self.assertEqual({"যোগ", "add"} & raw_tokens, set())
        # পুরনো algorithm-এ এটা match হতো না
        self.assertIsNone(_legacy_intent_score(add_pat, text))

        score = engine._score_pattern(add_pat, text)
        self.assertIsNotNone(score)
        # overlap = {"যোগ", "add"} (দুটোই গ্রুপ-প্রসারণে পাওয়া) → 2/2 * 0.9
        self.assertAlmostEqual(score, 0.9)

    # ------------------------------------------------------------------
    # 3. আলাদা অর্থের শব্দে false-positive নেই
    # ------------------------------------------------------------------
    def test_intent_no_false_positive(self):
        engine = self.main.PatternEngine()
        add_pat = self.make_pattern("যোগ, add")

        # কোনো শব্দই কোনো synonym গ্রুপে নেই → expand করলেও মিলবে না
        for text in ("আজ কেমন খবর", "আমার নাম রোহান", "বইটা পড়া শেষ"):
            with self.subTest(text=text):
                self.assertIsNone(engine._score_pattern(add_pat, text), text)

        # অন্য synonym গ্রুপের শব্দ (তালিকা/দেখাও) → add-intent-এর সাথে মেলে না
        help_pat = self.make_pattern("সাহায্য, help")
        self.assertIsNone(engine._score_pattern(help_pat, "তালিকা দেখাও"))

    # ------------------------------------------------------------------
    # 4. সমার্থক ছাড়া সরাসরি মিল — আগের মতোই (পুরনো formula-র সাথে একই)
    # ------------------------------------------------------------------
    def test_existing_intent_unchanged(self):
        engine = self.main.PatternEngine()
        pat = self.make_pattern("সংখ্যা, count", confidence_score=0.8)

        for text in ("একটা সংখ্যা দাও", "সংখ্যা count করো", "ফলটা যুক্ত হলে কেমন হয়"):
            with self.subTest(text=text):
                self.assertEqual(
                    engine._score_pattern(pat, text),
                    _legacy_intent_score(pat, text),
                )

        # স্পষ্ট expected মান — পুরনো formula: (overlap / len(intent_tokens)) * confidence
        self.assertAlmostEqual(engine._score_pattern(pat, "একটা সংখ্যা দাও"), (1 / 2) * 0.8)
        self.assertAlmostEqual(engine._score_pattern(pat, "সংখ্যা count করো"), 1.0 * 0.8)
        # "যুক্ত" যোগ-গ্রুপে থাকলেও {সংখ্যা, count}-এর সাথে কোনো মিল নেই
        self.assertIsNone(engine._score_pattern(pat, "ফলটা যুক্ত হলে কেমন হয়"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
