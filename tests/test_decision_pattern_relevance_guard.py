"""Decision Engine — Pattern stage relevance guard regression tests.

যা যাচাই করা হয়:
  1. PatternEngine keyword matching এখন whole-word — \"কমান্ড\" কোনো বড় বাক্যের
     দূরবর্তী substring বা \"helpful\"-এর ভেতর \"help\" হিসেবে মেলে না।
  2. Coding-context DecisionEngine.execute(..., exclude_categories=[\"bot_info\",\"greeting\"])
     greeting/bot-info FAQ-কে candidate থেকে সম্পূর্ণ বাদ দেয়।
  3. সাধারণ চ্যাটে (exclude ছাড়া) \"হ্যালো\"/\"ধন্যবাদ\"/\"কমান্ড\" আগের মতোই direct কাজ করে।
  4. process_next_code_task greeting/bot-info FAQ-কে task.code হিসেবে সেভ করে না —
     AI রুটে যায় (বা no-api-তে fail), done+FAQ হয় না।
  5. _coding_result_looks_like_code FAQ টেক্সট reject করে, আসল কোড accept করে।

চালানো যায়:
    python3 tests/test_decision_pattern_relevance_guard.py
    python3 -m unittest tests.test_decision_pattern_relevance_guard -v
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


USER_ID = 662211


class DecisionPatternRelevanceGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-pattern-guard-")
        shutil.copyfile(os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        logging.disable(logging.CRITICAL)

        module_name = "rohan_pattern_guard_test_main"
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
        sys.modules.pop("rohan_pattern_guard_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def setUp(self):
        self.main.decision_engine_service.clear_cache()

    # ------------------------------------------------------------------
    # 1. Whole-word keyword matching
    # ------------------------------------------------------------------
    def test_keyword_does_not_match_distant_substring_or_larger_word(self):
        engine = self.main.PatternEngine()
        command_pat = self.main.BrainPattern(
            pattern_type="keyword",
            match_value="কমান্ড",
            category="bot_info",
            confidence_score=0.8,
        )
        help_pat = self.main.BrainPattern(
            pattern_type="keyword",
            match_value="help",
            category="bot_info",
            confidence_score=0.85,
        )
        # The original bug: incidental \"কমান্ড\"-less coding text, or a larger word.
        self.assertIsNone(
            engine._score_pattern(command_pat, "একটা কোড লেখা যে রান করলে সফল হয়েছে লেখা আসবে")
        )
        self.assertIsNone(engine._score_pattern(command_pat, "কমান্ডারকে বলো প্রোগ্রাম চালাতে"))
        self.assertIsNone(engine._score_pattern(help_pat, "this is a helpful coding hint"))
        # Whole-word still matches in ordinary chat.
        self.assertIsNotNone(engine._score_pattern(command_pat, "কমান্ড তালিকা চাই"))
        self.assertIsNotNone(engine._score_pattern(help_pat, "I need help"))
        self.assertIsNotNone(engine._score_pattern(help_pat, "/help"))

    def test_whole_word_helper_handles_phrases_and_errors(self):
        self.assertTrue(self.main._whole_word_in_text("thank you", "Thank   you so much"))
        self.assertTrue(self.main._whole_word_in_text("হ্যালো", "হ্যালো!"))
        self.assertFalse(self.main._whole_word_in_text("help", "helpful"))
        self.assertFalse(self.main._whole_word_in_text("", "hello"))
        self.assertFalse(self.main._whole_word_in_text("hello", None))  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # 2 + 3. Category-aware Decision Engine
    # ------------------------------------------------------------------
    def test_chat_greetings_and_bot_info_still_direct(self):
        engine = self.main.decision_engine_service
        for query in ("হ্যালো", "ধন্যবাদ", "কমান্ড", "hello"):
            with self.subTest(query=query):
                decision = engine.execute(query)
                self.assertEqual(decision["strategy"], "direct", decision)
                self.assertIn(decision["stage"], ("pattern", "knowledge"), decision)
                answer = self.main._brain_payload_to_answer(decision.get("payload"))
                self.assertTrue(answer.strip(), f"empty answer for {query!r}")
                self.assertFalse(
                    self.main._coding_result_looks_like_code(answer, "python"),
                    f"chat FAQ unexpectedly looks like code: {answer[:80]!r}",
                )

    def test_coding_context_excludes_bot_info_and_greeting(self):
        engine = self.main.decision_engine_service
        coding_request = (
            "Project: demo\nStack: python\n"
            "Task: প্রোগ্রাম চালান\n"
            "Description: রান করলে সফল হয়েছে লেখা আসবে এবং প্রয়োজনীয় কমান্ড লিখুন"
        )
        excluded = engine.execute(
            coding_request,
            exclude_categories=list(self.main.CODING_EXCLUDED_BRAIN_CATEGORIES),
        )
        self.assertNotEqual(excluded.get("stage"), "pattern")
        self.assertNotIn(_payload_cat(excluded.get("payload")), {"bot_info", "greeting"})
        if excluded.get("strategy") == "direct":
            answer = self.main._brain_payload_to_answer(excluded.get("payload"))
            self.assertNotIn("কমান্ডের তালিকা", answer)
            self.assertNotIn("/help", answer)

        # Same request without exclude may still pick the incidental \"কমান্ড\" whole-word
        # (that's why category-scoping is the reliable coding-orchestrator fix).
        open_decision = engine.execute(coding_request)
        self.assertIn(open_decision.get("stage"), ("pattern", "knowledge", "ai", "documentation", "template"))

    def test_exclude_categories_does_not_break_empty_or_unknown(self):
        engine = self.main.decision_engine_service
        decision = engine.execute("হ্যালো", exclude_categories=["no_such_category"])
        self.assertEqual(decision["strategy"], "direct")
        decision = engine.execute("হ্যালো", exclude_categories=None)
        self.assertEqual(decision["strategy"], "direct")

    # ------------------------------------------------------------------
    # 4. process_next_code_task must not save FAQ as code
    # ------------------------------------------------------------------
    def test_process_next_code_task_does_not_save_bot_info_faq(self):
        project_id = self.main.create_code_project(
            USER_ID,
            "সফল হয়েছে প্রজেক্ট",
            "একটা কোড লেখা যে রান করলে সফল হয়েছে লেখা আসবে",
            "python",
            [{
                "title": "প্রোগ্রাম চালান",
                "description": "রান করলে সফল হয়েছে লেখা আসবে; প্রয়োজন হলে কমান্ডও লিখুন",
            }],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)
        fake_code = 'print("সফল হয়েছে")\n'

        async def run():
            with patch.object(self.main, "ask_ai", new=AsyncMock(return_value=fake_code)) as ask_ai:
                result = await self.main.process_next_code_task(project)
                return result, ask_ai

        result, ask_ai = asyncio.run(run())
        self.assertIsNotNone(result)
        code = result.get("code") or ""
        self.assertNotIn("কমান্ডের তালিকা", code)
        self.assertNotIn("/help অথবা /menu", code)
        self.assertNotIn("আপনাকেও ধন্যবাদ", code)
        self.assertNotIn("আসসালামু আলাইকুম", code)
        self.assertFalse(str(result.get("source", "")).startswith("brain:pattern"))
        self.assertFalse(str(result.get("source", "")).startswith("brain:knowledge"))
        # Either real AI code, or a failed/no-api path — never a silent FAQ success.
        if result.get("status") == "done":
            self.assertIn("print", code)
            self.assertTrue(ask_ai.await_count >= 1 or str(result.get("source", "")).startswith("knowledge_base:"))

    def test_process_next_code_task_rejects_non_code_direct_payload(self):
        project_id = self.main.create_code_project(
            USER_ID,
            "Sanity net project",
            "write a runner",
            "python",
            [{"title": "Implement runner", "description": "print success when run"}],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)
        fake_code = "def run():\n    print('ok')\n"

        async def run():
            with patch.object(
                self.main,
                "decision_engine_service",
                **{
                    "execute_async": AsyncMock(
                        return_value={
                            "strategy": "direct",
                            "stage": "pattern",
                            "payload": {
                                "pattern": {
                                    "category": "coding",
                                    "description": "সব কমান্ডের তালিকা দেখতে /help অথবা /menu লিখুন।",
                                }
                            },
                        }
                    )
                },
            ), patch.object(self.main, "ask_ai", new=AsyncMock(return_value=fake_code)) as ask_ai:
                result = await self.main.process_next_code_task(project)
                return result, ask_ai

        result, ask_ai = asyncio.run(run())
        self.assertNotIn("কমান্ডের তালিকা", result.get("code") or "")
        self.assertEqual(result.get("source"), "ai")
        ask_ai.assert_awaited()

    # ------------------------------------------------------------------
    # 5. Code-sanity helper
    # ------------------------------------------------------------------
    def test_code_sanity_accepts_code_rejects_faq(self):
        looks = self.main._coding_result_looks_like_code
        self.assertFalse(looks("সব কমান্ডের তালিকা দেখতে /help অথবা /menu লিখুন — বাটন-ভিত্তিক মেনু চলে আসবে।", "python"))
        self.assertFalse(looks("আপনাকেও ধন্যবাদ! 🙏 আর কিছু লাগলে জানাবেন।", "python"))
        self.assertFalse(looks("Hello! How can I help you? Type your question or use /menu.", "javascript"))
        self.assertTrue(looks('print("সফল হয়েছে")\n', "python"))
        self.assertTrue(looks("def main():\n    return 1\n", "python"))
        self.assertTrue(looks("from flask import Flask\napp = Flask(__name__)\n", "python"))
        self.assertTrue(looks("__pycache__/\n*.pyc\n.env\nvenv/\n", "python"))


def _payload_cat(payload):
    try:
        if isinstance(payload, dict):
            if payload.get("category"):
                return str(payload["category"]).strip().lower()
            inner = payload.get("pattern")
            if inner is not None:
                return str(getattr(inner, "category", "") or (inner.get("category") if isinstance(inner, dict) else "") or "").strip().lower()
        return str(getattr(payload, "category", "") or "").strip().lower()
    except Exception:
        return ""


if __name__ == "__main__":
    unittest.main(verbosity=2)
