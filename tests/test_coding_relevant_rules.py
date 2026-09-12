"""Coding AI prompt-এ "প্রাসঙ্গিক নিয়ম/গাইডলাইন" (relevant_rules) ইনজেকশনের টেস্ট।

গ্যাপ: Decision Engine (Phase 17) থেকে knowledge/pattern/template ম্যাচ এসেও
`_coding_result_looks_like_code()` চেকে ফেল করলে এন্ট্রিটা আগে সম্পূর্ণ বাতিল হয়ে
যেত — ইউজারের /addknowledge, /addpattern, /addtemplate-এ দেওয়া কোডিং-স্ট্যান্ডার্ড
(টেক্সট-রুল) AI-এর কাছে কখনোই পৌঁছাত না। এখন সেগুলো candidate list থেকে confidence
অনুযায়ী শীর্ষ ৩টা (প্রতিটা ৪০০ ক্যারেক্টারে truncation করে) system_prompt-এর
"অবশ্যই মেনে চলার নিয়ম" সেকশনে ঢোকে।

চালানো যায়:
    python3 tests/test_coding_relevant_rules.py
    python3 -m unittest tests.test_coding_relevant_rules -v
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

USER_ID = 900202


class _MainLoaderMixin:
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-rules-")
        shutil.copyfile(os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        logging.disable(logging.CRITICAL)

        module_name = "rohan_rules_test_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        cls.main.seed_brain_os_defaults()
        cls.main.register_user(USER_ID)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_rules_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def setUp(self):
        self.main.decision_engine_service.clear_cache()


class RuleTextClassificationTests(_MainLoaderMixin, unittest.TestCase):
    """_rule_text_looks_like_code — কোন এন্ট্রি 'কোড' (বাদ যাবে), কোনটা 'রুল' (নেওয়া হবে)।"""

    def test_prose_rules_are_not_code(self):
        looks = self.main._rule_text_looks_like_code
        self.assertFalse(looks("প্রতিটা ফাংশনের নাম snake_case রাখো এবং docstring দাও।"))
        self.assertFalse(looks("Never use print() in library code; logging module is the right choice."))
        self.assertFalse(looks("Use tabs for indentation and keep lines under 100 chars."))

    def test_real_code_blocks_are_code(self):
        looks = self.main._rule_text_looks_like_code
        self.assertTrue(looks("```\ndef f():\n    return 1\n```"))
        self.assertTrue(looks("import os\nimport sys\n"))
        self.assertTrue(looks("def helper():\n    return 42"))
        self.assertTrue(looks("from flask import Flask\napp = Flask(__name__)"))
        self.assertFalse(looks(""))
        self.assertFalse(looks(None))  # type: ignore[arg-type]


class CollectRelevantBrainRulesTests(_MainLoaderMixin, unittest.TestCase):
    """_collect_relevant_brain_rules — candidate list → top-3 truncation-সহ রুল লিস্ট।"""

    def _cand(self, stage, confidence, content, **extra):
        payload = {"content": content, "category": "coding_standards"}
        payload.update(extra)
        return {"stage": stage, "confidence": confidence, "score": 60.0, "payload": payload}

    def test_top_entries_by_confidence_capped_and_truncated(self):
        long_rule = "ক " + "নিয়ম " * 300  # ৪০০+ ক্যারেক্টার
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            "payload": {"content": "সবার উপরের নিয়মটা সবচেয়ে জোরালো — এটাই প্রথমে আসবে।"},
            "candidates": [
                self._cand("ai", 0.99, ""),  # ai stage কখনো রুল নয়
                self._cand("knowledge", 0.60, "সবচেয়ে কম confidence — বাদ পড়বে (শীর্ষ ৩-এর বাইরে)।"),
                self._cand("knowledge", 0.90, "শীর্ষ confidence-এর নিয়ম A"),
                self._cand("pattern", 0.80, long_rule),
                self._cand("template", 0.70, "মাঝের নিয়ম C"),
                self._cand("documentation", 0.65, "মাঝের নিয়ম C"),  # হুবহু ডুপ্লিকেট — একবারই
            ],
        }
        rules = self.main._collect_relevant_brain_rules(decision, "python")
        self.assertEqual(len(rules), 3)
        self.assertEqual(rules[0], "শীর্ষ confidence-এর নিয়ম A")
        # ৪০০ ক্যারেক্টারে truncation
        self.assertLessEqual(len(rules[1]), self.main.CODING_RULE_TEXT_MAX_CHARS)
        self.assertTrue(rules[1].startswith("ক নিয়ম"))
        self.assertEqual(rules[2], "মাঝের নিয়ম C")
        self.assertNotIn("সবচেয়ে কম confidence — বাদ পড়বে (শীর্ষ ৩-এর বাইরে)।", rules)

    def test_skips_code_like_entries_faq_and_dupes(self):
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            "payload": {},
            "candidates": [
                self._cand("knowledge", 0.9, "def broken():\n    return 1"),
                self._cand("knowledge", 0.85, "সব কমান্ডের তালিকা দেখতে /help অথবা /menu লিখুন।"),  # FAQ
                self._cand("knowledge", 0.8, "হয় না"),  # < ৮ ক্যারেক্টার — বাদ
                self._cand("knowledge", 0.7, "ডুপ্লিকেট রুল একবারই আসবে, বারবার নয়।"),
                self._cand("knowledge", 0.69, "ডুপ্লিকেট রুল একবারই আসবে, বারবার নয়।"),
            ],
        }
        rules = self.main._collect_relevant_brain_rules(decision, "python")
        self.assertEqual(rules, ["ডুপ্লিকেট রুল একবারই আসবে, বারবার নয়।"])

    def test_falls_back_to_best_payload_without_candidates_key(self):
        # মক/পুরোনো decision — candidates নেই, best payload-টাই রুল হিসেবে বিবেচ্য
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.8,
            "payload": {"content": "TODO কমেন্ট ফাইনাল কোডে রাখবে না, রিভিউতে ধরা পড়ে।", "category": "coding"},
        }
        rules = self.main._collect_relevant_brain_rules(decision, "python")
        self.assertEqual(rules, ["TODO কমেন্ট ফাইনাল কোডে রাখবে না, রিভিউতে ধরা পড়ে।"])

    def test_empty_or_broken_decision_is_safe(self):
        self.assertEqual(self.main._collect_relevant_brain_rules({}, "python"), [])
        self.assertEqual(
            self.main._collect_relevant_brain_rules({"candidates": [1, 2, None]}, "python"), []
        )


class DecisionEngineCandidateAttachmentTests(_MainLoaderMixin, unittest.TestCase):
    """DecisionEngine.execute() এখন সাজানো top-candidates সংযোজন করে রাখে।"""

    def test_execute_attaches_top_candidates(self):
        marker = f"kanidha_{abs(hash('rules')) % 10**6}"
        self.main.KnowledgeEngine().create(
            "coding_standards", f"স্টাইল নিয়ম {marker}",
            f"এই {marker} এন্ট্রিটা রুল টেক্সট — কোড নয়, তাই prompt-এ নির্দেশনা হিসেবে যাবে।",
            confidence_score=0.95,
        )
        decision = self.main.decision_engine_service.execute(
            f"Project: x\nStack: python\nTask: helper\nDescription: {marker} মেনে utility ফাংশন",
            exclude_categories=list(self.main.CODING_EXCLUDED_BRAIN_CATEGORIES),
        )
        self.assertIn("candidates", decision)
        cands = decision["candidates"]
        self.assertTrue(1 <= len(cands) <= self.main.DECISION_CANDIDATES_KEPT)
        contents = [str((c.get("payload") or {}).get("content", "")) for c in cands if isinstance(c.get("payload"), dict)]
        self.assertTrue(any(marker in txt for txt in contents), contents)
        # cached decision-ও একই শেপ বজায় রাখে
        again = self.main.decision_engine_service.execute(
            f"Project: x\nStack: python\nTask: helper\nDescription: {marker} মেনে utility ফাংশন",
            exclude_categories=list(self.main.CODING_EXCLUDED_BRAIN_CATEGORIES),
        )
        self.assertTrue(again.get("cached"))
        self.assertIn("candidates", again)

    def test_rule_reaches_system_prompt_real_engine(self):
        """ইউজারের /addknowledge-ধরনের রুল-টাইপ (non-code) এন্ট্রি ম্যাচ হলে সেটা
        AI-এর system_prompt-এ অন্তর্ভুক্ত হয় কি না — পুরো end-to-end যাচাই।"""
        # নোট: রুলের টেক্সটে "import ", "def " জাতীয় কোড-মার্কার থাকলে
        # _coding_result_looks_like_code সেটাকে কোড বলে ভুল করবে — এখানে ইচ্ছাকৃত
        #ভাবে খাঁটি গদ্য রুল রাখা হয়েছে যাতে "রুল হিসেবে prompt-এ যাওয়া" পথটিই ধরা পড়ে।
        marker = "ronodhara_marker"
        self.main.KnowledgeEngine().create(
            "coding_standards", "নামকরণ নীতি",
            f"রান-অফলাইন টুলে সবসময় {marker} অনুযায়ী সাপোর্ট ফাংশন আলাদা ফাইলে রাখো, এক ফাইলে গুলিয়ে লিখবে না।",
            confidence_score=0.9,
        )
        project_id = self.main.create_code_project(
            USER_ID, "রুল ইনজেকশন প্রজ", "utils", "python",
            [{"title": "helper ভাগ", "description": f"{marker} ফলো করে একটা সাপোর্ট helper আলাদা ফাইলে সাজাও"}],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)
        fake_code = "import os\n\ndef helper():\n    return os.getcwd()\n"

        async def run():
            with patch.object(self.main, "ask_ai", new=AsyncMock(return_value=fake_code)) as ask_ai:
                result = await self.main.process_next_code_task(project)
            return result, ask_ai

        result, ask_ai = asyncio.run(run())
        # টাস্কটা AI রুটেই গেছে (dynamic/fixed KB/brain direct কোনোটাতেই resolve হয়নি)
        self.assertEqual(result.get("source"), "ai")
        self.assertIsNotNone(ask_ai.await_args, "ask_ai was not called")
        system_prompt = ask_ai.await_args.args[0]
        self.assertIn("এই ধাপের কোড লেখার সময় নিচের প্রাসঙ্গিক নিয়ম/গাইডলাইনগুলো অবশ্যই মেনে চলো:", system_prompt)
        self.assertIn(marker, system_prompt)

    def test_rule_reaches_prompt_with_mocked_direct_noncode_match(self):
        project_id = self.main.create_code_project(
            USER_ID, "মক রুল প্রজ", "api layer", "python",
            [{"title": "API layer", "description": "repository pattern আলাদা লেয়ারে সাজানো handler"}],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)
        rule_a = "প্রতিটা API handler slim রাখো — ব্যবসা-লজিক service লেয়ারে যাবে।"
        rule_b = "এরর রেসপন্সে ধ্রুপদী HTTP স্ট্যাটাস কোড ব্যবহার করো, কাস্টম নয়।"
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            # best payload নিজে একটা রুল টেক্সট → কোড-চেকে ফেল করবে → তবু ফেলবে না
            "payload": {"content": rule_a, "category": "coding_standards"},
            "candidates": [
                {"stage": "knowledge", "confidence": 0.9, "score": 80, "payload": {"content": rule_a, "category": "coding_standards"}},
                {"stage": "pattern", "confidence": 0.85, "score": 70, "payload": {"pattern": {"category": "coding", "description": rule_b}}},
                {"stage": "knowledge", "confidence": 0.5, "score": 60, "payload": {"content": "```\nimport os\n```"}},  # কোড → বাদ
                {"stage": "ai", "confidence": 0.55, "score": 45, "payload": {}},  # বাদ
            ],
        }
        fake_code = "from flask import Blueprint\nbp = Blueprint('api', __name__)\n"

        async def run():
            with patch.object(
                self.main, "decision_engine_service",
                **{"execute_async": AsyncMock(return_value=decision)},
            ), patch.object(self.main, "ask_ai", new=AsyncMock(return_value=fake_code)) as ask_ai:
                result = await self.main.process_next_code_task(project)
            return result, ask_ai

        result, ask_ai = asyncio.run(run())
        self.assertEqual(result.get("source"), "ai")  # রুল কোড নয় বলে AI রুটেই পড়ল
        sp = ask_ai.await_args.args[0]
        self.assertIn("নিচের প্রাসঙ্গিক নিয়ম/গাইডলাইনগুলো অবশ্যই মেনে চলো:", sp)
        self.assertIn(f"- {rule_a}", sp)
        self.assertIn(f"- {rule_b}", sp)
        self.assertNotIn("Blueprint", sp.split("মেনে চলো:")[-1])  # কোড-এন্ট্রি রুল সেকশনে ঢুকল না

    def test_ai_strategy_with_low_confidence_rule_also_included(self):
        project_id = self.main.create_code_project(
            USER_ID, "ai strategy প্রজ", "cache", "python",
            [{"title": "cache wrapper", "description": "ttl cache decorator টুল র‍্যাপার"}],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)
        decision = {
            "strategy": "ai",
            "stage": "ai",
            "confidence": 0.55,
            "payload": {},
            "candidates": [
                {"stage": "knowledge", "confidence": 0.6, "score": 66,
                 "payload": {"content": "ক্যাশে টাইমাউট বাধ্যতামূলক, অনন্ত ক্যাশে চলবে না — ধরা পড়লে রিভিউতে ঠেকানো হবে।",
                             "category": "coding_standards"}},
                {"stage": "ai", "confidence": 0.55, "score": 45, "payload": {}},
            ],
        }

        async def run():
            with patch.object(
                self.main, "decision_engine_service",
                **{"execute_async": AsyncMock(return_value=decision)},
            ), patch.object(self.main, "ask_ai", new=AsyncMock(return_value="def ttl_cache():\n    ...\n")) as ask_ai:
                result = await self.main.process_next_code_task(project)
            return result, ask_ai

        result, ask_ai = asyncio.run(run())
        self.assertEqual(result.get("source"), "ai")
        sp = ask_ai.await_args.args[0]
        self.assertIn("ক্যাশে টাইমাউট বাধ্যতামূলক", sp)

    def test_direct_code_match_still_short_circuits_without_rules(self):
        project_id = self.main.create_code_project(
            USER_ID, "direct code প্রজ", "retry", "python",
            [{"title": "retry helper", "description": "এক্সপোনেনশিয়াল ব্যাকঅফ হেল্পার মডিউল"}],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)
        real_code = "import time\n\n\ndef backoff(attempt: int) -> float:\n    return 2 ** attempt\n"
        decision = {
            "strategy": "direct",
            "stage": "knowledge",
            "confidence": 0.9,
            "payload": {"content": f"```\n{real_code}```", "category": "coding_standards"},
            "candidates": [
                {"stage": "knowledge", "confidence": 0.9, "score": 80,
                 "payload": {"content": f"```\n{real_code}```", "category": "coding_standards"}},
            ],
        }

        async def run():
            with patch.object(
                self.main, "decision_engine_service",
                **{"execute_async": AsyncMock(return_value=decision)},
            ), patch.object(self.main, "ask_ai", new=AsyncMock()) as ask_ai:
                result = await self.main.process_next_code_task(project)
            return result, ask_ai

        result, ask_ai = asyncio.run(run())
        # কোড-চেক পাস → brain direct-এই সেভ, AI কলই হবে না
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["source"], "brain:knowledge")
        self.assertIn("def backoff", result["code"])
        ask_ai.assert_not_awaited()


if __name__ == "__main__":
    unittest.main(verbosity=2)
