"""bangla_rule_engine — নিয়ম-ভিত্তিক বাংলা→কোড deterministic ইঞ্জিনের টেস্ট।

যা যাচাই করা হয়:

  1. **translate_bangla_rules() ইউনিট** — স্পেসিফিকেশনের লগইন-উদাহরণ ("ডাটাবেজে ইউজার
     আইডি এবং পাসওয়ার্ড থাকবে ... ইনপুট দেই ... চাইবে ... মিললে সাকসেস দেখাবে")
     থেকে সম্পূর্ণ চালানোর-যোগ্য লগইন-সিস্টেম কোড জেনারেট হয়: ডাটাবেজ dict +
     input() লাইন (রিকোয়েস্টের ক্রমে) + == তুলনা + সাকসেস/ব্যর্থ প্রিন্ট। জেনারেট
     হওয়া কোড সত্যিই রান করে দুই শাখাই (মিললে → সাকসেস, না মিললে → ব্যর্থতা)
     মিলিয়ে দেখা হয়। এছাড়া ছোট কেস: শুধু if (literal শর্ত), শুধু print (কনসোল-
     প্রসঙ্গ), negation সহ কেস ("... দেখাবে না" → ওই অংশ জেনারেট হয় না), "X এবং Y
     মিললে" পরস্পর-তুলনা, "না মিললে" else-বার্তা।

  2. **গার্ড (false-positive প্রতিরোধ)** — মুক্ত বাংলা, ইংরেজি, UI/ফিচার-বর্ণনা,
     কোটেশন-যুক্ত, dynamic-print-আকৃতি ("রান করলে ... লেখা আসবে"), অন্য ভাষার নাম
     (জাভা/জাভাস্ক্রিপ্ট...), খালি/অতিদীর্ঘ টেক্সটে ইঞ্জিন ফায়ার করে না (None) —
     AI ফলব্যাক অক্ষত থাকে।

  3. **ইন্টিগ্রেশন (main.py)** — matcher চেইনে ইঞ্জিন fixed-KB-র পরে, dynamic_print-এর
     আগে বসে; No API Mode চালু থাকলেও /codeproject-প্ল্যান → /codenext-টাস্ক stuck
     মেসেজ ছাড়াই আসল কোড ফেরায় (ask_ai/Decision Engine কোনোভাবেই ডাকা হয় না)।
     ক্লাসিক dynamic-print রিকোয়েস্ট আগের মতোই knowledge_base:dynamic_print থেকেই
     আসে (নতুন ইঞ্জিন পুরনো print-matcher ভাঙে না), আর নন-ডিটারমিনিস্টিক রিকোয়েস্ট
     আগের মতোই no-api-ব্লকড থাকে।

চালানো যায়:
    python3 tests/test_bangla_rule_engine.py
    python3 -m unittest tests.test_bangla_rule_engine -v
    python3 -m pytest tests/test_bangla_rule_engine.py -q
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import types
from unittest.mock import AsyncMock, MagicMock, patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import bangla_rule_engine as bre  # noqa: E402  (REPO_ROOT প্রথমে sys.path-এ ঢুকিয়ে নিয়েছি)

# স্পেসিফিকেশনের acceptance ইনপুট — হুবহু উদ্ধৃত
LOGIN_REQUEST = (
    "তোমাকে এখন একটি সিস্টেম বানাতে হবে ওই সিস্টেমে একটি ডাটাবেজ থাকবে "
    "ওই ডাটাবেজে ইউজার আইডি এবং পাসওয়ার্ড থাকবে আমি যদি পাসওয়ার্ড ইনপুট দেই "
    "তাহলে সে ইউজার নেম চাইবে এবং দুইটি মিললে সাকসেস দেখাবে"
)

USER_ID = 900201
USER_ID_NOAPI = 900202


def run_python_code(code: str, stdin_text: str, workdir: str, tag: str):
    """জেনারেট হওয়া কোড একটা টেম্প ফাইলে লিখে সত্যিই চালিয়ে stdout ফেরায়।"""
    script = os.path.join(workdir, f"bre_run_{tag}.py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(code)
    return subprocess.run(
        [sys.executable, script], input=stdin_text, capture_output=True,
        text=True, timeout=30, cwd=workdir,
    )


# ---------------------------------------------------------------------------
# ১. ইঞ্জিন-ইউনিট টেস্ট (main.py ছাড়াই, সরাসরি bangla_rule_engine মডিউলে)
# ---------------------------------------------------------------------------
class BanglaRuleEngineUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="rohan-bre-unit-")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def _translate(self, text):
        result = bre.translate_bangla_rules(text)
        self.assertIsNotNone(result, f"ইঞ্জিন ম্যাচ করেনি: {text!r}")
        label, code = result
        self.assertEqual(label, bre.ENGINE_LABEL)
        self.assertEqual(label, "bangla_rule_engine")
        import ast
        ast.parse(code)  # জেনারেট হওয়া কোড সবসময় বৈধ Python হতে হবে
        return code

    # -- acceptance: লগইন-সিস্টেম --------------------------------------------
    def test_login_system_acceptance_case(self):
        code = self._translate(LOGIN_REQUEST)
        # ডাটাবেজ dict (ইউজার আইডি + পাসওয়ার্ড ফিল্ড, ডিফল্ট মানসহ)
        self.assertIn("database = {", code)
        self.assertIn('"user_id": "admin"', code)
        self.assertIn('"password": "admin123"', code)
        # দুইটি ইনপুট — রিকোয়েস্টের ক্রমে: আগে পাসওয়ার্ড, পরে ইউজার নেম
        self.assertEqual(code.count("input("), 2)
        self.assertLess(code.index('input("পাসওয়ার্ড লিখুন: ")'),
                        code.index('input("ইউজার নেম লিখুন: ")'))
        # == তুলনা (ডাটাবেজের সাথে) + সাকসেস প্রিন্ট + else-ব্যর্থতা
        self.assertIn('password == database["password"]', code)
        self.assertIn('username == database["user_id"]', code)
        self.assertIn('print("সাকসেস")', code)
        self.assertIn("else:", code)
        # আসলেই চালিয়ে দেখা: মিললে সাকসেস
        r_ok = run_python_code(code, "admin123\nadmin\n", self.workdir, "login_ok")
        self.assertEqual(r_ok.returncode, 0, r_ok.stderr[:300])
        self.assertIn("সাকসেস", r_ok.stdout)
        self.assertNotIn("ব্যর্থ", r_ok.stdout)
        # না মিললে ব্যর্থতার মেসেজ
        r_bad = run_python_code(code, "admin123\nwrong\n", self.workdir, "login_bad")
        self.assertEqual(r_bad.returncode, 0, r_bad.stderr[:300])
        self.assertIn("ব্যর্থ", r_bad.stdout)
        self.assertNotIn("সাকসেস", r_bad.stdout)

    # -- ছোট কেস: শুধু if -----------------------------------------------------
    def test_if_only_case(self):
        code = self._translate("যদি নাম রহিম হলে তাহলে স্বাগতম দেখাবে")
        self.assertIn('if name == "রহিম":', code)
        self.assertIn('print("স্বাগতম")', code)
        r_hit = run_python_code(code, "রহিম\n", self.workdir, "if_hit")
        self.assertEqual(r_hit.returncode, 0)
        self.assertIn("স্বাগতম", r_hit.stdout)
        r_miss = run_python_code(code, "করিম\n", self.workdir, "if_miss")
        self.assertEqual(r_miss.returncode, 0)
        self.assertNotIn("স্বাগতম", r_miss.stdout)

    # -- ছোট কেস: শুধু print --------------------------------------------------
    def test_print_only_case(self):
        code = self._translate("প্রোগ্রামটা কনসোলে হ্যালো ওয়ার্ল্ড লিখবে")
        self.assertIn('print("হ্যালো ওয়ার্ল্ড")', code)
        self.assertNotIn("input(", code)
        r = run_python_code(code, "", self.workdir, "print_only")
        self.assertEqual(r.returncode, 0)
        self.assertIn("হ্যালো ওয়ার্ল্ড", r.stdout)

    # -- ছোট কেস: negation ----------------------------------------------------
    def test_negation_drops_negated_output(self):
        # ক্রিয়ার পরে "না" → ওই অংশের কোড জেনারেট হয় না
        code = self._translate("যদি নাম রহিম হলে তাহলে স্বাগতম দেখাবে আর বিদায় দেখাবে না")
        self.assertIn('print("স্বাগতম")', code)
        self.assertNotIn("বিদায়", code)
        r = run_python_code(code, "রহিম\n", self.workdir, "neg_if")
        self.assertEqual(r.returncode, 0)
        self.assertIn("স্বাগতম", r.stdout)
        self.assertNotIn("বিদায়", r.stdout)

    def test_negation_in_login_family_suppresses_default_else(self):
        # লগইন-গোষ্ঠীতে নিষেধ থাকলে ডিফল্ট else-বার্তাও জোর করে বসে না
        code = self._translate(
            "নাম এবং পাসওয়ার্ড থাকবে আমি নাম ইনপুট দিলে সে পাসওয়ার্ড চাইবে "
            "দুইটি মিললে সাকসেস দেখাবে আর বিদায় দেখাবে না"
        )
        self.assertIn('print("সাকসেস")', code)
        self.assertNotIn("বিদায়", code)
        self.assertNotIn("else:", code)

    # -- ছোট কেস: "X এবং Y মিললে" পরস্পর-তুলনা --------------------------------
    def test_two_field_match_comparison(self):
        code = self._translate("নাম এবং পাসওয়ার্ড মিললে সাকসেস দেখাবে")
        self.assertEqual(code.count("input("), 2)
        self.assertIn("if name == password:", code)
        r_ok = run_python_code(code, "abc\nabc\n", self.workdir, "pair_ok")
        self.assertEqual(r_ok.returncode, 0)
        self.assertIn("সাকসেস", r_ok.stdout)
        r_bad = run_python_code(code, "abc\nxyz\n", self.workdir, "pair_bad")
        self.assertEqual(r_bad.returncode, 0)
        self.assertNotIn("সাকসেস", r_bad.stdout)

    # -- "না মিললে" = else-শাখার স্পষ্ট নির্দেশ --------------------------------
    def test_else_marker_sets_explicit_failure_message(self):
        code = self._translate(
            "নাম এবং পাসওয়ার্ড মিললে সাকসেস দেখাবে না মিললে ফেইল দেখাবে"
        )
        self.assertIn('print("সাকসেস")', code)
        self.assertIn('print("ফেইল")', code)
        # if-শাখায় সাকসেস, else-শাখায় ফেইল
        self.assertLess(code.index('print("সাকসেস")'), code.index("else:"))
        self.assertGreater(code.index('print("ফেইল")'), code.index("else:"))
        r_bad = run_python_code(code, "abc\nxyz\n", self.workdir, "else_bad")
        self.assertEqual(r_bad.returncode, 0)
        self.assertIn("ফেইল", r_bad.stdout)

    # -- বাংলা সংখ্যা → ASCII লিটারেল -----------------------------------------
    def test_bengali_digits_become_ascii_literals(self):
        code = self._translate("যদি নাম্বার ১০ হলে তাহলে সঠিক দেখাবে")
        self.assertIn('if number == "10":', code)
        r = run_python_code(code, "10\n", self.workdir, "digits")
        self.assertEqual(r.returncode, 0)
        self.assertIn("সঠিক", r.stdout)

    # -- গার্ড: এই ইঞ্জিনের নয় এমন ইনপুট → None (AI ফলব্যাক) -------------------
    def test_non_strict_inputs_return_none(self):
        must_none = (
            # মুক্ত বাংলা
            "লগইন সিস্টেম আর সেশন ম্যানেজমেন্ট বানাও",
            "stripe webhook সহ ইনভয়েস সিস্টেম বানাও",
            "রেস্টুরেন্ট ম্যানেজমেন্ট সফটওয়্যার বানাতে হবে",
            "ফিজবাজ প্রোগ্রাম লিখে দাও",
            # ইংরেজি
            "Build a REST API with JWT auth and rate limiting",
            "build a login system with a database, take username input and show success",
            # dynamic-print-আকৃতি (পুরনো ম্যাচারের ডোমেইন)
            "রান করলে সফলভাবে সম্পূর্ণ লেখা আসবে",
            "রান করলে ডেটাবেকআপ সম্পূর্ন প্রিন্ট হবে",
            # কোটেশন — dynamic-print-এর quoted-শাখা
            "লগইন পেজে \"ব্যবহারকারী নেই\" message দেখাবে",
            # UI/ফিচার-বর্ণনা
            "ড্যাশবোর্ডে ইউজার প্রোফাইল দেখাবে এমন সিস্টেম বানাও",
            "সাবমিট করলে ফর্মে ধন্যবাদ স্ক্রিন দেখাবে",
            # ফাইল-লেখার মতো ফিচার
            "প্রোগ্রাম ইনভয়েস PDF লিখবে",
            # অন্য ভাষা (ল্যাটিন + বাংলা বানানে)
            "জাভাস্ক্রিপ্টে নাম এবং পাসওয়ার্ড মিললে সাকসেস দেখাবে",
            "জাভাতে একটা সিস্টেম বানাও যেখানে নাম এবং পাসওয়ার্ড মিললে সাকসেস দেখাবে",
            "php তে নাম মিললে সাকসেস দেখাবে",
            # খালি/অতিদীর্ঘ
            "",
            "   ",
            "নাম থাকবে " + "খুব দীর্ঘ বাক্য " * 120,
            None,
        )
        for text in must_none:
            with self.subTest(text=(text or "")[:40]):
                self.assertIsNone(bre.translate_bangla_rules(text))

    def test_python_language_mention_still_matches(self):
        # "পাইথনে ..." — ভাষার নাম ইঞ্জিনকে আটকায় না, ফিল্ড-নামেও ঢুকে যায় না
        code = self._translate("পাইথনে নাম এবং পাসওয়ার্ড মিললে সাকসেস দেখাবে")
        self.assertIn("name = input(", code)
        self.assertIn("password = input(", code)
        self.assertIn("if name == password:", code)

    def test_engine_never_raises_on_garbage(self):
        for text in ("()", "{}", "নানান\n\n\n", "!!!", "যদি", "মিললে", "থাকবে"):
            self.assertIsNone(bre.translate_bangla_rules(text))


# ---------------------------------------------------------------------------
# ২. ইন্টিগ্রেশন টেস্ট — main.py-এর matcher চেইন (ইঞ্জিন সক্রিয় রেখে)
# ---------------------------------------------------------------------------
class _FakeReply:
    def __init__(self, sink: list):
        self._sink = sink

    async def delete(self):
        self._sink.append("<thinking deleted>")


class _FakeMessage:
    def __init__(self, user_id: int, text: str = ""):
        self.from_user = types.SimpleNamespace(id=user_id, first_name="Test", username="t")
        self.text = text
        self.sent: list = []

    async def reply_text(self, text_msg, **_kw):
        self.sent.append(text_msg)
        return _FakeReply(self.sent)


class _FakeUpdate:
    def __init__(self, user_id: int, text: str = ""):
        self.effective_user = types.SimpleNamespace(id=user_id)
        self.message = _FakeMessage(user_id, text)

    @property
    def sent_texts(self):
        return self.message.sent


class _FakeContext:
    def __init__(self, args):
        self.args = args


class BanglaRuleEngineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="rohan-bre-int-")
        shutil.copyfile(os.path.join(REPO_ROOT, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        logging.disable(logging.CRITICAL)

        # REPO_ROOT ইতিমধ্যে sys.path-এ (মডিউল লোডের সময়ই) — তাই কপি করা main.py-ও
        # bangla_rule_engine ইমপোর্ট করতে পারে এবং চেইনে ইঞ্জিন সক্রিয় থাকে।
        module_name = "rohan_bre_test_main"
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
        sys.modules.pop("rohan_bre_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def setUp(self):
        # কমান্ড-লেভেল টেস্টে flood/quota-স্টেট পরিষ্কার রাখা
        self.main._last_message_time.clear()
        self.main._flood_strikes.clear()

    # -- হেল্পার --------------------------------------------------------------
    def _patch_ai(self):
        fake_engine = MagicMock()
        fake_engine.execute_async = AsyncMock(return_value={"strategy": "ai", "stage": "ai"})
        return patch.object(self.main, "ask_ai", new=AsyncMock(return_value="# ai fallback\n")), \
            patch.object(self.main, "decision_engine_service", fake_engine), fake_engine

    # -- acceptance: No API Mode-এ /codeproject → /codenext --------------------
    def test_no_api_codeproject_codenext_returns_real_code(self):
        """No API Mode চালু ইউজারের লগইন-রিকোয়েস্ট: প্ল্যান blocked নয়, ধাপটা
        stuck মেসেজ নয় — আসল কাজ-করা কোড ফেরে, কোনো AI/Decision কল ছাড়াই।"""
        with patch.object(self.main, "ask_ai", new=AsyncMock(return_value="# ai\n")) as ask_ai:
            plan = asyncio.run(self.main.coding_analyze_and_plan(LOGIN_REQUEST, USER_ID_NOAPI))
        # প্ল্যান deterministic, blocked-নয়
        self.assertTrue(plan.get("deterministic"))
        self.assertNotIn("no_api_blocked", plan)
        self.assertFalse(plan.get("no_api_blocked", False))
        self.assertEqual(plan["stack"], "python")
        self.assertEqual(len(plan["tasks"]), 1)
        self.assertEqual(plan["tasks"][0]["description"], LOGIN_REQUEST)
        ask_ai.assert_not_awaited()

        pid = self.main.create_code_project(
            USER_ID_NOAPI, plan["project_name"], LOGIN_REQUEST, plan["stack"], plan["tasks"]
        )
        project = self.main.get_project(pid, owner_id=USER_ID_NOAPI)

        ask_patch, engine_patch, fake_engine = self._patch_ai()
        with ask_patch as ask_ai, engine_patch:
            result = asyncio.run(self.main.process_next_code_task(project))
        # আসল কোড ফেরত এসেছে — stuck মেসেজ নয়
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["source"], "knowledge_base:bangla_rule_engine")
        self.assertNotIn("No API Mode", result["code"])
        self.assertIn('print("সাকসেস")', result["code"])
        self.assertIn('input(', result["code"])
        ask_ai.assert_not_awaited()
        fake_engine.execute_async.assert_not_awaited()
        # ডাটাবেসেও তাই সেভ হয়েছে
        saved = self.main.get_project_tasks(pid)
        self.assertEqual(saved[0]["status"], "done")
        self.assertEqual(saved[0]["source"], "knowledge_base:bangla_rule_engine")
        # জেনারেট হওয়া কোড সত্যিই চলে (মিললে সাকসেস / না মিললে ব্যর্থতা)
        r_ok = run_python_code(result["code"], "admin123\nadmin\n", self.workdir, "int_ok")
        self.assertEqual(r_ok.returncode, 0, r_ok.stderr[:300])
        self.assertIn("সাকসেস", r_ok.stdout)
        r_bad = run_python_code(result["code"], "admin123\nwrong\n", self.workdir, "int_bad")
        self.assertEqual(r_bad.returncode, 0)
        self.assertIn("ব্যর্থ", r_bad.stdout)

    def test_codenext_command_replies_with_real_code(self):
        """কমান্ড-সারফেস পর্যন্ত: /codeproject <লগইন-টেক্সট> → /codenext দিলে
        রিপ্লাইতে আসল কোড আসে, NO_API blocked মেসেজ আসে না।"""
        update = _FakeUpdate(USER_ID_NOAPI)
        context = _FakeContext([LOGIN_REQUEST])
        ask_patch, engine_patch, _fake = self._patch_ai()
        with ask_patch, engine_patch:
            asyncio.run(self.main.codeproject_command(update, context))
        project = self.main.get_active_project(USER_ID_NOAPI)
        self.assertIsNotNone(project)
        plan_texts = "\n".join(update.sent_texts)
        self.assertNotIn("No API Mode", plan_texts)
        self.assertIn("deterministic", plan_texts)  # deterministic নোট দেখায়

        update2 = _FakeUpdate(USER_ID_NOAPI)
        with ask_patch as ask_ai, engine_patch:
            asyncio.run(self.main.codenext_command(update2, _FakeContext([])))
        reply = "\n".join(update2.sent_texts)
        self.assertNotIn("No API Mode", reply)          # stuck/blocked মেসেজ নয়
        self.assertIn("✅", reply)                       # সফল-ধাপের রিপ্লাই
        self.assertIn("input(", reply)                   # আসল কোড ফেরত এসেছে
        self.assertIn("সাকসেস", reply)
        ask_ai.assert_not_awaited()

    # -- পরিপূরকতা: পুরনো dynamic-print matcher অক্ষত -------------------------
    def test_dynamic_print_task_not_stolen_by_rule_engine(self):
        """ক্লাসিক "রান করলে 'X' লেখা আসবে" টাস্ক ইঞ্জিন সক্রিয় থাকা অবস্থায়ও
        knowledge_base:dynamic_print থেকেই আসে — নতুন রুল-ইঞ্জিন এগুলো দাবি করে না।"""
        pid = self.main.create_code_project(
            USER_ID, "ডাইনামিক প্রিন্ট প্রজেক্ট", "টেস্ট", "python",
            [{"title": "হ্যালো প্রিন্ট", "description": "রান করলে 'হ্যালো ওয়ার্ল্ড' লেখা আসবে"}],
        )
        project = self.main.get_project(pid, owner_id=USER_ID)
        ask_patch, engine_patch, fake_engine = self._patch_ai()
        with ask_patch as ask_ai, engine_patch:
            result = asyncio.run(self.main.process_next_code_task(project))
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["source"], "knowledge_base:dynamic_print")
        self.assertIn('print("হ্যালো ওয়ার্ল্ড")', result["code"])
        self.assertNotIn("bangla_rule_engine", str(result["source"]))
        ask_ai.assert_not_awaited()
        fake_engine.execute_async.assert_not_awaited()

    def test_dynamic_print_request_wrapper_still_defers(self):
        # রিকোয়েস্ট-লেভেল: dynamic-print আকৃতির টেক্সটে রুল-ইঞ্জিন wrapper None দেয়
        self.assertIsNone(self.main._match_bangla_rule_request("রান করলে 'হ্যালো' লেখা আসবে"))
        self.assertIsNone(self.main._match_bangla_rule_request(
            'The script prints "bye" when run'))
        # লগইন-টেক্সটে (label, code, python) ফেরে
        wrapped = self.main._match_bangla_rule_request(LOGIN_REQUEST)
        self.assertIsNotNone(wrapped)
        label, code, language = wrapped
        self.assertEqual(label, "bangla_rule_engine")
        self.assertEqual(language, "python")
        self.assertIn('print("সাকসেস")', code)

    def test_match_bangla_rule_task_stack_language_guard(self):
        # v1 ইঞ্জিন শুধু Python — স্ট্যাকে অন্য ভাষা থাকলে জোর করে ম্যাচ হয় না
        self.assertIsNone(self.main.match_bangla_rule_task("t", LOGIN_REQUEST, "Node.js"))
        self.assertIsNone(self.main.match_bangla_rule_task("t", LOGIN_REQUEST, "Java 17"))
        matched = self.main.match_bangla_rule_task("t", LOGIN_REQUEST, "Python (Flask)")
        self.assertIsNotNone(matched)
        self.assertEqual(matched[0], "bangla_rule_engine")
        # রিকোয়েস্ট-টেক্সটেই অন্য ভাষার নাম থাকলেও None
        self.assertIsNone(self.main.match_bangla_rule_task(
            "t", "জাভাস্ক্রিপ্টে নাম মিললে সাকসেস দেখাবে", "python"))

    # -- রিগ্রেশন: No API Mode অতিরিক্ত রিকোয়েস্ট আগের মতোই ব্লকড -------------
    def test_no_api_freeform_request_still_blocked(self):
        with patch.object(self.main, "ask_ai", new=AsyncMock(return_value="# ai\n")):
            plan = asyncio.run(self.main.coding_analyze_and_plan(
                "stripe webhook সহ ইনভয়েস সিস্টেম বানাও", USER_ID_NOAPI))
        self.assertTrue(plan.get("no_api_blocked"))
        self.assertFalse(plan.get("deterministic", False))

        pid = self.main.create_code_project(
            USER_ID_NOAPI, plan["project_name"], "stripe webhook সহ ইনভয়েস সিস্টেম",
            plan["stack"], plan["tasks"])
        project = self.main.get_project(pid, owner_id=USER_ID_NOAPI)
        ask_patch, engine_patch, _fake = self._patch_ai()
        with ask_patch as ask_ai, engine_patch:
            result = asyncio.run(self.main.process_next_code_task(project))
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["source"], "no_api_blocked")
        self.assertNotIn("knowledge_base:bangla_rule_engine", str(result["source"]))
        ask_ai.assert_not_awaited()

    def test_rule_engine_resolves_only_first_pending_task(self):
        """Gap-fix রিগ্রেশন: generic ধাপে ভাঙা প্ল্যানে প্রথম pending ধাপেই
        project-লেভেল ম্যাচ — একই কোড দ্বিতীয় ধাপে stamp হয় না।"""
        pid = self.main.create_code_project(
            USER_ID_NOAPI, "লগইন ডেমো", LOGIN_REQUEST, "python",
            [
                {"title": "Initialize Project Folder", "description": "প্রজেক্ট ফোল্ডার আর এন্ট্রি ফাইল তৈরি করো"},
                {"title": "Implement Login Check", "description": "লগইন যাচাই ইমপ্লিমেন্ট করো"},
            ],
        )
        project = self.main.get_project(pid, owner_id=USER_ID_NOAPI)
        ask_patch, engine_patch, _fake = self._patch_ai()
        with ask_patch as ask_ai, engine_patch:
            first = asyncio.run(self.main.process_next_code_task(project))
            second = asyncio.run(self.main.process_next_code_task(project))
        self.assertEqual(first["status"], "done")
        self.assertEqual(first["source"], "knowledge_base:bangla_rule_engine")
        self.assertIn('print("সাকসেস")', first["code"])
        # দ্বিতীয় ধাপে একই কোড stamp হয় না — no-api-ব্লকড পথে যায়
        self.assertEqual(second["status"], "failed")
        self.assertEqual(second["source"], "no_api_blocked")
        self.assertNotIn('print("সাকসেস")', second.get("code", ""))
        ask_ai.assert_not_awaited()

    def test_fixed_kb_entries_still_win_before_rule_engine(self):
        """matcher চেইনের ক্রম: fixed KB (fizzbuzz) → rule engine → dynamic print।
        KB-তে মেলা টাস্ক এখনও KB থেকেই আসে।"""
        pid = self.main.create_code_project(
            USER_ID, "কেবি প্রজেক্ট", "বিবরণ", "python",
            [{"title": "fizzbuzz", "description": "fizzbuzz ২০ পর্যন্ত লেখো"}],
        )
        project = self.main.get_project(pid, owner_id=USER_ID)
        ask_patch, engine_patch, _fake = self._patch_ai()
        with ask_patch as ask_ai, engine_patch:
            result = asyncio.run(self.main.process_next_code_task(project))
        self.assertEqual(result["source"], "knowledge_base:fizzbuzz")
        ask_ai.assert_not_awaited()


if __name__ == "__main__":
    unittest.main(verbosity=2)
