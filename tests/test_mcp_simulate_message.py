"""MCP টুল `simulate_message`-এর টেস্ট — বটের রিপ্লাই সিমুলেশন (টেলিগ্রাম/প্রোডাকশন ছাড়া)।

যা যাচাই করা হয়:

  1. **/ping** — simulate_message("/ping") রিপ্লাইতে পং/pong-জাতীয় সাড়া ফেরে এবং
     রিটার্ন-শেপ হয় {"status": "ok", "replies": [...], "user_id": ...}।

  2. **No API Mode রিগ্রেশন (PR #21 bangla_rule_engine)** — "/noapimode on" →
     "/codeproject <লগইন-রিকোয়েস্ট>" → "/codenext" চালালে শেষ রিপ্লাইতে আসল
     deterministic কোড আসে (✅ + input( + সাকসেস), আর NO_API_CODING_BLOCKED_MESSAGE
     দেখানো হয় না (AI/Decision Engine কোনোভাবেই ডাকা হয় না)।

  3. **অচেনা কমান্ড** — "/এমন_কমান্ড_নেই" ক্র্যাশ না করে reasonable ফল দেয়
     (status ok/error, replies তালিকা), সাধারণ চ্যাট-ফলব্যাক (chat_general) অক্ষত থাকে।

  4. **কমান্ড ছাড়া সাধারণ টেক্সট** — chat_general-এ যায় এবং রিপ্লাই ফেরে।

চালানো যায়:
    python3 tests/test_mcp_simulate_message.py
    python3 -m unittest tests.test_mcp_simulate_message -v
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

TEST_USER_ID = 990000001

# test_bangla_rule_engine.py-র acceptance ইনপুট — হুবহু (deterministic লগইন-সিস্টেম রিকোয়েস্ট)
LOGIN_REQUEST = (
    "তোমাকে এখন একটি সিস্টেম বানাতে হবে ওই সিস্টেমে একটি ডাটাবেজ থাকবে "
    "ওই ডাটাবেজে ইউজার আইডি এবং পাসওয়ার্ড থাকবে আমি যদি পাসওয়ার্ড ইনপুট দেই "
    "তাহলে সে ইউজার নেম চাইবে এবং দুইটি মিললে সাকসেস দেখাবে"
)


def run(coro):
    # unittest discover-এ আগের কোনো test module asyncio.run() ব্যবহার করলে গ্লোবাল
    # event loop None হয়ে যায় আর get_event_loop() RuntimeError ছোড়ে (Python 3.11+)।
    # তখন নতুন loop বানিয়ে আগের মতোই গ্লোবালি সেট করি।
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# ---------------------------------------------------------------------------
# ফেক HTTP লেয়ার — chat_general-এর Browse Search (DuckDuckGo/Wikipedia) কল আটকে দেয়
# ---------------------------------------------------------------------------
class _FakeResponse:
    def __init__(self, status_code: int = 404, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}

    def json(self):
        return self._payload


class _FakeHTTPClient:
    """সব রিকোয়েস্টে খালি/404 ফেরত দেয় — ব্রাউজ-সার্চ সবসময় 'কিছু পাওয়া যায়নি' বলে
    AI-ফলব্যাকে চলে যায়, কোনো আসল নেটওয়ার্ক কল হয় না।"""

    async def get(self, url, params=None, timeout=None):
        return _FakeResponse(404, {})

    async def post(self, url, json=None, timeout=None):
        return _FakeResponse(404, {})


# ===========================================================================
# মূল মডিউল লোডার — main.py-কে নিজের টেম্প-ডিরেক্টরিতে চালায় (আসল DB নষ্ট না করে)
# ===========================================================================
class SimulateMessageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="rohan-sim-msg-")
        shutil.copyfile(os.path.join(REPO_ROOT, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        # টেস্ট নিজে নিয়ন্ত্রণ করবে — বাইরের env থেকে Key আসা যাবে না।
        os.environ.pop("TAVILY_API_KEY", None)

        logging.disable(logging.CRITICAL)

        # REPO_ROOT ইতিমধ্যে sys.path-এ — তাই কপি করা main.py-ও bangla_rule_engine
        # ইমপোর্ট করতে পারে (No API Mode-এর deterministic কোড-জেনারেশন সক্রিয় থাকে)।
        module_name = "rohan_sim_msg_test_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        cls.main.seed_brain_os_defaults()

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_sim_msg_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def setUp(self):
        # কমান্ড-লেভেল টেস্টে flood/quota/decision-cache স্টেট পরিষ্কার রাখা
        self.main._last_message_time.clear()
        self.main._flood_strikes.clear()
        self.main._flood_blocked_until.clear()
        self.main.decision_engine_service.clear_cache()

    def _patch_offline(self):
        """chat_general-এর সব নেটওয়ার্ক/AI পথ অফলাইন মকে প্রতিস্থাপন করে।"""
        return (
            patch.object(self.main, "get_http_client", new=AsyncMock(return_value=_FakeHTTPClient())),
            patch.object(self.main, "ask_ai", new=AsyncMock(return_value="টেস্ট AI উত্তর")),
            patch.object(self.main, "ask_ai_with_history", new=AsyncMock(return_value="টেস্ট AI উত্তর")),
            patch.object(self.main, "should_show_own_key_hint", return_value=False),
        )

    # ------------------------------------------------------------------
    # 1. /ping — pong-জাতীয় রিপ্লাই + রিটার্ন-শেপ
    # ------------------------------------------------------------------
    def test_ping_returns_pong_like_reply(self):
        result = run(self.main.simulate_message("/ping"))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["user_id"], TEST_USER_ID)
        self.assertIsInstance(result["replies"], list)
        joined = "\n".join(result["replies"])
        self.assertIn("পং", joined)  # pong-জাতীয় সাড়া

    # ------------------------------------------------------------------
    # 2. No API Mode রিগ্রেশন: /noapimode on → /codeproject → /codenext
    # ------------------------------------------------------------------
    def test_noapi_codeproject_codenext_returns_real_code(self):
        uid = TEST_USER_ID

        on = run(self.main.simulate_message("/noapimode on", uid))
        self.assertEqual(on["status"], "ok")
        self.assertTrue(self.main.is_no_api_mode(uid))

        ask_patch = patch.object(self.main, "ask_ai", new=AsyncMock(return_value="# ai\n"))
        with ask_patch as ask_ai:
            plan = run(self.main.simulate_message(f"/codeproject {LOGIN_REQUEST}", uid))
            result = run(self.main.simulate_message("/codenext", uid))

        # প্ল্যান deterministic, blocked-নয়
        self.assertEqual(plan["status"], "ok")
        plan_texts = "\n".join(plan["replies"])
        self.assertNotIn("No API Mode", plan_texts)

        # শেষ রিপ্লাইতে আসল কাজ-করা কোড — stuck/blocked মেসেজ নয়
        self.assertEqual(result["status"], "ok")
        reply = "\n".join(result["replies"])
        self.assertIn("✅", reply)
        self.assertIn("input(", reply)
        self.assertIn("সাকসেস", reply)
        self.assertNotIn("No API Mode", reply)
        self.assertNotIn(self.main.NO_API_CODING_BLOCKED_MESSAGE, reply)
        # deterministic পথে AI কল হয়ইনি
        ask_ai.assert_not_awaited()

    # ------------------------------------------------------------------
    # 3. অচেনা কমান্ড — ক্র্যাশ না করে reasonable ফল
    # ------------------------------------------------------------------
    def test_unknown_command_does_not_crash(self):
        http_patch, ask_patch, history_patch, hint_patch = self._patch_offline()
        with http_patch, ask_patch, history_patch, hint_patch:
            result = run(self.main.simulate_message("/এমন_কমান্ড_নেই"))
        self.assertIn(result["status"], ("ok", "error"))
        self.assertIsInstance(result["replies"], list)

    # ------------------------------------------------------------------
    # 4. কমান্ড ছাড়া সাধারণ টেক্সট — chat_general-এ যায়
    # ------------------------------------------------------------------
    def test_plain_text_goes_to_chat_general(self):
        http_patch, ask_patch, history_patch, hint_patch = self._patch_offline()
        with http_patch, ask_patch, history_patch, hint_patch:
            result = run(self.main.simulate_message("হ্যালো, কেমন আছো?"))
        self.assertEqual(result["status"], "ok")
        self.assertIsInstance(result["replies"], list)
        # chat_general-এর সিগনেচার "ভাবছি..." thinking মেসেজ আগে আসে, তারপর আসল উত্তর
        self.assertTrue(result["replies"])
        self.assertIn("ভাবছি...", result["replies"][0])
        self.assertTrue(any(len(r.strip()) > 0 for r in result["replies"][1:]))

    # ------------------------------------------------------------------
    # 5. ডিফল্ট user_id আলাদা টেস্ট-ডেটা আইসোলেশনের জন্য (idempotent register)
    # ------------------------------------------------------------------
    def test_default_user_isolated_and_register_idempotent(self):
        first = run(self.main.simulate_message("/ping"))
        second = run(self.main.simulate_message("/ping"))
        self.assertEqual(first["user_id"], TEST_USER_ID)
        self.assertEqual(second["user_id"], TEST_USER_ID)
        # register_user idempotent — একই ইউজার দ্বিতীয়বার register করলে নতুন হয় না
        self.assertFalse(self.main.register_user(TEST_USER_ID))


if __name__ == "__main__":
    unittest.main(verbosity=2)
