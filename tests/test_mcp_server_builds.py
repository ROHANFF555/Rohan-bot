"""MCP সার্ভার বিল্ড-স্মোক টেস্ট — `main._build_mcp_server()` আসলেই কাজ করে কি না।

পটভূমি (Render-এর আসল বাগ)
--------------------------
`requirements.txt`-এ `fastmcp` আনপিনড থাকায় লেটেস্ট ডিপ্লয়ে `fastmcp` 4.x
(আর `mcp` 2.x) ইনস্টল হয়ে গিয়েছিল। সেখানে —

  * `mcp.server.fastmcp` মডিউলটাই আর নেই (তাই main.py-এর `from mcp.server
    .fastmcp import FastMCP` → ImportError → ফলব্যাক `from fastmcp import
    FastMCP` চালু হয়), এবং
  * `FastMCP()`-এর কনস্ট্রাক্টর থেকে `stateless_http`/`json_response`/
    `streamable_http_path`/`transport_security` kwarg-গুলো সরিয়ে দেওয়া হয়েছে
    (v3+ থেকে এগুলো `.run()`/`.http_app()`-এ দিতে হয়)।

ফলে `_build_mcp_server()` `TypeError` ছুঁড়ত; সেটা `run_bot_async()`-এর বড়
`try/except`-এর ভেতরে চাপা পড়ে যেত — বট ক্র্যাশ করত না, কিন্তু `/oauth/register`,
`/oauth/authorize`, `/mcp`, `/.well-known/oauth-*` রুটগুলো চুপচাপ রেজিস্টার
হতোই না, তাই Claude-এর মতো MCP ক্লায়েন্ট "Couldn't register with sign-in
service" দেখাত (`/oauth/register` → 404)।

ফিক্স: `requirements.txt`-এ `fastmcp>=2.0,<3` (v2-লাইন)। এই টেস্টটা সেই
ধারণাটাই লক করে দেয় — v2-লাইনে এই ৪টা kwarg কনস্ট্রাক্টরেই গ্রহণযোগ্য, তাই
`_build_mcp_server()` এক্সেপশন ছাড়াই সার্ভার বানাতে পারে।

যা যাচাই করা হয়
----------------
  1. `main._build_mcp_server(app=None)` কোনো এক্সেপশন ছাড়াই একটা FastMCP
     অবজেক্ট রিটার্ন করে, যাতে `streamable_http_app()` আছে (run_bot_async()
     মূলত এইটাই মাউন্ট করে)।
  2. main.py যে FastMCP ক্লাসটা রিজলভ করে (`mcp.server.fastmcp` অথবা
     ফলব্যাক `fastmcp`), তার কনস্ট্রাক্টর `stateless_http`, `json_response`,
     `streamable_http_path`, `transport_security` — ৪টা kwarg-ই নেয়
     (v3+/v4-এ এই ধাপেই ফেল করবে — আসল বাগ)।
  3. বিল্ড হওয়া সার্ভারে `simulate_message` টুল রেজিস্টার্ড আছে (PR #22)।
  4. কনস্ট্রাক্টরে পাঠানো মানগুলো সত্যিই ধরা হয়েছে (stateless_http/
     json_response True, streamable_http_path "/") — double-path-mount
     ফিক্সটা (Mount("/mcp") + ভেতরের path "/") অক্ষত আছে।
  5. `PUBLIC_URL` সেট থাকা অবস্থায়ও (Render-এর আসল কনফিগ, যেখানে
     `TransportSecuritySettings` বানানো হয়) বিল্ড সফল হয়।

চালানো যায়:
    python3 -m venv venv && venv/bin/pip install -r requirements.txt
    venv/bin/python tests/test_mcp_server_builds.py
    venv/bin/python -m unittest tests.test_mcp_server_builds -v
"""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import logging
import os
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# main.py-এর v2-স্টাইল কনস্ট্রাক্টর-কলে ব্যবহৃত ৪টি kwarg — v3+/v4-এ এগুলো নেই।
REQUIRED_CTOR_KWARGS = (
    "stateless_http",
    "json_response",
    "streamable_http_path",
    "transport_security",
)


def _dist_version(dist_name: str) -> str:
    try:
        import importlib.metadata as md

        return md.version(dist_name)
    except Exception:  # noqa: BLE001 — ইনস্টল না থাকলেই শুধু None
        return "(ইনস্টল নেই)"


def _resolve_fastmcp_class():
    """main._build_mcp_server()-এর মতোই FastMCP ক্লাস রিজলভ করে — (ক্লাস, import path)।"""
    try:
        from mcp.server.fastmcp import FastMCP

        return FastMCP, "mcp.server.fastmcp"
    except ImportError:
        from fastmcp import FastMCP

        return FastMCP, "fastmcp"


try:
    _FASTMCP_CLASS, _FASTMCP_IMPORT_PATH = _resolve_fastmcp_class()
    _MCP_AVAILABLE = True
    _MCP_SKIP_REASON = ""
except Exception as exc:  # noqa: BLE001 — mcp/fastmcp কোনোটাই ইনস্টল নেই
    _FASTMCP_CLASS = None
    _FASTMCP_IMPORT_PATH = ""
    _MCP_AVAILABLE = False
    _MCP_SKIP_REASON = f"mcp/fastmcp ইনস্টল নেই: {exc}"


def run(coro):
    """unittest discover-এ আগের কোনো test module asyncio.run() ব্যবহার করলে
    গ্লোবাল event loop None হয়ে যায় আর get_event_loop() RuntimeError ছোড়ে
    (Python 3.11+)। তখন নতুন loop বানিয়ে গ্লোবালি সেট করি।"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@unittest.skipUnless(_MCP_AVAILABLE, _MCP_SKIP_REASON)
class McpServerBuildsTests(unittest.TestCase):
    """main.py-কে টেম্প workdir-এ কপি করে লোড করা হয় (আসল bot_data.db নষ্ট না করে)।"""

    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.mkdtemp(prefix="rohan-mcp-build-")
        shutil.copyfile(
            os.path.join(REPO_ROOT, "main.py"), os.path.join(cls.workdir, "main.py")
        )
        cls.old_cwd = os.getcwd()
        os.chdir(cls.workdir)

        os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
        os.environ.setdefault("ADMIN_IDS", "111")
        os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")
        # PUBLIC_URL না থাকলে _build_mcp_server() transport_security=None পাঠায়;
        # টেস্টের ভেতরে প্রয়োজনমতো সেট করা হবে (restore সহ)।
        cls._saved_public_url = os.environ.pop("PUBLIC_URL", None)

        logging.disable(logging.CRITICAL)

        # REPO_ROOT sys.path-এ আছে — তাই কপি করা main.py bangla_rule_engine
        # ইত্যাদি সহ-মডিউল ইমপোর্ট করতে পারে।
        module_name = "rohan_mcp_build_test_main"
        spec = importlib.util.spec_from_file_location(
            module_name, os.path.join(cls.workdir, "main.py")
        )
        cls.main = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = cls.main
        assert spec.loader is not None
        spec.loader.exec_module(cls.main)
        cls.main.init_db()

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)
        if cls._saved_public_url is not None:
            os.environ["PUBLIC_URL"] = cls._saved_public_url
        else:
            os.environ.pop("PUBLIC_URL", None)
        os.chdir(cls.old_cwd)
        sys.modules.pop("rohan_mcp_build_test_main", None)
        shutil.rmtree(cls.workdir, ignore_errors=True)

    # ------------------------------------------------------------------
    # হেল্পার
    # ------------------------------------------------------------------
    @staticmethod
    def _tool_names(server) -> set:
        """রেজিস্টার্ড টুলের নাম — mcp 1.x/2.x আর standalone fastmcp দুটোতেই কাজ করে।"""
        try:
            names = {getattr(t, "name", None) for t in run(server.list_tools())}
            names.discard(None)
            if names:
                return names
        except Exception:  # noqa: BLE001 — ফলব্যাক পথ নিচে
            pass
        tool_manager = getattr(server, "_tool_manager", None)
        tools = getattr(tool_manager, "_tools", None) or {}
        return set(tools.keys())

    def _version_note(self) -> str:
        return (
            f"fastmcp=={_dist_version('fastmcp')}, mcp=={_dist_version('mcp')}, "
            f"FastMCP রিজলভ হয়েছে: {_FASTMCP_IMPORT_PATH}"
        )

    def _build_server(self):
        """_build_mcp_server(app=None) কল করে; ব্যর্থ হলে installed-ভার্সনসহ
        ডায়াগনস্টিক মেসেজ দিয়ে fail করে (v3+/v4-এ ঠিক কী ভেঙেছে বোঝা যায়)।"""
        try:
            return self.main._build_mcp_server(app=None)
        except Exception as exc:  # noqa: BLE001
            self.fail(
                "_build_mcp_server(app=None) ব্যর্থ — "
                f"{type(exc).__name__}: {exc} [{self._version_note()}]"
            )
            raise AssertionError("unreachable")  # self.fail() কখনো রিটার্ন করে না

    # ------------------------------------------------------------------
    # 1. মূল স্মোক — _build_mcp_server(app=None) কোনো এক্সেপশন ছাড়াই চলে
    # ------------------------------------------------------------------
    def test_build_mcp_server_returns_fastmcp_object(self):
        server = self._build_server()

        self.assertIsNotNone(server, f"_build_mcp_server() None রিটার্ন করেছে [{self._version_note()}]")
        self.assertEqual(
            str(getattr(server, "name", "")),
            "rohan-youtube-bot-brain",
            f"সার্ভারের নাম মেলেনি [{self._version_note()}]",
        )
        # run_bot_async() এই মেথডটাই কল করে Mount-এর জন্য ASGI অ্যাপ বানাতে।
        self.assertTrue(
            callable(getattr(server, "streamable_http_app", None)),
            f"সার্ভারে streamable_http_app() নেই [{self._version_note()}]",
        )

    # ------------------------------------------------------------------
    # 2. কনস্ট্রাক্টর kwarg গুলো আসলেই গ্রহণযোগ্য (v3+/v4-এ এখানেই ফেল করবে)
    # ------------------------------------------------------------------
    def test_fastmcp_ctor_accepts_v2_style_kwargs(self):
        params = inspect.signature(_FASTMCP_CLASS.__init__).parameters
        missing = [name for name in REQUIRED_CTOR_KWARGS if name not in params]
        self.assertFalse(
            missing,
            f"{_FASTMCP_IMPORT_PATH}.FastMCP.__init__() এই kwarg গুলো নেয় না: {missing}. "
            "requirements.txt-এ fastmcp>=2.0,<3 পিন করা আছে কি না দেখুন "
            f"[{self._version_note()}]",
        )

    # ------------------------------------------------------------------
    # 3. simulate_message টুল রেজিস্টার্ড (PR #22)
    # ------------------------------------------------------------------
    def test_simulate_message_tool_is_registered(self):
        server = self._build_server()
        names = self._tool_names(server)
        self.assertIn(
            "simulate_message",
            names,
            f"simulate_message টুল পাওয়া যায়নি; পাওয়া গেছে: {sorted(names)} "
            f"[{self._version_note()}]",
        )
        # অন্য টুলগুলোও অক্ষত (টুল-রেজিস্ট্রেশন কোনোভাবে কমে যায়নি)
        for expected in ("add_knowledge", "add_pattern", "add_template"):
            self.assertIn(expected, names, f"{expected} টুল হারিয়ে গেছে [{self._version_note()}]")

    # ------------------------------------------------------------------
    # 4. কনস্ট্রাক্টরের মানগুলো সত্যিই ধরা হয়েছে (double-path-mount ফিক্স অক্ষত)
    # ------------------------------------------------------------------
    def test_server_settings_match_constructor_values(self):
        server = self._build_server()
        settings = getattr(server, "settings", None)
        self.assertIsNotNone(settings, f"সার্ভারে .settings নেই [{self._version_note()}]")
        self.assertTrue(
            getattr(settings, "stateless_http", False),
            f"stateless_http=True ধরা হয়নি [{self._version_note()}]",
        )
        self.assertTrue(
            getattr(settings, "json_response", False),
            f"json_response=True ধরা হয়নি [{self._version_note()}]",
        )
        # streamable_http_path="/" — Mount("/mcp")-এর সাথে ডবল-পাথ 404 আটকায়।
        self.assertEqual(
            str(getattr(settings, "streamable_http_path", "")),
            "/",
            f"streamable_http_path '/' নয় [{self._version_note()}]",
        )

    # ------------------------------------------------------------------
    # 5. PUBLIC_URL সেট থাকলে (Render) TransportSecuritySettings পথটাও ঠিক
    # ------------------------------------------------------------------
    def test_build_with_public_url_builds_transport_security(self):
        os.environ["PUBLIC_URL"] = "https://rohan-bot-eod2.onrender.com"
        try:
            server = self._build_server()
            self.assertIn("simulate_message", self._tool_names(server))
        finally:
            os.environ.pop("PUBLIC_URL", None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
