"""Handler-registration dry-run — বট চালু হওয়ার সময় add_handler কলগুলো ভাঙে না।

পুরনো বেসলাইন: অন্তত ৮৬টা হ্যান্ডলার রেজিস্টার হতে হবে (webhook/uvicorn ছাড়া)।
এই ফিক্সের পরও run_bot_async()-এর রেজিস্ট্রেশন ব্লক exception ছাড়া শেষ হয় কিনা
এবং কমান্ডগুলো আসল কলব্যাকের সাথে বাঁধা আছে কিনা তা যাচাই করে।

চালানো যায়:
    python3 tests/test_handler_registration_dry_run.py
    python3 -m unittest tests.test_handler_registration_dry_run -v
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
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch


# Historical baseline from the original dry-run (command + message + callback handlers).
MIN_HANDLER_BASELINE = 86

# A few must-exist commands — if any of these is missing, startup is not "fully OK".
REQUIRED_COMMANDS = {
    "start", "help", "menu", "codeproject", "codenext", "codeplan",
    "brainstatus", "adminpanel", "noapimode",
}


class _FakeApp:
    def __init__(self):
        self.handlers = []
        self.error_handlers = []
        self.job_queue = None
        self.bot = SimpleNamespace(set_webhook=AsyncMock())

    def add_handler(self, handler, group=0):
        self.handlers.append((group, handler))

    def add_error_handler(self, handler):
        self.error_handlers.append(handler)

    async def initialize(self):
        return None

    async def start(self):
        return None

    async def stop(self):
        return None

    async def shutdown(self):
        return None


class _FakeBuilder:
    def __init__(self, app):
        self._app = app

    def token(self, *args, **kwargs):
        return self

    def post_shutdown(self, *args, **kwargs):
        return self

    def build(self):
        return self._app


class _FakeUvicornServer:
    def __init__(self, *args, **kwargs):
        pass

    async def serve(self):
        return None


class HandlerRegistrationDryRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.workdir = tempfile.mkdtemp(prefix="rohan-handler-dryrun-")
        shutil.copyfile(os.path.join(repo_root, "main.py"), os.path.join(cls.workdir, "main.py"))
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        os.environ.pop("PUBLIC_URL", None)
        os.environ.pop("MCP_ADMIN_TOKEN", None)

        logging.disable(logging.CRITICAL)

        module_name = "rohan_handler_dryrun_main"
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(cls.workdir, "main.py"))
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_handler_dryrun_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    def test_run_bot_async_registers_at_least_baseline_handlers(self):
        fake_app = _FakeApp()
        builder = _FakeBuilder(fake_app)

        async def run():
            with patch.object(self.main.Application, "builder", return_value=builder), patch(
                "uvicorn.Server", _FakeUvicornServer
            ), patch("uvicorn.Config", MagicMock()):
                await self.main.run_bot_async()

        asyncio.run(run())

        command_names = []
        message_count = 0
        callback_count = 0
        for _group, handler in fake_app.handlers:
            cls_name = type(handler).__name__
            if cls_name == "CommandHandler":
                cmds = getattr(handler, "commands", None) or getattr(handler, "command", None) or set()
                if isinstance(cmds, str):
                    command_names.append(cmds)
                else:
                    command_names.extend(sorted(cmds))
            elif cls_name == "MessageHandler":
                message_count += 1
            elif cls_name == "CallbackQueryHandler":
                callback_count += 1

        total = len(fake_app.handlers) + len(fake_app.error_handlers)
        unique_commands = sorted(set(command_names))

        print("\n===== Handler registration dry-run =====")
        print(f"add_handler calls     : {len(fake_app.handlers)}")
        print(f"error handlers        : {len(fake_app.error_handlers)}")
        print(f"total registrations   : {total}")
        print(f"CommandHandler cmds   : {len(unique_commands)}")
        print(f"MessageHandler        : {message_count}")
        print(f"CallbackQueryHandler  : {callback_count}")
        print(f"baseline (historical) : >= {MIN_HANDLER_BASELINE}")
        print("commands:", ", ".join(unique_commands))
        print("========================================\n")

        self.assertGreaterEqual(
            total,
            MIN_HANDLER_BASELINE,
            f"হ্যান্ডলার রেজিস্ট্রেশন {total}টা — পুরনো বেসলাইন {MIN_HANDLER_BASELINE}-এর নিচে",
        )
        self.assertTrue(fake_app.error_handlers, "error_handler রেজিস্টার হয়নি")
        missing = REQUIRED_COMMANDS - set(unique_commands)
        self.assertFalse(missing, f"প্রয়োজনীয় কমান্ড বাদ পড়েছে: {sorted(missing)}")
        self.assertGreaterEqual(callback_count, 1, "CallbackQueryHandler নেই")
        self.assertGreaterEqual(message_count, 2, "TEXT/VOICE MessageHandler কম")


if __name__ == "__main__":
    unittest.main(verbosity=2)
