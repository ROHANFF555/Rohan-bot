"""/exportcode (assemble_project_code) de-dup ও prompt-context ফিক্সের regression tests।

বাগ: প্রতিটা /codenext ধাপ নিজস্ব `def main()` + `if __name__ == "__main__":` সহ
সম্পূর্ণ স্ক্রিপ্ট লিখত, আর assemble_project_code() সেগুলো raw concatenate করত —
ফলে /exportcode-এর ফাইল রান করলে একাধিক ভিন্ন ভিন্ন মেসেজ প্রিন্ট হতো।

ফিক্স: (১) process_next_code_task() এখন আগের ধাপগুলোর assemble করা কোড context
হিসেবে AI-কে পাঠায় আর "সম্পূর্ণ আপডেটেড ফাইল" চায়; (২) assemble_project_code()-এ
safety-net — একাধিক ধাপে entry-point ব্লক থাকলে শুধু সর্বশেষ (সর্বোচ্চ seq)
ভার্সনটাই চূড়ান্ত ফাইল; multi-file হলে ফাইল-গ্রুপ ধরে আলাদাভাবে একই লজিক।

main.py একক-file application হওয়ায় test-টি সেটাকে অস্থায়ী ডিরেক্টরিতে কপি করে
আলাদা module হিসেবে import করে। এতে repository-তে bot_data.db বা logs/ তৈরি হয় না।

চালানো যায়:
    python3 tests/test_exportcode_assembly.py
    python3 -m unittest tests/test_exportcode_assembly.py
"""

from __future__ import annotations

import asyncio
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, patch


USER_ID = 885522


class ExportcodeAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-exportcode-test-")
        shutil.copyfile(os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        module_name = "rohan_exportcode_test_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        cls.main.register_user(USER_ID)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_exportcode_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    # ---------------------------------------------------------------- helpers

    def _make_project(self, name: str, steps: int) -> int:
        return self.main.create_code_project(
            USER_ID,
            name,
            f"{name} description",
            "python",
            [{"title": f"step {i}", "description": f"description {i}"} for i in range(1, steps + 1)],
        )

    def _finish_tasks(self, project_id: int, codes, target_files=None):
        tasks = self.main.get_project_tasks(project_id)
        conn = self.main.get_conn()
        cur = conn.cursor()
        for i, (task, code) in enumerate(zip(tasks, codes)):
            tf = (target_files[i] if target_files else "")
            cur.execute(
                "UPDATE code_tasks SET code = ?, status = 'done', source = 'ai', target_files = ? WHERE id = ?",
                (code, tf, task["id"]),
            )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------ tests

    def test_single_file_project_keeps_only_latest_version(self):
        """"Success Printer" রিগ্রেশন: ৫ ধাপ, প্রত্যেকটা নিজস্ব entry-point-ওয়ালা
        সম্পূর্ণ স্ক্রিপ্ট — /exportcode-এ শুধু শেষ ভার্সনটাই থাকবে, আর রান করলে
        একটামাত্র মেসেজ প্রিন্ট হবে।"""
        pid = self._make_project("Success Printer", 5)
        codes = [
            'def main():\n    print("Success")\n\nif __name__ == "__main__":\n    main()',
            'def main():\n    print("Success")\n\nif __name__ == "__main__":\n    main()',
            'def main():\n    print("সফল হয়েছে")\n\nif __name__ == "__main__":\n    main()',
            'def main():\n    print("সফল হয়েছে")\n\nif __name__ == "__main__":\n    main()',
            'def main():\n    print("Success! The script ran correctly.")\n\nif __name__ == "__main__":\n    main()',
        ]
        self._finish_tasks(pid, codes)

        assembled = self.main.assemble_project_code(pid)
        self.assertEqual(assembled.count("if __name__"), 1, "entry-point ব্লক একটার বেশি থাকা যাবে না")
        self.assertEqual(assembled.count("def main("), 1, "main() একবারই define হবে")

        out_path = os.path.join(self.workdir, "success_printer_out.py")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(assembled)
        run = subprocess.run([sys.executable, out_path], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), "Success! The script ran correctly.")

    def test_fragment_steps_are_still_concatenated(self):
        """সত্যিকারের খণ্ড-খণ্ড helper ধাপ (entry-point নেই / একটাতেই আছে) হলে আগের
        মতোই ধাপে ধাপে জোড়া লাগবে — কিছু হারাবে না।"""
        pid = self._make_project("Helpers", 3)
        codes = [
            "def load_data():\n    return [1, 2, 3]",
            "def process(data):\n    return sum(data)",
            'if __name__ == "__main__":\n    print(process(load_data()))',
        ]
        self._finish_tasks(pid, codes)
        assembled = self.main.assemble_project_code(pid)
        self.assertIn("def load_data", assembled)
        self.assertIn("def process", assembled)
        self.assertIn("if __name__", assembled)
        self.assertEqual(assembled.count("ধাপ 1"), 1)

    def test_multi_file_project_groups_by_target_file(self):
        """Multi-file প্রজেক্টে দুইটা ভিন্ন ফাইলের কোড মিশে যাবে না — প্রতি ফাইল-গ্রুপে
        আলাদাভাবে de-dup হবে (guarded ফাইলে সর্বশেষ ভার্সন, বাকিগুলো concatenate)।"""
        pid = self._make_project("Flask App", 4)
        codes = [
            'from flask import Flask\napp = Flask(__name__)\n\nif __name__ == "__main__":\n    app.run()',
            'def home():\n    return "v1"',
            'from flask import Flask\nfrom routes import home\napp = Flask(__name__)\napp.add_url_rule("/", "home", home)\n\nif __name__ == "__main__":\n    app.run(debug=True)',
            'def home():\n    return "v2"',
        ]
        self._finish_tasks(pid, codes, target_files=["app.py", "routes.py", "app.py", "routes.py"])
        assembled = self.main.assemble_project_code(pid)
        # app.py গ্রুপে দুইটা guarded ভার্সন — শুধু শেষটা (debug=True) থাকবে।
        self.assertIn("debug=True", assembled)
        self.assertEqual(assembled.count("if __name__"), 1)
        # routes.py গ্রুপে guard নেই — দুই ধাপই থাকবে, app.py-এর সাথে মিশবে না।
        self.assertIn('return "v1"', assembled)
        self.assertIn('return "v2"', assembled)
        self.assertIn("app.py", assembled)
        self.assertIn("routes.py", assembled)

    def test_process_next_code_task_sends_existing_code_context(self):
        """দ্বিতীয় ধাপ প্রসেস করার সময় system prompt-এ আগের ধাপের কোড আর
        'সম্পূর্ণ আপডেটেড ফাইল' নির্দেশ দুটোই থাকতে হবে।"""
        pid = self._make_project("Ctx Project", 2)
        first_code = 'def main():\n    print("hello")\n\nif __name__ == "__main__":\n    main()'
        tasks = self.main.get_project_tasks(pid)
        self.main.save_task_result(tasks[0]["id"], first_code, source="ai")
        project = self.main.get_project(pid, owner_id=USER_ID)

        captured = {}

        async def fake_ask_ai(system_prompt, user_text, **kwargs):
            captured["system"] = system_prompt
            return 'def main():\n    print("hello v2")\n\nif __name__ == "__main__":\n    main()'

        async def run():
            with patch.object(self.main, "match_knowledge_base", return_value=None), patch.object(
                self.main,
                "decision_engine_service",
                **{"execute_async": AsyncMock(return_value={"strategy": "fallback", "stage": "ai"})},
            ), patch.object(self.main, "ask_ai", new=fake_ask_ai):
                return await self.main.process_next_code_task(project)

        result = asyncio.run(run())
        self.assertEqual(result["status"], "done")
        self.assertIn('print("hello")', captured["system"], "আগের ধাপের কোড prompt-এ যায়নি")
        self.assertIn("সম্পূর্ণ আপডেটেড ফাইল", captured["system"])

    def test_process_first_task_uses_new_file_instruction(self):
        """প্রথম ধাপে আগের কোনো কোড নেই — 'প্রথম কোড/নতুন ফাইল' নির্দেশ থাকবে।"""
        pid = self._make_project("Fresh Project", 1)
        project = self.main.get_project(pid, owner_id=USER_ID)

        captured = {}

        async def fake_ask_ai(system_prompt, user_text, **kwargs):
            captured["system"] = system_prompt
            return 'print("first")'

        async def run():
            with patch.object(self.main, "match_knowledge_base", return_value=None), patch.object(
                self.main,
                "decision_engine_service",
                **{"execute_async": AsyncMock(return_value={"strategy": "fallback", "stage": "ai"})},
            ), patch.object(self.main, "ask_ai", new=fake_ask_ai):
                return await self.main.process_next_code_task(project)

        result = asyncio.run(run())
        self.assertEqual(result["status"], "done")
        self.assertIn("প্রথম কোড", captured["system"])

    def test_assemble_falls_back_to_concatenate_on_error(self):
        """De-dup লজিকে এক্সসেপশন হলেও assemble ভাঙবে না — পুরনো concatenate ফলাফল আসবে।"""
        pid = self._make_project("Fallback Project", 2)
        codes = [
            'def main():\n    print("a")\n\nif __name__ == "__main__":\n    main()',
            'def main():\n    print("b")\n\nif __name__ == "__main__":\n    main()',
        ]
        self._finish_tasks(pid, codes)
        with patch.object(self.main, "_assemble_task_group", side_effect=RuntimeError("boom")):
            assembled = self.main.assemble_project_code(pid)
        self.assertIn('print("a")', assembled)
        self.assertIn('print("b")', assembled)
        self.assertIn("ধাপ 1", assembled)


if __name__ == "__main__":
    unittest.main()
