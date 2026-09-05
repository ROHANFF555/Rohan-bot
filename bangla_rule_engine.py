"""bangla_rule_engine — নিয়ম-ভিত্তিক (deterministic) বাংলা→Python কোড ট্রান্সলেটর।

কোনো AI/LLM কল ছাড়াই ব্যবহারকারীর **কড়া, নির্দিষ্ট ফরম্যাটের** বাংলা নির্দেশনাকে
ধাপে ধাপে চালানোর-যোগ্য Python প্রোগ্রামে অনুবাদ করে। main.py-এর
match_dynamic_print_task()/_match_dynamic_print_request() জুটির *পরিপূরক* —
ইঞ্জিনের ভেতরের গার্ড dynamic-print-আকৃতির ("রান করলে X লেখা আসবে") বা কোটেশন-
যুক্ত রিকোয়েস্ট আগেই বাদ দিয়ে দেয়, তাই সেগুলো আগের মতোই পুরনো matcher-এ যায়
(matcher চেইনে এই ইঞ্জিন dynamic-print-এর আগে বসলেও)।

v1 রুলস (প্রতিটা রুল = ট্রিগার-প্যাটার্ন + কোড-টেমপ্লেট):
  1. ভেরিয়েবল/স্টোরেজ রুল — "X এবং Y থাকবে" / "X সংরক্ষণ করবে";
     বাক্যে "ডাটাবেজ" শব্দ থাকলে dict, নইলে saved_ স্ক্যালার ভ্যারিয়েবল
  2. ইনপুট রুল — "আমি (যদি) X ইনপুট দিলে/দেই" / "X চাইবে" / "X ইনপুট নেবে" → input()
  3. শর্ত রুল (if) — "যদি X <মান> হলে/মিললে (তাহলে) Y" / "X এবং Y মিললে" → if ব্লক
  4. নিষেধ/negation রুল (প্রি-প্রসেসিং ধাপ) — ক্রিয়ার পরে "না" ("দেখাবে না",
     "বানিও না", "চাইবেনা") থাকলে ওই ট্রিগারটা নিষেধ গণ্য — ওই অংশের কোড
     generate হয় না (বা শর্ত হলে বিপরীত অপারেটর != বসে)। "না মিললে/না হলে"
     আবার else-শাখার নির্দেশ হিসেবে ধরা হয়।
  5. আউটপুট রুল (print) — "X দেখাবে/লিখবে/প্রিন্ট করবে" → print(); একা
     আউটপুট-ট্রিগার তখনই যথেষ্ট যখন কনসোল-প্রসঙ্গ ("কনসোলে ... লিখবে") বা
     প্রোগ্রাম-সাবজেক্ট + "প্রিন্ট করবে" আছে — নইলে structured রুল লাগে।
  6. তুলনা রুল — "মিললে"/"সমান হলে" → == (নিষেধ হলে !=) তুলনা

স্কোপে নেই (পরের ধাপ): loop (for/while), একাধিক ফাংশন/ক্লাস, try/except,
মুক্ত/স্বাভাবিক বাংলা — এটা শুধু কড়া, নির্দিষ্ট ফরম্যাটের ইনপুটের জন্য।

কোনো রুল-সেটই পূর্ণ প্রোগ্রাম দাঁড়াতে না পারলে (বা জেনারেট হওয়া কোড
ast.parse-এ বৈধ না হলে) None রিটার্ন হয় — কলার তখন পুরনো ফ্লো
(dynamic-print matcher → Decision Engine → AI) এ ফলব্যাক করে; কখনো raise হয় না।

চালানো/টেস্ট:
    python3 tests/test_bangla_rule_engine.py
    python3 -m unittest tests.test_bangla_rule_engine -v
"""

from __future__ import annotations

import ast
import json
import keyword
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

ENGINE_LABEL = "bangla_rule_engine"

MAX_INPUT_CHARS = 600        # এর চেয়ে দীর্ঘ রিকোয়েস্ট কড়া-ফরম্যাটের নয় → অমিল
MAX_ITEMS = 8                # ইনপুট/ফিল্ড/আউটপুট-এর সর্বোচ্চ সংখ্যা
DEFAULT_FAILURE_MESSAGE = "ব্যর্থ হয়েছে"
DEFAULT_UNKNOWN_VALUE = "admin"

_BN_DIGIT_TABLE = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


# ---------------------------------------------------------------------------
# ইউনিকোড ক্যাননিকালাইজেশন — য়-এর দুই রূপ (U+09DF vs য+়) এবং বাংলা সংখ্যা এক করা,
# নইলে একই শব্দের দুই বানান-রূপ আলাদা টোকেন হয়ে যায়। সব প্যাটার্নও একই রূপে কম্পাইল।
# ---------------------------------------------------------------------------

def _canon(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    return s.replace("\u09df", "\u09af\u09bc")


def _rx(pattern: str) -> "re.Pattern[str]":
    return re.compile(_canon(pattern))


# ---------------------------------------------------------------------------
# শব্দ-ভাণ্ডার: চেনা বাংলা আইটি-শব্দ → python identifier + ডিফল্ট মান
# ---------------------------------------------------------------------------

_DATABASE_WORDS = ("ডাটাবেজ", "ডেটাবেস", "ডাটাবেস", "ডেটাবেজ", "database")

_PHRASE_MAP: Dict[str, str] = {
    _canon(p): ident
    for p, ident in {
        "ইউজার নেম": "username", "ইউজারনেম": "username", "ইউজার নাম": "username",
        "ইউজারনাম": "username", "ইউজার আইডি": "user_id", "ইউজার আইড": "user_id",
        "পাসওয়ার্ড": "password", "পাসওয়ার্দ": "password", "পাস ওয়ার্ড": "password",
        "নাম": "name", "নেম": "name", "আইডি": "id", "আইড": "id",
        "ইমেইল": "email", "ই-মেইল": "email", "মেইল": "email",
        "ফোন নম্বর": "phone", "মোবাইল নম্বর": "phone", "ফোন": "phone",
        "নম্বর": "number", "সংখ্যা": "number", "শহর": "city", "সিটি": "city",
        "দেশ": "country", "বয়স": "age", "এজ": "age", "রোল": "role",
        "কোড": "code", "পিন কোড": "pin", "টোকেন": "token",
    }.items()
}

_WORD_MAP: Dict[str, str] = {
    _canon(w): ident
    for w, ident in {
        "ইউজার": "user", "নেম": "name", "নাম": "name", "আইডি": "id", "আইড": "id",
        "পাসওয়ার্ড": "password", "পাসওয়ার্দ": "password", "ইমেইল": "email",
        "মেইল": "mail", "নম্বর": "number", "নাম্বার": "number", "সংখ্যা": "number",
        "ফোন": "phone",
        "শহর": "city", "সিটি": "city", "দেশ": "country", "বয়স": "age",
        "রোল": "role", "কোড": "code", "টোকেন": "token", "পিন": "pin",
    }.items()
}

_DEFAULT_VALUES: Dict[str, str] = {
    "username": "admin", "user_id": "admin", "user": "admin",
    "password": "admin123", "pass": "admin123",
    "name": "রহিম", "email": "admin@example.com", "mail": "admin@example.com",
    "id": "1", "phone": "01700000000", "number": "100", "age": "20",
    "city": "ঢাকা", "country": "বাংলাদেশ", "code": "1234", "role": "admin",
    "pin": "1234", "token": "secret-token",
}

# সীমানা-শব্দ: ফিল্ড-নাম বা প্রিন্ট-বার্তার অংশ হতে পারে না (সংযোজক, নির্দেশক,
# ট্রিগার-ক্রিয়া, কনসোল-শব্দ ...)। ক্যাপচার-জানালা থেকে শেষ থেকে এই শব্দে দাঁড়ালেই
# থেমে যায়।
_BOUNDARY_WORDS = {
    _canon(w) for w in (
        "তাহলে", "হলে", "যদি", "এবং", "ও", "আর", "কিন্তু", "না", "চাইবে", "চাইলে",
        "চাইবেন", "ইনপুট", "দেই", "দিলে", "দিয়ে", "দেও", "দেবে", "নেবে", "থাকবে",
        "হবে", "করবে", "করো", "করে", "সে", "সেই", "ওই", "এই", "ঐ", "একটি", "একটা",
        "একখানা", "কিছু", "দেখাবে", "দেখাক", "দেখাবেন", "লিখবে", "লিখবেন",
        "মিললে", "মিলে", "মিলবে", "সমান", "বানাতে", "বানাও", "বানাবে", "রাখবে",
        "সংরক্ষণ", "লাগবে", "হয়", "তোমাকে", "আমাকে", "আমার", "তোমার", "এখন",
        "প্রিন্ট", "কনসোল", "কনসোলে", "টার্মিনাল", "টার্মিনালে",
        "প্রোগ্রাম", "প্রোগ্রামটা", "প্রোগ্রামটি", "স্ক্রিপ্ট", "স্ক্রিপ্টটা",
        "স্ক্রিপ্টটি", "কোডটা", "সিস্টেম", "সিস্টেমে", "দিন", "লিখুন",
        # সর্বনাম — ফিল্ড-নামের অংশ নয় ("আমি নাম ইনপুট দিলে" → ফিল্ড "নাম")
        "আমি", "তুমি", "আপনি", "তারা", "ওরা", "নিজে",
        # ভাষার নাম — ফিল্ড-নাম নয় ("পাইথনে নাম এবং ..." → ফিল্ড "নাম")
        "পাইথন", "পাইথনে", "পাইথনন",
    )
}

# বিশেষণ/প্রেডিকেট — "যদি X সফল হলে"-তে literal নয়, X-এর অবস্থা; ওই জায়গায়
# literal-if ধরা হয় না (মিথ্যা positive ঠেকাতে)।
_PREDICATE_WORDS = {
    _canon(w) for w in (
        "সফল", "ব্যর্থ", "সফলভাবে", "ঠিক", "ভুল", "সঠিক", "অসঠিক", "শেষ",
        "সম্পূর্ণ", "খালি", "ভরা", "বড়", "ছোট", "বেশি", "কম", "পূর্ণ", "চালু",
        "বন্ধ", "আছে", "নেই", "সত্য", "মিথ্যা", "পাওয়া", "যাবে", "হবে",
    )
}

_IDENT_RE = re.compile(r"^[A-Za-z_\u0980-\u09ff][A-Za-z0-9_\u0980-\u09ff]*$")


def _is_boundary_word(word: str) -> bool:
    if not word or word in ("।", ","):
        return True
    if word in _BOUNDARY_WORDS:
        return True
    return any(word.startswith(db) for db in _DATABASE_WORDS)


# ---------------------------------------------------------------------------
# গার্ড — যেসব টেক্সট এই ইঞ্জিনের নয়, আগেই বাদ (dynamic-print/AI-এর ডোমেইন)
# ---------------------------------------------------------------------------

# dynamic-print-আকৃতির ট্রিগার — পুরনো matcher-ই এগুলোর জন্য দায়ী থাকে।
_DYNAMIC_PRINT_SHAPE_RE = _rx(
    r"রান\s*করলে|রান\s*করালে|চালালে|লেখা\s+আসবে|লেখা\s+দেখ|লেখা\s+উঠবে|"
    r"লেখা\s+প্রিন্ট|প্রিন্ট\s+হবে|প্রিন্ট\s+করা\s+হবে|দেখানো\s+হবে|"
    r"when\s+run|when\s+executed|\bprints?\b"
)
# কোটেশন — dynamic-print-এর quoted-শাখার ডোমেইন; কড়া ফরম্যাটে কোট লাগে না।
_QUOTE_RE = re.compile(r"[\"'`\u201c\u201d\u2018\u2019\u00ab\u00bb]")
# UI/ফ্রেমওয়ার্ক-বর্ণনা — কনসোল-প্রোগ্রামের নির্দেশনা নয় (dynamic-print-এর
# UI-গেটের মতোই conservative)।
_UI_FRAMEWORK_RE = _rx(
    r"স্ক্রিন|পেজ|পৃষ্ঠা|ফর্ম|উইজার্ড|ডায়ালগ|মোডাল|টোস্ট|বাটন|বোতাম|মেনু|"
    r"ওয়েব|ব্রাউজার|ড্যাশবোর্ড|ওয়েবসাইট|অ্যাপ|এপ্লিকেশ|"
    r"\bweb\b|\bhtml\b|\bcss\b|\breact\b|\bflask\b|\bdjango\b|\bapi\b|\bui\b|\bdashboard\b|\bfrontend\b"
)
# বাংলায় লেখা অন্য ভাষার নাম — v1 ইঞ্জিন শুধু Python জানে; ভুল সিনট্যাক্সে
# টাস্ক 'done' করার বদলে None (AI ফলব্যাক)।
_NON_PYTHON_LANG_RE = _rx(
    r"জাভাস্ক্রিপ্ট|জাভা\s*স্ক্রিপ্ট|জাভা|টাইপস্ক্রিপ্ট|পিএইচপি|নোড|কোটলিন|"
    r"সুইফট|গোল্যাং|সি\s*\+\+|সি\s*শার্প|"
    r"\bjavascript\b|\bjava\b|\bphp\b|\bnode\b|\bnodejs\b|\bkotlin\b|\bswift\b|"
    r"\bgolang\b|\bc\+\+\b|\bcsharp\b"
)


# ---------------------------------------------------------------------------
# রুল-ট্রিগার প্যাটার্ন (সবই ক্যাননিকালাইজড টেক্সটের উপর চলে)
# ---------------------------------------------------------------------------

# ১) স্টোরেজ রুল
_STORAGE_PAIR_RE = _rx(
    r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2})\s+(?:এবং|ও)\s+"
    r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2}?)\s+থাকবে"
)
_STORAGE_SINGLE_RE = _rx(r"([^\s।,.]+(?:\s+[^\s।,.]+){0,1}?)\s+থাকবে")
_STORAGE_SAVE_RE = _rx(r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2}?)\s+সংরক্ষণ\s+করবে")
_STORAGE_KEEP_RE = _rx(r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2}?)\s+রাখবে")

# ২) ইনপুট রুল
_INPUT_GIVE_RE = _rx(
    r"(?:আমি\s+)?(?:যদি\s+)?([^\s।,.]+(?:\s+[^\s।,.]+){0,2}?)\s+ইনপুট\s+"
    r"(?:দিলে|দেই|দিয়ে|দেও|দিলাম)"
)
_INPUT_ASK_RE = _rx(r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2})\s+চাইবে")
_INPUT_TAKE_RE = _rx(
    r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2}?)\s+ইনপুট\s+(?:নেবে|নিবে|চাইবে|দেবে)"
)

# ৩+৬) শর্ত/তুলনা রুল
_LITERAL_IF_RE = _rx(
    r"যদি\s+([^\s।,.]+(?:\s+[^\s।,.]+){1,2}?)\s+"
    r"(?:হলে|মিললে|সমান\s+হলে|মিলে\s+গেলে)"
)
_MATCH_RE = _rx(r"মিললে|মিলে\s+গেলে|সমান\s+হলে|এক\s+হলে|মিলবে")
_MATCH_FIELDS_RE = _rx(
    r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2})\s+(?:এবং|ও)\s+"
    r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2}?)\s+(?:মিললে|মিলে|সমান\s+হলে)"
)

# ৫) আউটপুট রুল — গ্রুপ ২ = ক্রিয়া (ক্রিয়ার অবস্থান দিয়ে else-মার্কার/নিষেধ বোঝা হয়,
# কারণ ক্যাপচার-জানালা পেছনের শব্দও গ্রাস করে — জানালার শুরু নয়, ক্রিয়াই আসল অ্যাঙ্কর)
_OUTPUT_RE = _rx(
    r"([^\s।,.]+(?:\s+[^\s।,.]+){0,2})\s+"
    r"(দেখাবে|দেখাক|লিখবে|প্রিন্ট\s+করবে|প্রিন্ট\s+করো|প্রিন্ট\s+করে)"
)

# ৪) নিষেধ/negation (প্রি-প্রসেসিং) — ক্রিয়ার পরে "না"
_NEGATION_ATTACHED_RE = _rx(
    r"(?:করবে|দেখাবে|চাইবে|হবে|থাকবে|মিলবে|লিখবে|নেবে|দেবে|বানাবে|করবেন|"
    r"দেখাবেন|চাইবেন|লিখবেন)না(?=[\s।,.]|$)"
)
_NEGATION_SPLIT_RE = _rx(r"([^\s।,.]+)\s+না(?=[\s।,.]|$)")
# "না মিললে/না হলে" → else-শাখার নির্দেশ (নিষেধ নয়)
_ELSE_COND_RE = _rx(r"না\s+(?:মিললে|মিলে|হলে|সমান\s+হলে|এক\s+হলে)(?=[\s।,.]|$)")

# আউটপুট-একা (print-only) ফ্যামিলির প্রসঙ্গ-গেট
_CONSOLE_RE = _rx(r"কনসোল|টার্মিনাল")
_PROGRAM_SUBJECT_RE = _rx(r"প্রোগ্রাম(?:টা|টি|টো)?|স্ক্রিপ্ট(?:টা|টি)?|কোড(?:টা|টি)?")
_PRINT_VERB_RE = _rx(r"প্রিন্ট\s+করবে|প্রিন্ট\s+করো|প্রিন্ট\s+করে")


# ---------------------------------------------------------------------------
# সাহায্যকারী
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    t = _canon(text or "")
    t = t.translate(_BN_DIGIT_TABLE)
    t = t.replace("।", " । ").replace(",", " , ")
    return " ".join(t.split())


def _clean_phrase(captured: str, max_len: int = 40) -> str:
    """ক্যাপচার-জানালার শেষ থেকে হাঁটে — সীমানা-শব্দে দাঁড়ালেই থামে।

    "ডাটাবেজে ইউজার আইডি" → "ইউজার আইডি", "তাহলে সে ইউজার নেম" → "ইউজার নেম"।
    খালি হলে ""।
    """
    words = [w for w in (captured or "").split() if w]
    kept: List[str] = []
    for w in reversed(words):
        if _is_boundary_word(w):
            break
        kept.append(w)
    kept.reverse()
    phrase = " ".join(kept)
    if not phrase or len(phrase) > max_len:
        return ""
    return phrase


def _tokens(phrase: str) -> set:
    return {w for w in (phrase or "").split() if w and not _is_boundary_word(w)}


def _token_overlap(a: str, b: str) -> bool:
    return bool(_tokens(a) & _tokens(b))


def _overlap_any(span: Tuple[int, int], spans: List[Tuple[int, int]]) -> bool:
    s0, s1 = span
    return any(not (s1 <= t0 or s0 >= t1) for t0, t1 in spans)


def _dq(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _looks_like_verb(word: str) -> bool:
    return word.endswith(("বে", "লে", "ো", "েন", "ই", "ি"))


def _to_identifier(phrase: str, registry: set) -> str:
    """বাংলা ফিল্ড-বাক্য → বৈধ python identifier (চেনা শব্দ ম্যাপ, নইলে বাংলাই)।"""
    p = (phrase or "").strip()
    base = ""
    if p in _PHRASE_MAP:
        base = _PHRASE_MAP[p]
    else:
        words = p.split()
        if words and all(w in _WORD_MAP for w in words):
            base = "_".join(_WORD_MAP[w] for w in words)
        elif words and all(_IDENT_RE.match(w) and not keyword.iskeyword(w) for w in words):
            base = "_".join(words)
    if not base or not base.isidentifier() or keyword.iskeyword(base):
        base = "value"
    ident, n = base, 2
    while ident in registry:
        ident = f"{base}_{n}"
        n += 1
    registry.add(ident)
    return ident


def _default_value(ident: str) -> str:
    return _DEFAULT_VALUES.get(ident, DEFAULT_UNKNOWN_VALUE)


# ---------------------------------------------------------------------------
# পার্সিং — টেক্সট → facts
# ---------------------------------------------------------------------------

def _find_negation_spans(t: str) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """নিষেধ-স্প্যান (ক্রিয়া + না) ও else-মার্কার-স্প্যান ("না মিললে") বের করে।

    else-মার্কার আগে বসে — "...সাকসেস দেখাবে না মিললে ফেইল দেখাবে"-এ "দেখাবে না"
    আসলে else-গঠন, নিষেধ নয়; তাই নিষেধ-হিসেবে গোনা হয় না।
    """
    else_spans: List[Tuple[int, int]] = [(m.start(), m.end()) for m in _ELSE_COND_RE.finditer(t)]
    neg_spans: List[Tuple[int, int]] = []
    for m in _NEGATION_ATTACHED_RE.finditer(t):
        span = (m.start(), m.end())
        if not _overlap_any(span, else_spans):
            neg_spans.append(span)
    for m in _NEGATION_SPLIT_RE.finditer(t):
        word = m.group(1)
        if not _looks_like_verb(word):
            continue
        span = (m.start(), m.end())
        if _overlap_any(span, else_spans):
            continue
        neg_spans.append(span)
    return neg_spans, else_spans


def _match_storage(t: str, neg_spans: List[Tuple[int, int]]) -> Tuple[bool, List[str]]:
    container = any(db in t for db in _DATABASE_WORDS)
    fields: List[str] = []
    seen = set()

    def _add(phrase: str, m: "re.Match[str]", group_end: int) -> None:
        # নিষেধ-চিহ্ন ক্রিয়ার গায়ে বসে ("থাকবে না") — ক্যাপচার-জানালা নয়, ক্রিয়া-অঞ্চল
        # (শেষ গ্রুপের পরের অংশ) দিয়েই মিলাতে হয়, নইলে অন্য রুলের নিষেধ এসে ভুলে
        # স্টোরেজ বাদ দেয় ("... দেখাবে না, পাসওয়ার্ড এবং ইমেইল থাকবে")।
        if _overlap_any((group_end, m.end()), neg_spans):
            return  # "নাম থাকবে না" — নিষেধ করা স্টোরেজ জেনারেট হয় না
        p = _clean_phrase(phrase)
        if p and p not in seen and not any(p.startswith(db) for db in _DATABASE_WORDS):
            seen.add(p)
            fields.append(p)

    for m in _STORAGE_PAIR_RE.finditer(t):
        _add(m.group(1), m, m.end(1))
        _add(m.group(2), m, m.end(2))
    for m in _STORAGE_SAVE_RE.finditer(t):
        _add(m.group(1), m, m.end(1))
    for m in _STORAGE_KEEP_RE.finditer(t):
        _add(m.group(1), m, m.end(1))
    for m in _STORAGE_SINGLE_RE.finditer(t):
        _add(m.group(1), m, m.end(1))
    if len(fields) > MAX_ITEMS:
        return container, []
    return container, fields


def _match_inputs(t: str, neg_spans: List[Tuple[int, int]]) -> List[dict]:
    found: List[dict] = []
    seen_triggers: List[Tuple[int, int]] = []

    def _add(m: "re.Match[str]") -> None:
        # ট্রিগার-ক্রিয়া অঞ্চল (ক্যাপচারের পরের অংশ) — দুই প্যাটার্ন একই ক্রিয়ায়
        # দাঁড়ালে ডুপ্লিকেট; পাশাপাশি আলাদা ট্রিগার ("... দিলে সে ... চাইবে") বাদ পড়ে না।
        trigger_start = m.start() + len(m.group(1))
        trigger = (trigger_start, m.end())
        if any(_overlap_any(trigger, [s]) for s in seen_triggers):
            return
        phrase = _clean_phrase(m.group(1))
        if not phrase:
            return
        seen_triggers.append(trigger)
        found.append({
            "phrase": phrase,
            "span": (m.start(), m.end()),
            "negated": _overlap_any(trigger, neg_spans),
        })

    for pattern in (_INPUT_GIVE_RE, _INPUT_TAKE_RE, _INPUT_ASK_RE):
        for m in pattern.finditer(t):
            _add(m)
    found.sort(key=lambda item: item["span"][0])
    # একই নাম দুইবার চাওয়া হলে প্রথমটাই থাকে
    deduped: List[dict] = []
    seen_phrases = set()
    for item in found:
        if item["phrase"] in seen_phrases:
            continue
        seen_phrases.add(item["phrase"])
        deduped.append(item)
    return deduped[:MAX_ITEMS]


def _match_condition(t: str, neg_spans: List[Tuple[int, int]]) -> Optional[dict]:
    cond: Optional[dict] = None
    m = _LITERAL_IF_RE.search(t)
    if m:
        words = m.group(1).split()
        var, value = "", ""
        # চেনা ফিল্ড-বাক্য দিয়ে সবচেয়ে লম্বা prefix-ই var (যেমন "ইউজার নাম")
        for n in range(len(words) - 1, 0, -1):
            prefix = " ".join(words[:n])
            if prefix in _PHRASE_MAP or all(w in _WORD_MAP for w in prefix.split()):
                var, value = prefix, " ".join(words[n:])
                break
        if not var:
            var, value = words[0], " ".join(words[1:])
        value = _clean_phrase(value, max_len=30)
        literal_ok = (
            value
            and all(not _is_boundary_word(w) for w in value.split())
            and not any(w in _PREDICATE_WORDS for w in value.split())
        )
        if literal_ok:
            cond = {
                "kind": "literal", "var": var, "value": value,
                "fields": [],
                # নিষেধ-চিহ্ন ক্রিয়া-অঞ্চলে (হলে/মিললে-এর ঘরে) খোঁজা হয় — ক্যাপচার-জানালায় নয়
                "negated": _overlap_any((m.end(1), m.end()), neg_spans),
                "span": (m.start(), m.end()),
            }
    if cond is None and _MATCH_RE.search(t):
        fields: List[str] = []
        fm = _MATCH_FIELDS_RE.search(t)
        if fm:
            x = _clean_phrase(fm.group(1))
            y = _clean_phrase(fm.group(2))
            if x and y and x != y:
                fields = [x, y]
        mm = _MATCH_RE.search(t)
        cond = {
            "kind": "match", "var": "", "value": "", "fields": fields,
            "negated": _overlap_any((mm.start(), mm.end()), neg_spans) if mm else False,
            "span": (mm.start(), mm.end()) if mm else (0, 0),
        }
    return cond


def _match_outputs(t: str, neg_spans: List[Tuple[int, int]],
                   else_spans: List[Tuple[int, int]]) -> List[dict]:
    outputs: List[dict] = []
    for m in _OUTPUT_RE.finditer(t):
        message = _clean_phrase(m.group(1), max_len=80)
        if not message:
            continue
        if any(ch in message for ch in "(){};<>`"):
            continue
        # ক্রিয়ার অবস্থানই আসল অ্যাঙ্কর — জানালা-ক্যাপচার পেছনের শব্দও নিতে পারে
        verb_span = (m.start(2), m.end(2))
        outputs.append({
            "message": message,
            "negated": _overlap_any(verb_span, neg_spans),
            # else-মার্কারের ("না মিললে") পরের ক্রিয়া = else-বার্তা
            "is_else": any(marker_end <= verb_span[0] for _, marker_end in else_spans),
        })
    return outputs[:MAX_ITEMS]


def _parse(text: str) -> Optional[dict]:
    t = _normalize(text)
    if not t or len(t) > MAX_INPUT_CHARS:
        return None
    if not re.search(r"[\u0980-\u09ff]", t):
        return None  # বাংলা অক্ষর নেই — এই ইঞ্জিনের নয়
    if _QUOTE_RE.search(t):
        return None  # কোটেশন — dynamic-print ম্যাচারের ডোমেইন
    if _DYNAMIC_PRINT_SHAPE_RE.search(t):
        return None  # "রান করলে ... লেখা আসবে" জাতীয় — পুরনো ম্যাচারের ডোমেইন
    if _UI_FRAMEWORK_RE.search(t):
        return None  # UI/ফিচার-বর্ণনা — কনসোল-প্রোগ্রামের নির্দেশনা নয়
    if _NON_PYTHON_LANG_RE.search(t):
        return None  # অন্য ভাষা চাওয়া হয়েছে — v1 শুধু Python

    neg_spans, else_spans = _find_negation_spans(t)
    container, storage_fields = _match_storage(t, neg_spans)
    inputs = _match_inputs(t, neg_spans)
    condition = _match_condition(t, neg_spans)
    outputs = _match_outputs(t, neg_spans, else_spans)
    if len(inputs) > MAX_ITEMS or len(outputs) > MAX_ITEMS:
        return None
    return {
        "container": container,
        "storage_fields": storage_fields,
        "inputs": inputs,
        "condition": condition,
        "outputs": outputs,
        "console": bool(_CONSOLE_RE.search(t)),
        "program_subject": bool(_PROGRAM_SUBJECT_RE.search(t)),
        "print_verb": bool(_PRINT_VERB_RE.search(t)),
    }


# ---------------------------------------------------------------------------
# কোড-অ্যাসেম্বলি — facts → চালানোর-যোগ্য Python
# ---------------------------------------------------------------------------

_HEADER = ("# বাংলা রুল ইঞ্জিন (bangla_rule_engine) — নিয়ম থেকে deterministic "
           "জেনারেট, কোনো AI কল হয়নি")


def _map_to_key(phrase: str, key_phrases: List[str]) -> Optional[str]:
    """ইনপুট-ফিল্ড → স্টোরেজ-ফিল্ড ম্যাপিং: সর্বোচ্চ টোকেন-ওভারল্যাপ (টাই হলে আগেরটা)।"""
    best, best_score = None, 0
    ptoks = _tokens(phrase)
    for key in key_phrases:
        score = len(ptoks & _tokens(key))
        if score > best_score:
            best, best_score = key, score
    return best  # type: ignore[return-value]


def _assemble_program(facts: dict, success_msgs: List[str], else_msg: Optional[str]) -> Optional[str]:
    cond = facts["condition"]
    if cond is None:
        return None

    # --- প্রোগ্রাম-ইনপুট: ইনপুট-রুলের ফিল্ড + শর্তের বাকি রেফারেন্স ---
    prog_inputs: List[str] = [i["phrase"] for i in facts["inputs"] if not i["negated"]]
    if cond["kind"] == "match":
        for fld in cond["fields"]:
            if not any(_token_overlap(fld, p) for p in prog_inputs):
                prog_inputs.append(fld)
    else:  # literal
        if not any(_token_overlap(cond["var"], p) or p == cond["var"] for p in prog_inputs):
            prog_inputs.append(cond["var"])
    if not prog_inputs:
        return None

    var_registry: set = set()
    input_idents = {p: _to_identifier(p, var_registry) for p in prog_inputs}

    lines: List[str] = [_HEADER, ""]

    # --- স্টোরেজ ডিক্লারেশন ---
    key_idents: Dict[str, str] = {}
    stored_idents: Dict[str, str] = {}
    if facts["container"]:
        key_phrases = facts["storage_fields"] or prog_inputs
        key_registry: set = set()
        key_idents = {p: _to_identifier(p, key_registry) for p in key_phrases}
        label = " এবং ".join(key_phrases)
        lines.append(f"# ডাটাবেজ: {label} (ডিফল্ট মান — দরকারমতো বদলে নিন)")
        lines.append("database = {")
        for p in key_phrases:
            ident = key_idents[p]
            lines.append(f'    "{ident}": {_dq(_default_value(ident))},')
        lines.append("}")
        lines.append("")
    elif facts["storage_fields"]:
        stored_registry: set = set()
        lines.append("# সংরক্ষিত মান (ডিফল্ট — দরকারমতো বদলে নিন)")
        for p in facts["storage_fields"]:
            ident = _to_identifier(p, stored_registry)
            stored_idents[p] = f"stored_{ident}"
            lines.append(f"stored_{ident} = {_dq(_default_value(ident))}")
        lines.append("")

    # --- ইনপুট লাইন (রিকোয়েস্টে যে ক্রমে চাওয়া হয়েছে সেই ক্রমে) ---
    for p in prog_inputs:
        lines.append(f'{input_idents[p]} = input({_dq(p + " লিখুন: ")})')
    lines.append("")

    # --- শর্ত ---
    op = "!=" if cond["negated"] else "=="
    comparisons: List[str] = []
    if cond["kind"] == "literal":
        target = cond["var"]
        for p in prog_inputs:
            if p == cond["var"] or _token_overlap(cond["var"], p):
                target = p
                break
        comparisons.append(f"{input_idents[target]} {op} {_dq(cond['value'])}")
    else:
        if facts["container"] or facts["storage_fields"]:
            key_phrases = facts["storage_fields"] or list(key_idents)
            for p in prog_inputs:
                key = _map_to_key(p, key_phrases)
                if key is None:
                    continue
                if facts["container"]:
                    comparisons.append(f'{input_idents[p]} {op} database["{key_idents[key]}"]')
                else:
                    comparisons.append(f"{input_idents[p]} {op} {stored_idents[key]}")
            if not comparisons:
                # কোনো ম্যাপিং হয়নি → প্রথম দুই ইনপুট পরস্পরের সাথে তুলনা
                if len(prog_inputs) >= 2:
                    comparisons.append(
                        f"{input_idents[prog_inputs[0]]} {op} {input_idents[prog_inputs[1]]}"
                    )
                else:
                    return None
        else:
            if len(prog_inputs) >= 2:
                for a, b in zip(prog_inputs, prog_inputs[1:]):
                    comparisons.append(f"{input_idents[a]} {op} {input_idents[b]}")
            else:
                return None
    if not comparisons:
        return None

    lines.append(f"if {' and '.join(comparisons)}:")
    for msg in success_msgs:
        lines.append(f"    print({_dq(msg)})")
    if else_msg:
        lines.append("else:")
        lines.append(f"    print({_dq(else_msg)})")
    return "\n".join(lines) + "\n"


def _assemble_print(success_msgs: List[str]) -> str:
    lines = [_HEADER, ""]
    for msg in success_msgs:
        lines.append(f"print({_dq(msg)})")
    return "\n".join(lines) + "\n"


def _assemble(facts: dict) -> Optional[str]:
    ok_outputs = [o for o in facts["outputs"] if not o["negated"]]
    success_msgs = [o["message"] for o in ok_outputs if not o["is_else"]]
    else_candidates = [o["message"] for o in ok_outputs if o["is_else"]]
    any_negated = any(o["negated"] for o in facts["outputs"])
    if not success_msgs:
        return None

    # ফ্যামিলি ১ (structured প্রোগ্রাম): শর্ত + আউটপুট + ইনপুট/স্টোরেজ
    if facts["condition"] is not None:
        if else_candidates:
            else_msg: Optional[str] = else_candidates[0]
        elif any_negated:
            else_msg = None  # ব্যবহারকারী স্পষ্টভাবে ব্যর্থতার বার্তা নিষেধ করেছেন
        elif facts["condition"]["kind"] == "match":
            # "মিললে"-শর্তে না-মিলার দিকটাও প্রোগ্রামের অংশ — ডিফল্ট ব্যর্থতার বার্তা
            else_msg = DEFAULT_FAILURE_MESSAGE
        else:
            # literal-if: শুধু সত্য-শাখার কথাই বলা হয়েছে — else জোর করে বসে না
            else_msg = None
        code = _assemble_program(facts, success_msgs, else_msg)
        if code:
            return code

    # ফ্যামিলি ২ (print-only): কনসোল-প্রসঙ্গ বা প্রোগ্রাম-সাবজেক্ট + প্রিন্ট-ক্রিয়া
    if facts["console"] or (facts["program_subject"] and facts["print_verb"]):
        return _assemble_print(success_msgs)
    return None


# ---------------------------------------------------------------------------
# পাবলিক API — match_dynamic_print_task()-এর মতোই (label, code) | None
# ---------------------------------------------------------------------------

def translate_bangla_rules(text: str) -> Optional[Tuple[str, str]]:
    """কড়া ফরম্যাটের বাংলা নির্দেশনা → (ENGINE_LABEL, python_code)।

    কোনো রুল-সেট পূর্ণ প্রোগ্রাম দাঁড়াতে না পারলে None — কলার (main.py) তখন
    পুরনো dynamic-print matcher → AI ফ্লোতে ফলব্যাক করে। জেনারেট হওয়া কোড
    সবসময় ast.parse-এ বৈধ কিনা যাচাই হয় — না হলেও None (কখনো raise নয়)।
    """
    try:
        facts = _parse(text)
        if facts is None:
            return None
        code = _assemble(facts)
        if not code:
            return None
        ast.parse(code)
        return ENGINE_LABEL, code
    except Exception:
        return None
