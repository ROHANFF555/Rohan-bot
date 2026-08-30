"""`dynamic_print_task` ডাইনামিক KB এন্ট্রি + নতুন ফিক্সড অ্যালগরিদম টেমপ্লেটের টেস্ট।

যা যাচাই করা হয়:
  1. extract_dynamic_print_message() — কোটেশন → বাংলা "করলে ... লেখা আসবে" →
     ইংরেজি "prints ... when run" অগ্রাধিকার; কিছু না মিললে None (AI ফলব্যাক),
     আর প্রিন্ট-প্রসঙ্গহীন কোটেশন/কোড-শনাক্তকারক/ফাইলনাম ভুলে ধরা পড়ে না।
  2. project['stack'] দেখে Python/Node/Java/C/C++/PHP/Bash/Go/C#/Ruby/Kotlin ভাষার
     সঠিক সিনট্যাক্সে সম্পূর্ণ চালানোর-যোগ্য কোড জেনারেট হয় (Python/Bash/JS/CC-
     টুল চেইন থাকলে সত্যিই রান করে আউটপুট মিলিয়ে দেখা হয়)। অচেনা ভাষা → None।
  3. process_next_code_task() — dynamic ম্যাচ fixed KB-র পরে, is_no_api_mode()-এর
     আগে চলে: No API Mode চালু থাকলেও টাস্ক source='knowledge_base:dynamic_print'
     হিসেবে AI/Decision Engine ছাড়াই সমাধান হয়; না-মিললে আগের আচরণই থাকে।
  4. CODE_KNOWLEDGE_BASE-এ যোগ হওয়া FizzBuzz/prime/factorial/fibonacci/
     string-reverse টেমপ্লেটগুলো সঠিক label-এ ম্যাচ করে ও আসলেই চলে।

চালানো যায়:
    python3 tests/test_dynamic_print_kb.py
    python3 -m unittest tests.test_dynamic_print_kb -v
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

USER_ID = 900101
USER_ID_NOAPI = 900102


class DynamicPrintKbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-dynprint-")
        shutil.copyfile(os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        logging.disable(logging.CRITICAL)

        module_name = "rohan_dynprint_test_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        cls.main.seed_brain_os_defaults()
        cls.main.register_user(USER_ID)
        cls.main.register_user(USER_ID_NOAPI)
        cls.main.set_no_api_mode(USER_ID_NOAPI, True)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_dynprint_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    # ------------------------------------------------------------------
    # 1. বার্তা বের করার regex ফাংশন
    # ------------------------------------------------------------------
    def test_bengali_patterns_extract_message(self):
        extract = self.main.extract_dynamic_print_message
        # কোটেশন (straight + curly), বাংলা প্রসঙ্গে
        self.assertEqual(
            extract("গ্রিটিং", "প্রোগ্রামটা রান করলে 'স্বাগতম!' লেখা আসবে"), "স্বাগতম!"
        )
        self.assertEqual(
            extract("greet", 'রান করলে "নমস্কার দুনিয়া" লেখা দেখাবে'), "নমস্কার দুনিয়া"
        )
        # কোটেশন নেই → করলে ... লেখা আসবে প্যাটার্নের মাঝের অংশ
        self.assertEqual(
            extract("হ্যালো", "স্ক্রিপ্টটা চালালে সফলভাবে সম্পন্ন লেখা আসবে"), "সফলভাবে সম্পন্ন"
        )
        # প্রিন্ট হবে-ভ্যারিয়েন্ট
        self.assertEqual(
            extract("টাস্ক", "রান করলে ডেটাবেকআপ সম্পন্ন প্রিন্ট হবে"), "ডেটাবেকআপ সম্পন্ন"
        )

    def test_english_patterns_extract_message(self):
        extract = self.main.extract_dynamic_print_message
        self.assertEqual(
            extract("greeting", 'The script prints "Hello, World!" when run'), "Hello, World!"
        )
        # কোটেশনবিহীন মাঝের অংশ
        self.assertEqual(
            extract("hello", "Write a program that prints welcome aboard if run"), "welcome aboard"
        )
        self.assertEqual(
            extract("hello", "a cli that shows done when executed"), "done"
        )

    def test_no_match_returns_none_for_fallback(self):
        extract = self.main.extract_dynamic_print_message
        # সম্পূর্ণ সাধারণ কোডিং টাস্ক — কিছুই মিলবে না, AI ফ্লো চলবে
        self.assertIsNone(extract("auth", "লগইন সিস্টেম আর সেশন ম্যানেজমেন্ট বানাও"))
        self.assertIsNone(extract("api", "Build a REST API with JWT auth and rate limiting"))
        # কোটেশন আছে কিন্তু প্রিন্ট/রান-প্রসঙ্গ নেই → কোটেশন-শাখা নিষ্ক্রিয়
        self.assertIsNone(extract("ui", "ডিজাইনে 'login' পেজ আর হেডার ব্যবহার করো"))
        # কোড-স্নিপেটের ভেতরের কোট — print("hi")-কে বার্তা ধরে নেওয়া যাবে না
        self.assertIsNone(extract("refactor", "replace every print(\"hi\") call with logging when run"))
        # snake_case শনাক্তকারক / ফাইলনাম বার্তা নয়
        self.assertIsNone(extract("log", "রান করলে user_id লেখা আসবে"))
        self.assertIsNone(extract("files", 'রান করলে "main.py" তৈরি হবে'))
        # খালি ইনপুট
        self.assertIsNone(extract("", ""))
        self.assertIsNone(extract(None, None))  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # 2. স্ট্যাক দেখে ভাষা-নির্বাচন ও সঠিক সিনট্যাক্সে সম্পূর্ণ কোড
    # ------------------------------------------------------------------
    LANG_CASES = (
        ("Python 3.11", 'print("hi")'),
        ("Node.js", 'console.log("hi");'),
        ("JavaScript (browser)", 'console.log("hi");'),
        ("TypeScript + React", 'console.log("hi");'),
        ("Java 17", "System.out.println(\"hi\")"),
        ("C", 'printf("%s\\n", "hi")'),
        ("C++", "std::cout << \"hi\""),
        ("PHP 8", "<?php"),
        ("Bash", "printf '%s\\n'"),
        ("Go", "fmt.Println(\"hi\")"),
        ("C# (.NET)", "Console.WriteLine(\"hi\")"),
        ("Ruby", "puts 'hi'"),
        ("Kotlin", "fun main()"),
    )

    def test_generates_runnable_code_per_language(self):
        for stack, expected in self.LANG_CASES:
            with self.subTest(stack=stack):
                res = self.main.match_dynamic_print_task("hello", 'print "hi" when run', stack)
                self.assertIsNotNone(res, f"no code for stack={stack}")
                label, code = res
                self.assertEqual(label, self.main.DYNAMIC_PRINT_KB_LABEL)
                self.assertIn(expected, code)
                self.assertIn("hi", code)

    def test_generated_code_actually_runs(self):
        """Python/Bash — এবং টুল চেইন থাকলে Node/C — জেনারেট হওয়া কোড সত্যিই চালিয়ে
        দেখা হয় যে ঠিক বার্তাটাই প্রিন্ট হয়।"""
        message = "সফল হয়েছে"  # Bengali text with unicode
        runs = [
            ("python", "dyn_run.py", lambda f, d: [sys.executable, f]),
            ("bash", "dyn_run.sh", lambda f, d: ["bash", f]),
        ]
        if shutil.which("node"):
            runs.append(("javascript", "dyn_run.js", lambda f, d: ["node", f]))
        if shutil.which("gcc"):
            runs.append(("c", "dyn_run.c", None))  # নিচে বিশেষ কেইস

        for stack, fname, argv_fn in runs:
            with self.subTest(stack=stack):
                res = self.main.match_dynamic_print_task("t", f'প্রিন্ট করলে "{message}" লেখা আসবে', stack)
                self.assertIsNotNone(res, f"no code for {stack}")
                fpath = os.path.join(self.workdir, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(res[1])
                if stack == "c":
                    exe = os.path.join(self.workdir, "dyn_run.out")
                    c = subprocess.run(["gcc", fpath, "-o", exe], capture_output=True, text=True)
                    self.assertEqual(c.returncode, 0, c.stderr[:400])
                    r = subprocess.run([exe], capture_output=True, text=True, timeout=30)
                else:
                    r = subprocess.run(argv_fn(fpath, self.workdir), capture_output=True, text=True, timeout=60)
                self.assertEqual(r.returncode, 0, r.stderr[:400])
                self.assertIn(message, r.stdout)

    def test_generated_python_snippets_parse(self):
        res = self.main.match_dynamic_print_task("t", 'print "5 + 3 = 8" when run', "python")
        self.assertIsNotNone(res)
        ast.parse(res[1])
        res = self.main.match_dynamic_print_task("t", 'প্রিন্ট করলে "টাকা: ৳৫০" লেখা আসবে', "python")
        self.assertIsNotNone(res)
        ast.parse(res[1])
        self.assertIn("টাকা: ৳৫০", res[1])

    def test_special_characters_are_escaped_not_broken(self):
        # কোট/ব্যাকস্ল্যাশ/ডলার — লিটারেল ভেঙে কোড ভেঙে যাবে না
        msg = 'He said "hi" \\ $HOME {x}'
        code = self.main._build_dynamic_print_code("python", msg)
        ast.parse(code)
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), msg)
        # PHP/Ruby সিঙ্গেল-কোট — ' ভেতরে থাকলেও পালাতে হবে
        php = self.main._build_dynamic_print_code("php", "it's done")
        self.assertIn("\\'", php)
        bash = self.main._build_dynamic_print_code("bash", "it's done")
        self.assertIn("'\\''", bash)
        # Kotlin — $ টেমপ্লেট মার্কার এস্কেপ হয়
        kt = self.main._build_dynamic_print_code("kotlin", "cost $5")
        self.assertIn("\\$", kt)

    def test_unknown_stack_or_message_falls_back_with_none(self):
        # বার্তা মিলল কিন্তু ভাষা চেনা নয় → None (AI হ্যান্ডেল করবে)
        self.assertIsNone(self.main.match_dynamic_print_task("t", 'print "hi" when run', "Rust (wasm)"))
        self.assertIsNone(self.main.match_dynamic_print_task("t", 'print "hi" when run', ""))
        self.assertIsNone(self.main.match_dynamic_print_task("t", 'print "hi" when run', "অজানা"))
        # ভাষা চেনা কিন্তু বার্তা নেই → None
        self.assertIsNone(self.main.match_dynamic_print_task("t", "custom payment module", "python"))

    def test_overlong_message_rejected(self):
        long_msg = "ক " * (self.main.DYNAMIC_PRINT_MSG_MAX_CHARS)  # ~2x max chars
        self.assertIsNone(self.main.extract_dynamic_print_message("t", f'প্রিন্ট করলে "{long_msg}" লেখা আসবে'))

    # ------------------------------------------------------------------
    # 3. process_next_code_task ইন্টিগ্রেশন
    # ------------------------------------------------------------------
    def _run_task(self, user_id: int, stack: str, title: str, description: str):
        project_id = self.main.create_code_project(
            user_id, "ডায়নামিক টাস্ক প্রজেক্ট", "টেস্ট প্রজেক্ট", stack,
            [{"title": title, "description": description}],
        )
        project = self.main.get_project(project_id, owner_id=user_id)

        async def run():
            # Decision Engine-ই ডাকা হলে ধরা পড়বে (dynamic check fixed-KB-র ঠিক
            # পরে, Decision Engine-ও is_no_api_mode()-এর আগে চলার কথা)।
            fake_engine = MagicMock()
            fake_engine.execute_async = AsyncMock(return_value={"strategy": "ai", "stage": "ai"})
            with patch.object(self.main, "ask_ai", new=AsyncMock(return_value="# ai fallback\n")) as ask_ai, \
                 patch.object(self.main, "decision_engine_service", fake_engine):
                result = await self.main.process_next_code_task(project)
            return result, ask_ai, fake_engine

        result, ask_ai, engine = asyncio.run(run())
        return result, ask_ai, engine, project_id

    def test_dynamic_print_resolves_task_without_ai(self):
        result, ask_ai, engine, project_id = self._run_task(
            USER_ID, "python", "হ্যালো প্রিন্ট", "রান করলে 'হ্যালো ওয়ার্ল্ড' লেখা আসবে")
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["source"], "knowledge_base:dynamic_print")
        self.assertIn('print("হ্যালো ওয়ার্ল্ড")', result["code"])
        ask_ai.assert_not_awaited()
        engine.execute_async.assert_not_awaited()  # fixed KB-র পরেই short-circuit
        # ডাটাবেসেও সেই রকমই সেভ হয়েছে
        saved = self.main.get_project_tasks(project_id)
        self.assertEqual(saved[0]["status"], "done")
        self.assertEqual(saved[0]["source"], "knowledge_base:dynamic_print")

    def test_dynamic_print_bypasses_no_api_mode(self):
        # No API Mode চালু থাকা ইউজারের জন্যও deterministic print টাস্ক সমাধান হয়
        result, ask_ai, engine, _pid = self._run_task(
            USER_ID_NOAPI, "Node.js", "hello", 'The script prints "bye" when run')
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["source"], "knowledge_base:dynamic_print")
        self.assertIn('console.log("bye")', result["code"])
        self.assertNotIn("no_api_blocked", str(result.get("source")))
        ask_ai.assert_not_awaited()
        engine.execute_async.assert_not_awaited()

    def test_no_api_mode_still_blocks_nondeterministic_tasks(self):
        # রিগ্রেশন গার্ড: যা dynamic KB-তে মিলবে না, সেটা আগের মতোই no-api-তে আটকাবে
        result, ask_ai, _engine, _pid = self._run_task(
            USER_ID_NOAPI, "python", "Payment module", "stripe webhook সহ ইনভয়েস সিস্টেম")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["source"], "no_api_blocked")
        ask_ai.assert_not_awaited()

    # ------------------------------------------------------------------
    # 4. ফিক্সড অ্যালগরিদম টেমপ্লেট (CODE_KNOWLEDGE_BASE-এ নতুন এন্ট্রি)
    # ------------------------------------------------------------------
    def test_fixed_algorithm_entries_match_and_run(self):
        cases = (
            ("fizzbuzz ২০ পর্যন্ত লেখো", "fizzbuzz", ["FizzBuzz", "Buzz"]),
            ("Write a prime number check function", "prime_check", ["2, 3, 5, 7"]),
            ("factorial বের করার ফাংশন দাও", "factorial", ["120"]),
            ("fibonacci sequence চাই", "fibonacci", ["0, 1, 1, 2, 3, 5, 8, 13, 21, 34"]),
            ("একটা string reverse টুল বানাও", "string_reverse", []),
        )
        for query, label, expect_out in cases:
            with self.subTest(query=query):
                res = self.main.match_knowledge_base(query, query, "প্রজেক্ট", "বিবরণ")
                self.assertIsNotNone(res, f"no KB match for {query!r}")
                self.assertEqual(res[0], label)
                ast.parse(res[1])  # টেমপ্লেট থেকে বসা কোড বৈধ Python হতে হবে
                if expect_out is not None:
                    script = os.path.join(self.workdir, f"algo_{label}.py")
                    with open(script, "w", encoding="utf-8") as f:
                        f.write(res[1])
                    r = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=30)
                    self.assertEqual(r.returncode, 0, r.stderr[:300])
                    for chunk in expect_out:
                        self.assertIn(chunk, r.stdout)

    def test_bengali_algorithm_keywords(self):
        for query, label in (
            ("ফিজবাজ প্রোগ্রাম", "fizzbuzz"),
            ("প্রাইম সংখ্যা চেক", "prime_check"),
            ("ফ্যাক্টোরিয়াল বের করার ফাংশন", "factorial"),
            ("ফিবোনাচি সিরিজ", "fibonacci"),
            ("স্ট্রিং উল্টো করে দাও", "string_reverse"),
        ):
            with self.subTest(query=query):
                res = self.main.match_knowledge_base(query, query, "p", "d")
                self.assertIsNotNone(res)
                self.assertEqual(res[0], label)

    def test_kb_entries_shape_and_unique_labels(self):
        labels = []
        for entry in self.main.CODE_KNOWLEDGE_BASE:
            keywords, label, template = entry
            self.assertTrue(keywords and all(k.strip() for k in keywords), label)
            self.assertTrue(template.strip(), label)
            labels.append(label)
        self.assertEqual(len(labels), len(set(labels)), "KB label ডুপ্লিকেট হয়েছে")
        for expected in ("fizzbuzz", "prime_check", "factorial", "fibonacci", "string_reverse"):
            self.assertIn(expected, labels)

    def test_unrelated_task_hits_no_algorithm_template(self):
        res = self.main.match_knowledge_base(
            "ড্যাশবোর্ড", "রিয়েলটাইম চার্ট ও অ্যালার্ট সিস্টেম বানাও", "p", "d")
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main(verbosity=2)
