# 🏷️ Source Attribution (উৎস নির্দেশনা)

Rohan-bot-এর প্রতিটা তথ্যবহ উত্তরের নিচে এখন একটা **source badge** বসে — ইউজার এক নজরেই
বুঝতে পারেন উত্তরটা **কোথা থেকে** এসেছে, কতটা নির্ভরযোগ্য, এবং মূল সোর্সের লিংকই বা কী।

> **Phase:** 47 · **Status:** ✅ চালু (ডিফল্ট) · **Breaking change:** নেই

---

## ১. উৎসের ধরন

| চিহ্ন | উৎস | কখন ব্যবহার হয় | ডিফল্ট confidence |
|---|---|---|---|
| 🔵 **Groq API** | `GROQ` | LLM (Groq / OpenRouter / Cerebras) দিয়ে তৈরি লেখা | 90% |
| 🌐 **Browser Search** | `BROWSER` | লাইভ ওয়েব সার্চ — DuckDuckGo Instant Answer, Wikipedia | 85% |
| 💾 **Database** | `DATABASE` | বটের নিজের Brain OS (Knowledge/Pattern/Template Engine) বা Response Cache | 90% |
| 🔄 **Hybrid** | `HYBRID` | একাধিক উৎস মিলিয়ে (যেমন Browser-এর কাঁচা তথ্য Groq দিয়ে গুছিয়ে লেখা) | 88% |

বাংলা লেবেল: `🔵 Groq API` · `🌐 ব্রাউজার সার্চ` · `💾 ডাটাবেজ` · `🔄 সম্মিলিত`

### Confidence স্তর

| চিহ্ন | স্তর | সীমা |
|---|---|---|
| 🟢 | High / উচ্চ | ৮৫–১০০% |
| 🟡 | Medium / মাঝারি | ৬০–৮৫% |
| 🔴 | Low / নিম্ন | < ৬০% |

---

## ২. ব্যাজ ফরম্যাট (৪ রকম)

### `minimal` — শুধু উৎস
```
🌐 Browser Search
```

### `compact` — ডিফল্ট (সাধারণ উত্তর)
```
_উৎস: 🌐 ব্রাউজার সার্চ | 🔵 Groq API_
_[🕐 2026-08-26 04:58 UTC] [🔗 1 লিংক] [নির্ভুলতা: 🟢 উচ্চ]_
```

### `full` — `/search`-এর ডিফল্ট
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 উৎস তথ্য
├─ মূল উৎস: 🌐 ব্রাউজার সার্চ
├─ অন্য উৎস: 🔵 Groq API
├─ ধরন: 🔄 সম্মিলিত
├─ চেক করা হয়েছে: DuckDuckGo Instant Answer → Wikipedia (bn)
├─ নোট: কাঁচা ওয়েব-তথ্য AI দিয়ে গুছিয়ে লেখা
├─ সময়: 2026-08-26 04:58:36 UTC
└─ নির্ভুলতা: 🟢 উচ্চ (85%)

🔗 মূল সোর্স:
  • https://bn.wikipedia.org/wiki/ঢাকা

[আরও জানুন] [যাচাই করুন] [সমস্যা জানান]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### `detailed` — সংবেদনশীল তথ্যের জন্য (শতাংশসহ ভাঙন)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 উৎসের ভাঙন:
  • 70% - 🌐 ব্রাউজার সার্চ
  • 30% - 🔵 Groq API

⚠️ নির্ভুলতা নোট: তথ্যটি 2026-08-26 পর্যন্ত হালনাগাদ · 🟢 উচ্চ (85%)
🔗 মূল সোর্স:
  • https://bn.wikipedia.org/wiki/ঢাকা
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

প্রতিটা ফরম্যাটেই `lang="en"` দিলে ইংরেজি লেবেল পাওয়া যায়
(`Source Information` / `Primary Source` / `Confidence: 🟢 High` ইত্যাদি)।

---

## ৩. কোন কমান্ডে কী ব্যাজ

| কমান্ড | উৎস | ফরম্যাট |
|---|---|---|
| `/search প্রশ্ন` | 🌐 Browser → 💾 Database → 🔵 Groq (ফলব্যাক ক্রম) | `full` |
| সাধারণ চ্যাট (Brain OS direct) | 💾 Database (cache hit) | `compact` |
| সাধারণ চ্যাট (AI রুট) | 🔵 Groq API | `compact` |
| সাধারণ চ্যাট (shared cache hit) | 💾 Database (cache hit) | `compact` |
| সাধারণ চ্যাট (Browse Search) | 🌐 Browser বা 🔄 Hybrid | `compact` |
| `/joke`, `/quote` | 🔵 Groq API (confidence 0.95) | `compact` |
| `/translate`, `/grammar`, `/rewrite`, `/tone`, `/summarize` | 🔵 Groq API, অথবা cache hit হলে 💾 Database | `compact` |
| এরর / usage-নির্দেশিকা মেসেজ | কোনো ব্যাজ নয় | — |

---

## ৪. `/search` কমান্ড

```
/search বাংলাদেশের রাজধানী কোনটি?
```

খোঁজার ক্রম (প্রথম যেখানে আসল তথ্য মেলে সেটাই ফেরত যায়):

1. **🌐 Browser Search** — `browse_web_search()`: DuckDuckGo Instant Answer →
   Wikipedia (ইউজারের ভাষা) → Wikipedia (English)। AI দিয়ে গুছিয়ে লেখা হলে ব্যাজ হয় 🔄 Hybrid।
2. **💾 Database** — Brain OS Decision Engine-এর direct উত্তর (cache hit হিসেবে চিহ্নিত)।
3. **🔵 Groq API** — সাধারণ AI কল। *No API Call Mode চালু থাকলে এই ধাপ বাদ যায়।*

কিছুই না মিললে বন্ধুত্বপূর্ণ "পাওয়া যায়নি" মেসেজ যায় — তখন কোনো ব্যাজ বসে না
(কারণ তখন কোনো উৎসই নেই)।

---

## ৫. কোড স্ট্রাকচার

```
rohan_bot/
├── config.py                    # সেটিংস (single source of truth) + env override
└── utils/
    └── source_tracker.py        # DataSource, SourceMetadata, ব্যাজ তৈরি, format_with_source
main.py                          # Phase 47: লোডার + make_source_metadata/attach_source_badge
                                 #           + /search কমান্ড + হ্যান্ডলার ইন্টিগ্রেশন
docs/SOURCE_ATTRIBUTION.md       # এই ফাইল
tests/test_source_attribution.py        # ১২০ unit + integration টেস্ট
tests/test_browser_search_feature.py    # ৫৩ browser-search টেস্ট
```

`rohan_bot/utils/source_tracker.py` ইচ্ছে করেই Telegram/AI/DB থেকে **সম্পূর্ণ স্বাধীন** —
তাই এটা একা import করে মিলিসেকেন্ডে unit-test করা যায়।

### মূল API

```python
from rohan_bot.utils.source_tracker import (
    DataSource, SourceMetadata, build_metadata,
    metadata_from_browse_result, metadata_from_decision, format_with_source,
)

meta = build_metadata("browser", confidence_score=0.85, query="ঢাকা কোন দেশে?")
meta.add_url("https://bn.wikipedia.org/wiki/ঢাকা")
meta.add_secondary("groq")          # AI দিয়ে গুছিয়ে লেখা → 🔄 Hybrid
reply = format_with_source(answer, meta, command="search")   # lang="bn" ডিফল্ট
```

### `main.py`-এ ব্যবহার (হ্যান্ডলারের ভেতরে)

```python
metadata = make_source_metadata("groq", confidence=0.95, query="একটা জোক বলো")
await send_long_text(update, attach_source_badge(reply, metadata, "joke", attribution_lang(user_id)))
```

`make_source_metadata()` / `attach_source_badge()` **কখনো exception তোলে না** —
কোনো সমস্যা হলে মূল উত্তরটাই অপরিবর্তিত ফেরত যায়।

---

## ৬. কনফিগারেশন

### কোডে (`rohan_bot/config.py`)

```python
COMMAND_SETTINGS = {
    "search": {"enabled": True, "format": "full"},
    "joke":   {"enabled": True, "format": "compact"},
    ...
}
```

### Environment variable (Render/Replit Secrets — সবগুলো ঐচ্ছিক)

| Variable | উদাহরণ | কাজ |
|---|---|---|
| `SOURCE_ATTRIBUTION_ENABLED` | `false` | পুরো ফিচার বন্ধ |
| `SOURCE_ATTRIBUTION_FORMAT` | `full` | ডিফল্ট ফরম্যাট (`minimal`/`compact`/`full`/`detailed`) |
| `SOURCE_ATTRIBUTION_LANG` | `en` | ব্যাজের ডিফল্ট ভাষা |
| `SOURCE_ATTRIBUTION_DISABLED_COMMANDS` | `joke,quote` | নির্দিষ্ট কমান্ডের ব্যাজ বন্ধ |
| `SOURCE_ATTRIBUTION_ENABLED_COMMANDS` | `ocr` | নির্দিষ্ট কমান্ডের ব্যাজ চালু |

---

## ৭. নিরাপত্তা ও সীমা

* **ব্যাজ বন্ধ থাকলে তথ্য হারায় না** — Phase 44-এর Browse Search উত্তরে তখন পুরোনো
  `🔗 উৎস: ... / 🔎 চেক করা হয়েছে: ...` ফুটারই দেখানো হয়।
* **প্যাকেজ না থাকলে বট ভাঙে না** — শুধু `main.py` কপি করে চালালে
  `SOURCE_ATTRIBUTION_AVAILABLE = False` হয়ে যায়, ব্যাজ বন্ধ থাকে, বাকি সব আগের মতো চলবে।
* **চ্যাট-মেমরি পরিষ্কার থাকে** — কথোপকথনের ইতিহাসে ব্যাজ ছাড়া উত্তরই সেভ হয়।
* **Overhead** — একটা ব্যাজ বানাতে < ১ মি.সে. (টেস্টে ১০ মি.সে.-এর সীমা assert করা আছে)।
* **ভাষা** — ব্যাজের স্ট্যাটিক লেবেল বাংলা ও ইংরেজিতে আছে; অন্য UI ভাষা (hi/ar/ur/es)
  বেছে নিলে ব্যাজ ইংরেজিতে যায়।

---

## ৮. টেস্ট চালানো

```bash
python3 tests/test_browser_search_feature.py      # ৫৩ টেস্ট (Phase 1)
python3 tests/test_source_attribution.py          # ১২০ টেস্ট (Phase 2)

# অথবা pytest দিয়ে
python3 -m pytest tests/test_browser_search_feature.py tests/test_source_attribution.py -q
```

নতুন কোডের coverage: **`rohan_bot/` = 100%** (`python3 -m coverage run --source=rohan_bot ...`)।

---

## ৯. অ্যাডমিন মনিটরিং

`/brainstatus`-এ এখন এগুলোও দেখা যায়:

```
🌐 Phase 44 Browse Search দিয়ে উত্তর দেওয়া হয়েছে: 12 বার
🔎 Phase 47 /search দিয়ে উত্তর দেওয়া হয়েছে: 5 বার
🏷️ Source Attribution: ✅ চালু (ডিফল্ট ফরম্যাট: compact)
```
