# 🏷️ Source Attribution (উৎস নির্দেশনা)

Rohan-bot-এর প্রতিটা তথ্যবহ উত্তরের নিচে এখন একটা **source badge** বসে — ইউজার এক নজরেই
বুঝতে পারেন উত্তরটা **কোথা থেকে** এসেছে, কতটা নির্ভরযোগ্য, এবং মূল সোর্সের লিংকই বা কী।

> **Phase:** 47 · **Status:** ✅ চালু (ডিফল্ট) · **Breaking change:** নেই

---

## ১. উৎসের ধরন

| চিহ্ন | উৎস | কখন ব্যবহার হয় | ডিফল্ট confidence |
|---|---|---|---|
| 🔵 **Groq API** | `GROQ` | LLM (Groq / OpenRouter / Cerebras) দিয়ে তৈরি লেখা | 90% |
| 🌐 **Browser Search** | `BROWSER` | লাইভ ওয়েব সার্চ — Tavily (Phase 48, Key থাকলে), DuckDuckGo Instant Answer, Wikipedia | 85% |
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

## ২. স্বয়ংক্রিয় Priority (Automatic priority)

প্রতিটা তথ্যবহ উত্তরের জন্য বট এই ক্রমে উৎস খোঁজে — **কোনো আলাদা `/search` কমান্ডের দরকার নেই**:

```
ইউজারের প্রশ্ন
      │
      ▼
1️⃣ 💾 Database check ────────────── পেলে → 💾 Database (ব্যাজসহ উত্তর)
      │ না পেলে
      ▼
2️⃣ 🌐 Browser Search (automatic) ── পেলে → 🌐 Browser / 🔄 Hybrid (ব্যাজসহ উত্তর)
      │ না পেলে
      ▼
3️⃣ 🔵 Groq API (fallback) ─────────── → 🔵 Groq API (ব্যাজসহ উত্তর)
```

- **Step 2** সম্পূর্ণ স্বয়ংক্রিয় (Phase 48): Tavily Real Web Search (`TAVILY_API_KEY` থাকলে) →
  DuckDuckGo Instant Answer → Wikipedia (ইউজারের ভাষা) →
  Wikipedia (English)। No API Call Mode বন্ধ থাকলে কাঁচা ওয়েব-তথ্য AI দিয়ে গুছিয়ে লেখা হয়
  (তখন ব্যাজ 🔄 Hybrid); চালু থাকলে কোনো AI কল ছাড়াই কাঁচা তথ্যটাই যায় (🌐 Browser)।
- **No API Call Mode** চালু থাকলে Step 3 (🔵 Groq API) বাদ যায় — DB ও (ফ্রি) Browser-এ কিছু
  না পেলে "আটকে গেছে" মেসেজ যায়।

এই একই ক্রম সব হ্যান্ডলারে প্রযোজ্য: **chat, joke, quote, translate, grammar, rewrite,
tone, summarize**।

উদাহরণ:

```
User: "বাংলাদেশের প্রধানমন্ত্রী কে?"
↓ (automatic priority)
Database check → (না থাকলে) Browser search → (তাও না থাকলে) Groq API
```

---

## ৩. ব্যাজ ফরম্যাট (৪ রকম)

### `minimal` — শুধু উৎস
```
🌐 Browser Search
```

### `compact` — ডিফল্ট (সাধারণ উত্তর)
```
_উৎস: 🌐 ব্রাউজার সার্চ | 🔵 Groq API_
_[🕐 2026-08-26 04:58 UTC] [🔗 1 লিংক] [নির্ভুলতা: 🟢 উচ্চ]_
```

### `full` — সোর্স-গুরুত্বপূর্ণ উত্তরের জন্য (কনফিগে যেকোনো কমান্ডে বসানো যায়)
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

## ৪. কোন হ্যান্ডলারে কী ব্যাজ

| হ্যান্ডলার | উৎস | ফরম্যাট |
|---|---|---|
| সাধারণ চ্যাট (DB direct) | 💾 Database (cache hit) | `compact` |
| সাধারণ চ্যাট (Browser Search) | 🌐 Browser বা 🔄 Hybrid | `compact` |
| সাধারণ চ্যাট (Groq API / shared cache) | 🔵 Groq API, ক্যাশ-হিটে 💾 Database | `compact` |
| `/joke`, `/quote` | 💾 Database (ক্যাশ) → 🌐 Browser → 🔵 Groq API | `compact` |
| `/translate`, `/grammar`, `/rewrite`, `/tone`, `/summarize` | 💾 Database (ক্যাশ) → 🌐 Browser → 🔵 Groq API | `compact` |
| এরর / usage-নির্দেশিকা মেসেজ | কোনো ব্যাজ নয় | — |

> সব হ্যান্ডলারেই priority একই: **💾 Database → 🌐 Browser → 🔵 Groq API**।

---

## ৫. কোড স্ট্রাকচার

```
rohan_bot/
├── config.py                    # সেটিংস (single source of truth) + env override
└── utils/
    └── source_tracker.py        # DataSource, SourceMetadata, ব্যাজ তৈরি, format_with_source
main.py                          # Phase 47: লোডার + make_source_metadata/attach_source_badge
                                 #           + _automatic_browse_answer (automatic Browser Search)
                                 #           + প্রতিটা হ্যান্ডলারে DB→Browser→API priority
docs/SOURCE_ATTRIBUTION.md       # এই ফাইল
tests/test_source_attribution.py # unit + integration + automatic-browse টেস্ট
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
reply = format_with_source(answer, meta, command="chat")   # lang="bn" ডিফল্ট
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
    "chat":   {"enabled": True, "format": "compact"},
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

* **ব্যাজ বন্ধ থাকলে তথ্য হারায় না** — Browse Search উত্তরে তখন পুরোনো
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
python3 tests/test_source_attribution.py          # unit + integration + automatic-browse টেস্ট

# অথবা pytest দিয়ে
python3 -m pytest tests/test_source_attribution.py -q
```

নতুন কোডের coverage: **`rohan_bot/` = 100%** (`python3 -m coverage run --source=rohan_bot ...`)।

---

## ৯. অ্যাডমিন মনিটরিং

`/brainstatus`-এ এখন এগুলোও দেখা যায়:

```
🌐 Phase 44 Browse Search দিয়ে উত্তর দেওয়া হয়েছে: 12 বার
🏷️ Source Attribution: ✅ চালু (ডিফল্ট ফরম্যাট: compact)
```
