"""telegram_webhook ক্র্যাশ-ফিক্সের টেস্ট — আসল main.py কোড চালিয়ে।

বাগ (Render লগ): `POST /webhook/<secret>`-এ `{}`-এর মতো `update_id`-বিহীন
পেলোড এলে `Update.de_json()` থেকে `TypeError` ছুঁড়ে রিকোয়েস্ট 500 দিয়ে
ক্র্যাশ করত। ফিক্স: `main.make_telegram_webhook()`-এর হ্যান্ডলার এখন
অসম্পূর্ণ পেলোডে `ok` ফেরত দেয় আর প্রসেসিং এরর লগে রেখে `ok`-ই দেয়।

এই টেস্টটা main.py-কে সত্যিই import করে (DB অস্থায়ী ডিরেক্টরিতে তৈরি হয়,
রিপোতে bot_data.db তৈরি হয় না), আসল হ্যান্ডলারটাকে Starlette `TestClient`
দিয়ে চালিয়ে নিচের দাবিগুলো যাচাই করে:

  1. `{}` POST করলে 200/"ok" আসে, কোনো এক্সেপশন ওঠে না,
     `process_update` ডাকাই হয় না।
  2. `update_id` ছাড়া র‍্যান্ডম dict (এমনকি non-dict JSON) দিলেও একই —
     200/"ok", ক্র্যাশ নেই।
  3. বৈধ ন্যূনতম টেলিগ্রাম আপডেট দিলে `app.process_update` ঠিক একবার ডাকা
     হয় (সঠিক `update_id` সহ) এবং 200 ফেরত আসে।
  4. অবৈধ JSON (garbage bytes) দিলে আগের মতোই 400/"bad request" আসে
     (regression — এই আচরণ বদলানো হয়নি)।
  5. `process_update` ভেতরে এক্সেপশন হলেও হ্যান্ডলার 500 দেয় না — এররটা
     লগে রেখে 200/"ok" ফেরত দেয় (টেলিগ্রাম রিট্রাই-লুপে পড়ে না)।

চালানোর নিয়ম:
    python3 -m venv venv && venv/bin/pip install -r requirements.txt
    TELEGRAM_BOT_TOKEN=dummy:token ADMIN_IDS=111 GROQ_API_KEY=dummy \\
        venv/bin/python tests/test_webhook_crash_fix.py
"""

from __future__ import annotations

import os
import importlib.util
import shutil
import sys
import tempfile

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
OLD_CWD = os.getcwd()
os.chdir(WORKDIR)

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:dummy-token")
os.environ.setdefault("ADMIN_IDS", "111")
os.environ.setdefault("GROQ_API_KEY", "gsk_dummy_key_for_tests")

# Do not reuse another test's cached main module and deleted temporary DB.
spec = importlib.util.spec_from_file_location("webhook_test_main", os.path.join(WORKDIR, "main.py"))
main = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = main
spec.loader.exec_module(main)

from starlette.applications import Starlette  # noqa: E402
from starlette.routing import Route  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402
from telegram import Update  # noqa: E402

main.init_db()

WEBHOOK_PATH = "/webhook/test-secret"


# ---------------------------------------------------------------------------
# Fake Application — আসল python-telegram-bot Application-এর বদলে; শুধু
# হ্যান্ডলার যা যা ব্যবহার করে (`.bot`, `.process_update()`) তাই আছে।
# ---------------------------------------------------------------------------
class FakeBot:
    """Update.de_json(data, bot) শুধু bot রেফারেন্সটা ধরে রাখে — ডি-সিরিয়ালাইজ
    করতে কোনো নেটওয়ার্ক মেথড ডাকে না, তাই খালি stub-ই যথেষ্ট।"""


class FakeApp:
    def __init__(self) -> None:
        self.bot = FakeBot()
        self.processed: list = []

    async def process_update(self, update) -> None:
        self.processed.append(update)


class ExplodingApp(FakeApp):
    """process_update সবসময় ব্যর্থ হয় — ৫ নম্বর টেস্টের জন্য।"""

    async def process_update(self, update) -> None:
        raise RuntimeError("simulated handler boom")


def make_client(app) -> TestClient:
    web = Starlette(
        routes=[Route(WEBHOOK_PATH, main.make_telegram_webhook(app), methods=["POST"])]
    )
    # raise_server_exceptions=True (ডিফল্ট): হ্যান্ডলারে ধরা-না-পড়া এক্সেপশন
    # হলে TestClient সেটা এখানেই ছুঁড়বে — "ক্র্যাশ নেই" দাবিটা সরাসরি প্রমাণ হয়।
    return TestClient(web, raise_server_exceptions=True)


VALID_UPDATE = {
    "update_id": 4242,
    "message": {
        "message_id": 7,
        "date": 1700000000,
        "chat": {"id": 111, "type": "private"},
        "from": {"id": 111, "is_bot": False, "first_name": "Test"},
        "text": "hi",
    },
}


# ---------------------------------------------------------------------------
# 1. খালি dict {} — আসল ক্র্যাশ-কেস (আগে TypeError -> 500 হতো)
# ---------------------------------------------------------------------------
fake = FakeApp()
client = make_client(fake)
try:
    resp = client.post(WEBHOOK_PATH, json={})
    check("খালি dict {} POST-এ এক্সেপশন ওঠে না", True)
    check("খালি dict {} POST-এ 200 আসে", resp.status_code == 200, f"status={resp.status_code}")
    check("খালি dict {} POST-এ 'ok' ফেরত আসে", resp.text == "ok", f"body={resp.text!r}")
except Exception as e:  # noqa: BLE001
    check("খালি dict {} POST-এ এক্সেপশন ওঠে না", False, f"{type(e).__name__}: {e}")
check("খালি dict {} POST-এ process_update ডাকা হয় না", fake.processed == [])

# ---------------------------------------------------------------------------
# 2. update_id-বিহীন র‍্যান্ডম dict / non-dict JSON
# ---------------------------------------------------------------------------
for label, payload in [
    ("র‍্যান্ডম dict", {"foo": "bar", "health": "check", "nested": {"a": [1, 2]}}),
    ("non-dict JSON (list)", [1, 2, 3]),
    ("non-dict JSON (string)", "ping"),
]:
    fake2 = FakeApp()
    client2 = make_client(fake2)
    try:
        resp = client2.post(WEBHOOK_PATH, json=payload)
        ok = resp.status_code == 200 and resp.text == "ok"
        check(f"{label} POST-এ 200/'ok', ক্র্যাশ নেই", ok,
              f"status={resp.status_code} body={resp.text!r}")
    except Exception as e:  # noqa: BLE001
        check(f"{label} POST-এ 200/'ok', ক্র্যাশ নেই", False, f"{type(e).__name__}: {e}")
    check(f"{label} POST-এ process_update ডাকা হয় না", fake2.processed == [])

# ---------------------------------------------------------------------------
# 3. বৈধ ন্যূনতম টেলিগ্রাম আপডেট — process_update ঠিক একবার ডাকা হয়
# ---------------------------------------------------------------------------
fake3 = FakeApp()
client3 = make_client(fake3)
try:
    resp = client3.post(WEBHOOK_PATH, json=VALID_UPDATE)
    check("বৈধ আপডেটে 200 আসে", resp.status_code == 200, f"status={resp.status_code}")
    check("বৈধ আপডেটে 'ok' ফেরত আসে", resp.text == "ok", f"body={resp.text!r}")
except Exception as e:  # noqa: BLE001
    check("বৈধ আপডেটে এক্সেপশন ওঠে না", False, f"{type(e).__name__}: {e}")
check("বৈধ আপডেটে process_update ঠিক একবার ডাকা হয়", len(fake3.processed) == 1,
      f"calls={len(fake3.processed)}")
if len(fake3.processed) == 1:
    got = fake3.processed[0]
    check("process_update আসল telegram.Update পায়", isinstance(got, Update),
          f"type={type(got).__name__}")
    check("process_update সঠিক update_id পায়",
          isinstance(got, Update) and got.update_id == VALID_UPDATE["update_id"],
          f"update_id={getattr(got, 'update_id', None)!r}")
    check("process_update-এর মেসেজ টেক্সট অক্ষত থাকে",
          isinstance(got, Update) and got.message is not None and got.message.text == "hi",
          f"text={getattr(getattr(got, 'message', None), 'text', None)!r}")

# ---------------------------------------------------------------------------
# 4. অবৈধ JSON — regression: আগের মতোই 400 "bad request"
# ---------------------------------------------------------------------------
fake4 = FakeApp()
client4 = make_client(fake4)
resp = client4.post(
    WEBHOOK_PATH,
    content=b"\xff\xfe this is not json {{{",
    headers={"Content-Type": "application/json"},
)
check("অবৈধ JSON-এ 400 আসে", resp.status_code == 400, f"status={resp.status_code}")
check("অবৈধ JSON-এ 'bad request' ফেরত আসে", resp.text == "bad request",
      f"body={resp.text!r}")
check("অবৈধ JSON-এ process_update ডাকা হয় না", fake4.processed == [])

# ---------------------------------------------------------------------------
# 5. process_update ভেতরে ফেটে গেলেও 200/"ok" (রিট্রাই-লুপ এড়াতে)
# ---------------------------------------------------------------------------
boom = ExplodingApp()
client5 = make_client(boom)
try:
    resp = client5.post(WEBHOOK_PATH, json=VALID_UPDATE)
    check("process_update ফেল করলেও 200 আসে", resp.status_code == 200,
          f"status={resp.status_code}")
    check("process_update ফেল করলেও 'ok' ফেরত আসে", resp.text == "ok",
          f"body={resp.text!r}")
except Exception as e:  # noqa: BLE001
    check("process_update ফেল করলেও এক্সেপশন বাইরে আসে না", False,
          f"{type(e).__name__}: {e}")

# ---------------------------------------------------------------------------
print("\n".join(f"✅ {p}" for p in PASSED))
if FAILED:
    print("\n".join(f"❌ {f}" for f in FAILED))
print(f"\nমোট: {len(PASSED)} passed, {len(FAILED)} failed")

os.chdir(OLD_CWD)
sys.modules.pop(spec.name, None)
shutil.rmtree(WORKDIR, ignore_errors=True)
if __name__ == "__main__":
    sys.exit(1 if FAILED else 0)
assert not FAILED, "\n".join(FAILED)
