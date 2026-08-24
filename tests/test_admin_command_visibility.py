"""Admin-only coding command-এর দৃশ্যমানতা যাচাই — আসল main.py কোড চালিয়ে।

এই টেস্টটা main.py-কে সত্যিই import করে (DB অস্থায়ী ডিরেক্টরিতে তৈরি হয়, রিপোতে
bot_data.db তৈরি হয় না) এবং নিচের দাবিগুলো আসল ফাংশন কল করে যাচাই করে:

  1. /start সাধারণ ইউজারকে **একটাই** মেসেজ পাঠায় (দুইটা না)।
  2. সেই একটা মেসেজে **সব public coding command** থাকে।
  3. সেই মেসেজে **কোনো admin-only coding command** থাকে না (অ্যাডমিনের জন্যও না)।
  4. /help, /codehelp ও /menu-তেও admin-only command থাকে না।
  5. /adminpanel-এ "💻 Admin Coding কমান্ড" বাটন থাকে এবং সেটাতে admin-only
     command-গুলোর তালিকা দেখা যায়।
  6. সাধারণ ইউজার admin-only command টাইপ করলে সেটা বাতিল হয় (is_admin গেট)।
  7. /start-এর মেসেজ Telegram-এর দৈর্ঘ্য সীমার (TELEGRAM_MAX_MSG_LEN) ভিতরে থাকে,
     তাই একটাই মেসেজে পাঠানো সম্ভব।

চালানোর নিয়ম:
    python3 -m venv venv && venv/bin/pip install -r requirements.txt
    TELEGRAM_BOT_TOKEN=dummy:token ADMIN_IDS=111 GROQ_API_KEY=dummy \
        venv/bin/python tests/test_admin_command_visibility.py
"""

from __future__ import annotations

import asyncio
import os
import shutil
import sys
import tempfile

ADMIN_ID = 111          # ADMIN_IDS env-এ এই আইডি থাকবে (owner)
USER_ID = 999001        # সাধারণ ইউজার (কোনো অ্যাডমিন রোল নেই)

FAILED: list[str] = []
PASSED: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    (PASSED if condition else FAILED).append(f"{label}{f' — {detail}' if detail else ''}")


# ---------------------------------------------------------------------------
# main.py-কে অস্থায়ী ডিরেক্টরিতে কপি করে import করা, যাতে রিপোতে bot_data.db
# বা logs/ তৈরি না হয়।
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKDIR = tempfile.mkdtemp(prefix="rohan-bot-test-")
shutil.copyfile(os.path.join(REPO_ROOT, "main.py"), os.path.join(WORKDIR, "main.py"))
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
os.environ.setdefault("ADMIN_IDS", str(ADMIN_ID))
os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

import main  # noqa: E402  (উপরের env/path সেটআপের পরেই import করতে হবে)

main.init_db()


# ---------------------------------------------------------------------------
# হালকা ফেক Telegram অবজেক্ট — শুধু যতটুকু handler-গুলোর দরকার।
# ---------------------------------------------------------------------------
class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id
        self.first_name = "Test"
        self.username = "test_user"


class FakeMessage:
    def __init__(self, user_id: int):
        self.from_user = FakeUser(user_id)
        self.reply_to_message = None
        self.document = None
        self.text = ""
        self.sent: list[str] = []

    async def reply_text(self, text: str, **_kwargs):
        self.sent.append(text)
        return self


class FakeQuery:
    def __init__(self, user_id: int, data: str):
        self.from_user = FakeUser(user_id)
        self.data = data
        self.answered = False
        self.edited: list[str] = []

    async def answer(self, *args, **kwargs):
        self.answered = True

    async def edit_message_text(self, text: str, **_kwargs):
        self.edited.append(text)


class FakeUpdate:
    def __init__(self, user_id: int, callback_data: str | None = None):
        self.effective_user = FakeUser(user_id)
        self.message = FakeMessage(user_id)
        self.effective_message = self.message
        self.callback_query = FakeQuery(user_id, callback_data) if callback_data else None


class FakeBot:
    username = "test_bot"

    async def send_message(self, *args, **kwargs):
        return None


class FakeContext:
    def __init__(self):
        self.bot = FakeBot()
        self.args: list[str] = []
        self.user_data: dict = {}
        self.bot_data: dict = {}


def run(coro):
    """প্রতিটা কল আলাদা event loop-এ চালাই — python-telegram-bot handler-গুলো async।"""
    return asyncio.run(coro)


admin_commands = [
    usage.split()[0]
    for _, admin_only, commands in main.CODING_COMMAND_GROUPS
    if admin_only
    for usage, _desc in commands
]
public_commands = [
    usage.split()[0]
    for _, admin_only, commands in main.CODING_COMMAND_GROUPS
    if not admin_only
    for usage, _desc in commands
]

# ---------------------------------------------------------------------------
# 1–3. /start — এক মেসেজ, সব public coding command, কোনো admin-only command নয়
# ---------------------------------------------------------------------------
for actor, label in ((USER_ID, "সাধারণ ইউজার"), (ADMIN_ID, "অ্যাডমিন")):
    update = FakeUpdate(actor)
    run(main.start_command(update, FakeContext()))
    sent = update.message.sent
    check(f"/start ({label}) ঠিক একটাই মেসেজ পাঠায়", len(sent) == 1, f"পাঠিয়েছে {len(sent)}টা")
    if sent:
        body = sent[0]
        missing_public = [c for c in public_commands if c not in body]
        leaked_admin = [c for c in admin_commands if c in body]
        check(f"/start ({label}) সব public coding command দেখায়", not missing_public, f"নেই: {missing_public}")
        check(f"/start ({label}) কোনো admin-only command দেখায় না", not leaked_admin, f"ফাঁস: {leaked_admin}")
        check(
            f"/start ({label}) এক মেসেজের দৈর্ঘ্য সীমার ভিতরে",
            len(body) <= main.TELEGRAM_MAX_MSG_LEN,
            f"{len(body)} > {main.TELEGRAM_MAX_MSG_LEN}",
        )

# ---------------------------------------------------------------------------
# 4. /help, /codehelp, /menu — কোনোটাতেই admin-only command ফাঁস হবে না
# ---------------------------------------------------------------------------
update = FakeUpdate(USER_ID)
run(main.help_command(update, FakeContext()))
check("/help-এ admin-only command নেই", not [c for c in admin_commands if c in "".join(update.message.sent)])

update = FakeUpdate(USER_ID)
run(main.codehelp_command(update, FakeContext()))
codehelp_body = "".join(update.message.sent)
check("/codehelp-এ admin-only command নেই", not [c for c in admin_commands if c in codehelp_body])
check("/codehelp-এ public coding command আছে", all(c in codehelp_body for c in public_commands))

update = FakeUpdate(USER_ID)
run(main.menu_command(update, FakeContext()))
menu_sections = "\n".join(body for _title, body in main.MENU_SECTIONS.values())
check("/menu সেকশনে admin-only command নেই", not [c for c in admin_commands if c in menu_sections])
check("/menu সেকশনে public coding command আছে", all(c in menu_sections for c in public_commands))

# ---------------------------------------------------------------------------
# 5. /adminpanel — admin-only command-এর তালিকা এখানেই থাকবে
# ---------------------------------------------------------------------------
panel_text, panel_markup = main.build_admin_panel_view(ADMIN_ID)
callbacks = [b.callback_data for row in panel_markup.inline_keyboard for b in row]
check(
    "/adminpanel-এ Admin Coding কমান্ড বাটন আছে",
    "adm_codecommands" in callbacks,
    f"বাটন: {callbacks}",
)

admin_list = main.build_admin_coding_commands_text()
# তালিকার প্রতিটা কমান্ড-লাইন "/cmd ... — বিবরণ" ফরম্যাটে থাকে, তাই শুধু সেই লাইনগুলোই
# দেখা হয় — হেডারের সাধারণ কথা (যেমন "/start-এ দেখানো হয় না") এতে ধরা পড়ে না।
listed_in_admin_panel = {
    line.split()[0]
    for line in admin_list.splitlines()
    if line.startswith("/") and " — " in line
}
check("Admin তালিকায় সব admin-only command আছে", all(c in admin_list for c in admin_commands))
check(
    "Admin তালিকায় public coding command ঢোকে না",
    not (listed_in_admin_panel & set(public_commands)),
    f"ঢুকেছে: {sorted(listed_in_admin_panel & set(public_commands))}",
)
check(
    "Admin তালিকায় যে কমান্ডগুলো আছে সবগুলোই admin-only",
    listed_in_admin_panel == set(admin_commands),
    f"পার্থক্য: {sorted(listed_in_admin_panel ^ set(admin_commands))}",
)

update = FakeUpdate(ADMIN_ID, "adm_codecommands")
run(main.button_callback(update, FakeContext()))
edited = update.callback_query.edited
check("Admin বাটনে চাপলে তালিকা দেখায়", bool(edited) and all(c in edited[0] for c in admin_commands))

update = FakeUpdate(USER_ID, "adm_codecommands")
run(main.button_callback(update, FakeContext()))
user_edited = "".join(update.callback_query.edited)
check(
    "সাধারণ ইউজার ওই বাটন চাপলে admin তালিকা পায় না",
    not [c for c in admin_commands if c in user_edited],
    f"পেয়েছে: {user_edited[:80]}",
)

update = FakeUpdate(USER_ID)
run(main.adminpanel_command(update, FakeContext()))
check(
    "সাধারণ ইউজার /adminpanel খুলতে পারে না",
    all(c not in "".join(update.message.sent) for c in admin_commands),
)

# ---------------------------------------------------------------------------
# 6. সাধারণ ইউজার admin-only command চালাতে পারে না
# ---------------------------------------------------------------------------
gated_handlers = [
    ("codebasescan_command", main.codebasescan_command),
    ("codebasestatus_command", main.codebasestatus_command),
    ("securityscan_command", main.securityscan_command),
    ("autonomous_test_report_command", main.autonomous_test_report_command),
    ("codeauto_command", main.codeauto_command),
    ("phase30_execute_command_command", main.phase30_execute_command_command),
    ("phase28_impact_command", main.phase28_impact_command),
]
for name, handler in gated_handlers:
    update = FakeUpdate(USER_ID)
    ctx = FakeContext()
    ctx.args = ["1"]
    run(handler(update, ctx))
    reply = "".join(update.message.sent)
    blocked = ("অ্যাডমিন" in reply) or ("Admin only" in reply)
    check(f"সাধারণ ইউজারের জন্য {name} বন্ধ", blocked, reply[:60].replace("\n", " "))

# ---------------------------------------------------------------------------
print("\n".join(f"✅ {p}" for p in PASSED))
if FAILED:
    print("\n".join(f"❌ {f}" for f in FAILED))
print(f"\nমোট: {len(PASSED)} passed, {len(FAILED)} failed")

shutil.rmtree(WORKDIR, ignore_errors=True)
sys.exit(1 if FAILED else 0)
