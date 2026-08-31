"""No API Mode-এ Coding Agent যেন কোনো AI provider-এ না যায়, তার regression tests।

main.py একক-file application হওয়ায় test-টি সেটাকে অস্থায়ী ডিরেক্টরিতে কপি করে
আলাদা module হিসেবে import করে। এতে test চালালে repository-তে bot_data.db বা logs/
তৈরি হয় না।

চালানো যায়:
    python3 tests/test_no_api_coding_guards.py
    python3 -m unittest tests/test_no_api_coding_guards.py
"""

from __future__ import annotations

import asyncio
import ast
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, patch


USER_ID = 774433


class NoApiCodingGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-no-api-test-")
        shutil.copyfile(os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        module_name = "rohan_no_api_guard_test_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        cls.main.register_user(USER_ID)
        cls.main.set_no_api_mode(USER_ID, True)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_no_api_guard_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def test_autonomous_plan_does_not_call_ai(self):
        async def run():
            with patch.object(self.main, "ask_ai", new=AsyncMock()) as ask_ai:
                plan = await self.main.autonomous_generate_plan(USER_ID, "একটি অচেনা inventory app বানাও")
                ask_ai.assert_not_awaited()
                return plan

        plan = asyncio.run(run())
        self.assertTrue(plan["no_api_blocked"])
        self.assertEqual(plan["tasks"][0]["title"], "No API Mode চালু আছে")

    def test_codeproject_plan_does_not_call_ai_in_no_api_mode(self):
        # /codeproject-এর প্ল্যানার (coding_analyze_and_plan) — /codeplan-এর মতোই
        # No API Mode-এ ask_ai কল করার আগেই deterministic/blocked ফলাফলে থামবে।
        async def run():
            with patch.object(self.main, "ask_ai", new=AsyncMock()) as ask_ai:
                plan = await self.main.coding_analyze_and_plan(
                    "একটি অচেনা inventory analytics app বানাও", USER_ID
                )
                ask_ai.assert_not_awaited()
                return plan

        plan = asyncio.run(run())
        self.assertTrue(plan["no_api_blocked"])
        self.assertEqual(plan["stack"], "unknown")
        self.assertEqual(len(plan["tasks"]), 1)
        self.assertEqual(plan["tasks"][0]["title"], "No API Mode চালু আছে")

    def test_codeproject_dynamic_print_resolves_without_ai(self):
        # এক্স্যাক্ট repro: "রান করলে ... লেখা আসবে" ধরনের এক-লাইনের রিকোয়েস্ট No API
        # Mode-এও /codeproject প্ল্যানার + process_next_code_task() দিয়ে AI ছাড়াই
        # একটাই সঠিক ধাপে resolve হবে — কোডে "সফল হয়েছে" প্রিন্ট থাকবে।
        raw_request = "একটি কোড লেখ যেটা রান করলে সফল হয়েছে লেখা আসবে"

        async def run():
            with patch.object(self.main, "ask_ai", new=AsyncMock()) as ask_ai:
                plan = await self.main.coding_analyze_and_plan(raw_request, USER_ID)
                ask_ai.assert_not_awaited()
                project_id = self.main.create_code_project(
                    USER_ID, plan["project_name"], raw_request, plan["stack"], plan["tasks"]
                )
                project = self.main.get_project(project_id, owner_id=USER_ID)
                result = await self.main.process_next_code_task(project)
                return plan, project_id, result, ask_ai

        plan, project_id, result, ask_ai = asyncio.run(run())
        self.assertFalse(plan.get("no_api_blocked"))
        self.assertTrue(plan.get("deterministic"))
        self.assertEqual(len(plan["tasks"]), 1)
        self.assertEqual(result["status"], "done")
        self.assertTrue(result["source"].startswith("knowledge_base:"))
        ask_ai.assert_not_awaited()
        # জেনারেট হওয়া কোডে বার্তাটা সত্যিই আছে
        self.assertIn("সফল হয়েছে", result["code"])
        # ডাটাবেসেও done হিসেবে সেভ হয়েছে
        saved = self.main.get_project_tasks(project_id)
        self.assertEqual(saved[0]["status"], "done")
        self.assertTrue(saved[0]["source"].startswith("knowledge_base:"))
        # ধরা পড়া ভাষার সিনট্যাক্সে কোডটা সত্যিই বার্তাটা প্রিন্ট করে
        lang = self.main._detect_dynamic_print_language(plan["stack"])
        self.assertTrue(lang)
        if lang == "python":
            ast.parse(result["code"])
            run_result = subprocess.run(
                [sys.executable, "-c", result["code"]], capture_output=True, text=True, timeout=30
            )
            self.assertEqual(run_result.returncode, 0, run_result.stderr[:300])
            self.assertIn("সফল হয়েছে", run_result.stdout)

    def test_legacy_task_fallback_does_not_call_ai(self):
        project_id = self.main.create_code_project(
            USER_ID,
            "Quux workspace",
            "একটি quux workflow তৈরি করো",
            "unknown",
            [{"title": "Quux workflow implementation", "description": "quux-এ custom workflow"}],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)

        async def run():
            # Decision Engine miss-এর পরেও ask_ai-তে যাওয়া যাবে না।
            with patch.object(
                self.main,
                "decision_engine_service",
                **{"execute_async": AsyncMock(return_value={"strategy": "fallback", "stage": "ai"})},
            ), patch.object(self.main, "ask_ai", new=AsyncMock()) as ask_ai:
                result = await self.main.process_next_code_task(project)
                ask_ai.assert_not_awaited()
                return result

        result = asyncio.run(run())
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["no_api_blocked"])
        self.assertEqual(result["source"], "no_api_blocked")

    def test_autonomous_implementation_path_is_also_blocked(self):
        project_id = self.main.create_code_project(
            USER_ID,
            "Autonomous quux workspace",
            "একটি quux autonomous workflow তৈরি করো",
            "unknown",
            [{"title": "Autonomous quux implementation", "description": "quux implementation"}],
        )
        project = self.main.get_project(project_id, owner_id=USER_ID)
        task = self.main.get_next_pending_task(project_id)

        async def run():
            with patch.object(self.main, "ask_ai", new=AsyncMock()) as ask_ai:
                result = await self.main.autonomous_implement_task(project, task)
                ask_ai.assert_not_awaited()
                return result

        result = asyncio.run(run())
        self.assertTrue(result["no_api_blocked"])
        self.assertEqual(result["status"], "failed")


if __name__ == "__main__":
    unittest.main()
