"""Batch 1 — Core/onboarding কমান্ডগুলোর regression test (আসল main.py কোড চালিয়ে)।

যা যাচাই করা হয়:

  1. সাধারণ ইউজার + normal input → এরর ছাড়া চলে এবং reply আসে।
  2. আর্গুমেন্ট ছাড়া কল (context.args = []) → crash না করে বন্ধুত্বপূর্ণ মেসেজ।
  3. খালি/ভুল ফরম্যাটের input → handled, unhandled exception নয়।
  4. Admin-only কমান্ড সাধারণ ইউজার দিয়ে কল করলে permission gate-এ বাতিল হয়।
  5. যেসব কমান্ড DB touch করে (/memory, /autoreply, /noapimode, voice/speed button) —
     শুধু reply মেসেজ না, users টেবিলের আসল স্টেটও বদলায় কিনা।
  6. Inline callback-এ অজানা/ভুল value এলে crash হবে না এবং DB-তে ভুয়া মান লেখা হবে না
     (bug: `speed_<অজানা>` → KeyError + users.speed-এ ভুয়া মান কমিট হতো)।

main.py একক-file application, তাই test-টি সেটাকে অস্থায়ী ডিরেক্টরিতে কপি করে আলাদা
module হিসেবে import করে — এতে repository-তে bot_data.db বা logs/ তৈরি হয় না।

চালানো যায়:
    python3 tests/test_core_onboarding_commands.py
    python3 -m unittest tests/test_core_onboarding_commands.py -v
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


ADMIN_ID = 111          # ADMIN_IDS env-এ এই আইডি (owner)
USER_ID = 555001        # সাধারণ ইউজার
OTHER_USER_ID = 555002


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
    """reply_text()-এর রিটার্ন — /ping-এর মতো কমান্ড edit_text() কল করে।"""

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
        self.document = None
        self.voice = None
        self.text = ""
        self.sent: list[str] = []
        self.deleted = False

    async def reply_text(self, text: str, **_kwargs):
        self.sent.append(text)
        return _SentMessage(self.sent)

    async def reply_voice(self, *args, **kwargs):
        return None

    async def delete(self):
        self.deleted = True


class FakeQuery:
    def __init__(self, user_id: int, data: str):
        self.from_user = FakeUser(user_id)
        self.data = data
        self.answered = False
        self.edited: list[str] = []
        self.markups: list = []

    async def answer(self, *args, **kwargs):
        self.answered = True

    async def edit_message_text(self, text: str, reply_markup=None, **_kwargs):
        self.edited.append(text)
        self.markups.append(reply_markup)


class FakeUpdate:
    def __init__(self, user_id: int, callback_data: str | None = None):
        self.effective_user = FakeUser(user_id)
        self.effective_chat = FakeChat()
        self.message = FakeMessage(user_id)
        self.effective_message = self.message
        self.callback_query = FakeQuery(user_id, callback_data) if callback_data else None


class FakeBot:
    username = "test_bot"

    def __init__(self):
        self.sent: list[dict] = []

    async def send_message(self, chat_id=None, text="", **kwargs):
        self.sent.append({"chat_id": chat_id, "text": text})
        return None


class FakeJobQueue:
    def __init__(self):
        self.jobs: list = []

    def run_once(self, callback, when, **kwargs):
        self.jobs.append((callback, when, kwargs))
        return object()


class FakeContext:
    def __init__(self, args: list | None = None):
        self.bot = FakeBot()
        self.args: list = list(args or [])
        self.user_data: dict = {}
        self.bot_data: dict = {}
        self.job_queue = FakeJobQueue()


def run(coro):
    """প্রতিটা কল আলাদা event loop-এ — python-telegram-bot handler-গুলো async।"""
    return asyncio.run(coro)


class CoreOnboardingCommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-core-test-")
        shutil.copyfile(os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", str(ADMIN_ID))
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

        logging.disable(logging.CRITICAL)

        module_name = "rohan_core_onboarding_test_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()
        for uid in (USER_ID, OTHER_USER_ID):
            cls.main.register_user(uid)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_core_onboarding_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    # ---------------- helpers ----------------
    def call(self, handler, args=None, user_id=USER_ID):
        update = FakeUpdate(user_id)
        ctx = FakeContext(args)
        run(handler(update, ctx))
        return update, "".join(update.message.sent)

    def callback(self, data, user_id=USER_ID):
        """button_callback চালায়; রিটার্ন করে (update, মেসেজের লেখা, বাটনের callback_data তালিকা)।"""
        update = FakeUpdate(user_id, data)
        run(self.main.button_callback(update, FakeContext()))
        q = update.callback_query
        offered = [
            b.callback_data
            for m in q.markups if m is not None
            for row in m.inline_keyboard
            for b in row
        ]
        return update, "".join(q.edited), offered

    def db_scalar(self, sql, params=()):
        conn = self.main.get_conn()
        try:
            return conn.execute(sql, params).fetchone()[0]
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # 1. সাধারণ ইউজার + normal input → এরর ছাড়া চলে এবং reply আসে
    # -----------------------------------------------------------------
    def test_plain_commands_reply_without_error(self):
        plain = [
            "start_command", "help_command", "menu_command", "about_command",
            "profile_command", "mylimit_command", "ping_command", "uptime_command",
            "settings_command", "leaderboard_command", "setlang_command",
            "setvoice_command", "setspeed_command", "myreferrals_command",
            "myapikey_command", "clearmemory_command",
        ]
        for name in plain:
            with self.subTest(command=name):
                _update, body = self.call(getattr(self.main, name), [])
                self.assertTrue(body.strip(), f"{name} কোনো reply পাঠায়নি")

    def test_commands_with_normal_args_reply(self):
        cases = [
            ("feedback_command", ["ভালো", "বট"]),
            ("bugreport_command", ["crash", "করে"]),
            ("detectlang_command", ["hello", "there"]),
            ("memory_command", ["on"]),
            ("autoreply_command", ["on"]),
            ("noapimode_command", ["on"]),
            ("setapikey_command", ["groq", "gsk_abcdefghijklmnop"]),
            ("removeapikey_command", ["all"]),
        ]
        for name, args in cases:
            with self.subTest(command=name):
                _update, body = self.call(getattr(self.main, name), args)
                self.assertTrue(body.strip(), f"{name} কোনো reply পাঠায়নি")

    # -----------------------------------------------------------------
    # 2. আর্গুমেন্ট ছাড়া কল → crash না করে বন্ধুত্বপূর্ণ মেসেজ
    # -----------------------------------------------------------------
    def test_missing_args_give_friendly_usage_not_crash(self):
        cases = [
            ("feedback_command", "/feedback"),
            ("bugreport_command", "/bugreport"),
            ("detectlang_command", "/detectlang"),
            ("setapikey_command", "/setapikey"),
            ("removeapikey_command", "/removeapikey"),
        ]
        for name, usage in cases:
            with self.subTest(command=name):
                _update, body = self.call(getattr(self.main, name), [])
                self.assertIn(usage, body, f"{name}-এর usage hint নেই: {body[:60]}")

    def test_partial_setapikey_args_show_usage(self):
        _update, body = self.call(self.main.setapikey_command, ["groq"])
        self.assertIn("/setapikey", body)
        self.assertFalse(
            self.db_scalar("SELECT own_groq_key FROM users WHERE user_id = ?", (USER_ID,)),
            "অসম্পূর্ণ আর্গুমেন্টে Key সেভ হওয়া উচিত না",
        )

    def test_memory_and_autoreply_without_args_show_current_state(self):
        for name, label in (("memory_command", "AI Memory"), ("autoreply_command", "Auto Reply")):
            with self.subTest(command=name):
                _update, body = self.call(getattr(self.main, name), [])
                self.assertIn(label, body)
                self.assertIn("বর্তমানে", body)

    def test_noapimode_without_args_shows_status_and_usage(self):
        _update, body = self.call(self.main.noapimode_command, [])
        self.assertIn("No API Call Mode", body)
        self.assertIn("/noapimode on", body)

    # -----------------------------------------------------------------
    # 3. খালি/ভুল ফরম্যাটের input → handled, unhandled exception নয়
    # -----------------------------------------------------------------
    def test_invalid_on_off_values_show_state_instead_of_crashing(self):
        for name in ("memory_command", "autoreply_command"):
            for bad in (["maybe"], ["ONN"], ["1"], ["", "x"]):
                with self.subTest(command=name, args=bad):
                    _update, body = self.call(getattr(self.main, name), bad)
                    self.assertTrue(body.strip())

    def test_invalid_noapimode_arg_shows_usage(self):
        _update, body = self.call(self.main.noapimode_command, ["yes-please"])
        self.assertIn("/noapimode on", body)

    def test_start_command_bad_referral_payload_is_ignored(self):
        """ভুয়া ref payload crash করাবে না, ভুয়া রেফারারও তৈরি হবে না।"""
        for payload in (["ref_notanumber"], ["ref_"], ["ref_-5"], ["ref_99999999999999999999"], ["junk"]):
            with self.subTest(payload=payload):
                _update, body = self.call(self.main.start_command, payload, user_id=OTHER_USER_ID)
                self.assertIn("স্বাগতম", body)
        self.assertEqual(
            self.db_scalar("SELECT referred_by FROM users WHERE user_id = ?", (OTHER_USER_ID,)),
            0,
        )

    def test_setapikey_rejects_unknown_provider_and_blank_key(self):
        _update, body = self.call(self.main.setapikey_command, ["nope", "gsk_abcdefghijklmnop"])
        self.assertIn("প্রোভাইডার", body)
        self.assertFalse(
            self.db_scalar("SELECT own_openrouter_key FROM users WHERE user_id = ?", (USER_ID,)),
            "অজানা প্রোভাইডারে Key সেভ হওয়া উচিত না",
        )

    def test_removeapikey_unknown_provider_is_handled(self):
        _update, body = self.call(self.main.removeapikey_command, ["nope"])
        self.assertTrue(body.strip())

    def test_unknown_inline_menu_and_lang_callbacks_give_feedback(self):
        """অজানা menu/lang callback চাপলে ইউজার অন্তত একটা বার্তা পাবে — নিঃশব্দ no-op নয়।"""
        for data in ("menu_nosuchsection", "lang_nosuchlang"):
            with self.subTest(callback=data):
                _update, edited, _offered = self.callback(data)
                self.assertTrue(edited.strip(), f"{data}-তে কোনো ফিডব্যাক নেই (নিঃশব্দ no-op)")

    # -----------------------------------------------------------------
    # 4. Admin-only কমান্ড সাধারণ ইউজার দিয়ে কল করলে permission gate
    # -----------------------------------------------------------------
    def test_admin_only_core_commands_are_gated(self):
        for name in ("brainstatus_command", "decisionhistory_command"):
            with self.subTest(command=name):
                _update, body = self.call(getattr(self.main, name), ["10"], user_id=USER_ID)
                self.assertIn("অ্যাডমিন", body)

        _update, body = self.call(self.main.decisionhistory_command, ["notanumber"], user_id=USER_ID)
        self.assertIn("অ্যাডমিন", body)

    def test_admin_can_open_admin_only_core_commands(self):
        for name in ("brainstatus_command", "decisionhistory_command"):
            with self.subTest(command=name):
                _update, body = self.call(getattr(self.main, name), ["10"], user_id=ADMIN_ID)
                self.assertNotIn("শুধু অ্যাডমিনের জন্য", body)

    # -----------------------------------------------------------------
    # 5. DB-touching কমান্ড — reply নয়, আসল স্টেট বদলায় কিনা
    # -----------------------------------------------------------------
    def test_memory_command_persists_to_db(self):
        self.call(self.main.memory_command, ["off"])
        self.assertEqual(
            self.db_scalar("SELECT memory_enabled FROM users WHERE user_id = ?", (USER_ID,)), 0
        )
        self.call(self.main.memory_command, ["on"])
        self.assertEqual(
            self.db_scalar("SELECT memory_enabled FROM users WHERE user_id = ?", (USER_ID,)), 1
        )

    def test_autoreply_command_persists_to_db(self):
        self.call(self.main.autoreply_command, ["off"])
        self.assertEqual(
            self.db_scalar("SELECT auto_reply FROM users WHERE user_id = ?", (USER_ID,)), 0
        )
        self.call(self.main.autoreply_command, ["on"])
        self.assertEqual(
            self.db_scalar("SELECT auto_reply FROM users WHERE user_id = ?", (USER_ID,)), 1
        )

    def test_no_api_mode_persists_and_guard_reads_it(self):
        """/noapimode on → DB-তে 1, আর is_no_api_mode() guard সেটাই পড়বে।"""
        self.call(self.main.noapimode_command, ["on"])
        self.assertEqual(
            self.db_scalar("SELECT no_api_mode FROM users WHERE user_id = ?", (USER_ID,)), 1
        )
        self.assertTrue(self.main.is_no_api_mode(USER_ID))
        # অন্য ইউজারের চ্যাটে প্রভাব পড়বে না (per-user)।
        self.assertFalse(self.main.is_no_api_mode(OTHER_USER_ID))

        self.call(self.main.noapimode_command, ["off"])
        self.assertEqual(
            self.db_scalar("SELECT no_api_mode FROM users WHERE user_id = ?", (USER_ID,)), 0
        )
        self.assertFalse(self.main.is_no_api_mode(USER_ID))

    def test_valid_voice_and_speed_callbacks_persist_to_db(self):
        self.callback("voice_female")
        self.assertEqual(self.db_scalar("SELECT voice FROM users WHERE user_id = ?", (USER_ID,)), "female")
        self.callback("voice_male")
        self.assertEqual(self.db_scalar("SELECT voice FROM users WHERE user_id = ?", (USER_ID,)), "male")

        self.callback("speed_fast")
        self.assertEqual(self.db_scalar("SELECT speed FROM users WHERE user_id = ?", (USER_ID,)), "fast")
        self.callback("speed_slow")
        self.assertEqual(self.db_scalar("SELECT speed FROM users WHERE user_id = ?", (USER_ID,)), "slow")
        self.callback("speed_normal")
        self.assertEqual(self.db_scalar("SELECT speed FROM users WHERE user_id = ?", (USER_ID,)), "normal")

    def test_settings_buttons_persist_to_db(self):
        before_auto, before_mem, _ = self.main.get_user_settings(USER_ID)
        self.callback("settings_toggle_autoreply")
        after_auto, _, _ = self.main.get_user_settings(USER_ID)
        self.assertNotEqual(before_auto, after_auto)
        self.assertEqual(
            self.db_scalar("SELECT auto_reply FROM users WHERE user_id = ?", (USER_ID,)),
            1 if after_auto else 0,
        )

        self.callback("settings_toggle_memory")
        _, after_mem, _ = self.main.get_user_settings(USER_ID)
        self.assertNotEqual(before_mem, after_mem)

        self.main.save_message(USER_ID, "user", "পুরনো কথা")
        self.assertTrue(self.main.get_recent_history(USER_ID))
        self.callback("settings_clear_memory")
        self.assertFalse(self.main.get_recent_history(USER_ID))

    def test_language_callback_persists_to_db(self):
        """lang_<code> → users.language + lang_manual=1; lang_auto → lang_manual=0 (ভাষা
        কলামটা আগের মানেই থাকে — 'auto' মোডটা lang_manual ফ্ল্যাগ দিয়েই নির্ধারিত হয়,
        get_effective_language()/localize() সেটাই পড়ে)।"""
        self.callback("lang_en")
        self.assertEqual(self.db_scalar("SELECT language FROM users WHERE user_id = ?", (USER_ID,)), "en")
        self.assertEqual(self.db_scalar("SELECT lang_manual FROM users WHERE user_id = ?", (USER_ID,)), 1)
        self.assertEqual(self.main.get_effective_language(USER_ID), ("en", True))

        self.callback("lang_auto")
        self.assertEqual(
            self.db_scalar("SELECT lang_manual FROM users WHERE user_id = ?", (USER_ID,)), 0,
            "lang_auto চাপার পরেও lang_manual=1 রয়ে গেছে",
        )
        self.assertFalse(self.main.get_effective_language(USER_ID)[1])
        # Auto মোডে localize() মূল বাংলা লেখাই ফেরত দেবে (AI অনুবাদ কল হবে না)।
        self.assertEqual(run(self.main.localize(USER_ID, "পরীক্ষার লেখা")), "পরীক্ষার লেখা")

        text, _markup = run(self.main.build_settings_view(USER_ID))
        self.assertIn("স্বয়ংক্রিয়", text)

    def test_setapikey_persists_and_myapikey_masks_it(self):
        _update, _body = self.call(self.main.setapikey_command, ["groq", "gsk_abcdefghijklmnop"])
        stored = self.db_scalar("SELECT own_groq_key FROM users WHERE user_id = ?", (USER_ID,))
        self.assertEqual(stored, "gsk_abcdefghijklmnop")

        _update, body = self.call(self.main.myapikey_command, [])
        self.assertNotIn("gsk_abcdefghijklmnop", body, "/myapikey পুরো Key ফাঁস করছে")
        self.assertIn(self.main.mask_api_key("gsk_abcdefghijklmnop"), body)

        _update, _body = self.call(self.main.removeapikey_command, ["groq"])
        self.assertFalse(
            self.db_scalar("SELECT own_groq_key FROM users WHERE user_id = ?", (USER_ID,)),
            "/removeapikey groq — Key মুছে যায়নি",
        )

    # -----------------------------------------------------------------
    # 6. REGRESSION — অজানা voice/speed callback: crash + DB corruption
    # -----------------------------------------------------------------
    def test_unknown_speed_callback_does_not_crash_or_corrupt_db(self):
        """`speed_<অজানা>` আগে KeyError ছুঁড়ত এবং তার আগেই users.speed-এ ভুয়া মান কমিট হতো
        (ফলে /profile-এ "গতি পছন্দ: bogusvalue" ছাপা হতো)।"""
        self.callback("speed_normal")
        _update, edited, offered = self.callback("speed_bogusvalue")
        self.assertTrue(edited.strip(), "ভুল speed callback-এ ইউজার কোনো ফিডব্যাক পায়নি")
        self.assertEqual(
            self.db_scalar("SELECT speed FROM users WHERE user_id = ?", (USER_ID,)),
            "normal",
            "ভুয়া speed মান DB-তে লেখা হয়েছে",
        )
        self.assertIn("speed_normal", offered, "বৈধ অপশনগুলো আবার দেখানো হয়নি")
        # ভুয়া মান DB-তে ঢুকলে /profile-এ সেটাই ছাপা হতো — এখন হবে না।
        _update, body = self.call(self.main.profile_command, [])
        self.assertNotIn("bogusvalue", body, "/profile-এ ভুয়া speed মান ছাপা হচ্ছে")
        self.assertIn("normal", body)

    def test_unknown_voice_callback_does_not_corrupt_db(self):
        """`voice_<অজানা>` আগে কোনো এরর না দেখিয়েই users.voice-এ ভুয়া মান লিখে ফেলত,
        আর ইউজারকে 'মেয়ে কণ্ঠ সেট হয়েছে' বলে ভুল নিশ্চিতকরণ দিত।"""
        self.callback("voice_male")
        _update, edited, offered = self.callback("voice_bogusvalue")
        self.assertEqual(
            self.db_scalar("SELECT voice FROM users WHERE user_id = ?", (USER_ID,)),
            "male",
            "ভুয়া voice মান DB-তে লেখা হয়েছে",
        )
        self.assertNotIn("কণ্ঠ সেট করা হয়েছে", edited, "ভুয়া voice-এ মিথ্যা নিশ্চিতকরণ দেখানো হয়েছে")
        self.assertEqual(offered, ["voice_male", "voice_female"], "বৈধ অপশনগুলো আবার দেখানো হয়নি")
        _update, body = self.call(self.main.profile_command, [])
        self.assertNotIn("bogusvalue", body, "/profile-এ ভুয়া voice মান ছাপা হচ্ছে")

    def test_settings_view_survives_after_valid_speed_change(self):
        """ভালো মান সেটের পরে /settings আবার খোলা যায় (speed label ম্যাপিং ঠিক আছে)।"""
        self.callback("speed_fast")
        text, _markup = run(self.main.build_settings_view(USER_ID))
        self.assertIn("দ্রুত", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
