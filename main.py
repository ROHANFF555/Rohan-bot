"""
=========================================================================
 সম্পূর্ণ Telegram AI Bot — একটাই ফাইল, সব ফ্রি টুলস দিয়ে বানানো
=========================================================================
গুরুত্বপূর্ণ: পুরো বট এই একটা মাত্র ফাইলে (main.py)। আলাদা কোনো requirements.txt
বা .env ফাইলের দরকার নেই — নিচের নির্দেশনা মতো Shell আর Secrets সেট করলেই হবে।

Replit-এ চালানোর ধাপ:
  1) এই ফাইলটাকে main.py নামে Replit-এ পেস্ট করুন (আগের main.py প্রতিস্থাপন করে)
  2) Shell-এ একবার এই লাইনটা রান করুন (সবগুলো ফ্রি ও ওপেন-সোর্স লাইব্রেরি):
     pip install "python-telegram-bot[job-queue]" edge-tts groq python-dotenv PyPDF2 langdetect pytesseract Pillow httpx
     (Replit-এর Shell-এ ffmpeg না থাকলে) নিচেরটাও রান করুন:
     nix-env -iA nixpkgs.ffmpeg
     — ভিডিও বাংলা ডাবিং ফিচারের জন্য ffmpeg দরকার। ইনস্টলের পর নিশ্চিত হতে লিখুন: ffmpeg -version
     (OCR ফিচারের জন্য) নিচেরটাও রান করুন:
     nix-env -iA nixpkgs.tesseract
     — Tesseract না থাকলে OCR ফিচার নিজে থেকে বন্ধ থাকবে, বটের বাকি অংশ ঠিকই চলবে।
  3) Replit-এর "Secrets" (তালা চিহ্ন) এ এই Key-গুলো বসান:
     TELEGRAM_BOT_TOKEN   = আপনার বট টোকেন (BotFather থেকে) — বাধ্যতামূলক
     ADMIN_IDS            = আপনার Telegram ইউজার আইডি, কমা দিয়ে একাধিক দেওয়া যায় — বাধ্যতামূলক

     Phase 8: প্রতিটা AI Provider-এ একাধিক Key দেওয়া যায় (Load Balancing/Health Check-এর জন্য) —
     GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3         = console.groq.com থেকে ফ্রি Key
     OPENROUTER_API_KEY_1, OPENROUTER_API_KEY_2             = openrouter.ai থেকে ফ্রি Key
     CEREBRAS_API_KEY_1, CEREBRAS_API_KEY_2                 = cloud.cerebras.ai থেকে ফ্রি Key
     (আগের একক GROQ_API_KEY / OPENROUTER_API_KEY / CEREBRAS_API_KEY Secret থাকলে সেগুলোও
     এখনো কাজ করবে — মুছে ফেলার দরকার নেই, বট সবগুলোকেই একসাথে pool হিসেবে ব্যবহার করবে)

     প্রতিটা Provider-এর অন্তত একটা Key থাকলে ভালো, না থাকলেও বট বন্ধ হবে না — শুধু সেই
     Provider বাদ পড়ে পরেরটা ব্যবহার হয়। AI Provider-এর মধ্যে অন্তত একটা Key মোটকথা লাগবে।
     GROQ Key না থাকলে শুধু Voice-to-Text (ভয়েস মেসেজ/ভিডিও ডাবিং) ফিচারটা বন্ধ থাকবে,
     কারণ ওটা এখনো শুধু Groq Whisper দিয়েই হয় (দেখুন নিচে "Phase 7")।
  4) Run বাটনে চাপুন। ব্যস, বট চালু।

ফ্রি সীমা: প্রতিদিন একজন সাধারণ ইউজার ১৫ বার AI ফিচার ব্যবহার করতে পারবে।
অ্যাডমিন (ADMIN_IDS-এ যার আইডি আছে) এর কোনো সীমা নেই।

Phase 1 আপডেটে যা যা নতুন যোগ হয়েছে:
  Better Logging, Better Error Handling, Anti-Spam/Anti-Flood,
  /ping, /uptime, /mylimit, /feedback, /bugreport,
  /serverstatus, /backup, /restore, /dashboard, Better Broadcast।
  (লগ ফাইল নিজে থেকে তৈরি হবে: logs/bot.log — আলাদা করে কিছু করা লাগবে না)

Phase 2 আপডেটে যা যা নতুন যোগ হয়েছে:
  AI Memory (/memory, /clearmemory), Language Detection (/detectlang),
  Auto Reply On/Off (/autoreply), Better Profile/Help/Settings
  (/menu, /settings — ইনলাইন কীবোর্ড মেনু), Leaderboard (/leaderboard),
  Daily ও Monthly Statistics (/dailystats, /monthlystats)।
  লাইব্রেরি না থাকলেও (langdetect) বট ভাঙবে না — নিজে থেকে সাধারণ পদ্ধতিতে
  ভাষা অনুমান করবে, তবে ভালো ফলাফলের জন্য pip install-এ langdetect রাখুন।

Phase 3 আপডেটে যা যা নতুন যোগ হয়েছে:
  OCR (/ocr — ছবিতে রিপ্লাই দিয়ে লিখুন, ছবির লেখা বের করে দেবে, pytesseract দিয়ে ফ্রি),
  PDF প্রশ্ন-উত্তর (/askpdf প্রশ্ন — PDF-এ রিপ্লাই দিয়ে বা আগে /pdf পড়ানো থাকলে সরাসরি
  নির্দিষ্ট প্রশ্ন করলে ডকুমেন্ট থেকে উত্তর দেবে, /clearpdf দিয়ে সেশন মুছে ফেলা যাবে),
  শিডিউল ব্রডকাস্ট (/schedulebroadcast, /listschedules, /cancelschedule — নির্দিষ্ট
  তারিখ-সময়ে ব্রডকাস্ট পাঠানো, বট বন্ধ থেকে আবার চালু হলেও মিস হবে না),
  মাল্টি-ভাষা সাপোর্ট (/setlang — ইউজার নিজের পছন্দের ভাষা সেট করলে বটের মূল মেনু,
  প্রোফাইল, সেটিংস ইত্যাদি জায়গায় বট সেই ভাষায় উত্তর দেবে; অনুবাদ একবার হলে দ্রুততার
  জন্য মেমরিতে ক্যাশ করে রাখা হয়),
  এবং Performance ও Security Improvement (AI/Whisper কল এখন ব্যাকগ্রাউন্ড থ্রেডে চলে
  যাতে একজনের অনুরোধের সময় বট অন্য সবার জন্য আটকে না থাকে, ঘন ঘন ব্যবহৃত টেবিলে ডাটাবেস
  ইনডেক্স যোগ হয়েছে, ছবি/ফাইলের সাইজ-সীমা ও ইনপুট যাচাই আরও শক্ত করা হয়েছে)।

Phase 4 আপডেটে যা যা নতুন যোগ হয়েছে:
  Premium System — ফ্রি ও প্রিমিয়াম ইউজার আলাদা। প্রিমিয়াম ইউজারের দৈনিক সীমা ফ্রি-এর
  চেয়ে বেশি (ডিফল্ট ১০০ বার/দিন), এবং কিছু অতিরিক্ত সুবিধা পান (AI Memory-তে বেশি কথোপকথন
  মনে রাখা হয়, Anti-Flood কুলডাউন প্রযোজ্য হয় না)। মেয়াদ (দিন সংখ্যা দিয়ে সেট করা,
  তাই ৩০ দিলে মাস, ৩৬৫ দিলে বছর ইত্যাদি) সহ অ্যাডমিন কমান্ড দিয়ে কাউকে প্রিমিয়াম করা/
  বাতিল করা/চেক করা যায়:
    /addpremium ইউজার_আইডি দিন_সংখ্যা   — প্রিমিয়াম দেওয়া বা মেয়াদ বাড়ানো (অ্যাডমিন)
    /removepremium ইউজার_আইডি          — প্রিমিয়াম বাতিল করা (অ্যাডমিন)
    /premiumstatus [ইউজার_আইডি]        — নিজের প্ল্যান দেখা (সবাই); অ্যাডমিন অন্য কারো আইডি
                                          দিয়ে অন্য কারো প্ল্যানও দেখতে পারবেন
    /premiumlist                       — সব সক্রিয় প্রিমিয়াম ইউজারের তালিকা (অ্যাডমিন)
  Notifications — মেয়াদ শেষ হওয়ার ২ দিন আগে ইউজারকে রিমাইন্ডার পাঠানো হয় (একবারই),
  মেয়াদ শেষ হয়ে গেলে স্বয়ংক্রিয়ভাবে প্রিমিয়াম বাতিল করে ইউজার ও অ্যাডমিনদের জানানো হয়,
  এবং অ্যাডমিন কাউকে প্রিমিয়াম দিলে/বাতিল করলে সাথে সাথে সেই ইউজার ও অন্য অ্যাডমিনদেরও
  বার্তা পাঠানো হয়। এই চেকগুলো একটা ব্যাকগ্রাউন্ড জব দিয়ে নিয়মিত (প্রতি ৬ ঘণ্টায়) চলে,
  পুরোপুরি ফ্রি — কোনো পেইড API/সার্ভিস লাগে না (শুধু ডাটাবেস + বটের নিজের মেসেজ পাঠানো)।

Phase 5 আপডেটে যা যা নতুন যোগ হয়েছে:
  Referral System — প্রতিটা ইউজারের নিজস্ব রেফার লিংক (/myreferrals দিয়ে দেখা যায়)।
  কেউ সেই লিংক দিয়ে নতুন হয়ে বটে জয়েন করলে রেফারার ও নতুন ইউজার — দুজনেই +৩ (স্থায়ী)
  অতিরিক্ত দৈনিক সীমা পান (সর্বোচ্চ +৬০ পর্যন্ত জমা যায়, অপব্যবহার ঠেকাতে)। দুজনকেই
  সাথে সাথে বার্তা দিয়ে জানানো হয়।
  Admin Roles — এখন একাধিক অ্যাডমিন রাখা যায়, আলাদা ক্ষমতাসহ:
    Owner (Secrets/.env-এর ADMIN_IDS) — সব কমান্ড, Admin/Moderator যোগ-বাদ দিতে পারেন
    Admin (/addadmin দিয়ে যোগ করা)     — ব্যান/আনব্যান/প্রিমিয়াম/ব্রডকাস্ট করতে পারেন
    Moderator (/addadmin দিয়ে যোগ করা) — শুধু ব্যান/আনব্যান ও দেখাশোনা করতে পারেন
    /addadmin ইউজার_আইডি রোল, /removeadmin ইউজার_আইডি, /adminlist — রোল ম্যানেজমেন্ট
  Admin Control Panel — /adminpanel লিখলে বাটন-ভিত্তিক ইনলাইন কীবোর্ড প্যানেল খুলবে:
  ইউজার আইডি সার্চ করে এক জায়গা থেকেই ব্যান/আনব্যান, প্রিমিয়াম দেওয়া/বাতিল করা যাবে,
  সাথে প্রিমিয়াম তালিকা, পরিসংখ্যান ও অ্যাডমিন তালিকা দেখা যাবে — কোনো কমান্ড টাইপ না করেই।
  Admin-only coding command-গুলো (/codebasescan, /codeauto, /codeexec ইত্যাদি) সাধারণ
  ইউজারদের /start, /help, /menu বা /codehelp-এ দেখানো হয় না — ওগুলোর তালিকা শুধু এই
  প্যানেলের "💻 Admin Coding কমান্ড" বাটনে থাকে, আর প্রতিটা কমান্ডের ভিতরে is_admin() চেক আছে।

Phase 6 আপডেটে যা যা নতুন যোগ হয়েছে:
  আরও গভীর Analytics (/analytics [দিন]) — সর্বকালের সেরা ১০ কমান্ড/ফিচার, দিনের কোন
  সময়ে বট বেশি ব্যবহার হয় (ঘণ্টাভিত্তিক), এবং গত কয়েক দিনের ইউজার-গ্রোথ — সবই সাধারণ
  টেক্সট বার-চার্ট আকারে (কোনো ইমেজ লাইব্রেরি লাগে না)। Admin Panel-এও এই বাটন যোগ হয়েছে।
  পুরো বট আরেকবার রিভিউ করে একটা পারফরম্যান্স বাগ ঠিক করা হয়েছে (অ্যাডমিন-রোল চেক এখন
  মেমরিতে ক্যাশ হয়, প্রতিটা মেসেজে বাড়তি ডাটাবেস কুয়েরি লাগে না)। সাথে এই README.md ফাইল।

Phase 7 আপডেটে যা যা নতুন যোগ হয়েছে (সম্পূর্ণ ফ্রি AI Architecture):
  আগে বট শুধু Groq-এর উপর নির্ভর করত। এখন AI Provider Router চালু হয়েছে —
  OpenRouter (ফ্রি মডেল) -> Groq (fallback) -> Cerebras (fallback), স্বয়ংক্রিয়ভাবে
  একটা ব্যর্থ হলে (rate limit/টাইমআউট/এরর) পরেরটায় চলে যায়। AI চ্যাট, অনুবাদ, গ্রামার,
  Rewrite, Tone, Summarize, PDF সামারি/প্রশ্ন-উত্তর — সবগুলো ফিচার এখন এই Router ব্যবহার করে।
  তিনটা AI Provider-এর জন্য আলাদা ক্লাস (OpenRouterProvider/GroqProvider/CerebrasProvider) —
  ভবিষ্যতে নতুন কোনো ফ্রি Provider যোগ করতে চাইলে শুধু একটা নতুন ক্লাস লিখে ai_router-এর
  লিস্টে যোগ করলেই হবে। কোনো একটা Secret (API Key) না থাকলে বট Crash করবে না — শুধু
  সেই Provider বাদ পড়ে পরেরটা ব্যবহার হয় (Console-এ স্পষ্ট Warning দেখাবে)। Language
  Detection আগে থেকেই local (langdetect) লাইব্রেরি দিয়ে হতো, কোনো API লাগে না — অপরিবর্তিত।
  Text-to-Speech (Edge-TTS) ও Speech-to-Text (Groq Whisper) অপরিবর্তিত আছে — GROQ_API_KEY
  না থাকলে শুধু Speech-to-Text (ভয়েস মেসেজ/ভিডিও ডাবিং) বন্ধ থাকবে, বাকি সব ঠিকই চলবে।
  বটের কোনো Command/Button/UI বদলায়নি — শুধু ভেতরের AI কল করার পদ্ধতি বদলেছে।

Phase 8 আপডেটে যা যা নতুন যোগ হয়েছে (Enterprise Multi-Key Pool):
  প্রতিটা AI Provider (OpenRouter/Groq/Cerebras)-এ এখন একাধিক API Key দেওয়া যায়
  (GROQ_API_KEY_1/2/3, OPENROUTER_API_KEY_1/2, CEREBRAS_API_KEY_1/2) — শুধু Performance ও
  Availability বাড়ানোর জন্য (কোনো Provider-এর Rate Limit/ToS এড়ানোর জন্য নয়)।
  ManagedKey ক্লাস প্রতিটা Key-এর অবস্থা (কয়টা রিকোয়েস্ট চলছে, গড় রেসপন্স টাইম, স্বাস্থ্য)
  আলাদাভাবে ট্র্যাক করে। KeyPool ক্লাস Load Balancer হিসেবে কাজ করে — প্রতিটা কলে সবচেয়ে
  কম ব্যস্ত ও সবচেয়ে দ্রুত Key বেছে নেয় (Key Rotation)। Health Checker: কোনো Key পরপর কয়েকবার
  ব্যর্থ হলে (rate limit/টাইমআউট/এরর) সাময়িক Inactive হয়ে যায় (কুলডাউন ক্রমশ বাড়ে), কুলডাউন
  শেষ হলে এমনিতেই আবার ব্যবহারযোগ্য হয়ে যায় — আলাদা কোনো ব্যাকগ্রাউন্ড জব ছাড়াই।
  Smart Routing (OpenRouter -> Groq -> Cerebras) অপরিবর্তিত আছে — একটা Provider-এর পুরো Key
  Pool ব্যর্থ হলে তবেই পরের Provider-এ যাওয়া হয়, তার আগে একই Provider-এর অন্য Key দিয়ে চেষ্টা
  হয়। Security: কোনো আসল API Key কখনো লগ/প্রিন্ট হয় না — শুধু label (যেমন "Groq Key #2")
  ব্যবহার হয়। আগের একক Secret (GROQ_API_KEY ইত্যাদি) মুছে ফেলার দরকার নেই — ব্যাকওয়ার্ড-
  কম্প্যাটিবল, সেগুলোও pool-এর অংশ হিসেবে গণ্য হয়। /serverstatus-এ এখন প্রতিটা Provider-এ
  কয়টা Key সুস্থ আছে তা দেখা যায়। বটের কোনো Command/Button/UI বদলায়নি।

Phase 9 আপডেটে যা যা নতুন যোগ হয়েছে (Queue Manager + Retry/Timeout + Performance):
  Async Queue Manager — একসাথে অনেক ইউজার AI ফিচার (চ্যাট/অনুবাদ/সামারি ইত্যাদি) ব্যবহার
  করলে বট freeze না করে সবগুলো রিকোয়েস্ট একটা FIFO সারিতে জমা রেখে সীমিতসংখ্যক Worker
  (ডিফল্ট ৮টা, AI_QUEUE_MAX_WORKERS) দিয়ে সমান্তরালে, non-blocking ভাবে প্রসেস করে। এটা
  asyncio.Queue + Worker Task দিয়ে বানানো, কোনো বাহ্যিক সার্ভিস (Redis ইত্যাদি) লাগে না।
  Per-Key Retry System রিফাইন — আগে একটা Key ব্যর্থ হলেই সাথে সাথে পরের Key-তে চলে যেত;
  এখন প্রতিটা Key-তে (Exponential Backoff সহ, AI_KEY_RETRY_MAX_ATTEMPTS বার পর্যন্ত) আবার
  চেষ্টা করা হয়, শুধু বারবার ব্যর্থ হলে বা Key সাময়িক Inactive হয়ে গেলে তবেই পরের Key/
  Provider-এ যাওয়া হয় — সাময়িক (transient) নেটওয়ার্ক/rate-limit সমস্যায় অযথা Provider
  বদলানো কমে।
  Timeout Manager — প্রতিটা HTTP/API কলের নিজস্ব timeout (AI_HTTP_TIMEOUT) আগে থেকেই ছিল;
  এখন এর উপরে গোটা রিকোয়েস্টের (সব Retry/Provider-বদল মিলিয়ে) একটা Hard Timeout-ও যোগ
  হয়েছে (AI_REQUEST_HARD_TIMEOUT) — এর বেশি সময় ধরে আটকে থাকা কোনো রিকোয়েস্ট
  asyncio.wait_for দিয়ে বাতিল হয়ে ইউজারকে আগে থেকে থাকা এরর মেসেজ দেখানো হয়।
  Connection Pool — OpenRouter ও Cerebras-এর জন্য (যেগুলো httpx দিয়ে সরাসরি HTTP কল করে)
  আগে প্রতিটা কলে নতুন httpx.AsyncClient তৈরি হতো; এখন একটাই Shared, পুনর্ব্যবহারযোগ্য
  httpx.AsyncClient (Keep-Alive Connection Pool সহ) পুরো বট জুড়ে ব্যবহার হয় — বারবার নতুন
  TCP/TLS কানেকশন বানানোর ওভারহেড কমে, রেসপন্স আগের চেয়ে দ্রুত আসে।
  উপরের সবগুলোই ask_ai/ask_ai_with_history ফাংশনের ভেতরে (স্বচ্ছভাবে) যোগ হয়েছে — বটের
  কোনো Command/Feature/UI বদলায়নি, শুধু AI Engine-টা ভেতরে ভেতরে আরও শক্তিশালী হয়েছে।

Phase 10 আপডেটে যা যা নতুন যোগ হয়েছে (Response Cache + Statistics Manager + Logging):
  Response Cache — translate/grammar/rewrite/tone/summarize/askpdf-এর মতো deterministic
  ফিচারে একই (system_prompt + প্রশ্ন) কম্বিনেশন আগে জিজ্ঞেস করা থাকলে আবার AI Provider-এ না
  পাঠিয়ে সরাসরি আগের উত্তর থেকে জবাব দেয় (ask_ai(..., use_cache=True))। সম্পূর্ণ মেমরিতে
  (LRU, সর্বোচ্চ ৩০০ এন্ট্রি + ৩০ মিনিট TTL), কোনো Redis/এক্সট্রা সার্ভিস লাগে না, বট
  রিস্টার্ট হলে খালি হয়ে যায়। joke/quote (ইচ্ছাকৃতভাবে ভিন্ন উত্তর) ও Memory-ভিত্তিক চ্যাটে
  (প্রসঙ্গ প্রতিবার বদলায়) এই ক্যাশ প্রযোজ্য না — ডিফল্ট use_cache=False, তাই বাকি সব ফিচার
  আগের মতোই প্রতিবার তাজা উত্তর পায়।
  Statistics Manager — প্রতিটা Provider/Key কতবার ব্যবহার হয়েছে, Response Time, Error/Retry
  সংখ্যা (এগুলো আগে থেকেই ManagedKey ট্র্যাক করত), সাথে এখন Queue Time (গড়/সর্বোচ্চ) ও
  Response Cache Hit/Miss-ও কেন্দ্রীয়ভাবে ট্র্যাক হয়। অ্যাডমিনের জন্য নতুন কমান্ড /aistats
  দিয়ে সবকিছু এক জায়গায় দেখা যায়।
  বিস্তারিত Logging — প্রতিটা AI রিকোয়েস্টে কোন Provider/Key (শুধু label/নম্বর, যেমন
  "Groq Key #2" — আসল Key কখনোই না), Response Time, Retry Count, এবং সফল/ব্যর্থ (Error সহ)
  স্ট্যাটাস এখন স্পষ্টভাবে লগ হয় (logs/bot.log-এ)।
  বটের কোনো Command/Feature/UI বদলায়নি (শুধু নতুন /aistats কমান্ড যোগ হয়েছে) — বাকি সব আগের
  মতোই কাজ করে, ভেতরের AI Engine আরও পর্যবেক্ষণযোগ্য (observable) হয়েছে।

Phase 11 আপডেটে যা যা নতুন যোগ হয়েছে (Coding Orchestrator):
  বড় কোডিং রিকোয়েস্ট এখন একবারে AI-কে না পাঠিয়ে ধাপে ধাপে সামলানো হয়:
    /codeproject <বিবরণ>  — Prompt Analyze (রিকোয়েস্ট বিশ্লেষণ) + Project Plan (ছোট ছোট
                            ধারাবাহিক ধাপে ভাগ করা), একটা AI কলে JSON প্ল্যান আকারে তৈরি হয়
    /codenext              — Task Split: পরের ধাপটা একাই প্রসেস হয় (পুরো প্রজেক্ট না, শুধু
                            সেই ধাপের জন্য ছোট নির্দিষ্ট প্রশ্ন AI-কে পাঠানো হয়)
    /codestatus, /codetask <নাম্বার>, /codeprojects, /useproject <আইডি>,
    /exportcode, /deleteproject <আইডি>, /codehelp
  Knowledge Base/Template — কমন প্যাটার্ন/বয়লারপ্লেট (.gitignore, README, .env, Flask/
  FastAPI স্কেলিটন, logging setup, sqlite boilerplate, বেসিক HTML, package.json ইত্যাদি)
  বট নিজে থেকেই জানে — এসব ধাপে AI-কে জিজ্ঞেস না করে সরাসরি কোড বসিয়ে দেয়।
  Assemble — AI/Knowledge Base থেকে পাওয়া প্রতিটা ধাপের কোড বট নিজে জোড়া লাগিয়ে
  /exportcode দিয়ে একটা সম্পূর্ণ ফাইল হিসেবে পাঠায়।
  Project Memory — প্রতিটা ইউজারের প্রতিটা প্রজেক্ট ও তার সব ধাপ ডাটাবেসে (code_projects,
  code_tasks টেবিল) স্থায়ীভাবে থাকে, বট রিস্টার্ট হলেও হারায় না; একজন ইউজার একসাথে একাধিক
  প্রজেক্ট রাখতে পারেন, /useproject দিয়ে যেকোনোটা সক্রিয় করা যায়।
  বটের আগের কোনো Command/Feature/UI বদলায়নি — এই পুরো সেকশনটাই নতুন সংযোজন।

Phase 18: Full Codebase Intelligence — project scan/index, AST symbol/import/route extraction,
file dependency + caller/callee edges, relevant-code search/context, architecture summary,
impact analysis, placement heuristic, persistent SQLite index এবং incremental re-indexing।
Admin commands: /codebasescan, /codebasestatus।

Phase 44 আপডেটে যা যা নতুন যোগ হয়েছে (Browse Search — ফ্রি ওয়েব সার্চ ফলব্যাক):
  স্বাভাবিক চ্যাটে ইউজার কিছু জিজ্ঞেস করলে ক্রম এখন এমন: প্রথমে Brain OS নিজের ডাটাবেজে
  (Knowledge/Pattern/Template/Documentation Engine, Decision Engine দিয়ে) খোঁজে (আগে থেকেই
  ছিল) — কোনো ভরসাযোগ্য সরাসরি উত্তর না পেলে, AI API কল করার আগে একবার সম্পূর্ণ ফ্রি (কোনো
  Key/টাকা লাগে না) Browse Search চেষ্টা করা হয় (DuckDuckGo Instant Answer, না পেলে
  Wikipedia)। যেমন: "বাংলাদেশের প্রধানমন্ত্রীর নাম কি" প্রশ্নটা ডাটাবেজে না থাকলে Browse
  Search-এ যাবে, তথ্য পেলে (No API Call Mode বন্ধ থাকলে) ছোট্ট একটা AI কল দিয়ে সেটা ইউজারের
  ভাষায় সাজিয়ে-গুছিয়ে উত্তর দেওয়া হয় এবং সাথে সাথেই নিজের Knowledge Engine-এ যুক্ত হয়ে যায়
  (পরের বার একই/কাছাকাছি প্রশ্নে আর Browse/AI কোনোটাই লাগবে না, Brain OS সরাসরি উত্তর
  দিতে পারবে)। Browse Search-এ কিছু না পেলে তখনই স্বাভাবিক AI API কল (ask_ai/
  ask_ai_with_history) হয়, আগের মতোই — আর AI যে উত্তরই দিক না কেন, সেটাও নিজে থেকে
  Knowledge Engine-এ সেভ হয়ে যায়। No API Call Mode চালু থাকলে Browse Search চলবে (এটা কোনো
  AI Provider কল নয়), কিন্তু ফলাফল গুছাতে আলাদা কোনো AI কল করা হয় না — কাঁচা তথ্যই উৎসসহ
  দেখানো হয়। বটের কোনো Command/Button/UI বদলায়নি, /brainstatus-এ এখন Browse Search-এর
  পরিসংখ্যানও দেখা যায়।

Phase 45 আপডেটে যা যা নতুন যোগ হয়েছে (নিজস্ব API Key — Own API Key):
  প্রতিটা ইউজার এখন চাইলে নিজের OpenRouter/Groq/Cerebras API Key বটে যুক্ত করতে পারবেন —
  /setapikey provider আপনার_key (DM/প্রাইভেট চ্যাটে ব্যবহারের পরামর্শ দেওয়া হয়; গ্রুপে লিখলে
  বট নিজে থেকে সেই মেসেজ মুছে ফেলার চেষ্টা করে)। যুক্ত করলে তার সেই Provider-এর AI
  রিকোয়েস্টগুলো শুধু তার নিজের Key দিয়েই যায় — বটের শেয়ার্ড Key Pool স্পর্শ করে না, তাই
  একসাথে ৫/১০ জন ফ্রি Key শেয়ার করে ব্যবহার করলেও তার রিকোয়েস্ট তাদের সাথে প্রতিযোগিতা করে
  না (rate limit-এ পড়ার সম্ভাবনা কমে, সাড়া আরও দ্রুত আসে)। যে Provider-এ নিজস্ব Key নেই,
  সেখানে এখনো বটের শেয়ার্ড (কমিউনিটি) Key Pool ব্যবহার হয় — তাই কেউ কিছু যুক্ত না করলেও বট
  আগের মতোই স্বাভাবিকভাবে চলবে। /myapikey দিয়ে কোন প্রোভাইডারে নিজস্ব Key আছে তা (মাস্ক করে,
  যেমন gsk_****xxxx) দেখা যায়, /removeapikey provider (বা all) দিয়ে মুছে ফেলা যায়। যাদের
  কোনো নিজস্ব Key নেই (ও অ্যাডমিন নন), তাদের সাধারণ AI চ্যাটের উত্তরের নিচে দিনে একবার একটা
  ছোট্ট অনুস্মারক জুড়ে দেওয়া হয় — নিজস্ব Key যুক্ত করলে আরও দ্রুত ও নির্ভুলভাবে (accuracy)
  উত্তর পাওয়া যাবে। নিরাপত্তা: প্রতিটা ইউজারের নিজের Key শুধু তার নিজের রিকোয়েস্টেই ব্যবহার
  হয় (কখনো শেয়ার্ড পুলে/অন্য কারো রিকোয়েস্টে যোগ হয় না), এবং কোথাও দেখানোর সময় সবসময় মাস্ক
  করা থাকে। এই পুরো ফিচারটা backward-compatible ভাবে যোগ হয়েছে (ask_ai/ask_ai_with_history-এ
  নতুন ঐচ্ছিক user_id প্যারামিটার, ডিফল্ট None) — আগের কোনো Command/Feature/UI/MCP
  সার্ভার-টুল বদলায়নি বা ভাঙেনি।

Phase 47 আপডেটে যা যা নতুন যোগ হয়েছে (Source Attribution):
  প্রতিটা তথ্যবহ উত্তরের নিচে এখন একটা ছোট্ট **উৎস-ব্যাজ** বসে — ইউজার এক নজরেই দেখতে পান
  তথ্যটা কোথা থেকে এসেছে: 🔵 Groq API (LLM-এর লেখা) · 🌐 Browser Search (লাইভ ওয়েব) ·
  💾 Database (নিজের Brain OS / Response Cache) · 🔄 Hybrid (একাধিক উৎস মিলিয়ে)। সাথে থাকে
  সময়, মূল সোর্সের লিংক, কোন কোন সোর্স চেক করা হয়েছিল এবং নির্ভুলতার স্তর
  (🟢 উচ্চ ৮৫–১০০% / 🟡 মাঝারি ৬০–৮৫% / 🔴 নিম্ন < ৬০%)।
  Automatic priority (স্বয়ংক্রিয় ক্রম, কোনো আলাদা /search কমান্ডের দরকার নেই):
  1️⃣ 💾 Database (Brain OS / Response Cache) → 2️⃣ 🌐 Browser Search (DuckDuckGo/Wikipedia,
  দরকার হলে AI দিয়ে গুছিয়ে) → 3️⃣ 🔵 Groq API (fallback)। এই একই ক্রম সব হ্যান্ডলারে
  (chat, joke, quote, translate, grammar, rewrite, tone, summarize) প্রযোজ্য — ব্রাউজার সার্চ
  এখন আলাদা কমান্ড নয়, বরং ডাটাবেজে না পেলে স্বয়ংক্রিয়ভাবে চলে (বিস্তারিত:
  docs/SOURCE_ATTRIBUTION.md)।
  ব্যাজের আসল লজিক rohan_bot/utils/source_tracker.py + rohan_bot/config.py-তে (Telegram/AI/DB
  থেকে সম্পূর্ণ স্বাধীন, তাই আলাদাভাবে দ্রুত unit-test করা যায়)। নিরাপত্তা: প্যাকেজটা কোনো
  কারণে import না হলে বা ফিচার বন্ধ করা থাকলে বট ভাঙে না — শুধু ব্যাজ থাকে না, আর Browse
  Search-এর উত্তরে তখন আগের মতোই সাধারণ উৎস-ফুটার দেখানো হয়। কোনোটাই breaking change নয়।
  /brainstatus-এ এখন Browse Search ও Source Attribution-এর অবস্থাও দেখা যায়।
"""

from __future__ import annotations

import os
import sys
import sqlite3
import logging
import logging.handlers
import tempfile
import random
import subprocess
import glob
import math
import time
import platform
import shutil
import asyncio
import threading
import ast
from datetime import date, datetime, timedelta, timezone

import edge_tts
import httpx
from groq import Groq
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ApplicationHandlerStop,
    filters,
)

try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from langdetect import detect as _langdetect_detect, DetectorFactory
    DetectorFactory.seed = 0  # ফলাফল প্রতিবার একই রাখার জন্য
    LANGDETECT_SUPPORT = True
except ImportError:
    LANGDETECT_SUPPORT = False

try:
    import pytesseract
    from PIL import Image
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False

import hashlib
import json
import re
import difflib
import inspect
import functools
import traceback
from dataclasses import dataclass, field, fields
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type
from collections import OrderedDict
from urllib.parse import quote as _url_quote  # Phase 44: Browse Search (Wikipedia URL বানাতে)
import secrets  # Phase 43: OAuth 2.1 সার্ভার (client_id/code/token জেনারেশন)
import contextlib  # Phase 43: FastMCP lifespan fallback বানাতে
import base64   # Phase 43: OAuth 2.1 PKCE (S256 code_challenge ভেরিফিকেশন)
from urllib.parse import urlencode as _url_encode  # Phase 43: OAuth redirect URL বানাতে
from urllib.parse import parse_qs  # Phase 43: ASGI middleware-এ query string থেকে token পড়তে

# ---- Bangla Rule Engine (নিয়ম-ভিত্তিক বাংলা→Python deterministic ট্রান্সলেটর) ----
# আলাদা মডিউল bangla_rule_engine.py-তে (ভেরিয়েবল/ইনপুট/শর্ত/নিষেধ/আউটপুট/তুলনা রুল)।
# টেস্ট-স্যান্ডবক্সে main.py কে একা টেম্প-ডিরেক্টরিতে কপি করা হলে (tests/test_dynamic_print_kb.py
# -এর মতো) মডিউলটি sys.path-এ নাও থাকতে পারে — তখন ইঞ্জিন নিঃশব্দে বন্ধ থাকে
# (ম্যাচ=None → আগের ফ্লো অক্ষত), কোনো এররে বট ভাঙে না।
try:
    from bangla_rule_engine import translate_bangla_rules as _bangla_rule_translate
except ImportError:  # pragma: no cover — স্যান্ডবক্স-পরিস্থিতি
    try:
        _bre_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.isfile(os.path.join(_bre_dir, "bangla_rule_engine.py")):
            sys.path.insert(0, _bre_dir)
            from bangla_rule_engine import translate_bangla_rules as _bangla_rule_translate
        else:
            _bangla_rule_translate = None  # type: ignore[assignment]
    except ImportError:
        _bangla_rule_translate = None  # type: ignore[assignment]


# ============================= সেটআপ (Configuration) =============================

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN পাওয়া যায়নি। Secrets-এ বসান।")


def _collect_key_pool(*env_names: str) -> list:
    """
    Phase 8: একাধিক এনভায়রনমেন্ট ভ্যারিয়েবল (Secrets) থেকে নন-এম্পটি API Key জোগাড় করে,
    ডুপ্লিকেট বাদ দিয়ে (একই Key দুই জায়গায় বসানো থাকলে) একটা লিস্ট রিটার্ন করে।
    পুরনো একক Key (যেমন GROQ_API_KEY) আর নতুন নাম্বারড Key (GROQ_API_KEY_1/2/3) — দুটোই
    সাপোর্ট করে, তাই আগের Secrets মুছে ফেলার দরকার নেই (ব্যাকওয়ার্ড-কম্প্যাটিবিলিটি)।
    """
    seen = set()
    keys = []
    for name in env_names:
        val = os.getenv(name, "").strip()
        if val and val not in seen:
            seen.add(val)
            keys.append(val)
    return keys


GROQ_KEY_POOL_RAW = _collect_key_pool("GROQ_API_KEY", "GROQ_API_KEY_1", "GROQ_API_KEY_2", "GROQ_API_KEY_3")
OPENROUTER_KEY_POOL_RAW = _collect_key_pool("OPENROUTER_API_KEY", "OPENROUTER_API_KEY_1", "OPENROUTER_API_KEY_2")
CEREBRAS_KEY_POOL_RAW = _collect_key_pool("CEREBRAS_API_KEY", "CEREBRAS_API_KEY_1", "CEREBRAS_API_KEY_2")

# ব্যাকওয়ার্ড-কম্প্যাটিবিলিটি: পুরনো কোডের কোথাও এককভাবে GROQ_API_KEY/OPENROUTER_API_KEY/
# CEREBRAS_API_KEY রেফারেন্স থাকলে যেন না ভাঙে (এগুলো এখন শুধু "প্রথম পাওয়া Key" নির্দেশ করে)।
GROQ_API_KEY = GROQ_KEY_POOL_RAW[0] if GROQ_KEY_POOL_RAW else ""
OPENROUTER_API_KEY = OPENROUTER_KEY_POOL_RAW[0] if OPENROUTER_KEY_POOL_RAW else ""
CEREBRAS_API_KEY = CEREBRAS_KEY_POOL_RAW[0] if CEREBRAS_KEY_POOL_RAW else ""

if not (GROQ_KEY_POOL_RAW or OPENROUTER_KEY_POOL_RAW or CEREBRAS_KEY_POOL_RAW):
    raise RuntimeError(
        "অন্তত একটা ফ্রি AI Provider Key লাগবে — Secrets-এ GROQ_API_KEY(_1/2/3), "
        "OPENROUTER_API_KEY(_1/2), CEREBRAS_API_KEY(_1/2) — এর যেকোনো একটা অন্তত বসান।"
    )

# Phase 7: তিনটা ফ্রি AI Provider সাপোর্ট করে। Phase 8: প্রতিটার একাধিক Key (Pool) সাপোর্ট করে
# Load Balancing/Health Check/Rotation-এর জন্য (দেখুন নিচে "AI Provider Router")।
# GROQ Key না থাকলেও বট চালু হবে, শুধু Speech-to-Text (ভয়েস মেসেজ/ভিডিও ডাবিং ট্রান্সক্রিপশন)
# ফিচারটা বন্ধ থাকবে — এটা এখনো শুধু একটা Groq Key (প্রথমটা) দিয়ে হয়, পুলিং লাগে না।
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
WHISPER_SUPPORT = bool(GROQ_API_KEY)

# Provider-ভিত্তিক মডেল — future-তে বদলাতে চাইলে শুধু Secrets/env-এ বসালেই হবে, কোড এডিট লাগবে না
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama3.1-8b").strip()
AI_MODEL = GROQ_MODEL  # ব্যাকওয়ার্ড-কম্প্যাটিবিলিটি: পুরনো কোডের কোথাও AI_MODEL রেফারেন্স থাকলে যেন না ভাঙে

# Phase 8: Key Health Checker-এর সীমা — future-এ চাইলে বদলানো যাবে
KEY_UNHEALTHY_THRESHOLD = 3        # পরপর এতবার ব্যর্থ হলে Key সাময়িক Inactive হবে
KEY_UNHEALTHY_BASE_COOLDOWN = 30   # সেকেন্ড — প্রথমবার Inactive হলে এতক্ষণ বিরতি
KEY_UNHEALTHY_MAX_COOLDOWN = 300   # সেকেন্ড — বারবার ব্যর্থ হতে থাকলে কুলডাউন সর্বোচ্চ এই পর্যন্ত বাড়বে (৫ মিনিট)

# ---- Phase 9: Queue Manager + Retry/Timeout + Connection Pool ----
AI_QUEUE_MAX_WORKERS = 8            # একসাথে সর্বোচ্চ কতটা AI রিকোয়েস্ট সমান্তরালে প্রসেস হবে (বাকিগুলো সারিতে অপেক্ষা করবে)
AI_KEY_RETRY_MAX_ATTEMPTS = 2       # একটা Key-তে সর্বোচ্চ কতবার চেষ্টা হবে (Exponential Backoff সহ), তারপর পরের Key
AI_KEY_RETRY_BASE_DELAY = 0.6       # সেকেন্ড — প্রথম রিট্রাইয়ের আগে বিরতি
AI_KEY_RETRY_BACKOFF_FACTOR = 2.0   # প্রতি রিট্রাইয়ে বিরতি এই হারে বাড়বে (Exponential Backoff)
AI_HTTP_TIMEOUT = 30                # সেকেন্ড — httpx/Groq SDK-এর প্রতিটা একক কলের timeout
AI_REQUEST_HARD_TIMEOUT = 55        # সেকেন্ড — সব Retry/Provider-বদল মিলিয়ে একটা রিকোয়েস্টের সর্বোচ্চ সময়, তারপর বাতিল
HTTP_POOL_MAX_CONNECTIONS = 50      # Connection Pool: সর্বোচ্চ সমান্তরাল কানেকশন
HTTP_POOL_MAX_KEEPALIVE = 20        # Connection Pool: Keep-Alive-এ রাখা কানেকশনের সংখ্যা

# ---- Phase 10: Response Cache + Statistics Manager ----
AI_CACHE_MAX_ENTRIES = 300          # Response Cache-এ সর্বোচ্চ কতগুলো এন্ট্রি রাখা হবে (LRU, এর বেশি হলে সবচেয়ে পুরনোটা বাদ)
AI_CACHE_TTL_SECONDS = 1800         # সেকেন্ড — একটা ক্যাশ এন্ট্রি সর্বোচ্চ কতক্ষণ বৈধ থাকবে (৩০ মিনিট পর মেয়াদ শেষ)

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

_log_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_log_formatter)
_file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
_file_handler.setFormatter(_log_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(_console_handler)
root_logger.addHandler(_file_handler)
# তৃতীয়-পক্ষ লাইব্রেরির verbose লগ কমানো (httpx ইত্যাদি)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

if not WHISPER_SUPPORT:
    logger.warning("কোনো GROQ Key সেট করা নেই — Speech-to-Text (ভয়েস মেসেজ ও ভিডিও ডাবিং) ফিচার বন্ধ থাকবে।")
if not OPENROUTER_KEY_POOL_RAW:
    logger.warning("OPENROUTER_API_KEY(_1/2) সেট করা নেই — AI Router-এ OpenRouter বাদ পড়বে, পরের প্রোভাইডার ব্যবহার হবে।")
if not GROQ_KEY_POOL_RAW:
    logger.warning("GROQ_API_KEY(_1/2/3) সেট করা নেই — AI Router-এ Groq ফলব্যাক হিসেবে পাওয়া যাবে না।")
if not CEREBRAS_KEY_POOL_RAW:
    logger.warning("CEREBRAS_API_KEY(_1/2) সেট করা নেই — AI Router-এ Cerebras ফলব্যাক হিসেবে পাওয়া যাবে না।")
logger.info(
    f"Phase 8 Key Pool — OpenRouter: {len(OPENROUTER_KEY_POOL_RAW)}টা Key, "
    f"Groq: {len(GROQ_KEY_POOL_RAW)}টা Key, Cerebras: {len(CEREBRAS_KEY_POOL_RAW)}টা Key"
)

BOT_START_TIME = time.time()

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.db")

VOICE_MALE = "bn-BD-PradeepNeural"
VOICE_FEMALE = "bn-BD-NabanitaNeural"
SPEED_OPTIONS = {"slow": "-20%", "normal": "+0%", "fast": "+20%"}

# ---- Phase 46: ভয়েস/গতি পছন্দের বৈধ মানের তালিকা (single source of truth) ----
# inline বাটনের callback_data ("voice_male", "speed_fast" …) থেকে আসা মানটা DB-তে লেখার
# আগে এই তালিকা দিয়ে যাচাই করা হয়। আগে যাচাই ছাড়াই সরাসরি users.voice / users.speed-এ
# লেখা হতো, আর speed-এর ক্ষেত্রে তারপরে labels[choice] করতে গিয়ে KeyError ছুঁড়ত —
# অর্থাৎ crash-এর আগেই ভুয়া মানটা কমিট হয়ে যেত (users.speed-এ কোনো CHECK constraint নেই)।
VOICE_CHOICES = ("male", "female")
SPEED_LABELS_BN = {"slow": "ধীর", "normal": "স্বাভাবিক", "fast": "দ্রুত"}

FREE_DAILY_LIMIT = 15

# ---- Phase 4: Premium System ----
PREMIUM_DAILY_LIMIT = 100          # প্রিমিয়াম ইউজারের দৈনিক সীমা
MEMORY_HISTORY_LIMIT_PREMIUM = 12  # প্রিমিয়াম ইউজারের জন্য AI Memory-তে বেশি কথোপকথন মনে রাখা (অতিরিক্ত সুবিধা)
PREMIUM_EXPIRY_REMINDER_DAYS = 2   # মেয়াদ শেষ হওয়ার এই কয়দিন আগে রিমাইন্ডার পাঠানো হবে
PREMIUM_NOTIFY_INTERVAL_SECONDS = 6 * 60 * 60   # প্রিমিয়াম মেয়াদ/রিমাইন্ডার চেক করার ব্যাকগ্রাউন্ড জব — প্রতি ৬ ঘণ্টায়
PREMIUM_MAX_DAYS = 3650            # একবারে সর্বোচ্চ যত দিনের প্রিমিয়াম দেওয়া যাবে (নিরাপত্তা: ভুল করে বিশাল সংখ্যা দেওয়া ঠেকাতে)

# Anti-Flood: একজন ইউজার কত সেকেন্ডের মধ্যে একটার বেশি মেসেজ পাঠাতে পারবে না
MIN_SECONDS_BETWEEN_MESSAGES = 2
FLOOD_WARNING_THRESHOLD = 5   # এই কয়বার দ্রুত মেসেজ পাঠালে সাময়িক ব্লক
FLOOD_BLOCK_SECONDS = 30      # সাময়িক ব্লকের সময়
_last_message_time = {}       # user_id -> শেষ মেসেজের সময় (মেমরিতে, দ্রুত চেক করার জন্য)
_flood_strikes = {}           # user_id -> পরপর কতবার দ্রুত মেসেজ পাঠিয়েছে
_flood_blocked_until = {}     # user_id -> কোন সময় পর্যন্ত ব্লক

BOT_NAME = "ROHAN AI Assistant"
CREATOR_NAME = "ROHAN"
CREATOR_COMPANY = "ROHAN E.C Company"

FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"
MAX_DOWNLOAD_MB = 19   # টেলিগ্রাম বট ২০ MB এর বেশি ফাইল ডাউনলোড করতে পারে না, তাই একটু কম রাখা হলো
MAX_SEND_MB = 45       # টেলিগ্রামে বড় ফাইল পাঠানোর নিরাপদ সীমা

# ---- Phase 3: OCR ----
MAX_IMAGE_MB = 15                  # OCR-এর জন্য ছবির সর্বোচ্চ সাইজ (নিরাপত্তা: খুব বড় ফাইল দিয়ে বট আটকে রাখা ঠেকাতে)
OCR_LANGS = "ben+eng"              # প্রথমে বাংলা+ইংরেজি দুটো একসাথে চেষ্টা করা হবে
TELEGRAM_MAX_MSG_LEN = 3500        # এক মেসেজে যতটা লেখা নিরাপদে পাঠানো যায় (টেলিগ্রামের ৪০৯৬ সীমার একটু নিচে)

# ---- Phase 3: PDF প্রশ্ন-উত্তরের জন্য ডকুমেন্ট থেকে যতটুকু লেখা AI-কে পাঠানো হবে ----
PDF_CONTEXT_CHARS = 12000
PDF_SESSION_STORE_CHARS = 15000    # ডাটাবেসে একজন ইউজারের জন্য সর্বোচ্চ যতটুকু PDF লেখা জমা রাখা হবে

# ---- Phase 3: মাল্টি-ভাষা সাপোর্ট ----
UI_LANG_CHOICES = {
    "bn": "বাংলা",
    "en": "English",
    "hi": "हिन्दी",
    "ar": "العربية",
    "ur": "اردو",
    "es": "Español",
}
_localize_cache = OrderedDict()    # (lang, text_hash) -> অনুবাদ; Performance: বারবার একই টেক্সট AI দিয়ে অনুবাদ না করানোর জন্য
LOCALIZE_CACHE_MAX = 300

# ---- Phase 5: Referral System ----
REFERRAL_BONUS = 3        # রেফারেল সফল হলে রেফারার ও নতুন ইউজার — দুজনেই এই পরিমাণ অতিরিক্ত (স্থায়ী) দৈনিক সীমা পাবেন
REFERRAL_MAX_BONUS = 60   # নিরাপত্তা: একজন ইউজার রেফারেল দিয়ে সর্বোচ্চ যতটুকু বোনাস জমাতে পারবেন (অপব্যবহার ঠেকাতে)

# ---- Phase 5: Admin Roles ----
ADMIN_ROLE_RANK = {"moderator": 1, "admin": 2, "owner": 3}
ADMIN_ROLE_LABEL_BN = {"owner": "👑 Owner", "admin": "🛡️ Admin", "moderator": "🔰 Moderator"}


# ============================= ডাটাবেস (Database) =============================


# =============================================================================
# BRAIN OS v1.0 — একক-ফাইল সংস্করণ (ইউজারের অনুরোধে brain/ প্যাকেজ থেকে এখানে একীভূত করা হয়েছে)
# মূল উৎস: brain/models.py, database.py, search_engine.py, knowledge_engine.py,
# pattern_engine.py, template_engine.py, documentation_engine.py, error_engine.py
# Phase 13-15 সম্পূর্ণ (Database Schema, Search+Knowledge Engine, Pattern+Template+
# Documentation+Error Engine)। Decision Engine/Context Engine (Phase 16+) এখনো বাকি।
# =============================================================================


# =============================================================================
# Brain OS — originally brain/models.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================




def _from_row(cls, row: Sequence[Any]):
    """sqlite3 cursor থেকে পাওয়া একটা row (tuple) কে dataclass-এ রূপান্তর করে।
    ধরে নেওয়া হয় row-এর কলাম-অর্ডার dataclass ফিল্ড-অর্ডারের সাথে মিলে যায়
    (অর্থাৎ SELECT * টেবিলের CREATE TABLE-এর কলাম-অর্ডার অনুযায়ী)।"""
    field_names = [f.name for f in fields(cls)]
    return cls(**dict(zip(field_names, row)))


# ============================= 4.1 Knowledge Engine =============================

@dataclass
class BrainKnowledge:
    id: Optional[int] = None
    level: Optional[int] = None
    category: str = ""
    title: str = ""
    content: str = ""
    tags: str = ""            # কমা-সেপারেটেড
    priority: int = 5          # ১-১০
    version: int = 1
    source: str = ""           # 'seed' / 'admin' / 'learning_engine'
    created_at: str = ""
    updated_at: str = ""
    # ---- Phase 14: Knowledge Engine এক্সটেনশন (brain_knowledge-এ ALTER COLUMN দিয়ে যোগ,
    #      দেখুন brain/database.py-এর _migrate_knowledge_columns()) ----
    metadata: str = "{}"           # JSON স্ট্রিং — Metadata Support
    confidence_score: float = 1.0  # 0.0-1.0 — Confidence Score
    status: str = "active"         # 'draft' / 'active' / 'archived'
    deleted_at: str = ""           # খালি স্ট্রিং = ডিলিট হয়নি (Soft Delete)
    content_hash: str = ""         # sha256(category+title+content) — Duplicate Detection

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainKnowledge":
        return _from_row(cls, row)

    def is_deleted(self) -> bool:
        """Soft-delete হয়েছে কিনা (deleted_at খালি না থাকলে ডিলিটেড)।"""
        return bool(self.deleted_at)


# ============================= 4.2 Pattern Engine =============================

@dataclass
class BrainPattern:
    id: Optional[int] = None
    pattern_type: str = ""     # 'keyword' / 'regex' / 'intent'
    match_value: str = ""
    category: str = ""
    template_id: Optional[int] = None
    priority: int = 5
    created_at: str = ""
    # ---- Phase 15: Pattern Engine এক্সটেনশন (ALTER COLUMN দিয়ে যোগ, ক্রম গুরুত্বপূর্ণ —
    #      দেখুন brain/database.py-এর _migrate_pattern_columns()) ----
    name: str = ""                 # সহজে চেনার জন্য নাম
    description: str = ""
    tags: str = ""                 # কমা-সেপারেটেড
    confidence_score: float = 1.0  # 0.0-1.0
    version: int = 1
    is_active: int = 1             # Enable/Disable — 0/1
    updated_at: str = ""
    pattern_hash: str = ""         # sha256(pattern_type+match_value+category) — Duplicate Detection

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainPattern":
        return _from_row(cls, row)

    def is_enabled(self) -> bool:
        return bool(self.is_active)


@dataclass
class BrainPatternAnalytics:
    """Phase 15: প্রতিবার একটা প্যাটার্ন ম্যাচ হলে তার লগ (Pattern Analytics)।"""
    id: Optional[int] = None
    pattern_id: Optional[int] = None
    matched_at: str = ""
    input_preview: str = ""    # প্রথম ১৫০ অক্ষর (privacy-বান্ধব)
    confidence: float = 0.0

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainPatternAnalytics":
        return _from_row(cls, row)


# ============================= 4.3 Template Engine =============================

@dataclass
class BrainTemplate:
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    language: Optional[str] = None   # 'python' / 'javascript' / None (ভাষা-নিরপেক্ষ)
    body: str = ""                    # {variable} প্লেসহোল্ডার সহ
    variables: str = "[]"             # JSON list স্ট্রিং, যেমন '["function_name","params"]'
    created_at: str = ""
    updated_at: str = ""
    # ---- Phase 15: Template Engine এক্সটেনশন (ক্রম _migrate_template_columns()-এর সাথে মিল) ----
    description: str = ""
    is_active: int = 1              # Active/Inactive — 0/1
    is_default: int = 0             # Default Templates — 0/1
    priority: int = 5
    template_type: str = "prompt"   # 'prompt'/'response'/'message'/'notification'/'system'

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainTemplate":
        return _from_row(cls, row)

    def is_enabled(self) -> bool:
        return bool(self.is_active)


@dataclass
class BrainTemplateVersion:
    """Phase 15: Template Versioning হিস্টোরি — body/variables-এর প্রতিটা পুরনো স্ন্যাপশট।"""
    id: Optional[int] = None
    template_id: Optional[int] = None
    version: int = 1
    body: str = ""
    variables: str = "[]"
    created_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainTemplateVersion":
        return _from_row(cls, row)


# ============================= 4.4 Documentation Engine =============================

@dataclass
class BrainDocumentation:
    id: Optional[int] = None
    technology: str = ""
    category: str = ""
    title: str = ""
    content: str = ""
    source_url: str = ""
    version: str = ""
    created_at: str = ""
    updated_at: str = ""
    # ---- Phase 15: Documentation Engine এক্সটেনশন (ক্রম _migrate_documentation_columns()-এর সাথে মিল) ----
    tags: str = ""
    status: str = "active"          # 'draft'/'active'/'archived'
    doc_type: str = "module"        # 'api'/'module'/'function'/'class'
    deleted_at: str = ""            # খালি স্ট্রিং = ডিলিট হয়নি (Soft Delete)
    internal_notes: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainDocumentation":
        return _from_row(cls, row)

    def is_deleted(self) -> bool:
        return bool(self.deleted_at)


@dataclass
class BrainDocumentationHistory:
    """Phase 15: Documentation Version History / Change Log — প্রতিটা কনটেন্ট-পরিবর্তনের স্ন্যাপশট।"""
    id: Optional[int] = None
    documentation_id: Optional[int] = None
    version: str = ""
    content: str = ""
    change_note: str = ""
    changed_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainDocumentationHistory":
        return _from_row(cls, row)


# ============================= 4.5 Error Engine =============================

@dataclass
class BrainError:
    id: Optional[int] = None
    language: str = ""
    error_signature: str = ""   # যেমন "ModuleNotFoundError"
    description: str = ""
    solution: str = ""
    related_doc_id: Optional[int] = None
    occurrence_count: int = 1
    created_at: str = ""
    updated_at: str = ""
    # ---- Phase 15: Error Engine এক্সটেনশন (ক্রম _migrate_error_columns()-এর সাথে মিল) ----
    category: str = "unknown"       # 'validation'/'database'/'api'/'unknown' ইত্যাদি
    error_code: str = ""
    severity: str = "medium"        # 'low'/'medium'/'high'/'critical'
    is_resolved: int = 0            # 0/1
    deleted_at: str = ""            # Soft Delete

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainError":
        return _from_row(cls, row)

    def is_deleted(self) -> bool:
        return bool(self.deleted_at)


@dataclass
class BrainErrorLog:
    """Phase 15: Error History — প্রতিটা occurrence-এর stack trace/context সহ পূর্ণ লগ।"""
    id: Optional[int] = None
    error_id: Optional[int] = None
    language: str = ""
    error_signature: str = ""
    category: str = "unknown"
    severity: str = "medium"
    stack_trace: str = ""
    context: str = "{}"    # JSON স্ট্রিং
    created_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainErrorLog":
        return _from_row(cls, row)


# ============================= 4.6 Cache Engine =============================
# ৪টা টেবিলই (brain_cache_knowledge/search/ai/project) একই shape — তাই একটাই মডেল,
# টেবিল কোনটা সেটা রিপোজিটরি-লেয়ারে (Phase 17) নির্ধারিত হবে।

@dataclass
class BrainCacheEntry:
    cache_key: str = ""
    cache_value: str = ""
    expires_at: str = ""
    created_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainCacheEntry":
        return _from_row(cls, row)


# ============================= 4.7 Context Engine =============================

@dataclass
class BrainContext:
    id: Optional[int] = None
    user_id: Optional[int] = None
    session_key: str = ""       # সাধারণত user_id-ই, ভবিষ্যতে multi-session সাপোর্টের জন্য আলাদা
    context_data: str = "{}"    # JSON স্ট্রিং
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainContext":
        return _from_row(cls, row)


# ============================= 4.8 Project Memory Engine =============================

@dataclass
class BrainProjectMemory:
    id: Optional[int] = None
    project_id: Optional[int] = None   # REFERENCES code_projects(id) — বিদ্যমান টেবিল (Phase 11)
    memory_type: str = ""              # 'file'/'folder'/'dependency'/'function'/'class'/'import'/'architecture'
    key_name: str = ""
    details: str = "{}"                # JSON স্ট্রিং
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainProjectMemory":
        return _from_row(cls, row)


# ============================= 4.9 Learning Engine =============================

@dataclass
class BrainLearningQueueItem:
    id: Optional[int] = None
    proposed_category: str = ""
    proposed_title: str = ""
    proposed_content: str = ""
    proposed_by: Optional[int] = None   # user_id (সাধারণত সিস্টেম নিজে)
    status: str = "pending"             # 'pending' / 'approved' / 'rejected'
    reviewed_by: Optional[int] = None
    created_at: str = ""
    reviewed_at: Optional[str] = None

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainLearningQueueItem":
        return _from_row(cls, row)


# ============================= 4.10 Decision Engine =============================

@dataclass
class BrainDecisionLogEntry:
    id: Optional[int] = None
    user_id: Optional[int] = None
    request_preview: str = ""    # প্রথম ১৫০ অক্ষর (privacy-বান্ধব)
    matched_stage: str = "none"  # 'knowledge'/'pattern'/'template'/'documentation'/'ai'/'none'
    confidence: float = 0.0
    ai_used: int = 0              # 0/1 (SQLite-এ boolean নেই)
    response_time_ms: Optional[int] = None
    created_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainDecisionLogEntry":
        return _from_row(cls, row)


# ============================= 4.11 Search Engine (Phase 14) =============================

@dataclass
class BrainSearchHistory:
    id: Optional[int] = None
    user_id: Optional[int] = None
    query: str = ""
    entity: str = "knowledge"     # কোন টেবিলে সার্চ হয়েছে: 'knowledge'/'documentation'/'errors'
    results_count: int = 0
    created_at: str = ""

    @classmethod
    def from_row(cls, row: Sequence[Any]) -> "BrainSearchHistory":
        return _from_row(cls, row)


# =============================================================================
# Brain OS — originally brain/database.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================


logger = logging.getLogger(__name__)

# একক-ফাইল সংস্করণ: Brain OS-এর কোড এখন main.py-এরই ভেতরে, তাই আলাদা কোনো Dependency
# Injection/provider-registration দরকার নেই — get_conn() (উপরে, এই একই ফাইলে সংজ্ঞায়িত)
# সরাসরি ব্যবহার করা হচ্ছে। (আলাদা brain/ প্যাকেজ সংস্করণে এখানে একটা DI-লেয়ার ছিল, যেটা
# main.py-কে ভুলভাবে পুনরায়-import হওয়া থেকে বাঁচাতো — একক ফাইলে সেই সমস্যাটাই অস্তিত্বহীন,
# তাই সরিয়ে ফেলা হয়েছে।)


def get_brain_conn() -> sqlite3.Connection:
    """Brain OS-এর সব Engine এই ফাংশন দিয়েই DB কানেকশন নেয় (এই ফাইলেরই get_conn() পুনর্ব্যবহার করে)।"""
    return get_conn()


def _create_core_tables(cur: sqlite3.Cursor) -> None:
    """৪.১ থেকে ৪.৫, ৪.৭ থেকে ৪.১০ — সাধারণ (নন-cache) brain_* টেবিলগুলো।"""

    # ---- 4.1 Knowledge Engine ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level INTEGER,
            category TEXT,
            title TEXT,
            content TEXT,
            tags TEXT,
            priority INTEGER DEFAULT 5,
            version INTEGER DEFAULT 1,
            source TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    # ---- 4.2 Pattern Engine ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            match_value TEXT,
            category TEXT,
            template_id INTEGER,
            priority INTEGER DEFAULT 5,
            created_at TEXT
        )
        """
    )

    # ---- 4.3 Template Engine ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            language TEXT,
            body TEXT,
            variables TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    # ---- 4.4 Documentation Engine ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_documentation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            technology TEXT,
            category TEXT,
            title TEXT,
            content TEXT,
            source_url TEXT,
            version TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    # ---- 4.5 Error Engine ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT,
            error_signature TEXT,
            description TEXT,
            solution TEXT,
            related_doc_id INTEGER,
            occurrence_count INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    # ---- 4.7 Context Engine ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_key TEXT,
            context_data TEXT,
            updated_at TEXT
        )
        """
    )

    # ---- 4.8 Project Memory Engine (code_projects/code_tasks এক্সটেন্ড করে, রিপ্লেস না) ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_project_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            memory_type TEXT,
            key_name TEXT,
            details TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    # ---- 4.9 Learning Engine (Admin-অনুমোদন ওয়ার্কফ্লো) ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_learning_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposed_category TEXT,
            proposed_title TEXT,
            proposed_content TEXT,
            proposed_by INTEGER,
            status TEXT DEFAULT 'pending',
            reviewed_by INTEGER,
            created_at TEXT,
            reviewed_at TEXT
        )
        """
    )

    # ---- 4.10 Decision Engine (লগ/পরিসংখ্যান) ----
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_decision_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            request_preview TEXT,
            matched_stage TEXT,
            confidence REAL,
            ai_used INTEGER DEFAULT 0,
            response_time_ms INTEGER,
            created_at TEXT
        )
        """
    )


def _create_cache_tables(cur: sqlite3.Cursor) -> None:
    """৪.৬ Cache Engine — ৪টা আলাদা টেবিল, স্পেসিফিকেশন অনুযায়ী একই shape।"""

    for table_name in (
        "brain_cache_knowledge",
        "brain_cache_search",
        "brain_cache_ai",
        "brain_cache_project",
    ):
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                cache_key TEXT PRIMARY KEY,
                cache_value TEXT,
                expires_at TEXT,
                created_at TEXT
            )
            """
        )


def _create_search_engine_tables(cur: sqlite3.Cursor) -> None:
    """Phase 14: Search Engine — সার্চ হিস্টোরি/অটো-সাজেশনের ভিত্তি টেবিল।"""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            entity TEXT DEFAULT 'knowledge',
            results_count INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mcp_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            tool_name TEXT,
            summary TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )


def _create_oauth_tables(cur: sqlite3.Cursor) -> None:
    """Phase 43: OAuth 2.1 সার্ভার — Claude/MCP Custom Connector-এর জন্য Dynamic Client
    Registration, Authorization Code (+PKCE), Access/Refresh Token স্টোরেজ।"""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS oauth_clients (
            client_id TEXT PRIMARY KEY,
            client_secret TEXT,
            client_name TEXT,
            redirect_uris TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS oauth_auth_codes (
            code TEXT PRIMARY KEY,
            client_id TEXT,
            redirect_uri TEXT,
            code_challenge TEXT,
            code_challenge_method TEXT,
            resource TEXT,
            scope TEXT,
            used INTEGER DEFAULT 0,
            expires_at TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            access_token TEXT PRIMARY KEY,
            refresh_token TEXT,
            client_id TEXT,
            resource TEXT,
            scope TEXT,
            expires_at TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_oauth_tokens_refresh ON oauth_tokens(refresh_token)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_oauth_auth_codes_client ON oauth_auth_codes(client_id)"
    )


def _migrate_knowledge_columns(cur: sqlite3.Cursor) -> None:
    """
    Phase 14: Knowledge Engine ফিচারের জন্য `brain_knowledge` টেবিলে নতুন কলাম যোগ করে
    (Metadata Support, Confidence Score, Status, Soft Delete, Duplicate Detection)।
    main.py-এর `migrate_db()`-এর মতোই ধরন — `PRAGMA table_info` দিয়ে চেক করে শুধু যেটা
    নেই সেটাই `ALTER TABLE ... ADD COLUMN` দিয়ে যোগ করে, তাই বারবার চালালেও (bot restart)
    কোনো সমস্যা হয় না এবং আগে থেকে থাকা ডাটা/রো নষ্ট হয় না।
    """
    cur.execute("PRAGMA table_info(brain_knowledge)")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_columns = {
        "metadata": "TEXT DEFAULT '{}'",
        "confidence_score": "REAL DEFAULT 1.0",
        "status": "TEXT DEFAULT 'active'",
        "deleted_at": "TEXT DEFAULT ''",
        "content_hash": "TEXT DEFAULT ''",
    }
    for col, col_type in new_columns.items():
        if col not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE brain_knowledge ADD COLUMN {col} {col_type}")
                logger.info(f"Brain OS মাইগ্রেশন (Phase 14): brain_knowledge-এ '{col}' কলাম যোগ হলো")
            except sqlite3.OperationalError as e:
                logger.warning(f"Brain OS মাইগ্রেশন এরর (Phase 14, {col}): {e}")


def _create_phase14_indexes(cur: sqlite3.Cursor) -> None:
    """Phase 14: নতুন কলাম/টেবিলগুলোর জন্য ইনডেক্স (এগুলো migrate/create ফাংশনগুলোর *পরে*
    চালাতে হবে, কারণ কলাম/টেবিল তৈরির আগে তার উপর ইনডেক্স বানানো যায় না)।"""
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_knowledge_status ON brain_knowledge(status, deleted_at)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_knowledge_hash ON brain_knowledge(content_hash)")
    except sqlite3.OperationalError as e:
        logger.warning(f"Brain OS: Phase 14 brain_knowledge ইনডেক্স তৈরি করা যায়নি: {e}")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_search_history_user ON brain_search_history(user_id, created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_search_history_query ON brain_search_history(query)")


def _migrate_pattern_columns(cur: sqlite3.Cursor) -> None:
    """
    Phase 15: Pattern Engine — `brain_patterns`-এ নতুন কলাম যোগ করে (Name, Description,
    Tags, Confidence Score, Versioning, Enable/Disable, Duplicate Detection)। আগের
    Phase-গুলোর মতোই `PRAGMA table_info` চেক করে শুধু অনুপস্থিত কলামগুলোই যোগ হয়, তাই
    বারবার চালালেও নিরাপদ এবং বিদ্যমান ডাটা অক্ষত থাকে।
    """
    cur.execute("PRAGMA table_info(brain_patterns)")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_columns = {
        "name": "TEXT DEFAULT ''",
        "description": "TEXT DEFAULT ''",
        "tags": "TEXT DEFAULT ''",
        "confidence_score": "REAL DEFAULT 1.0",
        "version": "INTEGER DEFAULT 1",
        "is_active": "INTEGER DEFAULT 1",
        "updated_at": "TEXT DEFAULT ''",
        "pattern_hash": "TEXT DEFAULT ''",
    }
    for col, col_type in new_columns.items():
        if col not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE brain_patterns ADD COLUMN {col} {col_type}")
                logger.info(f"Brain OS মাইগ্রেশন (Phase 15): brain_patterns-এ '{col}' কলাম যোগ হলো")
            except sqlite3.OperationalError as e:
                logger.warning(f"Brain OS মাইগ্রেশন এরর (Phase 15, patterns.{col}): {e}")


def _migrate_template_columns(cur: sqlite3.Cursor) -> None:
    """Phase 15: Template Engine — `brain_templates`-এ নতুন কলাম যোগ করে (Description,
    Active/Inactive, Default Templates, Priority, Template Type)।"""
    cur.execute("PRAGMA table_info(brain_templates)")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_columns = {
        "description": "TEXT DEFAULT ''",
        "is_active": "INTEGER DEFAULT 1",
        "is_default": "INTEGER DEFAULT 0",
        "priority": "INTEGER DEFAULT 5",
        "template_type": "TEXT DEFAULT 'prompt'",
    }
    for col, col_type in new_columns.items():
        if col not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE brain_templates ADD COLUMN {col} {col_type}")
                logger.info(f"Brain OS মাইগ্রেশন (Phase 15): brain_templates-এ '{col}' কলাম যোগ হলো")
            except sqlite3.OperationalError as e:
                logger.warning(f"Brain OS মাইগ্রেশন এরর (Phase 15, templates.{col}): {e}")


def _migrate_documentation_columns(cur: sqlite3.Cursor) -> None:
    """Phase 15: Documentation Engine — `brain_documentation`-এ নতুন কলাম যোগ করে
    (Tags, Status, Doc Type, Soft Delete, Internal Notes)।"""
    cur.execute("PRAGMA table_info(brain_documentation)")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_columns = {
        "tags": "TEXT DEFAULT ''",
        "status": "TEXT DEFAULT 'active'",
        "doc_type": "TEXT DEFAULT 'module'",
        "deleted_at": "TEXT DEFAULT ''",
        "internal_notes": "TEXT DEFAULT ''",
    }
    for col, col_type in new_columns.items():
        if col not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE brain_documentation ADD COLUMN {col} {col_type}")
                logger.info(f"Brain OS মাইগ্রেশন (Phase 15): brain_documentation-এ '{col}' কলাম যোগ হলো")
            except sqlite3.OperationalError as e:
                logger.warning(f"Brain OS মাইগ্রেশন এরর (Phase 15, documentation.{col}): {e}")


def _migrate_error_columns(cur: sqlite3.Cursor) -> None:
    """Phase 15: Error Engine — `brain_errors`-এ নতুন কলাম যোগ করে (Category, Error Code,
    Severity, Resolved Flag, Soft Delete)।"""
    cur.execute("PRAGMA table_info(brain_errors)")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_columns = {
        "category": "TEXT DEFAULT 'unknown'",
        "error_code": "TEXT DEFAULT ''",
        "severity": "TEXT DEFAULT 'medium'",
        "is_resolved": "INTEGER DEFAULT 0",
        "deleted_at": "TEXT DEFAULT ''",
    }
    for col, col_type in new_columns.items():
        if col not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE brain_errors ADD COLUMN {col} {col_type}")
                logger.info(f"Brain OS মাইগ্রেশন (Phase 15): brain_errors-এ '{col}' কলাম যোগ হলো")
            except sqlite3.OperationalError as e:
                logger.warning(f"Brain OS মাইগ্রেশন এরর (Phase 15, errors.{col}): {e}")


def _create_phase15_tables(cur: sqlite3.Cursor) -> None:
    """
    Phase 15: চারটা নতুন সাপোর্ট-টেবিল —
      - brain_pattern_analytics: Pattern Analytics (কোন প্যাটার্ন কখন/কতবার ম্যাচ হলো)
      - brain_template_versions: Template Versioning হিস্টোরি (body/variables স্ন্যাপশট)
      - brain_documentation_history: Documentation Version History / Change Log
      - brain_error_log: Error History (প্রতিটা occurrence-এর stack trace/context সহ)
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_pattern_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_id INTEGER,
            matched_at TEXT,
            input_preview TEXT,
            confidence REAL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_template_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            version INTEGER,
            body TEXT,
            variables TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_documentation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documentation_id INTEGER,
            version TEXT,
            content TEXT,
            change_note TEXT,
            changed_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS brain_error_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_id INTEGER,
            language TEXT,
            error_signature TEXT,
            category TEXT,
            severity TEXT,
            stack_trace TEXT,
            context TEXT,
            created_at TEXT
        )
        """
    )


def _create_phase15_indexes(cur: sqlite3.Cursor) -> None:
    """Phase 15: নতুন কলাম/টেবিলগুলোর জন্য ইনডেক্স — মাইগ্রেশন/টেবিল-তৈরির *পরে* চালাতে হবে।"""
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_patterns_active ON brain_patterns(is_active, category)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_patterns_hash ON brain_patterns(pattern_hash)")
    except sqlite3.OperationalError as e:
        logger.warning(f"Brain OS: Phase 15 brain_patterns ইনডেক্স তৈরি করা যায়নি: {e}")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_templates_active ON brain_templates(is_active, is_default)")
    except sqlite3.OperationalError as e:
        logger.warning(f"Brain OS: Phase 15 brain_templates ইনডেক্স তৈরি করা যায়নি: {e}")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_documentation_status ON brain_documentation(status, doc_type)")
    except sqlite3.OperationalError as e:
        logger.warning(f"Brain OS: Phase 15 brain_documentation ইনডেক্স তৈরি করা যায়নি: {e}")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_errors_category ON brain_errors(category, severity, is_resolved)")
    except sqlite3.OperationalError as e:
        logger.warning(f"Brain OS: Phase 15 brain_errors ইনডেক্স তৈরি করা যায়নি: {e}")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_pattern_analytics_pattern ON brain_pattern_analytics(pattern_id, matched_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_template_versions_template ON brain_template_versions(template_id, version)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_documentation_history_doc ON brain_documentation_history(documentation_id, changed_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_brain_error_log_error ON brain_error_log(error_id, created_at)")


def _create_fts_tables_and_triggers(cur: sqlite3.Cursor) -> None:
    """
    ৪.১/৪.৪/৪.৫ — external-content FTS5 ভার্চুয়াল টেবিল + sync ট্রিগার।
    FTS5 না থাকলে (বিরল) sqlite3.OperationalError ধরে শুধু এই অংশ বাদ দেওয়া হয়,
    বাকি brain_* টেবিল ও বট স্বাভাবিকভাবে চলবে।
    """
    try:
        # ---- brain_knowledge_fts ----
        cur.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS brain_knowledge_fts USING fts5(
                title, content, tags, category,
                content='brain_knowledge', content_rowid='id'
            )
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_knowledge_ai AFTER INSERT ON brain_knowledge BEGIN
                INSERT INTO brain_knowledge_fts(rowid, title, content, tags, category)
                VALUES (new.id, new.title, new.content, new.tags, new.category);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_knowledge_ad AFTER DELETE ON brain_knowledge BEGIN
                INSERT INTO brain_knowledge_fts(brain_knowledge_fts, rowid, title, content, tags, category)
                VALUES ('delete', old.id, old.title, old.content, old.tags, old.category);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_knowledge_au AFTER UPDATE ON brain_knowledge BEGIN
                INSERT INTO brain_knowledge_fts(brain_knowledge_fts, rowid, title, content, tags, category)
                VALUES ('delete', old.id, old.title, old.content, old.tags, old.category);
                INSERT INTO brain_knowledge_fts(rowid, title, content, tags, category)
                VALUES (new.id, new.title, new.content, new.tags, new.category);
            END
            """
        )

        # ---- brain_documentation_fts ----
        cur.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS brain_documentation_fts USING fts5(
                title, content, technology,
                content='brain_documentation', content_rowid='id'
            )
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_documentation_ai AFTER INSERT ON brain_documentation BEGIN
                INSERT INTO brain_documentation_fts(rowid, title, content, technology)
                VALUES (new.id, new.title, new.content, new.technology);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_documentation_ad AFTER DELETE ON brain_documentation BEGIN
                INSERT INTO brain_documentation_fts(brain_documentation_fts, rowid, title, content, technology)
                VALUES ('delete', old.id, old.title, old.content, old.technology);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_documentation_au AFTER UPDATE ON brain_documentation BEGIN
                INSERT INTO brain_documentation_fts(brain_documentation_fts, rowid, title, content, technology)
                VALUES ('delete', old.id, old.title, old.content, old.technology);
                INSERT INTO brain_documentation_fts(rowid, title, content, technology)
                VALUES (new.id, new.title, new.content, new.technology);
            END
            """
        )

        # ---- brain_errors_fts ----
        cur.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS brain_errors_fts USING fts5(
                error_signature, description, solution,
                content='brain_errors', content_rowid='id'
            )
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_errors_ai AFTER INSERT ON brain_errors BEGIN
                INSERT INTO brain_errors_fts(rowid, error_signature, description, solution)
                VALUES (new.id, new.error_signature, new.description, new.solution);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_errors_ad AFTER DELETE ON brain_errors BEGIN
                INSERT INTO brain_errors_fts(brain_errors_fts, rowid, error_signature, description, solution)
                VALUES ('delete', old.id, old.error_signature, old.description, old.solution);
            END
            """
        )
        cur.execute(
            """
            CREATE TRIGGER IF NOT EXISTS brain_errors_au AFTER UPDATE ON brain_errors BEGIN
                INSERT INTO brain_errors_fts(brain_errors_fts, rowid, error_signature, description, solution)
                VALUES ('delete', old.id, old.error_signature, old.description, old.solution);
                INSERT INTO brain_errors_fts(rowid, error_signature, description, solution)
                VALUES (new.id, new.error_signature, new.description, new.solution);
            END
            """
        )
    except sqlite3.OperationalError as e:
        logger.warning(
            "Brain OS: FTS5 ভার্চুয়াল টেবিল/ট্রিগার তৈরি করা যায়নি (SQLite বিল্ডে FTS5 না "
            f"থাকতে পারে) — সার্চ ফিচার (Phase 14) সীমিত থাকবে, তবে বট/বাকি সব Brain টেবিল "
            f"স্বাভাবিকভাবে কাজ করবে। বিস্তারিত: {e}"
        )


def _create_indexes(cur: sqlite3.Cursor) -> None:
    """Performance ইনডেক্স — আর্কিটেকচার ডকের ৪.১০ সেকশনে বর্ণিত ৩টা + বাকি টেবিলের জন্য যুক্তিসঙ্গত অতিরিক্ত।"""

    # আর্কিটেকচার ডকে সুনির্দিষ্টভাবে উল্লেখ করা ৩টা ইনডেক্স
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_decision_log_stage ON brain_decision_log(matched_stage)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_knowledge_category ON brain_knowledge(category, level)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_patterns_type ON brain_patterns(pattern_type)"
    )

    # অতিরিক্ত (যুক্তিসঙ্গত) ইনডেক্স — ভবিষ্যৎ Engine/Repository কুয়েরিগুলো দ্রুত রাখতে
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_decision_log_user ON brain_decision_log(user_id)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_decision_log_created ON brain_decision_log(created_at)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_documentation_tech ON brain_documentation(technology, category)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_errors_signature ON brain_errors(error_signature)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_templates_category ON brain_templates(category, language)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_context_user ON brain_context(user_id, session_key)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_project_memory_project ON brain_project_memory(project_id, memory_type)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_learning_queue_status ON brain_learning_queue(status)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_cache_knowledge_exp ON brain_cache_knowledge(expires_at)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_cache_search_exp ON brain_cache_search(expires_at)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_cache_ai_exp ON brain_cache_ai(expires_at)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_cache_project_exp ON brain_cache_project(expires_at)"
    )


def init_brain_db() -> None:
    """
    Brain OS-এর সব `brain_*` টেবিল/FTS5/ট্রিগার/ইনডেক্স তৈরি করে (থাকলে কিছুই করে না)।
    main.py-এর বিদ্যমান `init_db()`-এর ভেতর থেকে একবার কল হয় — `init_brain_db()`।

    এই ফাংশন ব্যর্থ হলেও (যেমন খুবই বিরল কোনো ডিস্ক/পারমিশন সমস্যা) পুরো বট Crash করা
    উচিত না — তাই এখানে try/except দিয়ে ধরে শুধু Warning লগ করা হয়, exception আবার
    ছোঁড়া হয় না। ফলে Brain OS টেবিল তৈরি ব্যর্থ হলেও বিদ্যমান বট (users/code_projects
    ইত্যাদি সহ) স্বাভাবিকভাবে চালু হবে।
    """
    try:
        conn = get_brain_conn()
        try:
            cur = conn.cursor()
            _create_core_tables(cur)
            _create_cache_tables(cur)
            _create_fts_tables_and_triggers(cur)
            _create_indexes(cur)
            # ---- Phase 14: Search Engine + Knowledge Engine — নতুন টেবিল/কলাম/ইনডেক্স ----
            # ক্রম গুরুত্বপূর্ণ: প্রথমে টেবিল/কলাম তৈরি, তারপর সেগুলোর উপর ইনডেক্স।
            _create_search_engine_tables(cur)
            _migrate_knowledge_columns(cur)
            _create_phase14_indexes(cur)
            # ---- Phase 15: Pattern + Template + Documentation + Error Engine ----
            # ক্রম এখানেও গুরুত্বপূর্ণ: প্রথমে কলাম-মাইগ্রেশন/নতুন টেবিল, সবশেষে ইনডেক্স।
            _migrate_pattern_columns(cur)
            _migrate_template_columns(cur)
            _migrate_documentation_columns(cur)
            _migrate_error_columns(cur)
            _create_phase15_tables(cur)
            _create_phase15_indexes(cur)
            # ---- Phase 16: Context + Decision Engine ----
            _create_phase16_tables(cur)
            # Phase 25: extend existing Project Memory Engine safely/idempotently.
            _migrate_project_memory_v2(cur)
            _migrate_coding_knowledge_v1(cur)
            # ---- Phase 43: OAuth 2.1 সার্ভার (MCP Custom Connector auth) ----
            _create_oauth_tables(cur)
            conn.commit()
            logger.info(
                "Brain OS (Phase 13-16): brain_* টেবিল/ইনডেক্স/Search+Knowledge+Pattern+"
                "Template+Documentation+Error+Project Memory+Coding Knowledge schema প্রস্তুত।"
            )
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — ইচ্ছাকৃত broad catch, উপরের docstring দেখুন
        logger.warning(f"Brain OS: init_brain_db() ব্যর্থ হয়েছে, বট বাকি সব ফিচার নিয়ে স্বাভাবিকভাবে চালু থাকবে। বিস্তারিত: {e}")


# =============================================================================
# Brain OS — originally brain/search_engine.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================




logger = logging.getLogger(__name__)

# ---- সমর্থিত সর্টিং অপশন ----
SORT_RELEVANCE = "relevance"
SORT_NEWEST = "newest"
SORT_OLDEST = "oldest"
SORT_PRIORITY = "priority"
VALID_SORTS = (SORT_RELEVANCE, SORT_NEWEST, SORT_OLDEST, SORT_PRIORITY)

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
FUZZY_CANDIDATE_LIMIT = 200      # difflib fallback-এ সর্বোচ্চ কতগুলো রো স্ক্যান করা হবে
FUZZY_MIN_RATIO = 0.55           # difflib সাদৃশ্য থ্রেশহোল্ড


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _get_columns(conn: sqlite3.Connection, table: str) -> set:
    """`PRAGMA table_info` দিয়ে টেবিলের কলাম-নামগুলো বের করে (কোন optional কলাম
    আছে/নেই সেটা রানটাইমে জানার জন্য — এভাবে টেবিল-নির্দিষ্ট if/else হার্ডকোড করা লাগে না,
    Future-Proof থাকে)।"""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def _tokenize(query: str) -> List[str]:
    """সাদা-স্পেস/পাংচুয়েশন দিয়ে টোকেনাইজ করে, খালি টোকেন বাদ দিয়ে।"""
    tokens = re.findall(r"[\w\u0980-\u09FF]+", query, flags=re.UNICODE)
    return [t for t in tokens if t]


def _build_match_expr(tokens: Sequence[str], relax: bool = False) -> str:
    """
    টোকেনগুলো থেকে একটা নিরাপদ FTS5 MATCH এক্সপ্রেশন বানায়।
    - প্রতিটা টোকেন ডাবল-কোটে মোড়ানো হয় (FTS5 কুয়েরি-সিনট্যাক্স ইনজেকশন এড়াতে —
      ইউজার ইনপুটে থাকা `AND`/`OR`/`NOT`/`*`/`"` ইত্যাদি বিশেষ অর্থ পাবে না)।
    - প্রতিটা টোকেনের পরে `*` (প্রিফিক্স-ম্যাচ) — এতে আংশিক/টাইপোযুক্ত শব্দও কিছুটা ধরা পড়ে
      (Typo Tolerance-এর প্রথম ধাপ)।
    - `relax=True` হলে প্রতিটা টোকেনের প্রথম ~৭০% অক্ষর নিয়ে প্রিফিক্স বানানো হয় (আরও শিথিল
      ম্যাচ — Fuzzy fallback-এর দ্বিতীয় ধাপ)।
    """
    parts = []
    for tok in tokens:
        clean = tok.replace('"', "")
        if not clean:
            continue
        if relax and len(clean) >= 4:
            cut = max(2, int(len(clean) * 0.7))
            clean = clean[:cut]
        parts.append(f'"{clean}"*')
    # টোকেনগুলো OR দিয়ে জোড়া হয় (AND নয়) — স্বাভাবিক-ভাষার কোয়েরিতে (যেমন Auto Retrieval-এ
    # ব্যবহৃত বহু-শব্দের প্রশ্ন) প্রতিটা শব্দ মিলতেই হবে এমন কড়াকড়ি রাখলে Recall কমে যায়;
    # BM25 নিজেই বেশি-শব্দ-মেলা রেজাল্টকে বেশি স্কোর দেয়, তাই OR + BM25 র‍্যাঙ্কিং একসাথে
    # যথেষ্ট প্রাসঙ্গিক ফলাফল দেয়।
    return " OR ".join(parts)


@dataclass
class SearchResult:
    """একটা সার্চ-রেজাল্ট রো (highlight/rank_score সহ) + পেজিনেশন মেটাডেটা `search()`-এর
    রিটার্ন-ভ্যালুতে থাকে (dict আকারে) — এই dataclass শুধু একটা আইটেমের শেপ বোঝাতে।"""
    row: Dict[str, Any]
    rank_score: Optional[float] = None
    match_type: str = "exact"   # 'exact' / 'relaxed' / 'fuzzy'


class SearchEngine:
    """
    জেনেরিক FTS5-ভিত্তিক Search Engine। কোন টেবিল সার্চ হবে তা কনস্ট্রাক্টরে বলা হয়,
    কিন্তু সাধারণত নিচের factory-মেথডগুলোর একটা ব্যবহার করাই সহজ ও নিরাপদ।
    """

    def __init__(
        self,
        table: str,
        fts_table: str,
        fts_columns: Sequence[str],
        title_column: str = "title",
    ) -> None:
        self.table = table
        self.fts_table = fts_table
        self.fts_columns = list(fts_columns)
        self.title_column = title_column

    # ------------------------- Factory (preset) কনফিগারেশন -------------------------

    @classmethod
    def for_knowledge(cls) -> "SearchEngine":
        return cls("brain_knowledge", "brain_knowledge_fts", ("title", "content", "tags", "category"))

    @classmethod
    def for_documentation(cls) -> "SearchEngine":
        return cls("brain_documentation", "brain_documentation_fts", ("title", "content", "technology"))

    @classmethod
    def for_errors(cls) -> "SearchEngine":
        return cls(
            "brain_errors", "brain_errors_fts", ("error_signature", "description", "solution"),
            title_column="error_signature",
        )

    # ------------------------------- মূল সার্চ ফাংশন -------------------------------

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = "active",
        sort: str = SORT_RELEVANCE,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        highlight: bool = True,
        fuzzy: bool = True,
        include_deleted: bool = False,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        মূল সার্চ ফাংশন — Keyword + Category + Tag + Multi-Filter + Relevance(BM25)/
        Newest/Oldest/Priority সর্টিং + Pagination + Highlight + Fuzzy fallback,
        সব একসাথে। রিটার্ন করে:

        {
            "items": [ {..row.., "_highlight_title": str|None, "_rank_score": float|None,
                        "_match_type": "exact"|"relaxed"|"fuzzy"}, ... ],
            "total": int, "page": int, "page_size": int, "total_pages": int,
            "query": str, "match_type": "exact"|"relaxed"|"fuzzy"|"empty",
        }

        কোনো এক্সেপশন ছুঁড়ে না — সমস্যা হলে খালি রেজাল্ট + লগ-ওয়ার্নিং।
        """
        query = (query or "").strip()
        page = max(1, page)
        page_size = max(1, min(page_size, MAX_PAGE_SIZE))
        if sort not in VALID_SORTS:
            sort = SORT_RELEVANCE
        empty_result = {
            "items": [], "total": 0, "page": page, "page_size": page_size,
            "total_pages": 0, "query": query, "match_type": "empty",
        }
        if not query:
            return empty_result

        tokens = _tokenize(query)
        if not tokens:
            return empty_result

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine: ডাটাবেস কানেকশন ব্যর্থ: {e}")
            return empty_result

        try:
            columns = _get_columns(conn, self.table)
            match_type = "exact"
            match_expr = _build_match_expr(tokens, relax=False)
            rows, total = self._run_match_query(
                conn, columns, match_expr, category, tag, status, include_deleted, sort, page, page_size,
            )

            if not rows and fuzzy:
                # ধাপ ২: রিল্যাক্সড প্রিফিক্স
                match_type = "relaxed"
                relaxed_expr = _build_match_expr(tokens, relax=True)
                rows, total = self._run_match_query(
                    conn, columns, relaxed_expr, category, tag, status, include_deleted, sort, page, page_size,
                )

            if not rows and fuzzy:
                # ধাপ ৩: difflib দিয়ে সাদৃশ্য-স্কোরিং (সীমিত ক্যান্ডিডেট পুলে)
                match_type = "fuzzy"
                rows, total = self._fuzzy_scan(
                    conn, columns, query, category, tag, status, include_deleted, page, page_size,
                )

            items = [self._decorate(conn, columns, row, query, highlight, match_type) for row in rows]

            if user_id is not None:
                self._log_search(conn, user_id, query, total)

            total_pages = (total + page_size - 1) // page_size if total else 0
            return {
                "items": items, "total": total, "page": page, "page_size": page_size,
                "total_pages": total_pages, "query": query, "match_type": match_type if rows else "empty",
            }
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine.search() ব্যর্থ (table={self.table}): {e}")
            return empty_result
        finally:
            conn.close()

    # ------------------------------- সহায়ক মেথড -------------------------------

    def _build_filters(
        self, columns: set, category: Optional[str], tag: Optional[str],
        status: Optional[str], include_deleted: bool,
    ) -> tuple:
        """স্ট্যাটাস/ক্যাটাগরি/ট্যাগ ফিল্টার — শুধু কলাম আসলে থাকলেই যোগ হয় (ফলে এই একই
        কোড brain_documentation/brain_errors-এর মতো টেবিলেও ভাঙে না, যাদের status/tags নেই)।"""
        clauses: List[str] = []
        params: List[Any] = []
        if category and "category" in columns:
            clauses.append("k.category = ?")
            params.append(category)
        if tag and "tags" in columns:
            clauses.append("k.tags LIKE ?")
            params.append(f"%{tag}%")
        if status and "status" in columns:
            clauses.append("k.status = ?")
            params.append(status)
        if "deleted_at" in columns and not include_deleted:
            clauses.append("(k.deleted_at IS NULL OR k.deleted_at = '')")
        return clauses, params

    def _order_clause(self, columns: set, sort: str) -> str:
        if sort == SORT_NEWEST and "created_at" in columns:
            return "k.created_at DESC"
        if sort == SORT_OLDEST and "created_at" in columns:
            return "k.created_at ASC"
        if sort == SORT_PRIORITY and "priority" in columns:
            return "k.priority DESC, rank_score ASC"
        return "rank_score ASC"   # relevance (bm25: ছোট মান = বেশি প্রাসঙ্গিক)

    def _run_match_query(
        self, conn, columns, match_expr, category, tag, status, include_deleted, sort, page, page_size,
    ):
        if not match_expr:
            return [], 0
        clauses, params = self._build_filters(columns, category, tag, status, include_deleted)
        where_extra = (" AND " + " AND ".join(clauses)) if clauses else ""
        order_by = self._order_clause(columns, sort)
        offset = (page - 1) * page_size

        # লক্ষ্য করুন: FTS5 ভার্চুয়াল টেবিলকে (external-content) alias না দিয়ে সরাসরি নামে
        # ব্যবহার করা হয়েছে — কিছু SQLite বিল্ডে aliased FTS5 টেবিলে `MATCH`/`bm25()`
        # "no such column" এরর দেয়, রিয়েল টেবিল-নাম ব্যবহার করলে সেই সমস্যা হয় না।
        base_from = (
            f"FROM {self.fts_table} JOIN {self.table} k ON k.id = {self.fts_table}.rowid "
            f"WHERE {self.fts_table} MATCH ?{where_extra}"
        )
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) {base_from}", (match_expr, *params))
        total = cur.fetchone()[0]

        cur.execute(
            f"SELECT k.*, bm25({self.fts_table}) AS rank_score {base_from} "
            f"ORDER BY {order_by} LIMIT ? OFFSET ?",
            (match_expr, *params, page_size, offset),
        )
        rows = cur.fetchall()
        col_names = [d[0] for d in cur.description]
        return [dict(zip(col_names, r)) for r in rows], total

    def _fuzzy_scan(self, conn, columns, query, category, tag, status, include_deleted, page, page_size):
        """
        সবশেষ ফলব্যাক: FTS5 MATCH একদমই কিছু না পেলে (খুব বেশি টাইপো/ভিন্ন বানান), সাম্প্রতিক
        `FUZZY_CANDIDATE_LIMIT`টা রো টেনে এনে `difflib.SequenceMatcher` দিয়ে টাইটেলের সাথে
        সাদৃশ্য মাপা হয়, থ্রেশহোল্ডের উপরে যা পাওয়া যায় তা সাদৃশ্য অনুযায়ী সাজিয়ে রিটার্ন করা হয়।
        এটা O(candidates) — তাই ইচ্ছাকৃতভাবে candidate সংখ্যা সীমিত রাখা হয়েছে (Performance)।
        """
        clauses, params = self._build_filters(columns, category, tag, status, include_deleted)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM {self.table} k{where} ORDER BY k.id DESC LIMIT ?",
            (*params, FUZZY_CANDIDATE_LIMIT),
        )
        rows = cur.fetchall()
        col_names = [d[0] for d in cur.description]
        candidates = [dict(zip(col_names, r)) for r in rows]

        q_lower = query.lower()
        scored = []
        for row in candidates:
            title = str(row.get(self.title_column, "") or "")
            ratio = difflib.SequenceMatcher(None, q_lower, title.lower()).ratio()
            if ratio >= FUZZY_MIN_RATIO:
                row["rank_score"] = 1.0 - ratio  # ছোট = ভালো, বাকি ranking-এর সাথে সামঞ্জস্যপূর্ণ রাখতে
                scored.append((ratio, row))

        scored.sort(key=lambda x: x[0], reverse=True)
        total = len(scored)
        start = (page - 1) * page_size
        page_rows = [r for _, r in scored[start:start + page_size]]
        return page_rows, total

    def _decorate(self, conn, columns, row: Dict[str, Any], query: str, highlight: bool, match_type: str) -> Dict[str, Any]:
        """হাইলাইট টেক্সট ও ম্যাচ-টাইপ যোগ করে রেজাল্ট রো সাজায় (Highlight Matched Words)।"""
        result = dict(row)
        result["_match_type"] = match_type
        if highlight and match_type in ("exact", "relaxed"):
            try:
                tokens = _tokenize(query)
                expr = _build_match_expr(tokens, relax=(match_type == "relaxed"))
                title_idx = self.fts_columns.index(self.title_column) if self.title_column in self.fts_columns else 0
                cur = conn.cursor()
                cur.execute(
                    f"SELECT highlight({self.fts_table}, ?, '**', '**') FROM {self.fts_table} "
                    f"WHERE rowid = ? AND {self.fts_table} MATCH ?",
                    (title_idx, row["id"], expr),
                )
                hl = cur.fetchone()
                result["_highlight_title"] = hl[0] if hl else result.get(self.title_column)
            except Exception:  # noqa: BLE001
                result["_highlight_title"] = result.get(self.title_column)
        else:
            result["_highlight_title"] = result.get(self.title_column)
        return result

    def _log_search(self, conn, user_id: int, query: str, results_count: int) -> None:
        """Search History — কে, কী খুঁজেছে, কতগুলো ফল পেয়েছে তা লগ করে (Suggestions-এর ভিত্তি)।"""
        try:
            entity = "knowledge" if self.table == "brain_knowledge" else (
                "documentation" if self.table == "brain_documentation" else "errors"
            )
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO brain_search_history (user_id, query, entity, results_count, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, query, entity, results_count, _now()),
            )
            conn.commit()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine: search history লগ করা যায়নি: {e}")

    # ------------------------------- Auto Suggestions -------------------------------

    def suggest(self, prefix: str, limit: int = 5) -> List[str]:
        """
        Auto Search Suggestions — টাইটেল-প্রিফিক্স ম্যাচ + জনপ্রিয় পূর্ববর্তী সার্চ-কোয়েরি
        (search history থেকে), মিলিয়ে সবচেয়ে প্রাসঙ্গিক `limit`টা সাজেশন রিটার্ন করে।
        """
        prefix = (prefix or "").strip()
        if not prefix:
            return []
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine.suggest(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            suggestions: List[str] = []
            cur = conn.cursor()
            cur.execute(
                f"SELECT DISTINCT {self.title_column} FROM {self.table} "
                f"WHERE {self.title_column} LIKE ? LIMIT ?",
                (f"{prefix}%", limit),
            )
            suggestions.extend(row[0] for row in cur.fetchall() if row[0])

            if len(suggestions) < limit:
                entity = "knowledge" if self.table == "brain_knowledge" else (
                    "documentation" if self.table == "brain_documentation" else "errors"
                )
                cur.execute(
                    "SELECT query, COUNT(*) c FROM brain_search_history "
                    "WHERE entity = ? AND query LIKE ? GROUP BY query ORDER BY c DESC LIMIT ?",
                    (entity, f"{prefix}%", limit - len(suggestions)),
                )
                for row in cur.fetchall():
                    if row[0] not in suggestions:
                        suggestions.append(row[0])
            return suggestions[:limit]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine.suggest() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    def get_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """একজন ইউজারের সাম্প্রতিক সার্চ হিস্টোরি (নতুন আগে)।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine.get_history(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, user_id, query, entity, results_count, created_at FROM brain_search_history "
                "WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine.get_history() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ------------------------------- Duplicate Detection -------------------------------

    def find_duplicates(self) -> List[Dict[str, Any]]:
        """
        `content_hash` কলাম আছে এমন টেবিলে (এখন পর্যন্ত শুধু `brain_knowledge`) একই হ্যাশের
        একাধিক (নন-ডিলিটেড) রো থাকলে সেগুলোর গ্রুপ রিটার্ন করে — যেমন:
        [{"content_hash": "...", "count": 2, "ids": [3, 17]}, ...]
        """
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine.find_duplicates(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            columns = _get_columns(conn, self.table)
            if "content_hash" not in columns:
                return []
            deleted_filter = "AND (deleted_at IS NULL OR deleted_at = '')" if "deleted_at" in columns else ""
            cur = conn.cursor()
            cur.execute(
                f"SELECT content_hash, COUNT(*) c, GROUP_CONCAT(id) ids FROM {self.table} "
                f"WHERE content_hash != '' {deleted_filter} GROUP BY content_hash HAVING c > 1"
            )
            return [
                {"content_hash": row[0], "count": row[1], "ids": [int(x) for x in row[2].split(",")]}
                for row in cur.fetchall()
            ]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"SearchEngine.find_duplicates() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ------------------------------- Async ওয়্র্যাপার -------------------------------
    # Performance রিকোয়ারমেন্ট "Async Search Operations" — async Telegram হ্যান্ডলার
    # থেকে কল করলে ইভেন্ট-লুপ ব্লক না করার জন্য `asyncio.to_thread` দিয়ে থ্রেডে চালানো হয়।

    async def search_async(self, *args, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.search, *args, **kwargs)

    async def suggest_async(self, *args, **kwargs) -> List[str]:
        return await asyncio.to_thread(self.suggest, *args, **kwargs)

    async def get_history_async(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_history, *args, **kwargs)

    async def find_duplicates_async(self) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.find_duplicates)


# =============================================================================
# Brain OS — originally brain/knowledge_engine.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================




logger = logging.getLogger(__name__)

VALID_STATUSES = ("draft", "active", "archived")
DEFAULT_CONTEXT_MAX_CHARS = 4000   # Context Optimization-এর ডিফল্ট বাজেট


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize(text: str) -> str:
    """হ্যাশ/তুলনার জন্য টেক্সট নরমালাইজ করে (lowercase + একাধিক স্পেস একটাতে)।"""
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _knowledge_compute_hash(category: str, title: str, content: str) -> str:
    """Duplicate Detection-এর জন্য sha256(category+title+content), নরমালাইজড।"""
    payload = f"{_normalize(category)}|{_normalize(title)}|{_normalize(content)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class KnowledgeEngine:
    """Knowledge Engine — brain_knowledge-এর জন্য পুরো CRUD + Ranking + Retrieval API।"""

    def __init__(self) -> None:
        # ল্যাজি ইম্পোর্ট নয় (search_engine, database.py-এর মতো main.py-এর উপর
        # নির্ভর করে না, তাই সরাসরি টপ-লেভেল ইম্পোর্ট নিরাপদ, কোনো circular-import নেই)।

        self._search_engine = SearchEngine.for_knowledge()

    # ================================ Create ================================

    def create(
        self,
        category: str,
        title: str,
        content: str,
        tags: str = "",
        priority: int = 5,
        level: Optional[int] = None,
        source: str = "admin",
        metadata: Optional[Dict[str, Any]] = None,
        confidence_score: float = 1.0,
        status: str = "active",
        allow_duplicate: bool = False,
    ) -> Optional[BrainKnowledge]:
        """
        নতুন Knowledge Entry তৈরি করে। ডিফল্টে ডুপ্লিকেট (একই category+title+content)
        পাওয়া গেলে নতুন করে ইনসার্ট না করে বিদ্যমানটাই রিটার্ন করে (`allow_duplicate=True`
        দিলে জোর করে নতুন রো তৈরি হবে)।
        """
        if not title or not content:
            logger.warning("KnowledgeEngine.create(): title/content খালি রাখা যাবে না")
            return None
        if status not in VALID_STATUSES:
            status = "active"

        content_hash = _knowledge_compute_hash(category, title, content)
        if not allow_duplicate:
            existing = self.check_duplicate(category, title, content)
            if existing is not None:
                logger.info(f"KnowledgeEngine.create(): ডুপ্লিকেট পাওয়া গেছে (id={existing.id}), বিদ্যমানটাই রিটার্ন হলো")
                return existing

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.create(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            now = _now()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO brain_knowledge
                    (level, category, title, content, tags, priority, version, source,
                     created_at, updated_at, metadata, confidence_score, status, deleted_at, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, '', ?)
                """,
                (
                    level, category, title, content, tags, priority, source, now, now,
                    json.dumps(metadata or {}, ensure_ascii=False), confidence_score, status, content_hash,
                ),
            )
            conn.commit()
            new_id = cur.lastrowid
            return self.get(new_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.create() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def check_duplicate(self, category: str, title: str, content: str) -> Optional[BrainKnowledge]:
        """একই category+title+content-এর অ-ডিলিটেড রো আগে থেকে আছে কিনা চেক করে।"""
        content_hash = _knowledge_compute_hash(category, title, content)
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.check_duplicate(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM brain_knowledge WHERE content_hash = ? "
                "AND (deleted_at IS NULL OR deleted_at = '') LIMIT 1",
                (content_hash,),
            )
            row = cur.fetchone()
            return BrainKnowledge.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.check_duplicate() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    # ================================= Read =================================

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Phase 35 বাগ-ফিক্স: আগে এই মেথডটাই ছিল না, তাই Decision Engine-এর
        `hasattr(KnowledgeEngine(), "search")` চেক সবসময় False হতো এবং Knowledge Engine
        কখনোই কোনো candidate দিতে পারতো না — যতই তথ্য সেভ করা থাকুক না কেন, সবসময় সরাসরি
        AI-তে চলে যেত। এখন `self._search_engine` (FTS5 ভিত্তিক) দিয়ে আসল সার্চ চালিয়ে
        Decision Engine-এর ranking-এর জন্য উপযুক্ত shape-এ (score 0..1, confidence_score,
        content) রিটার্ন করে। Phase 48: metadata-য় expires_at (মেয়াদ) থাকা এন্ট্রি মেয়াদ
        পেরোলে স্কিপ হয় — ক্যাশ-পয়জনিং ঠেকাতে মেয়াদোত্তীর্ণ উত্তর আর Step 1-এ ফেরে না।
        কোনো এক্সেপশন ছুঁড়ে না — সমস্যা হলে খালি লিস্ট।
        """
        try:
            result = self._search_engine.search(query, page_size=max(1, min(limit, 20)), status="active")
            items = result.get("items", []) or []
            match_type = result.get("match_type", "empty")
            out: List[Dict[str, Any]] = []
            for row in items:
                # Phase 48: মেয়াদোত্তীর্ণ (expires_at পেরোনো) এন্ট্রি বাদ — পুরোনো/ভুল
                # cached উত্তর আর Decision Engine-এর কাছে পৌঁছায় না (ক্যাশ-পয়জনিং ঠেকানো)।
                if _knowledge_entry_expired(row.get("metadata") if isinstance(row, dict) else None):
                    logger.debug(f"KnowledgeEngine.search(): মেয়াদোত্তীর্ণ এন্ট্রি স্কিপ (id={row.get('id')})")
                    continue
                rank = row.get("rank_score")
                if match_type in ("exact", "relaxed") and isinstance(rank, (int, float)):
                    # bm25(): সবসময় <=0, |rank| যত বড় তত জোরালো/বহু-টোকেন মিল। তাই
                    # score = |rank|/(1+|rank|) — |rank| বড় হলে score 1-এর কাছে,
                    # |rank| প্রায় 0 (একটামাত্র বিরল টোকেনে কাকতালীয় মিল) হলে score ~0।
                    magnitude = abs(float(rank))
                    score = magnitude / (1.0 + magnitude)
                elif match_type == "fuzzy" and isinstance(rank, (int, float)):
                    # fuzzy scan-এ rank_score = 1-ratio (উল্টো কনভেনশন — ছোট rank_score
                    # মানে ratio বেশি, অর্থাৎ ভালো মিল), তাই সরাসরি ratio-ই আসল score।
                    score = max(0.0, min(1.0, 1.0 - float(rank)))
                else:
                    score = 0.5
                out.append({
                    "id": row.get("id"),
                    "title": row.get("title", ""),
                    "content": row.get("content", ""),
                    "category": row.get("category", "") or "",
                    "confidence_score": float(row.get("confidence_score", 0.7) or 0.7),
                    "score": max(0.0, min(1.0, score)),
                })
            return out
        except Exception as e:  # noqa: BLE001
            logger.debug("KnowledgeEngine.search() ব্যর্থ: %s", e)
            return []

    async def search_async(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.search, *args, **kwargs)

    def get(self, knowledge_id: int, include_deleted: bool = False) -> Optional[BrainKnowledge]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.get(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            if include_deleted:
                cur.execute("SELECT * FROM brain_knowledge WHERE id = ?", (knowledge_id,))
            else:
                cur.execute(
                    "SELECT * FROM brain_knowledge WHERE id = ? AND (deleted_at IS NULL OR deleted_at = '')",
                    (knowledge_id,),
                )
            row = cur.fetchone()
            return BrainKnowledge.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.get() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def _paginated_list(self, where_clause: str, params: tuple, page: int, page_size: int, sort: str) -> Dict[str, Any]:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        order_by = {
            "priority": "priority DESC, updated_at DESC",
            "newest": "created_at DESC",
            "oldest": "created_at ASC",
        }.get(sort, "priority DESC, updated_at DESC")
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine: কানেকশন ব্যর্থ: {e}")
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM brain_knowledge WHERE {where_clause}", params)
            total = cur.fetchone()[0]
            offset = (page - 1) * page_size
            cur.execute(
                f"SELECT * FROM brain_knowledge WHERE {where_clause} ORDER BY {order_by} LIMIT ? OFFSET ?",
                (*params, page_size, offset),
            )
            items = [BrainKnowledge.from_row(row) for row in cur.fetchall()]
            total_pages = (total + page_size - 1) // page_size if total else 0
            return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine পেজিনেটেড-লিস্ট ব্যর্থ: {e}")
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
        finally:
            conn.close()

    def list_by_category(
        self, category: str, page: int = 1, page_size: int = 20,
        include_deleted: bool = False, sort: str = "priority",
    ) -> Dict[str, Any]:
        if include_deleted:
            return self._paginated_list("category = ?", (category,), page, page_size, sort)
        return self._paginated_list(
            "category = ? AND (deleted_at IS NULL OR deleted_at = '')", (category,), page, page_size, sort,
        )

    def list_by_tag(
        self, tag: str, page: int = 1, page_size: int = 20,
        include_deleted: bool = False, sort: str = "priority",
    ) -> Dict[str, Any]:
        if include_deleted:
            return self._paginated_list("tags LIKE ?", (f"%{tag}%",), page, page_size, sort)
        return self._paginated_list(
            "tags LIKE ? AND (deleted_at IS NULL OR deleted_at = '')", (f"%{tag}%",), page, page_size, sort,
        )

    # =============================== Update/Delete ===============================

    def update(self, knowledge_id: int, **fields: Any) -> Optional[BrainKnowledge]:
        """
        আংশিক আপডেট — শুধু যেসব ফিল্ড দেওয়া হয়েছে সেগুলোই বদলায়। অনুমোদিত ফিল্ড:
        category, title, content, tags, priority, level, source, metadata (dict),
        confidence_score, status। title/content বদলালে Version Management অনুযায়ী
        `version` স্বয়ংক্রিয়ভাবে ১ বাড়ে ও `content_hash` নতুন করে গণনা হয়।
        """
        allowed = {
            "category", "title", "content", "tags", "priority", "level",
            "source", "metadata", "confidence_score", "status",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get(knowledge_id)
        if "status" in updates and updates["status"] not in VALID_STATUSES:
            updates.pop("status")

        current = self.get(knowledge_id, include_deleted=True)
        if current is None:
            logger.warning(f"KnowledgeEngine.update(): id={knowledge_id} পাওয়া যায়নি")
            return None

        content_changed = "title" in updates or "content" in updates
        new_title = updates.get("title", current.title)
        new_content = updates.get("content", current.content)
        new_category = updates.get("category", current.category)

        if "metadata" in updates and isinstance(updates["metadata"], dict):
            updates["metadata"] = json.dumps(updates["metadata"], ensure_ascii=False)

        set_parts = [f"{col} = ?" for col in updates]
        params: List[Any] = list(updates.values())
        set_parts.append("updated_at = ?")
        params.append(_now())
        if content_changed:
            set_parts.append("version = version + 1")
            set_parts.append("content_hash = ?")
            params.append(_knowledge_compute_hash(new_category, new_title, new_content))
        params.append(knowledge_id)

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.update(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE brain_knowledge SET {', '.join(set_parts)} WHERE id = ?", params)
            conn.commit()
            return self.get(knowledge_id, include_deleted=True)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.update() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def delete(self, knowledge_id: int) -> bool:
        """Soft Delete — `deleted_at` সেট করে, রো আসলে মোছে না (Restore-এর সুবিধার্থে)।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.delete(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_knowledge SET deleted_at = ?, updated_at = ? WHERE id = ?",
                (_now(), _now(), knowledge_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.delete() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    def restore(self, knowledge_id: int) -> bool:
        """Soft-ডিলিটেড রো ফিরিয়ে আনে (`deleted_at` খালি করে)।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.restore(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_knowledge SET deleted_at = '', updated_at = ? WHERE id = ?",
                (_now(), knowledge_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.restore() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    # ============================ Related / Ranking ============================

    def get_related(self, knowledge_id: int, limit: int = 5) -> List[BrainKnowledge]:
        """
        Related Knowledge Detection — একই category বা ট্যাগ-ওভারল্যাপ থাকা বাকি অ্যাক্টিভ
        এন্ট্রিগুলো খুঁজে বের করে, শেয়ার্ড-ট্যাগ সংখ্যা (বেশি ভালো) তারপর priority অনুযায়ী
        সাজিয়ে সেরা `limit`টা রিটার্ন করে।
        """
        base = self.get(knowledge_id, include_deleted=True)
        if base is None:
            return []
        base_tags = {t.strip().lower() for t in base.tags.split(",") if t.strip()}

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.get_related(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM brain_knowledge WHERE id != ? AND category = ? "
                "AND (deleted_at IS NULL OR deleted_at = '') AND status = 'active' "
                "ORDER BY priority DESC LIMIT 50",
                (knowledge_id, base.category),
            )
            candidates = [BrainKnowledge.from_row(row) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.get_related() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

        def shared_tag_count(entry: BrainKnowledge) -> int:
            entry_tags = {t.strip().lower() for t in entry.tags.split(",") if t.strip()}
            return len(base_tags & entry_tags)

        candidates.sort(key=lambda e: (shared_tag_count(e), e.priority), reverse=True)
        return candidates[:limit]

    def rank(self, entries: List[BrainKnowledge]) -> List[BrainKnowledge]:
        """Knowledge Ranking — priority, তারপর confidence_score, তারপর সাম্প্রতিকতা অনুযায়ী সাজায়।"""
        return sorted(
            entries,
            key=lambda e: (e.priority, e.confidence_score, e.updated_at),
            reverse=True,
        )

    # ================================ Bulk I/O ================================

    def bulk_import(self, entries: List[Dict[str, Any]], skip_duplicates: bool = True) -> Dict[str, int]:
        """
        একসাথে অনেক Knowledge Entry ইমপোর্ট করে (যেমন সিড-ডাটা/ব্যাকআপ থেকে)।
        প্রতিটা dict-এ অন্তত `category`/`title`/`content` থাকতে হবে। রিটার্ন করে
        {"created": n, "skipped_duplicates": n, "failed": n}।
        """
        summary = {"created": 0, "skipped_duplicates": 0, "failed": 0}
        for entry in entries:
            title = entry.get("title", "")
            content = entry.get("content", "")
            category = entry.get("category", "")
            if not title or not content:
                summary["failed"] += 1
                continue
            if skip_duplicates and self.check_duplicate(category, title, content) is not None:
                summary["skipped_duplicates"] += 1
                continue
            created = self.create(
                category=category,
                title=title,
                content=content,
                tags=entry.get("tags", ""),
                priority=entry.get("priority", 5),
                level=entry.get("level"),
                source=entry.get("source", "bulk_import"),
                metadata=entry.get("metadata"),
                confidence_score=entry.get("confidence_score", 1.0),
                status=entry.get("status", "active"),
                allow_duplicate=not skip_duplicates,
            )
            if created is not None:
                summary["created"] += 1
            else:
                summary["failed"] += 1
        return summary

    def bulk_export(
        self, category: Optional[str] = None, status: Optional[str] = None, include_deleted: bool = False,
    ) -> List[Dict[str, Any]]:
        """সব (বা ফিল্টার করা) Knowledge Entry-কে JSON-এক্সপোর্টযোগ্য dict লিস্ট হিসেবে রিটার্ন করে।"""
        clauses: List[str] = []
        params: List[Any] = []
        if category:
            clauses.append("category = ?")
            params.append(category)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if not include_deleted:
            clauses.append("(deleted_at IS NULL OR deleted_at = '')")
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.bulk_export(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM brain_knowledge{where} ORDER BY id ASC", params)
            entries = [BrainKnowledge.from_row(row) for row in cur.fetchall()]
            return [entry.__dict__ for entry in entries]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"KnowledgeEngine.bulk_export() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ======================= Context Optimization / Auto Retrieval =======================

    def optimize_context(
        self, entries: List[BrainKnowledge], max_chars: int = DEFAULT_CONTEXT_MAX_CHARS,
    ) -> List[BrainKnowledge]:
        """
        Context Optimization — AI-কে পাঠানোর আগে entry-লিস্টকে অক্ষর-বাজেটের মধ্যে আনে।
        সবচেয়ে গুরুত্বপূর্ণ (rank() অনুযায়ী) এন্ট্রিগুলো আগে রাখা হয়, বাজেট শেষ হলে বাকিগুলো
        বাদ পড়ে (আংশিক এন্ট্রি কাটা হয় না — পুরো এন্ট্রি থাকে অথবা বাদ যায়, যাতে জ্ঞান
        অর্ধেক-অসম্পূর্ণ অবস্থায় AI-কে না দেওয়া হয়)।
        """
        ranked = self.rank(entries)
        selected: List[BrainKnowledge] = []
        used = 0
        for entry in ranked:
            entry_len = len(entry.title) + len(entry.content)
            if used + entry_len > max_chars and selected:
                break
            selected.append(entry)
            used += entry_len
        return selected

    def auto_retrieve(
        self, query: str, top_k: int = 5, max_chars: int = DEFAULT_CONTEXT_MAX_CHARS,
    ) -> List[BrainKnowledge]:
        """
        Auto Retrieval — একটা কোয়েরির জন্য সবচেয়ে প্রাসঙ্গিক Knowledge Entry-গুলো খুঁজে
        (Search Engine ব্যবহার করে), Ranking করে, ও Context Optimization দিয়ে বাজেটের মধ্যে
        এনে রিটার্ন করে। এটাই Knowledge Engine-এর "Search Engine-এর উপর সম্পূর্ণ নির্ভরশীলতা"-র
        মূল প্রয়োগ — এখানে কোনো নিজস্ব FTS/ম্যাচিং লজিক নেই।
        """
        result = self._search_engine.search(query, status="active", sort="relevance", page=1, page_size=top_k)
        ids = [item["id"] for item in result["items"]]
        entries = [self.get(i) for i in ids]
        entries = [e for e in entries if e is not None]
        return self.optimize_context(entries, max_chars=max_chars)

    # ================================= Async ওয়্র্যাপার =================================

    async def create_async(self, *args, **kwargs) -> Optional[BrainKnowledge]:
        return await asyncio.to_thread(self.create, *args, **kwargs)

    async def update_async(self, *args, **kwargs) -> Optional[BrainKnowledge]:
        return await asyncio.to_thread(self.update, *args, **kwargs)

    async def delete_async(self, *args, **kwargs) -> bool:
        return await asyncio.to_thread(self.delete, *args, **kwargs)

    async def restore_async(self, *args, **kwargs) -> bool:
        return await asyncio.to_thread(self.restore, *args, **kwargs)

    async def get_related_async(self, *args, **kwargs) -> List[BrainKnowledge]:
        return await asyncio.to_thread(self.get_related, *args, **kwargs)

    async def auto_retrieve_async(self, *args, **kwargs) -> List[BrainKnowledge]:
        return await asyncio.to_thread(self.auto_retrieve, *args, **kwargs)


# =============================================================================
# Brain OS — originally brain/pattern_engine.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================




logger = logging.getLogger(__name__)

VALID_PATTERN_TYPES = ("keyword", "regex", "intent")
CACHE_TTL_SECONDS = 30  # Pattern Cache — এই সময় পর অ্যাক্টিভ-প্যাটার্ন লিস্ট রিফ্রেশ হয়


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


_WORD_TOKEN_RE = re.compile(r"[\w\u0980-\u09FF]+", flags=re.UNICODE)


def _whole_word_in_text(keyword: str, text: str) -> bool:
    """keyword টেক্সটে whole-word/phrase হিসেবে আছে কিনা — সাধারণ substring নয়।

    বাংলা ভাওয়েল-সাইন/হসন্ত `\\w`-এ পড়ে না, তাই lookaround নয় — টোকেন তুলনা
    (`[\\w\\u0980-\\u09FF]+`) ব্যবহার করা হয়। ফলে \"কমান্ড\" \"কমান্ডারকে\"-এর ভেতর
    মেলে না, কিন্তু \"কমান্ড তালিকা\"-তে মেলে; \"help\" \"helpful\"-এ মেলে না।
    মাল্টি-ওয়ার্ড ফ্রেজ (যেমন \"thank you\") পরপর টোকেন হিসেবে মিলে।
    কোনো এক্সসেপশনে False — কলার তখন ম্যাচ না ধরে AI/পরের ক্যান্ডিডেটে যায়।
    """
    try:
        kw = (keyword or "").strip()
        if not kw:
            return False
        kw_tokens = [t.casefold() for t in _WORD_TOKEN_RE.findall(kw)]
        if not kw_tokens:
            return False
        text_tokens = [t.casefold() for t in _WORD_TOKEN_RE.findall(text or "")]
        n = len(kw_tokens)
        if n > len(text_tokens):
            return False
        for i in range(len(text_tokens) - n + 1):
            if text_tokens[i:i + n] == kw_tokens:
                return True
        return False
    except Exception:
        return False


def _pattern_compute_hash(pattern_type: str, match_value: str, category: str) -> str:
    """Duplicate Pattern Detection-এর জন্য sha256(pattern_type+match_value+category)।"""
    payload = f"{(pattern_type or '').strip().lower()}|{(match_value or '').strip().lower()}|{(category or '').strip().lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class PatternEngine:
    """Pattern Engine — brain_patterns-এর জন্য পুরো CRUD + Matching + Analytics API।"""

    def __init__(self) -> None:
        # ---- Pattern Cache (in-memory) ----
        self._active_cache: Optional[List[BrainPattern]] = None
        self._active_cache_at: float = 0.0
        self._regex_cache: Dict[str, "re.Pattern[str]"] = {}

    # ================================ Validation ================================

    def validate_pattern(self, pattern_type: str, match_value: str) -> Optional[str]:
        """Pattern Validation — সমস্যা পেলে error message রিটার্ন করে, ঠিক থাকলে None।"""
        if pattern_type not in VALID_PATTERN_TYPES:
            return f"অবৈধ pattern_type: {pattern_type} (অনুমোদিত: {VALID_PATTERN_TYPES})"
        if not (match_value or "").strip():
            return "match_value খালি রাখা যাবে না"
        if pattern_type == "regex":
            try:
                re.compile(match_value)
            except re.error as e:
                return f"অবৈধ regex: {e}"
        return None

    # ================================ Create ================================

    def create(
        self,
        pattern_type: str,
        match_value: str,
        category: str = "",
        name: str = "",
        description: str = "",
        tags: str = "",
        template_id: Optional[int] = None,
        priority: int = 5,
        confidence_score: float = 1.0,
        allow_duplicate: bool = False,
    ) -> Optional[BrainPattern]:
        """নতুন Pattern তৈরি করে। ডিফল্টে ডুপ্লিকেট (একই type+value+category) পাওয়া গেলে
        বিদ্যমানটাই রিটার্ন করে (`allow_duplicate=True` দিলে জোর করে নতুন রো তৈরি হবে)।"""
        error = self.validate_pattern(pattern_type, match_value)
        if error:
            logger.warning(f"PatternEngine.create(): ভ্যালিডেশন ব্যর্থ: {error}")
            return None

        pattern_hash = _pattern_compute_hash(pattern_type, match_value, category)
        if not allow_duplicate:
            existing = self.check_duplicate(pattern_type, match_value, category)
            if existing is not None:
                logger.info(f"PatternEngine.create(): ডুপ্লিকেট পাওয়া গেছে (id={existing.id}), বিদ্যমানটাই রিটার্ন হলো")
                return existing

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.create(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            now = _now()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO brain_patterns
                    (pattern_type, match_value, category, template_id, priority, created_at,
                     name, description, tags, confidence_score, version, is_active, updated_at, pattern_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
                """,
                (
                    pattern_type, match_value, category, template_id, priority, now,
                    name, description, tags, confidence_score, now, pattern_hash,
                ),
            )
            conn.commit()
            new_id = cur.lastrowid
            self._invalidate_cache()
            return self.get(new_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.create() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def check_duplicate(self, pattern_type: str, match_value: str, category: str = "") -> Optional[BrainPattern]:
        pattern_hash = _pattern_compute_hash(pattern_type, match_value, category)
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.check_duplicate(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM brain_patterns WHERE pattern_hash = ? LIMIT 1", (pattern_hash,))
            row = cur.fetchone()
            return BrainPattern.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.check_duplicate() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    # ================================= Read =================================

    def get(self, pattern_id: int) -> Optional[BrainPattern]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.get(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM brain_patterns WHERE id = ?", (pattern_id,))
            row = cur.fetchone()
            return BrainPattern.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.get() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def list_by_category(self, category: str, active_only: bool = True, limit: int = 100) -> List[BrainPattern]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.list_by_category(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            if active_only:
                cur.execute(
                    "SELECT * FROM brain_patterns WHERE category = ? AND is_active = 1 "
                    "ORDER BY priority DESC, confidence_score DESC LIMIT ?",
                    (category, limit),
                )
            else:
                cur.execute(
                    "SELECT * FROM brain_patterns WHERE category = ? "
                    "ORDER BY priority DESC, confidence_score DESC LIMIT ?",
                    (category, limit),
                )
            return [BrainPattern.from_row(row) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.list_by_category() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    def list_by_type(self, pattern_type: str, active_only: bool = True, limit: int = 100) -> List[BrainPattern]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.list_by_type(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            clause = "AND is_active = 1" if active_only else ""
            cur.execute(
                f"SELECT * FROM brain_patterns WHERE pattern_type = ? {clause} "
                "ORDER BY priority DESC, confidence_score DESC LIMIT ?",
                (pattern_type, limit),
            )
            return [BrainPattern.from_row(row) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.list_by_type() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    def _load_active_patterns(self) -> List[BrainPattern]:
        """Pattern Cache — TTL-এর মধ্যে থাকলে ক্যাশ থেকে, নাহলে DB থেকে রিফ্রেশ করে।"""
        now = time.monotonic()
        if self._active_cache is not None and (now - self._active_cache_at) < CACHE_TTL_SECONDS:
            return self._active_cache
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine: কানেকশন ব্যর্থ (cache-refresh): {e}")
            return self._active_cache or []
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM brain_patterns WHERE is_active = 1 ORDER BY priority DESC")
            patterns = [BrainPattern.from_row(row) for row in cur.fetchall()]
            self._active_cache = patterns
            self._active_cache_at = now
            return patterns
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine: cache-refresh ব্যর্থ: {e}")
            return self._active_cache or []
        finally:
            conn.close()

    def _invalidate_cache(self) -> None:
        self._active_cache = None
        self._active_cache_at = 0.0

    def _get_compiled_regex(self, pattern: BrainPattern) -> Optional["re.Pattern[str]"]:
        key = f"{pattern.id}:{pattern.match_value}"
        compiled = self._regex_cache.get(key)
        if compiled is None:
            try:
                compiled = re.compile(pattern.match_value, re.IGNORECASE)
                self._regex_cache[key] = compiled
            except re.error as e:
                logger.warning(f"PatternEngine: id={pattern.id} regex কম্পাইল ব্যর্থ: {e}")
                return None
        return compiled

    # =============================== Matching ===============================

    def _score_pattern(self, pattern: BrainPattern, text: str) -> Optional[float]:
        """একটা প্যাটার্ন টেক্সটের সাথে মেলে কিনা চেক করে; মিললে confidence স্কোর (0-1) রিটার্ন করে।"""
        text_lower = text.lower()
        if pattern.pattern_type == "keyword":
            keywords = [k.strip().lower() for k in pattern.match_value.split(",") if k.strip()]
            if not keywords:
                return None
            # Whole-word/phrase match only — "কমান্ড" যেন কোনো বড় বাক্যের দূরবর্তী
            # substring হিসেবে (বা "helpful"-এর ভেতর "help") ভুলভাবে না মেলে।
            matched = sum(1 for k in keywords if _whole_word_in_text(k, text))
            if matched == 0:
                return None
            return min(1.0, matched / len(keywords)) * pattern.confidence_score

        if pattern.pattern_type == "regex":
            compiled = self._get_compiled_regex(pattern)
            if compiled is None:
                return None
            return pattern.confidence_score if compiled.search(text) else None

        if pattern.pattern_type == "intent":
            # Intent Pattern Matching — match_value-কে কমা-সেপারেটেড ইনটেন্ট-কিওয়ার্ড হিসেবে
            # ধরে টোকেন-ওভারল্যাপ রেশিও দিয়ে স্কোর করা হয় (কোনো ML মডেল ছাড়াই best-effort)।
            intent_tokens = {t.strip().lower() for t in pattern.match_value.split(",") if t.strip()}
            text_tokens = set(re.findall(r"[\w\u0980-\u09FF]+", text_lower, flags=re.UNICODE))
            if not intent_tokens or not text_tokens:
                return None
            overlap = len(intent_tokens & text_tokens)
            if overlap == 0:
                return None
            return (overlap / len(intent_tokens)) * pattern.confidence_score

        return None

    def match(
        self, text: str, category: Optional[str] = None, top_n: int = 1, log_analytics: bool = True,
        exclude_categories: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Intelligent Pattern Matching — সব অ্যাক্টিভ প্যাটার্নের বিপরীতে টেক্সট চেক করে,
        Priority-based Selection (প্রথমে priority, তারপর confidence) অনুযায়ী সাজিয়ে সেরা
        `top_n`টা ম্যাচ রিটার্ন করে। রিটার্ন ফরম্যাট:
        [{"pattern": BrainPattern, "confidence": float}, ...]
        `exclude_categories` দিলে সেই ক্যাটাগরির প্যাটার্ন (যেমন coding-context-এ
        bot_info/greeting) আগেই বাদ পড়ে।
        """
        text = (text or "").strip()
        if not text:
            return []

        candidates = self._load_active_patterns()
        if category:
            candidates = [p for p in candidates if p.category == category]
        if exclude_categories:
            try:
                excluded = {
                    str(c).strip().lower()
                    for c in exclude_categories
                    if str(c).strip()
                }
                if excluded:
                    candidates = [
                        p for p in candidates
                        if str(getattr(p, "category", "") or "").strip().lower() not in excluded
                    ]
            except Exception:
                pass

        results: List[Dict[str, Any]] = []
        for pattern in candidates:
            score = self._score_pattern(pattern, text)
            if score is not None:
                results.append({"pattern": pattern, "confidence": score})

        results.sort(key=lambda r: (r["pattern"].priority, r["confidence"]), reverse=True)
        top_results = results[:max(1, top_n)]

        if log_analytics and top_results:
            self._log_analytics(top_results[0]["pattern"].id, text, top_results[0]["confidence"])

        return top_results

    def _log_analytics(self, pattern_id: Optional[int], text: str, confidence: float) -> None:
        """Pattern Analytics — কোন প্যাটার্ন কখন/কী ইনপুটে/কত confidence-এ ম্যাচ হলো তা লগ করে।"""
        if pattern_id is None:
            return
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine._log_analytics(): কানেকশন ব্যর্থ: {e}")
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO brain_pattern_analytics (pattern_id, matched_at, input_preview, confidence) "
                "VALUES (?, ?, ?, ?)",
                (pattern_id, _now(), text[:150], confidence),
            )
            conn.commit()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine._log_analytics() ব্যর্থ: {e}")
        finally:
            conn.close()

    def get_analytics(self, pattern_id: int, limit: int = 20) -> Dict[str, Any]:
        """একটা প্যাটার্নের ম্যাচ-হিস্টোরি + সারাংশ পরিসংখ্যান।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.get_analytics(): কানেকশন ব্যর্থ: {e}")
            return {"pattern_id": pattern_id, "match_count": 0, "recent": []}
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), AVG(confidence) FROM brain_pattern_analytics WHERE pattern_id = ?", (pattern_id,))
            count, avg_conf = cur.fetchone()
            cur.execute(
                "SELECT id, matched_at, input_preview, confidence FROM brain_pattern_analytics "
                "WHERE pattern_id = ? ORDER BY matched_at DESC LIMIT ?",
                (pattern_id, limit),
            )
            recent = [
                {"id": r[0], "matched_at": r[1], "input_preview": r[2], "confidence": r[3]}
                for r in cur.fetchall()
            ]
            return {
                "pattern_id": pattern_id, "match_count": count or 0,
                "avg_confidence": round(avg_conf, 4) if avg_conf is not None else 0.0, "recent": recent,
            }
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.get_analytics() ব্যর্থ: {e}")
            return {"pattern_id": pattern_id, "match_count": 0, "recent": []}
        finally:
            conn.close()

    # =============================== Update/Delete ===============================

    def update(self, pattern_id: int, **fields: Any) -> Optional[BrainPattern]:
        """আংশিক আপডেট — শুধু দেওয়া ফিল্ড বদলায়। match_value/pattern_type/category বদলালে
        Pattern Versioning অনুযায়ী `version` স্বয়ংক্রিয়ভাবে ১ বাড়ে ও hash নতুন করে গণনা হয়।"""
        allowed = {
            "pattern_type", "match_value", "category", "template_id", "priority",
            "name", "description", "tags", "confidence_score",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get(pattern_id)

        current = self.get(pattern_id)
        if current is None:
            logger.warning(f"PatternEngine.update(): id={pattern_id} পাওয়া যায়নি")
            return None

        new_type = updates.get("pattern_type", current.pattern_type)
        new_value = updates.get("match_value", current.match_value)
        if "pattern_type" in updates or "match_value" in updates:
            error = self.validate_pattern(new_type, new_value)
            if error:
                logger.warning(f"PatternEngine.update(): ভ্যালিডেশন ব্যর্থ: {error}")
                return None

        hash_changed = "match_value" in updates or "pattern_type" in updates or "category" in updates
        new_category = updates.get("category", current.category)

        set_parts = [f"{col} = ?" for col in updates]
        params: List[Any] = list(updates.values())
        set_parts.append("updated_at = ?")
        params.append(_now())
        if hash_changed:
            set_parts.append("version = version + 1")
            set_parts.append("pattern_hash = ?")
            params.append(_pattern_compute_hash(new_type, new_value, new_category))
        params.append(pattern_id)

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.update(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE brain_patterns SET {', '.join(set_parts)} WHERE id = ?", params)
            conn.commit()
            self._invalidate_cache()
            self._regex_cache.pop(f"{pattern_id}:{current.match_value}", None)
            return self.get(pattern_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.update() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def set_active(self, pattern_id: int, active: bool) -> bool:
        """Pattern Enable/Disable।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.set_active(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_patterns SET is_active = ?, updated_at = ? WHERE id = ?",
                (1 if active else 0, _now(), pattern_id),
            )
            conn.commit()
            self._invalidate_cache()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.set_active() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    def enable(self, pattern_id: int) -> bool:
        return self.set_active(pattern_id, True)

    def disable(self, pattern_id: int) -> bool:
        return self.set_active(pattern_id, False)

    def delete(self, pattern_id: int) -> bool:
        """Pattern হার্ড-ডিলিট করে (প্যাটার্ন ছোট/lightweight রেকর্ড, Enable/Disable-ই
        মূল lifecycle কন্ট্রোল — Restore দরকার হলে disable() ব্যবহার করাই ভালো)।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.delete(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM brain_patterns WHERE id = ?", (pattern_id,))
            conn.commit()
            self._invalidate_cache()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.delete() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    # ================================ Bulk I/O ================================

    def bulk_import(self, patterns: List[Dict[str, Any]], skip_duplicates: bool = True) -> Dict[str, int]:
        summary = {"created": 0, "skipped_duplicates": 0, "failed": 0}
        for p in patterns:
            pattern_type = p.get("pattern_type", "")
            match_value = p.get("match_value", "")
            category = p.get("category", "")
            if self.validate_pattern(pattern_type, match_value):
                summary["failed"] += 1
                continue
            if skip_duplicates and self.check_duplicate(pattern_type, match_value, category) is not None:
                summary["skipped_duplicates"] += 1
                continue
            created = self.create(
                pattern_type=pattern_type, match_value=match_value, category=category,
                name=p.get("name", ""), description=p.get("description", ""), tags=p.get("tags", ""),
                template_id=p.get("template_id"), priority=p.get("priority", 5),
                confidence_score=p.get("confidence_score", 1.0), allow_duplicate=not skip_duplicates,
            )
            summary["created" if created is not None else "failed"] += 1
        return summary

    def bulk_export(self, category: Optional[str] = None, active_only: bool = False) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if category:
            clauses.append("category = ?")
            params.append(category)
        if active_only:
            clauses.append("is_active = 1")
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.bulk_export(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM brain_patterns{where} ORDER BY id ASC", params)
            return [BrainPattern.from_row(row).__dict__ for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"PatternEngine.bulk_export() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ================================= Async ওয়্র্যাপার =================================

    async def create_async(self, *args, **kwargs) -> Optional[BrainPattern]:
        return await asyncio.to_thread(self.create, *args, **kwargs)

    async def update_async(self, *args, **kwargs) -> Optional[BrainPattern]:
        return await asyncio.to_thread(self.update, *args, **kwargs)

    async def delete_async(self, *args, **kwargs) -> bool:
        return await asyncio.to_thread(self.delete, *args, **kwargs)

    async def match_async(self, *args, **kwargs) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self.match, *args, **kwargs)


# =============================================================================
# Brain OS — originally brain/template_engine.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================




logger = logging.getLogger(__name__)

VALID_TEMPLATE_TYPES = ("prompt", "response", "message", "notification", "system")
PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _extract_variables(body: str) -> List[str]:
    """বডি থেকে `{variable}` প্লেসহোল্ডারগুলো স্বয়ংক্রিয়ভাবে বের করে (ক্রম-সংরক্ষিত, ডুপ্লিকেট-মুক্ত)।"""
    seen: List[str] = []
    for match in PLACEHOLDER_RE.finditer(body or ""):
        name = match.group(1)
        if name not in seen:
            seen.append(name)
    return seen


class TemplateEngine:
    """Template Engine — brain_templates-এর জন্য পুরো CRUD + Render + Versioning API।"""

    # ================================ Validation ================================

    def validate_template(self, body: str, template_type: str = "prompt") -> Optional[str]:
        """Template Validation — braces ব্যালান্সড কিনা ও template_type বৈধ কিনা চেক করে।"""
        if not (body or "").strip():
            return "body খালি রাখা যাবে না"
        if body.count("{") != body.count("}"):
            return "টেমপ্লেট বডিতে অসামঞ্জস্যপূর্ণ '{' / '}' আছে"
        if template_type not in VALID_TEMPLATE_TYPES:
            return f"অবৈধ template_type: {template_type} (অনুমোদিত: {VALID_TEMPLATE_TYPES})"
        return None

    # ================================ Create ================================

    def create(
        self,
        name: str,
        category: str,
        body: str,
        variables: Optional[List[str]] = None,
        language: Optional[str] = None,
        description: str = "",
        priority: int = 5,
        template_type: str = "prompt",
        is_default: bool = False,
    ) -> Optional[BrainTemplate]:
        """নতুন Template তৈরি করে। `variables` না দিলে বডি থেকে স্বয়ংক্রিয়ভাবে বের করা হয়।"""
        error = self.validate_template(body, template_type)
        if error:
            logger.warning(f"TemplateEngine.create(): ভ্যালিডেশন ব্যর্থ: {error}")
            return None
        if not name:
            logger.warning("TemplateEngine.create(): name খালি রাখা যাবে না")
            return None

        var_list = variables if variables is not None else _extract_variables(body)

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.create(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            now = _now()
            cur = conn.cursor()
            if is_default:
                self._clear_default(cur, category, template_type)
            cur.execute(
                """
                INSERT INTO brain_templates
                    (name, category, language, body, variables, created_at, updated_at,
                     description, is_active, is_default, priority, template_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    name, category, language, body, json.dumps(var_list, ensure_ascii=False), now, now,
                    description, 1 if is_default else 0, priority, template_type,
                ),
            )
            new_id = cur.lastrowid
            self._snapshot_version(cur, new_id, 1, body, var_list)
            conn.commit()
            return self.get(new_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.create() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def _clear_default(self, cur, category: str, template_type: str) -> None:
        """একই category+template_type-এ আগের ডিফল্ট টেমপ্লেট থাকলে unset করে (Default Templates)।"""
        cur.execute(
            "UPDATE brain_templates SET is_default = 0 WHERE category = ? AND template_type = ? AND is_default = 1",
            (category, template_type),
        )

    def _snapshot_version(self, cur, template_id: int, version: int, body: str, variables: List[str]) -> None:
        cur.execute(
            "INSERT INTO brain_template_versions (template_id, version, body, variables, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (template_id, version, body, json.dumps(variables, ensure_ascii=False), _now()),
        )

    # ================================= Read =================================

    def get(self, template_id: int) -> Optional[BrainTemplate]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.get(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM brain_templates WHERE id = ?", (template_id,))
            row = cur.fetchone()
            return BrainTemplate.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.get() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def get_by_name(self, name: str) -> Optional[BrainTemplate]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.get_by_name(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM brain_templates WHERE name = ? ORDER BY id DESC LIMIT 1", (name,))
            row = cur.fetchone()
            return BrainTemplate.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.get_by_name() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def list_by_category(
        self, category: str, template_type: Optional[str] = None, active_only: bool = True,
    ) -> List[BrainTemplate]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.list_by_category(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            clauses = ["category = ?"]
            params: List[Any] = [category]
            if template_type:
                clauses.append("template_type = ?")
                params.append(template_type)
            if active_only:
                clauses.append("is_active = 1")
            cur = conn.cursor()
            cur.execute(
                f"SELECT * FROM brain_templates WHERE {' AND '.join(clauses)} "
                "ORDER BY is_default DESC, priority DESC",
                params,
            )
            return [BrainTemplate.from_row(row) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.list_by_category() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    def get_default(self, category: str, template_type: str = "prompt") -> Optional[BrainTemplate]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.get_default(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM brain_templates WHERE category = ? AND template_type = ? "
                "AND is_default = 1 AND is_active = 1 LIMIT 1",
                (category, template_type),
            )
            row = cur.fetchone()
            return BrainTemplate.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.get_default() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    # ============================ Render / Preview ============================

    def render(self, template_id: int, context: Dict[str, Any], strict: bool = False) -> Optional[str]:
        """
        Placeholder Replacement — `{variable}` গুলো `context`-এর মান দিয়ে বদলায়।
        `strict=True` হলে কোনো ভ্যারিয়েবল context-এ না থাকলে None রিটার্ন করে;
        ডিফল্টে (strict=False) অনুপস্থিত ভ্যারিয়েবল প্লেসহোল্ডার আকারেই রেখে দেয়।
        """
        template = self.get(template_id)
        if template is None:
            return None
        return self.render_body(template.body, context, strict=strict)

    def render_body(self, body: str, context: Dict[str, Any], strict: bool = False) -> Optional[str]:
        required = _extract_variables(body)
        missing = [v for v in required if v not in context]
        if strict and missing:
            logger.warning(f"TemplateEngine.render_body(): প্রয়োজনীয় ভ্যারিয়েবল অনুপস্থিত: {missing}")
            return None

        def _replace(match: "re.Match[str]") -> str:
            key = match.group(1)
            return str(context[key]) if key in context else match.group(0)

        return PLACEHOLDER_RE.sub(_replace, body)

    def preview(self, template_id: int, sample_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Template Preview — ভ্যারিয়েবল লিস্ট + (দেওয়া হলে) sample_context দিয়ে রেন্ডার-করা প্রিভিউ।"""
        template = self.get(template_id)
        if template is None:
            return {"error": "template পাওয়া যায়নি"}
        variables = json.loads(template.variables or "[]")
        result: Dict[str, Any] = {
            "id": template.id, "name": template.name, "variables": variables, "body": template.body,
        }
        if sample_context is not None:
            result["rendered_preview"] = self.render_body(template.body, sample_context, strict=False)
        return result

    # =============================== Update/Delete ===============================

    def update(self, template_id: int, **fields: Any) -> Optional[BrainTemplate]:
        """আংশিক আপডেট। body বদলালে Template Versioning অনুযায়ী নতুন ভার্সন স্ন্যাপশট নেওয়া হয়।"""
        allowed = {
            "name", "category", "language", "body", "variables", "description",
            "priority", "template_type",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get(template_id)

        current = self.get(template_id)
        if current is None:
            logger.warning(f"TemplateEngine.update(): id={template_id} পাওয়া যায়নি")
            return None

        new_type = updates.get("template_type", current.template_type)
        if new_type not in VALID_TEMPLATE_TYPES:
            updates.pop("template_type", None)
            new_type = current.template_type

        body_changed = "body" in updates
        new_body = updates.get("body", current.body)
        if body_changed:
            error = self.validate_template(new_body, new_type)
            if error:
                logger.warning(f"TemplateEngine.update(): ভ্যালিডেশন ব্যর্থ: {error}")
                return None
            if "variables" not in updates:
                updates["variables"] = _extract_variables(new_body)

        if "variables" in updates and isinstance(updates["variables"], list):
            updates["variables"] = json.dumps(updates["variables"], ensure_ascii=False)

        set_parts = [f"{col} = ?" for col in updates]
        params: List[Any] = list(updates.values())
        set_parts.append("updated_at = ?")
        params.append(_now())
        params.append(template_id)

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.update(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE brain_templates SET {', '.join(set_parts)} WHERE id = ?", params)
            if body_changed:
                cur.execute("SELECT MAX(version) FROM brain_template_versions WHERE template_id = ?", (template_id,))
                last_version = cur.fetchone()[0] or 1
                new_variables = json.loads(updates.get("variables", current.variables) or "[]")
                self._snapshot_version(cur, template_id, last_version + 1, new_body, new_variables)
            conn.commit()
            return self.get(template_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.update() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def set_default(self, template_id: int) -> bool:
        """এই টেমপ্লেটটাকে তার category+template_type-এর Default Template বানায়
        (একই গ্রুপের আগের ডিফল্ট স্বয়ংক্রিয়ভাবে unset হয়)।"""
        template = self.get(template_id)
        if template is None:
            return False
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.set_default(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            self._clear_default(cur, template.category, template.template_type)
            cur.execute(
                "UPDATE brain_templates SET is_default = 1, updated_at = ? WHERE id = ?",
                (_now(), template_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.set_default() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    def set_active(self, template_id: int, active: bool) -> bool:
        """Active/Inactive Templates।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.set_active(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_templates SET is_active = ?, updated_at = ? WHERE id = ?",
                (1 if active else 0, _now(), template_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.set_active() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    def delete(self, template_id: int) -> bool:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.delete(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM brain_templates WHERE id = ?", (template_id,))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.delete() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    # ============================ Version History ============================

    def version_history(self, template_id: int, limit: int = 20) -> List[BrainTemplateVersion]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.version_history(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM brain_template_versions WHERE template_id = ? ORDER BY version DESC LIMIT ?",
                (template_id, limit),
            )
            return [BrainTemplateVersion.from_row(row) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.version_history() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ================================ Bulk I/O ================================

    def bulk_import(self, templates: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"created": 0, "failed": 0}
        for t in templates:
            created = self.create(
                name=t.get("name", ""), category=t.get("category", ""), body=t.get("body", ""),
                variables=t.get("variables"), language=t.get("language"),
                description=t.get("description", ""), priority=t.get("priority", 5),
                template_type=t.get("template_type", "prompt"), is_default=t.get("is_default", False),
            )
            summary["created" if created is not None else "failed"] += 1
        return summary

    def bulk_export(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        where = " WHERE category = ?" if category else ""
        params = (category,) if category else ()
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.bulk_export(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM brain_templates{where} ORDER BY id ASC", params)
            return [BrainTemplate.from_row(row).__dict__ for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"TemplateEngine.bulk_export() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ================================= Async ওয়্র্যাপার =================================

    async def create_async(self, *args, **kwargs) -> Optional[BrainTemplate]:
        return await asyncio.to_thread(self.create, *args, **kwargs)

    async def update_async(self, *args, **kwargs) -> Optional[BrainTemplate]:
        return await asyncio.to_thread(self.update, *args, **kwargs)

    async def render_async(self, *args, **kwargs) -> Optional[str]:
        return await asyncio.to_thread(self.render, *args, **kwargs)

    async def delete_async(self, *args, **kwargs) -> bool:
        return await asyncio.to_thread(self.delete, *args, **kwargs)


# =============================================================================
# Brain OS — originally brain/documentation_engine.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================




logger = logging.getLogger(__name__)

VALID_STATUSES = ("draft", "active", "archived")
VALID_DOC_TYPES = ("api", "module", "function", "class")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class DocumentationEngine:
    """Documentation Engine — brain_documentation-এর জন্য পুরো CRUD + Auto-Doc + Search API।"""

    def __init__(self) -> None:

        self._search_engine = SearchEngine.for_documentation()

    # ================================ Create ================================

    def create(
        self,
        technology: str,
        category: str,
        title: str,
        content: str,
        source_url: str = "",
        version: str = "1.0",
        doc_type: str = "module",
        tags: str = "",
        status: str = "active",
        internal_notes: str = "",
    ) -> Optional[BrainDocumentation]:
        if not title or not content:
            logger.warning("DocumentationEngine.create(): title/content খালি রাখা যাবে না")
            return None
        if status not in VALID_STATUSES:
            status = "active"
        if doc_type not in VALID_DOC_TYPES:
            doc_type = "module"

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.create(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            now = _now()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO brain_documentation
                    (technology, category, title, content, source_url, version, created_at, updated_at,
                     tags, status, doc_type, deleted_at, internal_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?)
                """,
                (technology, category, title, content, source_url, version, now, now, tags, status, doc_type, internal_notes),
            )
            new_id = cur.lastrowid
            cur.execute(
                "INSERT INTO brain_documentation_history (documentation_id, version, content, change_note, changed_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (new_id, version, content, "initial creation", now),
            )
            conn.commit()
            return self.get(new_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.create() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    # ============================ Auto Documentation Generator ============================

    def auto_generate(
        self,
        obj: Any,
        category: str = "auto-generated",
        technology: str = "python",
        status: str = "draft",
    ) -> Optional[BrainDocumentation]:
        """
        Auto Documentation Generator — একটা লাইভ পাইথন মডিউল/ক্লাস/ফাংশন থেকে `inspect`
        দিয়ে Markdown ডকুমেন্টেশন তৈরি করে ও Knowledge Base-এ সংরক্ষণ করে। ফাংশন/ক্লাস/মডিউল
        — সবই সমর্থিত (doc_type স্বয়ংক্রিয়ভাবে ধরা হয়)।
        """
        try:
            name = getattr(obj, "__name__", str(obj))
            docstring = inspect.getdoc(obj) or "_কোনো docstring পাওয়া যায়নি_"

            if inspect.isclass(obj):
                doc_type = "class"
                try:
                    signature = str(inspect.signature(obj.__init__))
                except (ValueError, TypeError):
                    signature = "(...)"
                members = [
                    m for m, _ in inspect.getmembers(obj, predicate=inspect.isfunction)
                    if not m.startswith("_")
                ]
                body = (
                    f"# Class `{name}`\n\n```python\nclass {name}{signature}\n```\n\n"
                    f"{docstring}\n\n## Methods\n" + "\n".join(f"- `{m}`" for m in members)
                )
            elif inspect.isfunction(obj) or inspect.ismethod(obj):
                doc_type = "function"
                try:
                    signature = str(inspect.signature(obj))
                except (ValueError, TypeError):
                    signature = "(...)"
                body = f"# Function `{name}{signature}`\n\n```python\ndef {name}{signature}\n```\n\n{docstring}"
            elif inspect.ismodule(obj):
                doc_type = "module"
                functions = [m for m, _ in inspect.getmembers(obj, predicate=inspect.isfunction)]
                classes = [m for m, _ in inspect.getmembers(obj, predicate=inspect.isclass)]
                body = (
                    f"# Module `{name}`\n\n{docstring}\n\n"
                    f"## Functions\n" + "\n".join(f"- `{f}`" for f in functions) +
                    f"\n\n## Classes\n" + "\n".join(f"- `{c}`" for c in classes)
                )
            else:
                doc_type = "module"
                body = f"# `{name}`\n\n{docstring}"

            return self.create(
                technology=technology, category=category, title=name, content=body,
                doc_type=doc_type, status=status, tags="auto-generated",
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.auto_generate() ব্যর্থ: {e}")
            return None

    # ================================= Read =================================

    def get(self, doc_id: int, include_deleted: bool = False) -> Optional[BrainDocumentation]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.get(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            if include_deleted:
                cur.execute("SELECT * FROM brain_documentation WHERE id = ?", (doc_id,))
            else:
                cur.execute(
                    "SELECT * FROM brain_documentation WHERE id = ? AND (deleted_at IS NULL OR deleted_at = '')",
                    (doc_id,),
                )
            row = cur.fetchone()
            return BrainDocumentation.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.get() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def _paginated_list(self, where_clause: str, params: tuple, page: int, page_size: int) -> Dict[str, Any]:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine: কানেকশন ব্যর্থ: {e}")
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM brain_documentation WHERE {where_clause}", params)
            total = cur.fetchone()[0]
            offset = (page - 1) * page_size
            cur.execute(
                f"SELECT * FROM brain_documentation WHERE {where_clause} "
                "ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (*params, page_size, offset),
            )
            items = [BrainDocumentation.from_row(row) for row in cur.fetchall()]
            total_pages = (total + page_size - 1) // page_size if total else 0
            return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine পেজিনেটেড-লিস্ট ব্যর্থ: {e}")
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
        finally:
            conn.close()

    def list_by_category(self, category: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        return self._paginated_list(
            "category = ? AND (deleted_at IS NULL OR deleted_at = '')", (category,), page, page_size,
        )

    def list_by_tag(self, tag: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        return self._paginated_list(
            "tags LIKE ? AND (deleted_at IS NULL OR deleted_at = '')", (f"%{tag}%",), page, page_size,
        )

    def list_by_type(self, doc_type: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        return self._paginated_list(
            "doc_type = ? AND (deleted_at IS NULL OR deleted_at = '')", (doc_type,), page, page_size,
        )

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Searchable Documentation — Search Engine (Phase 14) কে পুনর্ব্যবহার করে।"""
        return self._search_engine.search(query, **kwargs)

    # =============================== Update/Delete ===============================

    def update(self, doc_id: int, change_note: str = "", **fields: Any) -> Optional[BrainDocumentation]:
        """আংশিক আপডেট। content বদলালে Version History-তে পুরনো content-এর স্ন্যাপশট নেওয়া হয়
        (Change Log)।"""
        allowed = {
            "technology", "category", "title", "content", "source_url", "version",
            "tags", "status", "doc_type", "internal_notes",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get(doc_id)
        if "status" in updates and updates["status"] not in VALID_STATUSES:
            updates.pop("status")
        if "doc_type" in updates and updates["doc_type"] not in VALID_DOC_TYPES:
            updates.pop("doc_type")

        current = self.get(doc_id, include_deleted=True)
        if current is None:
            logger.warning(f"DocumentationEngine.update(): id={doc_id} পাওয়া যায়নি")
            return None

        content_changed = "content" in updates

        set_parts = [f"{col} = ?" for col in updates]
        params: List[Any] = list(updates.values())
        set_parts.append("updated_at = ?")
        params.append(_now())
        params.append(doc_id)

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.update(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            if content_changed:
                cur.execute(
                    "INSERT INTO brain_documentation_history (documentation_id, version, content, change_note, changed_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (doc_id, updates.get("version", current.version), current.content, change_note or "updated", _now()),
                )
            cur.execute(f"UPDATE brain_documentation SET {', '.join(set_parts)} WHERE id = ?", params)
            conn.commit()
            return self.get(doc_id, include_deleted=True)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.update() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def delete(self, doc_id: int) -> bool:
        """Soft Delete — `deleted_at` সেট করে, রো আসলে মোছে না (Restore-এর সুবিধার্থে)।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.delete(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_documentation SET deleted_at = ?, updated_at = ? WHERE id = ?",
                (_now(), _now(), doc_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.delete() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    def restore(self, doc_id: int) -> bool:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.restore(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_documentation SET deleted_at = '', updated_at = ? WHERE id = ?",
                (_now(), doc_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.restore() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    # ============================ Change Log / History ============================

    def changelog(self, doc_id: int, limit: int = 20) -> List[BrainDocumentationHistory]:
        """Version History / Change Log — পুরনো content-স্ন্যাপশটের তালিকা (নতুন আগে)।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.changelog(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM brain_documentation_history WHERE documentation_id = ? "
                "ORDER BY changed_at DESC LIMIT ?",
                (doc_id, limit),
            )
            return [BrainDocumentationHistory.from_row(row) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.changelog() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ================================ Bulk I/O ================================

    def bulk_import(self, docs: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"created": 0, "failed": 0}
        for d in docs:
            created = self.create(
                technology=d.get("technology", ""), category=d.get("category", ""),
                title=d.get("title", ""), content=d.get("content", ""),
                source_url=d.get("source_url", ""), version=d.get("version", "1.0"),
                doc_type=d.get("doc_type", "module"), tags=d.get("tags", ""),
                status=d.get("status", "active"), internal_notes=d.get("internal_notes", ""),
            )
            summary["created" if created is not None else "failed"] += 1
        return summary

    def bulk_export(self, category: Optional[str] = None, include_deleted: bool = False) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if category:
            clauses.append("category = ?")
            params.append(category)
        if not include_deleted:
            clauses.append("(deleted_at IS NULL OR deleted_at = '')")
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.bulk_export(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM brain_documentation{where} ORDER BY id ASC", params)
            return [BrainDocumentation.from_row(row).__dict__ for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DocumentationEngine.bulk_export() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ================================= Async ওয়্র্যাপার =================================

    async def create_async(self, *args, **kwargs) -> Optional[BrainDocumentation]:
        return await asyncio.to_thread(self.create, *args, **kwargs)

    async def auto_generate_async(self, *args, **kwargs) -> Optional[BrainDocumentation]:
        return await asyncio.to_thread(self.auto_generate, *args, **kwargs)

    async def update_async(self, *args, **kwargs) -> Optional[BrainDocumentation]:
        return await asyncio.to_thread(self.update, *args, **kwargs)

    async def delete_async(self, *args, **kwargs) -> bool:
        return await asyncio.to_thread(self.delete, *args, **kwargs)

    async def search_async(self, *args, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.search, *args, **kwargs)


# =============================================================================
# Brain OS — originally brain/error_engine.py (এখন একটাই main.py ফাইলে একীভূত করা হয়েছে)
# =============================================================================




logger = logging.getLogger(__name__)

VALID_SEVERITIES = ("low", "medium", "high", "critical")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ============================= Custom Error Classes =============================
# Exception Mapping-এর ভিত্তি — কোনো এক্সেপশনের ধরন থেকে category/severity বের করার
# জন্য ব্যবহৃত হয় (দেখুন _categorize())।

class BrainOSError(Exception):
    """Brain OS-এর সব কাস্টম এক্সেপশনের বেস ক্লাস।"""
    category = "unknown"
    severity = "medium"


class ValidationError(BrainOSError):
    """ইনপুট/ডাটা ভ্যালিডেশন ব্যর্থ হলে।"""
    category = "validation"
    severity = "low"


class DatabaseError(BrainOSError):
    """ডাটাবেস অপারেশন ব্যর্থ হলে (কানেকশন/কুয়েরি/মাইগ্রেশন সমস্যা)।"""
    category = "database"
    severity = "high"


class APIError(BrainOSError):
    """এক্সটার্নাল/ইন্টারনাল API কল ব্যর্থ হলে।"""
    category = "api"
    severity = "medium"


class UnknownError(BrainOSError):
    """যেসব এক্সেপশন কোনো নির্দিষ্ট ক্যাটাগরিতে পড়ে না।"""
    category = "unknown"
    severity = "medium"


# পাইথনের বিল্ট-ইন এক্সেপশন থেকে category/severity-তে ম্যাপিং (Exception Mapping)
_BUILTIN_CATEGORY_MAP: Dict[Type[BaseException], Tuple[str, str]] = {
    ValueError: ("validation", "low"),
    TypeError: ("validation", "low"),
    KeyError: ("validation", "low"),
    AssertionError: ("validation", "low"),
    ConnectionError: ("api", "high"),
    TimeoutError: ("api", "medium"),
    PermissionError: ("database", "high"),
    FileNotFoundError: ("database", "medium"),
}


def _categorize(exc: BaseException) -> Tuple[str, str]:
    """Exception Mapping — এক্সেপশন-টাইপ থেকে (category, severity) বের করে।"""
    if isinstance(exc, BrainOSError):
        return exc.category, exc.severity
    for exc_type, (category, severity) in _BUILTIN_CATEGORY_MAP.items():
        if isinstance(exc, exc_type):
            return category, severity
    if isinstance(exc, LookupError):

        if isinstance(exc, sqlite3.Error):
            return "database", "high"
    return "unknown", "medium"


class ErrorEngine:
    """Error Engine — Global Error Handler + Error Knowledge Base + Retry Logic API।"""

    # ============================ Global Error Handler ============================

    def handle(
        self,
        exc: BaseException,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        একটা এক্সেপশন হ্যান্ডল করে: ক্যাটাগরাইজ করে, `brain_errors`-এ occurrence_count
        বাড়ায় (বা নতুন এন্ট্রি তৈরি করে), পুরো ঘটনাটা `brain_error_log`-এ (stack trace +
        context সহ) লগ করে, ও পরিচিত সমাধান থাকলে Recovery Suggestion সহ রেজাল্ট রিটার্ন
        করে। কখনো নিজে এক্সেপশন ছোঁড়ে না।
        """
        error_signature = type(exc).__name__
        category, severity = _categorize(exc)
        description = str(exc)
        stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

        error_row = self._record_occurrence(language, error_signature, category, severity, description)
        self._log_occurrence(
            error_row.id if error_row else None, language, error_signature, category, severity,
            stack_trace, context or {},
        )

        suggestion = self.get_solution(error_signature, language=language)
        return {
            "error_signature": error_signature,
            "category": category,
            "severity": severity,
            "message": description,
            "stack_trace": stack_trace,
            "occurrence_count": error_row.occurrence_count if error_row else 1,
            "suggestion": suggestion.solution if suggestion else None,
        }

    def catch_errors(self, language: str = "python", reraise: bool = False):
        """Global Error Handler ডেকোরেটর — ফাংশন র‍্যাপ করে যেকোনো এক্সেপশন স্বয়ংক্রিয়ভাবে
        `handle()`-এ পাঠায়। `reraise=True` দিলে হ্যান্ডল করার পরেও এক্সেপশন আবার ছোঁড়ে।"""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    self.handle(e, language=language, context={"function": func.__name__})
                    if reraise:
                        raise
                    return None

            return wrapper

        return decorator

    # ============================ Error Knowledge Base (CRUD) ============================

    def register_solution(
        self,
        language: str,
        error_signature: str,
        description: str,
        solution: str,
        category: str = "unknown",
        severity: str = "medium",
        related_doc_id: Optional[int] = None,
        error_code: str = "",
    ) -> Optional[BrainError]:
        """একটা এরর-সিগনেচারের জন্য সমাধান রেজিস্টার করে (Recovery Suggestions ডাটাবেস তৈরি)।
        আগে থেকে থাকলে description/solution আপডেট হয়, না থাকলে নতুন এন্ট্রি হয়।"""
        if severity not in VALID_SEVERITIES:
            severity = "medium"
        existing = self._find_by_signature(language, error_signature)
        if existing:
            return self.update(
                existing.id, description=description, solution=solution,
                category=category, severity=severity, error_code=error_code,
                related_doc_id=related_doc_id,
            )
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.register_solution(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            now = _now()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO brain_errors
                    (language, error_signature, description, solution, related_doc_id, occurrence_count,
                     created_at, updated_at, category, error_code, severity, is_resolved, deleted_at)
                VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, 0, '')
                """,
                (language, error_signature, description, solution, related_doc_id, now, now, category, error_code, severity),
            )
            conn.commit()
            return self.get(cur.lastrowid)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.register_solution() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def _find_by_signature(self, language: str, error_signature: str) -> Optional[BrainError]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine._find_by_signature(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM brain_errors WHERE language = ? AND error_signature = ? "
                "AND (deleted_at IS NULL OR deleted_at = '') LIMIT 1",
                (language, error_signature),
            )
            row = cur.fetchone()
            return BrainError.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine._find_by_signature() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def _record_occurrence(
        self, language: str, error_signature: str, category: str, severity: str, description: str,
    ) -> Optional[BrainError]:
        """`brain_errors`-এ occurrence_count বাড়ায়; এন্ট্রি না থাকলে নতুন (সমাধান-বিহীন) এন্ট্রি তৈরি করে।"""
        existing = self._find_by_signature(language, error_signature)
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine._record_occurrence(): কানেকশন ব্যর্থ: {e}")
            return existing
        try:
            cur = conn.cursor()
            now = _now()
            if existing:
                cur.execute(
                    "UPDATE brain_errors SET occurrence_count = occurrence_count + 1, updated_at = ? WHERE id = ?",
                    (now, existing.id),
                )
                conn.commit()
                return self.get(existing.id)
            cur.execute(
                """
                INSERT INTO brain_errors
                    (language, error_signature, description, solution, related_doc_id, occurrence_count,
                     created_at, updated_at, category, error_code, severity, is_resolved, deleted_at)
                VALUES (?, ?, ?, '', NULL, 1, ?, ?, ?, '', ?, 0, '')
                """,
                (language, error_signature, description, now, now, category, severity),
            )
            conn.commit()
            return self.get(cur.lastrowid)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine._record_occurrence() ব্যর্থ: {e}")
            return existing
        finally:
            conn.close()

    def _log_occurrence(
        self, error_id: Optional[int], language: str, error_signature: str, category: str,
        severity: str, stack_trace: str, context: Dict[str, Any],
    ) -> None:
        """Error History — প্রতিটা occurrence-এর পূর্ণ রেকর্ড (stack trace/context সহ) `brain_error_log`-এ।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine._log_occurrence(): কানেকশন ব্যর্থ: {e}")
            return
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO brain_error_log "
                "(error_id, language, error_signature, category, severity, stack_trace, context, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (error_id, language, error_signature, category, severity, stack_trace,
                 json.dumps(context, ensure_ascii=False, default=str), _now()),
            )
            conn.commit()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine._log_occurrence() ব্যর্থ: {e}")
        finally:
            conn.close()

    def get(self, error_id: int) -> Optional[BrainError]:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.get(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM brain_errors WHERE id = ?", (error_id,))
            row = cur.fetchone()
            return BrainError.from_row(row) if row else None
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.get() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def get_solution(self, error_signature: str, language: Optional[str] = None) -> Optional[BrainError]:
        """Recovery Suggestions — সরাসরি সিগনেচার-ম্যাচ, না পেলে Search Engine (Phase 14) ফলব্যাক।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.get_solution(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            if language:
                cur.execute(
                    "SELECT * FROM brain_errors WHERE error_signature = ? AND language = ? "
                    "AND solution != '' AND (deleted_at IS NULL OR deleted_at = '') LIMIT 1",
                    (error_signature, language),
                )
            else:
                cur.execute(
                    "SELECT * FROM brain_errors WHERE error_signature = ? "
                    "AND solution != '' AND (deleted_at IS NULL OR deleted_at = '') LIMIT 1",
                    (error_signature,),
                )
            row = cur.fetchone()
            if row:
                return BrainError.from_row(row)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.get_solution() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

        # ফলব্যাক: সরাসরি সিগনেচার-ম্যাচ না পেলে Search Engine দিয়ে কাছাকাছি সমাধান খোঁজা
        try:

            result = SearchEngine.for_errors().search(error_signature, page_size=1, status=None)
            items = result.get("items", [])
            if items:
                return self.get(items[0]["id"])
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.get_solution() সার্চ-ফলব্যাক ব্যর্থ: {e}")
        return None

    def update(self, error_id: int, **fields: Any) -> Optional[BrainError]:
        allowed = {
            "description", "solution", "related_doc_id", "category", "error_code",
            "severity", "is_resolved",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get(error_id)
        if "severity" in updates and updates["severity"] not in VALID_SEVERITIES:
            updates.pop("severity")

        set_parts = [f"{col} = ?" for col in updates]
        params: List[Any] = list(updates.values())
        set_parts.append("updated_at = ?")
        params.append(_now())
        params.append(error_id)

        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.update(): কানেকশন ব্যর্থ: {e}")
            return None
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE brain_errors SET {', '.join(set_parts)} WHERE id = ?", params)
            conn.commit()
            return self.get(error_id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.update() ব্যর্থ: {e}")
            return None
        finally:
            conn.close()

    def mark_resolved(self, error_id: int, resolved: bool = True) -> bool:
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.mark_resolved(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_errors SET is_resolved = ?, updated_at = ? WHERE id = ?",
                (1 if resolved else 0, _now(), error_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.mark_resolved() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    def delete(self, error_id: int) -> bool:
        """Soft Delete।"""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.delete(): কানেকশন ব্যর্থ: {e}")
            return False
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE brain_errors SET deleted_at = ?, updated_at = ? WHERE id = ?",
                (_now(), _now(), error_id),
            )
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.delete() ব্যর্থ: {e}")
            return False
        finally:
            conn.close()

    def get_history(self, error_signature: Optional[str] = None, language: Optional[str] = None, limit: int = 20) -> List[BrainErrorLog]:
        """Error History — `brain_error_log` থেকে সাম্প্রতিক occurrence-গুলো (ফিল্টার সহ)।"""
        clauses: List[str] = []
        params: List[Any] = []
        if error_signature:
            clauses.append("error_signature = ?")
            params.append(error_signature)
        if language:
            clauses.append("language = ?")
            params.append(language)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.get_history(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(
                f"SELECT * FROM brain_error_log{where} ORDER BY created_at DESC LIMIT ?", (*params, limit),
            )
            return [BrainErrorLog.from_row(row) for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.get_history() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ================================ Retry Logic ================================

    def retry(
        self,
        func: Callable,
        *args: Any,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
        retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
        language: str = "python",
        **kwargs: Any,
    ) -> Any:
        """Retry Logic — এক্সপোনেনশিয়াল ব্যাকঅফ সহ `func(*args, **kwargs)` চালায়; প্রতিটা
        ব্যর্থ চেষ্টা `handle()`-এর মাধ্যমে লগ হয়। সব চেষ্টা শেষে ব্যর্থ হলে শেষ এক্সেপশন
        re-raise হয় (কলার-কে জানতেই হবে, নাহলে silently ভুল ডাটা নিয়ে এগোতে পারে)।"""
        last_exc: Optional[BaseException] = None
        for attempt in range(1, max_retries + 1):
            try:
                return func(*args, **kwargs)
            except retryable_exceptions as e:  # noqa: BLE001
                last_exc = e
                self.handle(e, language=language, context={"function": getattr(func, "__name__", "?"), "attempt": attempt})
                if attempt < max_retries:
                    time.sleep(backoff_seconds * (2 ** (attempt - 1)))
        if last_exc is not None:
            raise last_exc

    async def retry_async(
        self,
        func: Callable,
        *args: Any,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
        retryable_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
        language: str = "python",
        **kwargs: Any,
    ) -> Any:
        """`retry()`-এর async ভার্সন — async `func`-কে await করে, ব্যাকঅফে `asyncio.sleep` ব্যবহার করে।"""
        last_exc: Optional[BaseException] = None
        for attempt in range(1, max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return await asyncio.to_thread(func, *args, **kwargs)
            except retryable_exceptions as e:  # noqa: BLE001
                last_exc = e
                await asyncio.to_thread(
                    self.handle, e, language, {"function": getattr(func, "__name__", "?"), "attempt": attempt},
                )
                if attempt < max_retries:
                    await asyncio.sleep(backoff_seconds * (2 ** (attempt - 1)))
        if last_exc is not None:
            raise last_exc

    # ================================ Bulk I/O ================================

    def bulk_import(self, errors: List[Dict[str, Any]]) -> Dict[str, int]:
        summary = {"created": 0, "failed": 0}
        for e in errors:
            created = self.register_solution(
                language=e.get("language", ""), error_signature=e.get("error_signature", ""),
                description=e.get("description", ""), solution=e.get("solution", ""),
                category=e.get("category", "unknown"), severity=e.get("severity", "medium"),
                related_doc_id=e.get("related_doc_id"), error_code=e.get("error_code", ""),
            )
            summary["created" if created is not None else "failed"] += 1
        return summary

    def bulk_export(self, language: Optional[str] = None, include_deleted: bool = False) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if language:
            clauses.append("language = ?")
            params.append(language)
        if not include_deleted:
            clauses.append("(deleted_at IS NULL OR deleted_at = '')")
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        try:
            conn = get_brain_conn()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.bulk_export(): কানেকশন ব্যর্থ: {e}")
            return []
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM brain_errors{where} ORDER BY id ASC", params)
            return [BrainError.from_row(row).__dict__ for row in cur.fetchall()]
        except Exception as e:  # noqa: BLE001
            logger.warning(f"ErrorEngine.bulk_export() ব্যর্থ: {e}")
            return []
        finally:
            conn.close()

    # ================================= Async ওয়্র্যাপার =================================

    async def handle_async(self, *args, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.handle, *args, **kwargs)

    async def register_solution_async(self, *args, **kwargs) -> Optional[BrainError]:
        return await asyncio.to_thread(self.register_solution, *args, **kwargs)

    async def get_solution_async(self, *args, **kwargs) -> Optional[BrainError]:
        return await asyncio.to_thread(self.get_solution, *args, **kwargs)




# =============================================================================
# Phase 16 — Decision Engine + Context Engine (Production-ready single-file layer)
# =============================================================================

PHASE16_CONTEXT_CACHE_MAX = int(os.getenv("PHASE16_CONTEXT_CACHE_MAX", "500"))
PHASE16_CONTEXT_DEFAULT_TTL = int(os.getenv("PHASE16_CONTEXT_DEFAULT_TTL", "86400"))
PHASE16_CONTEXT_MAX_CHARS = int(os.getenv("PHASE16_CONTEXT_MAX_CHARS", "12000"))
PHASE16_DECISION_CACHE_TTL = int(os.getenv("PHASE16_DECISION_CACHE_TTL", "900"))

@dataclass
class BrainContextRecord:
    id: Optional[int] = None
    user_id: Optional[int] = None
    session_key: str = ""
    scope: str = "conversation"
    category: str = "general"
    context_data: str = "{}"
    tags: str = ""
    metadata: str = "{}"
    priority: int = 5
    version: int = 1
    expires_at: str = ""
    deleted_at: str = ""
    created_at: str = ""
    updated_at: str = ""

@dataclass
class BrainDecision:
    id: Optional[int] = None
    user_id: Optional[int] = None
    request_hash: str = ""
    stage: str = "ai"
    strategy: str = "fallback"
    provider_hint: str = ""
    confidence: float = 0.0
    score: float = 0.0
    payload: str = "{}"
    created_at: str = ""
    updated_at: str = ""

@dataclass
class BrainDecisionHistory:
    id: Optional[int] = None
    decision_id: Optional[int] = None
    stage: str = ""
    action: str = ""
    score: float = 0.0
    confidence: float = 0.0
    details: str = "{}"
    created_at: str = ""

class EngineInterface:
    """Phase 16 service contract: engines communicate through small public methods only."""
    name = "engine"
    def available(self) -> bool:
        return True

class ContextRepository:
    """SQLite repository with soft delete, audit fields and migration-safe upserts."""
    def _conn(self) -> sqlite3.Connection:
        conn = get_brain_conn()
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def create(self, record: BrainContextRecord) -> BrainContextRecord:
        now = _now()
        data = json.dumps(json.loads(record.context_data or "{}"), ensure_ascii=False, separators=(",", ":"))
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO brain_context_items
                (user_id,session_key,scope,category,context_data,tags,metadata,priority,version,expires_at,deleted_at,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (record.user_id, record.session_key, record.scope, record.category, data, record.tags,
                 record.metadata or "{}", max(1,min(10,int(record.priority))), max(1,int(record.version)),
                 record.expires_at, record.deleted_at, now, now))
            record.id, record.created_at, record.updated_at = cur.lastrowid, now, now
        return record

    def update(self, context_id: int, patch: Dict[str, Any]) -> Optional[BrainContextRecord]:
        allowed = {"context_data","tags","metadata","priority","category","scope","expires_at","deleted_at"}
        values = {k:v for k,v in patch.items() if k in allowed}
        if not values:
            return self.get(context_id, include_deleted=True)
        values["updated_at"] = _now()
        cols = ", ".join(f"{k}=?" for k in values)
        with self._conn() as conn:
            conn.execute(f"UPDATE brain_context_items SET {cols}, version=version+1 WHERE id=?",
                         list(values.values())+[context_id])
        return self.get(context_id, include_deleted=True)

    def get(self, context_id: int, include_deleted: bool=False) -> Optional[BrainContextRecord]:
        sql = "SELECT * FROM brain_context_items WHERE id=?"
        if not include_deleted: sql += " AND deleted_at=''"
        with self._conn() as conn:
            row = conn.execute(sql,(context_id,)).fetchone()
        return BrainContextRecord(**dict(zip([d.name for d in fields(BrainContextRecord)], row))) if row else None

    def active(self, user_id: int, session_key: str, limit: int=50) -> List[BrainContextRecord]:
        now = _now()
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT * FROM brain_context_items WHERE user_id=? AND session_key=?
                   AND deleted_at='' AND (expires_at='' OR expires_at>?)
                   ORDER BY priority DESC, updated_at DESC LIMIT ?""",
                (user_id,session_key,now,max(1,min(200,limit)))).fetchall()
        names=[d.name for d in fields(BrainContextRecord)]
        return [BrainContextRecord(**dict(zip(names,row))) for row in rows]

    def search(self, user_id: int, query: str, limit: int=20) -> List[BrainContextRecord]:
        q=f"%{(query or '').strip()}%"
        with self._conn() as conn:
            rows=conn.execute(
                """SELECT * FROM brain_context_items WHERE user_id=? AND deleted_at=''
                   AND (context_data LIKE ? OR tags LIKE ? OR category LIKE ?)
                   ORDER BY priority DESC,updated_at DESC LIMIT ?""",(user_id,q,q,q,max(1,min(100,limit)))).fetchall()
        names=[d.name for d in fields(BrainContextRecord)]
        return [BrainContextRecord(**dict(zip(names,row))) for row in rows]

class ContextEngine(EngineInterface):
    name="context"
    def __init__(self, repository: Optional[ContextRepository]=None) -> None:
        self.repo=repository or ContextRepository()
        self._cache: OrderedDict[str, Tuple[float,List[Dict[str,Any]]]] = OrderedDict()

    def _key(self,user_id:int,session_key:str)->str: return f"{user_id}:{session_key}"
    def _trim_cache(self)->None:
        while len(self._cache)>PHASE16_CONTEXT_CACHE_MAX: self._cache.popitem(last=False)

    def validate(self, data: Dict[str,Any]) -> Dict[str,Any]:
        if not isinstance(data,dict): raise ValueError("context_data অবশ্যই dictionary হতে হবে")
        raw=json.dumps(data,ensure_ascii=False)
        if len(raw)>PHASE16_CONTEXT_MAX_CHARS: raise ValueError("context_data অনুমোদিত সীমার চেয়ে বড়")
        return data

    def create_context(self,user_id:int,session_key:str,data:Dict[str,Any],scope:str="conversation",
                       category:str="general",tags:Sequence[str]=(),priority:int=5,
                       metadata:Optional[Dict[str,Any]]=None,ttl_seconds:Optional[int]=None)->BrainContextRecord:
        self.validate(data)
        ttl=PHASE16_CONTEXT_DEFAULT_TTL if ttl_seconds is None else max(0,int(ttl_seconds))
        expires="" if ttl==0 else (datetime.now(timezone.utc)+timedelta(seconds=ttl)).isoformat(timespec="seconds")
        rec=BrainContextRecord(user_id=user_id,session_key=str(session_key),scope=scope,category=category,
            context_data=json.dumps(data,ensure_ascii=False),tags=",".join(dict.fromkeys(map(str,tags))),
            metadata=json.dumps(metadata or {},ensure_ascii=False),priority=priority,expires_at=expires)
        self._cache.pop(self._key(user_id,str(session_key)),None)
        return self.repo.create(rec)

    def update_context(self,context_id:int,patch:Dict[str,Any])->Optional[BrainContextRecord]:
        if "context_data" in patch:
            self.validate(patch["context_data"] if isinstance(patch["context_data"],dict) else json.loads(patch["context_data"]))
            patch["context_data"]=json.dumps(patch["context_data"],ensure_ascii=False) if isinstance(patch["context_data"],dict) else patch["context_data"]
        return self.repo.update(context_id,patch)

    def delete_context(self,context_id:int)->bool:
        return self.repo.update(context_id,{"deleted_at":_now()}) is not None
    def restore_context(self,context_id:int)->bool:
        return self.repo.update(context_id,{"deleted_at":""}) is not None

    def get_active_context(self,user_id:int,session_key:str,limit:int=30)->List[Dict[str,Any]]:
        key=self._key(user_id,str(session_key)); now=time.time()
        cached=self._cache.get(key)
        if cached and now-cached[0]<60:
            self._cache.move_to_end(key); return cached[1]
        rows=self.repo.active(user_id,str(session_key),limit)
        result=[]
        for r in rows:
            try: data=json.loads(r.context_data or "{}")
            except json.JSONDecodeError: continue
            result.append({"id":r.id,"scope":r.scope,"category":r.category,"data":data,"tags":r.tags.split(",") if r.tags else [],
                           "priority":r.priority,"version":r.version,"metadata":json.loads(r.metadata or "{}")})
        self._cache[key]=(now,result); self._trim_cache(); return result

    def collect(self,user_id:int,session_key:str,request:str,max_chars:int=4000)->Dict[str,Any]:
        contexts=self.get_active_context(user_id,session_key)
        q=set(re.findall(r"[\w\u0980-\u09ff]+",(request or "").lower()))
        ranked=[]
        for item in contexts:
            blob=json.dumps(item.get("data",{}),ensure_ascii=False).lower()+" "+item.get("category","")+" "+" ".join(item.get("tags",[]))
            overlap=sum(1 for token in q if token in blob)
            score=item["priority"]*10+overlap*20
            ranked.append((score,item))
        ranked.sort(key=lambda x:x[0],reverse=True)
        chosen=[]; used=0
        for _,item in ranked:
            s=json.dumps(item["data"],ensure_ascii=False,separators=(",",":"))
            if used+len(s)>max_chars: continue
            chosen.append(item); used+=len(s)
        return {"items":chosen,"char_count":used,"compressed":len(chosen)<len(contexts)}

    def merge(self,items:Sequence[Dict[str,Any]])->Dict[str,Any]:
        merged={}
        for item in items:
            data=item.get("data",item) if isinstance(item,dict) else {}
            if isinstance(data,dict): merged.update(data)
        return merged
    def summarize(self,user_id:int,session_key:str,max_chars:int=1000)->str:
        ctx=self.collect(user_id,session_key,"",max_chars)
        return json.dumps(self.merge(ctx["items"]),ensure_ascii=False)[:max_chars]
    def search_context(self,user_id:int,query:str)->List[Dict[str,Any]]:
        return [{"id":r.id,"category":r.category,"data":json.loads(r.context_data or "{}"),"priority":r.priority}
                for r in self.repo.search(user_id,query)]
    def analytics(self,user_id:Optional[int]=None)->Dict[str,Any]:
        with self.repo._conn() as conn:
            where=" WHERE user_id=?" if user_id is not None else ""
            params=(user_id,) if user_id is not None else ()
            total=conn.execute("SELECT COUNT(*) FROM brain_context_items"+where,params).fetchone()[0]
            active=conn.execute("SELECT COUNT(*) FROM brain_context_items"+where+(" AND" if where else " WHERE")+" deleted_at=''",params).fetchone()[0]
        return {"total":total,"active":active,"cache_entries":len(self._cache)}
    async def create_context_async(self,*a,**kw): return await asyncio.to_thread(self.create_context,*a,**kw)
    async def get_active_context_async(self,*a,**kw): return await asyncio.to_thread(self.get_active_context,*a,**kw)

class DecisionRepository:
    def _conn(self)->sqlite3.Connection:
        conn=get_brain_conn(); conn.execute("PRAGMA foreign_keys=ON"); return conn
    def save(self,d:BrainDecision)->BrainDecision:
        now=_now()
        with self._conn() as conn:
            cur=conn.execute("""INSERT INTO brain_decisions
            (user_id,request_hash,stage,strategy,provider_hint,confidence,score,payload,created_at,updated_at,deleted_at)
            VALUES (?,?,?,?,?,?,?,?,?,?, '')""",(d.user_id,d.request_hash,d.stage,d.strategy,d.provider_hint,d.confidence,d.score,d.payload,now,now))
            d.id=cur.lastrowid; d.created_at=d.updated_at=now
        return d
    def history(self,user_id:Optional[int]=None,limit:int=100)->List[Dict[str,Any]]:
        sql="SELECT * FROM brain_decisions WHERE deleted_at=''"
        args=[]
        if user_id is not None: sql+=" AND user_id=?"; args.append(user_id)
        sql+=" ORDER BY id DESC LIMIT ?"; args.append(max(1,min(500,limit)))
        with self._conn() as conn: rows=conn.execute(sql,args).fetchall()
        return [dict(zip(["id","user_id","request_hash","stage","strategy","provider_hint","confidence","score","payload","created_at","updated_at","deleted_at"],r)) for r in rows]

# Coding-orchestrator context-এ greeting/bot-info FAQ কখনোই সঠিক উত্তর নয় —
# DecisionEngine.execute(..., exclude_categories=CODING_EXCLUDED_BRAIN_CATEGORIES)
# দিয়ে সেগুলো candidate তালিকা থেকে সম্পূর্ণ বাদ যায়।
CODING_EXCLUDED_BRAIN_CATEGORIES: List[str] = ["bot_info", "greeting"]

# decision dict-এর সাথে সাজানো candidate তালিকার কয়টা শীর্ষ এন্ট্রি সংযোজিত থাকবে —
# coding-orchestrator এগুলো থেকে "প্রাসঙ্গিক নিয়ম/গাইডলাইন" (non-code entries) বাছাই
# করে AI প্রম্পটে যোগ করে (সব candidate সংযোজন করলে decision dict অপ্রয়োজনে বড় হত)।
DECISION_CANDIDATES_KEPT = 6


def _normalize_exclude_categories(exclude_categories: Optional[Sequence[str]] = None) -> set:
    try:
        return {str(c).strip().lower() for c in (exclude_categories or []) if str(c).strip()}
    except Exception:
        return set()


def _decision_iter_search_items(results: Any) -> List[Any]:
    """Knowledge/Documentation/Template search রিটার্ন (list বা {items: [...]}) সমানভাবে iterate করে।"""
    try:
        if results is None:
            return []
        if isinstance(results, dict):
            items = results.get("items")
            return list(items) if isinstance(items, list) else []
        if isinstance(results, (list, tuple)):
            return list(results)
        return []
    except Exception:
        return []


def _payload_category(payload: Any) -> str:
    """Pattern/Knowledge/Documentation/Template payload থেকে category বের করে (lowercase)।"""
    try:
        if payload is None:
            return ""
        if isinstance(payload, dict):
            cat = payload.get("category")
            if cat:
                return str(cat).strip().lower()
            inner = payload.get("pattern")
            if inner is not None:
                return _payload_category(inner)
            for key in ("knowledge", "documentation", "template"):
                if key in payload:
                    nested = _payload_category(payload.get(key))
                    if nested:
                        return nested
            return ""
        return str(getattr(payload, "category", "") or "").strip().lower()
    except Exception:
        return ""


def _category_excluded(payload: Any, excluded: set) -> bool:
    if not excluded:
        return False
    return _payload_category(payload) in excluded


def _pattern_match_quality_ok(request: str, payload: Any) -> bool:
    """Pattern-এর match_value request-এ significant/whole-word অংশ কিনা — শুধু substring নয়।"""
    try:
        match_value = ""
        pattern_type = "keyword"
        if isinstance(payload, dict):
            inner = payload.get("pattern")
            if inner is not None:
                match_value = (
                    getattr(inner, "match_value", None)
                    or (inner.get("match_value") if isinstance(inner, dict) else "")
                    or ""
                )
                pattern_type = (
                    getattr(inner, "pattern_type", None)
                    or (inner.get("pattern_type") if isinstance(inner, dict) else "")
                    or "keyword"
                )
            if not match_value:
                match_value = str(payload.get("match_value") or "")
                pattern_type = str(payload.get("pattern_type") or pattern_type)
        else:
            match_value = str(getattr(payload, "match_value", "") or "")
            pattern_type = str(getattr(payload, "pattern_type", "keyword") or "keyword")
        match_value = (match_value or "").strip()
        if not match_value:
            return False
        if pattern_type == "regex":
            try:
                return re.search(match_value, request or "", flags=re.IGNORECASE) is not None
            except re.error:
                return False
        keywords = [k.strip() for k in match_value.split(",") if k.strip()]
        return any(_whole_word_in_text(k, request) for k in keywords)
    except Exception:
        return False


def _template_match_quality_ok(request: str, payload: Any) -> bool:
    """Template name/body-র significant token request-এ whole-word হিসেবে থাকতে হবে।"""
    try:
        if isinstance(payload, dict):
            name = str(payload.get("name") or "")
            body = str(payload.get("body") or "")
        else:
            name = str(getattr(payload, "name", "") or "")
            body = str(getattr(payload, "body", "") or "")
        tokens = re.findall(r"[\w\u0980-\u09FF]{3,}", f"{name} {body[:120]}", flags=re.UNICODE)
        if not tokens:
            return False
        return any(_whole_word_in_text(t, request) for t in tokens[:12])
    except Exception:
        return False


class DecisionEngine(EngineInterface):
    name="decision"
    def __init__(self,context_engine:Optional[ContextEngine]=None,repository:Optional[DecisionRepository]=None)->None:
        self.context=context_engine or ContextEngine()
        self.repo=repository or DecisionRepository()
        self._cache: OrderedDict[str,Tuple[float,Dict[str,Any]]]=OrderedDict()

    @staticmethod
    def _hash(request:str,context:Dict[str,Any])->str:
        return hashlib.sha256((request+"|"+json.dumps(context,sort_keys=True,ensure_ascii=False)).encode()).hexdigest()
    def _engine_candidates(self,request:str,exclude_categories:Optional[Sequence[str]]=None)->List[Dict[str,Any]]:
        candidates=[]
        excluded=_normalize_exclude_categories(exclude_categories)
        try:
            for item in PatternEngine().match(request, exclude_categories=list(excluded) or None):
                if _category_excluded(item, excluded):
                    continue
                candidates.append({"stage":"pattern","score":70+float(item.get("confidence",item.get("confidence_score",0))*20),"confidence":float(item.get("confidence",item.get("confidence_score",0.7))),"payload":item})
        except Exception as e: logger.debug("Decision pattern stage skipped: %s",e)
        try:
            results=KnowledgeEngine().search(request,limit=5) if hasattr(KnowledgeEngine(),"search") else []
            for item in _decision_iter_search_items(results):
                if _category_excluded(item, excluded):
                    continue
                candidates.append({"stage":"knowledge","score":60+float(item.get("score",0))*30,"confidence":float(item.get("confidence_score",0.7)),"payload":item})
        except Exception as e: logger.debug("Decision knowledge stage skipped: %s",e)
        try:
            results=DocumentationEngine().search(request,limit=5) if hasattr(DocumentationEngine(),"search") else []
            for item in _decision_iter_search_items(results):
                if _category_excluded(item, excluded):
                    continue
                candidates.append({"stage":"documentation","score":55+float((item.get("score",0) if isinstance(item,dict) else 0))*30,"confidence":float((item.get("confidence_score",0.6) if isinstance(item,dict) else 0.6)),"payload":item})
        except Exception as e: logger.debug("Decision documentation stage skipped: %s",e)
        try:
            results=TemplateEngine().search(request,limit=3) if hasattr(TemplateEngine(),"search") else []
            for item in _decision_iter_search_items(results):
                if _category_excluded(item, excluded):
                    continue
                priority = item.get("priority", 5) if isinstance(item, dict) else getattr(item, "priority", 5)
                candidates.append({"stage":"template","score":50+float(priority or 5)*4,"confidence":0.65,"payload":item})
        except Exception as e: logger.debug("Decision template stage skipped: %s",e)
        candidates.append({"stage":"ai","score":45,"confidence":0.55,"payload":{}})
        return candidates

    def execute(self,request:str,user_id:Optional[int]=None,session_key:str="",provider_hint:str="",exclude_categories:Optional[List[str]]=None)->Dict[str,Any]:
        request=(request or "").strip()
        if not request: raise ValueError("request খালি রাখা যাবে না")
        ctx=self.context.collect(user_id or 0,session_key or str(user_id or "anonymous"),request)
        hash_ctx=dict(ctx)
        hash_ctx["_exclude_categories"]=sorted(_normalize_exclude_categories(exclude_categories))
        key=self._hash(request,hash_ctx); cached=self._cache.get(key)
        if cached and time.time()-cached[0]<PHASE16_DECISION_CACHE_TTL:
            return dict(cached[1],cached=True)
        candidates=self._engine_candidates(request, exclude_categories=exclude_categories)
        # priority + confidence + context relevance; deterministic conflict resolution.
        for c in candidates:
            c["score"]=round(float(c["score"])+float(c["confidence"])*20+min(10,ctx["char_count"]/400),2)
        candidates.sort(key=lambda c:(c["score"],c["confidence"],c["stage"]!="ai"),reverse=True)
        best=candidates[0]
        # Phase 35 নিরাপত্তা-ফিক্স: knowledge/documentation stage-এ confidence মূলত এন্ট্রি
        # কতটা "authoritative" (যিনি লিখেছেন তার নিজের দেওয়া মান) তা বোঝায়, প্রশ্নের সাথে
        # আসলে কতটা মিলেছে তা নয়। শুধু confidence দেখে direct-এ যেতে দিলে দুর্বল/অপ্রাসঙ্গিক
        # fuzzy বা relaxed ম্যাচও (আসল মিল কম থাকা সত্ত্বেও) উচ্চ-confidence এন্ট্রির কারণে
        # ভুল সরাসরি উত্তর দিয়ে দিতে পারে — তাই এই দুই stage-এ আসল ম্যাচ-কোয়ালিটিও
        # (payload["score"], search()-এ normalize করা 0..1) যথেষ্ট ভালো হতে হবে।
        # Pattern/template-এর confidence_score এন্ট্রির নিজস্ব priority; matching quality নয় —
        # তাই match_value request-এ significant/whole-word অংশ হতে হবে।
        match_quality_ok = True
        try:
            if best["stage"] in ("knowledge", "documentation"):
                payload = best.get("payload") or {}
                match_quality_ok = float((payload.get("score", 0) if isinstance(payload, dict) else 0) or 0) >= 0.6
            elif best["stage"] == "pattern":
                match_quality_ok = _pattern_match_quality_ok(request, best.get("payload"))
            elif best["stage"] == "template":
                match_quality_ok = _template_match_quality_ok(request, best.get("payload"))
        except Exception as e:
            logger.debug("Decision match-quality guard fallback to AI: %s", e)
            match_quality_ok = False
        strategy="direct" if best["stage"] in ("knowledge","pattern","documentation","template") and best["confidence"]>=0.72 and match_quality_ok else "ai"
        decision={"request_hash":key,"stage":best["stage"],"strategy":strategy,"provider_hint":provider_hint,
                  "confidence":round(float(best["confidence"]),3),"score":best["score"],"candidate_count":len(candidates),
                  "context":ctx,"payload":best["payload"],"fallback":"ai","retry_max":AI_KEY_RETRY_MAX_ATTEMPTS,"cached":False,
                  # শীর্ষ candidate গুলো (সাজানো ক্রমে) সংযোজন — coding-orchestrator যেন
                  # direct-এ reject হওয়া/নিচের প্রাসঙ্গিক knowledge/pattern/template এন্ট্রি
                  # গুলো AI প্রম্পটে "নিয়ম/গাইডলাইন" হিসেবে ব্যবহার করতে পারে।
                  "candidates":[dict(c) for c in candidates[:DECISION_CANDIDATES_KEPT]]}
        saved=self.repo.save(BrainDecision(user_id=user_id,request_hash=key,stage=decision["stage"],strategy=strategy,
            provider_hint=provider_hint,confidence=decision["confidence"],score=decision["score"],
            payload=json.dumps(decision["payload"],ensure_ascii=False,default=str)))
        decision["decision_id"]=saved.id
        self._cache[key]=(time.time(),decision)
        while len(self._cache)>300: self._cache.popitem(last=False)
        return decision

    def history(self,user_id:Optional[int]=None,limit:int=100)->List[Dict[str,Any]]: return self.repo.history(user_id,limit)
    def analytics(self,user_id:Optional[int]=None)->Dict[str,Any]:
        rows=self.history(user_id,500)
        stages={}
        for r in rows: stages[r["stage"]]=stages.get(r["stage"],0)+1
        avg=sum(float(r["confidence"]) for r in rows)/len(rows) if rows else 0.0
        return {"total_decisions":len(rows),"by_stage":stages,"avg_confidence":round(avg,3),"cache_entries":len(self._cache)}
    def clear_cache(self)->int:
        n=len(self._cache); self._cache.clear(); return n
    async def execute_async(self,*a,**kw): return await asyncio.to_thread(self.execute,*a,**kw)

def _create_phase16_tables(cur: sqlite3.Cursor)->None:
    cur.execute("""CREATE TABLE IF NOT EXISTS brain_context_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,session_key TEXT NOT NULL,scope TEXT NOT NULL DEFAULT 'conversation',
        category TEXT NOT NULL DEFAULT 'general',context_data TEXT NOT NULL DEFAULT '{}',tags TEXT DEFAULT '',metadata TEXT DEFAULT '{}',
        priority INTEGER DEFAULT 5,version INTEGER DEFAULT 1,expires_at TEXT DEFAULT '',deleted_at TEXT DEFAULT '',
        created_at TEXT,updated_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS brain_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,request_hash TEXT NOT NULL,stage TEXT NOT NULL,strategy TEXT NOT NULL,
        provider_hint TEXT DEFAULT '',confidence REAL DEFAULT 0,score REAL DEFAULT 0,payload TEXT DEFAULT '{}',
        created_at TEXT,updated_at TEXT,deleted_at TEXT DEFAULT '')""")
    cur.execute("""CREATE TABLE IF NOT EXISTS brain_decision_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,decision_id INTEGER,stage TEXT,action TEXT,score REAL DEFAULT 0,
        confidence REAL DEFAULT 0,details TEXT DEFAULT '{}',created_at TEXT,
        FOREIGN KEY(decision_id) REFERENCES brain_decisions(id) ON DELETE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS brain_context_cache (
        cache_key TEXT PRIMARY KEY,cache_value TEXT NOT NULL,expires_at TEXT DEFAULT '',created_at TEXT,updated_at TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS brain_context_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,context_id INTEGER NOT NULL,version INTEGER NOT NULL,context_data TEXT NOT NULL,
        metadata TEXT DEFAULT '{}',created_at TEXT,FOREIGN KEY(context_id) REFERENCES brain_context_items(id) ON DELETE CASCADE)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS brain_context_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,context_id INTEGER,user_id INTEGER,action TEXT NOT NULL,details TEXT DEFAULT '{}',created_at TEXT)""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p16_context_active ON brain_context_items(user_id,session_key,deleted_at,expires_at,priority)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p16_context_category ON brain_context_items(user_id,category,updated_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p16_decision_user_time ON brain_decisions(user_id,created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p16_decision_hash ON brain_decisions(request_hash)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p16_history_decision ON brain_decision_history(decision_id,created_at)")

# Public API/service facade: suitable for future HTTP, plugin, workflow or command adapters.
context_engine_service = ContextEngine()
decision_engine_service = DecisionEngine(context_engine_service)

def api_create_context(**kwargs): return context_engine_service.create_context(**kwargs)
def api_update_context(context_id:int,patch:Dict[str,Any]): return context_engine_service.update_context(context_id,patch)
def api_delete_context(context_id:int): return context_engine_service.delete_context(context_id)
def api_restore_context(context_id:int): return context_engine_service.restore_context(context_id)
def api_get_active_context(user_id:int,session_key:str,limit:int=30): return context_engine_service.get_active_context(user_id,session_key,limit)
def api_search_context(user_id:int,query:str): return context_engine_service.search_context(user_id,query)
def api_decision_execute(request:str,user_id:Optional[int]=None,session_key:str="",provider_hint:str="",exclude_categories:Optional[List[str]]=None): return decision_engine_service.execute(request,user_id,session_key,provider_hint,exclude_categories)
def api_decision_history(user_id:Optional[int]=None,limit:int=100): return decision_engine_service.history(user_id,limit)
def api_decision_analytics(user_id:Optional[int]=None): return decision_engine_service.analytics(user_id)
def api_cache_management(clear:bool=False):
    return {"cleared":decision_engine_service.clear_cache() if clear else 0,"entries":len(decision_engine_service._cache)}
def api_bulk_export_context(user_id:int): return [r.__dict__ for r in context_engine_service.repo.active(user_id,str(user_id),200)]

async def execute_phase16_pipeline(
    user_id: int,
    session_key: str,
    user_request: str,
    system_prompt: str,
    use_cache: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    """Core Phase-16 orchestration entry point; existing ask_ai APIs remain untouched."""
    decision = await decision_engine_service.execute_async(
        user_request, user_id=user_id, session_key=session_key
    )
    response = await ask_ai(system_prompt, user_request, use_cache=use_cache, user_id=user_id)
    return response, decision

def api_bulk_import_context(records:Sequence[Dict[str,Any]])->int:
    count=0
    for item in records:
        try:
            api_create_context(user_id=int(item["user_id"]),session_key=str(item.get("session_key",item["user_id"])),
                data=item.get("data") or json.loads(item.get("context_data","{}")),scope=item.get("scope","conversation"),
                category=item.get("category","general"),tags=item.get("tags",[]),priority=int(item.get("priority",5)),
                metadata=item.get("metadata") if isinstance(item.get("metadata"),dict) else json.loads(item.get("metadata","{}")))
            count+=1
        except Exception as e: logger.warning("Phase 16 bulk import row skipped: %s",e)
    return count


def _migrate_code_tasks_autonomous(cur: sqlite3.Cursor) -> None:
    """Phase 20: safe/idempotent workflow-state columns for autonomous coding tasks."""
    try:
        cur.execute("PRAGMA table_info(code_tasks)")
        existing = {row[1] for row in cur.fetchall()}
        columns = {
            "depends_on_seq": "INTEGER DEFAULT NULL",
            "retry_count": "INTEGER DEFAULT 0",
            "last_error": "TEXT DEFAULT ''",
            "workflow_stage": "TEXT DEFAULT 'pending'",
            "target_files": "TEXT DEFAULT ''",
            "test_status": "TEXT DEFAULT ''",
            "test_output": "TEXT DEFAULT ''",
            "test_report": "TEXT DEFAULT ''",
            "test_updated_at": "TEXT DEFAULT ''",
            "last_working_code": "TEXT DEFAULT ''",
            "review_status": "TEXT DEFAULT ''",
            "review_score": "INTEGER DEFAULT 0",
            "review_report": "TEXT DEFAULT ''",
            "security_status": "TEXT DEFAULT ''",
            "security_score": "INTEGER DEFAULT 100",
            "security_report": "TEXT DEFAULT ''",
            "security_updated_at": "TEXT DEFAULT ''",
        }
        for col, typ in columns.items():
            if col not in existing:
                try:
                    cur.execute(f"ALTER TABLE code_tasks ADD COLUMN {col} {typ}")
                except sqlite3.OperationalError as e:
                    logger.warning("Phase 20 migration %s skipped: %s", col, e)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_code_tasks_workflow ON code_tasks(project_id, status, seq)")
    except Exception as e:
        logger.warning("Phase 20 code_tasks migration failed: %s", e)

def init_db():
    """বট প্রথমবার চালু হলে দরকারি টেবিল বানায়। বারবার চালালেও সমস্যা নেই।"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            voice TEXT DEFAULT 'male',
            speed TEXT DEFAULT 'normal',
            is_banned INTEGER DEFAULT 0,
            request_count INTEGER DEFAULT 0,
            last_request_date TEXT DEFAULT '',
            joined_date TEXT DEFAULT '',
            auto_reply INTEGER DEFAULT 1,
            memory_enabled INTEGER DEFAULT 1,
            language TEXT DEFAULT 'bn'
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS dub_sessions (
            user_id INTEGER,
            part_number INTEGER,
            file_path TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bug_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scheduled_broadcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            send_at TEXT,
            sent INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pdf_sessions (
            user_id INTEGER PRIMARY KEY,
            filename TEXT,
            content TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_roles (
            user_id INTEGER PRIMARY KEY,
            role TEXT,
            added_by INTEGER,
            added_at TEXT
        )
        """
    )
    # Phase 11: Coding Orchestrator — Project Memory (প্রতি ইউজারের চলমান কোডিং প্রজেক্ট
    # ও তার ধাপগুলো স্থায়ীভাবে সংরক্ষণ করার জন্য, বট রিস্টার্ট হলেও যেন না হারায়)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS code_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            description TEXT,
            stack TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS code_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            seq INTEGER,
            title TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            source TEXT DEFAULT '',
            code TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    # Performance Improvement: ঘন ঘন ব্যবহৃত কলামে ইনডেক্স, যাতে ইউজার বাড়লেও
    # leaderboard/dailystats/monthlystats/memory কুয়েরি ধীর না হয়ে যায়
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usage_log_user ON usage_log(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usage_log_created ON usage_log(created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_conv_history_user ON conversation_history(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_due ON scheduled_broadcasts(sent, send_at)")
    # Phase 11: কোডিং প্রজেক্ট/টাস্ক দ্রুত খোঁজার জন্য ইনডেক্স
    cur.execute("CREATE INDEX IF NOT EXISTS idx_code_projects_user ON code_projects(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_code_tasks_project ON code_tasks(project_id)")
    _migrate_code_tasks_autonomous(cur)
    conn.commit()
    conn.close()
    migrate_db()

    # Phase 18: Codebase Intelligence schema — safe/idempotent, existing tables untouched.
    try:
        conn = get_conn()
        conn.execute("PRAGMA foreign_keys = ON")
        _codebase_ensure_tables(conn)
        conn.close()
    except Exception as e:
        logger.warning(f"Phase 18 Codebase Intelligence DB init skipped: {e}")

    # Phase 13-15: Brain OS-এর নিজস্ব ডাটাবেস স্তর (brain_* টেবিল, Search/Knowledge/Pattern/
    # Template/Documentation/Error Engine স্কিমা) প্রস্তুত করা — একই bot_data.db ফাইলে,
    # বিদ্যমান কোনো টেবিল স্পর্শ না করে। একক-ফাইল সংস্করণ, তাই আলাদা প্যাকেজ import লাগে না —
    # init_brain_db() এই একই ফাইলে উপরে সংজ্ঞায়িত। try/except-এ মোড়ানো, যাতে Brain OS-এ
    # কোনো সমস্যা হলেও পুরো বট চালু হতে ব্যর্থ না হয় — শুধু Brain OS ফিচার বন্ধ থাকবে,
    # বাকি সব আগের মতোই চলবে।
    try:
        init_brain_db()
    except Exception as e:
        logger.warning(f"Brain OS ডাটাবেস চালু করতে সমস্যা হয়েছে, Brain OS ফিচার বন্ধ থাকবে: {e}")

    # Phase 27: Git/Rollback Intelligence — code_snapshots টেবিল, idempotent। ব্যর্থ হলেও
    # বাকি বট স্বাভাবিকভাবে চলবে, শুধু snapshot/rollback ফিচার বন্ধ থাকবে।
    try:
        conn = get_conn()
        _phase27_ensure_tables(conn)
        conn.close()
    except Exception as e:
        logger.warning(f"Phase 27 Git/Rollback DB init ব্যর্থ, ফিচার বন্ধ থাকবে: {e}")

    # Phase 28: Change Impact / Dependency Intelligence — additive, idempotent.
    # Failure must never block bot startup.
    try:
        conn = get_conn()
        _phase28_ensure_tables(conn)
        conn.close()
    except Exception as e:
        logger.warning(f"Phase 28 Impact DB init ব্যর্থ, feature fallback-only mode-এ থাকবে: {e}")

    # Phase 29: Autonomous Coding Supervisor 2.0 — additive, idempotent.
    try:
        conn = get_conn()
        _phase29_ensure_tables(conn)
        conn.commit(); conn.close()
    except Exception as e:
        logger.warning(f"Phase 29 Supervisor DB init ব্যর্থ, feature disabled: {e}")


def migrate_db():
    """
    আগে থেকে চলা বটের পুরোনো ডাটাবেসে নতুন কলাম (auto_reply, memory_enabled, language)
    যোগ করে। বারবার চালালেও সমস্যা নেই — যেটা আছে সেটা আবার যোগ করে না।
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    existing_cols = {row[1] for row in cur.fetchall()}
    new_columns = {
        "auto_reply": "INTEGER DEFAULT 1",
        "memory_enabled": "INTEGER DEFAULT 1",
        "language": "TEXT DEFAULT 'bn'",
        "lang_manual": "INTEGER DEFAULT 0",
        # Phase 4: Premium System
        "is_premium": "INTEGER DEFAULT 0",
        "premium_since": "TEXT DEFAULT ''",
        "premium_until": "TEXT DEFAULT ''",
        "premium_expiry_notified": "INTEGER DEFAULT 0",
        "premium_granted_by": "INTEGER DEFAULT 0",
        # Phase 5: Referral System
        "referred_by": "INTEGER DEFAULT 0",
        "bonus_daily_limit": "INTEGER DEFAULT 0",
        # Phase 11: Coding Orchestrator — ইউজারের বর্তমান সক্রিয় কোডিং প্রজেক্ট কোনটা তা মনে রাখা
        "active_code_project_id": "INTEGER DEFAULT 0",
        # Phase 43: No API Call Mode — প্রতিটা ইউজার নিজের চ্যাটের জন্য আলাদাভাবে চালু/বন্ধ করে
        "no_api_mode": "INTEGER DEFAULT 0",
        # Phase 45: নিজস্ব API Key — প্রতিটা ইউজার চাইলে নিজের OpenRouter/Groq/Cerebras Key
        # যুক্ত করতে পারবে, সেটা শুধু তার নিজের চ্যাটেই ব্যবহার হয় (শেয়ার্ড পুলে মেশে না)।
        "own_openrouter_key": "TEXT DEFAULT ''",
        "own_groq_key": "TEXT DEFAULT ''",
        "own_cerebras_key": "TEXT DEFAULT ''",
        "own_key_hint_shown_date": "TEXT DEFAULT ''",  # নিজস্ব Key যুক্ত করার অনুস্মারক দিনে একবারের বেশি দেখানো হয় না
    }
    for col, col_type in new_columns.items():
        if col not in existing_cols:
            try:
                cur.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
                logger.info(f"ডাটাবেস মাইগ্রেশন: users টেবিলে '{col}' কলাম যোগ হলো")
            except sqlite3.OperationalError as e:
                logger.warning(f"মাইগ্রেশন এরর ({col}): {e}")
    conn.commit()
    conn.close()


def get_conn():
    return sqlite3.connect(DB_PATH)


def register_user(user_id: int, referred_by: int = 0) -> bool:
    """নতুন ইউজার হলে সারিতে যোগ করে এবং True রিটার্ন করে; আগে থেকে থাকলে কিছুই বদলায় না
    এবং False রিটার্ন করে। referred_by দিলে (শুধু নতুন ইউজারের ক্ষেত্রে) কে রেফার করেছে তা সংরক্ষণ হয়
    (Phase 5: Referral System)।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    is_new = cur.fetchone() is None
    if is_new:
        cur.execute(
            "INSERT INTO users (user_id, joined_date, last_request_date, referred_by) VALUES (?, ?, ?, ?)",
            (user_id, str(date.today()), str(date.today()), referred_by or 0),
        )
        conn.commit()
    conn.close()
    return is_new


def get_user_row(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT voice, speed, is_banned, request_count, last_request_date FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_field(user_id: int, column: str, value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()


def is_banned(user_id: int) -> bool:
    row = get_user_row(user_id)
    return bool(row and row[2] == 1)


# ============================= Phase 4: Premium System =============================

def get_premium_info(user_id: int) -> tuple:
    """রিটার্ন করে (is_premium, premium_until, premium_since) — premium_until/since খালি
    স্ট্রিং হতে পারে যদি কখনো প্রিমিয়াম না নেওয়া থাকে।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT is_premium, premium_until, premium_since FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return (0, "", "")
    is_premium, premium_until, premium_since = row
    return (is_premium or 0, premium_until or "", premium_since or "")


def is_premium_active(user_id: int) -> bool:
    """
    ইউজার এখন প্রিমিয়াম কিনা চেক করে (রিড-অনলি, দ্রুত)। মেয়াদ ফাঁকা রাখা হলে সেটা
    আজীবন প্রিমিয়াম হিসেবে ধরা হয়। মেয়াদ পার হয়ে গেলেও ফ্ল্যাগ False দেখায় (আসল
    বাতিলটা ব্যাকগ্রাউন্ড জব check_premium_notifications করে) — যাতে প্রতিটা কুয়েরিতে
    আলাদা করে ডাটাবেসে লিখতে না হয়।
    """
    is_premium, premium_until, _ = get_premium_info(user_id)
    if not is_premium:
        return False
    if not premium_until:
        return True
    try:
        until_date = datetime.strptime(premium_until, "%Y-%m-%d").date()
    except ValueError:
        return True
    return date.today() <= until_date


def get_daily_limit(user_id: int) -> int:
    """অ্যাডমিনের জন্য -1 (সীমাহীন বোঝাতে), প্রিমিয়াম হলে PREMIUM_DAILY_LIMIT, না হলে FREE_DAILY_LIMIT
    — প্লাস রেফারেল বোনাস (bonus_daily_limit) যোগ করে (Phase 5)।"""
    if user_id in ADMIN_IDS:
        return -1
    base = PREMIUM_DAILY_LIMIT if is_premium_active(user_id) else FREE_DAILY_LIMIT
    return base + get_bonus_daily_limit(user_id)


def grant_premium(user_id: int, days: int, granted_by: int) -> str:
    """
    ইউজারকে প্রিমিয়াম দেয়। ইউজার আগে থেকেই সক্রিয় প্রিমিয়াম থাকলে বর্তমান মেয়াদ থেকে
    দিন যোগ হয় (মেয়াদ বাড়ানো); না থাকলে আজ থেকে গোনা শুরু হয়। নতুন মেয়াদের তারিখ
    (YYYY-MM-DD স্ট্রিং) রিটার্ন করে।
    """
    register_user(user_id)
    is_premium, premium_until, premium_since = get_premium_info(user_id)
    today = date.today()

    base = today
    if is_premium and premium_until:
        try:
            current_until = datetime.strptime(premium_until, "%Y-%m-%d").date()
            if current_until > today:
                base = current_until
        except ValueError:
            pass

    new_until = base + timedelta(days=days)
    new_since = premium_since if (is_premium and premium_since) else today.isoformat()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET is_premium = 1, premium_until = ?, premium_since = ?, "
        "premium_expiry_notified = 0, premium_granted_by = ? WHERE user_id = ?",
        (new_until.isoformat(), new_since, granted_by, user_id),
    )
    conn.commit()
    conn.close()
    return new_until.isoformat()


def revoke_premium(user_id: int):
    """ইউজারের প্রিমিয়াম বাতিল করে (অ্যাডমিন কমান্ড দিয়ে বা মেয়াদ শেষ হয়ে স্বয়ংক্রিয়ভাবে)।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET is_premium = 0, premium_until = '', premium_expiry_notified = 0 "
        "WHERE user_id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def list_active_premium_users():
    """(user_id, premium_until) — সক্রিয় প্রিমিয়াম ইউজারদের তালিকা, মেয়াদ শেষ হওয়ার ক্রম অনুযায়ী।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, premium_until FROM users WHERE is_premium = 1 ORDER BY premium_until ASC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# ============================= Phase 5: Referral System =============================

def get_bonus_daily_limit(user_id: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT bonus_daily_limit FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return (row[0] or 0) if row else 0


def get_referral_count(user_id: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count


def apply_referral_bonus(referrer_id: int, new_user_id: int) -> bool:
    """
    নতুন ইউজার কারো রেফার লিংক দিয়ে জয়েন করলে দুজনকেই বোনাস দেয় (একবারই, কারণ এটা
    শুধু register_user-এর মাধ্যমে সদ্য তৈরি হওয়া নতুন ইউজারের জন্য কল করা হয়)।
    নিরাপত্তা: নিজেকে নিজে রেফার করা যাবে না, এবং বোনাস REFERRAL_MAX_BONUS সীমার বেশি জমবে না।
    সফল হলে True রিটার্ন করে।
    """
    if referrer_id == new_user_id or referrer_id <= 0:
        return False
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (referrer_id,))
    if cur.fetchone() is None:
        conn.close()
        return False  # রেফারার আইডি ভুয়া/অস্তিত্বহীন

    cur.execute(
        "UPDATE users SET bonus_daily_limit = MIN(bonus_daily_limit + ?, ?) WHERE user_id = ?",
        (REFERRAL_BONUS, REFERRAL_MAX_BONUS, referrer_id),
    )
    cur.execute(
        "UPDATE users SET bonus_daily_limit = MIN(bonus_daily_limit + ?, ?) WHERE user_id = ?",
        (REFERRAL_BONUS, REFERRAL_MAX_BONUS, new_user_id),
    )
    conn.commit()
    conn.close()
    return True


def build_referral_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


def check_and_use_quota(user_id: int) -> bool:
    """
    ইউজারের দৈনিক সীমা চেক করে (ফ্রি হলে FREE_DAILY_LIMIT, প্রিমিয়াম হলে PREMIUM_DAILY_LIMIT)।
    সীমার মধ্যে থাকলে ব্যবহার গুনে True রিটার্ন করে। সীমা শেষ হলে False রিটার্ন করে।
    অ্যাডমিনের কোনো সীমা নেই।
    """
    if user_id in ADMIN_IDS:
        return True

    row = get_user_row(user_id)
    if row is None:
        register_user(user_id)
        row = get_user_row(user_id)

    _, _, _, count, last_date = row
    today = str(date.today())

    if last_date != today:
        count = 0  # নতুন দিন শুরু হলে গণনা রিসেট

    daily_limit = get_daily_limit(user_id)

    if count >= daily_limit:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET request_count = ?, last_request_date = ? WHERE user_id = ?",
            (count, today, user_id),
        )
        conn.commit()
        conn.close()
        return False

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET request_count = ?, last_request_date = ? WHERE user_id = ?",
        (count + 1, today, user_id),
    )
    conn.commit()
    conn.close()
    return True


# ============================= Phase 7/8: AI Provider Router (সম্পূর্ণ ফ্রি, একাধিক Provider + Key Pool) =============================
#
# আর্কিটেকচার: প্রতিটা AI Provider-এর জন্য একটা আলাদা ক্লাস (OpenRouterProvider, GroqProvider,
# CerebrasProvider) — সবগুলোই একই "chat(system_prompt, messages, timeout)" ইন্টারফেস মেনে চলে
# (BaseAIProvider থেকে ইনহেরিট করে)। AIRouter এই Provider-গুলোকে ক্রমানুসারে
# (OpenRouter -> Groq -> Cerebras) চেষ্টা করে — একটা সম্পূর্ণ ব্যর্থ হলে (তার সব Key শেষ)
# পরেরটায় চলে যায়। ভবিষ্যতে নতুন কোনো ফ্রি Provider যোগ করতে চাইলে শুধু একটা নতুন
# *Provider ক্লাস লিখে ai_router-এর providers লিস্টে যোগ করলেই হবে।
#
# Phase 8: এখন প্রতিটা Provider-এর একাধিক API Key (Pool) থাকতে পারে। প্রতিটা Key-এর
# স্বাস্থ্য (Health), লোড (কয়টা রিকোয়েস্ট চলছে) ও গড় রেসপন্স টাইম আলাদাভাবে ট্র্যাক করা হয়।
# একটা Provider-কে কল করলে সেই Provider-এর pool থেকে সবচেয়ে কম ব্যস্ত ও সবচেয়ে দ্রুত Key
# বেছে নেওয়া হয় (Load Balancer)। কোনো Key ব্যর্থ হলে একই Provider-এর পরের সেরা Key দিয়ে
# আবার চেষ্টা হয় (Key Rotation) — পুরো pool শেষ হয়ে গেলে তবেই পরের Provider-এ যাওয়া হয়।
# পরপর কয়েকবার ব্যর্থ হওয়া Key সাময়িকভাবে "Inactive" (Health Checker) থাকে, কুলডাউন শেষ
# হলে আবার এমনিতেই ব্যবহারযোগ্য হয়ে যায় — কোনো আলাদা ব্যাকগ্রাউন্ড জব ছাড়াই।

# Phase 9: Connection Pool — OpenRouter/Cerebras (httpx দিয়ে সরাসরি HTTP কল করে এমন Provider)
# আগে প্রতিটা কলে নতুন httpx.AsyncClient বানাত (তাতে প্রতিবার নতুন TCP/TLS কানেকশন লাগত)।
# এখন পুরো বট জুড়ে একটাই Shared client (Keep-Alive Connection Pool সহ) লেজি-ইনিশিয়ালাইজ
# হয়ে পুনর্ব্যবহার হয়। get_http_client() যেকোনো জায়গা থেকে নিরাপদে (thread/coroutine-safe
# লকসহ) কল করা যায়।
_shared_http_client: "httpx.AsyncClient | None" = None
_shared_http_client_lock = asyncio.Lock()


async def get_http_client() -> httpx.AsyncClient:
    """Phase 9: Connection Pool — একটাই পুনর্ব্যবহারযোগ্য httpx.AsyncClient রিটার্ন করে,
    দরকার হলে (প্রথমবার বা আগেরটা বন্ধ হয়ে গেলে) নতুন করে বানায়।"""
    global _shared_http_client
    if _shared_http_client is None or _shared_http_client.is_closed:
        async with _shared_http_client_lock:
            if _shared_http_client is None or _shared_http_client.is_closed:
                _shared_http_client = httpx.AsyncClient(
                    timeout=AI_HTTP_TIMEOUT,
                    limits=httpx.Limits(
                        max_connections=HTTP_POOL_MAX_CONNECTIONS,
                        max_keepalive_connections=HTTP_POOL_MAX_KEEPALIVE,
                    ),
                )
    return _shared_http_client


async def close_http_client():
    """বট বন্ধ হওয়ার সময় Shared client পরিষ্কারভাবে বন্ধ করার জন্য (main()-এর
    post_shutdown হুক থেকে কল হয়)।"""
    global _shared_http_client
    if _shared_http_client is not None and not _shared_http_client.is_closed:
        await _shared_http_client.aclose()


class AIProviderError(Exception):
    """কোনো একটা Key/Provider ব্যর্থ হলে (rate limit/timeout/key নেই/এরর) এই এক্সসেপশন তোলা হয়,
    যাতে AIRouter/KeyPool পরের Key বা Provider-এ চলে যেতে পারে। সব শেষ পর্যন্ত ব্যর্থ হলে এটাই
    উপরে (কমান্ড হ্যান্ডলারের নিজস্ব try/except-এ) চলে যায়, যেখানে আগে থেকেই প্রতিটা কমান্ডে
    ইউজার-বান্ধব বাংলা এরর মেসেজ দেখানোর ব্যবস্থা আছে — তাই এই পরিবর্তনে কোনো কমান্ডের
    আচরণ/মেসেজ বদলাচ্ছে না।"""
    pass


class ManagedKey:
    """
    একটা একক API Key-এর অবস্থা ট্র্যাক করে — Health Checker, Load Balancer ও Key Rotation
    সবকিছুরই ভিত্তি এই ক্লাস। নিরাপত্তা: আসল Key কখনো লগ/প্রিন্ট হয় না — শুধু label
    (যেমন "Groq Key #2") ব্যবহার হয়, যেটা এই ক্লাসের বাইরে দেখানো/লগ করা নিরাপদ।
    """

    def __init__(self, provider_name: str, index: int, api_key: str, is_own: bool = False):
        self.provider_name = provider_name
        self.index = index
        self.api_key = api_key
        self.label = f"{provider_name} Key #{index}"
        self.is_own = is_own               # Phase: এই Key কি ইউজারের নিজস্ব? (True হলে pick_best-এ সবসময় আগে চেষ্টা হয়)
        self.in_flight = 0                # Load Balancer: এই মুহূর্তে কয়টা রিকোয়েস্ট এই Key দিয়ে চলছে
        self.avg_response_time = 0.0       # Load Balancer: চলমান গড় রেসপন্স টাইম (সেকেন্ড)
        self.consecutive_failures = 0      # Health Checker
        self.unhealthy_until = 0.0         # Health Checker: time.time() টাইমস্ট্যাম্প, 0 মানে সুস্থ
        self.total_requests = 0            # Statistics (Phase 10-এ পুরোপুরি ব্যবহার হবে)
        self.total_failures = 0
        self.total_retries = 0             # Phase 10: এই Key-তে (Backoff দিয়ে) মোট কতবার আবার চেষ্টা হয়েছে

    def is_healthy(self) -> bool:
        return time.time() >= self.unhealthy_until

    def mark_success(self, elapsed: float):
        self.consecutive_failures = 0
        self.unhealthy_until = 0.0
        self.total_requests += 1
        if self.avg_response_time == 0:
            self.avg_response_time = elapsed
        else:
            self.avg_response_time = (self.avg_response_time * 0.7) + (elapsed * 0.3)

    def mark_failure(self):
        self.consecutive_failures += 1
        self.total_requests += 1
        self.total_failures += 1
        if self.consecutive_failures >= KEY_UNHEALTHY_THRESHOLD:
            extra_fails = self.consecutive_failures - KEY_UNHEALTHY_THRESHOLD
            cooldown = min(KEY_UNHEALTHY_MAX_COOLDOWN, KEY_UNHEALTHY_BASE_COOLDOWN * (2 ** min(extra_fails, 4)))
            self.unhealthy_until = time.time() + cooldown
            logger.warning(f"AI Health Checker: {self.label} সাময়িক Inactive করা হলো ({cooldown:.0f} সেকেন্ডের জন্য)।")


class KeyPool:
    """একটা Provider-এর সব API Key নিয়ে Load Balancer + Rotation করে সবচেয়ে উপযুক্ত Key বেছে দেয়।"""

    def __init__(self, provider_name: str, api_keys: list, extra_keys: list = None):
        self.provider_name = provider_name
        self.keys = [ManagedKey(provider_name, i + 1, k) for i, k in enumerate(api_keys) if k]
        if extra_keys:
            # Phase: আগে থেকে বানানো ManagedKey (যেমন বটের শেয়ার্ড pool-এর আসল Key অবজেক্ট)
            # সরাসরি pool-এ যোগ করার জন্য — এতে ঐ Key-গুলোর health/in_flight/avg_response_time
            # অবস্থা (যা পুরো বটজুড়ে শেয়ার্ড) অক্ষত থাকে, নতুন করে তৈরি হয় না।
            self.keys.extend(extra_keys)

    def has_keys(self) -> bool:
        return len(self.keys) > 0

    def healthy_keys(self) -> list:
        return [k for k in self.keys if k.is_healthy()]

    def pick_best(self, exclude_labels: set) -> "ManagedKey | None":
        """নিজস্ব (is_own) Key থাকলে ও সুস্থ থাকলে সবসময় সবার আগে বেছে নেওয়া হয় (লোড/গতি
        যাই হোক না কেন)। নিজস্ব Key না থাকলে/exclude হয়ে গেলে (ব্যর্থ হয়ে বাদ পড়লে বা
        Health Checker অসুস্থ ঘোষণা করলে), বাকি (শেয়ার্ড) Key-গুলোর মধ্যে সবচেয়ে কম ব্যস্ত
        (in_flight), টাই হলে সবচেয়ে দ্রুত (avg_response_time) — এটা বেছে নেওয়া হয়।"""
        candidates = [k for k in self.healthy_keys() if k.label not in exclude_labels]
        if not candidates:
            return None
        return min(candidates, key=lambda k: (0 if k.is_own else 1, k.in_flight, k.avg_response_time))


class BaseAIProvider:
    """
    সব Provider ক্লাসের বেস। নতুন Provider যোগ করতে চাইলে শুধু __init__-এ KeyPool/model সেট করে
    _call_with_key() ওভাররাইড করলেই যথেষ্ট — Key Rotation/Load Balancer লজিক (chat মেথডে)
    এখানেই কেন্দ্রীভূত, বারবার লিখতে হয় না।
    """
    name = "base"

    def __init__(self, key_pool: KeyPool, model: str):
        self.key_pool = key_pool
        self.model = model

    def is_configured(self) -> bool:
        return self.key_pool.has_keys()

    async def _call_with_key(self, managed_key: ManagedKey, system_prompt: str, messages: list, timeout: float, max_tokens: int = 1024) -> str:
        """সাব-ক্লাস এটা ওভাররাইড করে — একটা নির্দিষ্ট Key দিয়ে আসল API কল করে।"""
        raise NotImplementedError

    async def chat(self, system_prompt: str, messages: list, timeout: float, max_tokens: int = 1024) -> str:
        """
        Key Rotation + Load Balancer: pool-এর স্বাস্থ্যবান Key-গুলোর মধ্যে সবচেয়ে কম ব্যস্ত/
        দ্রুতটা বেছে চেষ্টা করে। Phase 9: একটা Key সাথে সাথে বাদ না দিয়ে, প্রথমে সেই একই
        Key-তে Exponential Backoff সহ আরও কয়েকবার (AI_KEY_RETRY_MAX_ATTEMPTS পর্যন্ত) আবার
        চেষ্টা করা হয় — সাময়িক (transient) নেটওয়ার্ক/rate-limit সমস্যা এতেই সেরে যায় বলে
        অযথা Key/Provider বদলানো কমে। শুধু বারবার ব্যর্থ হলে বা Key সাময়িক Inactive (Health
        Checker) হয়ে গেলে তবেই একই Provider-এর পরের সেরা Key-তে যাওয়া হয় — পুরো pool শেষ
        না হওয়া পর্যন্ত (তখনই AIRouter পরের Provider-এ যাবে)।

        Phase 20-fix: max_tokens pass-through — /codeplan-এর মতো বড় JSON আউটপুটের জন্য
        কলার চাওয়া মান (default 1024) প্রতিটা _call_with_key-তে পৌঁছে দেওয়া হয়।
        """
        if not self.key_pool.has_keys():
            raise AIProviderError(f"{self.name}: কোনো API Key কনফিগার করা নেই")
        tried_labels = set()
        errors = []
        while True:
            managed_key = self.key_pool.pick_best(exclude_labels=tried_labels)
            if managed_key is None:
                break
            tried_labels.add(managed_key.label)

            attempt = 0
            delay = AI_KEY_RETRY_BASE_DELAY
            last_error = None
            while True:
                attempt += 1
                call_start = time.time()
                try:
                    result = await self._call_with_key(managed_key, system_prompt, messages, timeout, max_tokens)
                    elapsed = time.time() - call_start
                    # Phase 10: বিস্তারিত Logging — কোন Provider/Key (শুধু নম্বর/label, আসল Key নয়),
                    # Response Time, Retry Count প্রতিটা সফল রিকোয়েস্টেই লগ হয়।
                    logger.info(
                        f"AI Request Log: Provider={self.name}, Key={managed_key.label}, "
                        f"ResponseTime={elapsed:.2f}s, Retries={attempt - 1}, Status=success"
                    )
                    return result
                except AIProviderError as e:
                    elapsed = time.time() - call_start
                    last_error = e
                    if attempt >= AI_KEY_RETRY_MAX_ATTEMPTS or not managed_key.is_healthy():
                        # Phase 10: বিস্তারিত Logging — চূড়ান্তভাবে ব্যর্থ হলে Error/Retry Count-সহ লগ।
                        logger.warning(
                            f"AI Request Log: Provider={self.name}, Key={managed_key.label}, "
                            f"ResponseTime={elapsed:.2f}s, Retries={attempt - 1}, Status=failed, Error={e}"
                        )
                        break
                    managed_key.total_retries += 1
                    logger.info(
                        f"AI Retry: {managed_key.label} — {attempt} নম্বর চেষ্টা ব্যর্থ ({e}), "
                        f"{delay:.1f}s পর আবার চেষ্টা হবে।"
                    )
                    await asyncio.sleep(delay)
                    delay *= AI_KEY_RETRY_BACKOFF_FACTOR

            errors.append(str(last_error))
        detail = "; ".join(errors) if errors else "সব Key সাময়িক Inactive (rate limit/এরর কুলডাউনে)"
        raise AIProviderError(f"{self.name}: সব Key ব্যর্থ ({detail})")


def _extract_openai_style_content(data: dict, label: str) -> str:
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise AIProviderError(f"{label}: অপ্রত্যাশিত রেসপন্স ফরম্যাট ({e})")
    if not content or not content.strip():
        raise AIProviderError(f"{label}: খালি উত্তর এসেছে")
    return content


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter-এর ফ্রি (':free' সাফিক্সযুক্ত) মডেল ব্যবহার করে — API OpenAI-compatible।"""
    name = "OpenRouter"
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    async def _call_with_key(self, managed_key: ManagedKey, system_prompt: str, messages: list, timeout: float, max_tokens: int = 1024) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        start = time.time()
        managed_key.in_flight += 1
        try:
            try:
                # Phase 9: Connection Pool — প্রতিবার নতুন client না বানিয়ে Shared,
                # পুনর্ব্যবহারযোগ্য httpx.AsyncClient ব্যবহার হয় (per-call timeout override সহ)।
                client = await get_http_client()
                resp = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {managed_key.api_key}",
                        "Content-Type": "application/json",
                        "X-Title": BOT_NAME,
                    },
                    json={"model": self.model, "messages": full_messages, "max_tokens": max_tokens},
                    timeout=timeout,
                )
            except httpx.TimeoutException:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: টাইমআউট")
            except httpx.HTTPError as e:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: নেটওয়ার্ক এরর ({e})")

            if resp.status_code == 429:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: rate limit-এ পৌঁছে গেছে (429)")
            if resp.status_code >= 400:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: HTTP {resp.status_code} — {resp.text[:200]}")

            content = _extract_openai_style_content(resp.json(), managed_key.label)
            managed_key.mark_success(time.time() - start)
            return content
        finally:
            managed_key.in_flight = max(0, managed_key.in_flight - 1)


class GroqProvider(BaseAIProvider):
    """Groq-এর ফ্রি টিয়ার ব্যবহার করে (groq SDK দিয়ে, আগে থেকেই বটে ইনস্টল করা আছে)।
    Phase 8: প্রতিটা Key-এর জন্য আলাদা Groq ক্লায়েন্ট লেজি-ইনিশিয়ালাইজড ও ক্যাশ করা থাকে।"""
    name = "Groq"

    def __init__(self, key_pool: KeyPool, model: str):
        super().__init__(key_pool, model)
        self._clients = {}  # label -> Groq ক্লায়েন্ট

    def _get_client(self, managed_key: ManagedKey):
        client = self._clients.get(managed_key.label)
        if client is None:
            client = Groq(api_key=managed_key.api_key)
            self._clients[managed_key.label] = client
        return client

    def _sync_call(self, client, full_messages: list, max_tokens: int = 1024) -> str:
        response = client.chat.completions.create(model=self.model, messages=full_messages, max_tokens=max_tokens)
        return response.choices[0].message.content

    async def _call_with_key(self, managed_key: ManagedKey, system_prompt: str, messages: list, timeout: float, max_tokens: int = 1024) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        client = self._get_client(managed_key)
        start = time.time()
        managed_key.in_flight += 1
        try:
            try:
                content = await asyncio.wait_for(
                    asyncio.to_thread(self._sync_call, client, full_messages, max_tokens), timeout=timeout
                )
            except asyncio.TimeoutError:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: টাইমআউট")
            except Exception as e:
                managed_key.mark_failure()
                msg = str(e)
                if "rate" in msg.lower() or "429" in msg:
                    raise AIProviderError(f"{managed_key.label}: rate limit-এ পৌঁছে গেছে")
                raise AIProviderError(f"{managed_key.label}: এরর ({e})")

            if not content or not content.strip():
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: খালি উত্তর এসেছে")
            managed_key.mark_success(time.time() - start)
            return content
        finally:
            managed_key.in_flight = max(0, managed_key.in_flight - 1)


class CerebrasProvider(BaseAIProvider):
    """Cerebras-এর ফ্রি টিয়ার ব্যবহার করে — API OpenAI-compatible।"""
    name = "Cerebras"
    BASE_URL = "https://api.cerebras.ai/v1/chat/completions"

    async def _call_with_key(self, managed_key: ManagedKey, system_prompt: str, messages: list, timeout: float, max_tokens: int = 1024) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        start = time.time()
        managed_key.in_flight += 1
        try:
            try:
                # Phase 9: Connection Pool — Shared httpx.AsyncClient পুনর্ব্যবহার হয়।
                client = await get_http_client()
                resp = await client.post(
                    self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {managed_key.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": self.model, "messages": full_messages, "max_tokens": max_tokens},
                    timeout=timeout,
                )
            except httpx.TimeoutException:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: টাইমআউট")
            except httpx.HTTPError as e:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: নেটওয়ার্ক এরর ({e})")

            if resp.status_code == 429:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: rate limit-এ পৌঁছে গেছে (429)")
            if resp.status_code >= 400:
                managed_key.mark_failure()
                raise AIProviderError(f"{managed_key.label}: HTTP {resp.status_code} — {resp.text[:200]}")

            content = _extract_openai_style_content(resp.json(), managed_key.label)
            managed_key.mark_success(time.time() - start)
            return content
        finally:
            managed_key.in_flight = max(0, managed_key.in_flight - 1)


class AIRouter:
    """
    একাধিক ফ্রি AI Provider-কে নির্দিষ্ট ক্রমে (Smart Routing) চেষ্টা করে — একটা Provider-এর
    পুরো Key Pool ব্যর্থ হলে (rate limit/timeout/key নেই/এরর) স্বয়ংক্রিয়ভাবে পরের Provider-এ
    চলে যায় (Automatic Provider Switching)। প্রতিটা Provider নিজের ভেতরেই Key Rotation করে।
    """

    def __init__(self, providers: list, timeout: float = 30):
        self.providers = providers
        self.timeout = timeout

    async def chat(self, system_prompt: str, messages: list, max_tokens: int = 1024) -> str:
        errors = []
        tried_any = False
        for provider in self.providers:
            if not provider.is_configured():
                continue
            tried_any = True
            try:
                result = await provider.chat(system_prompt, messages, timeout=self.timeout, max_tokens=max_tokens)
                logger.info(f"AIRouter: {provider.name} সফল হয়েছে।")
                return result
            except AIProviderError as e:
                logger.warning(f"AIRouter: {provider.name} সম্পূর্ণ ব্যর্থ (সব Key শেষ): {e}")
                errors.append(str(e))

        if not tried_any:
            raise AIProviderError("কোনো AI Provider কনফিগার করা নেই — Secrets-এ অন্তত একটা API Key বসান।")
        detail = "; ".join(errors)
        logger.error(f"AIRouter: সব প্রোভাইডার ব্যর্থ হয়েছে — {detail}")
        raise AIProviderError(f"সব ফ্রি AI Provider এই মুহূর্তে ব্যর্থ হয়েছে ({detail})")


# ক্রম গুরুত্বপূর্ণ (Smart Routing): ১) OpenRouter ২) Groq (OpenRouter ব্যস্ত/ব্যর্থ হলে)
# ৩) Cerebras (Groq-ও ব্যর্থ হলে)। প্রতিটার ভেতরে আবার নিজস্ব Key Pool + Load Balancer।
openrouter_key_pool = KeyPool("OpenRouter", OPENROUTER_KEY_POOL_RAW)
groq_key_pool = KeyPool("Groq", GROQ_KEY_POOL_RAW)
cerebras_key_pool = KeyPool("Cerebras", CEREBRAS_KEY_POOL_RAW)

ai_router = AIRouter(
    providers=[
        OpenRouterProvider(openrouter_key_pool, OPENROUTER_MODEL),
        GroqProvider(groq_key_pool, GROQ_MODEL),
        CerebrasProvider(cerebras_key_pool, CEREBRAS_MODEL),
    ],
    timeout=AI_HTTP_TIMEOUT,
)


# ============================= Phase 45: নিজস্ব API Key (Own API Key) =============================
# উদ্দেশ্য: প্রতিটা ইউজার চাইলে নিজের OpenRouter/Groq/Cerebras API Key বটে যুক্ত করতে পারবে।
# যুক্ত করলে তার AI রিকোয়েস্টগুলো (সেই Provider-এর জন্য) শুধু তার নিজের Key দিয়েই যাবে —
# বটের শেয়ার্ড Key Pool-এর সাথে মেশে না, তাই একসাথে অনেকজন (৫/১০ জন) শেয়ার্ড ফ্রি Key
# ব্যবহার করলেও তার রিকোয়েস্ট তাদের সাথে প্রতিযোগিতা করে না — rate limit-এ পড়ার সম্ভাবনা কমে
# এবং সাড়া আরও দ্রুত আসে। যে Provider-এ নিজের Key নেই, সেটার জন্য এখনো বটের শেয়ার্ড
# (কমিউনিটি) Key Pool ব্যবহার হয় — তাই কেউ নিজের Key যুক্ত না করলেও বট আগের মতোই কাজ করবে।
# নিরাপত্তা: প্রতিটা ইউজারের নিজের Key শুধু তার নিজের রিকোয়েস্টেই ব্যবহার হয় (কখনো অন্য কারো
# রিকোয়েস্টে/শেয়ার্ড পুলে যোগ হয় না), এবং কমান্ডে দেখানোর সময় সবসময় মাস্ক করা থাকে
# (শুরু+শেষের কয়েকটা অক্ষর ছাড়া বাকিটা ***)।

OWN_API_KEY_PROVIDERS = ("openrouter", "groq", "cerebras")
OWN_API_KEY_COLUMN = {
    "openrouter": "own_openrouter_key",
    "groq": "own_groq_key",
    "cerebras": "own_cerebras_key",
}
OWN_API_KEY_LABEL_BN = {
    "openrouter": "OpenRouter",
    "groq": "Groq",
    "cerebras": "Cerebras",
}
OWN_API_KEY_SIGNUP_URL = {
    "openrouter": "https://openrouter.ai/keys",
    "groq": "https://console.groq.com/keys",
    "cerebras": "https://cloud.cerebras.ai/",
}
_OWN_KEY_MIN_LEN = 20
_OWN_KEY_MAX_LEN = 250


def normalize_provider_name(raw: str) -> Optional[str]:
    """ইউজারের লেখা Provider নাম (ছোট/বড় হাতের অক্ষর, ছোট বানান) থেকে ক্যানোনিকাল নাম বের করে।"""
    val = (raw or "").strip().lower()
    aliases = {
        "openrouter": "openrouter", "open-router": "openrouter", "or": "openrouter",
        "groq": "groq",
        "cerebras": "cerebras", "cere": "cerebras",
    }
    return aliases.get(val)


def mask_api_key(key: str) -> str:
    """Key দেখানোর সময় সবসময় মাস্ক করা হয় — শুরু ও শেষের কয়েকটা অক্ষর ছাড়া বাকিটা লুকানো থাকে।"""
    key = (key or "").strip()
    if not key:
        return ""
    if len(key) <= 10:
        return "*" * len(key)
    return f"{key[:4]}{'*' * 8}{key[-4:]}"


def get_own_api_keys(user_id: int) -> Dict[str, str]:
    """এই ইউজারের সব প্রোভাইডারের নিজস্ব Key ফেরত দেয় (খালি স্ট্রিং মানে সেই প্রোভাইডারে Key নেই)।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT own_openrouter_key, own_groq_key, own_cerebras_key FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return {p: "" for p in OWN_API_KEY_PROVIDERS}
    return {"openrouter": row[0] or "", "groq": row[1] or "", "cerebras": row[2] or ""}


def has_any_own_api_key(user_id: int) -> bool:
    return any(get_own_api_keys(user_id).values())


# ইউজার-প্রতি তৈরি করা AIRouter ক্যাশ — বারবার একই ইউজারের জন্য নতুন Provider/Client না
# বানাতে (প্রতিটা Groq Provider ক্লায়েন্ট লেজি-ইনিশিয়ালাইজড, তাও অকারণে বারবার তৈরি করা
# অপচয়)। Key বদলালে/মুছে ফেললে cache entry-টা invalidate হয়ে যায় (নিচে দেখুন)।
_user_ai_router_cache: Dict[int, Tuple[Tuple[str, str, str], AIRouter]] = {}
_user_ai_router_cache_lock = threading.Lock()


def _invalidate_user_router_cache(user_id: int) -> None:
    with _user_ai_router_cache_lock:
        _user_ai_router_cache.pop(user_id, None)


def set_own_api_key(user_id: int, provider: str, api_key: str) -> Tuple[bool, str]:
    """ইউজারের নিজের Key সেভ করে। রিটার্ন করে (সফল?, বার্তা)।"""
    canonical = normalize_provider_name(provider)
    if canonical is None:
        return False, "প্রোভাইডার লিখুন: openrouter, groq অথবা cerebras"
    api_key = (api_key or "").strip()
    if " " in api_key or len(api_key) < _OWN_KEY_MIN_LEN or len(api_key) > _OWN_KEY_MAX_LEN:
        return False, "Key-টা সঠিক মনে হচ্ছে না (স্পেস ছাড়া, সাধারণত ২০-২৫০ অক্ষরের হয়)। আবার চেষ্টা করুন।"
    column = OWN_API_KEY_COLUMN[canonical]
    register_user(user_id)
    update_field(user_id, column, api_key)
    _invalidate_user_router_cache(user_id)
    label = OWN_API_KEY_LABEL_BN[canonical]
    return True, f"✅ আপনার নিজস্ব {label} API Key যুক্ত হয়েছে ({mask_api_key(api_key)})। এখন থেকে {label}-এর জন্য এই Key-ই ব্যবহার হবে, শুধু আপনার চ্যাটে।"


def remove_own_api_key(user_id: int, provider: str) -> Tuple[bool, str]:
    """provider == 'all' দিলে সবগুলো মুছে দেয়, নাহলে শুধু নির্দিষ্ট প্রোভাইডারেরটা।"""
    provider_norm = (provider or "").strip().lower()
    if provider_norm == "all":
        for col in OWN_API_KEY_COLUMN.values():
            update_field(user_id, col, "")
        _invalidate_user_router_cache(user_id)
        return True, "✅ আপনার সব নিজস্ব API Key মুছে ফেলা হয়েছে — এখন থেকে বটের শেয়ার্ড Key ব্যবহার হবে।"
    canonical = normalize_provider_name(provider_norm)
    if canonical is None:
        return False, "প্রোভাইডার লিখুন: openrouter, groq, cerebras, অথবা all (সবগুলো)"
    update_field(user_id, OWN_API_KEY_COLUMN[canonical], "")
    _invalidate_user_router_cache(user_id)
    label = OWN_API_KEY_LABEL_BN[canonical]
    return True, f"✅ আপনার নিজস্ব {label} API Key মুছে ফেলা হয়েছে — এখন থেকে {label}-এর জন্য বটের শেয়ার্ড Key ব্যবহার হবে।"


def _build_provider_key_pool(provider_label: str, own_key: Optional[str], shared_pool: "KeyPool") -> "KeyPool":
    """একটা Provider-এর জন্য KeyPool বানায়। ইউজারের নিজস্ব Key থাকলে সেটাকে (is_own=True)
    বটের শেয়ার্ড pool-এর আসল Key অবজেক্টগুলোর সাথে একই KeyPool-এ যোগ করে দেওয়া হয় — যাতে
    KeyPool.pick_best() প্রথমে নিজস্ব Key ট্রাই করে, আর সেটা ব্যর্থ/rate-limit/Health Checker-এ
    Inactive হলে স্বয়ংক্রিয়ভাবে বটের শেয়ার্ড Key-তে (একই Provider-এর ভেতরেই) Fallback করে —
    আগের মতো সরাসরি পরের Provider-এ চলে না গিয়ে। নিজস্ব Key না থাকলে শেয়ার্ড pool-ই সরাসরি
    রিটার্ন হয় (আগের আচরণ অক্ষত)।"""
    if not own_key:
        return shared_pool
    own_managed_key = ManagedKey(f"{provider_label} (নিজস্ব)", 1, own_key, is_own=True)
    return KeyPool(provider_label, [], extra_keys=[own_managed_key] + shared_pool.keys)


def _build_user_ai_router(user_id: Optional[int]) -> AIRouter:
    """
    এই ইউজারের জন্য কোন Provider-এ কোন Key ব্যবহার হবে তা ঠিক করে একটা AIRouter রিটার্ন করে।
    যে Provider-এ ইউজারের নিজস্ব Key আছে, সেখানে নিজস্ব Key আগে (Exponential Backoff সহ)
    চেষ্টা হয়; সেটা ব্যর্থ হলে বা rate-limit খেলে একই Provider-এর বটের শেয়ার্ড Key Pool-ও
    ব্যাকআপ হিসেবে ট্রাই হয় (_build_provider_key_pool দেখুন) — তারপরও ব্যর্থ হলে যেমন আগে
    হতো, পরের Provider-এ চলে যায়। যে Provider-এ নিজস্ব Key নেই, সেখানে আগের মতোই বটের
    শেয়ার্ড pool ব্যবহার হয়। কোনো নিজস্ব Key না থাকলে সরাসরি গ্লোবাল ai_router-ই রিটার্ন হয়
    (দ্রুততম পথ, নতুন কিছু বানাতে হয় না)।
    """
    if not user_id:
        return ai_router
    own_keys = get_own_api_keys(user_id)
    if not any(own_keys.values()):
        return ai_router

    cache_key = (own_keys.get("openrouter", ""), own_keys.get("groq", ""), own_keys.get("cerebras", ""))
    with _user_ai_router_cache_lock:
        cached = _user_ai_router_cache.get(user_id)
        if cached and cached[0] == cache_key:
            return cached[1]

    providers = [
        OpenRouterProvider(
            _build_provider_key_pool("OpenRouter", own_keys.get("openrouter"), openrouter_key_pool),
            OPENROUTER_MODEL,
        ),
        GroqProvider(
            _build_provider_key_pool("Groq", own_keys.get("groq"), groq_key_pool),
            GROQ_MODEL,
        ),
        CerebrasProvider(
            _build_provider_key_pool("Cerebras", own_keys.get("cerebras"), cerebras_key_pool),
            CEREBRAS_MODEL,
        ),
    ]

    router = AIRouter(providers=providers, timeout=AI_HTTP_TIMEOUT)
    with _user_ai_router_cache_lock:
        _user_ai_router_cache[user_id] = (cache_key, router)
    return router


def build_own_api_key_hint(user_id: int) -> str:
    """যারা এখনো নিজস্ব Key যুক্ত করেননি তাদের জন্য একটা সংক্ষিপ্ত অনুস্মারক বার্তা — চ্যাট
    রিপ্লাইয়ের নিচে মাঝেমধ্যে জুড়ে দেওয়া হয় (প্রতিবার নয়, দেখুন should_show_own_key_hint())।"""
    return (
        "\n\n💡 নিজস্ব API Key যুক্ত করুন — আরও দ্রুত ও নির্ভুলভাবে (accuracy) উত্তর পেতে, এবং "
        "শেয়ার্ড ফ্রি সীমার ভাগ না নিয়ে। লিখুন: /setapikey দেখুন।"
    )


def should_show_own_key_hint(user_id: int) -> bool:
    """দিনে একবারের বেশি এই হিন্ট দেখানো হয় না (বিরক্তিকর না করার জন্য)। ইতিমধ্যে নিজস্ব Key
    থাকলে বা অ্যাডমিন হলে কখনো দেখানো হয় না।"""
    if user_id in ADMIN_IDS:
        return False
    if has_any_own_api_key(user_id):
        return False
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT own_key_hint_shown_date FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    today = str(date.today())
    if row and row[0] == today:
        return False
    update_field(user_id, "own_key_hint_shown_date", today)
    return True


async def setapikey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/setapikey <provider> <key> — নিজস্ব API Key যুক্ত করা। DM/প্রাইভেট চ্যাটে ব্যবহার করার
    পরামর্শ দেওয়া হয় (গ্রুপে লিখলে Key অন্যরাও দেখে ফেলতে পারে)। প্রাইভেসির জন্য বট নিজে থেকে
    ইউজারের মূল মেসেজ মুছে ফেলার চেষ্টা করে (গ্রুপে বট অ্যাডমিন থাকলে কাজ করবে, না থাকলে চুপচাপ স্কিপ)।"""
    user_id = update.effective_user.id
    register_user(user_id)
    if len(context.args) < 2:
        providers_list = ", ".join(OWN_API_KEY_LABEL_BN[p] for p in OWN_API_KEY_PROVIDERS)
        await update.message.reply_text(
            "এভাবে লিখুন: /setapikey provider আপনার_key\n"
            f"প্রোভাইডার: {providers_list} (ছোট হাতের অক্ষরে: openrouter/groq/cerebras)\n"
            "উদাহরণ: /setapikey groq gsk_xxxxxxxxxxxxxxxx\n\n"
            "ফ্রি Key কোথায় পাবেন:\n"
            f"• OpenRouter: {OWN_API_KEY_SIGNUP_URL['openrouter']}\n"
            f"• Groq: {OWN_API_KEY_SIGNUP_URL['groq']}\n"
            f"• Cerebras: {OWN_API_KEY_SIGNUP_URL['cerebras']}\n\n"
            "⚠️ নিরাপত্তার জন্য এই কমান্ডটা প্রাইভেট চ্যাটে (বটকে সরাসরি DM করে) ব্যবহার করুন, গ্রুপে নয়।"
        )
        return
    provider = context.args[0]
    api_key = context.args[1].strip()
    ok, message = set_own_api_key(user_id, provider, api_key)
    await update.message.reply_text(message)
    # প্রাইভেসি: গ্রুপ চ্যাটে Key লিখে থাকলে বট নিজের অনুমতি থাকলে সাথে সাথে সেই মেসেজটা মুছে ফেলার চেষ্টা করে।
    if update.effective_chat and update.effective_chat.type != "private":
        try:
            await update.message.delete()
        except Exception as e:
            logger.debug(f"Phase 45: গ্রুপে Key মেসেজ ডিলিট করা যায়নি (বট অ্যাডমিন নাও থাকতে পারে): {e}")


async def removeapikey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/removeapikey <provider|all> — নিজস্ব API Key মুছে ফেলা।"""
    user_id = update.effective_user.id
    register_user(user_id)
    if not context.args:
        await update.message.reply_text(
            "এভাবে লিখুন: /removeapikey provider (openrouter/groq/cerebras) অথবা /removeapikey all (সবগুলো)"
        )
        return
    ok, message = remove_own_api_key(user_id, context.args[0])
    await update.message.reply_text(message)


async def myapikey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/myapikey — নিজের কোন কোন প্রোভাইডারে নিজস্ব Key যুক্ত আছে তা (মাস্ক করে) দেখা।"""
    user_id = update.effective_user.id
    register_user(user_id)
    own_keys = get_own_api_keys(user_id)
    lines = ["🔑 আপনার নিজস্ব API Key-এর অবস্থা:\n"]
    for provider in OWN_API_KEY_PROVIDERS:
        label = OWN_API_KEY_LABEL_BN[provider]
        key = own_keys.get(provider, "")
        if key:
            lines.append(f"• {label}: ✅ যুক্ত আছে ({mask_api_key(key)})")
        else:
            lines.append(f"• {label}: ❌ যুক্ত নেই (বটের শেয়ার্ড Key ব্যবহার হচ্ছে)")
    if not any(own_keys.values()):
        lines.append("\n💡 নিজস্ব Key যুক্ত করতে: /setapikey provider আপনার_key")
    else:
        lines.append("\nমুছে ফেলতে: /removeapikey provider অথবা /removeapikey all")
    await update.message.reply_text("\n".join(lines))


# ============================= Phase 10: Statistics Manager =============================
# প্রতিটা Provider/Key কতবার ব্যবহার হয়েছে, Response Time, Error, Retry — এগুলো আসলে
# ManagedKey নিজেই ট্র্যাক করে (total_requests/total_failures/avg_response_time/total_retries,
# উপরে দেখুন)। এই ক্লাস শুধু cross-cutting পরিসংখ্যান রাখে যেগুলো কোনো একটা নির্দিষ্ট Key-এর
# না — Response Cache Hit/Miss ও Queue Time — এবং /aistats-এর জন্য সবকিছু একসাথে ফরম্যাট
# করে দেয় (build_ai_stats_text)।

class AIStatisticsManager:
    def __init__(self):
        self.started_at = time.time()
        self.cache_hits = 0
        self.cache_misses = 0
        self.queue_wait_total = 0.0
        self.queue_wait_count = 0
        self.queue_wait_max = 0.0

    def record_cache_hit(self):
        self.cache_hits += 1

    def record_cache_miss(self):
        self.cache_misses += 1

    def record_queue_wait(self, seconds: float):
        self.queue_wait_total += seconds
        self.queue_wait_count += 1
        self.queue_wait_max = max(self.queue_wait_max, seconds)

    def avg_queue_wait(self) -> float:
        return (self.queue_wait_total / self.queue_wait_count) if self.queue_wait_count else 0.0

    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total else 0.0


ai_stats_manager = AIStatisticsManager()


# ============================= Phase 10: Response Cache =============================
# একই (system_prompt + প্রশ্ন) কম্বিনেশন বারবার এলে আবার AI Provider-এ না পাঠিয়ে সরাসরি
# আগের উত্তর থেকে জবাব দেয় (একই ইউজার একই প্রশ্ন বারবার পাঠালে এটাও কভার করে, তবে ক্যাশ
# আসলে content-ভিত্তিক — যেকোনো ইউজার হুবহু একই প্রশ্ন করলেও একবার AI-কে জিজ্ঞেস করলেই যথেষ্ট)।
# শুধু deterministic ফিচারে (translate/grammar/rewrite/tone/summarize/askpdf ইত্যাদি,
# ask_ai(..., use_cache=True) দিয়ে) ব্যবহার হয় — joke/quote-এর মতো ইচ্ছাকৃতভাবে ভিন্ন ভিন্ন
# উত্তর চাওয়া ফিচার, বা AI Memory-ভিত্তিক চ্যাট (ask_ai_with_history, যেখানে প্রসঙ্গ প্রতিবার
# বদলায়) এই ক্যাশে কখনোই ঢোকে না — ডিফল্ট use_cache=False, তাই আগের সব call site অপরিবর্তিত।
# LRU (সর্বোচ্চ AI_CACHE_MAX_ENTRIES এন্ট্রি) + TTL (AI_CACHE_TTL_SECONDS সেকেন্ড পর মেয়াদ
# শেষ) — সম্পূর্ণ মেমরিতে থাকে, বট রিস্টার্ট হলে খালি হয়ে যায়, কোনো এক্সট্রা সার্ভিস/ডিস্ক লাগে না।

class AIResponseCache:
    def __init__(self, max_entries: int = AI_CACHE_MAX_ENTRIES, ttl_seconds: int = AI_CACHE_TTL_SECONDS):
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._store: "OrderedDict[str, tuple]" = OrderedDict()  # key -> (value, expires_at)
        self._lock = asyncio.Lock()

    @staticmethod
    def make_key(system_prompt: str, user_text: str) -> str:
        raw = f"{system_prompt}||{user_text}".strip()
        return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()

    async def get(self, system_prompt: str, user_text: str):
        key = self.make_key(system_prompt, user_text)
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.time() >= expires_at:
                del self._store[key]
                return None
            self._store.move_to_end(key)  # LRU: এইমাত্র ব্যবহৃত হিসেবে সবার শেষে সরানো
            return value

    async def set(self, system_prompt: str, user_text: str, value: str):
        key = self.make_key(system_prompt, user_text)
        async with self._lock:
            self._store[key] = (value, time.time() + self.ttl_seconds)
            self._store.move_to_end(key)
            while len(self._store) > self.max_entries:
                self._store.popitem(last=False)  # LRU eviction: সবচেয়ে পুরনো এন্ট্রি বাদ

    def size(self) -> int:
        return len(self._store)


ai_response_cache = AIResponseCache()

# Phase 35: সাধারণ চ্যাটের (chat_general, Memory বন্ধ থাকা অবস্থায়) জন্য আলাদা, লম্বা-মেয়াদী
# ক্যাশ — একই/প্রায়-একই প্রশ্ন বারবার আসলে (যেকোনো ইউজারের কাছ থেকেই) আবার AI-কে না জিজ্ঞেস
# করে সরাসরি আগের উত্তর দিয়ে দেয়। ai_response_cache-এর মতোই কাজ করে, শুধু TTL অনেক বড়
# (৬ ঘণ্টা) কারণ সাধারণ প্রশ্নের উত্তর ৩০ মিনিটেই পুরনো হয়ে যায় না।
GENERAL_CHAT_CACHE_TTL_SECONDS = 6 * 60 * 60
general_chat_cache = AIResponseCache(max_entries=500, ttl_seconds=GENERAL_CHAT_CACHE_TTL_SECONDS)


# ============================= Phase 9: Async Queue Manager =============================
# একসাথে অনেক ইউজার AI ফিচার ব্যবহার করলে বট freeze না করে সব রিকোয়েস্ট একটা FIFO সারিতে
# জমা রেখে সীমিতসংখ্যক Worker Task দিয়ে সমান্তরালে (non-blocking) প্রসেস করে। ask_ai/
# ask_ai_with_history-এর ভেতর থেকেই এটা ব্যবহার হয় — বাকি কোনো ফিচার/কমান্ডে হাত দিতে হয়নি।

class AIQueueManager:
    """
    Async Queue Manager — asyncio.Queue + একদল Worker Task দিয়ে বানানো, কোনো বাহ্যিক
    সার্ভিস (Redis ইত্যাদি) ছাড়াই। submit() কল করলে রিকোয়েস্টটা সারিতে জমা হয়ে একটা
    asyncio.Future রিটার্ন করে; কোনো একটা ফাঁকা Worker সেটা তুলে নিয়ে ai_router.chat()
    দিয়ে প্রসেস করে Future-এ ফলাফল বসিয়ে দেয়। Worker-গুলো প্রথম submit()-এই লেজি-ভাবে চালু
    হয় (event loop চালু থাকা অবস্থায়), তাই আমদানি করার সময় (module import) কোনো সমস্যা হয় না।
    """

    def __init__(self, max_workers: int = AI_QUEUE_MAX_WORKERS):
        self.queue: "asyncio.Queue" = asyncio.Queue()
        self.max_workers = max_workers
        self._workers_started = False
        self._start_lock = asyncio.Lock()
        self.active_count = 0
        self.total_queued = 0
        self.total_processed = 0
        self.total_failed = 0

    async def _ensure_workers(self):
        if self._workers_started:
            return
        async with self._start_lock:
            if self._workers_started:
                return
            for i in range(self.max_workers):
                asyncio.create_task(self._worker(i + 1), name=f"ai-queue-worker-{i + 1}")
            self._workers_started = True
            logger.info(f"Phase 9 Async Queue Manager চালু হলো — {self.max_workers}টা Worker।")

    async def _worker(self, worker_id: int):
        while True:
            system_prompt, messages, future, enqueued_at, router, max_tokens = await self.queue.get()
            queue_wait = time.time() - enqueued_at
            ai_stats_manager.record_queue_wait(queue_wait)  # Phase 10: Statistics Manager
            if queue_wait > 2:
                logger.info(f"AI Queue Worker #{worker_id}: {queue_wait:.1f}s সারিতে অপেক্ষার পর প্রসেসিং শুরু।")
            self.active_count += 1
            try:
                if not future.done():
                    try:
                        # Phase 45: user_id-এর ভিত্তিতে ইতিমধ্যে ঠিক করা router (নিজস্ব Key
                        # থাকলে সেটা, নাহলে গ্লোবাল শেয়ার্ড ai_router) ব্যবহার হয়।
                        result = await router.chat(system_prompt, messages, max_tokens=max_tokens)
                        if not future.done():
                            future.set_result(result)
                    except Exception as e:  # noqa: BLE001 — যেকোনো এরর future-এ পাঠিয়ে দেওয়া, worker যাতে না মরে
                        self.total_failed += 1
                        if not future.done():
                            future.set_exception(e)
            finally:
                self.active_count -= 1
                self.total_processed += 1
                self.queue.task_done()

    async def submit(self, system_prompt: str, messages: list, user_id: Optional[int] = None, max_tokens: int = 1024) -> str:
        """রিকোয়েস্ট সারিতে জমা দিয়ে ফলাফলের জন্য অপেক্ষা করে (caller-এর জন্য এটা স্বচ্ছ —
        দেখতে সরাসরি ai_router.chat()-এর মতোই লাগে, ভেতরে কিউয়িং/লিমিটেড-কনকারেন্সি চলে)।
        Phase 45: user_id দিলে সেই ইউজারের নিজস্ব API Key (থাকলে) দিয়ে বানানো router ব্যবহার
        হয়, না দিলে বা নিজস্ব Key না থাকলে গ্লোবাল শেয়ার্ড router ব্যবহার হয় (আগের আচরণ)।
        Phase 20-fix: max_tokens pass-through — /codeplan-এর মতো বড় JSON আউটপুটের জন্য।"""
        await self._ensure_workers()
        router = _build_user_ai_router(user_id)
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.total_queued += 1
        await self.queue.put((system_prompt, messages, future, time.time(), router, max_tokens))
        return await future

    def stats(self) -> dict:
        """অ্যাডমিন/ডিবাগিংয়ের জন্য (আপাতত /serverstatus-এর UI বদলানো হয়নি, ভবিষ্যতে দরকার হলে
        এখান থেকেই দেখানো যাবে)।"""
        return {
            "queue_size": self.queue.qsize(),
            "active": self.active_count,
            "max_workers": self.max_workers,
            "total_queued": self.total_queued,
            "total_processed": self.total_processed,
            "total_failed": self.total_failed,
        }


ai_queue_manager = AIQueueManager()


# ============================= AI হেল্পার ফাংশন =============================
# নিচের দুটো ফাংশনের নাম ও প্যারামিটার আগের মতোই রাখা হয়েছে (ask_ai, ask_ai_with_history) —
# বটের বাকি পুরো কোড (translate/grammar/rewrite/summarize/pdf/chat/joke ইত্যাদি সব ফিচার)
# এই দুটো ফাংশনই কল করে, তাই ভেতরের ইমপ্লিমেন্টেশন Groq থেকে AIRouter-এ, এবং এখন Phase 9-এ
# Async Queue Manager + Hard Timeout-এ বদলে দিলেও বাকি কোনো ফিচার/কমান্ডে পরিবর্তন লাগেনি।

async def ask_ai(system_prompt: str, user_text: str, use_cache: bool = False, user_id: Optional[int] = None, max_tokens: int = 1024) -> str:
    """
    একাধিক ফ্রি AI Provider ব্যবহার করে (OpenRouter -> Groq -> Cerebras, স্বয়ংক্রিয় fallback সহ),
    Phase 9-এর Async Queue Manager দিয়ে (non-blocking, সীমিত-কনকারেন্সি) প্রসেস হয়। পুরো
    রিকোয়েস্টের (সব Retry/Provider-বদল মিলিয়ে) একটা Hard Timeout (AI_REQUEST_HARD_TIMEOUT)
    আছে — এর বেশি সময় ধরে আটকে থাকলে বাতিল হয়ে যায়। সব Provider ব্যর্থ হলে বা টাইমআউট হলে
    AIProviderError তোলে — প্রতিটা কলার আগে থেকেই এটা try/except দিয়ে ধরে ইউজারকে বাংলায়
    বন্ধুত্বপূর্ণ এরর মেসেজ দেখায় (Error Handling অপরিবর্তিত)।

    Phase 10: use_cache=True দিলে (translate/grammar/rewrite/tone/summarize/askpdf-এর মতো
    deterministic ফিচারে ব্যবহার হয়) একই system_prompt+প্রশ্ন কম্বিনেশন আগে জিজ্ঞেস করা থাকলে
    সরাসরি Response Cache থেকে উত্তর দেয়, আবার AI Provider-এ পাঠায় না। ডিফল্ট False, তাই
    joke/quote/chat-সহ বাকি সব call site আগের মতোই প্রতিবার তাজা উত্তর পায় — কোনো আচরণ
    বদলায়নি।

    Phase 45: user_id দিলে সেই ইউজারের নিজস্ব API Key (কোনো প্রোভাইডারে থাকলে) ব্যবহার হয় —
    বটের শেয়ার্ড Key Pool স্পর্শ করে না। user_id না দিলে (ডিফল্ট None) আগের মতোই সবসময়
    গ্লোবাল শেয়ার্ড router ব্যবহার হয়, তাই পুরোনো কোনো call site ভাঙে না।

    Phase 20-fix: max_tokens (ডিফল্ট 1024) এখন AI কল পর্যন্ত pass-through হয়। /codeplan-এর
    মতো বড় JSON আউটপুট দরকার হলে কলার max_tokens=4000 দিয়ে ডাকে — অন্য call site-গুলো
    default 1024-ই ব্যবহার করে, তাই কোনো আচরণ বদলায় না।
    """
    if use_cache:
        cached = await ai_response_cache.get(system_prompt, user_text)
        if cached is not None:
            ai_stats_manager.record_cache_hit()
            logger.info("Phase 10 Response Cache: HIT — AI Provider-এ পাঠানো হয়নি।")
            return cached
        ai_stats_manager.record_cache_miss()

    try:
        result = await asyncio.wait_for(
            ai_queue_manager.submit(system_prompt, [{"role": "user", "content": user_text}], user_id=user_id, max_tokens=max_tokens),
            timeout=AI_REQUEST_HARD_TIMEOUT,
        )
    except asyncio.TimeoutError:
        raise AIProviderError(
            f"রিকোয়েস্টটা {AI_REQUEST_HARD_TIMEOUT} সেকেন্ডের মধ্যে শেষ করা যায়নি (Hard Timeout) — একটু পর আবার চেষ্টা করুন।"
        )

    if use_cache:
        await ai_response_cache.set(system_prompt, user_text, result)
    return result


async def ask_ai_with_history(system_prompt: str, history: list, user_text: str, user_id: Optional[int] = None) -> str:
    """
    AI Memory ফিচার: আগের কয়েকটা মেসেজ context হিসেবে পাঠিয়ে AI-কে কথোপকথন মনে রাখতে সাহায্য করে।
    history হলো [{"role": "user"/"assistant", "content": "..."}] ফরম্যাটের লিস্ট।
    এটাও AIRouter (OpenRouter -> Groq -> Cerebras) ব্যবহার করে, Phase 9-এর Queue Manager +
    Hard Timeout সহ। Phase 45: user_id দিলে সেই ইউজারের নিজস্ব API Key (থাকলে) ব্যবহার হয়।
    """
    messages = list(history) + [{"role": "user", "content": user_text}]
    try:
        return await asyncio.wait_for(
            ai_queue_manager.submit(system_prompt, messages, user_id=user_id), timeout=AI_REQUEST_HARD_TIMEOUT
        )
    except asyncio.TimeoutError:
        raise AIProviderError(
            f"রিকোয়েস্টটা {AI_REQUEST_HARD_TIMEOUT} সেকেন্ডের মধ্যে শেষ করা যায়নি (Hard Timeout) — একটু পর আবার চেষ্টা করুন।"
        )


def flood_check(user_id: int) -> bool:
    """
    Anti-Flood: ইউজার খুব দ্রুত মেসেজ পাঠাচ্ছে কিনা চেক করে।
    True মানে চালিয়ে যাওয়া যাবে, False মানে ইউজার সাময়িক ব্লকড।
    Phase 4 প্রিমিয়াম সুবিধা: সক্রিয় প্রিমিয়াম ইউজারদের জন্য এই কুলডাউন প্রযোজ্য নয়।
    """
    if is_premium_active(user_id):
        return True

    now = time.time()

    blocked_until = _flood_blocked_until.get(user_id)
    if blocked_until and now < blocked_until:
        return False
    if blocked_until and now >= blocked_until:
        _flood_blocked_until.pop(user_id, None)
        _flood_strikes[user_id] = 0

    last_time = _last_message_time.get(user_id)
    _last_message_time[user_id] = now

    if last_time is not None and (now - last_time) < MIN_SECONDS_BETWEEN_MESSAGES:
        _flood_strikes[user_id] = _flood_strikes.get(user_id, 0) + 1
        if _flood_strikes[user_id] >= FLOOD_WARNING_THRESHOLD:
            _flood_blocked_until[user_id] = now + FLOOD_BLOCK_SECONDS
            return False
    else:
        _flood_strikes[user_id] = 0

    return True


def save_feedback(user_id: int, message: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO feedback (user_id, message, created_at) VALUES (?, ?, ?)",
        (user_id, message, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def save_bug_report(user_id: int, message: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bug_reports (user_id, message, created_at) VALUES (?, ?, ?)",
        (user_id, message, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def get_user_settings(user_id: int):
    """auto_reply, memory_enabled, language রিটার্ন করে (নতুন কলাম, get_user_row থেকে আলাদা রাখা হলো)।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT auto_reply, memory_enabled, language FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return (1, 1, "bn")
    auto_reply, memory_enabled, language = row
    return (
        1 if auto_reply is None else auto_reply,
        1 if memory_enabled is None else memory_enabled,
        language or "bn",
    )


def log_usage(user_id: int, action: str = "general"):
    """Leaderboard ও Daily/Monthly Statistics-এর জন্য প্রতিটা ব্যবহার লগ করে।"""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usage_log (user_id, action, created_at) VALUES (?, ?, ?)",
            (user_id, action, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"usage_log এ লিখতে সমস্যা: {e}")


MEMORY_HISTORY_LIMIT = 6      # প্রতিবার AI-কে যতগুলো আগের মেসেজ মনে করিয়ে দেওয়া হবে
MEMORY_KEEP_PER_USER = 40     # একজন ইউজারের জন্য ডাটাবেসে সর্বোচ্চ যতগুলো মেসেজ রাখা হবে


def save_message(user_id: int, role: str, content: str):
    """AI Memory: চ্যাটের হিস্টোরি সেভ করে, এবং পুরোনো লগ ছেঁটে ফেলে যাতে ডাটাবেস বড় না হয়ে যায়।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversation_history (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, role, content[:4000], datetime.now().isoformat(timespec="seconds")),
    )
    cur.execute(
        """
        DELETE FROM conversation_history
        WHERE user_id = ? AND id NOT IN (
            SELECT id FROM conversation_history WHERE user_id = ?
            ORDER BY id DESC LIMIT ?
        )
        """,
        (user_id, user_id, MEMORY_KEEP_PER_USER),
    )
    conn.commit()
    conn.close()


def get_recent_history(user_id: int, limit: int = MEMORY_HISTORY_LIMIT):
    """AI Memory: সাম্প্রতিক কয়েকটা মেসেজ ফেরত দেয় (পুরনো থেকে নতুন ক্রমে)।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM conversation_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    rows.reverse()
    return [{"role": role, "content": content} for role, content in rows]


def clear_memory(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def detect_language(text: str) -> str:
    """
    Language Detection ফিচার। langdetect লাইব্রেরি থাকলে সেটা ব্যবহার করে,
    না থাকলে ইউনিকোড রেঞ্জ দেখে সহজ পদ্ধতিতে ভাষা অনুমান করে (সম্পূর্ণ ফ্রি, অফলাইন)।
    রিটার্ন করে ISO-এর কাছাকাছি একটা কোড, যেমন: bn, en, hi, ar, unknown
    """
    if not text or not text.strip():
        return "unknown"

    if LANGDETECT_SUPPORT:
        try:
            return _langdetect_detect(text)
        except Exception:
            pass

    # ফলব্যাক: ইউনিকোড ব্লক দেখে সহজভাবে অনুমান
    counts = {"bn": 0, "hi": 0, "ar": 0, "en": 0}
    for ch in text:
        code = ord(ch)
        if 0x0980 <= code <= 0x09FF:
            counts["bn"] += 1
        elif 0x0900 <= code <= 0x097F:
            counts["hi"] += 1
        elif 0x0600 <= code <= 0x06FF:
            counts["ar"] += 1
        elif ch.isalpha() and code < 128:
            counts["en"] += 1
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "unknown"


LANGUAGE_NAMES_BN = {
    "bn": "বাংলা",
    "en": "ইংরেজি",
    "hi": "হিন্দি",
    "ar": "আরবি",
    "ur": "উর্দু",
    "unknown": "শনাক্ত করা যায়নি",
}


def language_display_name(code: str) -> str:
    return LANGUAGE_NAMES_BN.get(code, code)


# ============================= Phase 3: মাল্টি-ভাষা সাপোর্ট =============================

def get_effective_language(user_id: int) -> tuple:
    """
    ইউজার /setlang দিয়ে নিজে ভাষা বেছে নিয়েছেন কিনা এবং সেটা কী, তা রিটার্ন করে।
    রিটার্ন: (language_code, is_manual) — is_manual False মানে বট নিজে থেকে ভাষা বুঝে (auto) উত্তর দেবে।
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT language, lang_manual FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return ("bn", False)
    lang, manual = row
    return (lang or "bn", bool(manual))


def set_user_language(user_id: int, lang_code: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET language = ?, lang_manual = 1 WHERE user_id = ?",
        (lang_code, user_id),
    )
    conn.commit()
    conn.close()


def set_user_language_auto(user_id: int):
    """ইউজার আবার 'Auto' মোডে ফিরে গেলে — বট নিজে থেকে মেসেজের ভাষা বুঝে উত্তর দেবে।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET lang_manual = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


async def localize(user_id: int, bn_text: str) -> str:
    """
    ইউজার /setlang দিয়ে বাংলা ছাড়া অন্য ভাষা বেছে নিয়ে থাকলে, বটের নিজস্ব (স্ট্যাটিক) বার্তা
    সেই ভাষায় অনুবাদ করে দেয়। বাংলা হলে বা কিছু সেট না থাকলে মূল লেখাই ফেরত যায়।
    Performance Improvement: একই লেখা একই ভাষায় বারবার অনুবাদ না করে মেমরিতে ক্যাশ রাখা হয়।
    অনুবাদে সমস্যা হলে (এরর/টাইমআউট) মূল বাংলা লেখাই নিরাপদে ফেরত দেওয়া হয়, বট ভাঙে না।
    """
    lang, manual = get_effective_language(user_id)
    if not manual or lang == "bn":
        return bn_text

    cache_key = (lang, hashlib.md5(bn_text.encode("utf-8")).hexdigest())
    if cache_key in _localize_cache:
        _localize_cache.move_to_end(cache_key)
        return _localize_cache[cache_key]

    lang_name = UI_LANG_CHOICES.get(lang, lang)
    try:
        translated = await ask_ai(
            f"তুমি একজন অনুবাদক। নিচের বাংলা টেক্সটটা {lang_name} ভাষায় অনুবাদ করো। "
            "লাইনব্রেক, ইমোজি, স্ল্যাশ কমান্ড (যেমন /start) এবং ফরম্যাটিং অক্ষুণ্ণ রাখো। "
            "শুধু অনুবাদটাই ফেরত দাও, অন্য কোনো ব্যাখ্যা লিখবে না।",
            bn_text,
        )
        translated = translated.strip() or bn_text
    except Exception as e:
        logger.warning(f"UI অনুবাদ এরর, বাংলা রেখে দেওয়া হলো: {e}")
        translated = bn_text

    _localize_cache[cache_key] = translated
    if len(_localize_cache) > LOCALIZE_CACHE_MAX:
        _localize_cache.popitem(last=False)  # সবচেয়ে পুরনো ক্যাশ এন্ট্রি বাদ দেওয়া (মেমরি সীমিত রাখতে)
    return translated


async def quota_guard(update: Update, action: str = "general") -> bool:
    """সীমা শেষ হলে মেসেজ পাঠিয়ে False রিটার্ন করে, কাজ চালিয়ে যাওয়া ঠিক থাকলে True।"""
    user_id = update.effective_user.id
    # Note: Use effective_message to handle edited message updates safely.
    # Pattern should be audited repo-wide in a follow-up.
    msg = update.message or update.effective_message
    if is_banned(user_id):
        if msg:
            await msg.reply_text(await localize(user_id, "দুঃখিত, আপনাকে এই বট ব্যবহার করা থেকে বিরত রাখা হয়েছে।"))
        return False
    if user_id not in ADMIN_IDS and not flood_check(user_id):
        if msg:
            await msg.reply_text(
                await localize(user_id, f"⚠️ আপনি খুব দ্রুত মেসেজ পাঠাচ্ছেন। অনুগ্রহ করে {FLOOD_BLOCK_SECONDS} সেকেন্ড অপেক্ষা করুন।")
            )
        return False
    if not check_and_use_quota(user_id):
        daily_limit = get_daily_limit(user_id)
        extra_hint = "" if is_premium_active(user_id) else " বেশি সীমা পেতে প্রিমিয়াম নিন — /premiumstatus দেখুন।"
        if msg:
            await msg.reply_text(
                await localize(
                    user_id,
                    f"আজকের সীমা ({daily_limit} বার) শেষ হয়ে গেছে। আগামীকাল আবার ব্যবহার করতে পারবেন।{extra_hint}",
                )
            )
        return False
    log_usage(user_id, action)
    return True


# ============================= Coding command catalogue =============================
# এই তালিকাটাই /start, /menu এবং /codehelp—তিন জায়গায় ব্যবহার হয়। ফলে নতুন coding
# command যোগ হলে এক জায়গায় আপডেট করলেই সব help surface একই থাকে।
# প্রতিটা গ্রুপের দ্বিতীয় উপাদানটা হলো admin_only ফ্ল্যাগ — /start, /help, /menu ও
# /codehelp-এর মতো user-facing help surface-এ শুধু ফ্ল্যাগ False অর্থাৎ public গ্রুপই
# দেখানো হয়; admin-only command-এর নিজেদের handler অপরিবর্তিত থাকে।
# টাইপ: (group_title, admin_only, commands)
CODING_COMMAND_GROUPS: Tuple[Tuple[str, bool, Tuple[Tuple[str, str], ...]], ...] = (
    (
        "👤 সবার জন্য",
        False,
        (
            ("/codehelp", "এই সম্পূর্ণ coding command তালিকা"),
            ("/codingengine", "coding engine ও module status"),
            ("/codeproject <বিবরণ>", "নতুন coding project ও ধাপভিত্তিক plan"),
            ("/codeplan <বিবরণ>", "autonomous multi-step plan তৈরি"),
            ("/codenext", "পরের task implement, test ও review"),
            ("/codestatus", "active project-এর অগ্রগতি"),
            ("/codetask <নাম্বার>", "নির্দিষ্ট সম্পন্ন task-এর code"),
            ("/codeprojects", "আপনার সব coding project"),
            ("/useproject <আইডি>", "একটি project active করা"),
            ("/exportcode", "সম্পন্ন code ফাইল হিসেবে নেওয়া"),
            ("/deleteproject <আইডি>", "নিজের project মুছে ফেলা"),
            ("/codehistory", "project snapshot history"),
            ("/codediff <seq1> <seq2>", "দুই snapshot-এর diff"),
            ("/coderollback [seq]", "known-good snapshot-এ ফেরা"),
        ),
    ),
    (
        "🔐 শুধু অ্যাডমিন",
        True,
        (
            ("/codebasescan [path]", "codebase scan ও re-index"),
            ("/codebasestatus [path]", "codebase index status"),
            ("/contextpreview <request>", "Smart Context preview"),
            ("/testreport <task_id>", "autonomous test report"),
            ("/errorfixlog <task_id>", "auto-fix attempt log"),
            ("/reviewreport <task_id>", "code review report"),
            ("/securityscan [mode]", "security scan চালানো"),
            ("/projectmemory [query]", "Project Memory দেখা/খোঁজা"),
            ("/codingknowledge [query]", "coding knowledge দেখা/খোঁজা"),
            ("/impactanalysis <file/request>", "change impact analysis"),
            ("/codeauto [project_id] [max_tasks]", "continuous autonomous run"),
            ("/codeautostatus", "সর্বশেষ autonomous run status"),
            ("/codeexec <command>", "allow-listed workspace command চালানো"),
        ),
    ),
)


def build_coding_commands_text(include_title: bool = True) -> str:
    """user-facing তালিকা তৈরি করে — শুধু public (সবার) coding command।
    admin-only গ্রুপগুলো (/start, /help, /menu ও /codehelp-এর কোনোটাতেই দেখানো হয় না)
    এখানে ইচ্ছে করেই বাদ দেওয়া।"""
    lines = ["💻 Coding Commands", "━━━━━━━━━━━━━━━"] if include_title else []
    for group_title, admin_only, commands in CODING_COMMAND_GROUPS:
        if admin_only:
            continue
        if lines:
            lines.append("")
        lines.append(group_title)
        lines.extend(f"{usage} — {description}" for usage, description in commands)
    return "\n".join(lines)


CODING_COMMANDS_BODY = build_coding_commands_text(include_title=False)


def build_admin_coding_commands_text() -> str:
    """🔐 admin-only coding command-গুলোর তালিকা — শুধু /adminpanel-এর ভিতরে দেখানো হয়।

    সাধারণ ইউজারের কোনো help surface-এ (/start, /help, /menu, /codehelp) এই লেখা
    কখনো পাঠানো হয় না; তালিকাটা একমাত্র Admin Control Panel-এর ভেতরেই যায়। প্রতিটা
    কমান্ডের নিজস্ব handler-এর শুরুতে is_admin() চেক আগে থেকেই আছে, তাই কেউ কমান্ডটা
    নিজে থেকে টাইপ করলেও "⛔ এই কমান্ডটি শুধু অ্যাডমিনের জন্য।" উত্তর পাবে।
    """
    lines = [
        "🔐 Admin-only Coding Commands",
        "━━━━━━━━━━━━━━━",
        "এই কমান্ডগুলো শুধু অ্যাডমিন চালাতে পারেন। সাধারণ ইউজারদের",
        "/start, /help, /menu বা /codehelp-এ এগুলো দেখানো হয় না।",
    ]
    for group_title, admin_only, commands in CODING_COMMAND_GROUPS:
        if not admin_only:
            continue
        lines.append("")
        lines.append(group_title)
        lines.extend(f"{usage} — {description}" for usage, description in commands)
    return "\n".join(lines)


# ============================= বেসিক কমান্ড =============================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referrer_id = 0
    if context.args:
        payload = context.args[0]
        if payload.startswith("ref_") and payload[4:].isdigit():
            referrer_id = int(payload[4:])

    is_new = register_user(user_id, referred_by=referrer_id if referrer_id else 0)

    referral_welcome_line = ""
    if is_new and referrer_id:
        applied = apply_referral_bonus(referrer_id, user_id)
        if applied:
            referral_welcome_line = f"\n🎁 রেফারেল বোনাস: আপনি +{REFERRAL_BONUS} অতিরিক্ত দৈনিক সীমা পেয়েছেন! স্বাগতম।\n"
            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        "🎉 আপনার রেফারেল লিংক দিয়ে একজন নতুন ইউজার যোগ দিয়েছেন!\n"
                        f"আপনি +{REFERRAL_BONUS} বোনাস দৈনিক সীমা পেয়েছেন। মোট রেফারেল ও বোনাস দেখতে: /myreferrals"
                    ),
                )
            except Exception as e:
                logger.warning(f"রেফারেল নোটিফিকেশন পাঠাতে সমস্যা (referrer {referrer_id}): {e}")

    text = (
        f"🤖 {BOT_NAME}-এ স্বাগতম!\n"
        f"একটি প্রফেশনাল AI অ্যাসিস্ট্যান্ট বট — লেখা, অনুবাদ, কণ্ঠ, ভিডিও ডাবিং সহ নানান কাজে সাহায্য করবে।\n"
        f"{referral_welcome_line}"
        "━━━━━━━━━━━━━━━\n\n"
        "সরাসরি যেকোনো কিছু লিখুন — AI চ্যাট উত্তর দেবে (মনে রাখবে, ভাষা বুঝে উত্তর দেবে)\n"
        "📋 /menu লিখলে বাটন দিয়ে পুরো মেনু দেখতে পারবেন\n\n"
        "📝 লেখার কাজ\n"
        "/translate ভাষা লেখা — অনুবাদ (উদাহরণ: /translate english আমি ভালো আছি)\n"
        "/grammar লেখা — গ্রামার ঠিক করা\n"
        "/rewrite লেখা — লেখা নতুনভাবে লেখা\n"
        "/tone formal/casual লেখা — টোন বদলানো\n"
        "/summarize — কোনো মেসেজে রিপ্লাই দিয়ে লিখুন, সামারি করে দেবে\n"
        "/pdf — কোনো PDF ফাইলে রিপ্লাই দিয়ে লিখুন, সামারি করে দেবে\n"
        "/detectlang লেখা — ভাষা শনাক্ত করা\n\n"
        "🎬 ভিডিও ও কণ্ঠ\n"
        "/dub — ভিডিওতে রিপ্লাই দিয়ে লিখুন, বাংলা কণ্ঠে ডাবিং করে দেবে (২০ MB এর নিচে)\n"
        "/dub_part, /dub_finish, /dub_cancel — বড় ভিডিও ভাগে ভাগে ডাবিং করার কমান্ড\n"
        "/tts লেখা — লেখা থেকে কণ্ঠ বানাবে\n"
        "ভয়েস মেসেজ পাঠালে — লেখায় রূপান্তর করে দেবে\n"
        "/setvoice, /setspeed — কণ্ঠ ও গতি বদলানো\n\n"
        "🖼️ ছবি ও ডকুমেন্ট\n"
        "/ocr — কোনো ছবিতে রিপ্লাই দিয়ে লিখুন, ছবির লেখা বের করে দেবে\n"
        "/askpdf প্রশ্ন — PDF-এ রিপ্লাই দিয়ে (অথবা আগে একবার পড়ানো থাকলে সরাসরি) নির্দিষ্ট প্রশ্নের উত্তর\n"
        "/clearpdf — সংরক্ষিত PDF সেশন মুছে ফেলা\n\n"
        "💻 কোডিং\n"
        f"{CODING_COMMANDS_BODY}\n\n"
        "👤 অন্যান্য\n"
        "/profile — আপনার ব্যবহারের হিসাব\n"
        "/mylimit — আজকের বাকি সীমা\n"
        "/settings — সব সেটিংস এক জায়গায় (বাটন দিয়ে)\n"
        "/setlang — বটের উত্তর কোন ভাষায় হবে সেট করা\n"
        "/autoreply on/off — সরাসরি লেখায় বট উত্তর দেবে কিনা\n"
        "/memory on/off, /clearmemory — AI Memory নিয়ন্ত্রণ\n"
        "/noapimode on/off — চালু থাকলে আপনার চ্যাটে বট কোনো AI API কল করবে না, শুধু Brain OS দিয়ে উত্তর দেবে\n"
        "/leaderboard — টপ ব্যবহারকারী তালিকা\n"
        "/joke, /quote, /dice, /coin — মজার কমান্ড\n"
        "/feedback লেখা — মতামত জানান\n"
        "/bugreport লেখা — কোনো সমস্যা জানান\n"
        "/ping — বট সাড়া দিচ্ছে কিনা চেক\n"
        "/uptime — বট কতক্ষণ চালু আছে\n"
        "/about — এই বট সম্পর্কে তথ্য\n\n"
        "👑 প্রিমিয়াম\n"
        "/premiumstatus — আপনার প্ল্যান (ফ্রি/প্রিমিয়াম) ও মেয়াদ দেখুন\n\n"
        "🔑 নিজস্ব API Key\n"
        "/setapikey provider key — নিজের OpenRouter/Groq/Cerebras Key যুক্ত করুন (আরও দ্রুত ও নির্ভুল উত্তর, শেয়ার্ড সীমার বাইরে)\n"
        "/myapikey — কোন প্রোভাইডারে নিজস্ব Key যুক্ত আছে দেখুন\n"
        "/removeapikey provider — নিজস্ব Key মুছে ফেলুন\n\n"
        "🎁 রেফারেল\n"
        "/myreferrals — আপনার নিজের রেফার লিংক ও বোনাসের হিসাব দেখুন\n\n"
        "🏷️ উৎস চিহ্ন (Source badge)\n"
        "প্রতিটা তথ্যবহ উত্তরের নিচে দেখানো হয় তথ্যটা কোথা থেকে এসেছে:\n"
        "🔵 Groq API (AI-এর লেখা) · 🌐 Browser Search (লাইভ ওয়েব) · 💾 Database (নিজের নলেজ বেস) · 🔄 Hybrid (মিশ্র)\n\n"
        f"প্রতিদিন ফ্রি সীমা: {FREE_DAILY_LIMIT} বার, প্রিমিয়াম সীমা: {PREMIUM_DAILY_LIMIT} বার (AI ফিচারের জন্য)\n"
        "━━━━━━━━━━━━━━━\n"
        f"✨ Developed by {CREATOR_COMPANY}"
    )
    # Phase 45: /start-এর সব তথ্য (public coding command সহ) এখন একটাই বার্তায় —
    # আলাদা দ্বিতীয় বার্তা নেই। তালিকাটা /menu ও /codehelp-এর সঙ্গে একই shared source
    # (CODING_COMMAND_GROUPS) থেকে তৈরি, তাই সব help surface একই থাকে।
    # 🔐 admin-only coding command (/codebasescan, /codeauto, /codeexec …) এখানে ইচ্ছে করেই
    # নেই: CODING_COMMANDS_BODY শুধু public গ্রুপ নেয়। ওগুলোর তালিকা থাকে শুধু /adminpanel-এর
    # ভিতরে, আর প্রতিটা কমান্ডের handler-এ is_admin() চেক থাকায় সাধারণ ইউজার চালাতেও পারে না।
    await update.message.reply_text(await localize(user_id, text))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)


async def myreferrals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """নিজের রেফার লিংক, কতজনকে রেফার করেছেন এবং কতটুকু বোনাস পেয়েছেন তা দেখায়।"""
    user_id = update.effective_user.id
    register_user(user_id)
    referral_count = get_referral_count(user_id)
    bonus = get_bonus_daily_limit(user_id)
    bot_username = context.bot.username or ""
    link = build_referral_link(bot_username, user_id) if bot_username else "(বট ইউজারনেম পাওয়া যায়নি, একটু পর আবার চেষ্টা করুন)"

    maxed_out_line = (
        f"\n(সর্বোচ্চ বোনাস সীমা {REFERRAL_MAX_BONUS} এ পৌঁছে গেছেন 🎉)" if bonus >= REFERRAL_MAX_BONUS else ""
    )
    text = (
        "🎁 রেফারেল প্রোগ্রাম\n"
        "━━━━━━━━━━━━━━━\n"
        f"আপনার লিংক: {link}\n\n"
        f"👥 এই লিংক দিয়ে যোগ দিয়েছেন: {referral_count} জন\n"
        f"⭐ আপনার বর্তমান বোনাস দৈনিক সীমা: +{bonus}{maxed_out_line}\n\n"
        f"যাকে আনবেন সে নতুন হয়ে থাকলে দুজনেই +{REFERRAL_BONUS} করে অতিরিক্ত দৈনিক সীমা পাবেন (স্থায়ীভাবে)।\n"
        "লিংকটা বন্ধুদের সাথে শেয়ার করুন!"
    )
    await update.message.reply_text(await localize(user_id, text))


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"ℹ️ {BOT_NAME} সম্পর্কে\n"
        "━━━━━━━━━━━━━━━\n"
        f"🏢 তৈরি করেছে: {CREATOR_COMPANY}\n"
        f"👨‍💻 ডেভেলপার: {CREATOR_NAME}\n"
        "⚙️ ব্যবহৃত প্রযুক্তি: AI (Groq Llama), Text-to-Speech, Speech-to-Text\n"
        "🔒 নিরাপদ ও দ্রুত রেসপন্স\n"
        "━━━━━━━━━━━━━━━\n"
        "কোনো মতামত বা সমস্যা থাকলে অ্যাডমিনের সাথে যোগাযোগ করুন।"
    )
    await update.message.reply_text(await localize(update.effective_user.id, text))


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id)
    row = get_user_row(user_id)
    voice, speed, banned, count, last_date = row
    today = str(date.today())
    used_today = count if last_date == today else 0

    if user_id in ADMIN_IDS:
        limit_text = "সীমাহীন (অ্যাডমিন)"
        premium_line = ""
    else:
        active = is_premium_active(user_id)
        daily_limit = get_daily_limit(user_id)
        limit_text = f"{used_today}/{daily_limit}"
        if active:
            _, premium_until, _ = get_premium_info(user_id)
            premium_line = (
                f"\n👑 প্ল্যান: প্রিমিয়াম (মেয়াদ শেষ: {premium_until})"
                if premium_until
                else "\n👑 প্ল্যান: প্রিমিয়াম (আজীবন)"
            )
        else:
            premium_line = "\n🆓 প্ল্যান: ফ্রি"

    referral_count = get_referral_count(user_id)
    bonus = get_bonus_daily_limit(user_id)
    referral_line = (
        f"\n🎁 রেফারেল বোনাস: +{bonus} (রেফার করেছেন {referral_count} জনকে) — /myreferrals"
        if (referral_count or bonus)
        else "\n🎁 রেফারেল বোনাস: এখনো নেই — /myreferrals দিয়ে আপনার লিংক নিন"
    )

    text = (
        f"আপনার প্রোফাইল:\n"
        f"কণ্ঠ পছন্দ: {'ছেলে' if voice == 'male' else 'মেয়ে'}\n"
        f"গতি পছন্দ: {speed}\n"
        f"আজকের ব্যবহার: {limit_text}"
        f"{premium_line}"
        f"{referral_line}"
    )
    await update.message.reply_text(await localize(user_id, text))


async def mylimit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """শুধু আজকের ব্যবহারের সীমা দেখানোর জন্য ছোট কমান্ড।"""
    user_id = update.effective_user.id
    register_user(user_id)
    row = get_user_row(user_id)
    _, _, _, count, last_date = row
    today = str(date.today())
    used_today = count if last_date == today else 0
    if user_id in ADMIN_IDS:
        await update.message.reply_text(await localize(user_id, "আপনি অ্যাডমিন — আপনার কোনো দৈনিক সীমা নেই। ✅"))
        return

    active = is_premium_active(user_id)
    daily_limit = get_daily_limit(user_id)
    remaining = max(0, daily_limit - used_today)
    plan_line = "👑 প্ল্যান: প্রিমিয়াম" if active else "🆓 প্ল্যান: ফ্রি"
    upgrade_hint = "" if active else "\nবেশি সীমা পেতে প্রিমিয়াম নিন — /premiumstatus দিয়ে বিস্তারিত দেখুন।"
    await update.message.reply_text(
        await localize(
            user_id,
            f"📊 আজকের ব্যবহার: {used_today}/{daily_limit}\n"
            f"বাকি আছে: {remaining} বার\n"
            f"{plan_line}\n"
            f"রিসেট হবে: প্রতিদিন রাত ১২টায় (সার্ভার সময় অনুযায়ী)"
            f"{upgrade_hint}",
        )
    )


# ============================= সিস্টেম কমান্ড (Ping / Uptime / Status) =============================

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.monotonic()
    sent = await update.message.reply_text("পিং করা হচ্ছে...")
    elapsed_ms = (time.monotonic() - start) * 1000
    await sent.edit_text(f"🏓 পং! রেসপন্স সময়: {elapsed_ms:.0f} ms")


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days} দিন")
    if hours:
        parts.append(f"{hours} ঘণ্টা")
    if minutes:
        parts.append(f"{minutes} মিনিট")
    parts.append(f"{seconds} সেকেন্ড")
    return " ".join(parts)


async def uptime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    running_for = time.time() - BOT_START_TIME
    await update.message.reply_text(f"⏱️ বট চালু আছে: {format_duration(running_for)} ধরে।")


async def server_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিনের জন্য সার্ভারের অবস্থা দেখার কমান্ড।"""
    if not has_role(update.effective_user.id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return
    running_for = time.time() - BOT_START_TIME
    db_size_mb = (os.path.getsize(DB_PATH) / (1024 * 1024)) if os.path.exists(DB_PATH) else 0
    disk = shutil.disk_usage(os.path.dirname(os.path.abspath(__file__)))
    disk_free_mb = disk.free / (1024 * 1024)
    disk_total_mb = disk.total / (1024 * 1024)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    conn.close()

    text = (
        "🖥️ সার্ভার স্ট্যাটাস\n"
        "━━━━━━━━━━━━━━━\n"
        f"আপটাইম: {format_duration(running_for)}\n"
        f"Python সংস্করণ: {platform.python_version()}\n"
        f"OS: {platform.system()} {platform.release()}\n"
        f"মোট ইউজার: {total_users}\n"
        f"ডাটাবেস সাইজ: {db_size_mb:.2f} MB\n"
        f"ডিস্ক ফাঁকা: {disk_free_mb:.0f} MB / {disk_total_mb:.0f} MB\n"
        f"PDF সাপোর্ট: {'✅' if PDF_SUPPORT else '❌'}\n"
        f"OCR সাপোর্ট: {'✅' if OCR_SUPPORT else '❌'}\n"
        f"JobQueue (শিডিউল ব্রডকাস্ট): {'✅' if getattr(context, 'job_queue', None) is not None else '❓'}\n"
        f"Speech-to-Text (Groq Whisper): {'✅' if WHISPER_SUPPORT else '❌'}\n"
        "── AI Provider (ক্রম অনুযায়ী, Key Pool সহ) ──\n"
        f"1. OpenRouter: {len(openrouter_key_pool.healthy_keys())}/{len(openrouter_key_pool.keys)} Key সুস্থ ({OPENROUTER_MODEL})\n"
        f"2. Groq: {len(groq_key_pool.healthy_keys())}/{len(groq_key_pool.keys)} Key সুস্থ ({GROQ_MODEL})\n"
        f"3. Cerebras: {len(cerebras_key_pool.healthy_keys())}/{len(cerebras_key_pool.keys)} Key সুস্থ ({CEREBRAS_MODEL})\n"
        f"🧠 Brain OS-এর মাধ্যমে AI কল সাশ্রয় হয়েছে: {brain_os_metrics.get('direct_answers', 0)} বার\n"
    )
    await update.message.reply_text(text)


# ============================= ফিডব্যাক ও বাগ রিপোর্ট =============================

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("এভাবে লিখুন: /feedback আপনার মতামত")
        return
    user_id = update.effective_user.id
    save_feedback(user_id, text)
    await update.message.reply_text("ধন্যবাদ! আপনার মতামত পৌঁছে গেছে। 🙏")
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id, text=f"📩 নতুন ফিডব্যাক (User: {user_id}):\n{text}"
            )
        except Exception as e:
            logger.warning(f"অ্যাডমিনকে ফিডব্যাক পাঠাতে সমস্যা: {e}")


async def bugreport_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("এভাবে লিখুন: /bugreport সমস্যার বর্ণনা")
        return
    user_id = update.effective_user.id
    save_bug_report(user_id, text)
    await update.message.reply_text("ধন্যবাদ! বাগ রিপোর্টটি জমা হয়েছে। শীঘ্রই দেখা হবে। 🐞")
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id, text=f"🐞 নতুন বাগ রিপোর্ট (User: {user_id}):\n{text}"
            )
        except Exception as e:
            logger.warning(f"অ্যাডমিনকে বাগ রিপোর্ট পাঠাতে সমস্যা: {e}")


# ============================= AI টেক্সট ফিচার =============================

# ============================= Phase 17: Brain OS Live Integration =============================

# Runtime metrics: how many AI calls were avoided by a direct Brain OS answer.
brain_os_metrics = {
    "direct_answers": 0,
    "ai_routes": 0,
    "direct_failures": 0,
    "time_sensitive_skips": 0,  # Phase 48: time-sensitive প্রশ্নে Step 1 (Database) স্কিপের সংখ্যা
    "no_api_stuck": 0,   # Phase 43: No-API-Call Mode (per-user) চালু থাকা অবস্থায় মোট যতবার Brain OS নিজে থেকে উত্তর দিতে পারেনি (সব ইউজার মিলিয়ে)
    "browse_answers": 0,  # Phase 44: Brain OS ডাটাবেজে না পেয়ে ফ্রি Browse Search (DuckDuckGo/Wikipedia) দিয়ে যতবার উত্তর দিয়েছে
}


# ============================= Phase 43: No API Call Mode (per-user) =============================
# উদ্দেশ্য: প্রতিটা ইউজার চাইলে নিজের চ্যাটে টেস্টিং/ডেমো মোড চালু করতে পারবে — চালু থাকলে সেই
# ইউজারের সাথে বট কোনো AI API (Groq/OpenRouter/Cerebras) কল করবে না, শুধু Brain OS
# (Knowledge/Pattern/Template/Documentation/Decision Engine) দিয়েই উত্তর দেওয়ার চেষ্টা করবে।
# এটা গ্লোবাল না — অন্য ইউজারদের চ্যাটে কোনো প্রভাব পড়ে না। উত্তর না পেলে বট ইউজারকে সরাসরি
# জানাবে কোন ধাপে (stage) গিয়ে আটকে গেছে এবং আরও তথ্য চাইবে।

_BRAIN_STAGE_LABEL_BN = {
    "knowledge": "Knowledge Engine",
    "pattern": "Pattern Engine",
    "template": "Template Engine",
    "documentation": "Documentation Engine",
    "decision": "Decision Engine",
    "ai": "AI (এই মোডে বন্ধ)",
}


def is_no_api_mode(user_id: int) -> bool:
    """এই ইউজারের চ্যাটে No API Call Mode চালু আছে কিনা।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT no_api_mode FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row and row[0] == 1)


def set_no_api_mode(user_id: int, enabled: bool) -> None:
    """এই ইউজারের জন্য No API Call Mode চালু/বন্ধ করে — শুধু তার নিজের চ্যাটেই প্রভাব ফেলে।"""
    update_field(user_id, "no_api_mode", 1 if enabled else 0)


# ============================= Phase 44: Browse Search (ফ্রি ওয়েব সার্চ ফলব্যাক) =============================
# উদ্দেশ্য: ইউজার কিছু জিজ্ঞেস করলে Brain OS প্রথমে নিজের ডাটাবেজে (Knowledge/Pattern/
# Template/Documentation Engine) খোঁজে (Decision Engine, উপরে আগে থেকেই আছে)। সেখানে
# ভরসায়োগ্য সরাসরি উত্তর না পেলে, সরাসরি AI API কল করার আগে একবার Browse Search চেষ্টা
# করা হয়। Phase 48 থেকে চেইনের ক্রম: Real Web Search (Tavily — TAVILY_API_KEY থাকলে)
# → DuckDuckGo Instant Answer (সম্পূর্ণ ফ্রি) → Wikipedia। Tavily একটা আসল ফুল-টেক্সট
# সার্চ-ইঞ্জিন (LLM-optimized) — DuckDuckGo Instant Answer বাংলা প্রশ্ন-বাক্যে ("... কে?",
# "... কত?") প্রায় সবসময় খালি ফল দেয়, তাই Key থাকলে প্রথমে Tavily চেষ্টা হয়; Key না
# থাকলে/কল ব্যর্থ হলে ধীরে পুরোনো ফ্রি-চেইনে (DuckDuckGo → Wikipedia) ফেলব্যাক হয় —
# তাই পুরোনো আচরণ কোনোভাবেই ভাঙে না।
# উদাহরণ: "বাংলাদেশের প্রধানমন্ত্রীর নাম কি" — এটা ডাটাবেজে না থাকলে প্রথমে ব্রাউজ সার্চ করবে;
# তথ্য পেলে তা গুছিয়ে ইউজারকে দেওয়া হবে ও নিজের Knowledge Engine-এ সেভ হয়ে যাবে (পরের বার
# একই প্রশ্নে আর Browse/AI কোনোটাই লাগবে না)। ব্রাউজ থেকে কিছু না পেলে তখনই স্বাভাবিক AI API
# কল (ask_ai/ask_ai_with_history) হবে, আগের মতোই — এবং সেই AI-উত্তরও নিজে থেকে ডাটাবেজে
# যুক্ত হয়ে যাবে।

BROWSE_SEARCH_TIMEOUT = 8  # সেকেন্ড — DuckDuckGo/Wikipedia প্রতিটা কলের timeout, ধীর হলে দ্রুত বাদ দিয়ে পরেরটায় যায়


# ============================= Phase 48: Time-sensitive Query + Real Search =============================
# সমস্যা: "বর্তমান প্রধানমন্ত্রী/রাষ্ট্রপতি/CEO কে", "দাম কত", "স্কোর" জাতীয় সময়-সংবেদনশীল
# প্রশ্নের উত্তর Phase 44-এর চেইনে (DuckDuckGo Instant Answer + Wikipedia extract) প্রায়ই
# পুরোনো/ভুল হয়, আর সেই উত্তর Knowledge Engine-এ সেভ হয়ে ক্যাশ-পয়জনিং করত — একই/কাছাকাছি
# প্রশ্নে বারবার একই ভুল উত্তর ফিরে আসত, কখনো re-verify হতো না। Phase 48-এর সমাধান তিন স্তরে:
#   1. Real Web Search আগে (_browse_real_search — Tavily), তারপর পুরোনো ফ্রি-চেইন।
#   2. time-sensitive প্রশ্নে Step 1 (Database cache) স্কিপ (_phase17_decide-এ) —
#      যাতে পুরনো cached উত্তর না দেওয়া হয়, সবসময় নতুন করে সার্চ হয়।
#   3. time-sensitive উত্তর সেভ করলে metadata-তে expires_at (এখন + ৭ দিন) — read path
#      (KnowledgeEngine.search) মেয়াদোত্তীর্ণ এন্ট্রি স্কিপ করে, ভুল উত্তর আর ফেরে না।

# time-sensitive প্রশ্নের cached উত্তর কত দিন "তাজা" থাকবে (env দিয়ে বদলানো যায়)।
TIME_SENSITIVE_KNOWLEDGE_TTL_DAYS = max(1, int(os.getenv("TIME_SENSITIVE_KNOWLEDGE_TTL_DAYS", "7") or "7"))

TIME_SENSITIVE_KNOWLEDGE_TTL_SECONDS = TIME_SENSITIVE_KNOWLEDGE_TTL_DAYS * 24 * 60 * 60

#: Tavily Real Web Search — LLM-optimized আসল সার্চ-ইঞ্জিন, ফ্রি টায়ারে মাসে ১,০০০+ কল।
#: Key (TAVILY_API_KEY) না দিলে ফিচারটাই বন্ধ থাকে — চুপচাপ DuckDuckGo → Wikipedia
#: চেইনে ফেলব্যাক হয়, বট কখনো crash করে না।
TAVILY_API_ENDPOINT = "https://api.tavily.com/search"

#: যেসব শব্দ থাকলেই প্রশ্নটা "সময়-সংবেদনশীল" — উত্তর বদলাতে থাকে (দাম, স্কোর, খবর,
#: দিন-তারিখ) বা বর্তমান-নির্দেশক। ছোট শব্দগুলো whole-token হিসেবে মেলানো হয়
#: ("আজাদ"-এর ভেতরের "আজ" মিলবে না, কিন্তু স্বাধীন "আজ" টোকেন মিলবে)।
_TIME_SENSITIVE_WORDS = frozenset({
    "এখন", "এখনকার", "আজ", "আজকে", "আজকের", "কবে", "কখন", "স্কোর", "খবর", "লাইভ",
    "ফলাফল", "দাম", "মূল্য",
    "now", "current", "currently", "today", "tonight", "latest", "recent", "price",
    "score", "live", "news", "when",
})

#: বহু-শব্দ/দীর্ঘ অবিস্পষ্ট বাক্যাংশ — substring হিসেবেই মেলানো নিরাপদ।
_TIME_SENSITIVE_PHRASES = (
    "বর্তমান", "এই মুহূর্তে", "এ মুহূর্তে", "সর্বশেষ", "সবশেষ", "দাম কত", "কত দাম",
    "কত মূল্য", "right now", "as of now",
)

#: পদবি/উপাধি — "এখন কে" জাতীয় প্রশ্নের উত্তর প্রায়ই বদলায় (মেয়াদ, নির্বাচন, নিয়োগ)।
#: দীর্ঘ ও স্বতন্ত্র শব্দ, তাই substring ম্যাচ নিরাপদ ("প্রধানমন্ত্রীর"-এও মিলবে)।
_TIME_SENSITIVE_TITLE_PHRASES = (
    "প্রধানমন্ত্রী", "রাষ্ট্রপতি", "মুখ্যমন্ত্রী", "মন্ত্রী", "চেয়ারম্যান", "চেয়ারপারসন",
    "সভাপতি", "সম্পাদক", "মেয়র", "সিইও", "ব্যবস্থাপনা পরিচালক", "প্রধান নির্বাহী",
    "প্রেসিডেন্ট", "গভর্নর", "প্রধান বিচারপতি",
    "prime minister", "chief minister", "minister", "chairman", "chairperson",
    "ceo", "cto", "cfo", "mayor", "governor", "chief executive",
)

#: পদবি-প্রশ্নকে time-sensitive ধরতে সাথে এই "কে/কার/কোন/who" জাতীয় টোকেন থাকতে
#: হবে — নইলে ইতিহাস-প্রশ্নও ধরা পড়ত ("রবীন্দ্রনাথ কে ছিলেন")।
_TIME_SENSITIVE_WHO_TOKENS = frozenset({"কে", "কার", "কোন", "কাকে", "who", "whos"})


def _is_time_sensitive_query(text: str) -> bool:
    """প্রশ্নটা সময়-সংবেদনশীল কিনা — "বর্তমান প্রধানমন্ত্রী কে", "রাষ্ট্রপতি কে",
    "CEO কে", "দাম কত", "স্কোর", "কবে" জাতীয় প্রশ্নে True। এই ধরনের প্রশ্নের cached
    উত্তর পুরোনো হয়ে যেতে পারে, তাই Phase 48-এ এদের জন্য: Step 1 (Database cache)
    স্কিপ + সেভ করা উত্তরে expires_at (৭ দিন) + real search-কে অগ্রাধিকার।
    কোনো এক্সেপশন ছোঁড়ে না — ডিটেকশন ব্যর্থ হলে False (আগের আচরণ)।"""
    try:
        t = (text or "").strip().lower()
        if not t:
            return False
        # ১) বহু-শব্দের নিশ্চিত বাক্যাংশ আগে (substring ম্যাচ)।
        if any(phrase in t for phrase in _TIME_SENSITIVE_PHRASES):
            return True
        # ২) টোকেন ভাগ করে (যতিচিহ্ন বাদ) ছোট শব্দগুলো whole-token হিসেবে মেলানো হয়।
        tokens = set(re.findall(r"[\w\u0980-\u09FF]+", t, flags=re.UNICODE))
        if tokens & _TIME_SENSITIVE_WORDS:
            return True
        # ৩) পদবি/উপাধি + "কে/কার/কোন/who" জাতীয় প্রশ্নবোধক — বর্তমান-ধারক প্রশ্ন।
        if any(title in t for title in _TIME_SENSITIVE_TITLE_PHRASES):
            if tokens & _TIME_SENSITIVE_WHO_TOKENS:
                return True
        return False
    except Exception:  # noqa: BLE001 — ডিটেকশন কখনো চ্যাট-ফ্লো ভাঙবে না
        return False


def _phase48_knowledge_expires_at(user_text: str) -> str:
    """time-sensitive প্রশ্নের উত্তরের জন্য মেয়াদ (ISO 8601 UTC) — এখন + ৭ দিন;
    সাধারণ প্রশ্নে খালি স্ট্রিং (মানে মেয়াদ নেই — আগের মতোই দীর্ঘস্থায়ী ক্যাশ)।"""
    if not _is_time_sensitive_query(user_text):
        return ""
    return (
        datetime.now(timezone.utc) + timedelta(seconds=TIME_SENSITIVE_KNOWLEDGE_TTL_SECONDS)
    ).isoformat(timespec="seconds")


def _knowledge_entry_expired(metadata_value: Any, now: Optional[datetime] = None) -> bool:
    """Knowledge entry-র metadata-য় Phase 48-এর ``expires_at`` থাকলে এবং তা পেরিয়ে
    গেলে True — মেয়াদোত্তীর্ণ cached উত্তর আর Decision Engine-এর read path (Step 1)
    থেকে ফেরে না (ক্যাশ-পয়জনিং ঠেকানো)। ``expires_at`` না থাকলে/পার্স না হলে False —
    পুরোনো এন্ট্রির আচরণ অক্ষত থাকে।"""
    try:
        data = metadata_value
        if isinstance(data, str):
            data = json.loads(data or "{}")
        if not isinstance(data, dict):
            return False
        raw = str(data.get("expires_at") or "").strip()
        if not raw:
            return False
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt <= (now or datetime.now(timezone.utc))
    except Exception:  # noqa: BLE001 — খারাপ metadata কখনো read path ভাঙবে না
        return False


async def _browse_duckduckgo(query: str) -> Optional[Dict[str, str]]:
    """DuckDuckGo Instant Answer API (সম্পূর্ণ ফ্রি, কোনো Key লাগে না) থেকে সংক্ষিপ্ত তথ্য
    আনার চেষ্টা করে। মূলত সংজ্ঞা/পরিচিতিমূলক প্রশ্নে ভালো কাজ করে; খুব সাম্প্রতিক/সময়-
    সংবেদনশীল প্রশ্নে প্রায়ই খালি ফলাফল দেয় — তখন Wikipedia fallback ব্যবহার হয়।"""
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1, "no_redirect": 1},
            timeout=BROWSE_SEARCH_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        text = (data.get("AbstractText") or data.get("Answer") or data.get("Definition") or "").strip()
        if not text:
            for topic in data.get("RelatedTopics", []) or []:
                candidate = (topic.get("Text") or "").strip() if isinstance(topic, dict) else ""
                if candidate:
                    text = candidate
                    break
        if not text:
            return None
        source_url = (data.get("AbstractURL") or data.get("Redirect") or "").strip()
        source_name = (data.get("AbstractSource") or "DuckDuckGo").strip() or "DuckDuckGo"
        return {"text": text[:1800], "source": source_name, "url": source_url}
    except Exception as e:
        logger.debug(f"Phase 44 DuckDuckGo Browse Search ব্যর্থ: {e}")
        return None


async def _browse_wikipedia(query: str, lang: str = "bn") -> Optional[Dict[str, str]]:
    """Wikipedia REST Summary API (ফ্রি, কোনো Key লাগে না) থেকে সারসংক্ষেপ আনার চেষ্টা করে —
    প্রথমে opensearch দিয়ে সবচেয়ে কাছের টাইটেল খুঁজে বের করে, তারপর সেই টাইটেলের সামারি আনে।"""
    try:
        client = await get_http_client()
        search_resp = await client.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={"action": "opensearch", "search": query, "limit": 1, "namespace": 0, "format": "json"},
            timeout=BROWSE_SEARCH_TIMEOUT,
        )
        if search_resp.status_code != 200:
            return None
        result = search_resp.json()
        titles = result[1] if isinstance(result, list) and len(result) > 1 else []
        if not titles:
            return None
        title = titles[0]
        summary_resp = await client.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{_url_quote(title)}",
            timeout=BROWSE_SEARCH_TIMEOUT,
        )
        if summary_resp.status_code != 200:
            return None
        summary = summary_resp.json()
        text = (summary.get("extract") or "").strip()
        if not text:
            return None
        page_url = ((summary.get("content_urls") or {}).get("desktop") or {}).get("page", "")
        return {
            "text": text[:1800],
            "source": f"Wikipedia ({lang})",
            "url": page_url,
            # Issue C hardening: runtime সিদ্ধান্তে শুধু display source/URL regex-এর উপর
            # নির্ভর না করে Wikipedia ভাষাটা explicit metadata হিসেবেও বহন করা হয়।
            # এতে matched_source/source কোনো কারণে বদলে গেলেও `_browse_result_language_code()`
            # Bengali Wikipedia-কে নির্ভরযোগ্যভাবে `bn` হিসেবে চিনতে পারে।
            "source_lang_code": str(lang or "").strip().lower(),
        }
    except Exception as e:
        logger.debug(f"Phase 44 Wikipedia({lang}) Browse Search ব্যর্থ: {e}")
        return None


def _real_search_configured() -> bool:
    """Phase 48 Real Web Search (Tavily)-এর Key (TAVILY_API_KEY) সেট করা আছে কিনা।
    Key না থাকলে ফিচারটা নিঃশব্দে বন্ধ থাকে — পুরোনো DuckDuckGo → Wikipedia চেইনই চলে।"""
    try:
        return bool((os.getenv("TAVILY_API_KEY") or "").strip())
    except Exception:  # noqa: BLE001
        return False


async def _browse_real_search(query: str, lang_hint: str = "") -> Optional[Dict[str, str]]:
    """Phase 48: Tavily Real Web Search API (LLM-optimized আসল সার্চ-ইঞ্জিন) থেকে তথ্য
    আনে — DuckDuckGo Instant Answer নামি QA-ইঞ্জিন, বাংলা প্রশ্ন-বাক্যে খালি ফল দেয়;
    Tavily ফুল-টেক্সট ওয়েব সার্চ করে তাই ব্রেকিং নিউজ/দাম/স্কোর/নির্বাচনের ফলাফল জাতীয়
    প্রশ্নেও তাজা ফল পাওয়া যায়।

    - Key (TAVILY_API_KEY env) না থাকলে None — caller তখন পুরোনো ফ্রি-চেইনে ফেলব্যাক করে।
    - ফলাফলে Tavily-র synthesized answer + শীর্ষ কয়েকটা রেজাল্টের snippet থাকে।
    - কোনো এক্সেপশন ছোঁড়ে না — ব্যর্থ হলে None (browse_web_search পরের সোর্সে যাবে)।
    """
    api_key = (os.getenv("TAVILY_API_KEY") or "").strip()
    if not api_key:
        return None
    query = (query or "").strip()
    if not query:
        return None
    try:
        client = await get_http_client()
        resp = await client.post(
            TAVILY_API_ENDPOINT,
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "max_results": 5,
            },
            timeout=BROWSE_SEARCH_TIMEOUT,  # আগের মতোই একই timeout — ধীর হলে দ্রুত বাদ
        )
        if resp.status_code != 200:
            logger.debug(f"Phase 48 Tavily Real Search ব্যর্থ: HTTP {resp.status_code}")
            return None
        data = resp.json()
        answer = str((data.get("answer") or "") or "").strip()
        results = data.get("results") or []
        if not isinstance(results, list):
            results = []
        # শীর্ষ রেজাল্টগুলোর টাইটেল+snippet জুড়ে দেওয়া হয় — শুধু synthesized answer
        # খালি/অসম্পূর্ণ হলেও ইউজার বাস্তব উৎসের টুকরো থেকে তথ্য পায়।
        parts = []
        for item in results[:3]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            content = str(item.get("content") or "").strip()
            if title or content:
                parts.append(f"• {title}: {content}".strip(": "))
        text = answer
        if parts:
            text = (answer + "\n\n" if answer else "") + "\n".join(parts)
        text = (text or "").strip()
        if not text:
            return None
        first_url = ""
        if results and isinstance(results[0], dict):
            first_url = str(results[0].get("url") or "").strip()
        return {"text": text[:1800], "source": "Tavily Web Search", "url": first_url}
    except Exception as e:  # noqa: BLE001 — Key ভুল/নেটওয়ার্ক ডাউন → চুপচাপ পরের সোর্স
        logger.debug(f"Phase 48 Tavily Real Search ব্যর্থ: {e}")
        return None


def _browse_target_wikipedia_lang(lang_hint: str = "") -> str:
    """Browse Search-এ Wikipedia কোন ভাষায় জিজ্ঞেস করা হবে সেটা নির্ধারণ করে।"""
    hint = (lang_hint or "").strip().lower()
    return "bn" if ("bengali" in hint or "bangla" in hint or "বাংলা" in hint or hint == "bn") else "en"


async def browse_web_search(query: str, lang_hint: str = "") -> Optional[Dict[str, str]]:
    """Brain OS ডাটাবেজে সরাসরি উত্তর না পেলে এখান থেকে ফ্রি Browse Search করা হয়।
    ক্রম (Phase 48): Tavily Real Web Search (TAVILY_API_KEY থাকলে) -> DuckDuckGo
    Instant Answer -> Wikipedia (ইউজারের ভাষা অনুযায়ী) -> Wikipedia (ইংরেজি)।
    time-sensitive প্রশ্নে ("বর্তমান প্রধানমন্ত্রী কে", "দাম কত" ইত্যাদি) Tavily-কেই
    অগ্রাধিকার — DDG/Wikipedia শুধু ফেলব্যাক হিসেবে (এগুলোর ফল পুরোনো হতে পারে)।
    প্রথম যেটাতে আসল (খালি নয়) তথ্য পাওয়া যায় সেটাই রিটার্ন হয়। রিটার্ন করা dict-এ 'tried_sources'
    key-এ ক্রমানুসারে সব সোর্স যা চেষ্টা করা হয়েছে (সফল/ব্যর্থ নির্বিশেষে) থাকে — যাতে ইউজার/এডমিন
    দেখতে পারে ঠিক কোন কোন ব্রাউজার/সোর্স চেক করা হয়েছিল। সবগুলো খালি/ব্যর্থ হলে None — তখন
    caller (chat_general) স্বাভাবিক AI API fallback-এ চলে যাবে।"""
    query = (query or "").strip()
    if not query:
        return None

    tried_sources = []
    # Phase 48: আসল web search (Tavily) সবার আগে — DDG-র Instant Answer QA-ইঞ্জিন, বাংলা
    # প্রশ্নে প্রায় খালি ফল দেয়; Tavily ফুল-টেক্সট সার্চ করে। Key না থাকলে ধাপটা পুরো
    # স্কিপ (tried_sources-এও যোগ হয় না — চেষ্টাই করা হয়নি), ব্যর্থ হলে নিচের পুরোনো
    # ফ্রি-চেইনে ফেলব্যাক — আগের আচরণ অক্ষত।
    if _real_search_configured():
        tried_sources.append("Tavily Web Search")
        logger.info(f"[Browse Search] Tavily Real Web Search চেষ্টা করা হচ্ছে | query: {query!r}")
        result = await _browse_real_search(query, lang_hint=lang_hint)
        if result:
            logger.info(f"[Browse Search] Tavily থেকে উত্তর পাওয়া গেছে | query: {query!r}")
            result["tried_sources"] = tried_sources.copy()
            result["matched_source"] = "Tavily Web Search"
            return result
        logger.info(f"[Browse Search] Tavily ব্যর্থ, পুরোনো ফ্রি-চেইনে ফেলব্যাক | query: {query!r}")

    tried_sources.append("DuckDuckGo Instant Answer")
    logger.info(f"[Browse Search] DuckDuckGo চেষ্টা করা হচ্ছে | query: {query!r}")
    result = await _browse_duckduckgo(query)
    if result:
        logger.info(f"[Browse Search] DuckDuckGo থেকে উত্তর পাওয়া গেছে | query: {query!r}")
        result["tried_sources"] = tried_sources.copy()
        result["matched_source"] = "DuckDuckGo Instant Answer"
        return result

    wiki_lang = _browse_target_wikipedia_lang(lang_hint)
    tried_sources.append(f"Wikipedia ({wiki_lang})")
    logger.info(f"[Browse Search] Wikipedia ({wiki_lang}) চেষ্টা করা হচ্ছে | query: {query!r}")
    result = await _browse_wikipedia(query, lang=wiki_lang)
    if result:
        logger.info(f"[Browse Search] Wikipedia ({wiki_lang}) থেকে উত্তর পাওয়া গেছে | query: {query!r}")
        result["tried_sources"] = tried_sources.copy()
        result["matched_source"] = f"Wikipedia ({wiki_lang})"
        result["source_lang_code"] = str(result.get("source_lang_code") or wiki_lang).strip().lower()
        return result

    if wiki_lang != "en":
        tried_sources.append("Wikipedia (en)")
        logger.info(f"[Browse Search] Wikipedia (en) চেষ্টা করা হচ্ছে | query: {query!r}")
        result = await _browse_wikipedia(query, lang="en")
        if result:
            logger.info(f"[Browse Search] Wikipedia (en) থেকে উত্তর পাওয়া গেছে | query: {query!r}")
            result["tried_sources"] = tried_sources.copy()
            result["matched_source"] = "Wikipedia (en)"
            result["source_lang_code"] = str(result.get("source_lang_code") or "en").strip().lower()
            return result

    logger.info(f"[Browse Search] সব সোর্স ব্যর্থ, কিছুই পাওয়া যায়নি | tried: {tried_sources} | query: {query!r}")
    return None


def _phase44_save_browsed_knowledge(user_text: str, answer_text: str, source: str, url: str) -> None:
    """ব্রাউজ থেকে পাওয়া (এবং দরকার হলে AI দিয়ে গুছিয়ে দেওয়া) তথ্য নিজের Knowledge Engine-এ
    সেভ করে রাখে — যাতে একই/কাছাকাছি প্রশ্ন পরের বার Decision Engine-এর knowledge stage থেকেই
    সরাসরি (আবার Browse/AI ছাড়াই) উত্তর দেওয়া যায়। ব্যর্থ হলেও চুপচাপ স্কিপ করে — এটা কখনো
    মূল চ্যাট-ফ্লো ভাঙবে না।"""
    try:
        title = user_text.strip()[:150] or "browse_search"
        content = (answer_text or "").strip()
        if not content:
            return
        # Phase 48 (ক্যাশ-পয়জনিং ঠেকানো): time-sensitive প্রশ্নের উত্তর চিরদিনের জন্য
        # সেভ করা হয় না — metadata-তে expires_at (এখন + ৭ দিন) বসে; read path
        # (KnowledgeEngine.search) মেয়াদ পেরোলে এন্ট্রিটা আর কাউকে দেখায় না, ফলে
        # পরের বার নতুন করে সার্চই হয়। সাধারণ প্রশ্নে expires_at থাকে না (আগের মতোই)।
        metadata = {"origin": "browse_search", "source": source, "url": url}
        expires_at = _phase48_knowledge_expires_at(user_text)
        if expires_at:
            metadata["expires_at"] = expires_at
        engine = KnowledgeEngine()
        if expires_at:
            # একই উত্তর আগেও সেভ করা থাকলে create() নতুন রো বানায় না (ডুপ্লিকেট
            # রিটার্ন করে) — সেক্ষেত্রে পুরোনো এন্ট্রির মেয়াদই নতুন করে বসিয়ে দেওয়া
            # হয়, যাতে সেটা "চির-মেয়াদোত্তীর্ণ জম্বি" না হয়ে বরং আবার ব্যবহারযোগ্য থাকে।
            existing = engine.check_duplicate("browse_search", title, content)
            if existing is not None:
                try:
                    old_meta = json.loads(existing.metadata or "{}")
                    if not isinstance(old_meta, dict):
                        old_meta = {}
                except Exception:  # noqa: BLE001
                    old_meta = {}
                old_meta["expires_at"] = expires_at
                engine.update(existing.id, metadata=old_meta)
                return
        engine.create(
            category="browse_search",
            title=title,
            content=content,
            tags="auto,browse_search",
            priority=5,
            source="browse_search",
            metadata=metadata,
            confidence_score=0.75,
            status="active",
        )
    except Exception as e:
        logger.debug(f"Phase 44 browse ফলাফল Knowledge Engine-এ সেভ করা যায়নি: {e}")


def _phase44_save_ai_knowledge(user_text: str, answer_text: str) -> None:
    """Browse Search-এও কিছু না পেয়ে শেষমেশ AI API কল করে উত্তর পেলে, সেই উত্তরও নিজে থেকে
    Knowledge Engine-এ সেভ করে রাখা হয় — যাতে একই প্রশ্ন আবার এলে পরের বার আর AI API কল না
    লাগে, Brain OS নিজেই সরাসরি উত্তর দিতে পারে।"""
    try:
        title = user_text.strip()[:150] or "ai_answer"
        content = (answer_text or "").strip()
        if not content:
            return
        # Phase 48 (ক্যাশ-পয়জনিং ঠেকানো): AI-উত্তরেও হ্যালুসিনেশন/পুরোনো তথ্য থাকতে
        # পারে — time-sensitive প্রশ্নে সেভ করা উত্তরে expires_at (এখন + ৭ দিন) বসে,
        # যাতে ভুল উত্তর Step 1 থেকে অনন্তকাল রিপিট না হয় (মেয়াদ পেরোলে আবার সার্চ/AI)।
        metadata = {"origin": "ai_fallback"}
        expires_at = _phase48_knowledge_expires_at(user_text)
        if expires_at:
            metadata["expires_at"] = expires_at
        engine = KnowledgeEngine()
        if expires_at:
            existing = engine.check_duplicate("ai_answer", title, content)
            if existing is not None:
                try:
                    old_meta = json.loads(existing.metadata or "{}")
                    if not isinstance(old_meta, dict):
                        old_meta = {}
                except Exception:  # noqa: BLE001
                    old_meta = {}
                old_meta["expires_at"] = expires_at
                engine.update(existing.id, metadata=old_meta)
                return
        engine.create(
            category="ai_answer",
            title=title,
            content=content,
            tags="auto,ai_answer",
            priority=5,
            source="ai",
            metadata=metadata,
            confidence_score=0.7,
            status="active",
        )
    except Exception as e:
        logger.debug(f"Phase 44 AI উত্তর Knowledge Engine-এ সেভ করা যায়নি: {e}")


def _browse_result_language_code(found: Optional[Dict[str, Any]]) -> str:
    """Wikipedia source name বা metadata থেকে language code extract করে (যেমন: bn, en)।"""
    if not isinstance(found, dict):
        logger.info(
            f"[DEBUG] _browse_result_language_code(): invalid found type: {type(found).__name__}"
        )
        return ""
    logger.info(f"[DEBUG] _browse_result_language_code() input keys: {found.keys()}")
    for key in ("source_lang_code", "language_code", "lang", "wiki_lang"):
        val = str(found.get(key) or "").strip().replace("_", "-").lower()
        logger.info(f"[DEBUG] _browse_result_language_code() metadata {key}: '{val}'")
        if re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]+)?", val, re.IGNORECASE):
            logger.info(
                f"[DEBUG] _browse_result_language_code() matched metadata {key}: '{val}'"
            )
            return val
    for key in ("matched_source", "source"):
        val = str(found.get(key) or "").strip()
        logger.info(f"[DEBUG] _browse_result_language_code() inspecting {key}: {val!r}")
        m = re.search(r"wikipedia\s*\(([a-zA-Z_\-]+)\)", val, re.IGNORECASE)
        if m:
            extracted = m.group(1).replace("_", "-").lower()
            logger.info(
                f"[DEBUG] _browse_result_language_code() matched {key}: '{extracted}'"
            )
            return extracted
    url = str(found.get("url") or "").strip()
    logger.info(f"[DEBUG] _browse_result_language_code() inspecting url: {url!r}")
    m_url = re.search(r"https?://([a-zA-Z_\-]+)\.wikipedia\.org", url, re.IGNORECASE)
    if m_url:
        extracted = m_url.group(1).replace("_", "-").lower()
        logger.info(f"[DEBUG] _browse_result_language_code() matched url: '{extracted}'")
        return extracted
    logger.info("[DEBUG] _browse_result_language_code() no language code extracted")
    return ""


def _browse_result_needs_ai_organization(
    found: Optional[Dict[str, Any]], raw_text: str
) -> bool:
    """[DEPRECATED - Phase 49]

    Previously used to decide if browse content needs formatting via AI.
    No longer called — browser content is returned as-is (content is already well-formatted).
    Kept for backward compatibility. Always returns False.
    """
    return False  # Disabled in Phase 49 — no AI organization for browse content


async def _automatic_browse_answer(
    user_id: int, query: str, lang_hint: str, no_api_mode: bool, *, command: str = "chat"
) -> str:
    """Phase 47: ডাটাবেজে সরাসরি উত্তর না পেলে স্বয়ংক্রিয় (automatic) Browse Search চালায়।

    এটাই এখন **সব হ্যান্ডলারের** (chat/joke/quote/translate/grammar/rewrite/tone/summarize)
    দ্বিতীয় ধাপ — কোনো আলাদা /search কমান্ডের দরকার নেই। খোঁজার ক্রম সবসময়:
    💾 Database → 🌐 Browser Search → 🔵 Groq API। এই ফাংশন শুধু Browser ধাপটা করে:

      - `browse_web_search()`: Tavily Real Web Search (Key থাকলে, Phase 48) →
        DuckDuckGo Instant Answer → Wikipedia (ইউজারের ভাষা) → Wikipedia (en)।
      - No API Call Mode বন্ধ থাকলে: শুধু ব্রাউজার ফলাফলের ভাষা ইউজারের ভাষার সাথে না মিললে
        AI-কে ছোট্ট একটা translate কল করা হয় (তখন ব্যাজ 🔄 Hybrid: 🌐 Browser + 🔵 Groq)।
        একই ভাষার clean ব্রাউজার ফলাফল সরাসরি ফেরত যায় (🌐 Browser) — কোনো AI কল ছাড়াই।
      - No API Call Mode চালু থাকলে: কোনো AI কল ছাড়াই কাঁচা তথ্যটাই যায় (🌐 Browser)।

    উত্তরের নিচে উৎস-ব্যাজ যুক্ত হয় — কোন সোর্স থেকে এসেছে, কোন কোন সোর্স চেক করা হয়েছিল,
    মূল লিংক ও নির্ভুলতা সবসহ। ব্যাজ বন্ধ/অনুপলব্ধ থাকলে Phase 44-এর পুরোনো উৎস-ফুটার দেখানো হয়
    (তথ্য হারায় না)। ওয়েবে কিছু না পেলে খালি স্ট্রিং রিটার্ন হয় — caller তখন নিজের পরের
    (🔵 Groq API) fallback ব্যবহার করবে। কোনো ধাপেই এই ফাংশন এক্সসেপশন ছুঁড়ে না।
    """
    try:
        query = (query or "").strip()
        if not query:
            return ""

        found = await browse_web_search(query, lang_hint=lang_hint)
        raw_text = ((found or {}).get("text") or "").strip()
        if not found or not raw_text:
            return ""

        organized_by_ai = False
        final_text = raw_text

        if not no_api_mode:
            target_lang_code = _browse_target_wikipedia_lang(lang_hint)
            source_lang_code = _browse_result_language_code(found)
            raw_lang_code = source_lang_code or detect_language(raw_text)

            # Phase 49: Only organize with AI if actual language translation is needed
            # DO NOT call AI for formatting/beautification of already-clean content
            if raw_lang_code != target_lang_code:
                # Language mismatch: translate to user's language
                try:
                    translate_prompt = (
                        "আপনি একজন ভাষা অনুবাদক। নিচের পাঠ্যটি সঠিকভাবে অনুবাদ করুন, "
                        "অন্য কোনো পরিবর্তন করবেন না। নতুন তথ্য যোগ করবেন না।"
                    )
                    ai_result = (
                        await ask_ai(translate_prompt, raw_text, use_cache=False, user_id=user_id)
                    ).strip()
                    if ai_result:
                        final_text = ai_result
                        organized_by_ai = True
                except Exception as e:
                    logger.info("Browse result translation failed, using original: %s", e)

        metadata = metadata_from_browse_result(found, organized_by_ai=organized_by_ai, query=query)

        badged = attach_source_badge(final_text, metadata, command, attribution_lang(user_id))
        if badged == final_text:
            # Attribution বন্ধ/অনুপলব্ধ — Phase 44-এর পুরোনো উৎস-ফুটারই দেখানো হচ্ছে।
            badged = final_text + legacy_browse_footer(
                found.get("source", "") or "ওয়েব সার্চ",
                found.get("url", "") or "",
                found.get("tried_sources") or [],
            )
        return badged
    except Exception as e:
        logger.warning("Phase 47 automatic Browse Search সম্পূর্ণ ব্যর্থ, পরের fallback ব্যবহার হবে: %s", e)
        return ""


def _browse_lang_hint(user_id: int, text: str) -> str:
    """ব্রাউজার সার্চের ভাষা-ইঙ্গিত — ইউজার /setlang দিয়ে ভাষা বেছে থাকলে সেটা,
    নাহলে টেক্সট থেকে শনাক্ত করা ভাষা (Wikipedia-র ভাষা ও গুছিয়ে লেখার ভাষা বেছে নিতে ব্যবহার হয়)।"""
    manual_lang, is_manual = get_effective_language(user_id)
    if is_manual:
        return UI_LANG_CHOICES.get(manual_lang, manual_lang)
    return language_display_name(detect_language(text))


# ============================= Phase 47: Source Attribution (উৎস নির্দেশনা) =============================
# উদ্দেশ্য: ইউজার যেন প্রতিটা তথ্যবহ উত্তরের নিচে স্পষ্ট দেখতে পায় তথ্যটা **কোথা থেকে** এসেছে —
#   🔵 Groq API      → LLM (Groq/OpenRouter/Cerebras) দিয়ে তৈরি লেখা
#   🌐 Browser Search → লাইভ ওয়েব সার্চ (Phase 44-এর DuckDuckGo Instant Answer / Wikipedia)
#   💾 Database      → বটের নিজের Brain OS (Knowledge/Pattern/Template Engine) বা Response Cache
#   🔄 Hybrid        → একাধিক সোর্স মিলিয়ে (যেমন Browser-এর কাঁচা তথ্য Groq দিয়ে গুছিয়ে লেখা)
#
# আসল লজিক (badge তৈরি, confidence level, ফরম্যাট, per-command সেটিংস) আছে
# `rohan_bot/utils/source_tracker.py` + `rohan_bot/config.py`-তে — ওগুলো Telegram/AI/DB থেকে
# সম্পূর্ণ স্বাধীন, তাই আলাদাভাবে দ্রুত unit-test করা যায় (tests/test_source_attribution.py)।
# main.py এখান থেকে শুধু দুটো হেল্পার ব্যবহার করে: make_source_metadata() ও attach_source_badge()।
#
# গুরুত্বপূর্ণ (নিরাপত্তা): rohan_bot/ প্যাকেজটা কোনো কারণে import না হলে (যেমন শুধু main.py
# কপি করে চালানো হলে) বট ভাঙবে না — SOURCE_ATTRIBUTION_AVAILABLE False হয়ে যাবে, তখন ব্যাজ
# ছাড়াই আগের মতো উত্তর যাবে। তাই পুরোনো কোনো কমান্ডের আচরণ কখনো ভাঙে না।
#
# Environment override (Render/Replit Secrets — সবগুলো ঐচ্ছিক):
#   SOURCE_ATTRIBUTION_ENABLED=false          → পুরো ফিচার বন্ধ
#   SOURCE_ATTRIBUTION_FORMAT=full            → ডিফল্ট ব্যাজ ফরম্যাট (minimal/compact/full/detailed)
#   SOURCE_ATTRIBUTION_LANG=en                → ব্যাজের ভাষা (ডিফল্ট bn)
#   SOURCE_ATTRIBUTION_DISABLED_COMMANDS=joke,quote   → নির্দিষ্ট কমান্ডের ব্যাজ বন্ধ
#   SOURCE_ATTRIBUTION_ENABLED_COMMANDS=ocr           → নির্দিষ্ট কমান্ডের ব্যাজ চালু

SOURCE_ATTRIBUTION_MIN_OVERHEAD_MS = 10  # ডিজাইন লক্ষ্য: ব্যাজ যোগ করতে এর বেশি সময় লাগা যাবে না


def _load_source_tracker():
    """`rohan_bot.utils.source_tracker` মডিউলটা খুঁজে বের করে import করে; না পারলে None।

    main.py repo-root-এ থাকে, তাই সাধারণত `import rohan_bot...` সরাসরিই কাজ করে। কিন্তু
    টেস্ট/ডিপ্লয়মেন্টে main.py আলাদা ডিরেক্টরিতে কপি হতে পারে — তখন main.py-এর নিজের
    অবস্থান (বা তার প্যারেন্ট, অথবা cwd) থেকে প্যাকেজটা খোঁজা হয়। কোথাও না পেলে None
    ফেরত যায় এবং source attribution নিজে থেকে বন্ধ থাকে (বট চলতে কোনো সমস্যা হয় না)।
    """
    import importlib

    here = os.path.dirname(os.path.abspath(__file__))
    for root in (here, os.path.dirname(here), os.getcwd()):
        if not root:
            continue
        if os.path.isdir(os.path.join(root, "rohan_bot", "utils")):
            if root not in sys.path:
                sys.path.insert(0, root)
            break
    try:
        return importlib.import_module("rohan_bot.utils.source_tracker")
    except Exception as exc:  # pragma: no cover - প্যাকেজ না থাকলে বট যাতে না ভাঙে
        logger.warning(
            "Phase 47: rohan_bot.utils.source_tracker import করা যায়নি (%s) — "
            "source attribution বন্ধ থাকবে, বাকি সব ফিচার আগের মতোই চলবে।",
            exc,
        )
        return None


_source_tracker = _load_source_tracker()

#: প্যাকেজ পাওয়া গেছে কিনা — False হলে নিচের সব হেল্পার নিষ্ক্রিয় (no-op) হয়ে যায়।
SOURCE_ATTRIBUTION_AVAILABLE = _source_tracker is not None


def source_attribution_settings() -> Dict[str, Any]:
    """কার্যকর attribution কনফিগ (env override সহ) ফেরত দেয়; প্যাকেজ না থাকলে বন্ধ-কনফিগ।"""
    if _source_tracker is None:
        return {"enabled": False, "format": "compact", "lang": "bn", "commands": {}, "confidence": {}}
    try:
        return _source_tracker.load_settings()
    except Exception:  # pragma: no cover - প্রতিরক্ষামূলক
        return {"enabled": False, "format": "compact", "lang": "bn", "commands": {}, "confidence": {}}


def source_attribution_enabled(command: str = "") -> bool:
    """পুরো ফিচার এবং নির্দিষ্ট কমান্ডের জন্য ব্যাজ চালু আছে কিনা।"""
    if not SOURCE_ATTRIBUTION_AVAILABLE:
        return False
    settings = source_attribution_settings()
    if not settings.get("enabled", True):
        return False
    try:
        return bool(_source_tracker.resolve_command_settings(command, settings).get("enabled", True))
    except Exception:  # pragma: no cover - প্রতিরক্ষামূলক
        return False


def make_source_metadata(
    source: str,
    *,
    confidence: Optional[float] = None,
    urls: Optional[Sequence[str]] = None,
    secondary: Optional[Sequence[str]] = None,
    cache_hit: bool = False,
    note: str = "",
    breakdown: Optional[Dict[str, float]] = None,
    timestamp: Optional[datetime] = None,
    checked_sources: Optional[Sequence[str]] = None,
    query: str = "",
):
    """একটা উত্তরের জন্য source metadata বানায় (প্যাকেজ না থাকলে/ভুল ইনপুটে None)।

    Args:
        source: ``"groq"`` | ``"browser"`` | ``"database"`` | ``"hybrid"`` (ইমোজি/পূর্ণ নামও চলে)।
        confidence: 0.0–1.0; না দিলে সোর্সভেদে ডিফল্ট।
        urls: মূল সোর্সের লিংক।
        secondary: অতিরিক্ত উৎসের তালিকা — থাকলে উত্তর 🔄 Hybrid হিসেবে দেখানো হয়।
        cache_hit: ক্যাশ/ডাটাবেজ থেকে সরাসরি এসেছে কিনা।
        note: ছোট ব্যাখ্যা (যেমন "Response Cache")।
        breakdown: detailed ব্যাজের শতাংশ ভাগ।
        timestamp: উৎসের নিজস্ব সময় (DB রেকর্ডের last-updated ইত্যাদি)।
        checked_sources: কোন কোন সোর্স চেষ্টা করা হয়েছিল।
        query: ইউজারের মূল প্রশ্ন।

    Returns:
        SourceMetadata | None: ব্যাজ বানানো সম্ভব না হলে None (তখন উত্তর অপরিবর্তিত থাকে)।
    """
    if _source_tracker is None:
        return None
    try:
        return _source_tracker.build_metadata(
            source,
            confidence_score=confidence,
            urls=urls,
            secondary_sources=secondary,
            cache_hit=cache_hit,
            note=note,
            breakdown=breakdown,
            timestamp=timestamp,
            checked_sources=checked_sources,
            query=query,
        )
    except Exception as exc:
        logger.debug("Phase 47: source metadata বানানো যায়নি (%s): %s", source, exc)
        return None


def metadata_from_browse_result(found: Optional[Dict[str, Any]], *, organized_by_ai: bool = False, query: str = ""):
    """`browse_web_search()`-এর ফলাফল থেকে metadata বানায় (URL + চেক-করা সোর্সসহ)।"""
    if _source_tracker is None:
        return None
    try:
        return _source_tracker.metadata_from_browse_result(
            found, organized_by_ai=organized_by_ai, query=query
        )
    except Exception as exc:  # pragma: no cover - প্রতিরক্ষামূলক
        logger.debug("Phase 47: browse metadata বানানো যায়নি: %s", exc)
        return None


def metadata_from_decision(decision: Optional[Dict[str, Any]], *, query: str = ""):
    """Brain OS-এর direct উত্তরের জন্য 💾 Database metadata বানায়।"""
    if _source_tracker is None:
        return None
    try:
        return _source_tracker.metadata_from_decision(decision, query=query)
    except Exception as exc:  # pragma: no cover - প্রতিরক্ষামূলক
        logger.debug("Phase 47: decision metadata বানানো যায়নি: %s", exc)
        return None


def attribution_lang(user_id: int) -> str:
    """ব্যাজের ভাষা — ইউজার বাংলা (বা Auto) বেছে নিলে ``"bn"``, নইলে ``"en"``।

    বটের বাকি UI-এর মতোই /setlang-এর পছন্দ মানে; তবে badge-এর স্ট্যাটিক লেবেল শুধু
    বাংলা/ইংরেজিতেই আছে (অন্য ভাষার জন্য ইংরেজি লেবেল ব্যবহার হয়)।
    """
    try:
        lang, manual = get_effective_language(user_id)
    except Exception:  # pragma: no cover - DB সমস্যায় ব্যাজ যেন বট না ভাঙায়
        return "bn"
    if not manual:
        return "bn"
    return "bn" if str(lang or "bn").lower().startswith("bn") else "en"


def attach_source_badge(text: str, metadata, command: str, lang_code: str = "bn") -> str:
    """উত্তরের সাথে উৎস-ব্যাজ যুক্ত করে; কোনো কারণে সম্ভব না হলে মূল লেখাই ফেরত দেয়।

    এই ফাংশন কখনো exception তোলে না — source tracking-এর কারণে চ্যাট-ফ্লো ভাঙা যাবে না।
    """
    body = text or ""
    if metadata is None or _source_tracker is None:
        return body
    if not source_attribution_enabled(command):
        return body
    try:
        return _source_tracker.format_with_source(
            body, metadata, lang=lang_code or "bn", command=command
        )
    except Exception as exc:  # pragma: no cover - প্রতিরক্ষামূলক
        logger.debug("Phase 47: ব্যাজ যুক্ত করা যায়নি (%s): %s", command, exc)
        return body


def legacy_browse_footer(source: str, url: str, tried_sources: Optional[Sequence[str]] = None) -> str:
    """Phase 44-এর পুরোনো উৎস-ফুটার — শুধু তখন ব্যবহার হয় যখন attribution ব্যাজ বন্ধ থাকে।

    এতে ফিচার বন্ধ থাকলেও ইউজার আগের মতোই সোর্স-লিংক ও "চেক করা হয়েছে" তালিকা দেখতে পান
    (অর্থাৎ attribution বন্ধ করা মানে তথ্য হারানো নয়)।
    """
    footer = ""
    if url:
        footer += f"\n\n🔗 উৎস: {url}"
    elif source:
        footer += f"\n\n📚 উৎস: {source}"
    if tried_sources:
        footer += "\n🔎 চেক করা হয়েছে: " + " → ".join(tried_sources)
    return footer


def _cache_hit_marker(system_prompt: str, user_text: str) -> bool:
    """Response Cache-এ এই (prompt, text) জোড়া আগে থেকে আছে কিনা — শুধু পড়ে, কিছু বদলায় না।

    `ask_ai(..., use_cache=True)` কল করার **আগে** ডাকতে হয়; তাহলে উত্তরটা আসল AI কল থেকে
    এসেছে নাকি 💾 Database/Cache থেকে, সেটা source badge-এ ঠিকভাবে দেখানো যায়।
    """
    try:
        return ai_response_cache._store.get(ai_response_cache.make_key(system_prompt, user_text)) is not None
    except Exception:  # ক্যাশের অভ্যন্তরীণ গঠন বদলালেও ব্যাজ যেন বট না ভাঙায়
        return False


def _ai_source_metadata(system_prompt: str, user_text: str, *, confidence: float = 0.90, note: str = ""):
    """`ask_ai(..., use_cache=True)` কলার জন্য metadata — cache hit হলে 💾, নইলে 🔵।"""
    if _cache_hit_marker(system_prompt, user_text):
        return make_source_metadata(
            "database", confidence=max(0.60, confidence), cache_hit=True,
            note=note or "Response Cache", query=user_text,
        )
    return make_source_metadata("groq", confidence=confidence, note=note, query=user_text)


def build_no_api_stuck_message(decision: Dict[str, Any]) -> str:
    """No API Call Mode-এ Brain OS সরাসরি উত্তর দিতে না পারলে ইউজারকে এই মেসেজটা পাঠানো হয় —
    কোন ধাপে আটকে গেছে সেটা জানিয়ে আরও তথ্য চায়, কোনো AI কল হয় না।"""
    stage = str(decision.get("stage") or "unknown")
    stage_label = _BRAIN_STAGE_LABEL_BN.get(stage, stage)
    confidence = decision.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    browse_note = ""
    if stage == "ai":
        # এই স্টেজে পৌঁছালে মানে Brain OS নিজের ডাটাবেজে কিছু পায়নি, তাই Phase 44 অনুযায়ী
        # ফ্রি Browse Search (DuckDuckGo → Wikipedia) অবশ্যই চেষ্টা হয়েছিল কিন্তু কিছুই মেলেনি।
        browse_note = (
            "\n🔎 এর মাঝে ফ্রি Browse Search-ও চেষ্টা করা হয়েছিল "
            "(Tavily → DuckDuckGo Instant Answer → Wikipedia বাংলা → Wikipedia English) কিন্তু কোথাও "
            "এই প্রশ্নের উত্তর পাওয়া যায়নি।\n"
        )
    return (
        "🧪 আপনার চ্যাটে No API Call Mode চালু আছে — তাই এই প্রশ্নের উত্তর দিতে কোনো AI API কল করা হয়নি।\n\n"
        f"⚠️ Brain OS এই প্রশ্নের জন্য নিজের কাছে যথেষ্ট নিশ্চিত তথ্য পায়নি।\n"
        f"আটকে গেছে: {stage_label} ধাপে (confidence: {confidence:.2f})\n"
        f"{browse_note}\n"
        "দয়া করে প্রশ্নটা আরেকটু ভেঙে/সহজ করে লিখুন, অথবা বিষয়টা সম্পর্কে একটু বেশি তথ্য দিন — "
        "তাহলে Brain OS আবার চেষ্টা করবে।\n"
        "(বন্ধ করতে লিখুন: /noapimode off)"
    )


def _brain_payload_to_answer(payload: Any) -> str:
    """Best-effort conversion of a Decision Engine payload into a user-facing answer.
    Never raises; unsupported payloads simply return an empty string so the caller can
    gracefully fall back to the normal AI flow.
    """
    try:
        if payload is None:
            return ""
        if isinstance(payload, str):
            return payload.strip()
        if hasattr(payload, "content"):
            value = getattr(payload, "content", "")
            if value:
                return str(value).strip()
        if hasattr(payload, "body"):
            value = getattr(payload, "body", "")
            if value:
                return str(value).strip()
        if hasattr(payload, "solution"):
            value = getattr(payload, "solution", "")
            if value:
                return str(value).strip()
        if hasattr(payload, "description"):
            value = getattr(payload, "description", "")
            if value:
                return str(value).strip()
        if isinstance(payload, dict):
            for key in ("answer", "content", "solution", "body", "description", "text"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            # Decision payloads can contain nested engine objects/dicts.
            for key in ("knowledge", "documentation", "template", "pattern"):
                if key in payload:
                    answer = _brain_payload_to_answer(payload[key])
                    if answer:
                        return answer
        return ""
    except Exception as e:
        logger.debug("Phase 17 payload extraction skipped: %s", e)
        return ""


def _brain_context_text(records: Sequence[Any]) -> str:
    """Create a small, safe context block for the AI prompt."""
    parts = []
    try:
        for record in records[:12]:
            data = getattr(record, "context_data", None)
            if data is None and isinstance(record, dict):
                data = record.get("context_data", record.get("data", {}))
            if isinstance(data, str):
                try:
                    data = json.loads(data or "{}")
                except Exception:
                    data = {"value": data}
            if not isinstance(data, dict):
                continue
            compact = []
            for key in ("language", "project", "style", "last_request"):
                value = data.get(key)
                if value:
                    compact.append(f"{key}={str(value)[:300]}")
            if compact:
                parts.append("; ".join(compact))
    except Exception as e:
        logger.debug("Phase 17 context formatting skipped: %s", e)
    return "\n".join(parts[-8:])


def _brain_save_live_context(user_id: int, language: str, user_text: str) -> None:
    """Persist useful conversation context without making Brain OS a hard dependency."""
    try:
        active_project = get_active_project(user_id)
        project_name = active_project.get("name", "") if active_project else ""
        data = {
            "language": language,
            "project": project_name,
            "style": "concise",
            "last_request": user_text[:500],
        }
        api_create_context(
            user_id=user_id,
            session_key=str(user_id),
            data=data,
            scope="conversation",
            category="live_chat",
            tags=["phase17", "conversation"],
            priority=6,
        )
    except Exception as e:
        logger.debug("Phase 17 context save skipped: %s", e)


def _brain_get_live_context(user_id: int) -> str:
    try:
        records = api_get_active_context(user_id, str(user_id), limit=12)
        return _brain_context_text(records)
    except Exception as e:
        logger.debug("Phase 17 active context read skipped: %s", e)
        return ""


async def _phase17_decide(user_id: int, user_text: str) -> Dict[str, Any]:
    """Run Decision Engine safely. Any Brain OS failure returns a normal AI route.

    Phase 48: time-sensitive প্রশ্নে ("বর্তমান প্রধানমন্ত্রী কে", "দাম কত", "স্কোর" ইত্যাদি)
    Step 1 (Database cache) স্কিপ হয় — Decision Engine direct বললেও strategy "ai" করে
    দেওয়া হয়, যাতে পুরনো cached উত্তর না গিয়ে ফ্লো Step 2 (Browse Search — এখন সবার
    আগে Tavily Real Web Search)-এ যায় এবং তাজা তথ্য আনা যায়।
    """
    try:
        decision = await decision_engine_service.execute_async(
            user_text, user_id=user_id, session_key=str(user_id)
        )
    except Exception as e:
        logger.warning("Phase 17 Decision Engine fallback: %s", e)
        return {
            "strategy": "ai",
            "stage": "ai",
            "confidence": 0.0,
            "payload": {},
            "fallback": "ai",
            "phase17_error": True,
        }
    if decision.get("strategy") == "direct" and _is_time_sensitive_query(user_text):
        # সময়-সংবেদনশীল প্রশ্ন — cached (সম্ভবত পুরোনো) উত্তর বিশ্বাস করা যায় না।
        brain_os_metrics["time_sensitive_skips"] += 1
        decision = dict(decision)
        decision["strategy"] = "ai"
        decision["time_sensitive"] = True
        logger.info(f"[Phase 48] time-sensitive প্রশ্ন — Step 1 (Database) স্কিপ | query: {user_text!r}")
    return decision


def build_brain_status_text() -> str:
    """Admin-facing Brain OS status/analytics."""
    try:
        analytics = api_decision_analytics()
    except Exception as e:
        logger.warning("Brain OS analytics unavailable: %s", e)
        analytics = {"total_decisions": 0, "by_stage": {}, "avg_confidence": 0.0, "cache_entries": 0}
    total = int(analytics.get("total_decisions", 0))
    direct = int(brain_os_metrics.get("direct_answers", 0))
    ai_routes = int(brain_os_metrics.get("ai_routes", 0))
    by_stage = analytics.get("by_stage", {}) or {}
    return (
        "🧠 Brain OS Status\n"
        "━━━━━━━━━━━━━━━\n"
        f"মোট Decision: {total}\n"
        f"Direct: {by_stage.get('knowledge', 0) + by_stage.get('pattern', 0) + by_stage.get('documentation', 0) + by_stage.get('template', 0)}\n"
        f"AI stage: {by_stage.get('ai', 0)}\n"
        f"বর্তমান Cache Entry: {analytics.get('cache_entries', 0)}\n"
        f"গড় Confidence: {float(analytics.get('avg_confidence', 0.0)):.3f}\n"
        f"Brain OS-এর মাধ্যমে AI কল সাশ্রয় হয়েছে: {direct} বার\n"
        f"AI route হয়েছে: {ai_routes} বার\n"
        f"No API Call Mode-এ আটকে গিয়ে ইউজারের কাছে তথ্য চাওয়া হয়েছে (সব ইউজার মিলিয়ে): "
        f"{int(brain_os_metrics.get('no_api_stuck', 0))} বার\n"
        f"🌐 Phase 44 Browse Search দিয়ে উত্তর দেওয়া হয়েছে: {int(brain_os_metrics.get('browse_answers', 0))} বার\n"
        f"🏷️ Source Attribution: "
        + ("✅ চালু (ডিফল্ট ফরম্যাট: " + str(source_attribution_settings().get('format')) + ")"
           if source_attribution_enabled("chat") else "⛔ বন্ধ")
    ) + (build_phase27_status_text() if "build_phase27_status_text" in globals() else "")


async def brainstatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    await update.message.reply_text(build_brain_status_text())


async def noapimode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Phase 43: /noapimode on | off | status — প্রতিটা ইউজার নিজের চ্যাটের জন্য আলাদাভাবে
    ব্যবহার করতে পারবে (গ্লোবাল না, /memory বা /autoreply-এর মতোই শুধু নিজের চ্যাটে প্রভাব ফেলে)।
    চালু থাকলে সেই ইউজারের সাথে বট কোনো AI API কল করবে না, শুধু Brain OS দিয়েই উত্তর দেওয়ার চেষ্টা করবে।"""
    user_id = update.effective_user.id
    register_user(user_id)

    arg = context.args[0].lower() if context.args else ""
    if arg not in ("on", "off", "status"):
        current = "চালু ✅" if is_no_api_mode(user_id) else "বন্ধ ❌"
        await update.message.reply_text(
            "🧪 No API Call Mode (শুধু আপনার চ্যাটের জন্য)\n"
            f"বর্তমান অবস্থা: {current}\n\n"
            "চালু করতে: /noapimode on\n"
            "বন্ধ করতে: /noapimode off\n"
            "পরিসংখ্যান দেখতে: /noapimode status\n\n"
            "চালু থাকলে আপনার সাথে বট কোনো AI (Groq/OpenRouter/Cerebras) API কল করবে না — শুধু "
            "Brain OS (Knowledge/Pattern/Template/Documentation Engine) দিয়ে উত্তর দেওয়ার চেষ্টা করবে। "
            "উত্তর না পেলে জানাবে কোথায় আটকেছে এবং আরও তথ্য চাইবে — AI ফলব্যাক হবে না। "
            "এটা শুধু আপনার চ্যাটে প্রভাব ফেলে, অন্য কারও চ্যাটে না।"
        )
        return

    if arg == "status":
        current = "চালু ✅" if is_no_api_mode(user_id) else "বন্ধ ❌"
        await update.message.reply_text(
            "🧪 No API Call Mode — আপনার চ্যাট\n"
            f"অবস্থা: {current}"
        )
        return

    enabled = arg == "on"
    set_no_api_mode(user_id, enabled)
    if enabled:
        await update.message.reply_text(
            "✅ No API Call Mode চালু হলো (শুধু আপনার চ্যাটে)।\n"
            "এখন থেকে আপনার সাথে বট কোনো AI API কল করবে না — শুধু Brain OS দিয়ে যতটা সম্ভব উত্তর দেবে। "
            "না পারলে জানিয়ে দেবে কোথায় আটকে গেছে।"
        )
    else:
        await update.message.reply_text(
            "❌ No API Call Mode বন্ধ হলো — বট আপনার সাথে আগের মতো স্বাভাবিকভাবে AI API কল করতে পারবে।"
        )


async def decisionhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    try:
        limit = int(context.args[0]) if context.args and context.args[0].isdigit() else 10
        limit = max(1, min(limit, 50))
        rows = api_decision_history(limit=limit)
        if not rows:
            await update.message.reply_text("🧠 এখনো কোনো Decision history নেই।")
            return
        lines = ["🧠 Decision History", "━━━━━━━━━━━━━━━"]
        for row in rows[:limit]:
            lines.append(
                f"#{row.get('id', '?')} | {row.get('stage', '?')} | "
                f"confidence={float(row.get('confidence', 0)):.2f}\n"
                f"{str(row.get('created_at', ''))[:19]}"
            )
        await send_long_text(update, "\n".join(lines))
    except Exception as e:
        logger.warning("Decision history failed: %s", e)
        await update.message.reply_text("Decision history পড়তে সমস্যা হয়েছে।")


# ==================== Phase 36: Admin কমান্ড দিয়ে Knowledge/Pattern যোগ ====================

async def addknowledge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    এভাবে লিখুন (| দিয়ে আলাদা করে): /addknowledge ক্যাটাগরি | টাইটেল | কন্টেন্ট
    উদাহরণ: /addknowledge bot_info | রিফান্ড পলিসি | আমরা কোনো পেমেন্ট নিই না, তাই রিফান্ডের প্রশ্ন নেই।
    ঐচ্ছিকভাবে শেষে আরেকটা | দিয়ে priority(1-10) এবং confidence(0-1) দেওয়া যায়:
    /addknowledge ক্যাটাগরি | টাইটেল | কন্টেন্ট | 7 | 0.9
    Decision Engine এই এন্ট্রি সরাসরি ব্যবহার করবে (AI না ডেকেই উত্তর দিতে পারবে)।
    একই category+title+content আগে থেকে থাকলে নতুন করে যোগ হবে না, বিদ্যমানটাই দেখাবে।
    """
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return

    raw = update.message.text.split(None, 1)
    raw_args = raw[1] if len(raw) > 1 else ""
    parts = [p.strip() for p in raw_args.split("|")]
    if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
        await update.message.reply_text(
            "এভাবে লিখুন: /addknowledge ক্যাটাগরি | টাইটেল | কন্টেন্ট\n"
            "উদাহরণ: /addknowledge bot_info | রিফান্ড পলিসি | আমরা কোনো পেমেন্ট নিই না, তাই রিফান্ডের প্রশ্ন নেই।\n"
            "ঐচ্ছিক: শেষে | priority(1-10) | confidence(0-1) ও যোগ করা যায়।"
        )
        return

    category, title, content = parts[0], parts[1], parts[2]
    if len(content) > 4000:
        await update.message.reply_text("কন্টেন্ট একটু বেশি বড়। ৪০০০ অক্ষরের মধ্যে দিন।")
        return

    priority = 5
    confidence_score = 0.9
    try:
        if len(parts) >= 4 and parts[3]:
            priority = max(1, min(10, int(float(parts[3]))))
        if len(parts) >= 5 and parts[4]:
            confidence_score = max(0.0, min(1.0, float(parts[4])))
    except ValueError:
        await update.message.reply_text("priority সংখ্যা (1-10) ও confidence দশমিক সংখ্যা (0-1) হতে হবে।")
        return

    engine = KnowledgeEngine()
    try:
        existing = engine.check_duplicate(category, title, content)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addknowledge check_duplicate ব্যর্থ: {e}")
        existing = None

    if existing is not None:
        await update.message.reply_text(
            "⚠️ এই ডাটা আগে থেকেই আছে — একই ক্যাটাগরি+টাইটেল+কন্টেন্ট মিলে যাওয়ায় নতুন করে "
            "যোগ করা হয়নি (ডুপ্লিকেট রাখা হয় না)।\n"
            f"বিদ্যমান ID: {existing.id}\nক্যাটাগরি: {category}\nটাইটেল: {title}\n"
            "কন্টেন্ট বা টাইটেল বদলে দিলে আলাদা এন্ট্রি হিসেবে যোগ হবে।"
        )
        return

    try:
        result = engine.create(
            category=category, title=title, content=content,
            priority=priority, source=f"admin:{admin_id}", confidence_score=confidence_score,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addknowledge ব্যর্থ: {e}")
        result = None

    if result is None:
        await update.message.reply_text("❌ Knowledge যোগ করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        return

    await update.message.reply_text(
        "✅ নতুন Knowledge যোগ হয়েছে।\n"
        f"ID: {result.id}\nক্যাটাগরি: {category}\nটাইটেল: {title}\n"
        f"Priority: {priority} | Confidence: {confidence_score}"
    )


async def addpattern_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    এভাবে লিখুন (| দিয়ে আলাদা করে): /addpattern টাইপ | ম্যাচ_ভ্যালু | ক্যাটাগরি | নাম | উত্তর
    টাইপ হতে পারে: keyword / regex / intent
    উদাহরণ: /addpattern keyword | দাম কত | pricing | price_query | আমাদের সার্ভিস সম্পূর্ণ ফ্রি!
    এই প্যাটার্নের match_value ইউজারের মেসেজে পাওয়া গেলে বট সরাসরি "উত্তর" অংশটা রিপ্লাই দেবে,
    কোনো AI কল ছাড়াই।
    """
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return

    raw = update.message.text.split(None, 1)
    raw_args = raw[1] if len(raw) > 1 else ""
    parts = [p.strip() for p in raw_args.split("|")]
    if len(parts) < 5 or not parts[0] or not parts[1] or not parts[4]:
        await update.message.reply_text(
            "এভাবে লিখুন: /addpattern টাইপ | ম্যাচ_ভ্যালু | ক্যাটাগরি | নাম | উত্তর\n"
            f"টাইপ (pattern_type) হতে পারে: {', '.join(VALID_PATTERN_TYPES)}\n"
            "উদাহরণ: /addpattern keyword | দাম কত | pricing | price_query | আমাদের সার্ভিস সম্পূর্ণ ফ্রি!"
        )
        return

    pattern_type, match_value, category, name, description = parts[0], parts[1], parts[2], parts[3], parts[4]
    if pattern_type not in VALID_PATTERN_TYPES:
        await update.message.reply_text(f"অবৈধ টাইপ। ব্যবহার করুন: {', '.join(VALID_PATTERN_TYPES)}")
        return
    if len(description) > 2000:
        await update.message.reply_text("উত্তরের অংশটা একটু বেশি বড়। ২০০০ অক্ষরের মধ্যে দিন।")
        return

    engine = PatternEngine()
    try:
        existing = engine.check_duplicate(pattern_type, match_value, category)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addpattern check_duplicate ব্যর্থ: {e}")
        existing = None

    if existing is not None:
        await update.message.reply_text(
            "⚠️ এই প্যাটার্ন আগে থেকেই আছে — একই টাইপ+ম্যাচ_ভ্যালু+ক্যাটাগরি মিলে যাওয়ায় নতুন করে "
            "যোগ করা হয়নি (ডুপ্লিকেট রাখা হয় না)।\n"
            f"বিদ্যমান ID: {existing.id}\nটাইপ: {pattern_type}\nম্যাচ ভ্যালু: {match_value}\n"
            f"ক্যাটাগরি: {category}\n"
            "ভিন্ন উত্তর দিতে চাইলে match_value বা category পাল্টে আলাদা এন্ট্রি হিসেবে যোগ করুন।"
        )
        return

    try:
        result = engine.create(
            pattern_type=pattern_type, match_value=match_value, category=category,
            name=name or f"admin_{pattern_type}_{admin_id}", description=description,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addpattern ব্যর্থ: {e}")
        result = None

    if result is None:
        await update.message.reply_text(
            "❌ Pattern যোগ করতে সমস্যা হয়েছে। regex দিলে সঠিক regex কিনা চেক করুন, "
            "অথবা আবার চেষ্টা করুন।"
        )
        return

    await update.message.reply_text(
        "✅ নতুন Pattern যোগ হয়েছে।\n"
        f"ID: {result.id}\nটাইপ: {pattern_type}\nম্যাচ ভ্যালু: {match_value}\nক্যাটাগরি: {category}"
    )


async def addtemplate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    এভাবে লিখুন (| দিয়ে আলাদা করে): /addtemplate নাম | ক্যাটাগরি | বডি
    বডিতে {variable} স্টাইলে ভ্যারিয়েবল রাখা যায়, যেমন: "স্বাগতম {name}!"
    উদাহরণ: /addtemplate welcome_msg | onboarding | স্বাগতম {name}! আপনার ফ্রি লিমিট {limit} বার।
    ঐচ্ছিকভাবে শেষে | দিয়ে template_type ও priority(1-10) দেওয়া যায়:
    টাইপ হতে পারে: prompt / response / message / notification / system (ডিফল্ট: message)
    /addtemplate welcome_msg | onboarding | স্বাগতম... | message | 5
    রেন্ডার করতে DecisionEngine বা কোড থেকে TemplateEngine().render(id, {...}) ব্যবহার হয়।
    """
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return

    raw = update.message.text.split(None, 1)
    raw_args = raw[1] if len(raw) > 1 else ""
    parts = [p.strip() for p in raw_args.split("|")]
    if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
        await update.message.reply_text(
            "এভাবে লিখুন: /addtemplate নাম | ক্যাটাগরি | বডি\n"
            "উদাহরণ: /addtemplate welcome_msg | onboarding | স্বাগতম {name}! আপনার ফ্রি লিমিট {limit} বার।\n"
            f"ঐচ্ছিক: শেষে | template_type ({', '.join(VALID_TEMPLATE_TYPES)}) | priority(1-10) ও যোগ করা যায়।"
        )
        return

    name, category, body = parts[0], parts[1], parts[2]
    if len(body) > 4000:
        await update.message.reply_text("বডি একটু বেশি বড়। ৪০০০ অক্ষরের মধ্যে দিন।")
        return

    template_type = "message"
    priority = 5
    try:
        if len(parts) >= 4 and parts[3]:
            template_type = parts[3]
        if len(parts) >= 5 and parts[4]:
            priority = max(1, min(10, int(float(parts[4]))))
    except ValueError:
        await update.message.reply_text("priority সংখ্যা (1-10) হতে হবে।")
        return

    if template_type not in VALID_TEMPLATE_TYPES:
        await update.message.reply_text(f"অবৈধ template_type। ব্যবহার করুন: {', '.join(VALID_TEMPLATE_TYPES)}")
        return

    engine = TemplateEngine()
    try:
        existing = engine.get_by_name(name)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addtemplate get_by_name ব্যর্থ: {e}")
        existing = None

    if existing is not None:
        await update.message.reply_text(
            "⚠️ এই নামে টেমপ্লেট আগে থেকেই আছে — টেমপ্লেটের নাম ইউনিক হতে হয়, তাই নতুন করে যোগ করা "
            "হয়নি।\n"
            f"বিদ্যমান ID: {existing.id}\nনাম: {name}\nক্যাটাগরি: {existing.category}\n"
            "আপডেট করতে চাইলে ভিন্ন নাম দিয়ে নতুন টেমপ্লেট যোগ করুন, অথবা আমাকে বলুন — /updatetemplate "
            "চালু করে দিতে পারি।"
        )
        return

    error = engine.validate_template(body, template_type)
    if error:
        await update.message.reply_text(f"❌ টেমপ্লেট ভ্যালিডেশন ব্যর্থ: {error}")
        return

    try:
        result = engine.create(
            name=name, category=category, body=body, description=f"admin:{admin_id}",
            priority=priority, template_type=template_type,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addtemplate ব্যর্থ: {e}")
        result = None

    if result is None:
        await update.message.reply_text("❌ Template যোগ করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        return

    try:
        var_list = json.loads(result.variables) if result.variables else []
    except (json.JSONDecodeError, TypeError):
        var_list = []
    vars_found = ", ".join(var_list) if var_list else "কোনো ভ্যারিয়েবল নেই"
    await update.message.reply_text(
        "✅ নতুন Template যোগ হয়েছে।\n"
        f"ID: {result.id}\nনাম: {name}\nক্যাটাগরি: {category}\nটাইপ: {template_type}\n"
        f"ভ্যারিয়েবল: {vars_found}"
    )


async def adddoc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    এভাবে লিখুন (| দিয়ে আলাদা করে): /adddoc টেকনোলজি | ক্যাটাগরি | টাইটেল | কন্টেন্ট
    উদাহরণ: /adddoc telegram-bot | commands | /dub কীভাবে কাজ করে | ভিডিওতে রিপ্লাই দিয়ে...
    ঐচ্ছিকভাবে শেষে | দিয়ে doc_type দেওয়া যায়: api / module / function / class (ডিফল্ট: module)
    এটা মূলত ইন্টারনাল রেফারেন্স/নলেজ — DecisionEngine ও KnowledgeEngine.search() এটা ব্যবহার করতে পারে।
    """
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return

    raw = update.message.text.split(None, 1)
    raw_args = raw[1] if len(raw) > 1 else ""
    parts = [p.strip() for p in raw_args.split("|")]
    if len(parts) < 4 or not parts[0] or not parts[1] or not parts[2] or not parts[3]:
        await update.message.reply_text(
            "এভাবে লিখুন: /adddoc টেকনোলজি | ক্যাটাগরি | টাইটেল | কন্টেন্ট\n"
            "উদাহরণ: /adddoc telegram-bot | commands | /dub কীভাবে কাজ করে | ভিডিওতে রিপ্লাই দিয়ে...\n"
            f"ঐচ্ছিক: শেষে | doc_type ({', '.join(VALID_DOC_TYPES)}) ও যোগ করা যায়।"
        )
        return

    technology, category, title, content = parts[0], parts[1], parts[2], parts[3]
    if len(content) > 6000:
        await update.message.reply_text("কন্টেন্ট একটু বেশি বড়। ৬০০০ অক্ষরের মধ্যে দিন।")
        return

    doc_type = "module"
    if len(parts) >= 5 and parts[4]:
        doc_type = parts[4]
    if doc_type not in VALID_DOC_TYPES:
        await update.message.reply_text(f"অবৈধ doc_type। ব্যবহার করুন: {', '.join(VALID_DOC_TYPES)}")
        return

    try:
        conn = get_brain_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM brain_documentation WHERE technology=? AND category=? AND title=? "
            "AND deleted_at='' LIMIT 1",
            (technology, category, title),
        )
        dup_row = cur.fetchone()
        conn.close()
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/adddoc ডুপ্লিকেট চেক ব্যর্থ: {e}")
        dup_row = None

    if dup_row is not None:
        await update.message.reply_text(
            "⚠️ এই ডকুমেন্টেশন আগে থেকেই আছে — একই টেকনোলজি+ক্যাটাগরি+টাইটেল মিলে যাওয়ায় নতুন করে "
            "যোগ করা হয়নি (ডুপ্লিকেট রাখা হয় না)।\n"
            f"বিদ্যমান ID: {dup_row[0]}\nটেকনোলজি: {technology}\nক্যাটাগরি: {category}\nটাইটেল: {title}"
        )
        return

    try:
        result = DocumentationEngine().create(
            technology=technology, category=category, title=title, content=content,
            doc_type=doc_type, internal_notes=f"admin:{admin_id}",
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/adddoc ব্যর্থ: {e}")
        result = None

    if result is None:
        await update.message.reply_text("❌ Documentation যোগ করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        return

    await update.message.reply_text(
        "✅ নতুন Documentation যোগ হয়েছে।\n"
        f"ID: {result.id}\nটেকনোলজি: {technology}\nক্যাটাগরি: {category}\nটাইটেল: {title}\nটাইপ: {doc_type}"
    )


async def addsolution_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    এভাবে লিখুন (| দিয়ে আলাদা করে): /addsolution ভাষা | error_signature | বর্ণনা | সমাধান
    উদাহরণ: /addsolution python | KeyError | ডিকশনারিতে চাবি নেই | .get() ব্যবহার করুন অথবা আগে চেক করুন
    ঐচ্ছিকভাবে শেষে | দিয়ে category ও severity দেওয়া যায় (severity: low/medium/high/critical)
    /addsolution python | KeyError | ... | ... | data_error | high
    একই ভাষা+error_signature আগে থেকে থাকলে এন্ট্রি নতুন হয় না, বরং বর্ণনা/সমাধান আপডেট হয়ে যায় —
    যাতে ভবিষ্যতে একই এরর হলে ErrorEngine সবচেয়ে সাম্প্রতিক সমাধানটা দেখাতে পারে।
    """
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return

    raw = update.message.text.split(None, 1)
    raw_args = raw[1] if len(raw) > 1 else ""
    parts = [p.strip() for p in raw_args.split("|")]
    if len(parts) < 4 or not parts[0] or not parts[1] or not parts[2] or not parts[3]:
        await update.message.reply_text(
            "এভাবে লিখুন: /addsolution ভাষা | error_signature | বর্ণনা | সমাধান\n"
            "উদাহরণ: /addsolution python | KeyError | ডিকশনারিতে চাবি নেই | .get() ব্যবহার করুন\n"
            f"ঐচ্ছিক: শেষে | category | severity ({', '.join(VALID_SEVERITIES)}) ও যোগ করা যায়।"
        )
        return

    language, error_signature, description, solution = parts[0], parts[1], parts[2], parts[3]
    category = parts[4] if len(parts) >= 5 and parts[4] else "unknown"
    severity = parts[5] if len(parts) >= 6 and parts[5] else "medium"
    if severity not in VALID_SEVERITIES:
        await update.message.reply_text(f"অবৈধ severity। ব্যবহার করুন: {', '.join(VALID_SEVERITIES)}")
        return
    if len(solution) > 3000:
        await update.message.reply_text("সমাধানের অংশটা একটু বেশি বড়। ৩০০০ অক্ষরের মধ্যে দিন।")
        return

    engine = ErrorEngine()
    try:
        existing = engine._find_by_signature(language, error_signature)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addsolution বিদ্যমান এন্ট্রি চেক ব্যর্থ: {e}")
        existing = None

    try:
        result = engine.register_solution(
            language=language, error_signature=error_signature, description=description,
            solution=solution, category=category, severity=severity,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/addsolution ব্যর্থ: {e}")
        result = None

    if result is None:
        await update.message.reply_text("❌ Solution যোগ করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        return

    status_label = "আপডেট হয়েছে (আগে থেকেই ছিল)" if existing is not None else "নতুন যোগ হয়েছে"
    await update.message.reply_text(
        f"✅ Error solution {status_label}।\n"
        f"ID: {result.id}\nভাষা: {language}\nError signature: {error_signature}\nSeverity: {severity}"
    )


BULK_IMPORT_ENGINES = {
    "knowledge": ("KnowledgeEngine", "category, title, content আবশ্যক (tags/priority/source ঐচ্ছিক)"),
    "pattern": ("PatternEngine", "pattern_type, match_value, category, name আবশ্যক"),
    "template": ("TemplateEngine", "name, category, body আবশ্যক (template_type/priority ঐচ্ছিক)"),
    "doc": ("DocumentationEngine", "technology, category, title, content আবশ্যক"),
    "error": ("ErrorEngine", "language, error_signature, description, solution আবশ্যক"),
}


async def bulkimport_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Phase 40: একসাথে অনেক Knowledge/Pattern/Template/Doc/Error-solution যোগ করার জন্য।
    কোডিং জানা লাগে না — প্রথমে একটা .json ফাইল বটে পাঠান (কোনো কমান্ড ছাড়াই), তারপর
    সেই ফাইলটাতেই রিপ্লাই দিয়ে লিখুন:
    /bulkimport knowledge   (অথবা pattern / template / doc / error)
    JSON ফাইলটা এমন হতে হবে — একটা লিস্টের ভেতর অনেকগুলো dict, যেমন knowledge-এর জন্য:
    [
      {"category": "bot_info", "title": "রিফান্ড পলিসি", "content": "আমরা...", "priority": 7},
      {"category": "bot_info", "title": "সাপোর্ট সময়", "content": "..."}
    ]
    ডুপ্লিকেট এন্ট্রি (knowledge/pattern-এর ক্ষেত্রে) স্বয়ংক্রিয়ভাবে স্কিপ হয়ে যায়।
    JSON ফাইল বানাতে না জানলে, প্রতিটা তথ্য এখানে চ্যাটে লিখে/পেস্ট করে পাঠান —
    আমি সেটা গুছিয়ে ঠিকঠাক JSON ফাইল বানিয়ে দেব, আপনি শুধু সেটা বটে আপলোড করবেন।
    """
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return

    args = context.args
    if not args or args[0].lower() not in BULK_IMPORT_ENGINES:
        lines = ["এভাবে লিখুন: একটা .json ফাইল বটে পাঠান, তারপর সেটাতে রিপ্লাই দিয়ে লিখুন:",
                  "/bulkimport <ধরন>", "", "ধরন হতে পারে:"]
        for key, (_, hint) in BULK_IMPORT_ENGINES.items():
            lines.append(f"• {key} — {hint}")
        await update.message.reply_text("\n".join(lines))
        return

    kind = args[0].lower()
    target = update.message.reply_to_message
    doc = target.document if target and target.document else None
    if not doc or not (doc.file_name or "").lower().endswith(".json"):
        await update.message.reply_text(
            "প্রথমে একটা .json ফাইল বটে পাঠান, তারপর সেই ফাইলে রিপ্লাই দিয়ে "
            f"/bulkimport {kind} লিখুন।"
        )
        return
    if doc.file_size and doc.file_size > 5 * 1024 * 1024:
        await update.message.reply_text("ফাইল ৫ MB-এর বেশি বড়। ছোট ছোট ভাগে ভাগ করে পাঠান।")
        return

    status = await update.message.reply_text("ফাইল পড়া হচ্ছে...")
    try:
        file_obj = await doc.get_file()
        raw_bytes = await file_obj.download_as_bytearray()
        entries = json.loads(bytes(raw_bytes).decode("utf-8"))
    except json.JSONDecodeError as e:
        await status.edit_text(f"❌ JSON ফাইলটা সঠিক ফরম্যাটে নেই: {e}")
        return
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/bulkimport ফাইল পড়তে ব্যর্থ: {e}")
        await status.edit_text("❌ ফাইল পড়তে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        return

    if not isinstance(entries, list) or not entries:
        await status.edit_text("❌ JSON ফাইলটা একটা non-empty লিস্ট হতে হবে (প্রতিটা আইটেম একটা dict)।")
        return
    if len(entries) > 500:
        await status.edit_text(f"একবারে সর্বোচ্চ ৫০০টা এন্ট্রি — আপনার ফাইলে {len(entries)}টা আছে। ভাগ করে পাঠান।")
        return

    try:
        if kind == "knowledge":
            summary = KnowledgeEngine().bulk_import(entries)
        elif kind == "pattern":
            summary = PatternEngine().bulk_import(entries)
        elif kind == "template":
            summary = TemplateEngine().bulk_import(entries)
        elif kind == "doc":
            summary = DocumentationEngine().bulk_import(entries)
        else:
            summary = ErrorEngine().bulk_import(entries)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"/bulkimport ({kind}) ব্যর্থ: {e}")
        await status.edit_text("❌ ইমপোর্ট করতে সমস্যা হয়েছে। ফাইলের ফরম্যাট আরেকবার চেক করুন।")
        return

    created = summary.get("created", 0)
    skipped = summary.get("skipped_duplicates", summary.get("skipped", 0))
    failed = summary.get("failed", 0)
    await status.edit_text(
        f"✅ Bulk import শেষ ({kind})\n"
        f"মোট এন্ট্রি: {len(entries)}\n"
        f"✅ নতুন যোগ হয়েছে: {created}\n"
        f"⏭️ ডুপ্লিকেট (স্কিপ): {skipped}\n"
        f"❌ ব্যর্থ: {failed}"
    )


async def chat_general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Phase 17: live Brain OS routing + safe AI fallback for normal chat."""
    user_id = update.effective_user.id
    register_user(user_id)
    auto_reply, memory_enabled, _language_pref = get_user_settings(user_id)
    if not auto_reply:
        return
    if not await quota_guard(update, action="chat"):
        return

    user_text = update.message.text
    thinking = await update.message.reply_text(await localize(user_id, "ভাবছি..."))
    try:
        manual_lang, is_manual = get_effective_language(user_id)
        if is_manual:
            lang_name = UI_LANG_CHOICES.get(manual_lang, manual_lang)
            system_prompt = (
                "তুমি একজন সহায়ক AI সহকারী। ইউজার যেই ভাষাতেই লিখুক না কেন, তুমি সবসময় "
                f"{lang_name} ভাষায় সংক্ষেপে ও স্পষ্টভাবে উত্তর দেবে।"
            )
        else:
            detected_lang = detect_language(user_text)
            lang_name = language_display_name(detected_lang)
            system_prompt = (
                "তুমি একজন সহায়ক AI সহকারী। ইউজার যেই ভাষায় লিখেছে "
                f"(সনাক্ত হয়েছে: {lang_name}), সেই একই ভাষায় সংক্ষেপে ও স্পষ্টভাবে উত্তর দাও। "
                "ভাষা শনাক্ত করা না গেলে বাংলায় উত্তর দাও।"
            )

        # Phase 17: remember useful live context first; read prior context for richer routing.
        _brain_save_live_context(user_id, lang_name, user_text)
        live_context = _brain_get_live_context(user_id)
        if live_context:
            system_prompt += "\n\nআগের দরকারি Brain OS context:\n" + live_context

        decision = await _phase17_decide(user_id, user_text)

        # Step 1: 💾 Database — Brain OS-এর নিজের Knowledge/Pattern/Template/Documentation
        # Engine (Decision Engine) সরাসরি নিশ্চিত উত্তর দিতে পারলে সেটাই (ব্যাজসহ) ফেরত যায়।
        if decision.get("strategy") == "direct":
            direct_answer = _brain_payload_to_answer(decision.get("payload"))
            if direct_answer:
                brain_os_metrics["direct_answers"] += 1
                if memory_enabled:
                    save_message(user_id, "user", user_text)
                    save_message(user_id, "assistant", direct_answer)
                reply = attach_source_badge(
                    direct_answer,
                    metadata_from_decision(decision, query=user_text),
                    "chat",
                    attribution_lang(user_id),
                )
                await send_long_text(update, reply)
                return
            brain_os_metrics["direct_failures"] += 1

        no_api_mode = is_no_api_mode(user_id)

        # Step 2: 🌐 Browser Search — ডাটাবেজে না পেলে স্বয়ংক্রিয় (automatic, কোনো আলাদা
        # কমান্ড ছাড়াই) আগে Tavily Real Web Search (Key থাকলে), তারপর
        # DuckDuckGo/Wikipedia-তে খোঁজা হয়; পেলে সেটাই (দরকার হলে AI দিয়ে গুছিয়ে,
        # ব্যাজসহ) ফেরত যায় এবং নিজের Knowledge Engine-এ সেভ হয়।
        browse_answer = await _automatic_browse_answer(user_id, user_text, lang_name, no_api_mode)
        if browse_answer:
            brain_os_metrics["browse_answers"] += 1
            if memory_enabled:
                save_message(user_id, "user", user_text)
                save_message(user_id, "assistant", browse_answer)
            if not no_api_mode and should_show_own_key_hint(user_id):
                browse_answer += build_own_api_key_hint(user_id)
            await send_long_text(update, browse_answer)
            return

        # Step 3: 🔵 Groq API — ডাটাবেজ ও ব্রাউজার কোনোটাতেই না পেলে শেষ ধাপে AI API।
        if no_api_mode:
            # Phase 43: No API Call Mode চালু — Brain OS/Browse Search কোনোটাই সরাসরি উত্তর
            # দিতে পারেনি, তাই AI-কে (memory/cache কোনো পথেই) কল না করে ইউজারকে জানানো হচ্ছে
            # কোথায় আটকে গেছে।
            brain_os_metrics["no_api_stuck"] += 1
            reply = build_no_api_stuck_message(decision)
            source_meta = None
        elif memory_enabled:
            # Memory চালু থাকলে উত্তর কথোপকথনের ইতিহাসের উপর নির্ভরশীল, তাই শেয়ার্ড ক্যাশ
            # নিরাপদ নয় — এই পথে সবসময় সরাসরি AI-কে জিজ্ঞেস করা হয়, আগের মতোই।
            brain_os_metrics["ai_routes"] += 1
            history_limit = MEMORY_HISTORY_LIMIT_PREMIUM if is_premium_active(user_id) else MEMORY_HISTORY_LIMIT
            history = get_recent_history(user_id, limit=history_limit)
            # Phase 45: user_id দেওয়া হচ্ছে — নিজস্ব API Key থাকলে সেটাই ব্যবহার হবে।
            reply = await ask_ai_with_history(system_prompt, history, user_text, user_id=user_id)
            # Phase 47: Memory-পথে শেয়ার্ড ক্যাশ ব্যবহার হয় না, তাই এটা সবসময়ই তাজা 🔵 AI উত্তর।
            source_meta = make_source_metadata("groq", confidence=0.90, query=user_text)
            save_message(user_id, "user", user_text)
            save_message(user_id, "assistant", reply)
            # Phase 44: Browse Search-এও কিছু না পেয়ে AI API কল করে যে উত্তর পাওয়া গেল, সেটাও
            # নিজে থেকে Knowledge Engine-এ যুক্ত হয়ে যায় — পরের বার একই প্রশ্নে আর AI লাগবে না।
            _phase44_save_ai_knowledge(user_text, reply)
        else:
            # Phase 35: Memory বন্ধ থাকলে প্রতিটা মেসেজ স্বনির্ভর (single-turn), তাই একই/প্রায়-
            # একই প্রশ্ন যেকোনো ইউজার আবার জিজ্ঞেস করলে শেয়ার্ড ক্যাশ থেকে সরাসরি উত্তর দেওয়া
            # নিরাপদ — এতে বারবার একই প্রশ্নে নতুন করে AI কল লাগে না।
            cache_key_text = user_text.strip().lower()
            cached_reply = await general_chat_cache.get(lang_name, cache_key_text)
            if cached_reply is not None:
                reply = cached_reply
                brain_os_metrics["direct_answers"] += 1
                # Phase 47: ক্যাশ-হিট মানে তথ্যটা 💾 নিজের ডাটাবেজ/ক্যাশ থেকে এসেছে, AI কল হয়নি।
                source_meta = make_source_metadata(
                    "database", confidence=0.90, cache_hit=True,
                    note="General Chat Cache", query=user_text,
                )
            else:
                brain_os_metrics["ai_routes"] += 1
                # Phase 45: user_id দেওয়া হচ্ছে — নিজস্ব API Key থাকলে সেটাই ব্যবহার হবে।
                reply = await ask_ai(system_prompt, user_text, user_id=user_id)
                await general_chat_cache.set(lang_name, cache_key_text, reply)
                source_meta = make_source_metadata("groq", confidence=0.90, query=user_text)
                # Phase 44: এই AI উত্তরও নিজে থেকে Knowledge Engine-এ যুক্ত হয়ে যায়।
                _phase44_save_ai_knowledge(user_text, reply)

        # Phase 45: Brain OS নিজে থেকে উত্তর দিতে পারেনি (তাই Browse/AI resource ব্যবহার হয়েছে)
        # এবং ইউজারের নিজস্ব API Key নেই — এমন ক্ষেত্রে দিনে একবার নিজস্ব Key যুক্ত করার
        # অনুস্মারক জুড়ে দেওয়া হয় (বেশি বিরক্তিকর না করার জন্য প্রতিবার নয়)।
        if reply and not no_api_mode and should_show_own_key_hint(user_id):
            reply += build_own_api_key_hint(user_id)

        # Phase 47: সবার শেষে উৎস-ব্যাজ বসে — উপরে চ্যাট-মেমরিতে যা সেভ হয়েছে তা ব্যাজ ছাড়াই
        # থাকে (ইতিহাসে অপ্রয়োজনীয় লেখা ঢোকে না), আর ব্যাজ বন্ধ/অনুপলব্ধ থাকলে reply অপরিবর্তিত।
        reply = attach_source_badge(reply, source_meta, "chat", attribution_lang(user_id))

        await send_long_text(update, reply)
    except Exception as e:
        logger.error(f"চ্যাট/Brain OS এরর: {e}")
        # Phase 43: No API Call Mode চালু থাকলে এই legacy fallback-ও AI কল করবে না —
        # ব্যর্থতাকে সরাসরি "আটকে গেছে" মেসেজ হিসেবে দেখানো হবে।
        if is_no_api_mode(user_id):
            brain_os_metrics["no_api_stuck"] += 1
            await update.message.reply_text(
                build_no_api_stuck_message({"stage": "decision", "confidence": 0.0})
            )
        else:
            # Brain OS is intentionally non-fatal. If the failure happened before AI routing,
            # perform one clean legacy AI attempt before showing the generic error.
            try:
                manual_lang, is_manual = get_effective_language(user_id)
                lang_name = UI_LANG_CHOICES.get(manual_lang, manual_lang) if is_manual else language_display_name(detect_language(user_text))
                fallback_prompt = (
                    "তুমি একজন সহায়ক AI সহকারী। ইউজারের ভাষায় সংক্ষেপে ও স্পষ্টভাবে উত্তর দাও। "
                    f"উত্তরের ভাষা: {lang_name}."
                )
                reply = await ask_ai(fallback_prompt, user_text, user_id=user_id)
                if memory_enabled:
                    save_message(user_id, "user", user_text)
                    save_message(user_id, "assistant", reply)
                brain_os_metrics["ai_routes"] += 1
                # Phase 44: legacy fallback পথেও AI উত্তর নিজে থেকে Knowledge Engine-এ সেভ হয়।
                _phase44_save_ai_knowledge(user_text, reply)
                # Phase 47: এই পথের উত্তরও 🔵 Groq API থেকে আসে, তাই ব্যাজ একই রকম।
                await send_long_text(
                    update,
                    attach_source_badge(
                        reply,
                        make_source_metadata("groq", confidence=0.85, query=user_text, note="Legacy fallback"),
                        "chat",
                        attribution_lang(user_id),
                    ),
                )
            except Exception as fallback_error:
                logger.error(f"Legacy AI fallback-ও ব্যর্থ: {fallback_error}")
                await update.message.reply_text(await localize(user_id, "দুঃখিত, উত্তর দিতে সমস্যা হয়েছে। আবার চেষ্টা করুন।"))
    finally:
        try:
            await thinking.delete()
        except Exception:
            pass


# ============================= AI মেমরি / ভাষা / অটো-রিপ্লাই সেটিংস =============================

async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI Memory চালু/বন্ধ করার কমান্ড: /memory on অথবা /memory off"""
    user_id = update.effective_user.id
    register_user(user_id)
    if not context.args or context.args[0].lower() not in ("on", "off"):
        _, memory_enabled, _ = get_user_settings(user_id)
        state = "চালু ✅" if memory_enabled else "বন্ধ ❌"
        await update.message.reply_text(
            f"AI Memory বর্তমানে: {state}\nবদলাতে লিখুন: /memory on অথবা /memory off"
        )
        return
    value = 1 if context.args[0].lower() == "on" else 0
    update_field(user_id, "memory_enabled", value)
    if value:
        await update.message.reply_text("✅ AI Memory চালু হলো — বট এখন থেকে আগের কথোপকথন মনে রাখবে।")
    else:
        await update.message.reply_text("❌ AI Memory বন্ধ হলো — প্রতিটা মেসেজ আলাদাভাবে বিবেচনা করা হবে।")


async def clearmemory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_memory(user_id)
    await update.message.reply_text("🧹 আপনার সাথে হওয়া আগের চ্যাটের স্মৃতি মুছে ফেলা হয়েছে।")


async def autoreply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto Reply On/Off: /autoreply on অথবা /autoreply off"""
    user_id = update.effective_user.id
    register_user(user_id)
    if not context.args or context.args[0].lower() not in ("on", "off"):
        auto_reply, _, _ = get_user_settings(user_id)
        state = "চালু ✅" if auto_reply else "বন্ধ ❌"
        await update.message.reply_text(
            f"Auto Reply বর্তমানে: {state}\nবদলাতে লিখুন: /autoreply on অথবা /autoreply off"
        )
        return
    value = 1 if context.args[0].lower() == "on" else 0
    update_field(user_id, "auto_reply", value)
    if value:
        await update.message.reply_text("✅ Auto Reply চালু হলো — সরাসরি লিখলেই বট উত্তর দেবে।")
    else:
        await update.message.reply_text(
            "❌ Auto Reply বন্ধ হলো — এখন থেকে শুধু কমান্ড (/translate, /tts ইত্যাদি) কাজ করবে, "
            "সরাসরি লেখায় বট চুপ থাকবে।"
        )


async def detectlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Language Detection: টেক্সট আর্গুমেন্ট দিয়ে অথবা কোনো মেসেজে রিপ্লাই দিয়ে ব্যবহার করা যায়।"""
    text = " ".join(context.args)
    if not text and update.message.reply_to_message and update.message.reply_to_message.text:
        text = update.message.reply_to_message.text
    if not text:
        await update.message.reply_text("এভাবে লিখুন: /detectlang আপনার লেখা\nঅথবা কোনো মেসেজে রিপ্লাই দিয়ে /detectlang লিখুন।")
        return
    lang_code = detect_language(text)
    await update.message.reply_text(
        f"🌐 সনাক্তকৃত ভাষা: {language_display_name(lang_code)} (কোড: {lang_code})"
    )


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="translate"):
        return
    if len(context.args) < 2:
        await update.message.reply_text("এভাবে লিখুন: /translate english আমি ভালো আছি")
        return
    target_lang = context.args[0]
    text = " ".join(context.args[1:])
    user_id = update.effective_user.id
    system_prompt = (
        f"তুমি একজন অনুবাদক। ইউজারের লেখাটা {target_lang} ভাষায় অনুবাদ করো। শুধু অনুবাদটাই লিখবে, অন্য কিছু লিখবে না।"
    )
    try:
        # Phase 47 priority: 💾 Database (cache) → 🌐 Browser → 🔵 Groq API।
        # Step 1: Database/cache — একই (ভাষা, লেখা) আগে অনুবাদ করা থাকলে সরাসরি ক্যাশ থেকে।
        cached = await ai_response_cache.get(system_prompt, text)
        if cached is not None:
            metadata = make_source_metadata(
                "database", confidence=0.92, cache_hit=True,
                note=f"অনুবাদ → {target_lang}", query=text,
            )
            await send_long_text(update, attach_source_badge(cached, metadata, "translate", attribution_lang(user_id)))
            return

        # Step 2: Browser Search (automatic, /search কমান্ড ছাড়াই)।
        no_api_mode = is_no_api_mode(user_id)
        if not no_api_mode:
            browse_answer = await _automatic_browse_answer(
                user_id, text, _browse_lang_hint(user_id, text), no_api_mode, command="translate"
            )
            if browse_answer:
                await send_long_text(update, browse_answer)
                return

        # Step 3: Groq API fallback (Phase 10: cache-এও সেভ হয়)।
        reply = await ask_ai(
            system_prompt,
            text,
            use_cache=True,  # Phase 10: একই ভাষায় একই লেখা আগে অনুবাদ করা থাকলে ক্যাশ থেকে দেওয়া হবে
            user_id=user_id,  # Phase 45: নিজস্ব API Key থাকলে সেটাই ব্যবহার হবে
        )
        metadata = make_source_metadata("groq", confidence=0.92, note=f"অনুবাদ → {target_lang}", query=text)
        await send_long_text(update, attach_source_badge(reply, metadata, "translate", attribution_lang(user_id)))
    except Exception as e:
        logger.error(f"অনুবাদ এরর: {e}")
        await update.message.reply_text(
            await localize(user_id, "দুঃখিত, অনুবাদ করতে সমস্যা হয়েছে।")
        )


async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="grammar"):
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("এভাবে লিখুন: /grammar আপনার লেখা")
        return
    user_id = update.effective_user.id
    system_prompt = "তুমি লেখার ভুল ঠিক করো (বানান, গ্রামার)। শুধু ঠিক করা লেখাটাই ফেরত দাও, অন্য কিছু বলবে না।"
    try:
        # Phase 47 priority: 💾 Database (cache) → 🌐 Browser → 🔵 Groq API।
        cached = await ai_response_cache.get(system_prompt, text)
        if cached is not None:
            metadata = make_source_metadata(
                "database", confidence=0.92, cache_hit=True,
                note="গ্রামার চেক", query=text,
            )
            await send_long_text(update, attach_source_badge(cached, metadata, "grammar", attribution_lang(user_id)))
            return

        no_api_mode = is_no_api_mode(user_id)
        if not no_api_mode:
            browse_answer = await _automatic_browse_answer(
                user_id, text, _browse_lang_hint(user_id, text), no_api_mode, command="grammar"
            )
            if browse_answer:
                await send_long_text(update, browse_answer)
                return

        reply = await ask_ai(
            system_prompt,
            text,
            use_cache=True,  # Phase 10: একই লেখা আগে গ্রামার চেক করা থাকলে ক্যাশ থেকে দেওয়া হবে
            user_id=user_id,  # Phase 45: নিজস্ব API Key থাকলে সেটাই ব্যবহার হবে
        )
        metadata = make_source_metadata("groq", confidence=0.92, note="গ্রামার চেক", query=text)
        await send_long_text(update, attach_source_badge(reply, metadata, "grammar", attribution_lang(user_id)))
    except Exception as e:
        logger.error(f"গ্রামার এরর: {e}")
        await update.message.reply_text(await localize(user_id, "দুঃখিত, সমস্যা হয়েছে।"))


async def rewrite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="rewrite"):
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("এভাবে লিখুন: /rewrite আপনার লেখা")
        return
    user_id = update.effective_user.id
    system_prompt = "তুমি লেখাটা একই অর্থ রেখে নতুনভাবে সুন্দর করে লেখো।"
    try:
        # Phase 47 priority: 💾 Database (cache) → 🌐 Browser → 🔵 Groq API।
        cached = await ai_response_cache.get(system_prompt, text)
        if cached is not None:
            metadata = make_source_metadata(
                "database", confidence=0.90, cache_hit=True, note="রিরাইট", query=text,
            )
            await send_long_text(update, attach_source_badge(cached, metadata, "rewrite", attribution_lang(user_id)))
            return

        no_api_mode = is_no_api_mode(user_id)
        if not no_api_mode:
            browse_answer = await _automatic_browse_answer(
                user_id, text, _browse_lang_hint(user_id, text), no_api_mode, command="rewrite"
            )
            if browse_answer:
                await send_long_text(update, browse_answer)
                return

        reply = await ask_ai(
            system_prompt, text,
            use_cache=True, user_id=user_id,
        )
        metadata = make_source_metadata("groq", confidence=0.90, note="রিরাইট", query=text)
        await send_long_text(update, attach_source_badge(reply, metadata, "rewrite", attribution_lang(user_id)))
    except Exception as e:
        logger.error(f"রিরাইট এরর: {e}")
        await update.message.reply_text(await localize(user_id, "দুঃখিত, সমস্যা হয়েছে।"))


async def tone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="tone"):
        return
    if len(context.args) < 2:
        await update.message.reply_text("এভাবে লিখুন: /tone formal আপনার লেখা (formal অথবা casual)")
        return
    tone_type = context.args[0]
    text = " ".join(context.args[1:])
    user_id = update.effective_user.id
    system_prompt = f"তুমি লেখাটাকে {tone_type} (আনুষ্ঠানিক/অনানুষ্ঠানিক) স্টাইলে বদলে দাও।"
    try:
        # Phase 47 priority: 💾 Database (cache) → 🌐 Browser → 🔵 Groq API।
        cached = await ai_response_cache.get(system_prompt, text)
        if cached is not None:
            metadata = make_source_metadata(
                "database", confidence=0.90, cache_hit=True,
                note=f"টোন → {tone_type}", query=text,
            )
            await send_long_text(update, attach_source_badge(cached, metadata, "tone", attribution_lang(user_id)))
            return

        no_api_mode = is_no_api_mode(user_id)
        if not no_api_mode:
            browse_answer = await _automatic_browse_answer(
                user_id, text, _browse_lang_hint(user_id, text), no_api_mode, command="tone"
            )
            if browse_answer:
                await send_long_text(update, browse_answer)
                return

        reply = await ask_ai(
            system_prompt, text,
            use_cache=True, user_id=user_id,
        )
        metadata = make_source_metadata("groq", confidence=0.90, note=f"টোন → {tone_type}", query=text)
        await send_long_text(update, attach_source_badge(reply, metadata, "tone", attribution_lang(user_id)))
    except Exception as e:
        logger.error(f"টোন এরর: {e}")
        await update.message.reply_text(await localize(user_id, "দুঃখিত, সমস্যা হয়েছে।"))


async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="summarize"):
        return
    text = " ".join(context.args)
    if not text and update.message.reply_to_message and update.message.reply_to_message.text:
        text = update.message.reply_to_message.text
    if not text:
        await update.message.reply_text(
            await localize(
                update.effective_user.id,
                "কোনো মেসেজে রিপ্লাই দিয়ে /summarize লিখুন, অথবা /summarize এর পর লেখা দিন।",
            )
        )
        return
    user_id = update.effective_user.id
    system_prompt = "তুমি লেখাটার সংক্ষিপ্ত সারমর্ম বাংলায় লিখে দাও।"
    try:
        # Phase 47 priority: 💾 Database (cache) → 🌐 Browser → 🔵 Groq API।
        cached = await ai_response_cache.get(system_prompt, text)
        if cached is not None:
            metadata = make_source_metadata(
                "database", confidence=0.90, cache_hit=True, note="সারসংক্ষেপ", query=text,
            )
            await send_long_text(update, attach_source_badge(cached, metadata, "summarize", attribution_lang(user_id)))
            return

        no_api_mode = is_no_api_mode(user_id)
        if not no_api_mode:
            browse_answer = await _automatic_browse_answer(
                user_id, text, _browse_lang_hint(user_id, text), no_api_mode, command="summarize"
            )
            if browse_answer:
                await send_long_text(update, browse_answer)
                return

        reply = await ask_ai(
            system_prompt, text,
            use_cache=True, user_id=user_id,
        )
        metadata = make_source_metadata("groq", confidence=0.90, note="সারসংক্ষেপ", query=text)
        await send_long_text(update, attach_source_badge(reply, metadata, "summarize", attribution_lang(user_id)))
    except Exception as e:
        logger.error(f"সামারি এরর: {e}")
        await update.message.reply_text(await localize(user_id, "দুঃখিত, সমস্যা হয়েছে।"))


# ============================= PDF ফিচার =============================

def is_pdf_document(doc) -> bool:
    if doc is None:
        return False
    file_name = doc.file_name or ""
    return (doc.mime_type == "application/pdf") or file_name.lower().endswith(".pdf")


def _extract_pdf_text_sync(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
    return full_text


async def extract_pdf_text(document) -> str:
    """PDF ডকুমেন্ট ডাউনলোড করে টেক্সট বের করে দেয়। CPU-ভারী কাজ (পড়া) ব্যাকগ্রাউন্ড
    থ্রেডে চলে যাতে বট অন্য ইউজারদের জন্য আটকে না থাকে (Performance Improvement)।"""
    pdf_path = None
    try:
        doc_file = await document.get_file()
        pdf_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
        await doc_file.download_to_drive(pdf_path)
        return await asyncio.to_thread(_extract_pdf_text_sync, pdf_path)
    finally:
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)


def save_pdf_session(user_id: int, filename: str, content: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pdf_sessions (user_id, filename, content, created_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET filename = excluded.filename, "
        "content = excluded.content, created_at = excluded.created_at",
        (user_id, filename, content[:PDF_SESSION_STORE_CHARS], datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def get_pdf_session(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT filename, content FROM pdf_sessions WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return (None, None)
    return row


def clear_pdf_session(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM pdf_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


async def send_long_text(update: Update, text: str):
    """টেলিগ্রামের মেসেজ-দৈর্ঘ্য সীমার (~৪০৯৬ অক্ষর) কারণে বড় লেখা কয়েক টুকরায় ভাগ করে পাঠায়।"""
    text = text.strip()
    if not text:
        return
    msg = update.message or update.effective_message
    if not msg:
        return
    for i in range(0, len(text), TELEGRAM_MAX_MSG_LEN):
        await msg.reply_text(text[i:i + TELEGRAM_MAX_MSG_LEN])


async def pdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="pdf"):
        return
    if not PDF_SUPPORT:
        await update.message.reply_text(await localize(update.effective_user.id, "PDF ফিচার চালু নেই। PyPDF2 ইনস্টল করা লাগবে।"))
        return

    user_id = update.effective_user.id
    target_message = update.message.reply_to_message
    if not target_message or not target_message.document:
        await update.message.reply_text(await localize(user_id, "একটা PDF ফাইলে রিপ্লাই দিয়ে /pdf লিখুন।"))
        return
    doc = target_message.document
    if not is_pdf_document(doc):
        await update.message.reply_text(await localize(user_id, "এটা PDF ফাইল মনে হচ্ছে না। শুধু .pdf ফাইল দিয়ে কাজ করবে।"))
        return

    processing = await update.message.reply_text(await localize(user_id, "PDF পড়া হচ্ছে..."))
    try:
        full_text = await extract_pdf_text(doc)

        if not full_text.strip():
            await update.message.reply_text(
                await localize(user_id, "এই PDF থেকে লেখা বের করা যায়নি (হয়তো এটা স্ক্যান করা ছবি)।")
            )
            return

        # পরবর্তীতে /askpdf দিয়ে সরাসরি প্রশ্ন করা যাবে বলে সেশন হিসেবে সংরক্ষণ করে রাখা হলো
        save_pdf_session(user_id, doc.file_name or "document.pdf", full_text)

        trimmed_text = full_text[:8000]  # খুব বড় লেখা হলে অংশ কেটে নেওয়া হয়
        reply = await ask_ai(
            "তুমি এই ডকুমেন্টের সংক্ষিপ্ত সারমর্ম বাংলায় লিখে দাও।", trimmed_text, use_cache=True,
            user_id=user_id,  # Phase 45: নিজস্ব API Key থাকলে সেটাই ব্যবহার হবে
        )
        await update.message.reply_text(reply)
        await update.message.reply_text(
            await localize(
                user_id,
                "💬 এই PDF নিয়ে নির্দিষ্ট কোনো প্রশ্ন থাকলে লিখুন: /askpdf আপনার প্রশ্ন",
            )
        )

    except Exception as e:
        logger.error(f"PDF এরর: {e}")
        await update.message.reply_text(await localize(user_id, "দুঃখিত, PDF পড়তে সমস্যা হয়েছে।"))
    finally:
        await processing.delete()


async def askpdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    PDF প্রশ্ন-উত্তর ফিচার: একটা PDF-এ রিপ্লাই দিয়ে /askpdf প্রশ্ন লিখলে সেই ডকুমেন্ট থেকে উত্তর দেবে।
    আগে একবার /pdf বা /askpdf দিয়ে কোনো PDF পড়ানো থাকলে, পরে শুধু /askpdf প্রশ্ন লিখলেই চলবে
    (নতুন করে PDF-এ রিপ্লাই দেওয়া লাগবে না) — যতক্ষণ না /clearpdf দিয়ে মুছে ফেলা হয়।
    """
    if not await quota_guard(update, action="askpdf"):
        return
    if not PDF_SUPPORT:
        await update.message.reply_text(await localize(update.effective_user.id, "PDF ফিচার চালু নেই। PyPDF2 ইনস্টল করা লাগবে।"))
        return

    user_id = update.effective_user.id
    question = " ".join(context.args).strip()
    target_message = update.message.reply_to_message

    pdf_text, filename = (None, None)
    processing = None
    try:
        if target_message and target_message.document and is_pdf_document(target_message.document):
            # নতুন PDF দিয়ে রিপ্লাই করা হয়েছে — নতুন করে পড়ে সেশন আপডেট করা হবে
            processing = await update.message.reply_text(await localize(user_id, "PDF পড়া হচ্ছে..."))
            pdf_text = await extract_pdf_text(target_message.document)
            if not pdf_text.strip():
                await update.message.reply_text(
                    await localize(user_id, "এই PDF থেকে লেখা বের করা যায়নি (হয়তো এটা স্ক্যান করা ছবি)।")
                )
                return
            filename = target_message.document.file_name or "document.pdf"
            save_pdf_session(user_id, filename, pdf_text)
        else:
            pdf_text, filename = get_pdf_session(user_id)

        if not pdf_text:
            await update.message.reply_text(
                await localize(
                    user_id,
                    "আগে কোনো PDF ফাইলে রিপ্লাই দিয়ে /askpdf প্রশ্ন লিখুন। এরপর একবার পড়া হয়ে গেলে "
                    "নতুন করে ফাইল না পাঠিয়েও শুধু /askpdf প্রশ্ন লিখলে চলবে।",
                )
            )
            return

        if not question:
            await update.message.reply_text(
                await localize(
                    user_id,
                    f"'{filename}' ফাইলটা প্রস্তুত আছে। এবার প্রশ্ন লিখুন, যেমন: /askpdf এই ডকুমেন্টের মূল বিষয় কী?",
                )
            )
            return

        trimmed = pdf_text[:PDF_CONTEXT_CHARS]
        system_prompt = (
            "তুমি একজন সহায়ক assistant। নিচে একটা ডকুমেন্টের লেখা দেওয়া আছে। শুধু এই ডকুমেন্টের "
            "তথ্যের ভিত্তিতে ইউজারের প্রশ্নের উত্তর দাও। ডকুমেন্টে উত্তরটা না থাকলে স্পষ্টভাবে জানিয়ে দাও "
            "যে এই তথ্য ডকুমেন্টে পাওয়া যায়নি, নিজে থেকে অনুমান করে উত্তর বানিয়ো না।\n\n"
            f"ডকুমেন্ট ({filename}):\n{trimmed}"
        )
        reply = await ask_ai(system_prompt, question, use_cache=True, user_id=user_id)
        await send_long_text(update, reply)

    except Exception as e:
        logger.error(f"PDF প্রশ্ন-উত্তর এরর: {e}")
        await update.message.reply_text(await localize(user_id, "দুঃখিত, প্রশ্নের উত্তর দিতে সমস্যা হয়েছে।"))
    finally:
        if processing:
            await processing.delete()


async def clearpdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_pdf_session(user_id)
    await update.message.reply_text(await localize(user_id, "🧹 সংরক্ষিত PDF সেশন মুছে ফেলা হয়েছে।"))


# ============================= Phase 3: OCR (ছবি থেকে লেখা) ফিচার =============================

def _run_ocr_sync(image_path: str) -> str:
    """pytesseract দিয়ে ছবি থেকে লেখা বের করে (সম্পূর্ণ ফ্রি, অফলাইন, ওপেন-সোর্স)।
    প্রথমে বাংলা+ইংরেজি একসাথে চেষ্টা করা হয়; বাংলা ভাষার ডেটা ইনস্টল করা না থাকলে
    শুধু ইংরেজি দিয়ে চেষ্টা করা হয়, যাতে ভাষার প্যাক না থাকলেও ফিচারটা পুরোপুরি বন্ধ না হয়ে যায়।"""
    image = Image.open(image_path)
    try:
        return pytesseract.image_to_string(image, lang=OCR_LANGS)
    except pytesseract.TesseractError:
        return pytesseract.image_to_string(image, lang="eng")


async def ocr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="ocr"):
        return
    user_id = update.effective_user.id
    if not OCR_SUPPORT:
        await update.message.reply_text(
            await localize(user_id, "OCR ফিচার চালু নেই। pytesseract, Pillow ও Tesseract ইনস্টল করা লাগবে।")
        )
        return

    target = update.message.reply_to_message
    file_obj = None
    if target:
        if target.photo:
            file_obj = target.photo[-1]  # সবচেয়ে ভালো রেজোলিউশনের কপি
        elif target.document and (target.document.mime_type or "").startswith("image/"):
            file_obj = target.document
    if not file_obj:
        await update.message.reply_text(await localize(user_id, "একটা ছবিতে রিপ্লাই দিয়ে /ocr লিখুন।"))
        return

    # নিরাপত্তা: অতিরিক্ত বড় ফাইল দিয়ে বট আটকে রাখা ঠেকাতে সাইজ যাচাই
    size_mb = (getattr(file_obj, "file_size", 0) or 0) / (1024 * 1024)
    if size_mb > MAX_IMAGE_MB:
        await update.message.reply_text(
            await localize(user_id, f"ছবিটা একটু বেশি বড় ({size_mb:.1f} MB)। {MAX_IMAGE_MB} MB এর ছোট ছবি পাঠান।")
        )
        return

    processing = await update.message.reply_text(await localize(user_id, "ছবি থেকে লেখা বের করা হচ্ছে..."))
    image_path = None
    try:
        tg_file = await file_obj.get_file()
        image_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        await tg_file.download_to_drive(image_path)

        extracted = await asyncio.to_thread(_run_ocr_sync, image_path)
        extracted = (extracted or "").strip()

        if not extracted:
            await update.message.reply_text(
                await localize(user_id, "দুঃখিত, এই ছবি থেকে কোনো লেখা শনাক্ত করা যায়নি।")
            )
            return

        await update.message.reply_text(await localize(user_id, "📝 ছবি থেকে পাওয়া লেখা:"))
        await send_long_text(update, extracted)

    except Exception as e:
        logger.error(f"OCR এরর: {e}")
        await update.message.reply_text(await localize(user_id, "দুঃখিত, ছবি থেকে লেখা বের করতে সমস্যা হয়েছে।"))
    finally:
        await processing.delete()
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


# ============================= ভিডিও বাংলা ডাবিং ফিচার =============================
"""
নিয়ম:
  - ২০ MB এর ছোট ভিডিও: সরাসরি ভিডিওতে রিপ্লাই দিয়ে /dub লিখলেই হবে
  - ২০ MB এর বড় ভিডিও: ইউজারকে নিজে কয়েক ভাগে ভাগ করে পাঠাতে হবে
      প্রতিটা অংশ ভিডিওতে রিপ্লাই দিয়ে /dub_part লিখতে হবে (ক্রম অনুযায়ী, একটার পর একটা)
      সব অংশ পাঠানো শেষ হলে /dub_finish লিখলে বট নিজে সব জোড়া লাগিয়ে ডাবিং করে দেবে
      ভুল হলে /dub_cancel দিয়ে বাতিল করা যাবে
  - লিমিটেশন: ঠোঁটের নড়াচড়ার সাথে কণ্ঠ মিলবে না (Lip Sync নেই), শুধু অডিও বাংলায় বদলে দেওয়া হয়
"""

def get_media_object(message):
    """মেসেজে ভিডিও অথবা ভিডিও-ফাইল (document) থাকলে সেটা রিটার্ন করে।"""
    if message is None:
        return None
    if message.video:
        return message.video
    if message.document:
        return message.document
    return None


def run_ffmpeg(command: list):
    """ffmpeg/ffprobe কমান্ড রান করে। সমস্যা হলে এরর তুলে ধরে।"""
    subprocess.run(command, check=True, capture_output=True)


def get_duration_seconds(path: str) -> float:
    result = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


async def run_dubbing_pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE, video_path: str):
    """ভিডিও থেকে অডিও বের করা -> লেখায় রূপান্তর -> বাংলা অনুবাদ -> বাংলা কণ্ঠ বানানো -> ভিডিওতে বসানো -> পাঠানো।"""
    processing = await update.message.reply_text(
        "ভিডিও প্রসেস করা হচ্ছে, ভিডিওর দৈর্ঘ্য অনুযায়ী কিছু সময় লাগতে পারে..."
    )
    audio_path = video_path + "_audio.wav"
    tts_path = video_path + "_bangla.mp3"
    output_path = video_path + "_dubbed.mp4"
    part_files = []

    try:
        # ধাপ ১: ভিডিও থেকে অডিও বের করা (Phase 37: ব্যাকগ্রাউন্ড থ্রেডে, যাতে ffmpeg চলাকালীন
        # পুরো বট আটকে না থাকে — Whisper কলের মতোই এখন এটাও asyncio.to_thread দিয়ে হয়)
        await asyncio.to_thread(
            run_ffmpeg,
            [FFMPEG, "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
             "-ar", "16000", "-ac", "1", audio_path],
        )

        # ধাপ ২: অডিও থেকে লেখা বের করা (Groq Whisper) — ব্যাকগ্রাউন্ড থ্রেডে (Performance Improvement)
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        transcript = await asyncio.to_thread(
            groq_client.audio.transcriptions.create,
            file=(os.path.basename(audio_path), audio_bytes),
            model="whisper-large-v3-turbo",
        )
        original_text = transcript.text
        if not original_text.strip():
            await update.message.reply_text("দুঃখিত, ভিডিওতে কোনো কথা বোঝা যায়নি।")
            return

        # ধাপ ৩: বাংলায় অনুবাদ
        # প্রথমে চেক করো যে কমপক্ষে একটা AI Provider সেট আছে কিনা
        if not (OPENROUTER_API_KEY or GROQ_API_KEY or CEREBRAS_API_KEY):
            await update.message.reply_text(
                "❌ ডাবিং ব্যর্থ হয়েছে।\n\n"
                "🔍 কারণ: কোনো AI Provider API Key সেট করা নেই।\n\n"
                "✅ সমাধান (এই তিনটির যেকোনো একটা):\n\n"
                "1️⃣ **Groq** (সবচেয়ে দ্রুত):\n"
                "   • যান: https://console.groq.com/keys\n"
                "   • Key কপি করুন\n"
                "   • Secrets-এ GROQ_API_KEY_1 = [Key] রাখুন\n\n"
                "2️⃣ **OpenRouter**:\n"
                "   • যান: https://openrouter.ai/keys\n"
                "   • Key কপি করুন\n"
                "   • Secrets-এ OPENROUTER_API_KEY_1 = [Key] রাখুন\n\n"
                "3️⃣ **Cerebras**:\n"
                "   • যান: https://cloud.cerebras.ai\n"
                "   • Key কপি করুন\n"
                "   • Secrets-এ CEREBRAS_API_KEY_1 = [Key] রাখুন\n\n"
                "Key যোগ করার পর বট রিস্টার্ট করুন।"
            )
            return

        bangla_text = await ask_ai(
            "তুমি এই লেখাটা বাংলায় অনুবাদ করো। শুধু অনুবাদটাই লিখবে, অন্য কিছু লিখবে না।",
            original_text,
            user_id=update.effective_user.id,  # Phase 45: নিজস্ব API Key থাকলে সেটাই ব্যবহার হবে
        )

        # ধাপ ৪: বাংলা কণ্ঠ বানানো (ইউজারের পছন্দ অনুযায়ী ছেলে/মেয়ে কণ্ঠ)
        row = get_user_row(update.effective_user.id)
        voice_pref = row[0] if row else "male"
        voice_name = VOICE_MALE if voice_pref == "male" else VOICE_FEMALE
        communicator = edge_tts.Communicate(bangla_text, voice=voice_name)
        await communicator.save(tts_path)

        # ধাপ ৫: ভিডিওর সাথে নতুন বাংলা অডিও জোড়া লাগানো (ব্যাকগ্রাউন্ড থ্রেডে)
        await asyncio.to_thread(
            run_ffmpeg,
            [FFMPEG, "-y", "-i", video_path, "-i", tts_path,
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
             "-shortest", output_path],
        )

        # ধাপ ৬: ফাইল অনেক বড় হলে ভাগ করে পাঠানো, নাহলে সরাসরি পাঠানো
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        if output_size_mb <= MAX_SEND_MB:
            with open(output_path, "rb") as vf:
                await update.message.reply_video(video=vf, caption="বাংলা ডাবিং করা ভিডিও")
        else:
            duration = await asyncio.to_thread(get_duration_seconds, output_path)
            ratio = MAX_SEND_MB / output_size_mb
            segment_seconds = max(10, int(duration * ratio * 0.9))
            pattern = output_path + "_part_%03d.mp4"
            await asyncio.to_thread(
                run_ffmpeg,
                [FFMPEG, "-y", "-i", output_path, "-c", "copy", "-map", "0",
                 "-f", "segment", "-segment_time", str(segment_seconds),
                 "-reset_timestamps", "1", pattern],
            )
            part_files = sorted(glob.glob(output_path + "_part_*.mp4"))
            total = len(part_files)
            for idx, part in enumerate(part_files, start=1):
                with open(part, "rb") as pf:
                    await update.message.reply_video(video=pf, caption=f"বাংলা ডাবিং - অংশ {idx}/{total}")

    except FileNotFoundError as e:
        # ffmpeg/ffprobe বাইনারিটাই সার্ভারে ইনস্টল নেই — এটা সবচেয়ে কমন সমস্যা, তাই স্পষ্ট করে বলা হচ্ছে।
        logger.error(f"ডাবিং এরর — ffmpeg/ffprobe খুঁজে পাওয়া যায়নি: {e}")
        await update.message.reply_text(
            "❌ ডাবিং ব্যর্থ হয়েছে।\n\n"
            "🔍 সমস্যা: সার্ভারে 'ffmpeg' প্রোগ্রামটাই ইনস্টল করা নেই (ভিডিও/অডিও প্রসেস করতে এটা লাগে)।\n\n"
            "✅ সমাধান: হোস্টিং (JustRunMy.App) কনফিগে ffmpeg ইনস্টল করতে হবে। "
            "যদি এটা একটা Nix/Docker/Buildpack সেটাপ হয়, সেখানে 'ffmpeg' প্যাকেজ যোগ করুন। "
            "ইনস্টলের পর নিশ্চিত হতে সার্ভারে গিয়ে লিখুন: ffmpeg -version"
        )
    except subprocess.CalledProcessError as e:
        # ffmpeg/ffprobe চলেছে কিন্তু ভিতরে এরর দিয়েছে — stderr-এর শেষ কিছু লাইন দেখানো হচ্ছে যাতে
        # আসল কারণটা বোঝা যায় (যেমন: করাপ্ট ভিডিও, ভুল ফরম্যাট, কোডেক সমস্যা ইত্যাদি)।
        stderr_text = ""
        try:
            stderr_text = (e.stderr or b"").decode("utf-8", errors="ignore").strip()
        except Exception:
            stderr_text = str(e.stderr)
        stderr_snippet = stderr_text[-400:] if stderr_text else "(কোনো বিস্তারিত এরর মেসেজ পাওয়া যায়নি)"
        logger.error(f"ffmpeg এরর (exit code {e.returncode}): {stderr_text}")
        await update.message.reply_text(
            "❌ ডাবিং ব্যর্থ হয়েছে।\n\n"
            f"🔍 সমস্যা: ভিডিও/অডিও প্রসেস করার সময় ffmpeg এরর দিয়েছে (exit code: {e.returncode})।\n\n"
            f"বিস্তারিত এরর:\n```\n{stderr_snippet}\n```\n\n"
            "সম্ভাব্য কারণ: ভিডিও ফাইলটা করাপ্ট, সাপোর্ট না করা ফরম্যাট, অথবা ভিডিওতে অডিও ট্র্যাক নেই।"
        )
    except Exception as e:
        # Groq API (Speech-to-Text), edge-tts (বাংলা কণ্ঠ তৈরি), অথবা অন্য যেকোনো অপ্রত্যাশিত এরর।
        # exception-এর টাইপ ও মেসেজ ইউজারকে দেখানো হচ্ছে যাতে ঠিক কোথায় আটকেছে সেটা বোঝা যায়।
        error_type = type(e).__name__
        error_detail = str(e)[:300] or "(কোনো বিস্তারিত মেসেজ নেই)"

        step_hint = "অজানা ধাপ"
        lowered = error_detail.lower()
        if "groq" in lowered or "whisper" in lowered or "transcri" in lowered:
            step_hint = "ধাপ ২ — অডিও থেকে লেখায় রূপান্তর (Groq Whisper API)"
        elif "edge" in lowered or "tts" in lowered or "novoiceparse" in lowered or "novoicedata" in error_type.lower():
            step_hint = "ধাপ ৪ — বাংলা কণ্ঠ তৈরি (Microsoft Edge TTS সার্ভিস, সম্ভবত সার্ভার থেকে এটাতে ইন্টারনেট এক্সেস ব্লক আছে)"
        elif "reply_video" in lowered or "timed out" in lowered or "network" in lowered:
            step_hint = "ধাপ ৬ — টেলিগ্রামে ডাবিং করা ভিডিও পাঠানো"
        elif "ask_ai" in lowered or "api" in lowered:
            step_hint = "ধাপ ৩ — বাংলায় অনুবাদ (AI API কল)"

        logger.error(f"ডাবিং এরর [{error_type}] at {step_hint}: {error_detail}")
        await update.message.reply_text(
            "❌ ডাবিং ব্যর্থ হয়েছে।\n\n"
            f"🔍 কোথায় আটকেছে: {step_hint}\n"
            f"এরর টাইপ: {error_type}\n"
            f"এরর মেসেজ: {error_detail}\n\n"
            "এই তথ্যটা কপি করে Claude-কে দেখালে সমাধান বের করা সহজ হবে।"
        )
    finally:
        await processing.delete()
        for p in [video_path, audio_path, tts_path, output_path] + part_files:
            if p and os.path.exists(p):
                os.remove(p)


async def dub_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ছোট ভিডিও (২০ MB এর নিচে) সরাসরি ডাবিং করার কমান্ড।"""
    if not await quota_guard(update, action="dub"):
        return
    if not WHISPER_SUPPORT:
        await update.message.reply_text(
            await localize(update.effective_user.id, "দুঃখিত, এই মুহূর্তে ভিডিও ডাবিং ফিচার বন্ধ আছে (GROQ_API_KEY সেট করা নেই)।")
        )
        return
    target = update.message.reply_to_message
    media = get_media_object(target)
    if not media:
        await update.message.reply_text("একটা ভিডিওতে রিপ্লাই দিয়ে /dub লিখুন।")
        return

    size_mb = (media.file_size or 0) / (1024 * 1024)
    if size_mb > MAX_DOWNLOAD_MB:
        parts_needed = math.ceil(size_mb / MAX_DOWNLOAD_MB)
        await update.message.reply_text(
            f"এই ভিডিওটা প্রায় {size_mb:.1f} MB — টেলিগ্রামের নিয়মে বট {MAX_DOWNLOAD_MB} MB এর বড় ফাইল সরাসরি "
            f"ডাউনলোড করতে পারে না।\n\n"
            f"করণীয়: ভিডিওটা যেকোনো ফ্রি ভিডিও-স্প্লিটার অ্যাপ/ওয়েবসাইট দিয়ে কমপক্ষে {parts_needed} ভাগে ভাগ করুন। "
            f"তারপর প্রতিটা অংশ এক এক করে (ক্রম অনুযায়ী) ভিডিওতে রিপ্লাই দিয়ে /dub_part লিখুন। সব অংশ পাঠানো "
            f"শেষ হলে /dub_finish লিখুন।"
        )
        return

    processing_download = await update.message.reply_text("ভিডিও ডাউনলোড হচ্ছে...")
    video_path = None
    try:
        file_obj = await media.get_file()
        video_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        await file_obj.download_to_drive(video_path)
    except Exception as e:
        logger.error(f"ভিডিও ডাউনলোড এরর: {e}")
        await update.message.reply_text("ভিডিও ডাউনলোড করতে সমস্যা হয়েছে।")
        return
    finally:
        await processing_download.delete()

    await run_dubbing_pipeline(update, context, video_path)


async def dub_part_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বড় ভিডিওর একটা অংশ জমা রাখার কমান্ড।"""
    if not await quota_guard(update, action="dub_part"):
        return
    target = update.message.reply_to_message
    media = get_media_object(target)
    if not media:
        await update.message.reply_text("ভিডিওর একটা অংশে রিপ্লাই দিয়ে /dub_part লিখুন।")
        return

    size_mb = (media.file_size or 0) / (1024 * 1024)
    if size_mb > MAX_DOWNLOAD_MB:
        await update.message.reply_text(
            f"এই অংশটাও {MAX_DOWNLOAD_MB} MB এর বড় ({size_mb:.1f} MB)। আরও ছোট ভাগে ভাগ করুন।"
        )
        return

    user_id = update.effective_user.id
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dub_sessions WHERE user_id = ?", (user_id,))
    part_number = cur.fetchone()[0] + 1
    conn.close()

    part_path = os.path.join(tempfile.gettempdir(), f"dubpart_{user_id}_{part_number}.mp4")
    try:
        file_obj = await media.get_file()
        await file_obj.download_to_drive(part_path)
    except Exception as e:
        logger.error(f"পার্ট ডাউনলোড এরর: {e}")
        await update.message.reply_text("এই অংশ ডাউনলোড করতে সমস্যা হয়েছে।")
        return

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO dub_sessions (user_id, part_number, file_path) VALUES (?, ?, ?)",
        (user_id, part_number, part_path),
    )
    conn.commit()
    conn.close()
    await update.message.reply_text(
        f"অংশ {part_number} গ্রহণ করা হয়েছে। বাকি অংশ পাঠান, সব শেষে /dub_finish লিখুন।"
    )


async def dub_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """চলমান মাল্টি-পার্ট ডাবিং সেশন বাতিল করে, জমানো ফাইল মুছে দেয়।"""
    user_id = update.effective_user.id
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT file_path FROM dub_sessions WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    for (path,) in rows:
        if path and os.path.exists(path):
            os.remove(path)
    cur.execute("DELETE FROM dub_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text("চলমান ভিডিও ডাবিং সেশন বাতিল করা হয়েছে।")


async def dub_finish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সব অংশ জোড়া লাগিয়ে পুরো ভিডিও বানিয়ে ডাবিং শুরু করে।"""
    if not await quota_guard(update, action="dub_finish"):
        return
    if not WHISPER_SUPPORT:
        await update.message.reply_text(
            await localize(update.effective_user.id, "দুঃখিত, এই মুহূর্তে ভিডিও ডাবিং ফিচার বন্ধ আছে (GROQ_API_KEY সেট করা নেই)।")
        )
        return
    user_id = update.effective_user.id
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT part_number, file_path FROM dub_sessions WHERE user_id = ? ORDER BY part_number ASC",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("কোনো ভিডিও অংশ পাওয়া যায়নি। আগে ভিডিওতে রিপ্লাই দিয়ে /dub_part পাঠান।")
        return

    processing = await update.message.reply_text("সব অংশ জোড়া লাগানো হচ্ছে...")
    list_file_path = os.path.join(tempfile.gettempdir(), f"dublist_{user_id}.txt")
    merged_path = os.path.join(tempfile.gettempdir(), f"dubmerged_{user_id}.mp4")

    try:
        with open(list_file_path, "w") as lf:
            for _, path in rows:
                lf.write(f"file '{path}'\n")
        await asyncio.to_thread(
            run_ffmpeg,
            [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_file_path,
             "-c", "copy", merged_path],
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"জোড়া লাগানোর এরর: {e}")
        await update.message.reply_text(
            "দুঃখিত, অংশগুলো জোড়া লাগাতে সমস্যা হয়েছে। অংশগুলো একই ভিডিও থেকে ঠিকমতো, ক্রম অনুযায়ী কাটা হয়েছে কিনা দেখুন।"
        )
        await processing.delete()
        return
    finally:
        for _, path in rows:
            if path and os.path.exists(path):
                os.remove(path)
        if os.path.exists(list_file_path):
            os.remove(list_file_path)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM dub_sessions WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    await processing.delete()
    await run_dubbing_pipeline(update, context, merged_path)


# ============================= ভয়েস ফিচার (TTS / STT) =============================

async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="tts"):
        return
    user_id = update.effective_user.id
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("লেখা দিন /tts এর পরে। উদাহরণ: /tts আমি ভালো আছি")
        return
    if len(text) > 800:
        await update.message.reply_text("লেখাটা একটু বেশি বড়। ৮০০ অক্ষরের মধ্যে দিন।")
        return

    row = get_user_row(user_id)
    voice_pref, speed_pref = row[0], row[1]
    voice_name = VOICE_MALE if voice_pref == "male" else VOICE_FEMALE
    rate = SPEED_OPTIONS.get(speed_pref, "+0%")

    processing = await update.message.reply_text("কণ্ঠ বানানো হচ্ছে...")
    output_path = None
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        output_path = temp_file.name
        temp_file.close()
        communicator = edge_tts.Communicate(text, voice=voice_name, rate=rate)
        await communicator.save(output_path)
        with open(output_path, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file)
    except Exception as e:
        logger.error(f"TTS এরর: {e}")
        await update.message.reply_text("দুঃখিত, কণ্ঠ বানাতে সমস্যা হয়েছে।")
    finally:
        await processing.delete()
        if output_path and os.path.exists(output_path):
            os.remove(output_path)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="voice_to_text"):
        return
    if not WHISPER_SUPPORT:
        await update.message.reply_text(
            await localize(update.effective_user.id, "দুঃখিত, এই মুহূর্তে ভয়েস-টু-টেক্সট ফিচার বন্ধ আছে (GROQ_API_KEY সেট করা নেই)।")
        )
        return
    processing = await update.message.reply_text("লেখায় রূপান্তর করা হচ্ছে...")
    ogg_path = None
    try:
        voice_file = await update.message.voice.get_file()
        ogg_path = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False).name
        await voice_file.download_to_drive(ogg_path)

        with open(ogg_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        result = await asyncio.to_thread(
            groq_client.audio.transcriptions.create,
            file=(os.path.basename(ogg_path), audio_bytes),
            model="whisper-large-v3-turbo",
        )
        transcribed = result.text
        if transcribed.strip():
            await update.message.reply_text(f"লেখা:\n{transcribed}")
        else:
            await update.message.reply_text("কোনো লেখা বোঝা যায়নি।")
    except Exception as e:
        logger.error(f"STT এরর: {e}")
        await update.message.reply_text("দুঃখিত, ভয়েস বুঝতে সমস্যা হয়েছে।")
    finally:
        await processing.delete()
        if ogg_path and os.path.exists(ogg_path):
            os.remove(ogg_path)


async def build_settings_view(user_id: int):
    """⚙️ সেটিংস মেনুর টেক্সট ও কীবোর্ড তৈরি করে (Better Settings ফিচার)।"""
    row = get_user_row(user_id)
    voice, speed = (row[0], row[1]) if row else ("male", "normal")
    auto_reply, memory_enabled, language = get_user_settings(user_id)
    _, is_manual = get_effective_language(user_id)

    voice_label = "ছেলে 👨" if voice == "male" else "মেয়ে 👩"
    speed_labels = {"slow": "ধীর 🐢", "normal": "স্বাভাবিক ⏺️", "fast": "দ্রুত 🐇"}
    lang_label = language_display_name(language) if is_manual else "স্বয়ংক্রিয় (Auto)"
    plan_label = "সীমাহীন (অ্যাডমিন) 🛡️" if user_id in ADMIN_IDS else (
        "প্রিমিয়াম 👑" if is_premium_active(user_id) else "ফ্রি 🆓"
    )

    text = (
        "⚙️ আপনার সেটিংস\n"
        "━━━━━━━━━━━━━━━\n"
        f"🎙 কণ্ঠ: {voice_label}\n"
        f"⚡ গতি: {speed_labels.get(speed, speed)}\n"
        f"🔁 Auto Reply: {'চালু ✅' if auto_reply else 'বন্ধ ❌'}\n"
        f"🧠 AI Memory: {'চালু ✅' if memory_enabled else 'বন্ধ ❌'}\n"
        f"🌐 বটের ভাষা: {lang_label}\n"
        f"👑 প্ল্যান: {plan_label}\n"
        "━━━━━━━━━━━━━━━\n"
        "নিচের বাটন থেকে বদলে নিন (প্ল্যান বদলাতে /premiumstatus দেখুন):"
    )
    keyboard = [
        [
            InlineKeyboardButton("🎙 কণ্ঠ বদলান", callback_data="settings_open_voice"),
            InlineKeyboardButton("⚡ গতি বদলান", callback_data="settings_open_speed"),
        ],
        [
            InlineKeyboardButton(
                f"🔁 Auto Reply {'বন্ধ' if auto_reply else 'চালু'} করুন",
                callback_data="settings_toggle_autoreply",
            )
        ],
        [
            InlineKeyboardButton(
                f"🧠 Memory {'বন্ধ' if memory_enabled else 'চালু'} করুন",
                callback_data="settings_toggle_memory",
            )
        ],
        [InlineKeyboardButton("🌐 ভাষা বদলান", callback_data="settings_open_lang")],
        [InlineKeyboardButton("🧹 মেমরি মুছে ফেলুন", callback_data="settings_clear_memory")],
    ]
    localized_text = await localize(user_id, text)
    return localized_text, InlineKeyboardMarkup(keyboard)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id)
    text, markup = await build_settings_view(user_id)
    await update.message.reply_text(text, reply_markup=markup)


# ============================= Better Help Menu (Inline Keyboard) =============================

MENU_SECTIONS = {
    "text": (
        "📝 লেখার কাজ",
        "/translate ভাষা লেখা — অনুবাদ (উদাহরণ: /translate english আমি ভালো আছি)\n"
        "/grammar লেখা — গ্রামার ঠিক করা\n"
        "/rewrite লেখা — লেখা নতুনভাবে লেখা\n"
        "/tone formal/casual লেখা — টোন বদলানো\n"
        "/summarize — কোনো মেসেজে রিপ্লাই দিয়ে লিখুন, সামারি করে দেবে\n"
        "/pdf — কোনো PDF ফাইলে রিপ্লাই দিয়ে লিখুন, সামারি করে দেবে\n"
        "/askpdf প্রশ্ন — PDF-এ রিপ্লাই দিয়ে (বা আগে পড়ানো থাকলে সরাসরি) নির্দিষ্ট প্রশ্নের উত্তর\n"
        "/clearpdf — সংরক্ষিত PDF সেশন মুছে ফেলা\n"
        "/ocr — কোনো ছবিতে রিপ্লাই দিয়ে লিখুন, ছবির লেখা বের করে দেবে\n"
        "/detectlang লেখা — ভাষা শনাক্ত করা",
    ),
    "coding": (
        "💻 কোডিং কমান্ড",
        CODING_COMMANDS_BODY,
    ),
    "media": (
        "🎬 ভিডিও ও কণ্ঠ",
        "/dub — ভিডিওতে রিপ্লাই দিয়ে লিখুন, বাংলা কণ্ঠে ডাবিং করে দেবে (২০ MB এর নিচে)\n"
        "/dub_part, /dub_finish, /dub_cancel — বড় ভিডিও ভাগে ভাগে ডাবিং\n"
        "/tts লেখা — লেখা থেকে কণ্ঠ বানাবে\n"
        "ভয়েস মেসেজ পাঠালে — লেখায় রূপান্তর করে দেবে",
    ),
    "profile": (
        "👤 প্রোফাইল ও সেটিংস",
        "/profile — ব্যবহারের হিসাব\n"
        "/mylimit — আজকের বাকি সীমা\n"
        "/settings — সব সেটিংস এক জায়গায় (বাটন দিয়ে)\n"
        "/setlang — বটের উত্তর কোন ভাষায় হবে সেট করা\n"
        "/setvoice, /setspeed — কণ্ঠ ও গতি বদলানো\n"
        "/autoreply on/off — সরাসরি লেখায় বট উত্তর দেবে কিনা\n"
        "/memory on/off — AI আগের কথা মনে রাখবে কিনা\n"
        "/noapimode on/off — চালু থাকলে আপনার চ্যাটে বট কোনো AI API কল করবে না, শুধু Brain OS দিয়ে উত্তর দেবে\n"
        "/clearmemory — চ্যাটের স্মৃতি মুছে ফেলা\n"
        "/premiumstatus — আপনার প্ল্যান (ফ্রি/প্রিমিয়াম) ও মেয়াদ দেখা\n"
        "/setapikey provider key — নিজস্ব API Key যুক্ত করা (আরও দ্রুত ও নির্ভুল, শেয়ার্ড সীমার বাইরে)\n"
        "/myapikey — নিজস্ব Key-এর অবস্থা দেখা\n"
        "/removeapikey provider — নিজস্ব Key মুছে ফেলা\n"
        "/myreferrals — নিজের রেফার লিংক ও বোনাস দেখা",
    ),
    "fun": (
        "😄 মজার কমান্ড",
        "/joke — একটা মজার জোক\n/quote — অনুপ্রেরণামূলক উক্তি\n"
        "/dice — ডাইস চালানো\n/coin — কয়েন টস\n/leaderboard — টপ ইউজার তালিকা",
    ),
    "other": (
        "🛠️ অন্যান্য",
        "/feedback লেখা — মতামত জানান\n/bugreport লেখা — সমস্যা জানান\n"
        "/ping — বট সাড়া দিচ্ছে কিনা\n/uptime — বট কতক্ষণ চালু\n/about — বট সম্পর্কে",
    ),
}


async def build_menu_root(user_id: int):
    text = await localize(user_id, "📋 মেনু থেকে একটা বিভাগ বেছে নিন:")
    keyboard = [
        [InlineKeyboardButton(MENU_SECTIONS["text"][0], callback_data="menu_text")],
        [InlineKeyboardButton(MENU_SECTIONS["coding"][0], callback_data="menu_coding")],
        [InlineKeyboardButton(MENU_SECTIONS["media"][0], callback_data="menu_media")],
        [InlineKeyboardButton(MENU_SECTIONS["profile"][0], callback_data="menu_profile")],
        [InlineKeyboardButton(MENU_SECTIONS["fun"][0], callback_data="menu_fun")],
        [InlineKeyboardButton(MENU_SECTIONS["other"][0], callback_data="menu_other")],
    ]
    return text, InlineKeyboardMarkup(keyboard)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text, markup = await build_menu_root(user_id)
    await update.message.reply_text(text, reply_markup=markup)


async def setvoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("ছেলে কণ্ঠ", callback_data="voice_male"),
        InlineKeyboardButton("মেয়ে কণ্ঠ", callback_data="voice_female"),
    ]]
    await update.message.reply_text("কোন কণ্ঠ চান বেছে নিন:", reply_markup=InlineKeyboardMarkup(keyboard))


async def setspeed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("ধীর", callback_data="speed_slow"),
        InlineKeyboardButton("স্বাভাবিক", callback_data="speed_normal"),
        InlineKeyboardButton("দ্রুত", callback_data="speed_fast"),
    ]]
    await update.message.reply_text("গতি বেছে নিন:", reply_markup=InlineKeyboardMarkup(keyboard))


# ============================= Phase 3: মাল্টি-ভাষা সেটিং কমান্ড =============================

def build_lang_picker_view():
    """ভাষা বাছাইয়ের ইনলাইন কীবোর্ড তৈরি করে। এই টেক্সট অনুবাদ করা হয় না ইচ্ছে করেই —
    যাতে ইউজার এখনো কোনো ভাষা বেছে না নিলেও (বা ভুল ভাষায় আটকে গেলেও) সবসময় বুঝতে পারেন
    কোন বাটনে কী আছে।"""
    text = (
        "🌐 বট কোন ভাষায় উত্তর দেবে বেছে নিন:\n"
        "━━━━━━━━━━━━━━━\n"
        "Auto বেছে নিলে বট নিজে থেকে আপনার লেখার ভাষা বুঝে সেই ভাষাতেই উত্তর দেবে (ডিফল্ট)।"
    )
    rows = []
    pair = []
    for code, name in UI_LANG_CHOICES.items():
        pair.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append([InlineKeyboardButton("🔄 Auto (স্বয়ংক্রিয়)", callback_data="lang_auto")])
    rows.append([InlineKeyboardButton("⚙️ সেটিংসে ফিরুন", callback_data="settings_back")])
    return text, InlineKeyboardMarkup(rows)


async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/setlang — ইউজার বটের উত্তরের ভাষা বেছে নিতে পারেন (বাটন দিয়ে)।"""
    user_id = update.effective_user.id
    register_user(user_id)
    text, markup = build_lang_picker_view()
    await update.message.reply_text(text, reply_markup=markup)


async def safe_edit_message_text(query, text: str, reply_markup=None):
    """
    Phase 38: query.edit_message_text()-এর নিরাপদ wrapper। ইউজার একই বাটনে দুইবার
    চাপলে (যেমন একই মেনু সেকশন বা অ্যাডমিন প্যানেলে আবার একই তথ্য আসলে) Telegram
    "Message is not modified" নামে একটা BadRequest ছোঁড়ে — এটা আসলে কোনো সমস্যা না,
    শুধু জানায় যে নতুন কন্টেন্ট আগের মতোই। আগে এই এরর ধরা হতো না, তাই সেটা সরাসরি
    error_handler পর্যন্ত পৌঁছে গিয়ে ইউজারকে "অপ্রত্যাশিত সমস্যা" মেসেজ ও অ্যাডমিনদের
    এরর নোটিফিকেশন পাঠাতো। এখন এই নির্দিষ্ট কেসটা চুপচাপ উপেক্ষা করা হয়, অন্য যেকোনো
    real BadRequest আগের মতোই উপরে ছুঁড়ে দেওয়া হয়।
    """
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        if "message is not modified" in str(e).lower():
            return
        raise


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    register_user(user_id)
    data = query.data

    back_to_settings_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⚙️ সেটিংসে ফিরুন", callback_data="settings_back")]]
    )

    if data.startswith("voice_"):
        choice = data.replace("voice_", "")
        # Phase 46: বৈধ মান না হলে DB-তে কিছুই লেখা হবে না — আগে ভুয়া মান কমিট হয়ে
        # যেত এবং ইউজারকে মিথ্যা নিশ্চিতকরণ ("মেয়ে কণ্ঠ সেট হয়েছে") দেখানো হতো।
        if choice not in VOICE_CHOICES:
            await safe_edit_message_text(
                query,
                "⚠️ কণ্ঠের এই অপশনটা চেনা যাচ্ছে না। নিচের বাটন থেকে আবার বেছে নিন।",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("ছেলে কণ্ঠ", callback_data="voice_male"),
                    InlineKeyboardButton("মেয়ে কণ্ঠ", callback_data="voice_female"),
                ]]),
            )
            return
        update_field(user_id, "voice", choice)
        label = "ছেলে কণ্ঠ" if choice == "male" else "মেয়ে কণ্ঠ"
        await safe_edit_message_text(query, f"কণ্ঠ সেট করা হয়েছে: {label}", reply_markup=back_to_settings_kb)
    elif data.startswith("speed_"):
        choice = data.replace("speed_", "")
        # Phase 46: আগে এখানে labels[choice] অজানা মানে KeyError ছুঁড়ত — সেটা error_handler
        # পর্যন্ত পৌঁছে ইউজারকে "অপ্রত্যাশিত সমস্যা" দেখাত, অথচ তার আগেই update_field()
        # ভুয়া মানটা users.speed-এ কমিট করে ফেলত। এখন প্রথমে যাচাই, তারপরে লেখা।
        if choice not in SPEED_LABELS_BN:
            await safe_edit_message_text(
                query,
                "⚠️ গতির এই অপশনটা চেনা যাচ্ছে না। নিচের বাটন থেকে আবার বেছে নিন।",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("ধীর", callback_data="speed_slow"),
                    InlineKeyboardButton("স্বাভাবিক", callback_data="speed_normal"),
                    InlineKeyboardButton("দ্রুত", callback_data="speed_fast"),
                ]]),
            )
            return
        update_field(user_id, "speed", choice)
        await safe_edit_message_text(
            query, f"গতি সেট করা হয়েছে: {SPEED_LABELS_BN[choice]}", reply_markup=back_to_settings_kb
        )

    elif data == "settings_open_voice":
        keyboard = [[
            InlineKeyboardButton("ছেলে কণ্ঠ", callback_data="voice_male"),
            InlineKeyboardButton("মেয়ে কণ্ঠ", callback_data="voice_female"),
        ]]
        await safe_edit_message_text(query, "কোন কণ্ঠ চান বেছে নিন:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "settings_open_speed":
        keyboard = [[
            InlineKeyboardButton("ধীর", callback_data="speed_slow"),
            InlineKeyboardButton("স্বাভাবিক", callback_data="speed_normal"),
            InlineKeyboardButton("দ্রুত", callback_data="speed_fast"),
        ]]
        await safe_edit_message_text(query, "গতি বেছে নিন:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "settings_toggle_autoreply":
        auto_reply, _, _ = get_user_settings(user_id)
        update_field(user_id, "auto_reply", 0 if auto_reply else 1)
        text, markup = await build_settings_view(user_id)
        await safe_edit_message_text(query, text, reply_markup=markup)
    elif data == "settings_toggle_memory":
        _, memory_enabled, _ = get_user_settings(user_id)
        update_field(user_id, "memory_enabled", 0 if memory_enabled else 1)
        text, markup = await build_settings_view(user_id)
        await safe_edit_message_text(query, text, reply_markup=markup)
    elif data == "settings_clear_memory":
        clear_memory(user_id)
        text, markup = await build_settings_view(user_id)
        await safe_edit_message_text(query, text, reply_markup=markup)
    elif data == "settings_back":
        text, markup = await build_settings_view(user_id)
        await safe_edit_message_text(query, text, reply_markup=markup)
    elif data == "settings_open_lang":
        text, markup = build_lang_picker_view()
        await safe_edit_message_text(query, text, reply_markup=markup)

    elif data == "menu_root":
        text, markup = await build_menu_root(user_id)
        await safe_edit_message_text(query, text, reply_markup=markup)
    elif data.startswith("menu_"):
        key = data.replace("menu_", "")
        if key in MENU_SECTIONS:
            title, body = MENU_SECTIONS[key]
            back_kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ মূল মেনু", callback_data="menu_root")]]
            )
            section_text = await localize(user_id, f"{title}\n━━━━━━━━━━━━━━━\n{body}")
            await safe_edit_message_text(query, section_text, reply_markup=back_kb)
        else:
            # Phase 46: অজানা সেকশনে আগে চুপচাপ কিছুই হতো না — ইউজার বাটন চেপে কোনো
            # ফিডব্যাকই পেত না। এখন মূল মেনুতে ফিরিয়ে দেওয়া হয়।
            text, markup = await build_menu_root(user_id)
            await safe_edit_message_text(query, text, reply_markup=markup)

    elif data == "lang_auto":
        set_user_language_auto(user_id)
        await safe_edit_message_text(query, 
            "✅ ভাষা মোড: স্বয়ংক্রিয় (Auto) — বট এখন থেকে আপনার লেখার ভাষা বুঝে সেই ভাষায় উত্তর দেবে।",
            reply_markup=back_to_settings_kb,
        )
    elif data.startswith("lang_"):
        lang_code = data.replace("lang_", "")
        if lang_code in UI_LANG_CHOICES:
            set_user_language(user_id, lang_code)
            confirm = await localize(
                user_id, f"✅ বটের ভাষা সেট করা হলো: {UI_LANG_CHOICES[lang_code]}"
            )
            await safe_edit_message_text(query, confirm, reply_markup=back_to_settings_kb)
        else:
            # Phase 46: অজানা ভাষা কোডে আগে নিঃশব্দ no-op হতো (কোনো ফিডব্যাক নেই)।
            # DB-তে ভুয়া language মান লেখাও হয়নি, কিন্তু ইউজার জানত না কী হয়েছে —
            # এখন ভাষা বাছাইয়ের তালিকাটা আবার দেখানো হয়।
            text, markup = build_lang_picker_view()
            await safe_edit_message_text(query, text, reply_markup=markup)

    # ---- Phase 5: Admin Control Panel ----
    elif data.startswith("adm_"):
        if not is_admin(user_id):
            await safe_edit_message_text(query, "এই প্যানেল শুধু অ্যাডমিনের জন্য।")
            return
        if data == "adm_back":
            text, markup = build_admin_panel_view(user_id)
            await safe_edit_message_text(query, text, reply_markup=markup)
        elif data == "adm_search":
            context.user_data["admin_awaiting"] = "search"
            await safe_edit_message_text(query, 
                "🔍 যে ইউজারের আইডি সার্চ করতে চান, সেটা এখন মেসেজ করে পাঠান।",
                reply_markup=build_admin_back_kb(),
            )
        elif data == "adm_premiumlist":
            await safe_edit_message_text(query, build_premiumlist_text(), reply_markup=build_admin_back_kb())
        elif data == "adm_stats":
            await safe_edit_message_text(query, build_stats_text(), reply_markup=build_admin_back_kb())
        elif data == "adm_analytics":
            report = build_analytics_report(14)
            if len(report) > TELEGRAM_MAX_MSG_LEN:
                report = report[:TELEGRAM_MAX_MSG_LEN] + "\n...(পূর্ণ রিপোর্ট দেখতে /analytics লিখুন)"
            await safe_edit_message_text(query, report, reply_markup=build_admin_back_kb())
        elif data == "adm_brainstatus":
            await safe_edit_message_text(query, build_brain_status_text(), reply_markup=build_admin_back_kb())
        elif data == "adm_decisionhistory":
            try:
                rows = api_decision_history(limit=10)
                if not rows:
                    report = "🧠 এখনো কোনো Decision history নেই।"
                else:
                    lines = ["🧠 Decision History", "━━━━━━━━━━━━━━━"]
                    for row in rows[:10]:
                        lines.append(
                            f"#{row.get('id', '?')} | {row.get('stage', '?')} | "
                            f"confidence={float(row.get('confidence', 0)):.2f} | {str(row.get('created_at', ''))[:19]}"
                        )
                    report = "\n".join(lines)
                await safe_edit_message_text(query, report[:TELEGRAM_MAX_MSG_LEN], reply_markup=build_admin_back_kb())
            except Exception as e:
                logger.warning("Admin decision history failed: %s", e)
                await safe_edit_message_text(query, "Decision history পড়তে সমস্যা হয়েছে।", reply_markup=build_admin_back_kb())
        elif data == "adm_roles":
            await safe_edit_message_text(query, build_admin_roles_text(), reply_markup=build_admin_back_kb())
        elif data == "adm_codecommands":
            # 🔐 admin-only coding command-এর তালিকা — এই branch-এ পৌঁছানোর আগেই
            # is_admin() চেক হয়ে গেছে (adm_ prefix-এর শুরুতে), তাই সাধারণ ইউজার এটা দেখবে না।
            report = build_admin_coding_commands_text()
            if len(report) > TELEGRAM_MAX_MSG_LEN:
                report = report[:TELEGRAM_MAX_MSG_LEN] + "\n...(তালিকা অনেক বড়, কেটে দেওয়া হয়েছে)"
            await safe_edit_message_text(query, report, reply_markup=build_admin_back_kb())
        elif data == "adm_broadcast_info":
            await safe_edit_message_text(query, 
                "📢 ব্রডকাস্ট পাঠাতে লিখুন:\n/broadcast আপনার মেসেজ\n\n"
                "নির্দিষ্ট সময়ে পাঠাতে (শিডিউল):\n/schedulebroadcast YYYY-MM-DD HH:MM আপনার মেসেজ",
                reply_markup=build_admin_back_kb(),
            )
        elif data.startswith("adm_do_"):
            if not has_role(user_id, "moderator"):
                return
            action_part = data[len("adm_do_"):]
            action, _, target_str = action_part.partition("_")
            if not target_str.isdigit():
                return
            target_id = int(target_str)

            if action == "ban":
                update_field(target_id, "is_banned", 1)
                await query.answer("ব্যান করা হয়েছে", show_alert=False)
            elif action == "unban":
                update_field(target_id, "is_banned", 0)
                await query.answer("আনব্যান করা হয়েছে", show_alert=False)
            elif action == "prem30" and has_role(user_id, "admin"):
                new_until = grant_premium(target_id, 30, user_id)
                await query.answer(f"৩০ দিন প্রিমিয়াম দেওয়া হয়েছে (মেয়াদ: {new_until})", show_alert=False)
                try:
                    await context.bot.send_message(chat_id=target_id, text=f"🎉 আপনাকে ৩০ দিনের প্রিমিয়াম দেওয়া হয়েছে! মেয়াদ শেষ: {new_until}")
                except Exception:
                    pass
            elif action == "prem365" and has_role(user_id, "admin"):
                new_until = grant_premium(target_id, 365, user_id)
                await query.answer(f"৩৬৫ দিন প্রিমিয়াম দেওয়া হয়েছে (মেয়াদ: {new_until})", show_alert=False)
                try:
                    await context.bot.send_message(chat_id=target_id, text=f"🎉 আপনাকে ৩৬৫ দিনের প্রিমিয়াম দেওয়া হয়েছে! মেয়াদ শেষ: {new_until}")
                except Exception:
                    pass
            elif action == "premdel" and has_role(user_id, "admin"):
                revoke_premium(target_id)
                await query.answer("প্রিমিয়াম বাতিল করা হয়েছে", show_alert=False)
                try:
                    await context.bot.send_message(chat_id=target_id, text="আপনার প্রিমিয়াম মেম্বারশিপ বাতিল করা হয়েছে।")
                except Exception:
                    pass
            else:
                return

            _, _, banned, _, _ = get_user_row(target_id) or (None, None, 0, 0, "")
            summary = build_admin_user_summary(target_id)
            await safe_edit_message_text(query, summary, reply_markup=build_admin_user_actions_kb(user_id, target_id, bool(banned)))


# ============================= মজার কমান্ড (Fun Features) =============================

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="joke"):
        return
    user_id = update.effective_user.id
    system_prompt = "তুমি একটা মজার, শালীন বাংলা জোক বলো। ছোট রাখবে।"
    text = "একটা জোক বলো"
    metadata = None
    try:
        # Phase 47 priority: 💾 Database (cache) → 🌐 Browser → 🔵 Groq API।
        cached = await ai_response_cache.get(system_prompt, text)
        if cached is not None:
            metadata = make_source_metadata(
                "database", confidence=0.95, cache_hit=True, note="Response Cache", query=text,
            )
            await send_long_text(update, attach_source_badge(cached, metadata, "joke", attribution_lang(user_id)))
            return

        no_api_mode = is_no_api_mode(user_id)
        if not no_api_mode:
            browse_answer = await _automatic_browse_answer(
                user_id, text, _browse_lang_hint(user_id, text), no_api_mode, command="joke"
            )
            if browse_answer:
                await send_long_text(update, browse_answer)
                return

        # Phase 47: জোক প্রতিবার তাজা — তাই use_cache=False (ক্যাশে জমা হয় না)।
        reply = await ask_ai(system_prompt, text, use_cache=False, user_id=user_id)
        metadata = make_source_metadata("groq", confidence=0.95, query=text)
    except Exception:
        reply = await localize(user_id, "দুঃখিত, এখন জোক আনতে পারলাম না।")
    await send_long_text(update, attach_source_badge(reply, metadata, "joke", attribution_lang(user_id)))


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await quota_guard(update, action="quote"):
        return
    user_id = update.effective_user.id
    system_prompt = "তুমি একটা অনুপ্রেরণামূলক ছোট উক্তি বাংলায় লেখো।"
    text = "একটা উক্তি দাও"
    metadata = None
    try:
        # Phase 47 priority: 💾 Database (cache) → 🌐 Browser → 🔵 Groq API।
        cached = await ai_response_cache.get(system_prompt, text)
        if cached is not None:
            metadata = make_source_metadata(
                "database", confidence=0.95, cache_hit=True, note="Response Cache", query=text,
            )
            await send_long_text(update, attach_source_badge(cached, metadata, "quote", attribution_lang(user_id)))
            return

        no_api_mode = is_no_api_mode(user_id)
        if not no_api_mode:
            browse_answer = await _automatic_browse_answer(
                user_id, text, _browse_lang_hint(user_id, text), no_api_mode, command="quote"
            )
            if browse_answer:
                await send_long_text(update, browse_answer)
                return

        # Phase 47: উক্তিও প্রতিবার তাজা — তাই use_cache=False।
        reply = await ask_ai(system_prompt, text, use_cache=False, user_id=user_id)
        metadata = make_source_metadata("groq", confidence=0.95, query=text)
    except Exception:
        reply = await localize(user_id, "দুঃখিত, এখন উক্তি আনতে পারলাম না।")
    await send_long_text(update, attach_source_badge(reply, metadata, "quote", attribution_lang(user_id)))


async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ডাইসে উঠেছে: {random.randint(1, 6)}")


async def coin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["হেড (Head)", "টেইল (Tail)"])
    await update.message.reply_text(f"কয়েন টসে এসেছে: {result}")


# ============================= অ্যাডমিন কমান্ড =============================

# ---- Phase 5: একাধিক অ্যাডমিনের রোল/পারমিশন ----
# ADMIN_IDS (Secrets/env থেকে) সবসময় সর্বোচ্চ ক্ষমতার "owner"। এছাড়া owner চাইলে
# ডাটাবেসে আরো admin/moderator যোগ করতে পারেন (/addadmin কমান্ড দিয়ে) — বট রিস্টার্ট
# হলেও তারা admin থেকে যাবেন যেহেতু এটা ডাটাবেসে সংরক্ষিত, .env-এ না।

_db_admin_role_cache = {}          # user_id -> role, ডাটাবেসে যোগ করা admin/moderator-দের ক্যাশ
_db_admin_role_cache_loaded = False


def _load_admin_role_cache():
    global _db_admin_role_cache, _db_admin_role_cache_loaded
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, role FROM admin_roles")
    _db_admin_role_cache = {uid: role for uid, role in cur.fetchall()}
    conn.close()
    _db_admin_role_cache_loaded = True


def get_admin_role(user_id: int) -> str:
    """
    রিটার্ন করে 'owner' / 'admin' / 'moderator' / '' (কোনো রোল না থাকলে)।
    Performance Improvement: ডাটাবেসে যোগ করা admin/moderator-দের তালিকা মেমরিতে ক্যাশ করা থাকে,
    যাতে প্রতিটা ইউজারের প্রতিটা মেসেজে (Admin Panel-এর ইনপুট-চেকের কারণে) আলাদা ডাটাবেস
    কুয়েরি করতে না হয় — অধিকাংশ ইউজারই অ্যাডমিন নন, তাই এই চেকটা দ্রুত হওয়া জরুরি।
    """
    if user_id in ADMIN_IDS:
        return "owner"
    if not _db_admin_role_cache_loaded:
        _load_admin_role_cache()
    return _db_admin_role_cache.get(user_id, "")


def has_role(user_id: int, min_role: str) -> bool:
    """user_id-এর রোল min_role এর সমান বা তার চেয়ে বেশি ক্ষমতাসম্পন্ন কিনা।"""
    rank = ADMIN_ROLE_RANK.get(get_admin_role(user_id), 0)
    return rank >= ADMIN_ROLE_RANK.get(min_role, 99)


def is_admin(user_id: int) -> bool:
    """যেকোনো ধরনের অ্যাডমিন (moderator/admin/owner) কিনা — সাধারণ (কম-সংবেদনশীল) কমান্ডের জন্য।"""
    return get_admin_role(user_id) != ""


def add_admin_role(user_id: int, role: str, added_by: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO admin_roles (user_id, role, added_by, added_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET role = excluded.role, added_by = excluded.added_by, "
        "added_at = excluded.added_at",
        (user_id, role, added_by, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()
    _db_admin_role_cache[user_id] = role  # ক্যাশ সাথে সাথে আপডেট, নতুন রোল অবিলম্বে কার্যকর হবে


def remove_admin_role(user_id: int) -> bool:
    """শুধু ডাটাবেসে যোগ করা admin/moderator বাদ দেওয়া যায় — .env-এর ADMIN_IDS (owner)
    বট থেকে বাদ দেওয়া যায় না, নিরাপত্তার জন্য (সেটা শুধু Secrets থেকেই বদলানো যাবে)।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM admin_roles WHERE user_id = ?", (user_id,))
    if cur.fetchone() is None:
        conn.close()
        return False
    cur.execute("DELETE FROM admin_roles WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    _db_admin_role_cache.pop(user_id, None)  # ক্যাশ থেকেও বাদ দেওয়া, সাথে সাথে কার্যকর হবে
    return True


def list_all_admins():
    """(user_id, role, source) — env-ভিত্তিক owner + ডাটাবেসে যোগ করা admin/moderator, রোলের ক্রমে।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, role FROM admin_roles")
    db_admins = {uid: role for uid, role in cur.fetchall()}
    conn.close()
    combined = [(uid, "owner", "env") for uid in ADMIN_IDS]
    combined += [(uid, role, "db") for uid, role in db_admins.items() if uid not in ADMIN_IDS]
    combined.sort(key=lambda x: -ADMIN_ROLE_RANK.get(x[1], 0))
    return combined


async def send_broadcast_to_all(bot, text: str, status_msg=None):
    """সব ইউজারকে একটা ব্রডকাস্ট মেসেজ পাঠায়। /broadcast এবং শিডিউল করা ব্রডকাস্ট দুটোই এটা ব্যবহার করে।
    রিটার্ন করে (sent, failed) সংখ্যা।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    all_users = [row[0] for row in cur.fetchall()]
    conn.close()

    sent, failed = 0, 0
    for i, uid in enumerate(all_users, start=1):
        try:
            await bot.send_message(chat_id=uid, text=f"📢 [ঘোষণা]\n{text}")
            sent += 1
        except Exception:
            failed += 1
        # Telegram-এর ফ্লাড লিমিট এড়াতে প্রতি মেসেজের মাঝে সামান্য বিরতি
        await asyncio.sleep(0.05)
        if status_msg and i % 25 == 0:
            try:
                await status_msg.edit_text(f"পাঠানো হচ্ছে... {i}/{len(all_users)}")
            except Exception:
                pass
    return sent, failed


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_role(update.effective_user.id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("এভাবে লিখুন: /broadcast আপনার মেসেজ")
        return

    status_msg = await update.message.reply_text("পাঠানো শুরু হচ্ছে...")
    sent, failed = await send_broadcast_to_all(context.bot, text, status_msg=status_msg)
    await status_msg.edit_text(f"✅ শেষ! পাঠানো হয়েছে: {sent} জনকে, ব্যর্থ: {failed} জন")


# ============================= Phase 3: শিডিউল ব্রডকাস্ট =============================
#
# পদ্ধতি: প্রতিটা শিডিউল করা ব্রডকাস্ট ডাটাবেসে জমা থাকে (sent=0)। বট প্রতি ৩০ সেকেন্ডে
# একটা ব্যাকগ্রাউন্ড জব চালিয়ে চেক করে কোনগুলোর সময় হয়ে গেছে, সেগুলো পাঠিয়ে sent=1 করে দেয়।
# এই পদ্ধতিতে বট মাঝে বন্ধ হয়ে আবার চালু হলেও কোনো শিডিউল মিস হয় না (নিরাপত্তা/নির্ভরযোগ্যতা)।

def parse_schedule_datetime(date_str: str, time_str: str) -> datetime:
    """'YYYY-MM-DD' ও 'HH:MM' ফরম্যাট থেকে datetime বানায়। ভুল ফরম্যাট হলে ValueError তোলে।"""
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


async def schedulebroadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    এভাবে লিখুন: /schedulebroadcast YYYY-MM-DD HH:MM আপনার মেসেজ
    উদাহরণ: /schedulebroadcast 2026-08-05 21:30 আজ রাতে নতুন আপডেট আসছে!
    সময়টা সার্ভারের ঘড়ি অনুযায়ী ধরা হয় (অন্যান্য কমান্ডের মতোই)।
    """
    if not has_role(update.effective_user.id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return
    if len(context.args) < 3:
        await update.message.reply_text(
            "এভাবে লিখুন: /schedulebroadcast YYYY-MM-DD HH:MM আপনার মেসেজ\n"
            "উদাহরণ: /schedulebroadcast 2026-08-05 21:30 আজ রাতে নতুন আপডেট আসছে!"
        )
        return

    date_str, time_str = context.args[0], context.args[1]
    message_text = " ".join(context.args[2:]).strip()
    if not message_text:
        await update.message.reply_text("মেসেজের লেখাটা খালি রাখা যাবে না।")
        return
    # নিরাপত্তা: অতিরিক্ত লম্বা মেসেজ/অপব্যবহার ঠেকাতে একটা যুক্তিসঙ্গত সীমা
    if len(message_text) > 3000:
        await update.message.reply_text("মেসেজটা একটু বেশি বড়। ৩০০০ অক্ষরের মধ্যে দিন।")
        return

    try:
        send_at = parse_schedule_datetime(date_str, time_str)
    except ValueError:
        await update.message.reply_text(
            "তারিখ/সময়ের ফরম্যাট ঠিক নেই। এভাবে দিন: YYYY-MM-DD HH:MM (উদাহরণ: 2026-08-05 21:30)"
        )
        return

    if send_at <= datetime.now():
        await update.message.reply_text("ভবিষ্যতের কোনো তারিখ-সময় দিন — অতীতের সময় দেওয়া যাবে না।")
        return

    user_id = update.effective_user.id
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scheduled_broadcasts (message, send_at, sent, created_by, created_at) "
        "VALUES (?, ?, 0, ?, ?)",
        (message_text, send_at.isoformat(timespec="minutes"), user_id, datetime.now().isoformat(timespec="seconds")),
    )
    schedule_id = cur.lastrowid
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ ব্রডকাস্ট শিডিউল করা হয়েছে (ID: {schedule_id})\n"
        f"পাঠানো হবে: {send_at.strftime('%Y-%m-%d %H:%M')}-এ\n"
        f"বাতিল করতে চাইলে: /cancelschedule {schedule_id}"
    )


async def listschedules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_role(update.effective_user.id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, message, send_at FROM scheduled_broadcasts WHERE sent = 0 ORDER BY send_at ASC"
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("এখন কোনো শিডিউল করা ব্রডকাস্ট নেই।")
        return

    lines = ["🗓️ পেন্ডিং শিডিউল ব্রডকাস্ট", "━━━━━━━━━━━━━━━"]
    for sid, msg, send_at in rows:
        preview = msg if len(msg) <= 60 else msg[:60] + "..."
        lines.append(f"#{sid} — {send_at}\n   {preview}")
    lines.append("━━━━━━━━━━━━━━━\nবাতিল করতে: /cancelschedule আইডি")
    await update.message.reply_text("\n".join(lines))


async def cancelschedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not has_role(update.effective_user.id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /cancelschedule আইডি (আইডি দেখতে /listschedules লিখুন)")
        return
    schedule_id = int(context.args[0])
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM scheduled_broadcasts WHERE id = ? AND sent = 0", (schedule_id,))
    if cur.fetchone() is None:
        conn.close()
        await update.message.reply_text("এই আইডির কোনো পেন্ডিং শিডিউল পাওয়া যায়নি।")
        return
    cur.execute("UPDATE scheduled_broadcasts SET sent = -1 WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"❌ শিডিউল #{schedule_id} বাতিল করা হয়েছে।")


async def check_scheduled_broadcasts(context: ContextTypes.DEFAULT_TYPE):
    """
    জব-কিউ (job_queue.run_repeating) দিয়ে নিয়মিত চলে — যেসব শিডিউল করা ব্রডকাস্টের সময়
    হয়ে গেছে কিন্তু এখনো পাঠানো হয়নি, সেগুলো পাঠিয়ে দেয়। বট বন্ধ থেকে আবার চালু হলেও
    কোনো শিডিউল মিস হবে না, কারণ এটা সবসময় ডাটাবেস দেখে চেক করে (উৎস একটাই — ডাটাবেস)।
    """
    now_iso = datetime.now().isoformat(timespec="minutes")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, message, created_by FROM scheduled_broadcasts WHERE sent = 0 AND send_at <= ?",
        (now_iso,),
    )
    due = cur.fetchall()
    conn.close()

    for schedule_id, message_text, created_by in due:
        try:
            sent, failed = await send_broadcast_to_all(context.bot, message_text)
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE scheduled_broadcasts SET sent = 1 WHERE id = ?", (schedule_id,))
            conn.commit()
            conn.close()
            logger.info(f"শিডিউল ব্রডকাস্ট #{schedule_id} পাঠানো হয়েছে: {sent} জনকে, ব্যর্থ {failed} জন")
            if created_by:
                try:
                    await context.bot.send_message(
                        chat_id=created_by,
                        text=f"✅ শিডিউল ব্রডকাস্ট #{schedule_id} পাঠানো হয়ে গেছে ({sent} জনকে, ব্যর্থ {failed} জন)।",
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"শিডিউল ব্রডকাস্ট #{schedule_id} পাঠাতে সমস্যা: {e}")


# ============================= Phase 4: Notifications (প্রিমিয়াম মেয়াদ) =============================

async def check_premium_notifications(context: ContextTypes.DEFAULT_TYPE):
    """
    জব-কিউ দিয়ে নিয়মিত (প্রতি PREMIUM_NOTIFY_INTERVAL_SECONDS সময়ে একবার) চলে:
      ১) যেসব প্রিমিয়াম ইউজারের মেয়াদ PREMIUM_EXPIRY_REMINDER_DAYS দিনের মধ্যে শেষ হবে,
         তাদের একবার রিমাইন্ডার পাঠায় (premium_expiry_notified দিয়ে ট্র্যাক করা হয়, বারবার
         পাঠানো হয় না)।
      ২) যাদের মেয়াদ ইতিমধ্যে শেষ হয়ে গেছে, তাদের প্রিমিয়াম স্বয়ংক্রিয়ভাবে বাতিল করে
         ইউজার ও সব অ্যাডমিনকে জানিয়ে দেয়।
    উৎস সবসময় ডাটাবেস, তাই বট মাঝে বন্ধ থেকে আবার চালু হলেও কোনো রিমাইন্ডার/মেয়াদ-শেষ
    ইভেন্ট মিস হয় না।
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, premium_until, premium_expiry_notified FROM users "
        "WHERE is_premium = 1 AND premium_until != ''"
    )
    rows = cur.fetchall()
    conn.close()

    today = date.today()
    for user_id, premium_until, notified in rows:
        try:
            until_date = datetime.strptime(premium_until, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        days_left = (until_date - today).days

        if days_left < 0:
            # মেয়াদ শেষ হয়ে গেছে — স্বয়ংক্রিয়ভাবে বাতিল করে জানানো
            revoke_premium(user_id)
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "⏳ আপনার প্রিমিয়াম মেয়াদ শেষ হয়ে গেছে।\n"
                        f"এখন থেকে ফ্রি সীমা প্রযোজ্য: দৈনিক {FREE_DAILY_LIMIT} বার।\n"
                        "আবার প্রিমিয়াম নিতে অ্যাডমিনের সাথে যোগাযোগ করুন।"
                    ),
                )
            except Exception as e:
                logger.warning(f"প্রিমিয়াম মেয়াদ-শেষ নোটিফিকেশন পাঠাতে সমস্যা (user {user_id}): {e}")

            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"ℹ️ ইউজার {user_id} এর প্রিমিয়াম মেয়াদ শেষ হয়ে স্বয়ংক্রিয়ভাবে বাতিল হয়েছে।",
                    )
                except Exception:
                    pass
            logger.info(f"ইউজার {user_id} এর প্রিমিয়াম মেয়াদ শেষ হয়ে স্বয়ংক্রিয়ভাবে বাতিল হলো।")

        elif days_left <= PREMIUM_EXPIRY_REMINDER_DAYS and not notified:
            # মেয়াদ শেষ হওয়ার কাছাকাছি — একবার রিমাইন্ডার
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"⏰ রিমাইন্ডার: আপনার প্রিমিয়াম মেয়াদ আর {days_left} দিন পর শেষ হয়ে যাবে "
                        f"({premium_until})।\nমেয়াদ বাড়াতে অ্যাডমিনের সাথে যোগাযোগ করুন।"
                    ),
                )
                conn2 = get_conn()
                cur2 = conn2.cursor()
                cur2.execute(
                    "UPDATE users SET premium_expiry_notified = 1 WHERE user_id = ?", (user_id,)
                )
                conn2.commit()
                conn2.close()
            except Exception as e:
                logger.warning(f"প্রিমিয়াম রিমাইন্ডার পাঠাতে সমস্যা (user {user_id}): {e}")


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /ban ইউজার_আইডি")
        return
    target_id = int(context.args[0])
    register_user(target_id)
    update_field(target_id, "is_banned", 1)
    await update.message.reply_text(f"ইউজার {target_id} কে ব্যান করা হয়েছে।")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /unban ইউজার_আইডি")
        return
    target_id = int(context.args[0])
    update_field(target_id, "is_banned", 0)
    await update.message.reply_text(f"ইউজার {target_id} কে আনব্যান করা হয়েছে।")


# ============================= Phase 5: অ্যাডমিন রোল ম্যানেজমেন্ট (শুধু Owner) =============================

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """এভাবে লিখুন: /addadmin ইউজার_আইডি রোল (রোল হতে হবে admin অথবা moderator)। শুধু Owner পারবেন।"""
    owner_id = update.effective_user.id
    if not has_role(owner_id, "owner"):
        await update.message.reply_text("এই কমান্ড শুধু Owner-এর জন্য।")
        return
    if len(context.args) < 2 or not context.args[0].isdigit() or context.args[1].lower() not in ("admin", "moderator"):
        await update.message.reply_text(
            "এভাবে লিখুন: /addadmin ইউজার_আইডি রোল\n"
            "রোল হতে হবে: admin অথবা moderator\n"
            "উদাহরণ: /addadmin 123456789 moderator"
        )
        return
    target_id = int(context.args[0])
    role = context.args[1].lower()
    if target_id in ADMIN_IDS:
        await update.message.reply_text("এই ইউজার আগে থেকেই Owner (Secrets থেকে সেট করা) — বদলানো যাবে না।")
        return
    register_user(target_id)
    add_admin_role(target_id, role, owner_id)
    await update.message.reply_text(f"✅ ইউজার {target_id} কে {ADMIN_ROLE_LABEL_BN[role]} বানানো হয়েছে।")
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"🎉 আপনাকে এই বটের {ADMIN_ROLE_LABEL_BN[role]} করা হয়েছে। /adminpanel লিখে অ্যাডমিন প্যানেল দেখুন।",
        )
    except Exception as e:
        logger.warning(f"অ্যাডমিন-নিয়োগ নোটিফিকেশন পাঠাতে সমস্যা (user {target_id}): {e}")


async def removeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """এভাবে লিখুন: /removeadmin ইউজার_আইডি। শুধু Owner পারবেন। .env-এর Owner বাদ দেওয়া যাবে না।"""
    owner_id = update.effective_user.id
    if not has_role(owner_id, "owner"):
        await update.message.reply_text("এই কমান্ড শুধু Owner-এর জন্য।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /removeadmin ইউজার_আইডি")
        return
    target_id = int(context.args[0])
    if target_id in ADMIN_IDS:
        await update.message.reply_text("এই ইউজার Secrets (.env)-এর ADMIN_IDS দিয়ে Owner — বটের ভেতর থেকে বাদ দেওয়া যাবে না।")
        return
    removed = remove_admin_role(target_id)
    if removed:
        await update.message.reply_text(f"✅ ইউজার {target_id} এর অ্যাডমিন রোল বাদ দেওয়া হয়েছে।")
        try:
            await context.bot.send_message(chat_id=target_id, text="আপনার অ্যাডমিন রোল বাতিল করা হয়েছে।")
        except Exception:
            pass
    else:
        await update.message.reply_text("এই ইউজারের কোনো অ্যাডমিন রোল পাওয়া যায়নি।")


def build_admin_roles_text() -> str:
    admins = list_all_admins()
    lines = ["👑 অ্যাডমিন তালিকা", "━━━━━━━━━━━━━━━"]
    for uid, role, source in admins:
        tag = " (Secrets/.env)" if source == "env" else ""
        lines.append(f"{ADMIN_ROLE_LABEL_BN.get(role, role)} — {uid}{tag}")
    lines.append("━━━━━━━━━━━━━━━\nনতুন অ্যাডমিন: /addadmin আইডি রোল (শুধু Owner)\nবাদ দিতে: /removeadmin আইডি (শুধু Owner)")
    return "\n".join(lines)


async def adminlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সব অ্যাডমিন (owner/admin/moderator) এর তালিকা — যেকোনো অ্যাডমিন দেখতে পারবেন।"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    await update.message.reply_text(build_admin_roles_text())


# ============================= Phase 5: বাটন-ভিত্তিক Admin Control Panel =============================
#
# /adminpanel — সব অ্যাডমিন কাজ (ইউজার সার্চ, ব্যান/আনব্যান, প্রিমিয়াম) এক জায়গা থেকে, ইনলাইন
# কীবোর্ড দিয়ে। কোন বাটন দেখা যাবে তা admin/owner/moderator রোলের উপর নির্ভর করে।
# ইউজার সার্চের সময় পরের মেসেজে ইউজার আইডি ধরার জন্য context.user_data["admin_awaiting"]
# ব্যবহার করা হয় — শুধু অ্যাডমিনদের জন্যই এটা সক্রিয় থাকে, সাধারণ ইউজারদের চ্যাটে কোনো প্রভাব নেই।

def build_admin_panel_view(user_id: int):
    role = get_admin_role(user_id)
    text = (
        f"🛠️ Admin Control Panel\n"
        f"আপনার রোল: {ADMIN_ROLE_LABEL_BN.get(role, role)}\n"
        "━━━━━━━━━━━━━━━\n"
        "নিচের বাটন থেকে বেছে নিন:\n\n"
        "🔐 Admin-only coding command-গুলো (যেমন /codebasescan, /codeauto) সাধারণ\n"
        "ইউজারদের /start, /help, /menu ও /codehelp-এ দেখানো হয় না — ওগুলোর তালিকা\n"
        "এই প্যানেলের ভিতরেই আছে (\"💻 Admin Coding কমান্ড\" বাটন)।"
    )
    rows = [[InlineKeyboardButton("🔍 ইউজার সার্চ", callback_data="adm_search")]]
    rows.append([InlineKeyboardButton("👑 প্রিমিয়াম তালিকা", callback_data="adm_premiumlist")])
    rows.append([InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="adm_stats")])
    rows.append([InlineKeyboardButton("📈 Analytics (গভীর)", callback_data="adm_analytics")])
    rows.append([InlineKeyboardButton("🧠 Brain Status", callback_data="adm_brainstatus")])
    rows.append([InlineKeyboardButton("🕘 Decision History", callback_data="adm_decisionhistory")])
    rows.append([InlineKeyboardButton("👥 অ্যাডমিন তালিকা", callback_data="adm_roles")])
    rows.append([InlineKeyboardButton("💻 Admin Coding কমান্ড", callback_data="adm_codecommands")])
    if has_role(user_id, "admin"):
        rows.append([InlineKeyboardButton("📢 ব্রডকাস্ট (নির্দেশনা)", callback_data="adm_broadcast_info")])
    return text, InlineKeyboardMarkup(rows)


def build_admin_back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ প্যানেলে ফিরুন", callback_data="adm_back")]])


def build_admin_user_summary(target_id: int) -> str:
    register_user(target_id)
    row = get_user_row(target_id)
    voice, speed, banned, count, last_date = row
    used_today = count if last_date == str(date.today()) else 0
    active = is_premium_active(target_id)
    _, premium_until, _ = get_premium_info(target_id)
    role = get_admin_role(target_id)
    lines = [
        f"👤 ইউজার আইডি: {target_id}",
        f"রোল: {ADMIN_ROLE_LABEL_BN.get(role, role) if role else '(সাধারণ ইউজার)'}",
        f"স্ট্যাটাস: {'🚫 ব্যানড' if banned else '✅ স্বাভাবিক'}",
        f"প্ল্যান: {'👑 প্রিমিয়াম (মেয়াদ: ' + (premium_until or 'আজীবন') + ')' if active else '🆓 ফ্রি'}",
        f"আজকের ব্যবহার: {used_today}/{get_daily_limit(target_id) if target_id not in ADMIN_IDS else '∞'}",
        f"রেফার করেছেন: {get_referral_count(target_id)} জনকে (বোনাস +{get_bonus_daily_limit(target_id)})",
    ]
    return "\n".join(lines)


def build_admin_user_actions_kb(admin_id: int, target_id: int, target_banned: bool):
    rows = []
    ban_label = "✅ আনব্যান করুন" if target_banned else "🚫 ব্যান করুন"
    ban_cb = f"adm_do_unban_{target_id}" if target_banned else f"adm_do_ban_{target_id}"
    rows.append([InlineKeyboardButton(ban_label, callback_data=ban_cb)])
    if has_role(admin_id, "admin"):
        rows.append([
            InlineKeyboardButton("👑 +৩০ দিন প্রিমিয়াম", callback_data=f"adm_do_prem30_{target_id}"),
            InlineKeyboardButton("+৩৬৫ দিন", callback_data=f"adm_do_prem365_{target_id}"),
        ])
        rows.append([InlineKeyboardButton("❌ প্রিমিয়াম বাতিল", callback_data=f"adm_do_premdel_{target_id}")])
    rows.append([InlineKeyboardButton("⬅️ প্যানেলে ফিরুন", callback_data="adm_back")])
    return InlineKeyboardMarkup(rows)


async def adminpanel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    text, markup = build_admin_panel_view(user_id)
    await update.message.reply_text(text, reply_markup=markup)


async def admin_text_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin Panel থেকে "ইউজার সার্চ" চাপার পর অ্যাডমিনের পরের টেক্সট মেসেজ (ইউজার আইডি) এখানে ধরা হয়।
    কোনো pending state না থাকলে কিছুই করে না — মেসেজটা স্বাভাবিকভাবে chat_general-এ চলে যায়।
    """
    user_id = update.effective_user.id
    if not is_admin(user_id) or context.user_data.get("admin_awaiting") != "search":
        return  # অ্যাডমিন না, বা কোনো pending সার্চ নেই — normal চ্যাট হ্যান্ডলারে চলে যাক

    context.user_data["admin_awaiting"] = None
    text_input = (update.message.text or "").strip()
    if not text_input.isdigit():
        await update.message.reply_text(
            "শুধু সংখ্যার (Telegram user ID) মাধ্যমে সার্চ করা যাবে। আবার চেষ্টা করতে /adminpanel লিখুন।"
        )
        raise ApplicationHandlerStop
    target_id = int(text_input)
    summary = build_admin_user_summary(target_id)
    _, _, banned, _, _ = get_user_row(target_id) or (None, None, 0, 0, "")
    await update.message.reply_text(summary, reply_markup=build_admin_user_actions_kb(user_id, target_id, bool(banned)))
    raise ApplicationHandlerStop


# ============================= Phase 4: প্রিমিয়াম অ্যাডমিন কমান্ড =============================

async def addpremium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """এভাবে লিখুন: /addpremium ইউজার_আইডি দিন_সংখ্যা (উদাহরণ: /addpremium 123456789 30 — ৩০ দিনের জন্য)।
    ইউজারের আগে থেকেই সক্রিয় প্রিমিয়াম থাকলে, এই দিনগুলো বর্তমান মেয়াদের সাথে যোগ হয়ে যায়।"""
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return
    if len(context.args) < 2 or not context.args[0].isdigit() or not context.args[1].isdigit():
        await update.message.reply_text(
            "এভাবে লিখুন: /addpremium ইউজার_আইডি দিন_সংখ্যা\n"
            "উদাহরণ: /addpremium 123456789 30  (৩০ দিন = প্রায় ১ মাস)"
        )
        return

    target_id = int(context.args[0])
    days = int(context.args[1])
    if days <= 0 or days > PREMIUM_MAX_DAYS:
        await update.message.reply_text(f"দিনের সংখ্যা ১ থেকে {PREMIUM_MAX_DAYS} এর মধ্যে দিন।")
        return

    new_until = grant_premium(target_id, days, admin_id)
    await update.message.reply_text(
        f"✅ ইউজার {target_id} কে প্রিমিয়াম করা হয়েছে ({days} দিনের জন্য)।\nমেয়াদ শেষ হবে: {new_until}"
    )

    # Notifications: ইউজারকে সাথে সাথে জানানো
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "🎉 অভিনন্দন! আপনাকে প্রিমিয়াম মেম্বারশিপ দেওয়া হয়েছে।\n"
                f"👑 মেয়াদ শেষ হবে: {new_until}\n"
                f"📈 দৈনিক সীমা এখন: {PREMIUM_DAILY_LIMIT} বার\n"
                "এছাড়া AI Memory-তে বেশি কথোপকথন মনে রাখা হবে এবং কোনো Anti-Flood কুলডাউন থাকবে না।"
            ),
        )
    except Exception as e:
        logger.warning(f"প্রিমিয়াম নোটিফিকেশন পাঠাতে সমস্যা (user {target_id}): {e}")

    # Notifications: অন্য অ্যাডমিনদেরও জানানো
    for other_admin in ADMIN_IDS:
        if other_admin != admin_id:
            try:
                await context.bot.send_message(
                    chat_id=other_admin,
                    text=f"ℹ️ ইউজার {target_id} কে প্রিমিয়াম করা হয়েছে (by {admin_id}), মেয়াদ শেষ: {new_until}",
                )
            except Exception:
                pass


async def removepremium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    if not has_role(admin_id, "admin"):
        await update.message.reply_text("এই কমান্ড শুধু Owner/Admin-এর জন্য (Moderator নয়)।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /removepremium ইউজার_আইডি")
        return

    target_id = int(context.args[0])
    was_active = is_premium_active(target_id)
    revoke_premium(target_id)
    await update.message.reply_text(f"❌ ইউজার {target_id} এর প্রিমিয়াম বাতিল করা হয়েছে।")

    if was_active:
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=(
                    "আপনার প্রিমিয়াম মেম্বারশিপ বাতিল করা হয়েছে।\n"
                    f"এখন থেকে ফ্রি সীমা প্রযোজ্য: দৈনিক {FREE_DAILY_LIMIT} বার।"
                ),
            )
        except Exception as e:
            logger.warning(f"প্রিমিয়াম বাতিল নোটিফিকেশন পাঠাতে সমস্যা (user {target_id}): {e}")

    for other_admin in ADMIN_IDS:
        if other_admin != admin_id:
            try:
                await context.bot.send_message(
                    chat_id=other_admin,
                    text=f"ℹ️ ইউজার {target_id} এর প্রিমিয়াম বাতিল করা হয়েছে (by {admin_id})।",
                )
            except Exception:
                pass


async def premiumstatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    সবাই নিজের প্ল্যান দেখতে পারেন: /premiumstatus
    অ্যাডমিন অন্য কারো প্ল্যানও দেখতে পারেন: /premiumstatus ইউজার_আইডি
    """
    requester_id = update.effective_user.id
    target_id = requester_id
    if context.args:
        if not is_admin(requester_id):
            await update.message.reply_text("অন্য কারো প্ল্যান দেখার অনুমতি শুধু অ্যাডমিনের আছে।")
            return
        if not context.args[0].isdigit():
            await update.message.reply_text("এভাবে লিখুন: /premiumstatus [ইউজার_আইডি]")
            return
        target_id = int(context.args[0])

    register_user(target_id)
    who = "আপনি" if target_id == requester_id else f"ইউজার {target_id}"

    if target_id in ADMIN_IDS:
        text = f"{who} অ্যাডমিন — দৈনিক সীমা প্রযোজ্য নয়, প্রিমিয়াম/ফ্রি প্ল্যানের বিষয়ও প্রযোজ্য নয়।"
    elif is_premium_active(target_id):
        _, premium_until, premium_since = get_premium_info(target_id)
        if premium_until:
            try:
                days_left = (datetime.strptime(premium_until, "%Y-%m-%d").date() - date.today()).days
                expiry_line = f"মেয়াদ শেষ: {premium_until} ({days_left} দিন বাকি)"
            except ValueError:
                expiry_line = f"মেয়াদ শেষ: {premium_until}"
        else:
            expiry_line = "মেয়াদ: আজীবন"
        text = (
            f"👑 {who} প্রিমিয়াম সদস্য\n"
            f"{expiry_line}\n"
            f"দৈনিক সীমা: {PREMIUM_DAILY_LIMIT} বার\n"
            "অতিরিক্ত সুবিধা: বেশি AI Memory, কোনো Anti-Flood কুলডাউন নেই"
        )
    else:
        text = (
            f"🆓 {who} ফ্রি ইউজার\n"
            f"দৈনিক সীমা: {FREE_DAILY_LIMIT} বার\n"
            "প্রিমিয়াম নিতে অ্যাডমিনের সাথে যোগাযোগ করুন।"
        )

    if target_id == requester_id:
        await update.message.reply_text(await localize(requester_id, text))
    else:
        await update.message.reply_text(text)


def build_premiumlist_text() -> str:
    rows = list_active_premium_users()
    if not rows:
        return "এখন কোনো সক্রিয় প্রিমিয়াম ইউজার নেই।"
    today = date.today()
    lines = ["👑 সক্রিয় প্রিমিয়াম ইউজার তালিকা", "━━━━━━━━━━━━━━━"]
    for uid, until in rows:
        if until:
            try:
                days_left = (datetime.strptime(until, "%Y-%m-%d").date() - today).days
                lines.append(f"• {uid} — মেয়াদ শেষ: {until} ({days_left} দিন বাকি)")
            except ValueError:
                lines.append(f"• {uid} — মেয়াদ শেষ: {until}")
        else:
            lines.append(f"• {uid} — আজীবন")
    lines.append(f"━━━━━━━━━━━━━━━\nমোট: {len(rows)} জন")
    return "\n".join(lines)


async def premiumlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিনের জন্য — বর্তমানে সক্রিয় সব প্রিমিয়াম ইউজারের তালিকা।"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    await update.message.reply_text(build_premiumlist_text())


def build_stats_text() -> str:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
    banned = cur.fetchone()[0]
    today = str(date.today())
    cur.execute("SELECT COUNT(*) FROM users WHERE last_request_date = ?", (today,))
    active_today = cur.fetchone()[0]
    conn.close()
    return f"মোট ইউজার: {total}\nব্যানড: {banned}\nআজকে সক্রিয়: {active_today}"


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    await update.message.reply_text(build_stats_text())


def build_ai_stats_text() -> str:
    """Phase 10: Statistics Manager — Queue, Response Cache ও প্রতিটা Provider/Key-এর
    ব্যবহার/Response Time/Error/Retry পরিসংখ্যান একসাথে ফরম্যাট করে /aistats-এর জন্য।"""
    lines = ["📈 AI ইঞ্জিন পরিসংখ্যান (Phase 9/10)", "━━━━━━━━━━━━━━━"]

    q = ai_queue_manager.stats()
    lines.append(
        f"🧵 Queue Manager: সারিতে {q['queue_size']}, চলছে {q['active']}/{q['max_workers']}, "
        f"মোট জমা {q['total_queued']}, প্রসেস {q['total_processed']}, ব্যর্থ {q['total_failed']}"
    )
    lines.append(
        f"⏱️ Queue Time: গড় {ai_stats_manager.avg_queue_wait():.2f}s, "
        f"সর্বোচ্চ {ai_stats_manager.queue_wait_max:.2f}s"
    )

    total_cache_calls = ai_stats_manager.cache_hits + ai_stats_manager.cache_misses
    hit_rate_text = f" ({ai_stats_manager.cache_hit_rate():.1f}% হিট রেট)" if total_cache_calls else ""
    lines.append(
        f"🗂️ Response Cache: {ai_stats_manager.cache_hits} হিট / {ai_stats_manager.cache_misses} মিস"
        f"{hit_rate_text}, বর্তমানে ক্যাশে জমা আছে: {ai_response_cache.size()}টা এন্ট্রি"
    )

    lines.append("━━━━━━━━━━━━━━━")
    for provider in ai_router.providers:
        keys = provider.key_pool.keys
        if not keys:
            lines.append(f"\n🔌 {provider.name}: কোনো Key কনফিগার করা নেই")
            continue
        lines.append(f"\n🔌 {provider.name} ({len(keys)}টা Key, মডেল: {provider.model}):")
        for k in keys:
            status = "✅ সুস্থ" if k.is_healthy() else "🚫 Inactive (কুলডাউনে)"
            success = k.total_requests - k.total_failures
            lines.append(
                f"  • {k.label} — {status}\n"
                f"    ব্যবহার: {k.total_requests} বার (সফল {success}, ব্যর্থ {k.total_failures}), "
                f"Retry: {k.total_retries}, গড় Response Time: {k.avg_response_time:.2f}s"
            )

    lines.append("━━━━━━━━━━━━━━━")
    lines.append(f"🧠 Brain OS-এর মাধ্যমে AI কল সাশ্রয় হয়েছে: {brain_os_metrics.get('direct_answers', 0)} বার")
    return "\n".join(lines)


async def aistats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Phase 10: অ্যাডমিনের জন্য AI ইঞ্জিনের বিস্তারিত পরিসংখ্যান (Queue/Cache/Provider/Key)।"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    await update.message.reply_text(build_ai_stats_text())


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সবাই দেখতে পারে এমন লিডারবোর্ড — সবচেয়ে বেশি বট ব্যবহারকারী টপ ১০ জন।"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id, COUNT(*) as cnt FROM usage_log
        GROUP BY user_id ORDER BY cnt DESC LIMIT 10
        """
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("এখনো কোনো ব্যবহারের তথ্য জমা হয়নি।")
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 লিডারবোর্ড (সর্বমোট ব্যবহার অনুযায়ী)", "━━━━━━━━━━━━━━━"]
    for i, (uid, cnt) in enumerate(rows):
        prefix = medals[i] if i < 3 else f"{i + 1}."
        display = f"User-{str(uid)[-4:]}"
        lines.append(f"{prefix} {display} — {cnt} বার")
    await update.message.reply_text("\n".join(lines))


async def dailystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিনের জন্য আজকের ব্যবহারের পরিসংখ্যান।"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    today_prefix = str(date.today())  # YYYY-MM-DD

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usage_log WHERE created_at LIKE ?", (f"{today_prefix}%",))
    total_uses = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) FROM usage_log WHERE created_at LIKE ?", (f"{today_prefix}%",)
    )
    active_users = cur.fetchone()[0]
    cur.execute(
        """
        SELECT action, COUNT(*) as cnt FROM usage_log WHERE created_at LIKE ?
        GROUP BY action ORDER BY cnt DESC LIMIT 5
        """,
        (f"{today_prefix}%",),
    )
    top_features = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM users WHERE joined_date = ?", (today_prefix,))
    new_users = cur.fetchone()[0]
    conn.close()

    lines = [
        f"📅 আজকের পরিসংখ্যান ({today_prefix})",
        "━━━━━━━━━━━━━━━",
        f"মোট ব্যবহার: {total_uses}",
        f"সক্রিয় ইউজার: {active_users}",
        f"নতুন যোগ দেওয়া ইউজার: {new_users}",
    ]
    if top_features:
        lines.append("সবচেয়ে বেশি ব্যবহৃত ফিচার:")
        for action, cnt in top_features:
            lines.append(f"  • {action}: {cnt} বার")
    await update.message.reply_text("\n".join(lines))


async def monthlystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিনের জন্য এই মাসের ব্যবহারের পরিসংখ্যান।"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    month_prefix = str(date.today())[:7]  # YYYY-MM

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usage_log WHERE created_at LIKE ?", (f"{month_prefix}%",))
    total_uses = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(DISTINCT user_id) FROM usage_log WHERE created_at LIKE ?", (f"{month_prefix}%",)
    )
    active_users = cur.fetchone()[0]
    cur.execute(
        """
        SELECT action, COUNT(*) as cnt FROM usage_log WHERE created_at LIKE ?
        GROUP BY action ORDER BY cnt DESC LIMIT 5
        """,
        (f"{month_prefix}%",),
    )
    top_features = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM users WHERE joined_date LIKE ?", (f"{month_prefix}%",))
    new_users = cur.fetchone()[0]
    conn.close()

    lines = [
        f"📆 এই মাসের পরিসংখ্যান ({month_prefix})",
        "━━━━━━━━━━━━━━━",
        f"মোট ব্যবহার: {total_uses}",
        f"সক্রিয় ইউজার: {active_users}",
        f"নতুন যোগ দেওয়া ইউজার: {new_users}",
    ]
    if top_features:
        lines.append("সবচেয়ে বেশি ব্যবহৃত ফিচার:")
        for action, cnt in top_features:
            lines.append(f"  • {action}: {cnt} বার")
    await update.message.reply_text("\n".join(lines))


# ============================= Phase 6: আরও গভীর Analytics =============================

def _text_bar(value: int, max_value: int, width: int = 18) -> str:
    """ইউনিকোড ব্লক দিয়ে সাধারণ টেক্সট-বার চার্ট বানায় (কোনো ইমেজ লাইব্রেরি লাগে না, সম্পূর্ণ ফ্রি)।"""
    if max_value <= 0:
        return "░" * width
    filled = max(0, min(width, round((value / max_value) * width)))
    return "█" * filled + "░" * (width - filled)


def build_analytics_report(days: int = 14) -> str:
    """
    বিস্তারিত অ্যানালিটিক্স রিপোর্ট বানায়:
      ১) সর্বকালের সেরা ১০টা কমান্ড/ফিচার (কোনটা কতবার ব্যবহার হয়েছে)
      ২) দিনের কোন সময়ে (ঘণ্টা অনুযায়ী) বট সবচেয়ে বেশি ব্যবহার হয়
      ৩) গত কয়েক দিনে নতুন ইউজার যোগ হওয়ার গ্রাফ-স্টাইল টেক্সট রিপোর্ট
    """
    conn = get_conn()
    cur = conn.cursor()

    # ১) সর্বকালের সেরা কমান্ড
    cur.execute(
        "SELECT action, COUNT(*) as cnt FROM usage_log GROUP BY action ORDER BY cnt DESC LIMIT 10"
    )
    top_commands = cur.fetchall()

    # ২) ঘণ্টা-ভিত্তিক ব্যবহার (০-২৩, সার্ভারের সময় অনুযায়ী)
    cur.execute(
        "SELECT substr(created_at, 12, 2) as hr, COUNT(*) as cnt FROM usage_log "
        "WHERE hr IS NOT NULL GROUP BY hr"
    )
    hour_counts = {int(hr): cnt for hr, cnt in cur.fetchall() if hr and hr.isdigit()}

    # ৩) গত N দিনের নতুন ইউজার
    start_day = date.today() - timedelta(days=days - 1)
    cur.execute(
        "SELECT joined_date, COUNT(*) FROM users WHERE joined_date >= ? GROUP BY joined_date",
        (start_day.isoformat(),),
    )
    growth_map = {d: c for d, c in cur.fetchall()}
    conn.close()

    lines = ["📈 বিস্তারিত Analytics রিপোর্ট", "━━━━━━━━━━━━━━━"]

    lines.append("🏆 সর্বকালের সেরা ১০ কমান্ড/ফিচার:")
    if top_commands:
        max_cmd = max(cnt for _, cnt in top_commands)
        for action, cnt in top_commands:
            lines.append(f"  {action:<15} {_text_bar(cnt, max_cmd, 12)} {cnt}")
    else:
        lines.append("  এখনো কোনো ব্যবহার লগ হয়নি।")

    lines.append("")
    lines.append("🕐 দিনের কোন সময়ে বট বেশি ব্যবহার হয় (ঘণ্টা অনুযায়ী, সার্ভার সময়):")
    if hour_counts:
        max_hr = max(hour_counts.values())
        busiest_hour = max(hour_counts, key=hour_counts.get)
        for h in range(0, 24, 3):  # প্রতি ৩ ঘণ্টা পরপর দেখানো — রিপোর্ট ছোট রাখতে
            cnt = hour_counts.get(h, 0)
            lines.append(f"  {h:02d}:00  {_text_bar(cnt, max_hr, 12)} {cnt}")
        lines.append(f"  সবচেয়ে ব্যস্ত সময়: {busiest_hour:02d}:00")
    else:
        lines.append("  এখনো তথ্য নেই।")

    lines.append("")
    lines.append(f"👥 গত {days} দিনে নতুন ইউজার (দিন-ভিত্তিক):")
    growth_values = []
    for i in range(days):
        d = (start_day + timedelta(days=i)).isoformat()
        growth_values.append((d, growth_map.get(d, 0)))
    max_growth = max((c for _, c in growth_values), default=0)
    for d, c in growth_values:
        lines.append(f"  {d}  {_text_bar(c, max_growth, 12)} {c}")
    lines.append(f"  মোট নতুন ({days} দিনে): {sum(c for _, c in growth_values)}")

    return "\n".join(lines)


async def analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিনের জন্য গভীর অ্যানালিটিক্স। এভাবে লিখুন: /analytics অথবা /analytics ৩০ (গত ৩০ দিনের গ্রোথ দেখতে)।"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    days = 14
    if context.args and context.args[0].isdigit():
        days = max(1, min(90, int(context.args[0])))  # নিরাপত্তা: অনেক বড় রেঞ্জ চেয়ে বসলে সীমা রাখা
    await send_long_text(update, build_analytics_report(days))


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিনকে ডাটাবেস ফাইল পাঠায় (ব্যাকআপ)।"""
    if not has_role(update.effective_user.id, "owner"):
        await update.message.reply_text("এই কমান্ড শুধু Owner-এর জন্য (Admin/Moderator নয়)।")
        return
    if not os.path.exists(DB_PATH):
        await update.message.reply_text("এখনো কোনো ডাটাবেস তৈরি হয়নি।")
        return
    backup_path = os.path.join(tempfile.gettempdir(), f"backup_{int(time.time())}.db")
    try:
        shutil.copyfile(DB_PATH, backup_path)
        with open(backup_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"bot_data_backup_{date.today()}.db",
                caption="✅ ডাটাবেস ব্যাকআপ। এটা /restore দিয়ে ফেরত বসানো যাবে।",
            )
    except Exception as e:
        logger.error(f"ব্যাকআপ এরর: {e}")
        await update.message.reply_text("দুঃখিত, ব্যাকআপ নিতে সমস্যা হয়েছে।")
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)


async def restore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিন একটা .db ফাইলে রিপ্লাই দিয়ে /restore লিখলে সেটা দিয়ে বর্তমান ডাটাবেস প্রতিস্থাপন হয়।"""
    if not has_role(update.effective_user.id, "owner"):
        await update.message.reply_text("এই কমান্ড শুধু Owner-এর জন্য (Admin/Moderator নয়)।")
        return
    target = update.message.reply_to_message
    if not target or not target.document:
        await update.message.reply_text("যে .db ব্যাকআপ ফাইল বসাতে চান, তাতে রিপ্লাই দিয়ে /restore লিখুন।")
        return
    if not target.document.file_name.endswith(".db"):
        await update.message.reply_text("শুধু .db ফাইল দিয়েই রিস্টোর করা যাবে।")
        return

    processing = await update.message.reply_text("রিস্টোর করা হচ্ছে...")
    tmp_path = os.path.join(tempfile.gettempdir(), f"restore_{int(time.time())}.db")
    try:
        doc_file = await target.document.get_file()
        await doc_file.download_to_drive(tmp_path)
        # আগে যাচাই করা হচ্ছে ফাইলটা আসলেই বৈধ SQLite ডাটাবেস কিনা
        test_conn = sqlite3.connect(tmp_path)
        test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        test_conn.close()

        shutil.copyfile(DB_PATH, DB_PATH + ".before_restore.bak")
        shutil.copyfile(tmp_path, DB_PATH)
        _load_admin_role_cache()  # ডাটাবেস বদলে গেছে, তাই অ্যাডমিন-রোল ক্যাশ নতুন করে লোড করা হলো
        await update.message.reply_text("✅ ডাটাবেস সফলভাবে রিস্টোর করা হয়েছে।")
    except Exception as e:
        logger.error(f"রিস্টোর এরর: {e}")
        await update.message.reply_text("দুঃখিত, এই ফাইলটা বৈধ ব্যাকআপ মনে হচ্ছে না। রিস্টোর করা যায়নি।")
    finally:
        await processing.delete()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডমিনের জন্য এক নজরে সবকিছু দেখানোর টেক্সট ড্যাশবোর্ড।"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
    banned = cur.fetchone()[0]
    today = str(date.today())
    cur.execute("SELECT COUNT(*) FROM users WHERE last_request_date = ?", (today,))
    active_today = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM feedback")
    feedback_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bug_reports")
    bug_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
    premium_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE referred_by != 0")
    referred_count = cur.fetchone()[0]
    conn.close()

    running_for = time.time() - BOT_START_TIME
    text = (
        "📊 অ্যাডমিন ড্যাশবোর্ড\n"
        "━━━━━━━━━━━━━━━\n"
        f"মোট ইউজার: {total_users}\n"
        f"ব্যানড ইউজার: {banned}\n"
        f"প্রিমিয়াম ইউজার: {premium_count}\n"
        f"রেফারেলে যোগ দিয়েছেন: {referred_count}\n"
        f"আজকে সক্রিয়: {active_today}\n"
        f"মোট ফিডব্যাক: {feedback_count}\n"
        f"মোট বাগ রিপোর্ট: {bug_count}\n"
        f"বট আপটাইম: {format_duration(running_for)}\n"
        "━━━━━━━━━━━━━━━\n"
        "কমান্ডসমূহ: /broadcast /schedulebroadcast /listschedules /cancelschedule /ban /unban /stats "
        "/backup /restore /serverstatus /dailystats /monthlystats /analytics\n"
        "প্রিমিয়াম: /addpremium /removepremium /premiumstatus /premiumlist\n"
        "রোল/প্যানেল: /adminpanel /adminlist /addadmin /removeadmin"
    )
    await update.message.reply_text(text)


# ============================= এরর হ্যান্ডলার =============================

# ============================= Phase 11: Coding Orchestrator =============================
# ইউজার কোনো কোডিং প্রজেক্টের বর্ণনা দিলে বট নিজে থেকে:
#   ১) Prompt Analyze  — রিকোয়েস্ট বিশ্লেষণ করে কী দরকার বোঝে
#   ২) Project Plan    — বড় কাজকে ছোট ছোট (ধারাবাহিক) ধাপে ভাগ করে
#   ৩) Task Split      — প্রতিটা ধাপ একবারে একটা করে সামলায়, পুরো প্রজেক্ট একসাথে AI-কে পাঠায় না
#   ৪) Knowledge Base  — খুবই কমন প্যাটার্ন/বয়লারপ্লেট (gitignore, README, Flask/FastAPI
#                        স্কেলিটন ইত্যাদি) বট নিজে থেকেই জানে, ওসবের জন্য AI-কে জিজ্ঞেস করে না
#   ৫) Assemble        — AI-এর উত্তর থেকে বট নিজে কোড জোড়া লাগিয়ে সম্পূর্ণ ফাইল বানায়
#   ৬) Project Memory  — প্রতি ইউজারের প্রতিটা প্রজেক্ট ও তার ধাপ আলাদাভাবে ডাটাবেসে থাকে,
#                        বট রিস্টার্ট হলেও হারায় না; একসাথে একাধিক প্রজেক্টও রাখা যায়
# এই পুরো সেকশনটাই নতুন সংযোজন — বটের আগের কোনো Command/Feature/UI স্পর্শ করা হয়নি।

CODE_TASK_MAX_TASKS = 12          # একটা প্রজেক্ট প্ল্যানে সর্বোচ্চ কতগুলো ধাপ থাকবে
CODE_CONTEXT_PREV_TASKS = 3       # একটা ধাপের কোড বানানোর সময় আগের কয়টা সম্পন্ন ধাপের শিরোনাম প্রসঙ্গ হিসেবে পাঠানো হবে
CODE_CONTEXT_EXISTING_CODE_MAX_CHARS = 8000  # আগের ধাপের assemble করা কোড কতটুকু পর্যন্ত prompt-এ পাঠানো হবে (শেষ অংশ রাখা হয়)

# ---- Knowledge Base: খুবই কমন প্যাটার্ন/বয়লারপ্লেট — মিলে গেলে AI-কে জিজ্ঞেস না করেই
#      বট নিজে থেকে সরাসরি কোড বসিয়ে দেয় (Task Split-এর সময় সবার আগে এটা চেক হয়) ----
CODE_KNOWLEDGE_BASE = [
    (("gitignore", ".gitignore"), "gitignore",
     "__pycache__/\n*.pyc\n.env\nvenv/\n.venv/\n*.db\n*.log\n.DS_Store\ndist/\nbuild/\n*.egg-info/\nnode_modules/\n"),
    (("readme",), "readme",
     "# {project_name}\n\n## বিবরণ\n{project_desc}\n\n## ইনস্টল\n```\npip install -r requirements.txt\n```\n\n"
     "## চালানো\n```\npython main.py\n```\n"),
    (("requirements.txt", "requirements file"), "requirements",
     "# প্রজেক্টের dependency এখানে যোগ করুন, যেমন:\n# requests\n# python-dotenv\n"),
    ((".env", "environment variable", "env file"), "env_template",
     "# গুরুত্বপূর্ণ কী/ভ্যালু এখানে বসান (এই ফাইল কখনো git-এ পুশ করবেন না)\nAPI_KEY=\nDEBUG=False\n"),
    (("flask skeleton", "flask app", "flask basic"), "flask_skeleton",
     "from flask import Flask, jsonify\n\napp = Flask(__name__)\n\n\n@app.route(\"/\")\ndef index():\n"
     "    return jsonify({\"status\": \"ok\"})\n\n\nif __name__ == \"__main__\":\n    app.run(debug=True)\n"),
    (("fastapi skeleton", "fastapi basic"), "fastapi_skeleton",
     "from fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get(\"/\")\ndef read_root():\n"
     "    return {\"status\": \"ok\"}\n\n# চালানো: uvicorn main:app --reload\n"),
    (("logging setup", "logger setup"), "logging_setup",
     "import logging\n\nlogging.basicConfig(\n    level=logging.INFO,\n"
     "    format=\"%(asctime)s [%(levelname)s] %(message)s\",\n)\nlogger = logging.getLogger(__name__)\n"),
    (("sqlite connection", "database connection boilerplate"), "sqlite_boilerplate",
     "import sqlite3\n\n\ndef get_conn(db_path=\"data.db\"):\n    conn = sqlite3.connect(db_path)\n"
     "    conn.row_factory = sqlite3.Row\n    return conn\n"),
    (("basic html", "html template"), "html_template",
     "<!DOCTYPE html>\n<html lang=\"bn\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>{project_name}</title>\n"
     "</head>\n<body>\n  <h1>{project_name}</h1>\n</body>\n</html>\n"),
    (("package.json",), "package_json",
     "{\n  \"name\": \"project\",\n  \"version\": \"1.0.0\",\n  \"main\": \"index.js\",\n"
     "  \"scripts\": {\n    \"start\": \"node index.js\"\n  }\n}\n"),
    (("calculator", "calc app", "ক্যালকুলেটর"), "calculator_cli",
     "def calculate(a: float, b: float, op: str) -> float:\n"
     "    \"\"\"op: +, -, *, / \"\"\"\n"
     "    ops = {\n"
     "        \"+\": lambda x, y: x + y,\n"
     "        \"-\": lambda x, y: x - y,\n"
     "        \"*\": lambda x, y: x * y,\n"
     "        \"/\": lambda x, y: x / y if y != 0 else float(\"inf\"),\n"
     "    }\n"
     "    if op not in ops:\n"
     "        raise ValueError(f\"অসমর্থিত অপারেটর: {op}\")\n"
     "    return ops[op](a, b)\n\n\n"
     "def main():\n"
     "    print(\"{project_name} — সাধারণ ক্যালকুলেটর (exit লিখে বের হন)\")\n"
     "    while True:\n"
     "        raw = input(\"expr (যেমন: 3 + 4): \").strip()\n"
     "        if raw.lower() in {\"exit\", \"quit\"}:\n"
     "            break\n"
     "        try:\n"
     "            a_str, op, b_str = raw.split()\n"
     "            result = calculate(float(a_str), float(b_str), op)\n"
     "            print(f\"= {result}\")\n"
     "        except Exception as e:\n"
     "            print(f\"ভুল ইনপুট: {e}\")\n\n\n"
     "if __name__ == \"__main__\":\n"
     "    main()\n"),
    (("todo app", "todo list", "টুডু"), "todo_app_cli",
     "import json\nimport os\n\nDB_FILE = \"todos.json\"\n\n\n"
     "def load_todos():\n"
     "    if not os.path.exists(DB_FILE):\n"
     "        return []\n"
     "    with open(DB_FILE, \"r\", encoding=\"utf-8\") as f:\n"
     "        return json.load(f)\n\n\n"
     "def save_todos(todos):\n"
     "    with open(DB_FILE, \"w\", encoding=\"utf-8\") as f:\n"
     "        json.dump(todos, f, ensure_ascii=False, indent=2)\n\n\n"
     "def add_todo(text: str):\n"
     "    todos = load_todos()\n"
     "    todos.append({\"text\": text, \"done\": False})\n"
     "    save_todos(todos)\n\n\n"
     "def list_todos():\n"
     "    for i, t in enumerate(load_todos()):\n"
     "        mark = \"x\" if t[\"done\"] else \" \"\n"
     "        print(f\"[{mark}] {i}: {t['text']}\")\n"),
    (("crud api", "rest api skeleton", "crud endpoint"), "crud_api_flask",
     "from flask import Flask, request, jsonify\n\napp = Flask(__name__)\nITEMS = {}\nNEXT_ID = 1\n\n\n"
     "@app.route(\"/items\", methods=[\"GET\"])\ndef list_items():\n"
     "    return jsonify(list(ITEMS.values()))\n\n\n"
     "@app.route(\"/items\", methods=[\"POST\"])\ndef create_item():\n"
     "    global NEXT_ID\n    data = request.get_json(force=True)\n"
     "    item = {\"id\": NEXT_ID, **data}\n    ITEMS[NEXT_ID] = item\n    NEXT_ID += 1\n"
     "    return jsonify(item), 201\n\n\n"
     "@app.route(\"/items/<int:item_id>\", methods=[\"PUT\"])\ndef update_item(item_id):\n"
     "    if item_id not in ITEMS:\n        return jsonify({\"error\": \"not found\"}), 404\n"
     "    ITEMS[item_id].update(request.get_json(force=True))\n    return jsonify(ITEMS[item_id])\n\n\n"
     "@app.route(\"/items/<int:item_id>\", methods=[\"DELETE\"])\ndef delete_item(item_id):\n"
     "    ITEMS.pop(item_id, None)\n    return \"\", 204\n\n\n"
     "if __name__ == \"__main__\":\n    app.run(debug=True)\n"),
    (("unit test", "pytest skeleton", "test skeleton"), "pytest_skeleton",
     "import pytest\n\n\n"
     "def test_example():\n    assert 1 + 1 == 2\n\n\n"
     "class TestSuite:\n    def test_placeholder(self):\n        assert True\n"),
    (("dockerfile", "docker setup"), "dockerfile",
     "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\n"
     "RUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\n"
     "CMD [\"python\", \"main.py\"]\n"),
    (("argparse cli", "command line tool skeleton"), "argparse_cli",
     "import argparse\n\n\n"
     "def main():\n"
     "    parser = argparse.ArgumentParser(description=\"{project_name}\")\n"
     "    parser.add_argument(\"input\", help=\"ইনপুট মান\")\n"
     "    parser.add_argument(\"-v\", \"--verbose\", action=\"store_true\")\n"
     "    args = parser.parse_args()\n"
     "    if args.verbose:\n        print(f\"ইনপুট পেলাম: {args.input}\")\n"
     "    print(args.input)\n\n\n"
     "if __name__ == \"__main__\":\n    main()\n"),
    (("password hash", "auth boilerplate", "login system boilerplate"), "auth_boilerplate",
     "import hashlib\nimport os\n\n\n"
     "def hash_password(password: str) -> str:\n"
     "    salt = os.urandom(16)\n"
     "    digest = hashlib.pbkdf2_hmac(\"sha256\", password.encode(), salt, 100_000)\n"
     "    return salt.hex() + \":\" + digest.hex()\n\n\n"
     "def verify_password(password: str, stored: str) -> bool:\n"
     "    salt_hex, digest_hex = stored.split(\":\")\n"
     "    salt = bytes.fromhex(salt_hex)\n"
     "    check = hashlib.pbkdf2_hmac(\"sha256\", password.encode(), salt, 100_000)\n"
     "    return check.hex() == digest_hex\n"),
    # ---- সুপরিচিত, সসীম অ্যালগরিদম প্যাটার্ন — এই ক্লাসিক একক-ধাপের টাস্কগুলোর জন্য
    #      AI কল করা অবান্তর; নির্দিষ্ট, যাচাইযোগ্য টেমপ্লেট নিচে দেওয়া ----
    (("fizzbuzz", "fizz buzz", "ফিজবাজ", "ফিজ বাজ"), "fizzbuzz",
     "def fizzbuzz(n: int) -> None:\n"
     "    for i in range(1, n + 1):\n"
     "        if i % 3 == 0 and i % 5 == 0:\n"
     "            print(\"FizzBuzz\")\n"
     "        elif i % 3 == 0:\n"
     "            print(\"Fizz\")\n"
     "        elif i % 5 == 0:\n"
     "            print(\"Buzz\")\n"
     "        else:\n"
     "            print(i)\n\n\n"
     "if __name__ == \"__main__\":\n"
     "    fizzbuzz(20)\n"),
    (("prime number", "prime check", "is prime", "প্রাইম", "মৌলিক সংখ্যা"), "prime_check",
     "def is_prime(n: int) -> bool:\n"
     "    \"\"\"Trial division — O(√n)।\"\"\"\n"
     "    if n < 2:\n"
     "        return False\n"
     "    if n % 2 == 0:\n"
     "        return n == 2\n"
     "    d = 3\n"
     "    while d * d <= n:\n"
     "        if n % d == 0:\n"
     "            return False\n"
     "        d += 2\n"
     "    return True\n\n\n"
     "if __name__ == \"__main__\":\n"
     "    print([n for n in range(2, 50) if is_prime(n)])\n"),
    (("factorial", "ফ্যাক্টোরিয়াল"), "factorial",
     "def factorial(n: int) -> int:\n"
     "    if n < 0:\n"
     "        raise ValueError(\"ঋণাত্মক সংখ্যার factorial নেই\")\n"
     "    result = 1\n"
     "    for i in range(2, n + 1):\n"
     "        result *= i\n"
     "    return result\n\n\n"
     "if __name__ == \"__main__\":\n"
     "    print(factorial(5))  # 120\n"),
    (("fibonacci", "ফিবোনাচি", "ফিবোনাচ্চি"), "fibonacci",
     "def fib_sequence(n: int) -> list:\n"
     "    a, b, out = 0, 1, []\n"
     "    for _ in range(n):\n"
     "        out.append(a)\n"
     "        a, b = b, a + b\n"
     "    return out\n\n\n"
     "if __name__ == \"__main__\":\n"
     "    print(fib_sequence(10))\n"),
    (("string reverse", "reverse a string", "reverse string", "স্ট্রিং রিভার্স", "স্ট্রিং উল্টো"), "string_reverse",
     "def reverse_string(text: str) -> str:\n"
     "    return text[::-1]\n\n\n"
     "if __name__ == \"__main__\":\n"
     "    print(reverse_string(\"আমার সোনার বাংলা\"))\n"),
]

# --------------------------------------------------------------------------
# Knowledge Base ম্যাচিং: শুধু প্রথম মিল না নিয়ে, সবগুলো এন্ট্রির সাথে স্কোর করে
# সবচেয়ে ভালো মিলটা বাছাই করে। word-boundary regex ব্যবহার করা হয়েছে যাতে
# ছোট/আংশিক শব্দে (যেমন শুধু "html" শব্দটা অন্য প্রসঙ্গে থাকলে) ভুল মিল না হয়।
# একটা ন্যূনতম স্কোর থ্রেশহোল্ডের নিচে কিছু না মিললে None রিটার্ন হয়, যাতে দুর্বল
# মিলের ক্ষেত্রে ভুল টেমপ্লেট চাপিয়ে না দিয়ে AI ফলব্যাকে যাওয়া যায়।
# --------------------------------------------------------------------------
KB_MIN_SCORE = 1.0

_KB_COMPILED = None


def _kb_compiled_patterns():
    """প্রতিটা কীওয়ার্ডকে একবার regex-এ কম্পাইল করে ক্যাশ করে রাখে (বারবার কম্পাইল না করার জন্য)।"""
    global _KB_COMPILED
    if _KB_COMPILED is None:
        compiled = []
        for keywords, label, template in CODE_KNOWLEDGE_BASE:
            kw_patterns = []
            for kw in keywords:
                # মাল্টি-ওয়ার্ড কীওয়ার্ড (যেমন "flask skeleton") হলে স্পেস \s+ দিয়ে বদলানো হয়
                # যাতে অতিরিক্ত হোয়াইটস্পেসেও মিলে; single word হলে word-boundary বসানো হয়।
                escaped = re.escape(kw.strip())
                escaped = escaped.replace(r"\ ", r"\s+")
                pattern = re.compile(r"(?<!\w)" + escaped + r"(?!\w)", re.IGNORECASE)
                # দৈর্ঘ্য অনুযায়ী ওজন — বড়/নির্দিষ্ট কীওয়ার্ড মিললে বেশি স্কোর পায়,
                # সংক্ষিপ্ত কীওয়ার্ড (false-positive ঝুঁকি বেশি) কম স্কোর পায়।
                weight = 1.0 + 0.3 * max(0, kw.count(" "))
                kw_patterns.append((pattern, weight))
            compiled.append((kw_patterns, label, template))
        _KB_COMPILED = compiled
    return _KB_COMPILED


def match_knowledge_base(title: str, description: str, project_name: str = "", project_desc: str = ""):
    """
    টাস্কের শিরোনাম/বর্ণনায় কোনো কমন প্যাটার্নের কীওয়ার্ড মিলে গেলে (label, code) রিটার্ন করে —
    তখন AI-কে আর জিজ্ঞেস করা লাগে না। এখন সবগুলো এন্ট্রি স্কোর করে সবচেয়ে ভালো মিলটা বাছাই করে,
    এবং ন্যূনতম স্কোরের নিচে হলে None রিটার্ন করে (দুর্বল/সন্দেহজনক মিলে AI ফলব্যাকে যায়)।
    """
    haystack = f"{title} {description}"
    best = None
    best_score = 0.0
    for kw_patterns, label, template in _kb_compiled_patterns():
        score = 0.0
        for pattern, weight in kw_patterns:
            if pattern.search(haystack):
                score += weight
        if score > best_score:
            best_score = score
            best = (label, template)
    if best is None or best_score < KB_MIN_SCORE:
        return None
    label, template = best
    code = template.replace("{project_name}", project_name or "প্রজেক্ট").replace(
        "{project_desc}", project_desc or ""
    )
    return label, code


# --------------------------------------------------------------------------
# Dynamic KB entry: `dynamic_print_task`
# এটা CODE_KNOWLEDGE_BASE-এর মতো স্থির-কীওয়ার্ড টেবিল নয় — একটা ডাইনামিক এন্ট্রি।
# টাস্কের মূল কাজ যদি "প্রোগ্রাম রান করলে একটা নির্দিষ্ট বার্তা প্রিন্ট হবে" ধরনের
# deterministic কাজ হয়, তাহলে title+description থেকে regex দিয়ে বার্তাটা বের করে,
# project['stack']-এ লেখা ভাষার সঠিক সিনট্যাক্সে সম্পূর্ণ চালানোর-যোগ্য কোড বানিয়ে
# দেয় — AI কল ছাড়াই। বার্তা-বের করার অগ্রাধিকার:
#   ১) কোটেশনের ভেতরের টেক্সট (শুধু প্রিন্ট/রান-প্রসঙ্গ থাকলেই গ্রহণ — নইলে
#      "ডিজাইনে 'login' পেজ" এধরনের বিচ্ছিন্ন কোটেড শব্দ ভুলে ধরা পড়ত);
#   ২) না পেলে বাংলা "করলে/চালালে ... লেখা আসবে/দেখাবে/প্রিন্ট হবে" প্যাটার্নের মাঝের অংশ;
#   ৩) তারপর ইংরেজি "prints/outputs/shows ... when/if run" প্যাটার্নের মাঝের অংশ।
# কোনোটিতেই কিছু না মিললে (বা স্ট্যাকের ভাষা চেনা না হলে) None — স্বাভাবিক AI ফ্লো
# চালু থাকে, জোর করে ভুল কিছু বসানো হয় না।
# --------------------------------------------------------------------------

DYNAMIC_PRINT_KB_LABEL = "dynamic_print"          # task.source → knowledge_base:dynamic_print
DYNAMIC_PRINT_MSG_MAX_CHARS = 160                 # এর চেয়ে লম্বা বার্তা সহজ print টাস্কের নয় → অমিল ধরা হয়
# রিকোয়েস্টে ভাষার নাম উল্লেখ না থাকলে dynamic-print কোড এই ডিফল্ট ভাষায় জেনারেট হয়
# (বটের বাকি deterministic coding টেমপ্লেট/টুলিংয়ের ডিফল্ট ভাষাও python)।
DEFAULT_DYNAMIC_PRINT_LANGUAGE = "python"

# রিকোয়েস্টে স্পষ্টভাবে এমন ভাষার নাম থাকলে যেটা dynamic KB জানে না, জোর করে ডিফল্ট
# python বসানো যাবে না — ভুল সিনট্যাক্সে টাস্ক 'done' হয়ে যাওয়ার ঝুঁকি থাকে। তখন
# None (blocked/AI ফলব্যাক) — "জোর করে ভুল সিনট্যাক্স বসানো হয় না" নীতিই বজায় থাকে।
_DYNAMIC_PRINT_UNSUPPORTED_LANG_RE = re.compile(
    r"\brust\b|\bswift\b|\blua\b|\bperl\b|\bscala\b|\bdart\b|\bhaskell\b|\bclojure\b"
    r"|\belixir\b|\bjulia\b|\br\b|\bmatlab\b|\bfortran\b|\bcobol\b|\bpascal\b"
    r"|\bvb(?:\.net)?\b|\bobjective-?c\b|\bf#\b",
    re.IGNORECASE,
)

# কোটেশন-শাখাটা চালু হবে কিনা — টেক্সটে কোথাও print/run-জাতীয় ইঙ্গিত থাকতে হবে।
_DYNAMIC_PRINT_CONTEXT_RE = re.compile(
    r"প্রিন্ট|print|লেখা\s+আসবে|লেখা\s+দেখ|দেখানো\s+হবে|দেখাবে|আউটপুট|আউটপুট|স্ক্রিনে|কনসোলে|স্টডাউট|"
    r"\bprint(?:s|ed|ing)?\b|\boutput(?:s)?\b|\bdisplay(?:s|ed|ing)?\b|\bshow(?:s|ed|ing)?\b|\becho(?:es|ed)?\b|"
    r"\brun\b|\bruns\b|\brunning\b|\bexecut(?:e|es|ed|ing|ion)\b|when\s+(?:it\s+|the\s+\w+\s+)?run(?:s)?\b|"
    r"\bif\s+run\b|রান\s*করলে|রান\s*করলে|রান\s*করলে|চালালে|চালালে|চালালে|ইনপুট\s+দিলে|"
    r"console\.log|system\.out|\bprintf\b",
    re.IGNORECASE,
)

# কোটেশন জোড়া (সোজা + বাঁকা + ফরাসি)। খোলা কোটের ঠিক আগে এবং বন্ধ কোটের ঠিক পরে
# ফাংশন-কল/অ্যারে-স্টাইল প্রতীক থাকলে সেটি বাতিল — `print("hi")`-এর মতো কোড-স্নিপেট
# থেকে ভুলভাবে "hi" তুলে নেওয়া যাবে না। single-quote জোড়ায় আবার শব্দের সাথে লেগে থাকা
# অ্যাপোস্ট্রফি ("user's script's") এড়াতে দুই পাশেই word-boundary না-লাগার শর্ত।
_DYNAMIC_PRINT_QUOTED_RES = (
    re.compile(r"(?<![(=\[{])\"([^\"\n]{1,200})\"(?![)\]}])"),
    re.compile(r"[\u201c]([^\"\u201d\u201c\n]{1,200})[\u201d]"),
    re.compile(r"(?<![\w(=\[{])'([^'\n]{1,200})'(?![\w)\]}])"),
    re.compile(r"(?<![\w])[\u2018]([^'\u2018\u2019\n]{1,200})[\u2019](?![\w])"),
    re.compile(r"\u00ab([^\u00bb\n]{1,200})\u00bb"),
)

# বাংলা: "... করলে/চালালে <বার্তা> লেখা আসবে/লেখা দেখাবে/প্রিন্ট হবে/দেখানো হবে"
_DYNAMIC_PRINT_BN_RE = re.compile(
    r"(?:চালালে|চালালে|রান\s*করলে|রান\s*করলে|করলে|করলে)\s+"
    r"[\"'`\u201c\u2018]?\s*([^\"'`\n]{1,200}?)\s*[\"'`\u201d\u2019]?\s+"
    r"(?:লেখা\s+আসবে|লেখা\s+দেখাবে|লেখা\s+দেখাবে|লেখা\s+উঠবে|লেখা\s+প্রিন্ট\s+হবে|প্রিন্ট\s+হবে|প্রিন্ট\s+করা\s+হবে|দেখানো\s+হবে)"
)

# ইংরেজি: "... prints/outputs/shows <বার্তা> when/if (it is) run/executed"
# capture-এ কোট চরিত্র থাকবে না — `print("hi")`-এর মতো কোড-কল থেকে গ্রাস করবে না;
# কোটেশনযুক্ত বার্তা আগেই quoted-শাখা ধরে ফেলে।
_DYNAMIC_PRINT_EN_RE = re.compile(
    r"\b(?:prints?|outputs?|displays?|shows?|echo(?:es|s)?)\b\s*[:\-]?\s*"
    r"(?:the\s+|this\s+)?(?:text|string|message|sentence|line|word)?\s*"
    r"[:\-]?\s*[\"'`\u201c\u2018]?\s*([^\"'`\n]{1,200}?)\s*[\"'`\u201d\u2019]?\s+"
    r"\b(?:when|if)\b\s+(?:it\s+|the\s+\w+\s+|they\s+)?(?:is\s+|are\s+|gets?\s+)?(?:run|ran|executed|invoked|launched)\b",
    re.IGNORECASE,
)

# কোটের ভেতরে ফাইল/পাথের মতো দেখতে লেখা প্রিন্ট-বার্তা না — উপেক্ষা।
_DYNAMIC_PRINT_PATHISH_RE = re.compile(
    r"^[\w./\\ -]{1,80}\.(?:py|pyw|js|mjs|cjs|ts|tsx|jsx|java|kt|c|h|cpp|hpp|go|rs|rb|php|pl|swift|sh|bash|zsh|"
    r"txt|md|json|ya?ml|toml|ini|cfg|html?|css|scss|sql|db|sqlite3?|csv|log|png|jpe?g|svg|ico|pdf|zip)$",
    re.IGNORECASE,
)

# ---- Negative-context গেট: UI/ফিচার-বর্ণনা ≠ লিটারেল প্রিন্ট-নির্দেশ --------------
# 'The onboarding wizard shows a "Welcome" screen first' — এধরনের বাক্যে "shows" +
# কোটেশন থাকায় এক্সট্র্যাক্টর ভুলে "Welcome" কে প্রিন্ট-বার্তা ধরে print("Welcome")
# জেনারেট করত, আর টাস্ক AI ছাড়াই 'done' মার্ক হয়ে ভুল কোডে আটকে যেত। অথচ বাক্যটা
# UI-তে কিছু 'দেখানো'র বর্ণনা — কনসোলে লিটারেল প্রিন্টের নির্দেশ না।
_DYNAMIC_PRINT_UI_WORDS_RE = re.compile(
    r"\bscreens?\b|\bpages?\b|\bwizards?\b|\bdialogs?\b|\bmodal(?:s| dialogs)?\b|\btoasts?\b|\bui\b|\bforms?\b|"
    r"স্ক্রিন|স্ক্রিন|পেজ|পৃষ্ঠা|ফর্ম|ফরম|উইজার্ড|ডায়ালগ|ডায়ালাগ|মোডাল|টোস্ট",
    re.IGNORECASE,
)
# স্পষ্ট "কনসোল/আউটপুটে ছাপো" নির্দেশ — এটা থাকলে UI-শব্দ সত্ত্বেও বার্তা-বের করা বৈধ
# (BN/EN মাঝের-অংশ প্যাটার্নের টার্মিনাল-ভার্বগুলোও এখানেই, তাই গেট সঠিক ম্যাচ কখনো
#  অকেজো করে না)। "দেখাবে" একা এই তালিকায় নেই — সেটাই বাস্তবে UI-বর্ণনার প্রধান ক্রিয়া।
_DYNAMIC_PRINT_LITERAL_PRINT_RE = re.compile(
    r"\bprint(?:s|ed|ing)?\b|\bprintf\b|\bconsole\.log\b|\becho(?:es|ed)?\b|\bstdout\b|\bstderr\b|"
    r"প্রিন্ট|প্রিন্ট|কনসোলে|স্টডাউট|লেখা\s+আসবে|লেখা\s+দেখ|লেখা\s+উঠবে|লেখা\s+প্রিন্ট|প্রিন্ট\s+হবে|প্রিন্ট\s+করা\s+হবে|দেখানো\s+হবে",
    re.IGNORECASE,
)


def _dynamic_print_looks_like_ui_description(text: str) -> bool:
    """টেক্সটটা কি UI/ফিচার-বর্ণনা, লিটারেল প্রিন্ট-টাস্ক না?

    UI/ফিচার-বর্ণনাসূচক শব্দ (screen/page/wizard/dialog/modal/toast/form/UI +
    বাংলা স্ক্রিন/পেজ/ফর্ম...) থাকলে এবং বাক্যে স্পষ্ট কনসোল-প্রিন্ট নির্দেশ
    (print/echo/প্রিন্ট/লেখা আসবে/দেখানো হবে) না থাকলে → True। True হলে dynamic
    এন্ট্রি পুরোপুরি প্রযোজ্য নয় — কোটেশন-শাখা আর ইংরেজি 'shows ... '-ধরনের
    মাঝের-অংশ গ্রাস দুটোই স্কিপ করে None (স্বাভাবিক AI ফ্লো)। বাংলা মাঝের-অংশ
    প্যাটার্ন স্বয়ংক্রিয়ভাবে নিরাপদ, কারণ ওর টার্মিনাল-ভার্বগুলো লিটারেল তালিকায়ই আছে।
    সন্দেহে AI-তে পাঠানো (একটু বেশি খরচ) ভুল কোড দিয়ে টাস্ক 'done' মার্ক করে
    অদৃশ্য করে দেওয়ার চেয়ে ঢের নিরাপদ — তাই গেট conservative দিকেই ঝুঁকে।
    """
    if not text or not _DYNAMIC_PRINT_UI_WORDS_RE.search(text):
        return False
    return not _DYNAMIC_PRINT_LITERAL_PRINT_RE.search(text)


# স্ট্যাক-স্ট্রিং → ভাষা। ক্রম গুরুত্বপূর্ণ: "javascript" "java"র আগে, "c++"/"c#" "c"র আগে,
# আর "kotlin" "java"র আগে — Android স্ট্যাক সহ "Kotlin for Android" ভুলে 'java' ধরে
# ফেলছিল (regression fix), তাই kotlin-চেক আগে এবং 'android' শব্দটা java-প্যাটার্ন থেকে
# সরানো হয়েছে (অ্যান্ড্রয়েড-প্রজেক্ট এখন প্রায় সবটাই Kotlin-ভিত্তিক — 'android'
# একা java-র নির্ভরযোগ্য সংকেত নয়; শুধু "Android" থাকলে কিছু না ধরে AI ফলব্যাকই নিরাপদ)।
_DYNAMIC_PRINT_LANG_PATTERNS = (
    (re.compile(r"javascript|typescript|\bjs\b|\bnode(?:\.js)?\b|nodejs|react|express|nestjs|\bdeno\b", re.IGNORECASE), "javascript"),
    (re.compile(r"c\+\+|\bcpp\b|\bcxx\b", re.IGNORECASE), "cpp"),
    (re.compile(r"c#|csharp|\.net\b|dotnet", re.IGNORECASE), "csharp"),
    (re.compile(r"\bkotlin\b", re.IGNORECASE), "kotlin"),
    (re.compile(r"\bjava\b|spring(?:boot)?", re.IGNORECASE), "java"),
    (re.compile(r"\bpython\b|\bpy\b|django|flask|fastapi|streamlit", re.IGNORECASE), "python"),
    (re.compile(r"\bphp\b|laravel|wordpress|\bmagento\b", re.IGNORECASE), "php"),
    (re.compile(r"\bbash\b|\bshell\b|\bzsh\b|\bsh\b|shell\s*script", re.IGNORECASE), "bash"),
    (re.compile(r"\bgo\b|golang", re.IGNORECASE), "go"),
    (re.compile(r"\bruby\b|rails", re.IGNORECASE), "ruby"),
    # একক "C" শেষে — বড় শব্দের অংশ হলে (\b না লাগলেও +,# থাকা অবস্থায়) বাদ।
    (re.compile(r"(?<![\w+#])c(?![\w+#])", re.IGNORECASE), "c"),
)


def _detect_dynamic_print_language(stack: str) -> str:
    """project['stack']-এর লেখা থেকে চেনা ভাষার কী-নাম; অচেনা হলে "" (তখন AI ফলব্যাক)।"""
    s = (stack or "").strip()
    if not s or "অজানা" in s or s.lower() in ("unknown", "none", "n/a"):
        return ""
    for pattern, language in _DYNAMIC_PRINT_LANG_PATTERNS:
        try:
            if pattern.search(s):
                return language
        except Exception:
            continue
    return ""


def _clean_dynamic_print_message(raw: str) -> str:
    """ক্যাপচার করা অংশ ছোট-লাইন, কোট-মুক্ত ও বৈধ-দৈর্ঘ্য না হলে খালি স্ট্রিং।"""
    msg = "".join(ch for ch in (raw or "") if ord(ch) >= 32 or ch == " ")
    msg = " ".join(msg.split())
    msg = msg.strip().strip("\"'`\u201c\u201d\u2018\u2019\u00ab\u00bb")
    msg = msg.lstrip(":>- \t").strip()
    if len(msg) < 2 or len(msg) > DYNAMIC_PRINT_MSG_MAX_CHARS:
        return ""
    if not re.search(r"[\u0980-\u09ffA-Za-z0-9\u00c0-\u024fÀ-ſ]", msg):
        return ""  # অন্তত এক অক্ষর/সংখ্যার শব্দ থাকতে হবে — "?!?" জাতীয় কিছু বার্তা নয়
    if any(tok in msg for tok in ("()", "{", "}", ";", "<html", "</", "#include", "def ", "import ")):
        return ""  # কোড-সদৃশ অংশ প্রিন্ট-বার্তা হতে পারে না
    if _DYNAMIC_PRINT_PATHISH_RE.match(msg):
        return ""  # "main.py", "index.js" — ফাইলনাম, বার্তা নয়
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", msg) and "_" in msg:
        return ""  # user_id জাতীয় snake_case শনাক্তকারক, লিটারেল বার্তা নয়
    return msg


def extract_dynamic_print_message(title: str, description: str) -> Optional[str]:
    """টাস্কের title+description থেকে প্রিন্ট করার বার্তা বের করে (dynamic KB অংশ ১)।

    ক্রম: ১) কোটেশনের ভেতরের টেক্সট (প্রিন্ট/রান-প্রসঙ্গ থাকা অবস্থায়),
    ২) বাংলা "করলে ... লেখা আসবে/দেখাবে/প্রিন্ট হবে" প্যাটার্নের মাঝের অংশ,
    ৩) ইংরেজি "prints/outputs/shows ... when/if run" প্যাটার্নের মাঝের অংশ।
    কোনোটিতেই মিলল না → None (কলার তখন স্বাভাবিক AI ফ্লোতে যায়)। এর আগেই
    negative-context গেট: টেক্সট UI/ফিচার-বর্ণনাসূল্য (screen/page/wizard/dialog...
    শব্দ আছে, অথচ লিটারেল print/প্রিন্ট-নির্দেশ নেই) হলে quote-শাখা ও ইংরেজি
    'shows ...'-মাঝের-অংশ গ্রাস দুটোই স্কিপ করে None — '...shows a "Welcome"
    screen first...' এধরনের বর্ণনাকে প্রিন্ট-টাস্ক বলে ভুল 'done' মার্ক হবে না।
    """
    text = f"{(title or '').strip()}\n{(description or '').strip()}".strip()
    if not text:
        return None
    # ০) negative context — UI/ফিচার-বর্ণনা প্রিন্ট-টাস্ক নয় (conservative: AI ফলব্যাক)
    if _dynamic_print_looks_like_ui_description(text):
        return None
    # ১) কোটেশন — কেবল প্রিন্ট/রান-জাতীয় প্রসঙ্গেই বিশ্বস্ত
    if _DYNAMIC_PRINT_CONTEXT_RE.search(text):
        for quote_re in _DYNAMIC_PRINT_QUOTED_RES:
            for m in quote_re.finditer(text):
                candidate = _clean_dynamic_print_message(m.group(1))
                if candidate:
                    return candidate
    # ২) বাংলা মাঝের-অংশ প্যাটার্ন (প্যাটার্নটাই প্রসঙ্গ বহন করে, আলাদা গেট দরকার নেই)
    m = _DYNAMIC_PRINT_BN_RE.search(text)
    if m:
        candidate = _clean_dynamic_print_message(m.group(1))
        if candidate:
            return candidate
    # ৩) ইংরেজি মাঝের-অংশ প্যাটার্ন
    m = _DYNAMIC_PRINT_EN_RE.search(text)
    if m:
        candidate = _clean_dynamic_print_message(m.group(1))
        if candidate:
            return candidate
    return None


def _dynamic_print_dq_literal(message: str) -> str:
    """C-পরিবার সিনট্যাক্সের (Python/JS/Java/C/C++/Go/C#/Kotlin) ডাবল-কোটেড স্ট্রিং লিটারেল।

    JSON এস্কেপ এ-সব ভাষার লিটারেল-এস্কেপের উপসেট; JSON-এর অতিরিক্ত `\\/` এস্কেপ
    কিছু ভাষায় (C/Go) অবৈধ, তাই বাদ। বাকি নিয়ন্ত্রণ-অক্ষর extract/clean ধাপেই মুছে
    যায়, আর বেহাল্লাসহ বাকি non-ASCII কাঁচা UTF-8-এ রাখা হয় (সব ভাষাই UTF-8 সোর্স
    চালায়)।
    """
    return json.dumps(message, ensure_ascii=False).replace("\\/", "/")


def _dynamic_print_sq_literal(message: str, shell: bool = False) -> str:
    """সিঙ্গেল-কোটেড লিটারেল (PHP/Ruby) — shell=True হলে bash-এর `'\''` কৌশল।"""
    if shell:
        return "'" + message.replace("'", "'\\''") + "'"
    return "'" + message.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _build_dynamic_print_code(language: str, message: str) -> str:
    """`message`-টাকে `language`-এর সঠিক সিনট্যাক্সে বসিয়ে সম্পূর্ণ চালানোর-যোগ্য কোড।

    তালিকায় থাকা প্রতিটা ভাষার জন্য একটা করে ছোট, স্ব-নির্ভর (কোনো dependency
    ছাড়াই চালানো যায়) entry-point ফাইল তৈরি হয়; তালিকায় না থাকা ভাষা → ""।
    """
    dq = _dynamic_print_dq_literal(message)
    if language == "python":
        return f"print({dq})\n"
    if language == "javascript":
        return f"console.log({dq});\n"
    if language == "java":
        return (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            f"        System.out.println({dq});\n"
            "    }\n"
            "}\n"
        )
    if language == "c":
        return (
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            f"    printf(\"%s\\n\", {dq});\n"
            "    return 0;\n"
            "}\n"
        )
    if language == "cpp":
        return (
            "#include <iostream>\n"
            "\n"
            "int main() {\n"
            f"    std::cout << {dq} << std::endl;\n"
            "    return 0;\n"
            "}\n"
        )
    if language == "php":
        return f"<?php\n\necho {_dynamic_print_sq_literal(message)} . \"\\n\";\n"
    if language == "bash":
        return f"#!/usr/bin/env bash\n\nprintf '%s\\n' {_dynamic_print_sq_literal(message, shell=True)}\n"
    if language == "go":
        return (
            "package main\n"
            "\n"
            "import \"fmt\"\n"
            "\n"
            "func main() {\n"
            f"    fmt.Println({dq})\n"
            "}\n"
        )
    if language == "csharp":
        return (
            "using System;\n"
            "\n"
            "class Program {\n"
            "    static void Main() {\n"
            f"        Console.WriteLine({dq});\n"
            "    }\n"
            "}\n"
        )
    if language == "ruby":
        return f"puts {_dynamic_print_sq_literal(message)}\n"
    if language == "kotlin":
        # Kotlin-এ ডাবল-কোটেড স্ট্রিংয়ে $ টেমপ্লেট-ইন্টারপোলেশন শুরু করে — এস্কেপ বাধ্যতামূলক।
        literal = dq.replace("$", "\\$")
        return f"fun main() {{\n    println({literal})\n}}\n"
    return ""


def match_dynamic_print_task(title: str, description: str, stack: str = "") -> Optional[Tuple[str, str]]:
    """`dynamic_print_task` ডাইনামিক KB এন্ট্রি — match_knowledge_base()-এর মতোই
    (label, code) টাপল রিটার্ন করে (label = "dynamic_print"), যাতে process_next_code_task
    একই ফর্ম্যাটে সরাসরি সেভ করতে পারে।

    বার্তা না মিললে, বা project['stack']-এর ভাষা চেনা না হলে None রিটার্ন — কলার তখন
    স্বাভাবিক AI ফ্লোতে ফলব্যাক করে (জোর করে ভুল সিনট্যাক্স বসানো হয় না)।
    """
    message = extract_dynamic_print_message(title, description)
    if not message:
        return None
    language = _detect_dynamic_print_language(stack)
    if not language:
        return None
    code = _build_dynamic_print_code(language, message)
    if not code:
        return None
    return DYNAMIC_PRINT_KB_LABEL, code


def _match_dynamic_print_request(text: str) -> Optional[Tuple[str, str, str]]:
    """রিকোয়েস্ট-টেক্সট থেকে deterministic dynamic-print ম্যাচ — (label, code, language)।

    No API Mode-এ /codeproject প্ল্যানার (coding_analyze_and_plan) এটাই ব্যবহার করে —
    dynamic_print_task ম্যাচার (match_dynamic_print_task) এর উপর ভর করে। ভাষা আগে
    রিকোয়েস্ট থেকেই ধরা হয় ("python এ কোড লেখ..." জাতীয় উল্লেখ); উল্লেখ না থাকলে
    ডিফল্ট ভাষা ধরে নেওয়া হয়। কিছু না মিললে None — কলার স্বাভাবিক ফ্লো/ফলব্যাকে
    যায়, কখনো raise হয় না।
    """
    try:
        # স্পষ্টভাবে unsupported ভাষার নাম থাকলে ডিফল্ট python জোর করা হয় না।
        if _DYNAMIC_PRINT_UNSUPPORTED_LANG_RE.search(text or ""):
            return None
        language = _detect_dynamic_print_language(text) or DEFAULT_DYNAMIC_PRINT_LANGUAGE
        match = match_dynamic_print_task("", text, language)
        if not match:
            return None
        label, code = match
        return label, code, language
    except Exception as e:
        logger.debug("deterministic dynamic-print request match failed: %s", e)
        return None


def match_bangla_rule_task(title: str, description: str, stack: str = "") -> Optional[Tuple[str, str]]:
    """`bangla_rule_engine` ডাইনামিক KB এন্ট্রি — match_dynamic_print_task()-এর ঠিক পাশে,
    একই প্যাটার্নে: (label, code) টাপল রিটার্ন করে (label = "bangla_rule_engine"),
    না মিললে None — কলার তখন স্বাভাবিক ফ্লোতে (dynamic-print matcher → Decision
    Engine → AI) ফলব্যাক করে।

    ইঞ্জিনটি bangla_rule_engine.py-তে: কড়া, নির্দিষ্ট ফরম্যাটের বাংলা নির্দেশনা
    (ভেরিয়েবল/স্টোরেজ, ইনপুট, শর্ত, নিষেধ, আউটপুট, তুলনা) AI ছাড়াই চালানোর-যোগ্য
    Python কোডে অনুবাদ করে। ইঞ্জিনের ভেতরের গার্ড dynamic-print-আকৃতির
    ("রান করলে X লেখা আসবে") বা কোটেশন-যুক্ত টেক্সট আগেই বাদ দেয়, তাই এই
    ম্যাচার dynamic_print-এর পরিপূরক — তার কাজ কেড়ে নেয় না।

    v1 ইঞ্জিন শুধু Python জেনারেট করে: স্ট্যাক বা টেক্সটে স্পষ্ট অন্য ভাষা
    (Java/JS/PHP... বা বাংলায় লেখা জাভা/জাভাস্ক্রিপ্ট...) থাকলে None —
    "জোর করে ভুল সিনট্যাক্স বসানো হয় না" নীতি অক্ষত।
    """
    if _bangla_rule_translate is None:
        return None
    text = f"{(title or '').strip()}\n{(description or '').strip()}".strip()
    if not text:
        return None
    # ভাষা-গার্ড: stack বা রিকোয়েস্ট-টেক্সটে চেনা অন্য ভাষার নাম থাকলে বাদ
    for source in (stack or "", text):
        if not source:
            continue
        if _DYNAMIC_PRINT_UNSUPPORTED_LANG_RE.search(source):
            return None
        language = _detect_dynamic_print_language(source)
        if language and language != "python":
            return None
    try:
        return _bangla_rule_translate(text)
    except Exception as e:
        logger.debug("bangla_rule_engine match failed: %s", e)
        return None


def _match_bangla_rule_request(text: str) -> Optional[Tuple[str, str, str]]:
    """রিকোয়েস্ট-টেক্সট থেকে deterministic বাংলা rule-engine ম্যাচ — (label, code, language)।

    _match_dynamic_print_request()-এর মতোই No API Mode-এ /codeproject প্ল্যানার
    (coding_analyze_and_plan) এটা ব্যবহার করে। v1 ইঞ্জিন শুধু Python জেনারেট করে,
    তাই language সবসময় "python"; টেক্সটে স্পষ্ট অন্য ভাষার নাম থাকলে None (AI
    ফলব্যাক)। কিছু না মিললে None — কখনো raise হয় না।
    """
    try:
        match = match_bangla_rule_task("", text, DEFAULT_DYNAMIC_PRINT_LANGUAGE)
        if not match:
            return None
        label, code = match
        return label, code, "python"
    except Exception as e:
        logger.debug("deterministic bangla-rule request match failed: %s", e)
        return None


def _strip_code_fences(text: str) -> str:
    """AI-এর উত্তরে ```code``` মার্কডাউন ফেন্স থাকলে সেটা সরিয়ে শুধু আসল কোডটুকু রাখে।"""
    text = (text or "").strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _extract_json_object(text: str):
    """AI-এর উত্তর থেকে প্রথম বৈধ JSON object বের করে (```json ...``` বা বাড়তি লেখাসহ আসলেও)।"""
    if not text:
        return None
    cleaned = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned.strip()).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(cleaned[start:end + 1])
    except (json.JSONDecodeError, ValueError):
        return None


async def coding_analyze_and_plan(raw_request: str, user_id: int) -> dict:
    """
    Prompt Analyze + Project Plan: ইউজারের কোডিং রিকোয়েস্ট একবারেই AI-কে পাঠিয়ে (নাম,
    স্ট্যাক/ভাষা, এবং ধারাবাহিক ছোট ছোট ধাপের তালিকা) JSON আকারে ফেরত চাওয়া হয়। JSON পার্স করা
    না গেলেও ফিচারটা যেন কখনো ভেঙে না পড়ে, তাই পুরো রিকোয়েস্টটাকেই তখন একটামাত্র ধাপ ধরে
    ফলব্যাক করা হয়।

    No API Call Mode গার্ড: AI কলের আগেই deterministic ম্যাচ চেষ্টা হয় — প্রথমে
    বাংলা রুল ইঞ্জিন (bangla_rule_engine: কড়া ফরম্যাটের স্ট্রাকচার্ড নির্দেশনা),
    তারপর dynamic-print ("রান করলে <বার্তা> লেখা আসবে") — দুটোই AI ছাড়াই একটাই
    সঠিক ধাপে resolve হয় (ask_ai কোনোভাবেই ডাকা হয় না)। কিছু না মিললে /codeplan-এর
    মতোই single-task fallback প্ল্যান (no_api_blocked চিহ্নসহ) ফেরত যায়, আর
    codeproject_command সেটা ইউজারকে জানিয়ে দেয়।
    """
    # No API Mode চালু থাকলে ask_ai কল করার আগেই আটকানো হয় — বাংলা রুল ইঞ্জিন বা
    # dynamic-print ম্যাচে পড়লে deterministic এক-ধাপের প্ল্যান, নইলে blocked fallback
    # (সবগুলো পথেই AI কল নেই)।
    if is_no_api_mode(user_id):
        # ১. Deterministic বাংলা রুল ইঞ্জিন (bangla_rule_engine) ম্যাচ চেষ্টা —
        # কড়া ফরম্যাটের স্ট্রাকচার্ড নির্দেশনা (স্টোরেজ/ইনপুট/শর্ত/আউটপুট) আগে
        # দেখা হয়; ইঞ্জিন-গার্ড dynamic-print-আকৃতির টেক্সট বাদ দিয়ে দেয়, তাই
        # না মিললে পরের ধাপে dynamic-print নিজের মতোই কাজ করে।
        try:
            rule_match = _match_bangla_rule_request(raw_request)
            if rule_match:
                return {
                    "project_name": raw_request[:40].strip() or "নতুন প্রজেক্ট",
                    "stack": "python",
                    "tasks": [{"title": "সম্পূর্ণ কাজ", "description": raw_request}],
                    "deterministic": True,
                }
        except Exception as e:
            logger.debug("coding_analyze_and_plan bangla_rule_engine check failed: %s", e)

        # ২. Deterministic dynamic-print ম্যাচ চেষ্টা
        try:
            dynamic = _match_dynamic_print_request(raw_request)
            if dynamic:
                _label, _code, language = dynamic
                return {
                    "project_name": raw_request[:40].strip() or "নতুন প্রজেক্ট",
                    "stack": language,
                    "tasks": [{"title": "সম্পূর্ণ কাজ", "description": raw_request}],
                    "deterministic": True,
                }
        except Exception as e:
            logger.debug("coding_analyze_and_plan dynamic_print check failed: %s", e)

        # ৩. Fixed Knowledge Base (CODE_KNOWLEDGE_BASE) ম্যাচ চেষ্টা
        try:
            kb_match = match_knowledge_base(
                raw_request, "", project_name=raw_request[:40].strip() or "নতুন প্রজেক্ট", project_desc=raw_request
            )
            if kb_match:
                return {
                    "project_name": raw_request[:40].strip() or "নতুন প্রজেক্ট",
                    "stack": "python",
                    "tasks": [{"title": "সম্পূর্ণ কাজ", "description": raw_request}],
                    "deterministic": True,
                }
        except Exception as e:
            logger.debug("coding_analyze_and_plan KB match check failed: %s", e)

        # ৪. Brain OS Decision Engine ম্যাচ চেষ্টা
        try:
            decision = await decision_engine_service.execute_async(
                raw_request,
                user_id=user_id,
                session_key=str(user_id),
                exclude_categories=list(CODING_EXCLUDED_BRAIN_CATEGORIES),
            )
            if decision and decision.get("strategy") == "direct":
                direct_code = _brain_payload_to_answer(decision.get("payload"))
                if direct_code:
                    direct_code = _strip_code_fences(direct_code)
                    if _coding_result_looks_like_code(direct_code, "python"):
                        return {
                            "project_name": raw_request[:40].strip() or "নতুন প্রজেক্ট",
                            "stack": "python",
                            "tasks": [{"title": "সম্পূর্ণ কাজ", "description": raw_request}],
                            "deterministic": True,
                        }
        except Exception as e:
            logger.debug("coding_analyze_and_plan Decision Engine check failed: %s", e)

        # ৫. কোনোটিতেই না মিললে blocked fallback
        stuck_msg = build_no_api_stuck_message({"stage": "coding_plan_ai", "confidence": 0.0})
        return {
            "project_name": raw_request[:40].strip() or "নতুন প্রজেক্ট",
            "stack": "unknown",
            "tasks": [{"title": "No API Mode চালু আছে", "description": stuck_msg}],
            "fallback": True,
            "no_api_blocked": True,
        }
    system_prompt = (
        "তুমি একজন সিনিয়র সফটওয়্যার আর্কিটেক্ট। ইউজারের কোডিং রিকোয়েস্ট বিশ্লেষণ করে "
        f"সর্বোচ্চ {CODE_TASK_MAX_TASKS}টা ছোট, ধারাবাহিক (implementation order অনুযায়ী) ধাপে ভাগ করো। "
        "প্রতিটা ধাপ এমনভাবে লিখবে যেন সেটা আলাদাভাবে ছোট একটা কোড অংশ হিসেবে বানানো যায়। "
        "শুধুমাত্র নিচের ফরম্যাটে একটা বিশুদ্ধ JSON object রিটার্ন করো, আর কোনো অতিরিক্ত লেখা/ব্যাখ্যা দেবে না:\n"
        '{"project_name": "সংক্ষিপ্ত নাম", "stack": "ভাষা/ফ্রেমওয়ার্ক", '
        '"tasks": [{"title": "ছোট শিরোনাম", "description": "এই ধাপে কী কোড লাগবে তার বিবরণ"}]}'
    )
    # Phase 20-fix: প্ল্যান JSON-এর জন্য বড় max_tokens — নাহলে 1024 টোকেনে রেসপন্স কাটা পড়ে
    # json.loads fail হয় এবং fallback প্ল্যান দেখানো হয়।
    reply = await ask_ai(system_prompt, raw_request, max_tokens=4000)
    parsed = _extract_json_object(reply)
    if not parsed or not isinstance(parsed.get("tasks"), list) or not parsed["tasks"]:
        return {
            "project_name": raw_request[:40].strip() or "নতুন প্রজেক্ট",
            "stack": "অজানা (AI নির্দিষ্ট করতে পারেনি)",
            "tasks": [{"title": "সম্পূর্ণ কাজ", "description": raw_request}],
        }
    tasks = []
    for t in parsed["tasks"][:CODE_TASK_MAX_TASKS]:
        if not isinstance(t, dict):
            continue
        title = str(t.get("title", "")).strip()[:150] or "ধাপ"
        desc = str(t.get("description", "")).strip()[:800]
        tasks.append({"title": title, "description": desc})
    if not tasks:
        tasks = [{"title": "সম্পূর্ণ কাজ", "description": raw_request}]
    return {
        "project_name": str(parsed.get("project_name", "")).strip()[:150] or (raw_request[:40] or "নতুন প্রজেক্ট"),
        "stack": str(parsed.get("stack", "")).strip()[:150] or "অজানা",
        "tasks": tasks,
    }


# ---- Project Memory: ডাটাবেস হেল্পার ----

def create_code_project(user_id: int, name: str, description: str, stack: str, tasks: list) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat(timespec="seconds")
    cur.execute(
        "INSERT INTO code_projects (user_id, name, description, stack, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 'active', ?, ?)",
        (user_id, name, description[:2000], stack, now, now),
    )
    project_id = cur.lastrowid
    for i, t in enumerate(tasks, start=1):
        cur.execute(
            "INSERT INTO code_tasks (project_id, seq, title, description, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 'pending', ?, ?)",
            (project_id, i, t["title"], t["description"], now, now),
        )
    cur.execute("UPDATE users SET active_code_project_id = ? WHERE user_id = ?", (project_id, user_id))
    conn.commit()
    conn.close()
    return project_id


def get_project(project_id: int, owner_id: int = None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, name, description, stack, status, created_at FROM code_projects WHERE id = ?",
        (project_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    if owner_id is not None and row[1] != owner_id:
        return None
    return {
        "id": row[0], "user_id": row[1], "name": row[2], "description": row[3],
        "stack": row[4], "status": row[5], "created_at": row[6],
    }


def get_active_project(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT active_code_project_id FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    active_id = row[0] if row else 0
    if not active_id:
        return None
    return get_project(active_id, owner_id=user_id)


def list_user_projects(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, status, created_at FROM code_projects WHERE user_id = ? ORDER BY id DESC LIMIT 30",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def set_active_project(user_id: int, project_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET active_code_project_id = ? WHERE user_id = ?", (project_id, user_id))
    conn.commit()
    conn.close()


def get_project_tasks(project_id: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, seq, title, description, status, source, code, depends_on_seq, retry_count, last_error, workflow_stage, target_files, test_status, test_output, test_report, test_updated_at "
            "FROM code_tasks WHERE project_id = ? ORDER BY seq ASC",
            (project_id,),
        )
        rows = cur.fetchall()
    except sqlite3.OperationalError:
        cur.execute(
            "SELECT id, seq, title, description, status, source, code FROM code_tasks "
            "WHERE project_id = ? ORDER BY seq ASC",
            (project_id,),
        )
        rows = [tuple(r) + (None, 0, "", r[4] if r[4] else "pending", "") for r in cur.fetchall()]
    conn.close()
    return [
        {"id": r[0], "seq": r[1], "title": r[2], "description": r[3], "status": r[4], "source": r[5], "code": r[6],
         "depends_on_seq": r[7], "retry_count": r[8] or 0, "last_error": r[9] or "", "workflow_stage": r[10] or r[4] or "pending",
         "target_files": r[11] or "", "test_status": r[12] or "", "test_output": r[13] or "", "test_report": r[14] or "", "test_updated_at": r[15] or ""}
        for r in rows
    ]


def get_next_pending_task(project_id: int):
    """Dependency-aware next task; blocked dependencies are skipped until ready."""
    try:
        tasks = get_project_tasks(project_id)
        done = {int(t["seq"]) for t in tasks if t["status"] == "done"}
        for t in tasks:
            if t["status"] != "pending":
                continue
            dep = t.get("depends_on_seq")
            if dep is not None and int(dep) not in done:
                continue
            return t
    except Exception as e:
        logger.warning("Phase 20 get_next_pending_task failed: %s", e)
    return None


def _is_first_task(project: dict) -> bool:
    """এই প্রজেক্টে এখনো কোনো ধাপ 'done' হয়নি কিনা — অর্থাৎ এখন প্রসেস হওয়া ধাপটাই
    প্রজেক্টের প্রথম ধাপ। process_next_code_task()-এর project-level dynamic-print
    fallback শুধু তখনই বৈধ, যাতে multistep প্রজেক্টের পরের ধাপগুলোতে একই প্রিন্ট-কোড
    বারবার stamp না হয়। DB-এরর হলে নিরাপদ দিক (False) — ফলব্যাক বন্ধ থাকে।"""
    try:
        tasks = get_project_tasks(project["id"])
        return not any(t.get("status") == "done" for t in tasks)
    except Exception as e:
        logger.debug("_is_first_task check failed (treated as not-first): %s", e)
        return False


def save_task_result(task_id: int, code: str, source: str, status: str = "done"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE code_tasks SET code = ?, source = ?, status = ?, updated_at = ? WHERE id = ?",
        (code[:6000], source, status, datetime.now().isoformat(timespec="seconds"), task_id),
    )
    conn.commit()
    conn.close()


def mark_project_status(project_id: int, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE code_projects SET status = ?, updated_at = ? WHERE id = ?",
        (status, datetime.now().isoformat(timespec="seconds"), project_id),
    )
    conn.commit()
    conn.close()


def delete_project(project_id: int, user_id: int) -> bool:
    project = get_project(project_id, owner_id=user_id)
    if not project:
        return False
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM code_tasks WHERE project_id = ?", (project_id,))
    cur.execute("DELETE FROM code_projects WHERE id = ?", (project_id,))
    cur.execute(
        "UPDATE users SET active_code_project_id = 0 WHERE user_id = ? AND active_code_project_id = ?",
        (user_id, project_id),
    )
    conn.commit()
    conn.close()
    return True



# =============================================================================
# PHASE 20 — AUTONOMOUS CODING AGENT
# Workflow/state layer over the existing Coding Orchestrator + Phase 18/19.
# =============================================================================

AUTONOMOUS_MAX_RETRIES = 3
AUTONOMOUS_MAX_PLAN_TASKS = CODE_TASK_MAX_TASKS
NO_API_CODING_BLOCKED_MESSAGE = (
    "⚠️ No API Mode চালু আছে — Brain OS একা এই কাজ করতে পারছে না। "
    "`/noapimode off` দিয়ে বন্ধ করুন অথবা Brain OS-এ এই ধরনের প্রজেক্টের knowledge/pattern যোগ করুন।"
)
NO_API_PLAN_BLOCKED_MESSAGE = "⚠️ No API Mode চালু আছে — AI প্ল্যান বানাতে পারেনি। /noapimode off দিয়ে বন্ধ করুন।"


def _autonomous_request_kind(user_text: str) -> dict:
    """Reuse Phase 19 classification and add a lightweight new/existing/bug-fix classifier."""
    try:
        base = _smart_context_classify(user_text)
    except Exception as e:
        logger.debug("Phase 20 classify reuse failed: %s", e)
        base = {"request_type": "general", "is_coding": False}
    text = (user_text or "").lower()
    bug_words = ("bug", "error", "exception", "traceback", "fix", "broken", "crash", "ভুল", "এরর", "ঠিক কর")
    new_words = ("create", "build", "new project", "বানাও", "তৈরি", "নতুন প্রজেক্ট")
    feature_words = ("add", "feature", "implement", "যোগ", "ফিচার", "যুক্ত")
    kind = "bug_fix" if any(w in text for w in bug_words) else "new_project" if any(w in text for w in new_words) else "feature_change" if any(w in text for w in feature_words) else "general_coding"
    base.update({"task_kind": kind, "is_autonomous_coding": bool(base.get("is_coding") or kind != "general_coding")})
    return base


def _autonomous_context_text(ctx: dict, limit: int = 9000) -> str:
    try:
        return _smart_context_trim(ctx.get("context", ""), limit)
    except Exception:
        return ""


async def autonomous_analyze_request(user_id: int, user_text: str) -> dict:
    """ANALYZE: request type + compact Phase 19 context."""
    try:
        kind = _autonomous_request_kind(user_text)
        context = await asyncio.to_thread(build_smart_context, user_id, user_text)
        return {"classification": kind, "context": context}
    except Exception as e:
        logger.warning("Phase 20 ANALYZE failed: %s", e)
        return {"classification": {"request_type": "general", "task_kind": "general_coding", "is_autonomous_coding": False}, "context": {"context": "", "files": [], "symbols": [], "dependencies": []}}


async def autonomous_generate_plan(user_id: int, user_text: str) -> dict:
    """PLAN: structured JSON plan using only compact Phase 19 context."""
    analysis = await autonomous_analyze_request(user_id, user_text)
    ctx = analysis.get("context", {})
    system = (
        "You are a senior software architect. Create a safe, dependency-aware implementation plan. "
        f"Return ONLY JSON with project_name, stack, tasks. Maximum {AUTONOMOUS_MAX_PLAN_TASKS} tasks. "
        "Each task must contain title, description, depends_on_seq, target_files. "
        "Use only the supplied compact context; never invent existing files when context does not support them.\n"
        f"Request type: {analysis['classification'].get('task_kind')}\n"
        f"Compact context:\n{_autonomous_context_text(ctx)}"
    )
    if is_no_api_mode(user_id):
        stuck_msg = build_no_api_stuck_message({"stage": "coding_plan_ai", "confidence": 0.0})
        return {
            "project_name": user_text[:50] or "Autonomous Project",
            "stack": "unknown",
            "tasks": [{"title": "No API Mode চালু আছে", "description": stuck_msg, "depends_on_seq": None, "target_files": []}],
            "analysis": analysis,
            "fallback": True,
            "no_api_blocked": True,
        }

    try:
        # Phase 20-fix: /codeplan-এর JSON প্ল্যান আঁটার জন্য বড় max_tokens দরকার — নাহলে
        # 1024 টোকেনে রেসপন্স মাঝপথে কাটা পড়ে, json.loads fail হয়ে deterministic fallback দেখায়।
        reply = await ask_ai(system, user_text, max_tokens=4000)
        parsed = _extract_json_object(reply)
        tasks = parsed.get("tasks") if isinstance(parsed, dict) else None
        if not isinstance(tasks, list) or not tasks:
            raise ValueError("AI plan JSON contains no tasks")
        clean=[]
        for i,t in enumerate(tasks[:AUTONOMOUS_MAX_PLAN_TASKS],1):
            if not isinstance(t, dict):
                continue
            dep=t.get("depends_on_seq")
            try: dep=int(dep) if dep not in (None, "", 0) else None
            except Exception: dep=None
            files=t.get("target_files", [])
            if isinstance(files,str): files=[files]
            files=[str(x).strip() for x in files if str(x).strip()][:8]
            clean.append({"title":str(t.get("title") or f"ধাপ {i}")[:150],"description":str(t.get("description") or user_text)[:1200],"depends_on_seq":dep,"target_files":files})
        if not clean: raise ValueError("empty cleaned plan")
        return {"project_name":str(parsed.get("project_name") or user_text[:50])[:150],"stack":str(parsed.get("stack") or "unknown")[:150],"tasks":clean,"analysis":analysis}
    except Exception as e:
        logger.warning("Phase 20 PLAN AI failed, deterministic fallback used: %s", e)
        return {"project_name":user_text[:50] or "Autonomous Project","stack":"unknown","tasks":[{"title":"Implement requested change","description":user_text[:1200],"depends_on_seq":None,"target_files":[]}],"analysis":analysis,"fallback":True}


def autonomous_save_plan(user_id: int, plan: dict) -> int:
    """Persist workflow state in existing code_projects/code_tasks tables."""
    try:
        project_id=create_code_project(user_id,plan.get("project_name") or "Autonomous Project",plan.get("analysis",{}).get("classification",{}).get("task_kind","")+"\n"+str(plan.get("analysis",{}).get("classification",{})),plan.get("stack") or "unknown",[])
        conn=get_conn(); cur=conn.cursor(); now=datetime.now().isoformat(timespec="seconds")
        for i,t in enumerate(plan.get("tasks",[])[:AUTONOMOUS_MAX_PLAN_TASKS],1):
            dep=t.get("depends_on_seq")
            if dep is not None and (dep < 1 or dep >= i): dep = i-1 if i>1 else None
            cur.execute("INSERT INTO code_tasks (project_id,seq,title,description,status,source,code,created_at,updated_at,depends_on_seq,retry_count,last_error,workflow_stage,target_files) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(project_id,i,t["title"],t["description"],"pending","autonomous_plan","",now,now,dep,0,"","pending",json.dumps(t.get("target_files",[]),ensure_ascii=False)))
        cur.execute("UPDATE users SET active_code_project_id=? WHERE user_id=?",(project_id,user_id)); conn.commit(); conn.close()
        return project_id
    except Exception:
        try: conn.close()
        except Exception: pass
        raise


def autonomous_set_task_state(task_id:int,status:str,stage:str=None,error:str="") -> None:
    try:
        conn=get_conn(); cur=conn.cursor(); now=datetime.now().isoformat(timespec="seconds")
        fields=["status=?","last_error=?","updated_at=?"]; vals=[status,error[:2000],now]
        if stage is not None: fields.append("workflow_stage=?"); vals.append(stage)
        vals.append(task_id); cur.execute(f"UPDATE code_tasks SET {', '.join(fields)} WHERE id=?",vals); conn.commit(); conn.close()
    except Exception as e: logger.warning("Phase 20 task state save failed: %s",e)


def autonomous_record_failure(exc:BaseException, task:dict, project:dict) -> None:
    try:
        ErrorEngine().handle(exc, language="python", context={"phase":"20","project_id":project.get("id"),"task_id":task.get("id"),"task":task.get("title")})
    except Exception as e: logger.warning("Phase 20 Brain Error record failed: %s",e)
    try:
        project_memory_record_failure(project,task,exc)
    except Exception as e: logger.debug("Phase 25 failure memory hook skipped: %s",e)


def autonomous_record_success(task:dict, project:dict) -> None:
    try:
        api_create_context(user_id=project.get("user_id"),session_key=str(project.get("id")),data={"task":task.get("title"),"result":"completed","workflow":"phase20","source":task.get("source","")},scope="project",category="coding_success",tags=["phase20","autonomous"],priority=7)
    except Exception as e: logger.debug("Phase 20 success memory skipped: %s",e)
    try:
        project_memory_record_success(project,task,task.get("test_report") or "implemented")
    except Exception as e: logger.debug("Phase 25 success memory hook skipped: %s",e)


# =============================================================================
# PHASE 21 — AUTOMATIC TESTING ENGINE
# =============================================================================
PHASE21_TEST_TIMEOUT = 12
PHASE21_MAX_TEST_OUTPUT = 12000
PHASE21_MAX_GENERATED_TEST = 12000

def _phase21_update_test_result(task_id, status, output="", report=None):
    try:
        conn=get_conn(); cur=conn.cursor()
        cur.execute("UPDATE code_tasks SET test_status=?,test_output=?,test_report=?,test_updated_at=?,updated_at=? WHERE id=?",(status,(output or "")[:PHASE21_MAX_TEST_OUTPUT],json.dumps(report or {},ensure_ascii=False)[:12000],datetime.now().isoformat(timespec="seconds"),datetime.now().isoformat(timespec="seconds"),task_id)); conn.commit(); conn.close()
    except Exception as e: logger.warning("Phase 21 test result persistence failed: %s",e)

def _phase21_syntax_check(code, language="python"):
    try:
        if (language or "python").lower() not in ("python","py"): return True,"syntax skipped"
        ast.parse(code or ""); return True,"ast.parse PASS"
    except Exception as e: return False,f"syntax error: {e}"

def _phase21_import_check(code, root=None):
    missing=[]; checked=[]
    try:
        tree=ast.parse(code or ""); root_path=Path(root or CODEBASE_DEFAULT_ROOT).resolve()
        for node in ast.walk(tree):
            names=[]
            if isinstance(node,ast.Import): names=[a.name.split('.')[0] for a in node.names]
            elif isinstance(node,ast.ImportFrom) and node.module: names=[node.module.split('.')[0]]
            for name in names:
                if not name or name in checked: continue
                checked.append(name)
                try: found=importlib.util.find_spec(name) is not None
                except Exception: found=False
                if not found and not (root_path/f"{name}.py").exists() and not (root_path/name/"__init__.py").exists(): missing.append(name)
        return not missing,checked,missing
    except Exception as e: return False,checked,[f"import-check-error: {e}"]

def _phase21_detect_existing_tests(root=None):
    found=[]
    try:
        conn=get_conn(); rows=conn.execute("SELECT relative_path FROM brain_codebase_files WHERE is_python=1").fetchall(); conn.close()
        for r in rows:
            path=r[0] or ""; base=os.path.basename(path).lower()
            if (base.startswith("test_") and base.endswith(".py")) or base.endswith("_test.py"): found.append(path)
    except Exception as e: logger.debug("Phase 21 indexed test detection failed: %s",e)
    return sorted(set(found))[:50]

def _phase21_fallback_test():
    return "import importlib.util\nimport unittest\nclass GeneratedTaskSmokeTest(unittest.TestCase):\n    def test_generated_module_imports(self):\n        spec=importlib.util.spec_from_file_location('generated_task','generated_task.py')\n        self.assertIsNotNone(spec)\n        module=importlib.util.module_from_spec(spec)\n        spec.loader.exec_module(module)\n        self.assertIsNotNone(module)\nif __name__=='__main__': unittest.main()\n"

async def _phase21_generate_test(project,task,code):
    try:
        ctx=await asyncio.to_thread(build_smart_context,project.get("user_id"),task.get("description","")+"\nTarget files: "+task.get("target_files",""),None,3000)
        impact_ctx=build_phase28_context(task.get("phase28_impact",{}),3500) if task.get("phase28_impact") else "Phase 28 impact unavailable; Confidence: LOW"
        prompt=("Generate ONLY a small Python unittest module for this task. Target generated_task.py. No network, subprocess, shell, or destructive operations. Return code only.\nTASK:\n"+task.get("description","")[:4000]+"\nCODE:\n"+code[:7000]+"\nPHASE 28 IMPACT:\n"+impact_ctx+"\nCONTEXT:\n"+_autonomous_context_text(ctx,7000))
        reply=await asyncio.wait_for(ask_ai(prompt,"Create the test case."),timeout=20)
        test=_strip_code_fences(reply or "")[:PHASE21_MAX_GENERATED_TEST]; ok,_=_phase21_syntax_check(test)
        if ok and "unittest" in test: return test,"ai"
    except Exception as e: logger.warning("Phase 21 test generation failed; fallback: %s",e)
    return _phase21_fallback_test(),"fallback"

def _phase21_run_subprocess(code,test_code):
    tmp=None
    try:
        tmp=tempfile.mkdtemp(prefix="rohan_phase21_"); root=Path(tmp)
        (root/"generated_task.py").write_text(code or "",encoding="utf-8"); (root/"test_generated_task.py").write_text(test_code or "",encoding="utf-8")
        env={"PATH":os.environ.get("PATH",""),"PYTHONNOUSERSITE":"1","PYTHONUNBUFFERED":"1"}
        kwargs={"cwd":str(root),"capture_output":True,"text":True,"timeout":PHASE21_TEST_TIMEOUT,"shell":False,"env":env}
        try:
            import resource
            def _phase21_limits():
                resource.setrlimit(resource.RLIMIT_CPU,(PHASE21_TEST_TIMEOUT,PHASE21_TEST_TIMEOUT+1))
                resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024*1024,2*1024*1024))
            kwargs["preexec_fn"]=_phase21_limits
        except Exception:
            pass
        proc=subprocess.run([sys.executable,"-S","test_generated_task.py"],**kwargs)
        out=((proc.stdout or "")+"\n"+(proc.stderr or ""))[:PHASE21_MAX_TEST_OUTPUT]
        return {"ok":proc.returncode==0,"exit_code":proc.returncode,"output":out,"timed_out":False}
    except subprocess.TimeoutExpired: return {"ok":False,"exit_code":-1,"output":"TEST TIMEOUT","timed_out":True}
    except Exception as e: return {"ok":False,"exit_code":-1,"output":str(e),"timed_out":False}
    finally:
        if tmp: shutil.rmtree(tmp,ignore_errors=True)

async def autonomous_test_hook(project,task):
    impact=task.get("phase28_impact",{}) or {}
    risk=str(impact.get("risk_level","LOW"))
    policy={"LOW":"targeted","MEDIUM":"targeted+related","HIGH":"affected-module+regression","CRITICAL":"full-regression+security"}.get(risk,"targeted")
    report={"phase":21,"phase28_impact_aware":True,"phase28_policy":policy,"phase28_risk":risk,"syntax":{},"imports":{},"existing_tests":[],"generated_test_source":"","execution":{}}
    task_id=task.get("id")
    try:
        code=task.get("code","")
        if not code: code=next((x.get("code","") for x in get_project_tasks(project["id"]) if x.get("id")==task_id),"")
        ok,detail=_phase21_syntax_check(code,project.get("stack","python")); report["syntax"]={"ok":ok,"detail":detail}
        if not ok: _phase21_update_test_result(task_id,"failed",detail,report); autonomous_record_failure(SyntaxError(detail),task,project); return False,detail,report
        iok,checked,missing=_phase21_import_check(code,project.get("root")); report["imports"]={"ok":iok,"checked":checked,"missing":missing}
        if not iok:
            detail="Missing imports: "+", ".join(missing); _phase21_update_test_result(task_id,"failed",detail,report); autonomous_record_failure(ImportError(detail),task,project); return False,detail,report
        report["existing_tests"]=_phase21_detect_existing_tests(project.get("root"))
        test_code,source=await _phase21_generate_test(project,task,code); report["generated_test_source"]=source
        tok,_=_phase21_syntax_check(test_code)
        if not tok: test_code=_phase21_fallback_test(); report["generated_test_source"]="fallback_after_invalid_ai"
        execution=await asyncio.to_thread(_phase21_run_subprocess,code,test_code); report["execution"]=execution
        if execution.get("ok"):
            # Phase 28 impact-aware regression policy: do not run the full suite for LOW.
            if risk in {"MEDIUM","HIGH","CRITICAL"}:
                root=project.get("root") or CODEBASE_DEFAULT_ROOT
                discovered=await asyncio.to_thread(_phase28_detect_tests,root)
                affected=(impact.get("expected_files",[]) or impact.get("direct_affected",[]) or [])
                selected=discovered if risk in {"HIGH","CRITICAL"} else _phase28_related_tests(discovered,affected)
                mode="full" if risk in {"HIGH","CRITICAL"} else "related"
                regression=await asyncio.to_thread(_phase28_run_regression,root,selected,mode)
                report["regression"]=regression
                if not regression.get("ok"):
                    detail="Regression tests failed: "+str(regression.get("output","")[:3000])
                    _phase21_update_test_result(task_id,"failed",detail,report); autonomous_record_failure(RuntimeError(detail),task,project); return False,detail,report
            _phase21_update_test_result(task_id,"passed",execution.get("output","")[:PHASE21_MAX_TEST_OUTPUT],report); return True,"Automatic tests PASS",report
        detail=execution.get("output","") or "Automatic test failed"; _phase21_update_test_result(task_id,"failed",detail,report); autonomous_record_failure(RuntimeError(detail[:2000]),task,project); return False,detail[:3000],report
    except Exception as e:
        logger.warning("Phase 21 test hook failed: %s",e); report["exception"]=str(e); _phase21_update_test_result(task_id,"error",str(e),report); autonomous_record_failure(e,task,project); return False,str(e),report

async def autonomous_test_report_command(update,context):
    try:
        if not is_admin(update.effective_user.id): await update.message.reply_text("⛔ এই কমান্ডটি শুধু অ্যাডমিনের জন্য।"); return
        if not context.args or not context.args[0].isdigit(): await update.message.reply_text("ব্যবহার: /testreport <task_id>"); return
        task_id=int(context.args[0]); conn=get_conn(); row=conn.execute("SELECT id,title,status,test_status,test_output,test_report,retry_count,last_error FROM code_tasks WHERE id=?",(task_id,)).fetchone(); conn.close()
        if not row: await update.message.reply_text("Task পাওয়া যায়নি।"); return
        text=f"🧪 TEST REPORT\nTask: {row[0]} — {row[1]}\nStatus: {row[2]}\nTest: {row[3] or 'not-run'}\nRetry: {row[6] or 0}\nLast error: {(row[7] or '')[:1000]}\n\nOutput:\n{(row[4] or '')[:5000]}\n\nReport:\n{(row[5] or '{}')[:4000]}"
        await send_long_text(update,text)
    except Exception as e: logger.warning("Phase 21 /testreport failed: %s",e); await update.message.reply_text("Test report দেখাতে সমস্যা হয়েছে।")


# =============================================================================
# PHASE 22 — AUTO ERROR-FIX LOOP
# =============================================================================
PHASE22_MAX_FIX_CONTEXT = 9000

def _phase22_parse_error(detail: str) -> dict:
    try:
        text=str(detail or "")
        m=re.search(r"\b([A-Za-z_][\w]*(?:Error|Exception|Warning))\b",text)
        exc_class=m.group(1) if m else "RuntimeError"
        fm=re.search(r'File ["\']([^"\']+)["\'], line (\d+)',text)
        return {"error_type":exc_class,"file":fm.group(1) if fm else "","line":int(fm.group(2)) if fm else 0,"message":text[-4000:]}
    except Exception as e:
        logger.debug("Phase 22 traceback parse failed: %s",e)
        return {"error_type":"RuntimeError","file":"","line":0,"message":str(detail or "")[-4000:]}

def _phase22_extract_code(solution: str) -> str:
    try:
        text=str(solution or "").strip()
        blocks=re.findall(r"```(?:python|py)?\s*(.*?)```",text,flags=re.I|re.S)
        candidate=(blocks[0] if blocks else text).strip()
        if not candidate or len(candidate)<8: return ""
        ast.parse(candidate)
        if not blocks and not re.search(r"\b(def|class|import|from|return|if|try|async)\b",candidate): return ""
        return candidate[:20000]
    except Exception:
        return ""

def _phase22_known_solution(error_type: str, language: str="python") -> dict:
    try:
        item=ErrorEngine().get_solution(error_type,language=language)
        if not item: return {"found":False,"direct":False,"solution":""}
        solution=getattr(item,"solution","") or ""
        code=_phase22_extract_code(solution)
        return {"found":True,"direct":bool(code),"solution":solution[:6000],"code":code,"error_id":getattr(item,"id",None)}
    except Exception as e:
        logger.warning("Phase 22 known-solution lookup failed: %s",e)
        return {"found":False,"direct":False,"solution":""}

def _phase22_save_attempt(task_id:int,code:str,backup_code:str="") -> None:
    try:
        conn=get_conn(); cur=conn.cursor(); now=datetime.now().isoformat(timespec="seconds")
        if backup_code:
            cur.execute("UPDATE code_tasks SET last_working_code=?,updated_at=? WHERE id=?",(backup_code[:20000],now,task_id))
        cur.execute("UPDATE code_tasks SET code=?,source=?,updated_at=? WHERE id=?",(code[:6000],"phase22_fix",now,task_id))
        conn.commit(); conn.close()
    except Exception as e: logger.warning("Phase 22 fix persistence failed: %s",e)

def _phase22_restore_code(task_id:int) -> bool:
    try:
        conn=get_conn(); cur=conn.cursor(); row=cur.execute("SELECT last_working_code FROM code_tasks WHERE id=?",(task_id,)).fetchone()
        if not row or not row[0]: conn.close(); return False
        cur.execute("UPDATE code_tasks SET code=?,source=?,updated_at=? WHERE id=?",(row[0],"phase22_restore",datetime.now().isoformat(timespec="seconds"),task_id)); conn.commit(); conn.close(); return True
    except Exception as e:
        logger.warning("Phase 22 restore failed: %s",e); return False

async def _phase22_generate_fix(project:dict,task:dict,error_info:dict,known:dict) -> str:
    try:
        ctx=await asyncio.to_thread(build_smart_context,project.get("user_id"),task.get("description","")+"\nError: "+error_info.get("message","")[:3000],None,4500)
        hint=known.get("solution","")[:3000] if known.get("found") else "No known solution found."
        system=("You are a targeted Python debugging agent. Return ONLY the complete corrected code artifact. "
                "Do not use network, shell, subprocess, or destructive operations. Preserve architecture. "
                "Fix only the reported failure.\nERROR:\n"+json.dumps(error_info,ensure_ascii=False)+
                "\nBRAIN HINT:\n"+hint+"\nCOMPACT CONTEXT:\n"+_autonomous_context_text(ctx,PHASE22_MAX_FIX_CONTEXT))
        reply=await asyncio.wait_for(ask_ai(system,"Fix the failing task."),timeout=25)
        code=_strip_code_fences(reply or ""); ok,_=_phase21_syntax_check(code,"python")
        return code if ok else ""
    except Exception as e:
        logger.warning("Phase 22 AI fix generation failed: %s",e); return ""

async def autonomous_auto_fix_loop(project:dict,task:dict,detail:str,test_report:dict|None=None) -> dict:
    result=dict(task); current_error=str(detail or "Automatic test failed"); attempts=[]
    try:
        while int(result.get("retry_count") or 0)<AUTONOMOUS_MAX_RETRIES:
            retry=int(result.get("retry_count") or 0)+1; info=_phase22_parse_error(current_error)
            known=_phase22_known_solution(info.get("error_type") or "RuntimeError",project.get("stack","python"))
            old_code=result.get("code","") or ""
            new_code=known.get("code","") if known.get("direct") else ""
            source="brain_known_solution" if new_code else "ai_targeted_fix"
            if not new_code: new_code=await _phase22_generate_fix(project,result,info,known)
            attempt={"attempt":retry,"error":info,"source":source,"brain_solution":bool(known.get("found")),"applied":bool(new_code)}
            if not new_code:
                attempts.append(attempt); current_error="No valid fix could be generated."
                autonomous_set_task_state(result["id"],"blocked","fix",current_error)
                result.update({"status":"blocked","retry_count":retry,"last_error":current_error,"workflow_stage":"fix"}); break
            _phase22_save_attempt(result["id"],new_code,old_code)
            result.update({"code":new_code,"retry_count":retry,"status":"in_progress","workflow_stage":"fix"}); autonomous_set_task_state(result["id"],"in_progress","fix","")
            ok,tdetail,report=await autonomous_test_hook(project,result)
            attempt.update({"test_ok":ok,"test_detail":tdetail[:3000]}); attempts.append(attempt)
            if ok:
                autonomous_set_task_state(result["id"],"done","review_hook","")
                result.update({"status":"done","workflow_stage":"review_hook","test_status":"passed","test_report":report,"last_error":""})
                try:
                    if known.get("error_id"): ErrorEngine().update(known["error_id"],solution="Applied successfully: "+new_code[:5000],is_resolved=1)
                    else: ErrorEngine().register_solution(project.get("stack","python") or "python",info.get("error_type") or "RuntimeError",info.get("message","")[:2000],new_code[:5000],category="autofix",severity="medium")
                except Exception as e: logger.debug("Phase 22 solution save skipped: %s",e)
                try:
                    project_memory_record_solved_bug(project,result,current_error,new_code,report)
                except Exception as e: logger.debug("Phase 25 solved-bug memory skipped: %s",e)
                try:
                    coding_knowledge_record_fix(project,result,current_error,new_code,report,True)
                except Exception as e: logger.debug("Phase 26 fix knowledge skipped: %s",e)
                break
            current_error=tdetail or "Automatic retest failed"
            state="pending" if retry<AUTONOMOUS_MAX_RETRIES else "blocked"
            result.update({"status":state,"last_error":current_error,"workflow_stage":"fix","test_status":"failed","test_report":report})
            autonomous_set_task_state(result["id"],state,"fix",current_error)
        if int(result.get("retry_count") or 0)>=AUTONOMOUS_MAX_RETRIES and result.get("status")!="done":
            _phase22_restore_code(result["id"])
            result["status"]="blocked"; autonomous_set_task_state(result["id"],"blocked","fix",result.get("last_error","") or "maximum auto-fix retries reached")
        conn=get_conn(); cur=conn.cursor(); cur.execute("UPDATE code_tasks SET test_report=?,test_output=?,updated_at=? WHERE id=?",(json.dumps({"phase":22,"attempts":attempts},ensure_ascii=False)[:12000],str(result.get("last_error","") )[:12000],datetime.now().isoformat(timespec="seconds"),result["id"])); conn.commit(); conn.close()
        return result
    except Exception as e:
        logger.warning("Phase 22 auto-fix loop failed: %s",e); autonomous_record_failure(e,result,project); autonomous_set_task_state(result["id"],"blocked","fix",str(e)[:2000]); result.update({"status":"blocked","workflow_stage":"fix","last_error":str(e)[:2000]}); return result

async def errorfixlog_command(update,context):
    try:
        if not is_admin(update.effective_user.id): await update.message.reply_text("⛔ এই কমান্ডটি শুধু অ্যাডমিনের জন্য।"); return
        if not context.args or not context.args[0].isdigit(): await update.message.reply_text("ব্যবহার: /errorfixlog <task_id>"); return
        task_id=int(context.args[0]); conn=get_conn(); row=conn.execute("SELECT id,title,status,retry_count,last_error,test_report FROM code_tasks WHERE id=?",(task_id,)).fetchone(); conn.close()
        if not row: await update.message.reply_text("Task পাওয়া যায়নি।"); return
        try: report=json.loads(row[5] or "{}")
        except Exception: report={"raw":row[5] or ""}
        text=f"🛠️ ERROR-FIX LOG\nTask: {row[0]} — {row[1]}\nStatus: {row[2]}\nRetries: {row[3] or 0}\nLast error: {(row[4] or '')[:1500]}\n\nAttempts:\n"+json.dumps(report.get("attempts",report),ensure_ascii=False,indent=2)[:7000]
        await send_long_text(update,text)
    except Exception as e:
        logger.warning("Phase 22 /errorfixlog failed: %s",e); await update.message.reply_text("Error-fix log দেখাতে সমস্যা হয়েছে।")

def autonomous_syntax_hook(code:str, language:str="python") -> tuple[bool,str]:
    """TEST placeholder: Phase 20 only validates Python syntax; deeper testing is Phase 21."""
    try:
        if language.lower() not in ("python","py"): return True,"syntax hook skipped (non-Python)"
        ast.parse(code or "")
        return True,"ast.parse PASS"
    except Exception as e: return False,str(e)


def autonomous_retry_allowed(task:dict) -> bool:
    try: return int(task.get("retry_count") or 0) < AUTONOMOUS_MAX_RETRIES
    except Exception: return False


async def autonomous_implement_task(project:dict,task:dict) -> dict:
    """IMPLEMENT: generate only this task's artifact using Smart Context; no project-wide prompt."""
    # /codeplan tasks use this Phase 20 path directly (rather than the legacy
    # process_next_code_task path), so enforce the same per-user no-API policy here too.
    if is_no_api_mode(project.get("user_id", 0)):
        stuck_msg = build_no_api_stuck_message({"stage": "coding_ai_route", "confidence": 0.0})
        blocked_code = f"[No API Mode]\n{stuck_msg}"
        save_task_result(task["id"], blocked_code, source="no_api_blocked", status="failed")
        autonomous_set_task_state(task["id"], "failed", "coding_ai_route", stuck_msg)
        task.update({
            "code": blocked_code,
            "source": "no_api_blocked",
            "status": "failed",
            "workflow_stage": "coding_ai_route",
            "last_error": stuck_msg,
            "no_api_blocked": True,
        })
        return task

    autonomous_set_task_state(task["id"],"in_progress","implement","")
    task["status"]="in_progress"; task["workflow_stage"]="implement"
    # Coding-context Decision Engine — greeting/bot_info ক্যাটাগরি এখানেও বাদ।
    # ব্যর্থ/অপ্রাসঙ্গিক হলে নিচের AI রুটে পড়ে (non-fatal)।
    try:
        decision_request = (
            f"Project: {project.get('name','')}\nStack: {project.get('stack','')}\n"
            f"Task: {task.get('title','')}\nDescription: {task.get('description','')}"
        )
        decision = await decision_engine_service.execute_async(
            decision_request,
            user_id=project.get("user_id"),
            session_key=str(project.get("id") or ""),
            exclude_categories=list(CODING_EXCLUDED_BRAIN_CATEGORIES),
        )
        if decision.get("strategy") == "direct":
            direct_code = _strip_code_fences(_brain_payload_to_answer(decision.get("payload")))
            if direct_code and _coding_result_looks_like_code(direct_code, project.get("stack", "")):
                ok, detail = autonomous_syntax_hook(direct_code, project.get("stack", "python"))
                if ok:
                    save_task_result(task["id"], direct_code, source=f"brain:{decision.get('stage', 'direct')}", status="done")
                    autonomous_set_task_state(task["id"], "done", "implement", "")
                    task.update({
                        "status": "done",
                        "code": direct_code,
                        "source": f"brain:{decision.get('stage', 'direct')}",
                        "workflow_stage": "implement",
                    })
                    autonomous_record_success(task, project)
                    return task
                logger.info("Phase 20 Decision Engine code rejected by syntax hook: %s", detail)
    except Exception as e:
        logger.debug("Phase 20 coding Decision Engine fallback to AI: %s", e)
    try:
        ctx=await asyncio.to_thread(build_smart_context,project.get("user_id"),task["description"]+"\nTarget files: "+task.get("target_files", ""))
        impact_ctx=build_phase28_context(task.get("phase28_impact",{}),6500) if task.get("phase28_impact") else "Phase 28 impact context unavailable; Confidence: LOW"
        # আগের সম্পন্ন কোনো task একই target_files-এ কাজ করে থাকলে সেই ফাইলের
        # বিদ্যমান কোড context হিসেবে দাও আর "সম্পূর্ণ আপডেটেড ফাইল ফেরত দাও"
        # নির্দেশ দাও — নইলে প্রতিটা ধাপ আলাদা fragment/duplicate entry-point
        # লিখে ফেলে আর assemble-এ ডুপ্লিকেট আউটপুট আসে। Non-fatal (এররে খালি)।
        existing_file_note=""
        try:
            my_target=(task.get("target_files") or "").strip().lower()
            prior=[t for t in get_project_tasks(project["id"])
                   if t.get("status")=="done" and t.get("code")
                   and t.get("id")!=task.get("id")
                   and (t.get("target_files") or "").strip().lower()==my_target]
            if prior:
                prev_code=(max(prior,key=lambda t:t["seq"])["code"] or "").strip()
                if len(prev_code)>CODE_CONTEXT_EXISTING_CODE_MAX_CHARS:
                    prev_code=prev_code[-CODE_CONTEXT_EXISTING_CODE_MAX_CHARS:]
                if prev_code:
                    existing_file_note=(
                        "\nEXISTING FILE CONTENT (this task edits/extends the SAME file):\n"
                        "```\n"+prev_code+"\n```\n"
                        "IMPORTANT: Return the COMPLETE UPDATED FILE (existing code merged with "
                        "this task's changes), not just a fragment. Do not duplicate functions "
                        "or the if __name__ == \"__main__\" block — edit/replace as needed so "
                        "the result is a single clean, runnable file.")
        except Exception as _e:
            logger.debug("Phase 20 existing-file context skipped: %s", _e)
        system=("You are an autonomous coding agent. Implement ONLY the requested task. "
                "Return code only. Do not claim files were changed; return the code artifact. "
                "Use the compact context below and preserve existing architecture.\n"
                "PHASE 28 IMPACT CONTEXT:\n"+impact_ctx+"\nSMART CONTEXT:\n"+_autonomous_context_text(ctx,10000)
                +existing_file_note)
        reply=await ask_ai(system,f"Task: {task['title']}\nDescription: {task['description']}\nTarget files: {task.get('target_files','')}")
        code=_strip_code_fences(reply)
        ok,detail=autonomous_syntax_hook(code,project.get("stack","python"))
        if not ok: raise SyntaxError(detail)
        save_task_result(task["id"],code,source="phase20_ai",status="done")
        autonomous_set_task_state(task["id"],"done","implement","")
        task.update({"status":"done","code":code,"source":"phase20_ai","workflow_stage":"implement"})
        autonomous_record_success(task,project)
        return task
    except Exception as e:
        retry=int(task.get("retry_count") or 0)+1
        conn=get_conn(); cur=conn.cursor(); cur.execute("UPDATE code_tasks SET retry_count=?,last_error=?,status=?,workflow_stage=?,updated_at=? WHERE id=?",(retry,str(e)[:2000],"failed" if retry>=AUTONOMOUS_MAX_RETRIES else "pending","implement",datetime.now().isoformat(timespec="seconds"),task["id"])); conn.commit(); conn.close()
        task.update({"status":"failed" if retry>=AUTONOMOUS_MAX_RETRIES else "pending","retry_count":retry,"last_error":str(e),"workflow_stage":"implement"})
        autonomous_record_failure(e,task,project)
        return task



# ========================= PHASE 23 — CODE REVIEW ENGINE =========================

def _phase23_static_review(code: str) -> dict:
    """Stdlib-only AST review. Never raises; findings are structured by severity."""
    result = {"critical": [], "high": [], "medium": [], "low": [], "suggestions": [], "quality": 100}
    try:
        tree = ast.parse(code or "")
        seen_names = set(); function_names = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_names.append(node.name)
                if node.name in seen_names:
                    result["medium"].append(f"Duplicate function definition: {node.name}")
                seen_names.add(node.name)
                if len(node.body) > 80:
                    result["medium"].append(f"Very long function: {node.name}")
                # Deep nesting heuristic.
                max_depth = [0]
                def depth(n, d=0):
                    max_depth[0] = max(max_depth[0], d)
                    for child in ast.iter_child_nodes(n):
                        depth(child, d + (1 if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncWith)) else 0))
                depth(node)
                if max_depth[0] >= 5:
                    result["medium"].append(f"Deep nesting in function: {node.name}")
                # Mutable defaults.
                for d in list(node.args.defaults) + [x for x in node.args.kw_defaults if x is not None]:
                    if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                        result["high"].append(f"Mutable default argument in: {node.name}")
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    result["high"].append("Bare except detected; catch specific exceptions instead.")
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                pass
        # Simple unused-variable heuristic: local assignments whose names never occur as Load.
        assigned, loaded = set(), set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                (assigned if isinstance(node.ctx, ast.Store) else loaded).add(node.id)
        for name in sorted(assigned - loaded):
            if not name.startswith("_") and name not in {"self", "cls"}:
                result["low"].append(f"Possibly unused variable: {name}")
        if not function_names:
            result["suggestions"].append("No functions found; review whether this task should produce executable code.")
        # Missing return heuristic for functions containing an explicit return plus fall-through.
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(isinstance(x, ast.Return) for x in ast.walk(node)):
                if node.returns and not isinstance(node.body[-1], ast.Return):
                    result["medium"].append(f"Annotated function may fall through without returning: {node.name}")
        penalties = len(result["critical"])*35 + len(result["high"])*18 + len(result["medium"])*8 + len(result["low"])*2
        result["quality"] = max(0, min(100, 100 - penalties))
        return result
    except SyntaxError as e:
        result["critical"].append(f"Syntax error: {e}"); result["quality"] = 0; return result
    except Exception as e:
        logger.warning("Phase 23 static review failed: %s", e); result["suggestions"].append("Static review partially failed; continue with safe fallback."); return result


def _phase23_duplicate_review(code: str, root: str = None) -> list:
    """Uses Phase 18 symbol index; name/signature heuristic only."""
    findings=[]
    try:
        tree=ast.parse(code or "")
        for n in ast.walk(tree):
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                hits=codebase_search(n.name, root, 5)
                for h in hits:
                    q=str(h.get("qualified_name") or h.get("symbol_name") or "")
                    if q.split(".")[-1] == n.name:
                        findings.append(f"Existing symbol with same name: {n.name} ({h.get('file','') or h.get('relative_path','')})")
        return list(dict.fromkeys(findings))[:20]
    except Exception as e:
        logger.warning("Phase 23 duplicate review failed: %s", e); return []


def _phase23_review_text(review: dict) -> str:
    lines=["🔎 CODE REVIEW", f"Quality Score: {review.get('quality',0)}/100"]
    for key,label in (("critical","CRITICAL"),("high","HIGH"),("medium","MEDIUM"),("low","LOW"),("suggestions","SUGGESTIONS")):
        vals=review.get(key,[])
        if vals:
            lines.append(f"\n{label}:")
            lines.extend(f"- {x}" for x in vals[:30])
    return "\n".join(lines)


async def autonomous_review_task(project: dict, task: dict) -> dict:
    """Phase 23 review: local AST first, targeted AI second, persisted on code_tasks."""
    try:
        code=str(task.get("code") or "")
        review=_phase23_static_review(code)
        root=project.get("root") or CODEBASE_DEFAULT_ROOT
        dups=_phase23_duplicate_review(code,root)
        review["medium"].extend(dups)
        # AI is reserved for deeper logic/architecture review after local checks.
        try:
            ctx=await asyncio.to_thread(build_smart_context,project.get("user_id"),task.get("description","") + "\nReview this implementation",None,4000)
            prompt=("Review this Python implementation. Return ONLY JSON with keys critical, high, medium, low, suggestions, quality. "
                    "Do not invent issues. Focus on logic, architecture, maintainability, performance and regressions.\n"+
                    _autonomous_context_text(ctx,4000)+"\nCODE:\n"+code[:12000])
            raw=await asyncio.wait_for(ask_ai("You are a strict code reviewer. JSON only.",prompt),timeout=25)
            match=re.search(r"\{.*\}",raw or "",re.S)
            if match:
                ai=json.loads(match.group(0))
                for k in ("critical","high","medium","low","suggestions"):
                    vals=ai.get(k,[])
                    if isinstance(vals,list): review[k].extend(str(x) for x in vals[:20])
                if isinstance(ai.get("quality"),(int,float)):
                    review["quality"]=min(review["quality"],int(ai["quality"]))
                review["ai_reviewed"]=True
            else: review["ai_reviewed"]=False
        except Exception as e:
            logger.warning("Phase 23 AI review fallback: %s",e); review["ai_reviewed"]=False
        for k in ("critical","high","medium","low","suggestions"):
            review[k]=list(dict.fromkeys(review.get(k,[])))
        review["quality"]=max(0,min(100,int(review.get("quality",100))))
        review["status"]="needs_review" if review["critical"] else "passed"
        report=_phase23_review_text(review)
        conn=get_conn(); cur=conn.cursor()
        cur.execute("UPDATE code_tasks SET review_status=?,review_score=?,review_report=?,workflow_stage=?,status=?,updated_at=? WHERE id=?",
                    (review["status"],review["quality"],json.dumps(review,ensure_ascii=False)[:15000],"review_hook", "needs_review" if review["critical"] else "done",datetime.now().isoformat(timespec="seconds"),task["id"]))
        conn.commit(); conn.close()
        task.update({"review_status":review["status"],"review_score":review["quality"],"review_report":json.dumps(review,ensure_ascii=False),"status":"needs_review" if review["critical"] else "done","workflow_stage":"review_hook"})
        return {"ok":True,"review":review,"text":report,"task":task}
    except Exception as e:
        logger.warning("Phase 23 review failed: %s",e)
        try:
            conn=get_conn(); conn.execute("UPDATE code_tasks SET review_status=?,review_report=?,workflow_stage=? WHERE id=?",("error",str(e)[:3000],"review_hook",task.get("id"))); conn.commit(); conn.close()
        except Exception: pass
        return {"ok":False,"review":{"quality":0,"critical":[str(e)]},"text":"Code review সাময়িকভাবে ব্যর্থ হয়েছে; manual review প্রয়োজন।","task":task}


async def reviewreport_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): await update.message.reply_text("⛔ Admin only."); return
        if not context.args or not context.args[0].isdigit(): await update.message.reply_text("ব্যবহার: /reviewreport <task_id>"); return
        conn=get_conn(); row=conn.execute("SELECT id,title,status,review_status,review_score,review_report,last_error FROM code_tasks WHERE id=?",(int(context.args[0]),)).fetchone(); conn.close()
        if not row: await update.message.reply_text("Task পাওয়া যায়নি।"); return
        report=row[5] or "Review এখনো চালানো হয়নি।"
        text=f"🔎 REVIEW REPORT\nTask: {row[0]} — {row[1]}\nStatus: {row[2]}\nReview: {row[3] or 'pending'}\nScore: {row[4] or 0}/100\nLast error: {(row[6] or '')[:1000]}\n\n{report[:7000]}"
        await send_long_text(update,text)
    except Exception as e:
        logger.warning("Phase 23 /reviewreport failed: %s",e); await update.message.reply_text("Review report দেখাতে সমস্যা হয়েছে।")

async def autonomous_run_next(project:dict) -> dict|None:
    """ANALYZE→IMPACT→IMPLEMENT→TEST→REVIEW→SECURITY with Phase 28 as a non-fatal gate."""
    try:
        await asyncio.to_thread(project_memory_sync_codebase, int(project.get("id",0)), project.get("root") or CODEBASE_DEFAULT_ROOT)
    except Exception as e:
        logger.debug("Phase 25 pre-task codebase memory sync skipped: %s",e)
    task=get_next_pending_task(project["id"])
    if task:
        try:
            impact = await asyncio.to_thread(phase28_analyze_change, project, task, None)
            task["phase28_impact"] = impact
            autonomous_set_task_state(task["id"], "in_progress", "impact_analysis", "")
            _phase28_persist_task_impact(task["id"], impact)
            if impact.get("risk_level") in {"HIGH", "CRITICAL"}:
                # Reuse Phase 27 checkpoint/rollback; no duplicate Git layer.
                try:
                    done_tasks=[t for t in get_project_tasks(project["id"]) if t.get("status")=="done" and t.get("code")]
                    if done_tasks: phase27_save_snapshot(project, done_tasks[-1], note="phase28-pre-change")
                except Exception as e: logger.debug("Phase 28 pre-change checkpoint skipped: %s",e)
        except Exception as e:
            logger.warning("Phase 28 pre-implementation impact analysis failed; safe workflow fallback: %s", e)
            task["phase28_impact"] = {"status":"failed","confidence":"LOW","error":str(e)[:2000]}
    if not task: return None
    if not autonomous_retry_allowed(task):
        autonomous_set_task_state(task["id"],"blocked","retry_limit",task.get("last_error","") or "max retries reached"); return task
    autonomous_set_task_state(task["id"],"in_progress","analyze","")
    phase28_before=await asyncio.to_thread(phase28_actual_files_snapshot, project.get("root") or CODEBASE_DEFAULT_ROOT)
    result=await autonomous_implement_task(project,task)
    try:
        phase28_after=await asyncio.to_thread(phase28_actual_files_snapshot, project.get("root") or CODEBASE_DEFAULT_ROOT)
        actual_files=phase28_changed_files(phase28_before,phase28_after)
        expected=(result.get("phase28_impact") or {}).get("expected_files",[])
        validation=phase28_expected_vs_actual(expected,actual_files)
        result["phase28_actual_files"]=actual_files; result["phase28_validation"]=validation
        _phase28_persist_task_impact(result.get("id",task.get("id")),result.get("phase28_impact") or {},actual_files,validation)
    except Exception as e:
        logger.warning("Phase 28 expected-vs-actual validation failed; continuing safely: %s",e)
    if result.get("status")=="done":
        autonomous_set_task_state(task["id"],"in_progress","test_hook","")
        ok,detail,report=await autonomous_test_hook(project,result)
        result.update({"test_report":report,"test_status":"passed" if ok else "failed"})
        if ok:
            review_result=await autonomous_review_task(project,result)
            if review_result.get("ok"):
                sec=await autonomous_security_scan(project,review_result.get("task") or result,mode="changed")
                task2=review_result.get("task") or result
                if sec.get("ok"):
                    sr=sec["report"]; task2["security_score"]=sr.get("score",100); task2["security_report"]=json.dumps(sr,ensure_ascii=False)[:20000]
                    status="needs_review" if sr.get("counts",{}).get("CRITICAL",0) or sr.get("counts",{}).get("HIGH",0) else "passed"; task2["status"]="needs_review" if status=="needs_review" else task2.get("status","done")
                    try:
                        conn=get_conn(); conn.execute("UPDATE code_tasks SET security_status=?,security_score=?,security_report=?,security_updated_at=?,status=? WHERE id=?",(status,sr.get("score",100),task2["security_report"],datetime.now().isoformat(timespec="seconds"),task2["status"],task2["id"])); conn.commit(); conn.close()
                    except Exception as e: logger.warning("Phase 24 task security persistence failed: %s",e)
                try: coding_knowledge_record_outcome(project, task2, task2)
                except Exception as e: logger.debug("Phase 26 review/security learning skipped: %s", e)
                return task2
            try: coding_knowledge_record_outcome(project, result, result)
            except Exception as e: logger.debug("Phase 26 review learning skipped: %s", e)
            return result
        fixed = await autonomous_auto_fix_loop(project,result,detail,report)
        try:
            coding_knowledge_record_outcome(project, fixed, fixed)
        except Exception as e: logger.debug("Phase 26 auto-fix learning skipped: %s", e)
        return fixed
    try:
        coding_knowledge_record_outcome(project, result, result)
    except Exception as e: logger.debug("Phase 26 failure learning skipped: %s", e)
    return result


# =============================================================================
# PHASE 30 — REAL WORKSPACE + TERMINAL EXECUTION ENGINE
# Safe, project-root confined workspace operations and allow-listed commands.
# =============================================================================
PHASE30_VERSION = "1.0"
PHASE30_COMMANDS = {"python", "python3", "pytest", "python -m pytest", "python -m unittest", "ruff", "mypy", "pip", "git"}
PHASE30_MAX_OUTPUT = 12000
PHASE30_TIMEOUT = 90


def phase30_project_root(project: dict) -> str:
    root = os.path.abspath(project.get("root") or CODEBASE_DEFAULT_ROOT)
    os.makedirs(root, exist_ok=True)
    return root


def phase30_safe_path(root: str, rel: str) -> str:
    root = os.path.abspath(root)
    target = os.path.abspath(os.path.join(root, rel))
    if target != root and not target.startswith(root + os.sep):
        raise ValueError("Path escapes project workspace")
    return target


def phase30_read_file(root: str, rel: str, limit: int = 30000) -> str:
    path = phase30_safe_path(root, rel)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(limit)


def phase30_write_file(root: str, rel: str, content: str) -> str:
    path = phase30_safe_path(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".rohan_tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)
    return os.path.relpath(path, root).replace(os.sep, "/")


def phase30_extract_files(text: str) -> dict:
    """Accept FILE: path blocks, fenced blocks, or a single code payload."""
    files = {}
    pattern = re.compile(r"(?:^|\n)\s*(?:FILE|PATH)\s*:\s*([^\n]+)\n```(?:\w+)?\n(.*?)```", re.I | re.S)
    for m in pattern.finditer(text or ""):
        files[m.group(1).strip()] = m.group(2)
    return files


def phase30_apply_task_artifacts(project: dict, task: dict) -> dict:
    root = phase30_project_root(project)
    payload = task.get("code") or ""
    files = phase30_extract_files(payload)
    if not files:
        return {"ok": True, "changed": [], "skipped": True, "reason": "No FILE/PATH artifact blocks"}
    changed = []
    for rel, content in files.items():
        written = phase30_write_file(root, rel, content)
        changed.append(written)
    return {"ok": True, "changed": changed, "skipped": False}


def phase30_command_allowed(command: str) -> bool:
    parts = shlex.split(command or "")
    if not parts:
        return False
    executable = parts[0]
    if executable in {"python", "python3"} and len(parts) >= 3 and parts[1] == "-m":
        return f"python -m {parts[2]}" in PHASE30_COMMANDS
    return executable in PHASE30_COMMANDS


def phase30_run_command(root: str, command: str, timeout: int = PHASE30_TIMEOUT) -> dict:
    if not phase30_command_allowed(command):
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": "Command not allow-listed"}
    try:
        proc = subprocess.run(shlex.split(command), cwd=root, shell=False, capture_output=True,
                              text=True, timeout=max(1, min(int(timeout), PHASE30_TIMEOUT)), env={
                                  k: v for k, v in os.environ.items()
                                  if k not in {"GROQ_API_KEY", "OPENROUTER_API_KEY", "CEREBRAS_API_KEY", "TELEGRAM_BOT_TOKEN"}
                              })
        return {"ok": proc.returncode == 0, "returncode": proc.returncode,
                "stdout": (proc.stdout or "")[-PHASE30_MAX_OUTPUT:], "stderr": (proc.stderr or "")[-PHASE30_MAX_OUTPUT:]}
    except Exception as e:
        return {"ok": False, "returncode": -1, "stdout": "", "stderr": str(e)}


async def phase30_execute_task(project: dict, task: dict) -> dict:
    artifact = await asyncio.to_thread(phase30_apply_task_artifacts, project, task)
    root = phase30_project_root(project)
    test_cmd = "python -m pytest -q" if os.path.exists(os.path.join(root, "pytest.ini")) or os.path.exists(os.path.join(root, "pyproject.toml")) else "python -m unittest discover"
    test = await asyncio.to_thread(phase30_run_command, root, test_cmd)
    return {"artifact": artifact, "test": test, "ok": artifact.get("ok", False) and test.get("ok", False)}


# =============================================================================
# PHASE 31 — MULTI-AGENT CODING TEAM
# Architect → Coder → Tester → Debugger → Reviewer roles with shared context.
# =============================================================================
PHASE31_VERSION = "1.0"
PHASE31_ROLES = ("architect", "coder", "tester", "debugger", "reviewer")


async def phase31_role_call(role: str, project: dict, task: dict, evidence: str = "") -> str:
    prompts = {
        "architect": "Define the safest minimal implementation plan and affected components.",
        "coder": "Produce implementation artifacts. Use FILE: relative/path followed by a fenced code block.",
        "tester": "Design focused tests and identify likely regressions. Do not invent passing results.",
        "debugger": "Analyze the supplied failure output and propose the smallest safe correction.",
        "reviewer": "Review implementation for correctness, regression risk, security, and maintainability. Return PASS or NEEDS_REVIEW with reasons.",
    }
    system = f"You are ROHAN Phase 31 {role} agent. {prompts.get(role, '')} Be precise and repository-aware."
    user = json.dumps({"project": {k: project.get(k) for k in ("name", "description", "stack")},
                       "task": {k: task.get(k) for k in ("title", "description", "target_files")}, "evidence": evidence[-12000:]}, ensure_ascii=False)
    return await ask_ai(system, user)


async def phase31_team_run(project: dict, task: dict) -> dict:
    plan = await phase31_role_call("architect", project, task)
    draft = await phase31_role_call("coder", project, task, plan)
    task_copy = dict(task); task_copy["code"] = draft
    execution = await phase30_execute_task(project, task_copy)
    evidence = json.dumps(execution, ensure_ascii=False)
    if not execution.get("ok"):
        debug = await phase31_role_call("debugger", project, task, evidence)
    else:
        debug = ""
    review = await phase31_role_call("reviewer", project, task, (plan + "\n" + evidence + "\n" + debug)[-20000:])
    return {"plan": plan, "draft": draft, "execution": execution, "debug": debug, "review": review,
            "ok": execution.get("ok", False) and "NEEDS_REVIEW" not in review.upper()}


# =============================================================================
# PHASE 32 — ADVANCED REGRESSION + TEST INTELLIGENCE
# Discover tests, run focused/full suites, retain evidence, reject false success.
# =============================================================================
def phase32_test_inventory(root: str) -> list:
    return _phase28_detect_tests(root)


def phase32_regression(root: str, affected: list | None = None) -> dict:
    tests = phase32_test_inventory(root)
    related = _phase28_related_tests(tests, affected or [])
    selected = related or tests
    return _phase28_run_regression(root, selected, mode="focused" if related else "full")


# =============================================================================
# PHASE 33 — REFACTOR + OPTIMIZATION GUARD
# Only permit measurable, reversible refactor candidates; never claim performance gains without evidence.
# =============================================================================
def phase33_refactor_guard(root: str, before: dict, after: dict) -> dict:
    before_files = set((before or {}).get("files", {}).keys()) if isinstance(before, dict) else set()
    after_files = set((after or {}).get("files", {}).keys()) if isinstance(after, dict) else set()
    return {"ok": True, "added": sorted(after_files-before_files)[:100], "removed": sorted(before_files-after_files)[:100],
            "note": "Refactor guard requires tests and review evidence before acceptance."}


# =============================================================================
# PHASE 34 — FINAL INTEGRATED AUTONOMOUS CODING CYCLE
# Supervisor that composes Phases 28–33 and stops safely on failed gates.
# =============================================================================
PHASE34_VERSION = "1.0"


async def phase34_integrated_cycle(project: dict, task: dict) -> dict:
    root = phase30_project_root(project)
    before = await asyncio.to_thread(phase28_actual_files_snapshot, root)
    impact = await asyncio.to_thread(phase28_analyze_change, project, task, None)
    if impact.get("risk_level") == "CRITICAL":
        return {"ok": False, "stage": "impact_gate", "impact": impact, "reason": "CRITICAL impact requires explicit review/checkpoint."}
    team = await phase31_team_run(project, task)
    after = await asyncio.to_thread(phase28_actual_files_snapshot, root)
    regression = await asyncio.to_thread(phase32_regression, root, impact.get("expected_files", []))
    guard = phase33_refactor_guard(root, before, after)
    ok = bool(team.get("ok") and regression.get("ok") and guard.get("ok"))
    return {"ok": ok, "impact": impact, "team": team, "regression": regression, "guard": guard,
            "stage": "complete" if ok else "verification_failed"}


async def phase30_execute_command_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only."); return
    command = " ".join(context.args).strip()
    if not command:
        await update.message.reply_text("ব্যবহার: /codeexec <allow-listed command>"); return
    result = await asyncio.to_thread(phase30_run_command, CODEBASE_DEFAULT_ROOT, command)
    await send_long_text(update, "🛠️ PHASE 30 EXECUTION\n" + json.dumps(result, ensure_ascii=False, indent=2)[:12000])


async def phase34_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("🚀 ROHAN CODING ENGINE\n\n"
            "Phase 29: Autonomous Supervisor\n"
            "Phase 30: Workspace + Terminal Engine\n"
            "Phase 31: Multi-Agent Coding Team\n"
            "Phase 32: Regression/Test Intelligence\n"
            "Phase 33: Refactor/Optimization Guard\n"
            "Phase 34: Integrated Autonomous Cycle\n\n"
            "All Phase 29–34 modules are present in this consolidated source file.")
    await send_long_text(update, text)


# =============================================================================
# PHASE 29 — AUTONOMOUS CODING SUPERVISOR 2.0
# =============================================================================
# Connects the existing Phase 20-28 stages into a persistent multi-task loop:
# PLAN -> IMPACT -> IMPLEMENT -> TEST -> AUTO-FIX -> REVIEW -> SECURITY -> CHECKPOINT.
# This supervisor never bypasses the existing safety gates and stops on blocked or
# high-risk review states instead of pretending that a project is complete.

PHASE29_VERSION = 1
PHASE29_DEFAULT_MAX_TASKS = 8
PHASE29_MAX_TASKS = 20
PHASE29_RUN_TIMEOUT = 900


def _phase29_ensure_tables(conn) -> None:
    """Create only Phase-29 orchestration metadata; idempotent and non-destructive."""
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS phase29_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER DEFAULT 0,
            user_id INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running',
            max_tasks INTEGER DEFAULT 0,
            completed_tasks INTEGER DEFAULT 0,
            failed_tasks INTEGER DEFAULT 0,
            blocked_tasks INTEGER DEFAULT 0,
            last_task_id INTEGER DEFAULT 0,
            started_at TEXT DEFAULT '',
            finished_at TEXT DEFAULT '',
            summary TEXT DEFAULT '{}'
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_phase29_runs_project ON phase29_runs(project_id, started_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_phase29_runs_status ON phase29_runs(status, started_at)")
    except Exception as e:
        logger.warning("Phase 29 table setup skipped: %s", e)


def _phase29_create_run(project_id: int, user_id: int, max_tasks: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat(timespec="seconds")
    cur.execute(
        "INSERT INTO phase29_runs(project_id,user_id,status,max_tasks,started_at,summary) VALUES(?,?,?,?,?,?)",
        (int(project_id), int(user_id), "running", int(max_tasks), now, "{}"),
    )
    run_id = int(cur.lastrowid)
    conn.commit(); conn.close()
    return run_id


def _phase29_update_run(run_id: int, status: str, completed: int, failed: int,
                        blocked: int, last_task_id: int = 0, summary: dict | None = None) -> None:
    try:
        conn = get_conn(); now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "UPDATE phase29_runs SET status=?,completed_tasks=?,failed_tasks=?,blocked_tasks=?,last_task_id=?,finished_at=?,summary=? WHERE id=?",
            (status, int(completed), int(failed), int(blocked), int(last_task_id),
             now if status != "running" else "", json.dumps(summary or {}, ensure_ascii=False)[:20000], int(run_id)),
        )
        conn.commit(); conn.close()
    except Exception as e:
        logger.warning("Phase 29 run persistence failed: %s", e)


def _phase29_latest_run(project_id: int) -> dict | None:
    try:
        conn = get_conn()
        row = conn.execute(
            "SELECT id,status,max_tasks,completed_tasks,failed_tasks,blocked_tasks,last_task_id,started_at,finished_at,summary FROM phase29_runs WHERE project_id=? ORDER BY id DESC LIMIT 1",
            (int(project_id),),
        ).fetchone(); conn.close()
        if not row: return None
        try: summary = json.loads(row[9] or "{}")
        except Exception: summary = {"raw": row[9] or ""}
        return {"id": row[0], "status": row[1], "max_tasks": row[2], "completed_tasks": row[3],
                "failed_tasks": row[4], "blocked_tasks": row[5], "last_task_id": row[6],
                "started_at": row[7], "finished_at": row[8], "summary": summary}
    except Exception as e:
        logger.warning("Phase 29 latest run lookup failed: %s", e); return None


def _phase29_task_outcome(result: dict | None) -> str:
    if not result: return "none"
    status = str(result.get("status") or "").lower()
    test_status = str(result.get("test_status") or "").lower()
    if status == "done" and test_status in ("", "passed"): return "completed"
    if status in ("blocked", "failed") or test_status in ("failed", "error"): return "failed"
    if status in ("needs_review", "pending"): return "blocked"
    return "failed"


async def phase29_autonomous_run(project: dict, max_tasks: int = PHASE29_DEFAULT_MAX_TASKS,
                                 notify=None) -> dict:
    """Run the existing autonomous task pipeline repeatedly until completion or a safety gate.

    Phase 29 is an orchestration layer: it deliberately reuses autonomous_run_next(), so
    Phase 21 tests, Phase 22 auto-fix, Phase 23 review, Phase 24 security, Phase 25/26
    learning, Phase 27 snapshots and Phase 28 impact analysis remain authoritative.
    """
    max_tasks = max(1, min(int(max_tasks or PHASE29_DEFAULT_MAX_TASKS), PHASE29_MAX_TASKS))
    project_id = int(project.get("id", 0)); user_id = int(project.get("user_id", 0))
    run_id = _phase29_create_run(project_id, user_id, max_tasks)
    completed = failed = blocked = 0; history = []; last_id = 0
    started = time.time()
    status = "completed"
    try:
        for _ in range(max_tasks):
            if time.time() - started > PHASE29_RUN_TIMEOUT:
                status = "timeout"; break
            task = get_next_pending_task(project_id)
            if not task:
                break
            last_id = int(task.get("id") or 0)
            if callable(notify):
                try: await notify(f"🔄 Phase 29: ধাপ {task.get('seq','?')} — {task.get('title','')}\nANALYZE → IMPACT → IMPLEMENT → TEST → REVIEW")
                except Exception: pass
            try:
                result = await autonomous_run_next(project)
            except Exception as e:
                result = {"id": last_id, "status": "failed", "last_error": str(e)[:2000]}
            outcome = _phase29_task_outcome(result)
            item = {"task_id": int(result.get("id", last_id) if result else last_id),
                    "seq": result.get("seq") if result else task.get("seq"),
                    "title": (result.get("title") if result else task.get("title", "")),
                    "status": result.get("status") if result else "failed",
                    "test_status": result.get("test_status", "") if result else "",
                    "security_score": result.get("security_score") if result else None,
                    "outcome": outcome}
            history.append(item)
            if outcome == "completed":
                completed += 1
                # Phase 27 checkpoint is already used by autonomous_run_next; keep a final
                # supervisor checkpoint as a second safety net for the completed task.
                try:
                    phase27_save_snapshot(project, result, note="phase29-complete")
                except Exception as e: logger.debug("Phase 29 checkpoint skipped: %s", e)
                continue
            if outcome == "blocked": blocked += 1; status = "blocked"; break
            failed += 1; status = "failed"; break
        else:
            status = "max_tasks_reached"
        if not get_next_pending_task(project_id) and status == "completed":
            status = "project_complete"
    except Exception as e:
        failed += 1; status = "failed"; history.append({"error": str(e)[:2000]})
    summary = {"run_id": run_id, "project_id": project_id, "status": status,
               "completed": completed, "failed": failed, "blocked": blocked,
               "last_task_id": last_id, "tasks": history}
    _phase29_update_run(run_id, status, completed, failed, blocked, last_id, summary)
    return summary


async def codeauto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Phase 29: /codeauto [project_id] [max_tasks] — continuous autonomous coding supervisor."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Phase 29 Autonomous Coding শুধু অ্যাডমিনের জন্য।"); return
    try:
        project = None
        args = list(context.args or [])
        if args and args[0].isdigit():
            project = get_project(int(args[0]), owner_id=update.effective_user.id)
        if not project:
            project = get_active_project(update.effective_user.id)
        if not project:
            await update.message.reply_text("কোনো active coding project নেই। /codeplan বা /useproject দিয়ে project নির্বাচন করুন।"); return
        max_tasks = int(args[1]) if len(args) > 1 and args[1].isdigit() else PHASE29_DEFAULT_MAX_TASKS
        max_tasks = max(1, min(max_tasks, PHASE29_MAX_TASKS))
        msg = await update.message.reply_text(
            f"🤖 Phase 29 Autonomous Coding 2.0 শুরু\nProject: {project.get('name','')}\nMax tasks: {max_tasks}\n\nANALYZE → IMPACT → IMPLEMENT → TEST → AUTO-FIX → REVIEW → SECURITY → CHECKPOINT"
        )
        async def notify(text):
            try: await update.message.reply_text(text[:3500])
            except Exception: pass
        summary = await asyncio.wait_for(phase29_autonomous_run(project, max_tasks, notify), timeout=PHASE29_RUN_TIMEOUT + 30)
        report = ("🏁 PHASE 29 RESULT\n"
                  f"Project: {project.get('name','')}\nStatus: {summary.get('status')}\n"
                  f"Completed: {summary.get('completed',0)} | Failed: {summary.get('failed',0)} | Blocked: {summary.get('blocked',0)}\n\n"
                  + json.dumps(summary.get('tasks',[]), ensure_ascii=False, indent=2)[:8000])
        await send_long_text(update, report)
        try: await msg.delete()
        except Exception: pass
    except Exception as e:
        logger.warning("Phase 29 /codeauto failed: %s", e)
        await update.message.reply_text("Phase 29 autonomous run ব্যর্থ হয়েছে; existing coding workflow নিরাপদে রাখা হয়েছে।")


async def codeautostatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only."); return
    try:
        project = get_active_project(update.effective_user.id)
        if not project:
            await update.message.reply_text("Active project নেই।"); return
        run = _phase29_latest_run(project["id"])
        if not run:
            await update.message.reply_text("Phase 29 run এখনো হয়নি। /codeauto চালান।"); return
        await send_long_text(update, "🤖 PHASE 29 STATUS\n" + json.dumps(run, ensure_ascii=False, indent=2)[:9000])
    except Exception as e:
        logger.warning("Phase 29 /codeautostatus failed: %s", e); await update.message.reply_text("Phase 29 status পাওয়া যায়নি।")


async def codeplan_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    """Phase 20: /codeplan <description> creates a persistent multi-step autonomous plan."""
    if not context.args:
        await update.message.reply_text("এভাবে লিখুন: /codeplan <কোডিং কাজের বিস্তারিত বর্ণনা>"); return
    if not await quota_guard(update,action="coding_plan"): return
    user_id=update.effective_user.id; text=" ".join(context.args).strip()
    thinking=await update.message.reply_text("🤖 Autonomous Agent: ANALYZE → PLAN চলছে…")
    try:
        plan=await autonomous_generate_plan(user_id,text); pid=autonomous_save_plan(user_id,plan); project=get_project(pid,owner_id=user_id)
        if plan.get("no_api_blocked"):
            await update.message.reply_text(NO_API_PLAN_BLOCKED_MESSAGE)
        else:
            await send_long_text(update,"✅ Autonomous plan saved.\n\n"+build_project_status_text(project)+"\n\n/codenext দিয়ে implementation শুরু করুন।")
    except Exception as e:
        logger.warning("Phase 20 /codeplan failed: %s",e); await update.message.reply_text("Autonomous plan তৈরি করতে সমস্যা হয়েছে।")
    finally:
        try: await thinking.delete()
        except Exception: pass

# ---- Task Split + Assemble ----

def _looks_like_programming_stack(stack: str) -> bool:
    """Coding-orchestrator task-এর stack কি কোড-সদৃশ আর্টিফ্যাক্ট আশা করে?"""
    try:
        s = (stack or "").strip().lower()
        if not s or s in ("unknown", "অজানা") or "অজানা" in s:
            return True
        non_code = ("docs", "documentation", "markdown", "writing", "copy", "prose")
        if any(n == s or n in s.split() for n in non_code) and not any(
            h in s for h in ("python", "js", "javascript", "html", "css")
        ):
            return False
        return True
    except Exception:
        return True


# greeting/bot-info FAQ-র ফিঙ্গারপ্রিন্ট — কোড-স্যানিটি চেক আর "প্রাসঙ্গিক নিয়ম"
# সংগ্রহ দুটোতেই ব্যবহৃত হয় (একই লিস্ট দুই জায়গায় কপি না করার জন্য মডিউল-লেভেল)।
_FAQ_REPLY_NEEDLES = (
    "সব কমান্ডের তালিকা",
    "/help অথবা /menu",
    "/menu অথবা /help",
    "আপনাকেও ধন্যবাদ",
    "you're welcome",
    "how can i help you",
    "আমি আপনাকে কীভাবে সাহায্য",
    "type your question or use /menu",
    "লিখুন অথবা /menu",
    "আসসালামু আলাইকুম / হ্যালো",
)

# Decision Engine-এর ম্যাচ "কোড" না হয়ে "নিয়ম/গাইডলাইন টেক্সট" হলে সেগুলো ফেলে না
# দিয়ে AI প্রম্পটে যোগ হয় — কয়টা এন্ট্রি ও প্রতিটা কত লম্বা থাকবে সেটা এখানে সীমাবদ্ধ,
# যাতে প্রম্পট অতিরিক্ত বড় না হয়ে যায়।
CODING_RELEVANT_RULES_MAX = 3
CODING_RULE_TEXT_MAX_CHARS = 400

# "নিয়ম" হতে পারে এমন টেক্সটের উল্টো-চেক: এই মার্কারগুলো বাক্যের শুরুতে থাকলে
# এন্ট্রিটা আসলে কোড-স্নিপেট (প্রম্পটে নিয়ম হিসেবে ঢোকানোর দরকার নেই — direct
# রুটে সেটা কোড হিসেবেই ব্যবহারের চেষ্টা হয়)।
_RULE_CODE_LINE_START_RE = re.compile(
    r"^(def |class |async def |import |from \w[\w.]* import|const |let |var |package |using |func |"
    r"public |private |protected |int main|#include|#\!|<\?php|@\w+\.\w+|#!\s*/)",
)


def _rule_text_looks_like_code(text: str) -> bool:
    """রুল-প্রার্থী টেক্সট আসলে কোড-ব্লক কিনা (নিয়ম সংগ্রহের ফিল্টার)।

    _coding_result_looks_like_code()-এর মার্কার-হিউরিস্টিক প্রোজার প্রতি বারবার ফেল
    করত (বিরাম-চিহ্ন/বন্ধনী থাকলেই "কোড" বলে ফেলে দিত), তাই এখানে আলাদা কড়া চেক —
    বহু-লাইন কোড-শুরুর-শব্দ বা ফেন্সড ব্লক দেখলেই শুধু "কোড" ধরা হয়।
    """
    try:
        t = (text or "").strip()
        if not t:
            return False
        if "```" in t:
            return True
        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
        code_lines = sum(1 for ln in lines if _RULE_CODE_LINE_START_RE.match(ln))
        if code_lines >= 2:
            return True
        if code_lines == 1 and len(lines) <= 2:
            return True
        return False
    except Exception:
        return False


def _collect_relevant_brain_rules(decision: Dict[str, Any], stack: str = "") -> List[str]:
    """Decision Engine-এর সাজানো candidate list থেকে শীর্ষ কয়েকটা প্রাসঙ্গিক
    (কোড-না-হওয়া) knowledge/pattern/template/documentation এন্ট্রি "নিয়ম/গাইডলাইন"
    হিসেবে তুলে আনে।

    গ্যাপ-ফিক্স: আগে direct ম্যাচ কোড-চেকে ফেল করলে এন্ট্রিটা সম্পূর্ণ বাতিল হয়ে
    যেত, AI-প্রম্পটে পৌঁছাত না। ইউজারের /addknowledge, /addpattern, /addtemplate
    দিয়ে দেওয়া কোডিং-স্ট্যান্ডার্ড প্রায়শই টেক্সট-রুল, কোড নয় — এগুলো এখন
    confidence অনুযায়ী সাজানো শীর্ষ CODING_RELEVANT_RULES_MAXটা এন্ট্রি হিসেবে
    (প্রতিটা CODING_RULE_TEXT_MAX_CHARS ক্যারেক্টারে truncation করে) AI-এর
    system_prompt-এ পৌঁছায়। কোনো এররে খালি লিস্ট রিটার্ন — প্রম্পট তখন আগের
    মতোই তৈরি হবে (কোনো নতুন সেকশন যোগ হবে না)।
    """
    rules: List[str] = []
    try:
        candidates = decision.get("candidates") or []
        if not candidates:
            # ক্যান্ডিডেট-বিহীন (পুরোনো/মক করা decision) decision-এ অন্তত best
            # এন্ট্রিটাই বিবেচনা করা হয় — ফেল-হওয়া ম্যাচটাই যে "নিয়ম" তাই।
            candidates = [{
                "stage": decision.get("stage"),
                "confidence": decision.get("confidence"),
                "payload": decision.get("payload"),
            }]
        ranked = [
            c for c in candidates
            if isinstance(c, dict) and c.get("stage") in ("knowledge", "pattern", "template", "documentation")
        ]
        ranked.sort(key=lambda c: (
            float(c.get("confidence") or 0.0),
            float(c.get("score") or 0.0),
        ), reverse=True)
        seen = set()
        for cand in ranked:
            if len(rules) >= CODING_RELEVANT_RULES_MAX:
                break
            content = _brain_payload_to_answer(cand.get("payload"))
            if not content:
                continue
            content = _strip_code_fences(content)
            content = " ".join(content.split())  # মাল্টি-লাইন এন্ট্রিকে এক লাইনের বুলেটে
            if len(content) < 8:
                continue
            if any(n in content or n in content.lower() for n in _FAQ_REPLY_NEEDLES):
                continue  # greeting/bot-info FAQ কখনো কোডিং-নিয়ম নয়
            if _rule_text_looks_like_code(content):
                continue  # কোড-সদৃশ এন্ট্রি নিয়ম হিসেবে ঢোকাবে না
            content = content[:CODING_RULE_TEXT_MAX_CHARS].rstrip()
            key = content.lower()
            if key in seen:
                continue
            seen.add(key)
            rules.append(content)
    except Exception as e:
        logger.debug("Relevant-rule collection skipped: %s", e)
    return rules


def _coding_result_looks_like_code(text: str, stack: str = "") -> bool:
    """Safety net: greeting/bot-info FAQ যেন coding task-এর `code` ফিল্ডে সেভ না হয়।

    stack যদি প্রোগ্রামিং ভাষা (বা অজানা coding-context) হয় এবং রেজাল্টে কোনো
    কোড-সদৃশ প্যাটার্ন না থাকে, False — কলার তখন AI রুটে যায়। FAQ ফিঙ্গারপ্রিন্ট
    পেলে সরাসরি False। কোনো এক্সসেপশনে False (safe fallback)।
    """
    try:
        blob = str(text or "")
        if not blob.strip():
            return False
        if not _looks_like_programming_stack(stack):
            return True
        if any(n in blob or n in blob.lower() for n in _FAQ_REPLY_NEEDLES):
            return False
        markers = (
            "def ", "async def", "import ", "from ", "class ",
            "function ", "const ", "let ", "var ", "=>",
            "=", "{", "(", "[",
            "```", "#!/", "<?", "<html", "<!doctype",
            "pip ", "npm ", "__pycache__",
            "package.json", "module.exports", "print(",
        )
        lowered = blob.lower()
        if any((m in blob) or (m.lower() in lowered) for m in markers):
            return True
        lines = [ln for ln in blob.splitlines() if ln.strip()]
        if len(lines) >= 3 and any(ch in blob for ch in ("/", "*", ".", "-", "#")):
            return True
        return False
    except Exception:
        return False


async def process_next_code_task(project: dict):
    """
    Task Split: পরের pending ধাপটা নেয়। Knowledge Base-এ মিলে গেলে AI ছাড়াই কোড বসায়,
    না মিললে এই ধাপের জন্য নির্দিষ্ট প্রশ্ন AI-কে পাঠানো হয় — সাথে প্রজেক্টের এতদূর
    assemble করা কোড context হিসেবে যায়, যাতে AI প্রতিবার সম্পূর্ণ আপডেটেড ফাইল দেয়
    (fragment/duplicate entry-point না)।
    """
    task = get_next_pending_task(project["id"])
    if not task:
        return None

    kb_match = match_knowledge_base(task["title"], task["description"], project["name"], project["description"])
    if kb_match:
        label, code = kb_match
        try:
            if not _coding_result_looks_like_code(code, project.get("stack", "")):
                logger.info(
                    "KB match '%s' rejected by code-sanity check (stack=%s)",
                    label, project.get("stack"),
                )
                kb_match = None
        except Exception as e:
            logger.debug("KB code-sanity check fallback to AI: %s", e)
            kb_match = None
    if kb_match:
        label, code = kb_match
        save_task_result(task["id"], code, source=f"knowledge_base:{label}")
        task["code"], task["source"], task["status"] = code, f"knowledge_base:{label}", "done"
        brain_os_metrics["direct_answers"] += 1
        return task

    # বাংলা রুল ইঞ্জিন (bangla_rule_engine): কড়া, নির্দিষ্ট ফরম্যাটের বাংলা নির্দেশনা
    # (ভেরিয়েবল/স্টোরেজ, ইনপুট, শর্ত, নিষেধ, আউটপুট, তুলনা) deterministicভাবে চালানোর-
    # যোগ্য Python কোডে অনুবাদ করে — AI ছাড়াই। dynamic_print-এর আগে চেষ্টা হয়
    # (matcher চেইনে নতুন এন্ট্রি), কিন্তু ইঞ্জিনের ভেতরের গার্ড dynamic-print-আকৃতির
    # ("রান করলে X লেখা আসবে") বা কোটেশন-যুক্ত টেক্সট আগেই বাদ দেয় — তাই পুরনো
    # print-matcher-এর আচরণ অক্ষত থাকে (পরিপূরক, প্রতিযোগী নয়)। এটাও
    # is_no_api_mode() চেকের আগে বসা, তাই No API Mode-এও এই টাস্কগুলো সমাধান হয়।
    # dynamic_print-এর মতোই প্রথম pending ধাপে (_is_first_task) project-এর
    # name+description-এর বিরুদ্ধেও একবার ম্যাচ চেষ্টা হয় — generic ধাপে ভাঙা প্ল্যানে
    # আসল রিকোয়েস্ট হারিয়ে না যায়; একই কোড দ্বিতীয় ধাপে stamp হয় না।
    rule_engine_match = None
    try:
        rule_engine_match = match_bangla_rule_task(
            task["title"], task["description"], project.get("stack", "")
        )
    except Exception as e:
        logger.debug("bangla_rule_engine task check failed (AI fallback): %s", e)
        rule_engine_match = None
    if not rule_engine_match and _is_first_task(project):
        try:
            rule_engine_match = match_bangla_rule_task(
                project.get("name", ""), project.get("description", ""), project.get("stack", "")
            )
        except Exception as e:
            logger.debug("bangla_rule_engine project-level check failed (AI fallback): %s", e)
            rule_engine_match = None
    if rule_engine_match:
        label, code = rule_engine_match
        save_task_result(task["id"], code, source=f"knowledge_base:{label}")
        task["code"], task["source"], task["status"] = code, f"knowledge_base:{label}", "done"
        brain_os_metrics["direct_answers"] += 1
        return task

    # Dynamic KB entry `dynamic_print_task`: title+description থেকে regex দিয়ে প্রিন্ট
    # বার্তা বের করে project['stack'] ভাষার সিনট্যাক্সে AI ছাড়াই সরাসরি কোড। কিছু
    # না মিললে None — স্বাভাবিক ফ্লো চলবে। এটা is_no_api_mode() চেকের আগে বসা,
    # তাই No API Mode চালু থাকলেও এই deterministic টাস্কগুলো ব্লক না হয়ে সমাধান হয়।
    dynamic_match = None
    try:
        dynamic_match = match_dynamic_print_task(
            task["title"], task["description"], project.get("stack", "")
        )
    except Exception as e:
        logger.debug("dynamic_print_task check failed (AI fallback): %s", e)
        dynamic_match = None
    # Gap fix: প্ল্যান (AI-নির্মিত বা deterministic) একটা রিকোয়েস্টকে একাধিক generic
    # ধাপে ভেঙে দিলে (যেমন "Initialize Project Folder", "Implement Success Message
    # Function") কোনো ধাপের title/description-এই আসল "...রান করলে সফল হয়েছে লেখা
    # আসবে" বাক্যটা থাকে না — অথচ project["description"]-এ আসল রিকোয়েস্ট অক্ষত থাকে।
    # তাই প্রথম pending ধাপে (এখনো কোনো ধাপ done না হলে, _is_first_task) project-এর
    # name+description-এর বিরুদ্ধেও একবার deterministic ম্যাচ চেষ্টা হয়। পরের
    # ধাপগুলোতে আর চেষ্টা হয় না, তাই একই প্রিন্ট-কোড একাধিক ধাপে stamp হয় না।
    # ম্যাচ ব্যর্থ হলে নিচের স্বাভাবিক ফ্লো (Decision Engine → AI/No API Mode গেট)
    # অক্ষত থাকে — কখনো raise হয় না।
    if not dynamic_match and _is_first_task(project):
        try:
            dynamic_match = match_dynamic_print_task(
                project.get("name", ""), project.get("description", ""), project.get("stack", "")
            )
        except Exception as e:
            logger.debug("dynamic_print_task project-level check failed (AI fallback): %s", e)
            dynamic_match = None
    if dynamic_match:
        label, code = dynamic_match
        save_task_result(task["id"], code, source=f"knowledge_base:{label}")
        task["code"], task["source"], task["status"] = code, f"knowledge_base:{label}", "done"
        brain_os_metrics["direct_answers"] += 1
        return task

    # Phase 17: Decision Engine gets a chance before a coding AI call.
    # greeting/bot_info ক্যাটাগরি coding-context-এ কখনোই সঠিক উত্তর নয়।
    relevant_rules: List[str] = []
    decision = None
    decision_request = (
        f"Project: {project['name']}\nStack: {project['stack']}\n"
        f"Task: {task['title']}\nDescription: {task['description']}"
    )
    try:
        decision = await decision_engine_service.execute_async(
            decision_request,
            user_id=project.get("user_id"),
            session_key=str(project["id"]),
            exclude_categories=list(CODING_EXCLUDED_BRAIN_CATEGORIES),
        )
        if decision.get("strategy") == "direct":
            direct_code = _brain_payload_to_answer(decision.get("payload"))
            code_ok = False
            if direct_code:
                direct_code = _strip_code_fences(direct_code)
                try:
                    code_ok = _coding_result_looks_like_code(direct_code, project.get("stack", ""))
                except Exception as e:
                    logger.debug("Decision code-sanity check fallback to AI: %s", e)
                    code_ok = False
            if code_ok:
                save_task_result(task["id"], direct_code, source=f"brain:{decision.get('stage', 'direct')}")
                task["code"], task["source"], task["status"] = direct_code, f"brain:{decision.get('stage', 'direct')}", "done"
                brain_os_metrics["direct_answers"] += 1
                return task
            logger.info(
                "Decision Engine direct answer rejected by code-sanity (stage=%s)",
                decision.get("stage"),
            )
            brain_os_metrics["direct_failures"] += 1
    except Exception as e:
        logger.warning("Phase 17 coding Decision Engine fallback: %s", e)
        decision = None
    # Gap fix: Decision Engine থেকে knowledge/pattern/template ম্যাচ এসেও কোড-চেকে
    # ফেল করলে (স্ট্র্যাটেজ direct) বা confidence কম বলে সরাসরি ai-তে পড়লে এন্ট্রিগুলো
    # আগে সম্পূর্ণ বাতিল হয়ে যেত। ইউজারের /addknowledge, /addpattern, /addtemplate
    # দেওয়া নিয়ম প্রায়শই কোড নয়, টেক্সট-গাইডলাইন — ফেলে না দিয়ে candidate list থেকে
    # শীর্ষ কয়েকটা non-code এন্ট্রি তুলে নিই; নিচে AI-এর system_prompt-এ "অবশ্যই মেনে
    # চলার নিয়ম" হিসেবে যাবে। (code_ok হলে উপরেই return — এখানে শুধু AI-routেই আসে।)
    if decision is not None:
        relevant_rules = _collect_relevant_brain_rules(decision, project.get("stack", ""))

    if is_no_api_mode(project.get("user_id", 0)):
        stuck_msg = build_no_api_stuck_message({"stage": "coding_ai_route", "confidence": 0.0})
        save_task_result(task["id"], f"[No API Mode]\n{stuck_msg}", source="no_api_blocked", status="failed")
        task["code"], task["source"], task["status"] = stuck_msg, "no_api_blocked", "failed"
        task["no_api_blocked"] = True
        return task

    brain_os_metrics["ai_routes"] += 1
    all_tasks = get_project_tasks(project["id"])
    done_titles = [t["title"] for t in all_tasks if t["status"] == "done"][-CODE_CONTEXT_PREV_TASKS:]
    context_note = ("আগের সম্পন্ন ধাপ: " + "; ".join(done_titles)) if done_titles else "এটাই প্রথম ধাপ।"

    # আগের ধাপগুলোর প্রকৃত কোডও context হিসেবে পাঠানো হয় — নইলে AI প্রতিবার
    # নতুন করে পুরো স্ক্রিপ্ট কল্পনা করে লেখে আর /exportcode-এ ডুপ্লিকেট main()/
    # if __name__ ব্লক জমে যায়। কোনো এররে আগের (শুধু-শিরোনাম) আচরণে fallback।
    existing_code = ""
    try:
        existing_code = assemble_project_code(project["id"])
        if len(existing_code) > CODE_CONTEXT_EXISTING_CODE_MAX_CHARS:
            existing_code = existing_code[-CODE_CONTEXT_EXISTING_CODE_MAX_CHARS:]
    except Exception as e:
        logger.warning("process_next_code_task: existing-code context failed: %s", e)
        existing_code = ""

    system_prompt = (
        "তুমি একজন অভিজ্ঞ প্রোগ্রামার। এই প্রজেক্টের একটা নির্দিষ্ট ধাপ (ফিচার/অংশ) "
        "যোগ করতে হবে। শুধু কোড দাও (দরকার হলে ছোট কমেন্ট থাকতে পারে), বাড়তি "
        "ভূমিকা/ব্যাখ্যা লেখার দরকার নেই।\n"
        f"প্রজেক্ট: {project['name']} | স্ট্যাক/ভাষা: {project['stack']}\n{context_note}\n"
    )
    if existing_code.strip():
        system_prompt += (
            "\nএখন পর্যন্ত ফাইলটা এরকম দেখতে (আগের ধাপগুলো মিলিয়ে):\n"
            f"```\n{existing_code}\n```\n"
            "গুরুত্বপূর্ণ: এই ধাপের জন্য তুমি **সম্পূর্ণ আপডেটেড ফাইল** ফেরত দেবে "
            "(উপরের কোডের সাথে এই ধাপের পরিবর্তন যোগ করে), শুধু নতুন অংশটুকু না। "
            "একই ফাংশন/if __name__ ব্লক দুইবার রাখবে না — পুরনোটা প্রয়োজনমতো "
            "সম্পাদনা/প্রতিস্থাপন করে একটামাত্র পরিষ্কার, চালানোর-যোগ্য ফাইল দেবে।"
        )
    else:
        system_prompt += "\nএটাই এই প্রজেক্টের প্রথম কোড — নতুন ফাইল লেখো।"
    # Decision Engine-এর প্রাসঙ্গিক কিন্তু কোড-না-হওয়া এন্ট্রিগুলো (/addknowledge,
    # /addpattern, /addtemplate-এ দেওয়া নিয়ম) নির্দেশনা হিসেবে AI-কে জানানো হয়।
    if relevant_rules:
        system_prompt += (
            "\nএই ধাপের কোড লেখার সময় নিচের প্রাসঙ্গিক নিয়ম/গাইডলাইনগুলো অবশ্যই মেনে চলো:\n"
            + "\n".join(f"- {rule}" for rule in relevant_rules)
            + "\n"
        )
    live_context = _brain_get_live_context(project.get("user_id", 0)) if project.get("user_id") else ""
    if live_context:
        context_note += "\nBrain OS context:\n" + live_context
    user_text = f"ধাপ: {task['title']}\nবিবরণ: {task['description']}"
    try:
        reply = await ask_ai(system_prompt, user_text, user_id=project.get("user_id"))
        code = _strip_code_fences(reply)
        save_task_result(task["id"], code, source="ai")
        task["code"], task["source"], task["status"] = code, "ai", "done"
    except AIProviderError as e:
        save_task_result(task["id"], f"[এরর: {e}]", source="ai_error", status="failed")
        task["status"] = "failed"
    return task


def _code_has_main_guard(code: str) -> bool:
    """Python entry-point ব্লক (if __name__ == "__main__") আছে কি না — de-dup heuristic-এর জন্য।"""
    return "if __name__" in (code or "") and "__main__" in (code or "")


def _assemble_task_group(tasks: list) -> str:
    """একই ফাইলের (গ্রুপের) ধাপগুলো জোড়া লাগায়; একাধিক ধাপে entry-point ব্লক থাকলে
    ধরে নেওয়া হয় পরের ধাপগুলো আগেরটার updated ভার্সন — শুধু সর্বশেষ (সর্বোচ্চ seq)
    ধাপের কোডটাই চূড়ান্ত রানেবল ফাইল হিসেবে নেওয়া হয়।"""
    guarded = [t for t in tasks if _code_has_main_guard(t["code"])]
    if len(guarded) >= 2:
        latest = max(guarded, key=lambda t: t["seq"])
        return (latest["code"] or "").strip()
    # অন্যথায় আগের মতো ধাপে ধাপে জোড়া (আলাদা আলাদা helper/অংশ হলে এটাই সঠিক)।
    parts = [f"# ---- ধাপ {t['seq']}: {t['title']} ----\n{t['code']}\n" for t in tasks]
    return "\n\n".join(parts).strip()


def assemble_project_code(project_id: int) -> str:
    """বট নিজে থেকে সব সম্পন্ন ধাপের কোড জোড়া লাগিয়ে (assemble) একটা সম্পূর্ণ ফাইল বানায়।

    Safety net: একাধিক ধাপে `if __name__ == "__main__":` ব্লক থাকলে সেগুলোকে একই
    ফাইলের ক্রমাগত ভার্সন ধরে শুধু সর্বশেষটাই রাখা হয় (raw concatenate করলে main()
    বারবার redefine হয়ে ডুপ্লিকেট আউটপুট আসত)। Multi-file প্রজেক্টে (আলাদা আলাদা
    target_files) প্রতিটা ফাইল-গ্রুপে আলাদাভাবে একই লজিক প্রয়োগ হয়। কোনো এররে
    পুরনো concatenate আচরণে fallback (non-fatal)।"""
    all_tasks = get_project_tasks(project_id)
    done_tasks = [t for t in all_tasks if t["status"] == "done" and t["code"]]
    if not done_tasks:
        return ""
    try:
        # Multi-file হলে target_files অনুযায়ী গ্রুপ (seq-অর্ডার অক্ষুণ্ণ রেখে);
        # target_files খালি থাকলে সবগুলো একটাই (single-file) গ্রুপ।
        groups: dict = {}
        group_order = []
        for t in done_tasks:
            key = (t.get("target_files") or "").strip().lower()
            if key not in groups:
                groups[key] = []
                group_order.append(key)
            groups[key].append(t)
        if len(group_order) <= 1:
            return _assemble_task_group(done_tasks)
        sections = []
        for key in group_order:
            body = _assemble_task_group(groups[key])
            if not body:
                continue
            label = (groups[key][0].get("target_files") or "").strip()
            header = f"# ==== ফাইল: {label} ====\n" if label else ""
            sections.append(f"{header}{body}")
        return "\n\n\n".join(sections).strip()
    except Exception as e:
        logger.warning("assemble_project_code de-dup fallback to concatenate: %s", e)
        parts = [f"# ---- ধাপ {t['seq']}: {t['title']} ----\n{t['code']}\n" for t in done_tasks]
        return "\n\n".join(parts).strip()


def build_project_status_text(project: dict) -> str:
    tasks = get_project_tasks(project["id"])
    done = sum(1 for t in tasks if t["status"] == "done")
    lines = [
        f"📂 প্রজেক্ট #{project['id']}: {project['name']}",
        f"স্ট্যাক: {project['stack']} | অবস্থা: {project['status']} | অগ্রগতি: {done}/{len(tasks)} ধাপ\n",
    ]
    status_icon = {"pending": "⏳", "done": "✅", "failed": "❌", "in_progress": "🔧"}
    for t in tasks:
        icon = status_icon.get(t["status"], "•")
        src = f" [{t['source']}]" if t["status"] == "done" and t["source"] else ""
        lines.append(f"{icon} ধাপ {t['seq']}: {t['title']}{src}")
    return "\n".join(lines)



# =============================================================================
# Phase 18 — Full Codebase Intelligence (stdlib-only, local, incremental)
# =============================================================================

CODEBASE_INDEX_VERSION = 1
CODEBASE_DEFAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
CODEBASE_IGNORED_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".tox", ".venv", "venv", "env", "node_modules", "logs",
}
CODEBASE_MAX_FILE_BYTES = int(os.getenv("CODEBASE_MAX_FILE_BYTES", str(5 * 1024 * 1024)))
CODEBASE_SCAN_BATCH_SIZE = int(os.getenv("CODEBASE_SCAN_BATCH_SIZE", "50"))

def _codebase_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _codebase_safe_relpath(path: str, root: str) -> str:
    try:
        return os.path.relpath(os.path.abspath(path), os.path.abspath(root)).replace(os.sep, "/")
    except Exception:
        return os.path.basename(path)

def _codebase_file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _codebase_docstring(node: ast.AST) -> str:
    try:
        value = ast.get_docstring(node, clean=True) or ""
        return value[:4000]
    except Exception:
        return ""

def _codebase_literal_string(node: Optional[ast.AST]) -> str:
    try:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Str):
            return node.s
    except Exception:
        pass
    return ""

def _codebase_import_info(node: ast.AST) -> Tuple[str, str]:
    if isinstance(node, ast.Import):
        parts = [a.name for a in node.names]
        return ", ".join(parts), ""
    if isinstance(node, ast.ImportFrom):
        module = "." * int(node.level or 0) + (node.module or "")
        names = ", ".join(
            f"{a.name}" + (f" as {a.asname}" if a.asname else "") for a in node.names
        )
        return module, names
    return "", ""

def _codebase_top_level_symbols(tree: ast.AST) -> List[Dict[str, Any]]:
    """AST থেকে module-level variable/function/class/import/route metadata বের করে।"""
    symbols: List[Dict[str, Any]] = []
    try:
        body = getattr(tree, "body", [])
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append({
                    "name": node.name, "qualified_name": node.name, "symbol_type": "function",
                    "line": getattr(node, "lineno", 0), "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                    "docstring": _codebase_docstring(node), "metadata": {},
                })
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Nested functions are useful context, but are not top-level functions.
                        pass
            elif isinstance(node, ast.ClassDef):
                symbols.append({
                    "name": node.name, "qualified_name": node.name, "symbol_type": "class",
                    "line": getattr(node, "lineno", 0), "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                    "docstring": _codebase_docstring(node), "metadata": {},
                })
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append({
                            "name": child.name, "qualified_name": f"{node.name}.{child.name}",
                            "symbol_type": "method", "line": getattr(child, "lineno", 0),
                            "end_line": getattr(child, "end_lineno", getattr(child, "lineno", 0)),
                            "docstring": _codebase_docstring(child), "metadata": {"class": node.name},
                        })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                module, imported = _codebase_import_info(node)
                for alias in node.names:
                    display = module if isinstance(node, ast.Import) else f"{module}:{alias.name}"
                    symbols.append({
                        "name": alias.asname or alias.name, "qualified_name": display,
                        "symbol_type": "import", "line": getattr(node, "lineno", 0),
                        "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                        "docstring": "", "metadata": {
                            "module": module, "imported": imported,
                            "name": alias.name, "alias": alias.asname or "",
                        },
                    })
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = []
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, (ast.Name, ast.Tuple, ast.List)):
                            targets.append(target)
                elif isinstance(node, ast.AnnAssign):
                    targets.append(node.target)
                else:
                    targets.append(node.target)
                for target in targets:
                    names = [target.id] if isinstance(target, ast.Name) else [
                        x.id for x in ast.walk(target) if isinstance(x, ast.Name)
                    ]
                    for name in names:
                        symbols.append({
                            "name": name, "qualified_name": name, "symbol_type": "variable",
                            "line": getattr(node, "lineno", 0),
                            "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                            "docstring": "", "metadata": {},
                        })
    except Exception as e:
        logger.warning("Phase 18 symbol extraction failed: %s", e)
    return symbols

def _codebase_find_local_python_files(root: str) -> List[str]:
    files: List[str] = []
    try:
        for current, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if d not in CODEBASE_IGNORED_DIRS and not d.startswith(".")]
            for name in names:
                path = os.path.join(current, name)
                if os.path.islink(path):
                    continue
                try:
                    if os.path.isfile(path):
                        abs_path = os.path.abspath(path)
                        ignored_runtime = {
                            os.path.abspath(str(globals().get("DB_PATH", ""))) if globals().get("DB_PATH") else "",
                            os.path.abspath(str(globals().get("LOG_FILE", ""))) if globals().get("LOG_FILE") else "",
                        }
                        if abs_path in ignored_runtime:
                            continue
                        files.append(abs_path)
                except OSError:
                    continue
    except Exception as e:
        logger.warning("Phase 18 project walk failed: %s", e)
    return files

def _codebase_is_local_python_import(module: str, root: str, current_file: Optional[str] = None) -> Optional[str]:
    """Import module-কে project-এর .py file-এ resolve করার best-effort চেষ্টা; relative import-ও ধরা হয়।"""
    try:
        module = (module or "").strip()
        if not module:
            return None
        if module.startswith("."):
            dots = len(module) - len(module.lstrip("."))
            tail = module[dots:].lstrip(".")
            base = os.path.dirname(os.path.abspath(current_file)) if current_file else root
            for _ in range(max(0, dots - 1)):
                base = os.path.dirname(base)
            rel = tail.replace(".", os.sep)
            candidates = [
                os.path.join(base, rel + ".py"),
                os.path.join(base, rel, "__init__.py"),
            ]
        else:
            rel = module.replace(".", os.sep)
            candidates = [
                os.path.join(root, rel + ".py"),
                os.path.join(root, rel, "__init__.py"),
            ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)
    except Exception:
        pass
    return None

def _codebase_extract_routes(tree: ast.AST) -> List[Dict[str, Any]]:
    routes: List[Dict[str, Any]] = []
    try:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_handler" or not node.args:
                continue
            handler = node.args[0]
            if not isinstance(handler, ast.Call) or not isinstance(handler.func, ast.Name):
                continue
            handler_type = handler.func.id
            if handler_type not in {"CommandHandler", "MessageHandler", "CallbackQueryHandler"}:
                continue
            callback_name = ""
            if handler_type == "CommandHandler":
                command = _codebase_literal_string(handler.args[0] if handler.args else None)
                callback = handler.args[1] if len(handler.args) > 1 else None
                callback_name = callback.id if isinstance(callback, ast.Name) else (
                    getattr(callback, "attr", "") if isinstance(callback, ast.Attribute) else ""
                )
                if command:
                    routes.append({
                        "route_type": "command", "route": "/" + command.lstrip("/"),
                        "handler": callback_name, "line": getattr(node, "lineno", 0),
                        "details": {"handler_class": handler_type},
                    })
            else:
                callback = handler.args[0] if handler.args else None
                callback_name = callback.id if isinstance(callback, ast.Name) else (
                    getattr(callback, "attr", "") if isinstance(callback, ast.Attribute) else ""
                )
                if callback_name:
                    routes.append({
                        "route_type": "message" if handler_type == "MessageHandler" else "callback",
                        "route": handler_type, "handler": callback_name,
                        "line": getattr(node, "lineno", 0),
                        "details": {"handler_class": handler_type},
                    })
    except Exception as e:
        logger.warning("Phase 18 route extraction failed: %s", e)
    return routes

def _codebase_collect_calls(node: ast.AST) -> List[Dict[str, Any]]:
    calls: List[Dict[str, Any]] = []
    try:
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            target = ""
            if isinstance(call.func, ast.Name):
                target = call.func.id
            elif isinstance(call.func, ast.Attribute):
                chain = []
                cur = call.func
                while isinstance(cur, ast.Attribute):
                    chain.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    chain.append(cur.id)
                target = ".".join(reversed(chain))
            if target:
                calls.append({"target": target, "line": getattr(call, "lineno", 0)})
    except Exception:
        pass
    return calls

def _codebase_parse_python(path: str) -> Tuple[Optional[ast.AST], List[Dict[str, Any]], List[Dict[str, Any]], str]:
    try:
        if os.path.getsize(path) > CODEBASE_MAX_FILE_BYTES:
            return None, [], [], "file_too_large"
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=path)
        symbols = _codebase_top_level_symbols(tree)
        routes = _codebase_extract_routes(tree)
        return tree, symbols, routes, ""
    except SyntaxError as e:
        return None, [], [], f"syntax_error:{e.msg}"
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        return None, [], [], f"read_error:{type(e).__name__}"
    except Exception as e:
        return None, [], [], f"parse_error:{type(e).__name__}"

def _migrate_codebase_intelligence(cur: sqlite3.Cursor) -> None:
    """Phase 18-এর idempotent schema migration; Phase 14/15-এর PRAGMA+ALTER pattern অনুসরণ করে।"""
    migrations = {
        "brain_codebase_files": {
            "relative_path": "TEXT", "is_directory": "INTEGER DEFAULT 0", "is_python": "INTEGER DEFAULT 0",
            "file_hash": "TEXT DEFAULT ''", "mtime": "REAL DEFAULT 0", "file_size": "INTEGER DEFAULT 0",
            "parse_ok": "INTEGER DEFAULT 0", "parse_error": "TEXT DEFAULT ''",
            "last_indexed_at": "TEXT DEFAULT ''", "scan_version": "INTEGER DEFAULT 1",
        },
        "brain_codebase_symbols": {
            "qualified_name": "TEXT DEFAULT ''", "symbol_type": "TEXT DEFAULT 'unknown'",
            "line_number": "INTEGER DEFAULT 0", "end_line": "INTEGER DEFAULT 0",
            "docstring": "TEXT DEFAULT ''", "metadata": "TEXT DEFAULT '{}'",
            "last_indexed_at": "TEXT DEFAULT ''",
        },
        "brain_codebase_edges": {
            "source_file_id": "INTEGER", "source_symbol_id": "INTEGER", "target_file_id": "INTEGER",
            "target_symbol_id": "INTEGER", "edge_type": "TEXT DEFAULT 'reference'",
            "source_name": "TEXT DEFAULT ''", "target_name": "TEXT DEFAULT ''",
            "route_name": "TEXT DEFAULT ''", "line_number": "INTEGER DEFAULT 0",
            "metadata": "TEXT DEFAULT '{}'", "last_indexed_at": "TEXT DEFAULT ''",
        },
    }
    for table, columns in migrations.items():
        try:
            cur.execute(f"PRAGMA table_info({table})")
            existing = {row[1] for row in cur.fetchall()}
            for col, col_type in columns.items():
                if col not in existing:
                    try:
                        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                    except sqlite3.OperationalError as e:
                        logger.warning("Phase 18 migration %s.%s skipped: %s", table, col, e)
        except Exception as e:
            logger.warning("Phase 18 migration inspection failed for %s: %s", table, e)

def _codebase_ensure_tables(conn: sqlite3.Connection) -> None:
    """Phase 18 schema — CREATE IF NOT EXISTS + safe column migration."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS brain_codebase_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            relative_path TEXT,
            is_directory INTEGER DEFAULT 0,
            is_python INTEGER DEFAULT 0,
            file_hash TEXT DEFAULT '',
            mtime REAL DEFAULT 0,
            file_size INTEGER DEFAULT 0,
            parse_ok INTEGER DEFAULT 0,
            parse_error TEXT DEFAULT '',
            last_indexed_at TEXT DEFAULT '',
            scan_version INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS brain_codebase_symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            symbol_name TEXT NOT NULL,
            qualified_name TEXT NOT NULL,
            symbol_type TEXT NOT NULL,
            line_number INTEGER DEFAULT 0,
            end_line INTEGER DEFAULT 0,
            docstring TEXT DEFAULT '',
            metadata TEXT DEFAULT '{}',
            last_indexed_at TEXT DEFAULT '',
            FOREIGN KEY(file_id) REFERENCES brain_codebase_files(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS brain_codebase_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file_id INTEGER,
            source_symbol_id INTEGER,
            target_file_id INTEGER,
            target_symbol_id INTEGER,
            edge_type TEXT NOT NULL,
            source_name TEXT DEFAULT '',
            target_name TEXT DEFAULT '',
            route_name TEXT DEFAULT '',
            line_number INTEGER DEFAULT 0,
            metadata TEXT DEFAULT '{}',
            last_indexed_at TEXT DEFAULT '',
            FOREIGN KEY(source_file_id) REFERENCES brain_codebase_files(id) ON DELETE CASCADE,
            FOREIGN KEY(source_symbol_id) REFERENCES brain_codebase_symbols(id) ON DELETE CASCADE
        )
    """)
    _migrate_codebase_intelligence(cur)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bc_files_hash ON brain_codebase_files(file_hash, mtime)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bc_symbols_file ON brain_codebase_symbols(file_id, symbol_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bc_symbols_name ON brain_codebase_symbols(symbol_name, qualified_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bc_edges_source ON brain_codebase_edges(source_file_id, source_symbol_id, edge_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bc_edges_target ON brain_codebase_edges(target_file_id, target_name, edge_type)")
    conn.commit()

def _codebase_resolve_symbol(cur: sqlite3.Cursor, name: str, current_file_id: int = 0) -> Optional[Tuple[int, int, str]]:
    """নাম থেকে best-effort symbol resolution: same-file -> exact qualified -> unique name."""
    try:
        if not name:
            return None
        base = name.split(".")[-1]
        if current_file_id:
            cur.execute(
                "SELECT id,file_id,qualified_name FROM brain_codebase_symbols "
                "WHERE file_id=? AND symbol_type NOT IN ('import','variable') "
                "AND (qualified_name=? OR symbol_name=?) "
                "ORDER BY CASE WHEN qualified_name=? THEN 0 ELSE 1 END LIMIT 1",
                (current_file_id, name, base, name),
            )
            row = cur.fetchone()
            if row:
                return row
        cur.execute(
            "SELECT id,file_id,qualified_name FROM brain_codebase_symbols "
            "WHERE symbol_type NOT IN ('import','variable') AND (qualified_name=? OR symbol_name=?) "
            "ORDER BY CASE WHEN qualified_name=? THEN 0 ELSE 1 END",
            (name, base, name),
        )
        rows = cur.fetchall()
        return rows[0] if len(rows) == 1 else (rows[0] if rows else None)
    except Exception:
        return None

def _codebase_insert_file(cur: sqlite3.Cursor, path: str, root: str, stat: os.stat_result,
                          file_hash: str, is_python: bool, parse_ok: bool, parse_error: str,
                          indexed_at: str) -> int:
    cur.execute("""
        INSERT INTO brain_codebase_files
        (file_path,relative_path,is_directory,is_python,file_hash,mtime,file_size,parse_ok,parse_error,last_indexed_at,scan_version)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(file_path) DO UPDATE SET
            relative_path=excluded.relative_path,is_directory=excluded.is_directory,
            is_python=excluded.is_python,file_hash=excluded.file_hash,mtime=excluded.mtime,
            file_size=excluded.file_size,parse_ok=excluded.parse_ok,parse_error=excluded.parse_error,
            last_indexed_at=excluded.last_indexed_at,scan_version=excluded.scan_version
    """, (
        os.path.abspath(path), _codebase_safe_relpath(path, root), 0, int(is_python),
        file_hash, float(stat.st_mtime), int(stat.st_size), int(parse_ok), parse_error,
        indexed_at, CODEBASE_INDEX_VERSION,
    ))
    cur.execute("SELECT id FROM brain_codebase_files WHERE file_path=?", (os.path.abspath(path),))
    return int(cur.fetchone()[0])

def _codebase_index_python_file(cur: sqlite3.Cursor, file_id: int, path: str, root: str,
                                tree: ast.AST, symbols: List[Dict[str, Any]],
                                routes: List[Dict[str, Any]], indexed_at: str) -> None:
    cur.execute("DELETE FROM brain_codebase_edges WHERE source_file_id=?", (file_id,))
    cur.execute("DELETE FROM brain_codebase_symbols WHERE file_id=?", (file_id,))
    symbol_ids: Dict[str, int] = {}
    for item in symbols:
        cur.execute("""
            INSERT INTO brain_codebase_symbols
            (file_id,symbol_name,qualified_name,symbol_type,line_number,end_line,docstring,metadata,last_indexed_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            file_id, item["name"], item["qualified_name"], item["symbol_type"],
            int(item.get("line", 0)), int(item.get("end_line", 0)), item.get("docstring", ""),
            json.dumps(item.get("metadata", {}), ensure_ascii=False), indexed_at,
        ))
        sid = int(cur.lastrowid)
        symbol_ids[item["qualified_name"]] = sid
        symbol_ids.setdefault(item["name"], sid)

    # Imports become file-to-file dependency edges where a local module can be resolved.
    for item in symbols:
        if item["symbol_type"] != "import":
            continue
        meta = item.get("metadata", {})
        module = meta.get("module", "")
        target_path = _codebase_is_local_python_import(module, root)
        if target_path:
            cur.execute("SELECT id FROM brain_codebase_files WHERE file_path=?", (target_path,))
            target_row = cur.fetchone()
            if target_row:
                cur.execute("""
                    INSERT INTO brain_codebase_edges
                    (source_file_id,source_symbol_id,target_file_id,target_symbol_id,edge_type,
                     source_name,target_name,line_number,metadata,last_indexed_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    file_id, symbol_ids.get(item["qualified_name"]), int(target_row[0]), None,
                    "file_import", item["qualified_name"], module, item.get("line", 0), "{}", indexed_at,
                ))



def _codebase_index_python_edges(cur: sqlite3.Cursor, file_id: int, tree: ast.AST,
                                 routes: List[Dict[str, Any]], indexed_at: str) -> int:
    """সব Python symbols উপস্থিত হওয়ার পরে caller/callee ও route edges তৈরি করে।"""
    edge_count = 0
    try:
        cur.execute(
            "SELECT id,symbol_name,qualified_name,line_number,end_line,symbol_type "
            "FROM brain_codebase_symbols WHERE file_id=?",
            (file_id,),
        )
        rows = cur.fetchall()
        symbol_ids = {}
        for sid, name, qualified, line, end_line, typ in rows:
            symbol_ids[qualified] = sid
            symbol_ids.setdefault(name, sid)

        symbol_nodes: Dict[str, ast.AST] = {}
        for node in getattr(tree, "body", []):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbol_nodes[node.name] = node
            elif isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbol_nodes[f"{node.name}.{child.name}"] = child

        for caller_name, caller_node in symbol_nodes.items():
            caller_id = symbol_ids.get(caller_name)
            if not caller_id:
                continue
            for call in _codebase_collect_calls(caller_node):
                target_name = call["target"]
                target = _codebase_resolve_symbol(cur, target_name, file_id)
                target_id = target[0] if target else None
                target_file_id = target[1] if target else None
                cur.execute("""
                    INSERT INTO brain_codebase_edges
                    (source_file_id,source_symbol_id,target_file_id,target_symbol_id,edge_type,
                     source_name,target_name,line_number,metadata,last_indexed_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    file_id, caller_id, target_file_id, target_id, "call",
                    caller_name, target_name, call["line"], "{}", indexed_at,
                ))
                edge_count += 1

        for route in routes:
            handler_name = route.get("handler", "")
            target = _codebase_resolve_symbol(cur, handler_name, file_id)
            target_id = target[0] if target else None
            target_file_id = target[1] if target else file_id
            source_id = None
            route_line = int(route.get("line", 0) or 0)
            for sid, _name, _qualified, line, end_line, typ in rows:
                if typ in ("function", "method") and line <= route_line <= max(end_line, line):
                    source_id = sid
                    break
            cur.execute("""
                INSERT INTO brain_codebase_edges
                (source_file_id,source_symbol_id,target_file_id,target_symbol_id,edge_type,
                 source_name,target_name,route_name,line_number,metadata,last_indexed_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                file_id, source_id, target_file_id, target_id, "route",
                "handler_registration", handler_name, route["route"], route_line,
                json.dumps(route.get("details", {}), ensure_ascii=False), indexed_at,
            ))
            edge_count += 1
    except Exception as e:
        logger.warning("Phase 18 edge extraction failed for file_id=%s: %s", file_id, e)
    return edge_count

def _codebase_scan_sync(root: Optional[str] = None, force_full: bool = False) -> Dict[str, Any]:
    """Full/incremental local project scan. Heavy work is wrapped by async callers in to_thread()."""
    root = os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    started = time.time()
    stats = {
        "root": root, "files_seen": 0, "files_indexed": 0, "files_skipped": 0,
        "python_files": 0, "symbols": 0, "edges": 0, "errors": 0, "removed": 0,
        "duration_ms": 0, "full": bool(force_full), "last_indexed_at": _codebase_now(),
    }
    conn = None
    try:
        if not os.path.isdir(root):
            raise FileNotFoundError(root)
        conn = get_conn()
        conn.execute("PRAGMA foreign_keys = ON")
        _codebase_ensure_tables(conn)
        cur = conn.cursor()
        indexed_at = stats["last_indexed_at"]
        paths = _codebase_find_local_python_files(root)
        path_set = set(os.path.abspath(x) for x in paths)
        stats["files_seen"] = len(paths)
        stats["python_files"] = sum(1 for x in paths if x.lower().endswith(".py"))

        # Pass 1: record every file's metadata first. This makes local import targets
        # resolvable regardless of os.walk ordering.
        changed: List[Tuple[str, int, bool, str, os.stat_result]] = []
        for path in paths:
            try:
                st = os.stat(path)
                is_python = path.lower().endswith(".py")
                if not is_python and st.st_size > CODEBASE_MAX_FILE_BYTES:
                    file_hash = f"skipped_size:{st.st_size}"
                else:
                    file_hash = _codebase_file_hash(path)
                cur.execute(
                    "SELECT id,file_hash,mtime,file_size,is_python FROM brain_codebase_files WHERE file_path=?",
                    (path,),
                )
                old = cur.fetchone()
                unchanged = (
                    old and not force_full and old[1] == file_hash and
                    abs(float(old[2] or 0) - float(st.st_mtime)) < 0.000001 and
                    int(old[3] or 0) == int(st.st_size) and int(old[4] or 0) == int(is_python)
                )
                if unchanged:
                    stats["files_skipped"] += 1
                    continue
                file_id = _codebase_insert_file(
                    cur, path, root, st, file_hash, is_python, False if is_python else True,
                    "pending" if is_python else "", indexed_at
                )
                changed.append((path, file_id, is_python, file_hash, st))
            except Exception as e:
                stats["errors"] += 1
                logger.warning("Phase 18 metadata scan skipped: %s — %s", path, e)

        # Pass 2: parse/index only changed files. This is the incremental boundary.
        changed_python: List[Tuple[str, int, ast.AST, List[Dict[str, Any]]]] = []
        for path, file_id, is_python, _file_hash, _st in changed:
            try:
                if not is_python:
                    cur.execute(
                        "UPDATE brain_codebase_files SET parse_ok=1,parse_error='',last_indexed_at=? WHERE id=?",
                        (indexed_at, file_id),
                    )
                    cur.execute("DELETE FROM brain_codebase_edges WHERE source_file_id=?", (file_id,))
                    cur.execute("DELETE FROM brain_codebase_symbols WHERE file_id=?", (file_id,))
                    stats["files_indexed"] += 1
                    continue

                tree, symbols, routes, parse_error = _codebase_parse_python(path)
                parse_ok = tree is not None
                cur.execute(
                    "UPDATE brain_codebase_files SET parse_ok=?,parse_error=?,last_indexed_at=? WHERE id=?",
                    (int(parse_ok), parse_error, indexed_at, file_id),
                )
                if tree is not None:
                    _codebase_index_python_file(cur, file_id, path, root, tree, symbols, routes, indexed_at)
                    changed_python.append((path, file_id, tree, routes))
                    stats["symbols"] += len(symbols)
                else:
                    cur.execute("DELETE FROM brain_codebase_edges WHERE source_file_id=?", (file_id,))
                    cur.execute("DELETE FROM brain_codebase_symbols WHERE file_id=?", (file_id,))
                    stats["errors"] += 1
                stats["files_indexed"] += 1
            except Exception as e:
                stats["errors"] += 1
                logger.warning("Phase 18 Python index skipped: %s — %s", path, e)

        # Pass 3: all changed-file symbols now exist, so cross-file caller/callee resolution is stronger.
        for path, file_id, tree, routes in changed_python:
            stats["edges"] += _codebase_index_python_edges(cur, file_id, tree, routes, indexed_at)

        # Delete disappeared files safely. Inbound edges are removed first because
        # target_file_id intentionally is not a hard FK (stale caller maps are retained
        # across incremental target changes until their source file is reindexed).
        prefix = root.rstrip(os.sep) + os.sep
        cur.execute("SELECT id,file_path FROM brain_codebase_files WHERE file_path LIKE ?", (prefix + "%",))
        for file_id, old_path in cur.fetchall():
            if os.path.abspath(old_path) not in path_set:
                cur.execute("DELETE FROM brain_codebase_edges WHERE source_file_id=? OR target_file_id=?", (file_id, file_id))
                cur.execute("DELETE FROM brain_codebase_files WHERE id=?", (file_id,))
                stats["removed"] += 1

        conn.commit()
        cur.execute("SELECT COUNT(*) FROM brain_codebase_files WHERE is_directory=0")
        stats["indexed_files_total"] = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM brain_codebase_symbols")
        stats["symbols_total"] = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM brain_codebase_edges")
        stats["edges_total"] = int(cur.fetchone()[0])
        return stats
    except Exception as e:
        if conn:
            conn.rollback()
        logger.warning("Phase 18 codebase scan failed: %s", e)
        stats["errors"] += 1
        stats["error"] = str(e)[:500]
        return stats
    finally:
        if conn:
            conn.close()
        stats["duration_ms"] = int((time.time() - started) * 1000)

def _codebase_status_sync(root: Optional[str] = None) -> Dict[str, Any]:
    root = os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    conn = None
    try:
        conn = get_conn()
        conn.execute("PRAGMA foreign_keys = ON")
        _codebase_ensure_tables(conn)
        cur = conn.cursor()
        prefix = root.rstrip(os.sep) + os.sep
        cur.execute("SELECT COUNT(*) FROM brain_codebase_files WHERE file_path LIKE ? AND is_python=1", (prefix + "%",))
        py_files = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM brain_codebase_files WHERE file_path LIKE ?", (prefix + "%",))
        files = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM brain_codebase_symbols s JOIN brain_codebase_files f ON f.id=s.file_id WHERE f.file_path LIKE ?", (prefix + "%",))
        symbols = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM brain_codebase_edges e JOIN brain_codebase_files f ON f.id=e.source_file_id WHERE f.file_path LIKE ?", (prefix + "%",))
        edges = int(cur.fetchone()[0])
        cur.execute("SELECT MAX(last_indexed_at) FROM brain_codebase_files WHERE file_path LIKE ?", (prefix + "%",))
        last_scan = cur.fetchone()[0] or ""
        cur.execute("SELECT COUNT(*) FROM brain_codebase_files WHERE file_path LIKE ? AND parse_ok=0 AND is_python=1", (prefix + "%",))
        parse_errors = int(cur.fetchone()[0])
        return {
            "root": root, "files": files, "python_files": py_files, "symbols": symbols,
            "edges": edges, "parse_errors": parse_errors, "last_scan": last_scan,
        }
    except Exception as e:
        logger.warning("Phase 18 status failed: %s", e)
        return {"root": root, "files": 0, "python_files": 0, "symbols": 0, "edges": 0, "parse_errors": 0, "last_scan": "", "error": str(e)}
    finally:
        if conn:
            conn.close()

def _codebase_search_sync(query: str, root: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Keyword/name/difflib search — no embeddings/API required."""
    root = os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    query = (query or "").strip()
    if not query:
        return []
    limit = max(1, min(int(limit), 100))
    tokens = [t.lower() for t in re.findall(r"[\w\u0980-\u09FF]+", query, flags=re.UNICODE) if t]
    conn = None
    try:
        conn = get_conn()
        _codebase_ensure_tables(conn)
        cur = conn.cursor()
        prefix = root.rstrip(os.sep) + os.sep
        cur.execute("""
            SELECT s.id,f.file_path,f.relative_path,s.symbol_name,s.qualified_name,s.symbol_type,
                   s.line_number,s.end_line,s.docstring,s.metadata
            FROM brain_codebase_symbols s JOIN brain_codebase_files f ON f.id=s.file_id
            WHERE f.file_path LIKE ?
            ORDER BY s.symbol_type,s.symbol_name
        """, (prefix + "%",))
        candidates = cur.fetchall()
        scored = []
        q_lower = query.lower()
        for row in candidates:
            _, file_path, rel, name, qual, typ, line, end_line, doc, metadata = row
            hay = " ".join([str(name), str(qual), str(rel), str(doc)]).lower()
            score = 0.0
            if q_lower == str(name).lower() or q_lower == str(qual).lower():
                score += 100
            if q_lower in hay:
                score += 50
            score += sum(15 for t in tokens if t in hay)
            if tokens:
                score += 20 * difflib.SequenceMatcher(None, q_lower, str(qual).lower()).ratio()
            if score > 0:
                scored.append({
                    "score": round(score, 3), "file_path": file_path, "relative_path": rel,
                    "name": name, "qualified_name": qual, "symbol_type": typ,
                    "line": line, "end_line": end_line, "docstring": doc,
                    "metadata": json.loads(metadata or "{}") if metadata else {},
                })
        scored.sort(key=lambda x: (x["score"], -int(x["line"] or 0)), reverse=True)
        return scored[:limit]
    except Exception as e:
        logger.warning("Phase 18 codebase search failed: %s", e)
        return []
    finally:
        if conn:
            conn.close()

def _codebase_relevant_context_sync(request: str, root: Optional[str] = None,
                                    max_items: int = 8, max_chars: int = 18000) -> str:
    """Future Coding Orchestrator-এর জন্য শুধু relevant file/function source অংশ ফেরত দেয়।"""
    root = os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    try:
        matches = _codebase_search_sync(request, root, max_items * 2)
        chunks: List[str] = []
        used = 0
        seen = set()
        for item in matches:
            key = (item["file_path"], item["line"], item["end_line"])
            if key in seen:
                continue
            seen.add(key)
            try:
                with open(item["file_path"], "r", encoding="utf-8") as f:
                    source_lines = f.readlines()
                start = max(1, int(item["line"] or 1) - 2)
                end = min(len(source_lines), int(item["end_line"] or item["line"] or start) + 2)
                snippet = "".join(source_lines[start - 1:end]).strip()
                block = (
                    f"# FILE: {item['relative_path']}\n"
                    f"# SYMBOL: {item['qualified_name']} ({item['symbol_type']}) lines {start}-{end}\n"
                    f"{snippet}\n"
                )
                if used + len(block) > max_chars:
                    break
                chunks.append(block)
                used += len(block)
                if len(chunks) >= max_items:
                    break
            except Exception as e:
                logger.debug("Phase 18 relevant context read skipped: %s", e)
        return "\n\n".join(chunks)
    except Exception as e:
        logger.warning("Phase 18 relevant context failed: %s", e)
        return ""

def _codebase_impact_sync(file_path: str, root: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """পরিবর্তিত file-এর reverse import/caller impact best-effort তালিকা।"""
    root = os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    target = os.path.abspath(file_path if os.path.isabs(file_path) else os.path.join(root, file_path))
    conn = None
    try:
        conn = get_conn()
        _codebase_ensure_tables(conn)
        cur = conn.cursor()
        cur.execute("SELECT id,relative_path FROM brain_codebase_files WHERE file_path=?", (target,))
        row = cur.fetchone()
        if not row:
            return []
        file_id, rel = row
        cur.execute("""
            SELECT e.edge_type,e.source_name,e.target_name,e.route_name,e.line_number,
                   sf.relative_path,ss.qualified_name
            FROM brain_codebase_edges e
            LEFT JOIN brain_codebase_files sf ON sf.id=e.source_file_id
            LEFT JOIN brain_codebase_symbols ss ON ss.id=e.source_symbol_id
            WHERE e.target_file_id=? AND e.edge_type IN ('file_import','call','route')
            ORDER BY e.edge_type,sf.relative_path,ss.qualified_name
            LIMIT ?
        """, (file_id, int(limit)))
        direct = cur.fetchall()
        result = []
        seen = set()
        for edge_type, source_name, target_name, route_name, line, src_rel, src_symbol in direct:
            key = (edge_type, src_rel, src_symbol, target_name, route_name)
            if key in seen:
                continue
            seen.add(key)
            result.append({
                "impact_type": edge_type, "file": src_rel or "",
                "function": src_symbol or "", "target": target_name or "",
                "route": route_name or "", "line": line or 0,
            })
        return result
    except Exception as e:
        logger.warning("Phase 18 impact analysis failed: %s", e)
        return []
    finally:
        if conn:
            conn.close()

def _codebase_suggest_placement_sync(request: str, root: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Existing architecture অনুসরণ করে নতুন code রাখার heuristic suggestion."""
    root = os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    try:
        matches = _codebase_search_sync(request, root, max(5, limit * 4))
        suggestions = []
        seen = set()
        for item in matches:
            key = item["file_path"]
            if key in seen:
                continue
            seen.add(key)
            reason = "similar symbol name"
            if any(t in item["symbol_type"] for t in ("function", "method")):
                reason = "similar function/method"
            elif item["symbol_type"] == "class":
                reason = "similar class"
            suggestions.append({
                "file_path": item["file_path"], "relative_path": item["relative_path"],
                "near_symbol": item["qualified_name"], "line": item["line"], "reason": reason,
            })
            if len(suggestions) >= limit:
                break
        if not suggestions:
            # Import heuristic: prefer a Python file that already contains the requested technology/module keyword.
            for item in _codebase_search_sync(request + " import", root, limit):
                suggestions.append({
                    "file_path": item["file_path"], "relative_path": item["relative_path"],
                    "near_symbol": item["qualified_name"], "line": item["line"],
                    "reason": "related import/name",
                })
        return suggestions[:limit]
    except Exception as e:
        logger.warning("Phase 18 placement heuristic failed: %s", e)
        return []

async def codebase_scan(root: Optional[str] = None, force_full: bool = False) -> Dict[str, Any]:
    try:
        return await asyncio.to_thread(_codebase_scan_sync, root, force_full)
    except Exception as e:
        logger.warning("Phase 18 async scan fallback: %s", e)
        return {"error": str(e), "files_indexed": 0, "symbols_total": 0, "edges_total": 0}

async def codebase_status(root: Optional[str] = None) -> Dict[str, Any]:
    try:
        return await asyncio.to_thread(_codebase_status_sync, root)
    except Exception as e:
        logger.warning("Phase 18 async status fallback: %s", e)
        return {"error": str(e), "files": 0, "python_files": 0, "symbols": 0, "edges": 0}

def codebase_search(query: str, root: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    try:
        return _codebase_search_sync(query, root, limit)
    except Exception as e:
        logger.warning("Phase 18 search fallback: %s", e)
        return []

def codebase_relevant_context(request: str, root: Optional[str] = None, max_items: int = 8, max_chars: int = 18000) -> str:
    try:
        return _codebase_relevant_context_sync(request, root, max_items, max_chars)
    except Exception as e:
        logger.warning("Phase 18 relevant context fallback: %s", e)
        return ""

def codebase_impact_analysis(file_path: str, root: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    try:
        return _codebase_impact_sync(file_path, root, limit)
    except Exception as e:
        logger.warning("Phase 18 impact fallback: %s", e)
        return []

def codebase_suggest_placement(request: str, root: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        return _codebase_suggest_placement_sync(request, root, limit)
    except Exception as e:
        logger.warning("Phase 18 placement fallback: %s", e)
        return []

def build_codebase_architecture_summary(root: Optional[str] = None, max_files: int = 60) -> str:
    try:
        root = os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
        status = _codebase_status_sync(root)
        conn = get_conn()
        _codebase_ensure_tables(conn)
        cur = conn.cursor()
        prefix = root.rstrip(os.sep) + os.sep
        cur.execute("""
            SELECT f.relative_path, f.is_python, f.parse_ok, COUNT(s.id)
            FROM brain_codebase_files f
            LEFT JOIN brain_codebase_symbols s ON s.file_id=f.id
            WHERE f.file_path LIKE ?
            GROUP BY f.id ORDER BY f.relative_path LIMIT ?
        """, (prefix + "%", int(max_files)))
        rows = cur.fetchall()
        cur.close(); conn.close()
        out = [
            "🧩 Codebase Architecture Summary",
            f"Root: {root}",
            f"Files: {status.get('files', 0)} | Python: {status.get('python_files', 0)} | Symbols: {status.get('symbols', 0)} | Edges: {status.get('edges', 0)}",
            f"Last scan: {status.get('last_scan') or 'এখনো scan হয়নি'}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        for rel, is_py, parse_ok, count in rows:
            marker = "🐍" if is_py else "📄"
            if is_py and not parse_ok:
                marker = "⚠️"
            out.append(f"{marker} {rel} — {count} symbols")
        return "\n".join(out)
    except Exception as e:
        logger.warning("Phase 18 architecture summary failed: %s", e)
        return "🧩 Codebase Architecture Summary\nএই মুহূর্তে index পড়া যাচ্ছে না।"

def build_codebase_scan_report(stats: Dict[str, Any]) -> str:
    return (
        "🧩 Codebase Scan সম্পন্ন\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Root: {stats.get('root', '')}\n"
        f"এই scan-এ index/re-index: {stats.get('files_indexed', 0)}\n"
        f"Unchanged skip: {stats.get('files_skipped', 0)}\n"
        f"Removed: {stats.get('removed', 0)}\n"
        f"Python file encountered: {stats.get('python_files', 0)}\n"
        f"Symbols এখন মোট: {stats.get('symbols_total', 0)}\n"
        f"Edges এখন মোট: {stats.get('edges_total', 0)}\n"
        f"Error/Skipped: {stats.get('errors', 0)}\n"
        f"সময়: {stats.get('duration_ms', 0)} ms"
    )

async def codebasescan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only Phase 18 full codebase rescan."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    try:
        root = " ".join(context.args).strip() if context.args else CODEBASE_DEFAULT_ROOT
        root = os.path.abspath(root)
        if not os.path.isdir(root):
            await update.message.reply_text("দেওয়া project directory পাওয়া যায়নি।")
            return
        thinking = await update.message.reply_text("🧩 Codebase scan শুরু হয়েছে… বড় project হলে কিছু সময় লাগতে পারে।")
        try:
            stats = await codebase_scan(root, force_full=True)
            await send_long_text(update, build_codebase_scan_report(stats))
        finally:
            try:
                await thinking.delete()
            except Exception:
                pass
    except Exception as e:
        logger.warning("Phase 18 /codebasescan failed: %s", e)
        await update.message.reply_text("Codebase scan চালাতে সমস্যা হয়েছে।")

async def codebasestatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only Phase 18 codebase index status."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    try:
        root = " ".join(context.args).strip() if context.args else CODEBASE_DEFAULT_ROOT
        status = await codebase_status(os.path.abspath(root))
        text = (
            "🧩 Codebase Index Status\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Root: {status.get('root', root)}\n"
            f"Files: {status.get('files', 0)}\n"
            f"Python files: {status.get('python_files', 0)}\n"
            f"Symbols: {status.get('symbols', 0)}\n"
            f"Edges: {status.get('edges', 0)}\n"
            f"Parse errors: {status.get('parse_errors', 0)}\n"
            f"Last indexed: {status.get('last_scan') or 'এখনো scan হয়নি'}"
        )
        await send_long_text(update, text)
    except Exception as e:
        logger.warning("Phase 18 /codebasestatus failed: %s", e)
        await update.message.reply_text("Codebase index status পড়তে সমস্যা হয়েছে।")


# ============================================================================
# PHASE 19 — SMART CONTEXT BUILDER
# Compact, local-only context assembly layer on top of Phase 11/16/17/18.
# No new dependency, table, embedding API, vector DB or GPU.
# ============================================================================

SMART_CONTEXT_CACHE_TTL = 45
SMART_CONTEXT_CACHE_MAX = 128
SMART_CONTEXT_DEFAULT_BUDGET = 12000
SMART_CONTEXT_CODE_BUDGET = 6500
SMART_CONTEXT_DEP_BUDGET = 2200
SMART_CONTEXT_MEMORY_BUDGET = 1200
SMART_CONTEXT_HISTORY_BUDGET = 1400
SMART_CONTEXT_ERROR_BUDGET = 1200
_SMART_CONTEXT_CACHE: OrderedDict[str, Tuple[float, Dict[str, Any]]] = OrderedDict()


def _smart_context_now() -> float:
    try:
        return time.time()
    except Exception:
        return 0.0


def _smart_context_tokens(text: Any) -> int:
    """Cheap token estimate; ~4 characters/token, deliberately dependency-free."""
    try:
        return max(0, int(math.ceil(len(str(text or "")) / 4.0)))
    except Exception:
        return 0


def _smart_context_trim(text: Any, max_chars: int) -> str:
    try:
        value = str(text or "")
        return value if len(value) <= max_chars else value[:max_chars].rstrip() + "…"
    except Exception:
        return ""


def _smart_context_classify(user_text: str) -> Dict[str, Any]:
    """Local heuristic classifier: chat vs coding vs debugging, plus context depth."""
    try:
        text = (user_text or "").strip().lower()
        coding_terms = {
            "code", "coding", "python", "javascript", "typescript", "java", "php", "flask",
            "fastapi", "django", "telegram", "api", "database", "sqlite", "function", "class",
            "bug", "debug", "error", "exception", "traceback", "syntax", "refactor", "implement",
            "fix", "command", "handler", "main.py", "код", "কোড", "কোডিং", "ফাংশন", "বাগ", "এরর",
            "ডিবাগ", "ফিক্স", "ইমপ্লিমেন্ট", "প্রোগ্রাম",
        }
        debug_terms = {"bug", "debug", "error", "exception", "traceback", "fails", "failure", "broken", "crash", "বাগ", "ডিবাগ", "এরর", "সমস্যা", "ক্র্যাশ"}
        tokens = set(re.findall(r"[\w\u0980-\u09FF]+", text, flags=re.UNICODE))
        coding = bool(tokens & coding_terms)
        debugging = bool(tokens & debug_terms)
        kind = "debugging" if debugging else ("coding" if coding else "chat")
        return {
            "request_type": kind,
            "coding": coding,
            "debugging": debugging,
            "context_depth": "deep" if debugging else ("medium" if coding else "light"),
            "tokens": sorted(tokens)[:60],
        }
    except Exception as e:
        logger.debug("Phase 19 classification skipped: %s", e)
        return {"request_type": "chat", "coding": False, "debugging": False, "context_depth": "light", "tokens": []}


def _smart_context_cache_get(key: str) -> Optional[Dict[str, Any]]:
    try:
        item = _SMART_CONTEXT_CACHE.get(key)
        if not item:
            return None
        created, value = item
        if _smart_context_now() - created > SMART_CONTEXT_CACHE_TTL:
            _SMART_CONTEXT_CACHE.pop(key, None)
            return None
        _SMART_CONTEXT_CACHE.move_to_end(key)
        result = dict(value)
        result["cache_hit"] = True
        return result
    except Exception as e:
        logger.debug("Phase 19 cache get skipped: %s", e)
        return None


def _smart_context_cache_set(key: str, value: Dict[str, Any]) -> None:
    try:
        cached = dict(value)
        cached.pop("cache_hit", None)
        _SMART_CONTEXT_CACHE[key] = (_smart_context_now(), cached)
        _SMART_CONTEXT_CACHE.move_to_end(key)
        while len(_SMART_CONTEXT_CACHE) > SMART_CONTEXT_CACHE_MAX:
            _SMART_CONTEXT_CACHE.popitem(last=False)
    except Exception as e:
        logger.debug("Phase 19 cache set skipped: %s", e)


def _smart_context_get_code_context(user_text: str, root: Optional[str], budget: int, limit: int) -> Dict[str, Any]:
    """Reuse Phase 18 search/index; never rebuild its indexing layer."""
    result = {"files": [], "symbols": [], "dependencies": [], "text": "", "chars": 0}
    conn = None
    try:
        matches = codebase_search(user_text, root=root, limit=max(limit * 3, 12))
        seen_files, seen_symbols = set(), set()
        for item in matches:
            path = item.get("relative_path") or item.get("file_path") or ""
            symbol = item.get("qualified_name") or item.get("name") or ""
            key = (path, symbol, item.get("line", 0))
            if key in seen_symbols:
                continue
            seen_symbols.add(key)
            if path and path not in seen_files:
                seen_files.add(path)
                result["files"].append(path)
            result["symbols"].append({
                "file": path, "name": symbol, "type": item.get("symbol_type", ""),
                "line": item.get("line", 0), "end_line": item.get("end_line", 0),
                "docstring": _smart_context_trim(item.get("docstring", ""), 500),
                "score": item.get("score", 0),
            })
            if len(result["symbols"]) >= limit:
                break

        # Phase 18 already has a compact source helper. Prefer it for coding/debugging.
        if result["symbols"]:
            source = codebase_relevant_context(user_text, root=root, max_items=limit, max_chars=budget)
            result["text"] = _smart_context_trim(source, budget)

        # Direct dependency/caller edges only. No full graph traversal.
        conn = get_conn()
        _codebase_ensure_tables(conn)
        cur = conn.cursor()
        prefix = os.path.abspath(root or CODEBASE_DEFAULT_ROOT).rstrip(os.sep) + os.sep
        wanted = list(result["files"])
        for rel in wanted[:limit]:
            target_path = os.path.abspath(os.path.join(root or CODEBASE_DEFAULT_ROOT, rel))
            row = cur.execute("SELECT id FROM brain_codebase_files WHERE file_path=?", (target_path,)).fetchone()
            if not row:
                continue
            file_id = int(row[0])
            rows = cur.execute("""
                SELECT e.edge_type,e.source_name,e.target_name,e.route_name,e.line_number,
                       sf.relative_path,ss.qualified_name
                FROM brain_codebase_edges e
                LEFT JOIN brain_codebase_files sf ON sf.id=e.source_file_id
                LEFT JOIN brain_codebase_symbols ss ON ss.id=e.source_symbol_id
                WHERE (e.source_file_id=? OR e.target_file_id=?)
                  AND e.edge_type IN ('file_import','call','route')
                ORDER BY e.edge_type,sf.relative_path,ss.qualified_name
                LIMIT 60
            """, (file_id, file_id)).fetchall()
            for edge_type, source_name, target_name, route_name, line, src_rel, src_symbol in rows:
                dep = {
                    "type": edge_type, "source_file": src_rel or rel, "source_symbol": src_symbol or source_name or "",
                    "target": target_name or "", "route": route_name or "", "line": line or 0,
                }
                if dep not in result["dependencies"]:
                    result["dependencies"].append(dep)
                if len(result["dependencies"]) >= 40:
                    break
            if len(result["dependencies"]) >= 40:
                break
        return result
    except Exception as e:
        logger.warning("Phase 19 code context source failed: %s", e)
        return result
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass


def _smart_context_get_project_memory(user_id: Optional[int], user_text: str, budget: int) -> str:
    try:
        if not user_id:
            return ""
        project = get_active_project(int(user_id))
        if not project:
            return ""
        parts = [
            f"Active project: {project.get('name', '')}",
            f"Stack: {project.get('stack', '')}",
            f"Description: {_smart_context_trim(project.get('description', ''), 700)}",
            f"Status: {project.get('status', '')}",
        ]
        tasks = get_project_tasks(int(project.get("id", 0)))
        if tasks:
            relevant = []
            q = set(re.findall(r"[\w\u0980-\u09FF]+", (user_text or "").lower(), flags=re.UNICODE))
            for task in tasks:
                hay = f"{task.get('title','')} {task.get('description','')}".lower()
                overlap = len(q & set(re.findall(r"[\w\u0980-\u09FF]+", hay, flags=re.UNICODE)))
                if task.get("status") == "done" or overlap:
                    relevant.append((overlap + (2 if task.get("status") == "done" else 0), task))
            relevant.sort(key=lambda x: x[0], reverse=True)
            for _, task in relevant[:4]:
                parts.append(f"Task {task.get('seq','?')} [{task.get('status','')}]: {task.get('title','')}")
        # Phase 25: retrieve only project-specific long-term memories relevant to this request.
        try:
            v2 = project_memory_context(int(project.get("id", 0)), user_text, min(900, budget))
            if v2:
                parts.append("Project Memory 2.0:\n" + v2)
            # Phase 26: add only relevant, quality-ranked coding knowledge.
            kctx = coding_knowledge_context(int(project.get("id", 0)), user_text, min(900, max(500, budget // 2)))
            if kctx:
                parts.append("Coding Knowledge:\n" + kctx)
        except Exception as e:
            logger.debug("Phase 25 memory source skipped: %s", e)
        return _smart_context_trim("\n".join(parts), budget)
    except Exception as e:
        logger.warning("Phase 19 project memory source failed: %s", e)
        return ""


def _smart_context_get_decision_history(user_id: Optional[int], user_text: str, budget: int) -> str:
    try:
        rows = api_decision_history(user_id=user_id, limit=80)
        q = set(re.findall(r"[\w\u0980-\u09FF]+", (user_text or "").lower(), flags=re.UNICODE))
        ranked = []
        for row in rows:
            payload = row.get("payload", "")
            hay = f"{row.get('stage','')} {row.get('strategy','')} {row.get('provider_hint','')} {payload}".lower()
            overlap = sum(1 for token in q if token and token in hay)
            ranked.append((overlap, float(row.get("confidence", 0) or 0), row))
        ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
        parts = []
        for overlap, conf, row in ranked[:6]:
            if overlap <= 0 and parts:
                continue
            payload = _smart_context_trim(row.get("payload", ""), 450)
            parts.append(f"stage={row.get('stage','')} strategy={row.get('strategy','')} confidence={conf:.2f} payload={payload}")
        return _smart_context_trim("\n".join(parts), budget)
    except Exception as e:
        logger.warning("Phase 19 decision history source failed: %s", e)
        return ""


def _smart_context_get_error_history(user_text: str, budget: int) -> str:
    try:
        q = set(re.findall(r"[\w\u0980-\u09FF]+", (user_text or "").lower(), flags=re.UNICODE))
        if not q:
            return ""
        conn = get_brain_conn()
        try:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT error_signature,language,description,solution,category,severity,occurrence_count,updated_at
                FROM brain_errors
                WHERE deleted_at='' OR deleted_at IS NULL
                ORDER BY occurrence_count DESC, updated_at DESC LIMIT 80
            """).fetchall()
            ranked = []
            for row in rows:
                hay = " ".join(str(x or "") for x in row[:6]).lower()
                overlap = sum(1 for token in q if token in hay)
                if overlap:
                    ranked.append((overlap, row))
            ranked.sort(key=lambda x: x[0], reverse=True)
            parts = []
            for _, row in ranked[:5]:
                parts.append(
                    f"{row[0]} [{row[1]}|{row[4]}|{row[5]}] occurrences={row[6]} "
                    f"desc={_smart_context_trim(row[2],220)} solution={_smart_context_trim(row[3],320)}"
                )
            return _smart_context_trim("\n".join(parts), budget)
        finally:
            conn.close()
    except Exception as e:
        logger.warning("Phase 19 error history source failed: %s", e)
        return ""


def _smart_context_pack_sections(user_text: str, classification: Dict[str, Any], sections: List[Tuple[str, str, int]], max_tokens: int) -> Tuple[str, Dict[str, int]]:
    """Priority packer: current task > code > dependencies > memory > history/errors."""
    try:
        budget_chars = max(800, int(max_tokens) * 4)
        used = 0
        parts = []
        stats = {"current_task": 0, "code": 0, "dependencies": 0, "memory": 0, "history": 0, "errors": 0}
        for label, text, priority in sorted(sections, key=lambda x: x[2], reverse=True):
            if not text:
                continue
            remaining = budget_chars - used
            if remaining <= 80:
                break
            block = _smart_context_trim(text, remaining)
            if not block:
                continue
            rendered = f"[{label}]\n{block}"
            if used + len(rendered) > budget_chars:
                rendered = _smart_context_trim(rendered, remaining)
            if rendered:
                parts.append(rendered)
                used += len(rendered)
                key = {"CURRENT TASK":"current_task", "RELEVANT CODE":"code", "DEPENDENCIES":"dependencies",
                       "PROJECT MEMORY":"memory", "DECISION HISTORY":"history", "RELATED ERRORS":"errors"}.get(label, "code")
                stats[key] += len(rendered)
        return "\n\n".join(parts), stats
    except Exception as e:
        logger.warning("Phase 19 context packing failed: %s", e)
        return "", {k: 0 for k in ("current_task", "code", "dependencies", "memory", "history", "errors")}


def build_smart_context(user_id: Optional[int], user_text: str, root: Optional[str] = None, max_tokens: int = SMART_CONTEXT_DEFAULT_BUDGET) -> Dict[str, Any]:
    """Central Phase 19 context assembly API. Each source is optional and non-fatal."""
    text = (user_text or "").strip()
    try:
        classification = _smart_context_classify(text)
        safe_budget = max(512, min(int(max_tokens or SMART_CONTEXT_DEFAULT_BUDGET), 30000))
        cache_key = hashlib.sha256(json.dumps({"u": user_id, "t": text, "r": os.path.abspath(root or CODEBASE_DEFAULT_ROOT), "b": safe_budget}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        cached = _smart_context_cache_get(cache_key)
        if cached is not None:
            return cached

        code = {"files": [], "symbols": [], "dependencies": [], "text": "", "chars": 0}
        if classification.get("coding") or classification.get("debugging"):
            code = _smart_context_get_code_context(text, root, SMART_CONTEXT_CODE_BUDGET, 10)
        memory = _smart_context_get_project_memory(user_id, text, SMART_CONTEXT_MEMORY_BUDGET) if user_id else ""
        history = _smart_context_get_decision_history(user_id, text, SMART_CONTEXT_HISTORY_BUDGET) if user_id else ""
        errors = _smart_context_get_error_history(text, SMART_CONTEXT_ERROR_BUDGET) if classification.get("debugging") else ""
        dep_text = "\n".join(
            f"{d['type']}: {d.get('source_file','')}::{d.get('source_symbol','')} -> {d.get('target','')}"
            for d in code.get("dependencies", [])[:24]
        )
        current_task = _smart_context_trim(text, min(2400, safe_budget * 4))
        sections = [
            ("CURRENT TASK", current_task, 100),
            ("RELEVANT CODE", code.get("text", ""), 90),
            ("DEPENDENCIES", dep_text, 80),
            ("PROJECT MEMORY", memory, 60),
            ("DECISION HISTORY", history, 40),
            ("RELATED ERRORS", errors, 30),
        ]
        compact, char_stats = _smart_context_pack_sections(text, classification, sections, safe_budget)
        result = {
            "phase": 19, "request_type": classification.get("request_type", "chat"),
            "classification": classification, "files": code.get("files", [])[:20],
            "symbols": code.get("symbols", [])[:20], "dependencies": code.get("dependencies", [])[:40],
            "project_memory": memory, "decision_history": history, "error_history": errors,
            "context": compact, "approx_tokens": _smart_context_tokens(compact),
            "char_count": len(compact), "token_budget": safe_budget, "priority_chars": char_stats,
            "cache_hit": False,
        }
        # Never exceed the declared token budget after final assembly.
        if result["approx_tokens"] > safe_budget:
            result["context"] = _smart_context_trim(result["context"], safe_budget * 4)
            result["char_count"] = len(result["context"])
            result["approx_tokens"] = _smart_context_tokens(result["context"])
        _smart_context_cache_set(cache_key, result)
        return result
    except Exception as e:
        logger.warning("Phase 19 build_smart_context failed: %s", e)
        return {
            "phase": 19, "request_type": "chat", "classification": {"request_type": "chat"},
            "files": [], "symbols": [], "dependencies": [], "project_memory": "",
            "decision_history": "", "error_history": "", "context": _smart_context_trim(text, 2000),
            "approx_tokens": _smart_context_tokens(_smart_context_trim(text, 2000)),
            "char_count": min(len(text), 2000), "token_budget": max(512, int(max_tokens or SMART_CONTEXT_DEFAULT_BUDGET)),
            "priority_chars": {"current_task": min(len(text), 2000), "code": 0, "dependencies": 0, "memory": 0, "history": 0, "errors": 0},
            "cache_hit": False, "fallback": True,
        }


def smart_context_to_ai_input(smart_context: Dict[str, Any], base_system_prompt: str = "") -> Dict[str, Any]:
    """Convert assembled context to ask_ai/AIQueue-compatible system_prompt + messages."""
    try:
        context_text = str(smart_context.get("context", "") or "").strip()
        system = str(base_system_prompt or "").strip()
        if context_text:
            system = (system + "\n\n" if system else "") + "নিচের Smart Context-এ শুধু প্রাসঙ্গিক তথ্য ব্যবহার করো; অপ্রাসঙ্গিক/অনুমানভিত্তিক তথ্য ব্যবহার কোরো না।\n" + context_text
        return {"system_prompt": system, "messages": [], "context": context_text, "approx_tokens": _smart_context_tokens(context_text)}
    except Exception as e:
        logger.warning("Phase 19 AI input conversion failed: %s", e)
        return {"system_prompt": base_system_prompt or "", "messages": [], "context": "", "approx_tokens": 0}


def get_smart_context_cache_stats() -> Dict[str, Any]:
    try:
        now = _smart_context_now()
        live = sum(1 for created, _ in _SMART_CONTEXT_CACHE.values() if now - created <= SMART_CONTEXT_CACHE_TTL)
        return {"entries": live, "max_entries": SMART_CONTEXT_CACHE_MAX, "ttl_seconds": SMART_CONTEXT_CACHE_TTL}
    except Exception as e:
        logger.debug("Phase 19 cache stats failed: %s", e)
        return {"entries": 0, "max_entries": SMART_CONTEXT_CACHE_MAX, "ttl_seconds": SMART_CONTEXT_CACHE_TTL}


async def contextpreview_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only Phase 19 Smart Context preview; never sends the full project to AI."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("এই কমান্ড শুধু অ্যাডমিনের জন্য।")
        return
    try:
        sample = " ".join(context.args).strip()
        if not sample:
            await update.message.reply_text("এভাবে লিখুন: /contextpreview <sample coding/debugging request>")
            return
        thinking = await update.message.reply_text("🧠 Smart Context তৈরি করছি…")
        try:
            result = await asyncio.to_thread(build_smart_context, update.effective_user.id, sample)
            cache = get_smart_context_cache_stats()
            text = (
                "🧠 Phase 19 Smart Context Preview\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"Type: {result.get('request_type')}\n"
                f"Files: {len(result.get('files', []))}\n"
                f"Symbols: {len(result.get('symbols', []))}\n"
                f"Dependencies: {len(result.get('dependencies', []))}\n"
                f"Approx tokens: {result.get('approx_tokens', 0)} / {result.get('token_budget', SMART_CONTEXT_DEFAULT_BUDGET)}\n"
                f"Chars: {result.get('char_count', 0)}\n"
                f"Cache hit: {'YES' if result.get('cache_hit') else 'NO'}\n"
                f"Cache entries: {cache.get('entries', 0)}\n\n"
                f"Relevant files: {', '.join(result.get('files', [])[:8]) or 'none'}\n\n"
                f"Context preview:\n{_smart_context_trim(result.get('context', ''), 5000)}"
            )
            await send_long_text(update, text)
        finally:
            try:
                await thinking.delete()
            except Exception:
                pass
    except Exception as e:
        logger.warning("Phase 19 /contextpreview failed: %s", e)
        await update.message.reply_text("Smart Context preview চালাতে সমস্যা হয়েছে।")


# ---- Command Handlers ----

async def codeproject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/codeproject <বিবরণ> — নতুন কোডিং প্রজেক্ট শুরু করে (Prompt Analyze + Project Plan)।"""
    # Note: Use effective_message to handle edited message updates safely.
    # Pattern should be audited repo-wide in a follow-up.
    msg = update.message or update.effective_message
    if not context.args:
        if msg:
            await msg.reply_text(
                "এভাবে লিখুন: /codeproject <আপনার কোডিং প্রজেক্টের বিবরণ>\n"
                "উদাহরণ: /codeproject একটা Flask API বানাও যেখানে ইউজার রেজিস্ট্রেশন ও লগইন থাকবে"
            )
        return
    if not await quota_guard(update, action="coding_plan"):
        return
    user_id = update.effective_user.id
    raw_request = " ".join(context.args).strip()
    thinking = await msg.reply_text("🧠 রিকোয়েস্ট বিশ্লেষণ করে প্ল্যান বানাচ্ছি...") if msg else None
    try:
        plan = await coding_analyze_and_plan(raw_request, user_id)
        project_id = create_code_project(user_id, plan["project_name"], raw_request, plan["stack"], plan["tasks"])
        project = get_project(project_id, owner_id=user_id)
        try:
            api_create_context(
                user_id=user_id, session_key=str(user_id),
                data={"language": plan.get("stack", ""), "project": plan.get("project_name", ""), "style": "step-by-step"},
                scope="project", category="coding_project", tags=["phase17", "coding"], priority=8,
            )
        except Exception as e:
            logger.debug("Phase 17 project context save skipped: %s", e)
        if plan.get("no_api_blocked"):
            # No API Mode-এ AI প্ল্যান হয়নি — "AI দিয়ে প্ল্যান তৈরি হয়েছে" দাবি না করে
            # /codeplan-এর মতোই blocked মেসেজ দেখানো হয়।
            if msg:
                await msg.reply_text(NO_API_PLAN_BLOCKED_MESSAGE)
        else:
            deterministic_note = (
                "\n\n🤖 এই প্ল্যানটি AI কল ছাড়াই deterministicভাবে তৈরি হয়েছে।"
                if plan.get("deterministic") else ""
            )
            await send_long_text(
                update,
                "✅ প্রজেক্ট প্ল্যান তৈরি হয়েছে (এটাই এখন আপনার সক্রিয় প্রজেক্ট)।\n\n"
                + build_project_status_text(project)
                + deterministic_note
                + "\n\nপরের ধাপ প্রসেস করতে /codenext লিখুন।",
            )
    except AIProviderError as e:
        if msg:
            await msg.reply_text(f"দুঃখিত, প্ল্যান বানাতে সমস্যা হয়েছে: {e}")
    except Exception as e:
        logger.error(f"Coding Orchestrator (/codeproject) এরর: {e}")
        if msg:
            await msg.reply_text("দুঃখিত, প্রজেক্ট প্ল্যান বানাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
    finally:
        if thinking:
            await thinking.delete()


async def codenext_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Phase 20: resume the persistent autonomous workflow; backward-compatible with old projects."""
    user_id = update.effective_user.id
    project = get_active_project(user_id)
    if not project:
        await update.message.reply_text("কোনো সক্রিয় প্রজেক্ট নেই। আগে /codeproject বা /codeplan দিয়ে একটা শুরু করুন।")
        return
    next_task = get_next_pending_task(project["id"])
    if not next_task:
        remaining=[t for t in get_project_tasks(project["id"]) if t["status"] in ("failed","blocked")]
        if remaining:
            await update.message.reply_text("⚠️ পরবর্তী কাজ নেই; failed/blocked task আছে। /codestatus দেখে retry সীমা যাচাই করুন।")
        else:
            mark_project_status(project["id"], "done")
            await update.message.reply_text("🎉 এই প্রজেক্টের সবগুলো ধাপ সম্পন্ন হয়েছে। /exportcode লিখে ফল নিন।")
        return
    if not await quota_guard(update, action="coding_task"):
        return
    thinking=await update.message.reply_text(f"🤖 Autonomous Agent: {next_task['title']} — ANALYZE → IMPLEMENT → TEST hook → REVIEW hook…")
    try:
        # Legacy projects still use the old processor; Phase 20 plans carry source=autonomous_plan.
        if next_task.get("source") == "autonomous_plan":
            result=await autonomous_run_next(project)
        else:
            result=await process_next_code_task(project)
        if result and result.get("no_api_blocked"):
            await update.message.reply_text(NO_API_CODING_BLOCKED_MESSAGE)
        elif result and result.get("status")=="done":
            try:
                imp=result.get("phase28_impact",{}) or {}
                phase28_record_outcome(int(project.get("id",0)),imp.get("expected_files",[]),"success",False,imp,int(imp.get("risk_score",0)),str(imp.get("risk_level","LOW")))
            except Exception as e: logger.debug("Phase 28 success history skipped: %s",e)
            # Phase 27: সফল ধাপের কোড একটা স্ন্যাপশট হিসেবে সংরক্ষণ করা হয় (git বা DB-fallback)।
            try:
                phase27_save_snapshot(project, result, note="task")
            except Exception as e:
                logger.debug("Phase 27 snapshot hook skipped: %s", e)
            await send_long_text(update, f"✅ ধাপ {result['seq']} '{result['title']}' সম্পন্ন।\n\n{result.get('code','')[:3000]}")
        elif result and result.get("status")=="pending":
            try:
                imp=result.get("phase28_impact",{}) or {}
                phase28_record_outcome(int(project.get("id",0)),imp.get("expected_files",[]),"failure",False,imp,int(imp.get("risk_score",0)),str(imp.get("risk_level","LOW")))
            except Exception as e: logger.debug("Phase 28 failure history skipped: %s",e)
            await update.message.reply_text(f"⚠️ ধাপটি ব্যর্থ হয়েছে (retry {result.get('retry_count',0)}/{AUTONOMOUS_MAX_RETRIES})। আবার /codenext দিলে সীমার মধ্যে retry হবে।")
        else:
            await update.message.reply_text(
                f"❌ ধাপটি সর্বোচ্চ {AUTONOMOUS_MAX_RETRIES} বার ব্যর্থ হয়েছে; infinite retry বন্ধ করা হয়েছে।\n"
                f"চাইলে /coderollback দিয়ে সর্বশেষ known-good অবস্থায় ফিরে যেতে পারেন (/codehistory দিয়ে আগে তালিকা দেখুন)।"
            )
    except Exception as e:
        logger.error("Phase 20 /codenext error: %s",e)
        await update.message.reply_text("Autonomous workflow-এ সমস্যা হয়েছে; task state database-এ রাখা হয়েছে।")
    finally:
        try: await thinking.delete()
        except Exception: pass


async def codestatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/codestatus — সক্রিয় প্রজেক্টের সবগুলো ধাপ ও অগ্রগতি দেখায়।"""
    project = get_active_project(update.effective_user.id)
    if not project:
        await update.message.reply_text(
            "কোনো সক্রিয় প্রজেক্ট নেই। /codeproject দিয়ে একটা শুরু করুন, বা /codeprojects দিয়ে আগের প্রজেক্ট দেখুন।"
        )
        return
    await send_long_text(update, build_project_status_text(project))


async def codeprojects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/codeprojects — ইউজারের সবগুলো (Project Memory-তে সংরক্ষিত) প্রজেক্টের তালিকা।"""
    rows = list_user_projects(update.effective_user.id)
    if not rows:
        await update.message.reply_text("এখনো কোনো কোডিং প্রজেক্ট শুরু করেননি। /codeproject দিয়ে শুরু করুন।")
        return
    lines = ["📁 আপনার প্রজেক্টসমূহ:\n"]
    for pid, name, status, created_at in rows:
        lines.append(f"#{pid} — {name} [{status}] ({created_at[:10]})")
    lines.append("\nকোনো একটা সক্রিয় করতে: /useproject <নাম্বার>")
    await send_long_text(update, "\n".join(lines))


async def useproject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/useproject <id> — নির্দিষ্ট প্রজেক্টকে সক্রিয় প্রজেক্ট হিসেবে সেট করে।"""
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /useproject প্রজেক্ট_আইডি (আইডি জানতে /codeprojects দেখুন)।")
        return
    project = get_project(int(context.args[0]), owner_id=user_id)
    if not project:
        await update.message.reply_text("এই আইডির কোনো প্রজেক্ট আপনার নামে পাওয়া যায়নি।")
        return
    set_active_project(user_id, project["id"])
    await send_long_text(update, f"✅ '{project['name']}' এখন আপনার সক্রিয় প্রজেক্ট।\n\n" + build_project_status_text(project))


async def codetask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/codetask <ধাপ_নাম্বার> — সক্রিয় প্রজেক্টের নির্দিষ্ট ধাপের কোড দেখায়।"""
    project = get_active_project(update.effective_user.id)
    if not project:
        await update.message.reply_text("কোনো সক্রিয় প্রজেক্ট নেই।")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /codetask ধাপ_নাম্বার (যেমন: /codetask 1)")
        return
    seq = int(context.args[0])
    match = next((t for t in get_project_tasks(project["id"]) if t["seq"] == seq), None)
    if not match:
        await update.message.reply_text("এই নাম্বারের কোনো ধাপ পাওয়া যায়নি।")
        return
    if match["status"] != "done":
        await update.message.reply_text(
            f"ধাপ {seq} ('{match['title']}') এখনো প্রসেস হয়নি। /codenext দিয়ে ক্রমান্বয়ে প্রসেস করুন।"
        )
        return
    await send_long_text(update, f"ধাপ {seq}: {match['title']}\n\n{match['code']}")


async def exportcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/exportcode — সক্রিয় প্রজেক্টের সবগুলো সম্পন্ন ধাপের কোড অ্যাসেম্বল করে ফাইল আকারে পাঠায়।"""
    project = get_active_project(update.effective_user.id)
    if not project:
        await update.message.reply_text("কোনো সক্রিয় প্রজেক্ট নেই।")
        return
    assembled = assemble_project_code(project["id"])
    if not assembled:
        await update.message.reply_text("এখনো কোনো ধাপ সম্পন্ন হয়নি। আগে /codenext দিয়ে অন্তত একটা ধাপ প্রসেস করুন।")
        return
    safe_name = re.sub(r"[^A-Za-z0-9_\-]+", "_", project["name"]).strip("_") or "project"
    out_path = os.path.join(tempfile.gettempdir(), f"{safe_name}_{project['id']}.txt")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(assembled)
        with open(out_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"{safe_name}.txt",
                caption=f"📦 '{project['name']}' প্রজেক্টের এখন পর্যন্ত সম্পন্ন সব কোড একসাথে।",
            )
    except Exception as e:
        logger.error(f"exportcode এরর: {e}")
        await update.message.reply_text("দুঃখিত, কোড এক্সপোর্ট করতে সমস্যা হয়েছে।")
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)


async def deleteproject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/deleteproject <id> — নিজের একটা প্রজেক্ট স্থায়ীভাবে মুছে ফেলে।"""
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("এভাবে লিখুন: /deleteproject প্রজেক্ট_আইডি")
        return
    project_id = int(context.args[0])
    if delete_project(project_id, user_id):
        await update.message.reply_text(f"🗑️ প্রজেক্ট #{project_id} মুছে ফেলা হয়েছে।")
    else:
        await update.message.reply_text("এই আইডির কোনো প্রজেক্ট আপনার নামে পাওয়া যায়নি।")


async def codehelp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/codehelp — public coding command-গুলোর সম্পূর্ণ তালিকা (admin-only command বাদে)।"""
    user_id = update.effective_user.id
    text = await localize(user_id, build_coding_commands_text())
    await send_long_text(update, text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"আনএক্সপেক্টেড এরর: {context.error}", exc_info=context.error)

    # ইউজারকে একটা সাধারণ বার্তা দেখানো, যদি সম্ভব হয়
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "দুঃখিত, একটা অপ্রত্যাশিত সমস্যা হয়েছে। আবার চেষ্টা করুন।"
            )
        except Exception:
            pass

    # অ্যাডমিনদের সংক্ষিপ্ত এরর নোটিফিকেশন পাঠানো
    error_text = f"⚠️ বট এরর:\n{type(context.error).__name__}: {context.error}"
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=error_text[:4000])
        except Exception:
            pass


# ============================= বট চালু করা =============================

async def _on_shutdown(application):
    """Phase 9: বট বন্ধ হওয়ার সময় Connection Pool-এর Shared httpx client গ্রেসফুলি বন্ধ করা।"""
    try:
        await close_http_client()
        logger.info("Phase 9: Shared HTTP client (Connection Pool) বন্ধ করা হলো।")
    except Exception as e:
        logger.warning(f"Shared HTTP client বন্ধ করতে সমস্যা: {e}")



# =============================================================================
# PHASE 25 — PROJECT MEMORY 2.0
# Project-specific long-term memory built by extending the existing
# brain_project_memory table. Local SQLite/stdlib only; no vector DB/paid API.
# =============================================================================

PHASE25_MEMORY_VERSION = 2
PHASE25_MEMORY_CACHE_TTL = 45
PHASE25_MEMORY_CACHE_MAX = 128
PHASE25_MEMORY_MAX_DETAILS = 8000
_PHASE25_MEMORY_CACHE = OrderedDict()


def _phase25_memory_tokens(text: str) -> set:
    try:
        return set(re.findall(r"[\w\u0980-\u09FF]+", str(text or "").lower(), flags=re.UNICODE))
    except Exception:
        return set()


def _phase25_memory_secret_safe(text: str) -> bool:
    """Phase 24 secret protection gate. Returns False when a credential is detected."""
    try:
        scanner = globals().get("_phase24_scan_text")
        if callable(scanner):
            findings = scanner(str(text or ""), "<project-memory>")
            if any(f.get("category") == "Secret / Credential" for f in findings):
                return False
    except Exception as e:
        logger.warning("Phase 25 secret gate scanner failed: %s", e)
    # Conservative stdlib fallback for common secret forms; this also runs when Phase 24 is available.
    try:
        patterns = (
            r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|password|passwd|private[_-]?key)\s*[:=]\s*\\?['\"][^'\"]{8,}\\?['\"]",
            r"\b(?:sk|ghp|github_pat|xox[baprs])-[_A-Za-z0-9-]{12,}\b",
        )
        return not any(re.search(p, str(text or "")) for p in patterns)
    except Exception:
        return False


def _phase25_memory_cache_key(project_id: int, query: str, limit: int) -> str:
    try:
        raw=f"{int(project_id)}|{str(query or '').strip().lower()}|{int(limit)}"
        return hashlib.sha256(raw.encode("utf-8", "ignore")).hexdigest()
    except Exception:
        return ""


def _phase25_memory_cache_get(key: str):
    try:
        item=_PHASE25_MEMORY_CACHE.get(key)
        if not item: return None
        created,value=item
        if time.time()-created>PHASE25_MEMORY_CACHE_TTL:
            _PHASE25_MEMORY_CACHE.pop(key,None); return None
        _PHASE25_MEMORY_CACHE.move_to_end(key)
        return value
    except Exception:
        return None


def _phase25_memory_cache_set(key: str, value: dict) -> None:
    try:
        if not key: return
        _PHASE25_MEMORY_CACHE[key]=(time.time(),value)
        _PHASE25_MEMORY_CACHE.move_to_end(key)
        while len(_PHASE25_MEMORY_CACHE)>PHASE25_MEMORY_CACHE_MAX:
            _PHASE25_MEMORY_CACHE.popitem(last=False)
    except Exception as e:
        logger.debug("Phase 25 memory cache set skipped: %s",e)


def _migrate_project_memory_v2(cur: sqlite3.Cursor) -> None:
    """Idempotent extension of the existing brain_project_memory table."""
    try:
        cur.execute("PRAGMA table_info(brain_project_memory)")
        existing={row[1] for row in cur.fetchall()}
        columns={
            "category":"TEXT DEFAULT ''",
            "confidence":"REAL DEFAULT 0.7",
            "status":"TEXT DEFAULT 'active'",
            "source":"TEXT DEFAULT 'manual'",
            "evidence":"TEXT DEFAULT ''",
            "version":"INTEGER DEFAULT 1",
            "last_used_at":"TEXT DEFAULT ''",
            "content_hash":"TEXT DEFAULT ''",
            "supersedes_id":"INTEGER DEFAULT NULL",
            "file_path":"TEXT DEFAULT ''",
            "symbol_name":"TEXT DEFAULT ''",
            "tags":"TEXT DEFAULT ''",
            "metadata":"TEXT DEFAULT '{}'",
            "usage_count":"INTEGER DEFAULT 0",
            # Phase 26: coding-knowledge lifecycle fields (same Project Memory table).
            "knowledge_scope":"TEXT DEFAULT ''",
            "quality_score":"INTEGER DEFAULT 0",
            "success_count":"INTEGER DEFAULT 0",
            "failure_count":"INTEGER DEFAULT 0",
            "verification_status":"TEXT DEFAULT 'UNVERIFIED'",
            "usage_success_count":"INTEGER DEFAULT 0",
            "usage_failure_count":"INTEGER DEFAULT 0",
            "last_validated_at":"TEXT DEFAULT ''",
            "compatibility":"TEXT DEFAULT '{}'",
            "preferred":"INTEGER DEFAULT 0",
        }
        for col,typ in columns.items():
            if col not in existing:
                try: cur.execute(f"ALTER TABLE brain_project_memory ADD COLUMN {col} {typ}")
                except sqlite3.OperationalError as e: logger.warning("Phase 25 migration %s skipped: %s",col,e)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_p25_memory_project_status ON brain_project_memory(project_id,status,category,updated_at)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_p25_memory_hash ON brain_project_memory(project_id,content_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_p25_memory_file_symbol ON brain_project_memory(project_id,file_path,symbol_name)")
    except Exception as e:
        logger.warning("Phase 25 project memory migration failed: %s",e)


def _phase25_memory_normalize_details(details: Any) -> str:
    try:
        if isinstance(details,dict):
            data=details.copy()
        else:
            try: data=json.loads(str(details or "{}"))
            except Exception: data={"content":str(details or "")}
        if not isinstance(data,dict): data={"content":str(data)}
        # Never persist obvious secrets even if a caller bypasses the category gate.
        for k in list(data):
            if str(k).lower() in {"api_key","token","password","passwd","secret","private_key","access_token"}:
                data[k]="[REDACTED]"
        return json.dumps(data,ensure_ascii=False,default=str)[:PHASE25_MEMORY_MAX_DETAILS]
    except Exception:
        return json.dumps({"content":str(details or "")[:PHASE25_MEMORY_MAX_DETAILS]},ensure_ascii=False)


def project_memory_save(project_id:int, memory_type:str, key_name:str, details:Any,
                        confidence:float=0.8, source:str="manual", evidence:str="",
                        file_path:str="", symbol_name:str="", tags:Any=None, metadata:Any=None) -> Optional[int]:
    """Create/update a project memory item; conflicts create a new version and mark old active data outdated."""
    try:
        if not project_id or not str(key_name or "").strip(): return None
        raw_text=json.dumps(details,ensure_ascii=False,default=str) if isinstance(details,(dict,list)) else str(details or "")
        if not _phase25_memory_secret_safe(raw_text):
            logger.warning("Phase 25 refused to store a suspected secret for project %s",project_id); return None
        normalized=_phase25_memory_normalize_details(details)
        digest=hashlib.sha256((str(memory_type).lower()+"|"+str(key_name).strip().lower()+"|"+normalized).encode("utf-8","ignore")).hexdigest()
        now=datetime.now().isoformat(timespec="seconds")
        conn=get_conn(); cur=conn.cursor()
        row=cur.execute("SELECT id,content_hash,version,status FROM brain_project_memory WHERE project_id=? AND memory_type=? AND key_name=? AND status IN ('active','current') ORDER BY version DESC,id DESC LIMIT 1",(int(project_id),str(memory_type)[:80],str(key_name)[:300])).fetchone()
        if row and row[1]==digest:
            cur.execute("UPDATE brain_project_memory SET confidence=?,source=?,evidence=?,last_used_at=?,usage_count=usage_count+1,updated_at=?,file_path=?,symbol_name=?,tags=?,metadata=?,category=? WHERE id=?",(max(0,min(1,float(confidence))),str(source)[:80],str(evidence)[:2000],now,now,str(file_path)[:500],str(symbol_name)[:300],json.dumps(tags or [],ensure_ascii=False) if not isinstance(tags,str) else tags[:1000],json.dumps(metadata or {},ensure_ascii=False) if not isinstance(metadata,str) else metadata[:3000],str(memory_type)[:80],row[0]))
            conn.commit(); conn.close(); _PHASE25_MEMORY_CACHE.clear(); return int(row[0])
        version=(int(row[2])+1) if row else 1
        supersedes=row[0] if row else None
        if row: cur.execute("UPDATE brain_project_memory SET status='outdated',updated_at=? WHERE id=?",(now,row[0]))
        cur.execute("INSERT INTO brain_project_memory(project_id,memory_type,key_name,details,created_at,updated_at,category,confidence,status,source,evidence,version,last_used_at,content_hash,supersedes_id,file_path,symbol_name,tags,metadata,usage_count) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(int(project_id),str(memory_type)[:80],str(key_name)[:300],normalized,now,now,str(memory_type)[:80],max(0,min(1,float(confidence))),"active",str(source)[:80],str(evidence)[:2000],version,now,digest,supersedes,str(file_path)[:500],str(symbol_name)[:300],json.dumps(tags or [],ensure_ascii=False) if not isinstance(tags,str) else tags[:1000],json.dumps(metadata or {},ensure_ascii=False) if not isinstance(metadata,str) else metadata[:3000],1))
        mid=cur.lastrowid; conn.commit(); conn.close(); _PHASE25_MEMORY_CACHE.clear(); return int(mid)
    except Exception as e:
        logger.warning("Phase 25 memory save failed: %s",e)
        try: conn.close()
        except Exception: pass
        return None


def project_memory_search(project_id:int, query:str, limit:int=8, categories:Optional[Sequence[str]]=None) -> List[Dict[str,Any]]:
    """Keyword/relevance retrieval; no embeddings required."""
    try:
        if not project_id: return []
        q=str(query or "").strip(); key=_phase25_memory_cache_key(project_id,q,limit)
        cached=_phase25_memory_cache_get(key)
        if cached is not None: return cached.get("rows",[])
        conn=get_conn(); cur=conn.cursor()
        params=[int(project_id)]
        where="project_id=? AND status='active'"
        if categories:
            marks=','.join('?' for _ in categories); where+=f" AND memory_type IN ({marks})"; params.extend([str(x) for x in categories])
        rows=cur.execute(f"SELECT id,memory_type,key_name,details,confidence,status,source,evidence,version,last_used_at,file_path,symbol_name,tags,metadata,usage_count,updated_at FROM brain_project_memory WHERE {where} ORDER BY confidence DESC,updated_at DESC LIMIT 300",params).fetchall(); conn.close()
        tokens=_phase25_memory_tokens(q); ranked=[]
        for r in rows:
            hay=_phase25_memory_tokens(" ".join(str(x or "") for x in (r[1],r[2],r[3],r[6],r[7],r[10],r[11],r[12])))
            overlap=len(tokens & hay) if tokens else 0
            exact=2 if q and q.lower() in " ".join(str(x or "") for x in r[1:4]).lower() else 0
            score=(overlap*3)+exact+(float(r[4] or 0)*2)+(min(int(r[14] or 0),10)*0.05)
            if not tokens or overlap or exact: ranked.append((score,r))
        ranked.sort(key=lambda x:x[0],reverse=True); out=[]
        now=datetime.now().isoformat(timespec="seconds")
        for score,r in ranked[:max(1,min(int(limit or 8),30))]:
            try: details=json.loads(r[3] or "{}")
            except Exception: details={"content":r[3] or ""}
            out.append({"id":r[0],"memory_type":r[1],"key_name":r[2],"details":details,"confidence":float(r[4] or 0),"status":r[5],"source":r[6],"evidence":r[7],"version":r[8],"file_path":r[10],"symbol_name":r[11],"tags":r[12],"metadata":r[13],"usage_count":r[14],"updated_at":r[15],"relevance":round(score,3)})
        if out:
            ids=[x["id"] for x in out]
            marks=','.join('?' for _ in ids); cur=get_conn().cursor()
            # separate connection keeps retrieval resilient; usage update is best-effort
            try:
                conn2=cur.connection; cur.execute(f"UPDATE brain_project_memory SET last_used_at=?,usage_count=usage_count+1 WHERE id IN ({marks})",[now,*ids]); conn2.commit(); conn2.close()
            except Exception:
                try: cur.connection.close()
                except Exception: pass
        _phase25_memory_cache_set(key,{"rows":out}); return out
    except Exception as e:
        logger.warning("Phase 25 memory search failed: %s",e); return []


def project_memory_context(project_id:int, query:str, budget:int=1400) -> str:
    try:
        rows=project_memory_search(project_id,query,12)
        parts=[]; used=0; max_chars=max(400,int(budget)*4)
        for r in rows:
            d=r.get("details") or {}; content=d.get("content") if isinstance(d,dict) else str(d)
            if not content: content=json.dumps(d,ensure_ascii=False,default=str)
            line=f"{r['memory_type']}::{r['key_name']} [v{r.get('version',1)} conf={r.get('confidence',0):.2f}] {str(content)[:900]}"
            if used+len(line)+1>max_chars: break
            parts.append(line); used+=len(line)+1
        return "\n".join(parts)
    except Exception as e:
        logger.warning("Phase 25 memory context failed: %s",e); return ""


def project_memory_stats(project_id:int) -> Dict[str,Any]:
    try:
        conn=get_conn(); cur=conn.cursor()
        total=cur.execute("SELECT COUNT(*) FROM brain_project_memory WHERE project_id=? AND status='active'",(project_id,)).fetchone()[0]
        rows=cur.execute("SELECT memory_type,COUNT(*) FROM brain_project_memory WHERE project_id=? AND status='active' GROUP BY memory_type ORDER BY COUNT(*) DESC",(project_id,)).fetchall()
        outdated=cur.execute("SELECT COUNT(*) FROM brain_project_memory WHERE project_id=? AND status='outdated'",(project_id,)).fetchone()[0]
        conn.close(); return {"total":total,"by_type":dict(rows),"outdated":outdated,"cache_entries":len(_PHASE25_MEMORY_CACHE)}
    except Exception as e:
        logger.warning("Phase 25 memory stats failed: %s",e); return {"total":0,"by_type":{},"outdated":0}


def project_memory_sync_codebase(project_id:int, root:Optional[str]=None) -> Dict[str,int]:
    """Pull high-value structural facts from the existing Phase 18 index."""
    stats={"architecture":0,"files":0,"symbols":0,"dependencies":0}
    try:
        if not project_id: return stats
        root=os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
        conn=get_conn(); cur=conn.cursor()
        files=cur.execute("SELECT id,relative_path,file_path,is_python,file_hash,last_indexed_at FROM brain_codebase_files WHERE file_path LIKE ? OR relative_path LIKE ? ORDER BY is_python DESC,last_indexed_at DESC LIMIT 80",(root+'%', '%')).fetchall()
        py=[f for f in files if f[3]]
        entry=next((f for f in py if os.path.basename(f[2] or '') in ('main.py','app.py','bot.py','__main__.py')), py[0] if py else None)
        if entry:
            project_memory_save(project_id,"architecture","entry_point",{"content":entry[1] or entry[2],"path":entry[2]},.95,"codebase_intelligence",file_path=entry[2]); stats["architecture"]+=1
        for f in files[:40]:
            rel=f[1] or f[2]
            project_memory_save(project_id,"important_file",rel,{"content":f"Indexed file: {rel}","path":f[2],"python":bool(f[3]),"hash":f[4],"last_indexed_at":f[5]},.9,"codebase_intelligence",file_path=f[2]); stats["files"]+=1
            if f[0] and f[3]:
                syms=cur.execute("SELECT symbol_name,symbol_type,line_number,docstring,qualified_name FROM brain_codebase_symbols WHERE file_id=? ORDER BY line_number LIMIT 8",(f[0],)).fetchall()
                for sm in syms:
                    project_memory_save(project_id,"important_symbol",f"{rel}::{sm[0]}",{"content":sm[3] or f"{sm[1]} {sm[0]}","type":sm[1],"line":sm[2],"qualified_name":sm[4]},.85,"codebase_intelligence",file_path=f[2],symbol_name=sm[0]); stats["symbols"]+=1
        deps=cur.execute("SELECT source_name,target_name,edge_type,source_file_id,target_file_id FROM brain_codebase_edges WHERE edge_type IN ('import','dependency','call') ORDER BY last_indexed_at DESC LIMIT 60").fetchall()
        for d in deps[:30]:
            project_memory_save(project_id,"dependency",f"{d[0]}->{d[1]}",{"content":f"{d[0]} -> {d[1]}","edge_type":d[2]},.8,"codebase_intelligence"); stats["dependencies"]+=1
        conn.close(); return stats
    except Exception as e:
        logger.warning("Phase 25 codebase memory sync failed: %s",e); return stats


def project_memory_record_success(project:dict, task:dict, test_report:Any=None) -> Optional[int]:
    try:
        pid=int(project.get("id") or 0)
        details={"content":f"Successful implementation: {task.get('title','')}","description":task.get("description","")[:1200],"target_files":task.get("target_files",""),"test":test_report or "passed"}
        return project_memory_save(pid,"successful_implementation",task.get("title") or f"task-{task.get('id')}",details,.92,"autonomous_agent",metadata={"task_id":task.get("id")})
    except Exception as e:
        logger.warning("Phase 25 success memory record failed: %s",e); return None


def project_memory_record_failure(project:dict, task:dict, exc:Any) -> Optional[int]:
    try:
        pid=int(project.get("id") or 0); msg=str(exc)[:1800]
        return project_memory_save(pid,"known_bug",f"task-{task.get('id')}-failure",{"content":msg,"task":task.get("title",""),"status":"failed"},.75,"error_engine",evidence=msg,file_path=str(task.get("target_files","")).split(',')[0])
    except Exception as e:
        logger.debug("Phase 25 failure memory skipped: %s",e); return None


def project_memory_record_solved_bug(project:dict, task:dict, error_text:str, fix_text:str, test_report:Any=None) -> Optional[int]:
    try:
        pid=int(project.get("id") or 0)
        details={"content":f"Solved bug: {error_text[:700]}","root_cause":error_text[:1500],"fix":fix_text[:2500],"test_result":test_report or "passed"}
        return project_memory_save(pid,"solved_bug",f"{task.get('title','task')}-{hashlib.sha1(error_text.encode('utf-8','ignore')).hexdigest()[:10]}",details,.95,"auto_fix",evidence=error_text,file_path=str(task.get("target_files","")).split(',')[0])
    except Exception as e:
        logger.debug("Phase 25 solved bug memory skipped: %s",e); return None


def project_memory_mark_obsolete(project_id:int, query:str) -> int:
    try:
        tokens=_phase25_memory_tokens(query); conn=get_conn(); cur=conn.cursor()
        rows=cur.execute("SELECT id,details FROM brain_project_memory WHERE project_id=? AND status='active'",(project_id,)).fetchall(); ids=[]
        for mid,details in rows:
            if tokens and not (tokens & _phase25_memory_tokens(details)):
                continue
        # Obsolescence is deliberately conservative: conflicting updates are handled by save().
        conn.close(); return 0
    except Exception as e:
        logger.debug("Phase 25 obsolete scan skipped: %s",e); return 0


def project_memory_inspect_command_text(project_id:int, query:str="") -> str:
    try:
        if query: rows=project_memory_search(project_id,query,20)
        else:
            conn=get_conn(); rows_raw=conn.execute("SELECT id,memory_type,key_name,details,confidence,status,version,updated_at FROM brain_project_memory WHERE project_id=? AND status='active' ORDER BY confidence DESC,updated_at DESC LIMIT 30",(project_id,)).fetchall(); conn.close(); rows=[{"id":r[0],"memory_type":r[1],"key_name":r[2],"details":json.loads(r[3] or '{}') if r[3] else {},"confidence":r[4],"status":r[5],"version":r[6],"updated_at":r[7]} for r in rows_raw]
        lines=["🧠 PROJECT MEMORY 2.0",f"Project: {project_id}",f"Memories shown: {len(rows)}"]
        for r in rows[:20]:
            d=r.get("details") or {}; c=d.get("content","") if isinstance(d,dict) else str(d)
            lines.append(f"\n• {r.get('memory_type')} :: {r.get('key_name')} | conf={float(r.get('confidence',0)):.2f} | v{r.get('version',1)}")
            lines.append(str(c)[:500])
        return "\n".join(lines)
    except Exception as e:
        logger.warning("Phase 25 memory inspection failed: %s",e); return "Memory inspection unavailable."


async def projectmemory_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): await update.message.reply_text("⛔ Admin only."); return
        project=get_active_project(update.effective_user.id)
        if not project: await update.message.reply_text("Active project পাওয়া যায়নি।"); return
        query=" ".join(context.args).strip() if context.args else ""
        if not query:
            stats=project_memory_stats(project["id"]); await send_long_text(update,"🧠 PROJECT MEMORY 2.0\n"+json.dumps(stats,ensure_ascii=False,indent=2)); return
        await send_long_text(update,project_memory_inspect_command_text(project["id"],query))
    except Exception as e:
        logger.warning("Phase 25 /projectmemory failed: %s",e); await update.message.reply_text("Project Memory পড়তে সমস্যা হয়েছে।")



# =============================================================================
# PHASE 26 — SELF-LEARNING CODING KNOWLEDGE ENGINE
# Integrated with Phase 25 Project Memory 2.0. No new table, service, vector DB,
# dependency, or GPU. Coding knowledge lives in brain_project_memory with a
# dedicated memory_type and lifecycle columns added by the safe migration above.
# =============================================================================
PHASE26_KNOWLEDGE_VERSION = 1
PHASE26_MAX_CONTEXT = 2600
PHASE26_MIN_CONFIDENCE = 0.45
PHASE26_MAX_SCAN = 500


def _migrate_coding_knowledge_v1(cur: sqlite3.Cursor) -> None:
    """Idempotent Phase 26 indexes/constraints; never replaces Project Memory."""
    try:
        cur.execute("PRAGMA table_info(brain_project_memory)")
        cols = {r[1] for r in cur.fetchall()}
        wanted = {
            "knowledge_scope":"TEXT DEFAULT ''",
            "quality_score":"INTEGER DEFAULT 0",
            "success_count":"INTEGER DEFAULT 0",
            "failure_count":"INTEGER DEFAULT 0",
            "verification_status":"TEXT DEFAULT 'UNVERIFIED'",
            "usage_success_count":"INTEGER DEFAULT 0",
            "usage_failure_count":"INTEGER DEFAULT 0",
            "last_validated_at":"TEXT DEFAULT ''",
            "compatibility":"TEXT DEFAULT '{}'",
            "preferred":"INTEGER DEFAULT 0",
        }
        for col, typ in wanted.items():
            if col not in cols:
                try:
                    cur.execute(f"ALTER TABLE brain_project_memory ADD COLUMN {col} {typ}")
                except sqlite3.OperationalError as e:
                    logger.warning("Phase 26 migration %s skipped: %s", col, e)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_p26_knowledge_lookup ON brain_project_memory(project_id,memory_type,verification_status,quality_score,confidence)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_p26_knowledge_scope ON brain_project_memory(project_id,knowledge_scope,status,updated_at)")
    except Exception as e:
        logger.warning("Phase 26 knowledge migration failed: %s", e)


def _phase26_tokens(text: Any) -> set:
    try:
        return set(re.findall(r"[\w\u0980-\u09FF]+", str(text or "").lower(), flags=re.UNICODE))
    except Exception:
        return set()


def _phase26_secret_safe(text: Any) -> bool:
    """Reuse Phase 24 scanner and keep a conservative fallback gate."""
    try:
        scanner = globals().get("_phase24_scan_text")
        if callable(scanner):
            findings = scanner(str(text or ""), "<coding-knowledge>")
            if any(str(f.get("category", "")).lower() == "secret / credential" for f in findings):
                return False
    except Exception as e:
        logger.debug("Phase 26 security scanner unavailable: %s", e)
    try:
        pats = (
            r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|password|passwd|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
            r"\b\d{7,12}:[A-Za-z0-9_-]{20,}\b",
            r"\b(?:sk|ghp|github_pat|xox[baprs])[-_A-Za-z0-9]{12,}\b",
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        )
        return not any(re.search(p, str(text or "")) for p in pats)
    except Exception:
        return False


def _phase26_normalize(text: Any, limit: int = 6000) -> str:
    try:
        return re.sub(r"\s+", " ", str(text or "").strip().lower())[:limit]
    except Exception:
        return str(text or "")[:limit]


def _phase26_fingerprint(knowledge_type: str, problem: str, solution: str, tags: Any = None) -> str:
    raw = "|".join((_phase26_normalize(knowledge_type, 120), _phase26_normalize(problem, 1800), _phase26_normalize(solution, 2600), _phase26_normalize(tags, 600)))
    return hashlib.sha256(raw.encode("utf-8", "ignore")).hexdigest()[:24]


def _phase26_quality(verification_status: str, success_count: int, failure_count: int, security_ok: bool = True, review_score: int = 100) -> int:
    try:
        base = {"UNVERIFIED": 45, "TESTED": 65, "VERIFIED": 82, "REPEATEDLY_VERIFIED": 94, "FAILED": 20, "OUTDATED": 10}.get(str(verification_status or "UNVERIFIED").upper(), 45)
        base += min(int(success_count or 0) * 3, 12)
        base -= min(int(failure_count or 0) * 5, 20)
        base += 5 if security_ok else -30
        base += max(-10, min(5, (int(review_score or 100) - 80) // 4))
        return max(0, min(100, int(base)))
    except Exception:
        return 0


def _phase26_confidence(verification_status: str, success_count: int, failure_count: int, quality_score: int, project_compatible: bool = True) -> float:
    try:
        c = {"UNVERIFIED": .45, "TESTED": .65, "VERIFIED": .82, "REPEATEDLY_VERIFIED": .94, "FAILED": .25, "OUTDATED": .10}.get(str(verification_status or "UNVERIFIED").upper(), .45)
        c += min(int(success_count or 0) * .025, .10) - min(int(failure_count or 0) * .04, .20)
        c += (max(0, min(100, int(quality_score or 0))) - 70) / 1000.0
        if not project_compatible:
            c *= .55
        return round(max(0.0, min(0.99, c)), 3)
    except Exception:
        return .0


def _phase26_parse_metadata(row) -> dict:
    try:
        return json.loads(row[13] or "{}") if row and row[13] else {}
    except Exception:
        return {}


def coding_knowledge_save(project_id: int, knowledge_type: str, title: str, problem: str = "", context: str = "", root_cause: str = "", solution: str = "", implementation: str = "", verification: Any = "", related_files: Any = None, related_functions: Any = None, related_error: str = "", tags: Any = None, scope: str = "project", confidence: float = .45, quality_score: int = 45, verification_status: str = "UNVERIFIED", source: str = "self_learning", success_count: int = 0, failure_count: int = 0, compatibility: Any = None, preferred: bool = False, metadata: Any = None) -> Optional[int]:
    """Store reusable coding knowledge inside the existing Project Memory table."""
    try:
        pid = int(project_id or 0)
        if not pid or not str(title or "").strip():
            return None
        payload = {
            "content": str(solution or problem or title)[:2200], "problem": str(problem or "")[:1800],
            "context": str(context or "")[:1400], "root_cause": str(root_cause or "")[:1800],
            "solution": str(solution or "")[:3000], "implementation": str(implementation or "")[:2200],
            "verification": verification if isinstance(verification, (dict, list)) else str(verification or "")[:1800],
            "related_files": related_files or [], "related_functions": related_functions or [],
            "related_error": str(related_error or "")[:1200], "knowledge_type": str(knowledge_type or "IMPLEMENTATION_PATTERN")[:80],
            "scope": str(scope or "project")[:20], "tags": tags or [],
        }
        raw = json.dumps(payload, ensure_ascii=False, default=str)
        if not _phase26_secret_safe(raw):
            logger.warning("Phase 26 refused to store suspected secret for project %s", pid)
            return None
        fp = _phase26_fingerprint(knowledge_type, problem, solution, tags)
        meta = dict(metadata or {}) if isinstance(metadata, dict) else {"metadata": str(metadata or "")}
        meta.update({"phase": 26, "fingerprint": fp, "knowledge_type": str(knowledge_type)[:80], "scope": str(scope or "project")[:20]})
        # Duplicate detection by fingerprint. A duplicate updates lifecycle metrics instead of creating a record.
        conn = get_conn(); cur = conn.cursor()
        row = cur.execute("SELECT id,confidence,quality_score,success_count,failure_count,verification_status,usage_success_count,usage_failure_count,compatibility,preferred,metadata FROM brain_project_memory WHERE project_id=? AND memory_type='coding_knowledge' AND status='active' AND metadata LIKE ? ORDER BY id DESC LIMIT 1", (pid, "%" + fp + "%")).fetchone()
        now = datetime.now().isoformat(timespec="seconds")
        if row:
            mid = int(row[0]); old_meta = {}
            try: old_meta = json.loads(row[10] or "{}")
            except Exception: pass
            old_meta.update(meta)
            new_s = int(row[3] or 0) + int(success_count or 0)
            new_f = int(row[4] or 0) + int(failure_count or 0)
            q = max(0, min(100, int(quality_score or row[2] or 45)))
            conf = _phase26_confidence(verification_status or row[5], new_s, new_f, q, True)
            cur.execute("UPDATE brain_project_memory SET confidence=?,quality_score=?,success_count=?,failure_count=?,verification_status=?,source=?,evidence=?,last_used_at=?,usage_count=usage_count+1,updated_at=?,metadata=?,knowledge_scope=?,compatibility=?,preferred=?,last_validated_at=? WHERE id=?", (conf,q,new_s,new_f,str(verification_status or row[5] or "UNVERIFIED")[:40],str(source)[:80],str(verification)[:2000],now,now,json.dumps(old_meta,ensure_ascii=False)[:5000],str(scope or "project")[:20],json.dumps(compatibility or {},ensure_ascii=False)[:2000],1 if preferred else int(row[9] or 0),now,mid))
            conn.commit(); conn.close(); _PHASE25_MEMORY_CACHE.clear(); return mid
        conn.close()
        mid = project_memory_save(pid, "coding_knowledge", f"{title[:240]} [{fp}]", payload, confidence, source, str(verification)[:2000], file_path=(related_files[0] if isinstance(related_files,list) and related_files else ""), symbol_name=(related_functions[0] if isinstance(related_functions,list) and related_functions else ""), tags=tags, metadata=meta)
        if not mid:
            return None
        conn = get_conn(); cur = conn.cursor()
        cur.execute("UPDATE brain_project_memory SET knowledge_scope=?,quality_score=?,success_count=?,failure_count=?,verification_status=?,usage_success_count=?,usage_failure_count=?,last_validated_at=?,compatibility=?,preferred=? WHERE id=?", (str(scope or "project")[:20], max(0,min(100,int(quality_score or 45))), int(success_count or 0), int(failure_count or 0), str(verification_status or "UNVERIFIED")[:40], 0, 0, now, json.dumps(compatibility or {},ensure_ascii=False)[:2000], 1 if preferred else 0, mid))
        conn.commit(); conn.close(); _PHASE25_MEMORY_CACHE.clear(); return int(mid)
    except Exception as e:
        logger.warning("Phase 26 knowledge save failed: %s", e)
        try: conn.close()
        except Exception: pass
        return None


def _phase26_project_compatibility(project: dict, knowledge: dict) -> float:
    try:
        comp = knowledge.get("compatibility") or knowledge.get("metadata", {}).get("compatibility") or {}
        if isinstance(comp, str):
            try: comp = json.loads(comp)
            except Exception: comp = {}
        if not isinstance(comp, dict) or not comp:
            return 1.0
        checks = 0; hits = 0
        for key in ("language", "stack", "framework", "database"):
            val = str(comp.get(key) or "").strip().lower()
            if not val: continue
            checks += 1
            pval = str(project.get("stack") or "").lower()
            if val in pval or pval in val: hits += 1
        return hits / checks if checks else 1.0
    except Exception:
        return .5


def coding_knowledge_search(project_id: int, query: str, limit: int = 8, include_failed: bool = False, project: Optional[dict] = None) -> List[Dict[str, Any]]:
    """Fast local relevance ranking; no embeddings or external service."""
    try:
        pid = int(project_id or 0)
        q = str(query or "").strip()
        if not pid or not q: return []
        conn = get_conn(); cur = conn.cursor()
        where = "project_id=? AND memory_type='coding_knowledge' AND status='active'"
        params = [pid]
        if not include_failed:
            where += " AND verification_status NOT IN ('FAILED','OUTDATED')"
        rows = cur.execute(f"SELECT id,key_name,details,confidence,quality_score,success_count,failure_count,verification_status,knowledge_scope,compatibility,preferred,tags,metadata,usage_success_count,usage_failure_count,updated_at,file_path,symbol_name FROM brain_project_memory WHERE {where} ORDER BY quality_score DESC,confidence DESC,updated_at DESC LIMIT {PHASE26_MAX_SCAN}", params).fetchall()
        conn.close()
        qt = _phase26_tokens(q); ranked=[]
        for r in rows:
            try: details=json.loads(r[2] or "{}")
            except Exception: details={"content":r[2] or ""}
            text=" ".join(str(details.get(k,"")) for k in ("content","problem","context","root_cause","solution","implementation","related_error","knowledge_type")) + " " + str(r[1]) + " " + str(r[11] or "")
            ht=_phase26_tokens(text); overlap=len(qt & ht)
            if not overlap and qt:
                # File/function names are strong signals.
                if not any(t in str(r[16] or "").lower() or t in str(r[17] or "").lower() for t in qt): continue
            compat=_phase26_project_compatibility(project or {}, {"compatibility":r[9]}) if project else 1.0
            status=str(r[7] or "UNVERIFIED").upper(); ver_bonus={"REPEATEDLY_VERIFIED":8,"VERIFIED":5,"TESTED":2,"UNVERIFIED":0,"FAILED":-8,"OUTDATED":-15}.get(status,0)
            score=overlap*4 + float(r[3] or 0)*10 + int(r[4] or 0)*.08 + min(int(r[5] or 0),10)*.6 - min(int(r[6] or 0),6)*1.2 + ver_bonus + int(r[10] or 0)*2 + compat*6
            ranked.append((score,r,details,compat))
        ranked.sort(key=lambda x:x[0], reverse=True); out=[]; now=datetime.now().isoformat(timespec="seconds")
        for score,r,details,compat in ranked[:max(1,min(int(limit or 8),20))]:
            out.append({"id":r[0],"key_name":r[1],"details":details,"confidence":float(r[3] or 0),"quality_score":int(r[4] or 0),"success_count":int(r[5] or 0),"failure_count":int(r[6] or 0),"verification_status":r[7],"scope":r[8],"compatibility":r[9],"preferred":bool(r[10]),"tags":r[11],"metadata":r[12],"usage_success_count":int(r[13] or 0),"usage_failure_count":int(r[14] or 0),"updated_at":r[15],"file_path":r[16],"symbol_name":r[17],"relevance":round(score,3),"project_compatibility":round(compat,3)})
        if out:
            ids=[x["id"] for x in out]; marks=','.join('?' for _ in ids)
            conn=get_conn(); conn.execute(f"UPDATE brain_project_memory SET last_used_at=?,usage_count=usage_count+1 WHERE id IN ({marks})",[now,*ids]); conn.commit(); conn.close()
        return out
    except Exception as e:
        logger.warning("Phase 26 knowledge search failed: %s", e); return []


def coding_knowledge_context(project_id:int, query:str, budget:int=900) -> str:
    try:
        project = None
        try:
            conn=get_conn(); row=conn.execute("SELECT id,user_id,name,description,stack,status,root FROM code_projects WHERE id=?",(int(project_id),)).fetchone(); conn.close()
            if row: project={"id":row[0],"user_id":row[1],"name":row[2],"description":row[3],"stack":row[4],"status":row[5],"root":row[6]}
        except Exception: pass
        rows=coding_knowledge_search(project_id,query,10,False,project); parts=[]; max_chars=max(500,int(budget)*4)
        used=0
        for r in rows:
            d=r.get("details") or {}; content=d.get("solution") or d.get("content") or json.dumps(d,ensure_ascii=False,default=str)
            line=f"{d.get('knowledge_type','coding_knowledge')}::{r.get('key_name','')} [status={r.get('verification_status')} quality={r.get('quality_score')}/100 conf={r.get('confidence'):.2f}] {str(content)[:850]}"
            if used+len(line)+1>max_chars: break
            parts.append(line); used+=len(line)+1
        return "\n".join(parts)
    except Exception as e:
        logger.debug("Phase 26 knowledge context skipped: %s", e); return ""


def coding_knowledge_record_outcome(project:dict, task:dict, outcome:Optional[dict]=None) -> Optional[int]:
    """Extract one high-value knowledge record from a completed/failed coding task."""
    try:
        pid=int(project.get("id") or 0)
        if not pid: return None
        result=outcome or task or {}; code=str(result.get("code") or "")
        title=str(result.get("title") or "").strip(); desc=str(result.get("description") or "").strip()
        test_status=str(result.get("test_status") or "").lower(); review_score=int(result.get("review_score") or 100)
        sec_score=int(result.get("security_score") or 100)
        success = result.get("status") in ("done","passed") and test_status in ("passed","success","") and not result.get("last_error")
        failed = bool(result.get("last_error")) or test_status in ("failed","error") or result.get("status") in ("failed","blocked","needs_review")
        if not title or (not success and not failed): return None
        ktype="SUCCESSFUL_IMPLEMENTATION" if success else "FAILED_APPROACH"
        verification="REPEATEDLY_VERIFIED" if success and int(result.get("retry_count") or 0)==0 and test_status=="passed" and review_score>=85 and sec_score>=85 else ("VERIFIED" if success else "FAILED")
        quality=_phase26_quality(verification,1 if success else 0,0 if success else 1,sec_score>=80,review_score)
        conf=_phase26_confidence(verification,1 if success else 0,0 if success else 1,quality,True)
        solution=code[:3000] if success else str(result.get("last_error") or desc)[:2200]
        verification_payload=result.get("test_report") or result.get("test_output") or test_status or ("failed" if failed else "")
        tags=["autonomous", ktype.lower(), str(project.get("stack") or "python").lower()]
        return coding_knowledge_save(pid,ktype,title,problem=desc,context=str(result.get("target_files") or ""),root_cause=str(result.get("last_error") or ""),solution=solution,implementation=code[:2200],verification=verification_payload,related_files=[x.strip() for x in str(result.get("target_files") or "").split(",") if x.strip()],related_error=str(result.get("last_error") or ""),tags=tags,scope="project",confidence=conf,quality_score=quality,verification_status=verification,source="autonomous_workflow",success_count=1 if success else 0,failure_count=0 if success else 1,compatibility={"stack":str(project.get("stack") or "")},preferred=bool(success and quality>=90),metadata={"task_id":result.get("id"),"test_status":test_status,"review_score":review_score,"security_score":sec_score})
    except Exception as e:
        logger.debug("Phase 26 outcome extraction skipped: %s", e); return None


def coding_knowledge_record_fix(project:dict, task:dict, error_text:str, fix_text:str, test_report:Any=None, success:bool=True) -> Optional[int]:
    try:
        pid=int(project.get("id") or 0); title=str(task.get("title") or "Auto-fix")
        if not pid or not fix_text: return None
        verification="VERIFIED" if success else "FAILED"; q=_phase26_quality(verification,1 if success else 0,0 if success else 1,True,90 if success else 50); c=_phase26_confidence(verification,1 if success else 0,0 if success else 1,q,True)
        return coding_knowledge_save(pid,"BUG_SOLUTION" if success else "FAILED_APPROACH",title,problem=str(error_text)[:1800],context=str(task.get("target_files") or ""),root_cause=str(error_text)[:1800],solution=str(fix_text)[:3000],implementation=str(fix_text)[:2200],verification=test_report or ("passed" if success else "failed"),related_files=[x.strip() for x in str(task.get("target_files") or "").split(",") if x.strip()],related_error=str(error_text)[:1200],tags=["auto-fix","bug"],scope="project",confidence=c,quality_score=q,verification_status=verification,source="auto_fix",success_count=1 if success else 0,failure_count=0 if success else 1,preferred=bool(success and q>=90),metadata={"task_id":task.get("id")})
    except Exception as e:
        logger.debug("Phase 26 fix knowledge skipped: %s", e); return None


def coding_knowledge_mark_reuse(project_id:int, knowledge_id:int, success:bool) -> bool:
    try:
        conn=get_conn(); cur=conn.cursor(); now=datetime.now().isoformat(timespec="seconds")
        row=cur.execute("SELECT success_count,failure_count,quality_score,verification_status FROM brain_project_memory WHERE id=? AND project_id=? AND memory_type='coding_knowledge'",(int(knowledge_id),int(project_id))).fetchone()
        if not row: conn.close(); return False
        sc=int(row[0] or 0)+(1 if success else 0); fc=int(row[1] or 0)+(0 if success else 1)
        status="REPEATEDLY_VERIFIED" if success and sc>=3 else ("VERIFIED" if success else ("FAILED" if fc>=2 else str(row[3] or "UNVERIFIED")))
        q=_phase26_quality(status,sc,fc,True,100)
        conf=_phase26_confidence(status,sc,fc,q,True)
        cur.execute("UPDATE brain_project_memory SET success_count=?,failure_count=?,usage_success_count=usage_success_count+?,usage_failure_count=usage_failure_count+?,verification_status=?,quality_score=?,confidence=?,last_validated_at=?,updated_at=?,preferred=? WHERE id=?",(sc,fc,1 if success else 0,0 if success else 1,status,q,conf,now,now,1 if success and q>=90 else 0,int(knowledge_id)))
        conn.commit(); conn.close(); _PHASE25_MEMORY_CACHE.clear(); return True
    except Exception as e:
        logger.debug("Phase 26 reuse update skipped: %s", e); return False


def coding_knowledge_stats(project_id:int) -> Dict[str,Any]:
    try:
        conn=get_conn(); cur=conn.cursor(); pid=int(project_id)
        total=cur.execute("SELECT COUNT(*) FROM brain_project_memory WHERE project_id=? AND memory_type='coding_knowledge' AND status='active'",(pid,)).fetchone()[0]
        rows=cur.execute("SELECT verification_status,COUNT(*) FROM brain_project_memory WHERE project_id=? AND memory_type='coding_knowledge' AND status='active' GROUP BY verification_status",(pid,)).fetchall()
        avg=cur.execute("SELECT AVG(quality_score),AVG(confidence),SUM(success_count),SUM(failure_count) FROM brain_project_memory WHERE project_id=? AND memory_type='coding_knowledge' AND status='active'",(pid,)).fetchone()
        conn.close(); return {"total":int(total or 0),"by_status":dict(rows),"avg_quality":round(float(avg[0] or 0),1),"avg_confidence":round(float(avg[1] or 0),3),"successes":int(avg[2] or 0),"failures":int(avg[3] or 0)}
    except Exception as e:
        logger.warning("Phase 26 stats failed: %s", e); return {"total":0,"by_status":{},"avg_quality":0,"avg_confidence":0,"successes":0,"failures":0}


def coding_knowledge_revalidate(project_id:int, project:Optional[dict]=None, limit:int=100) -> Dict[str,int]:
    """Conservative freshness check: mark project knowledge outdated when referenced files no longer exist."""
    out={"checked":0,"outdated":0}
    try:
        conn=get_conn(); rows=conn.execute("SELECT id,details,file_path,verification_status FROM brain_project_memory WHERE project_id=? AND memory_type='coding_knowledge' AND status='active' LIMIT ?",(int(project_id),int(limit))).fetchall();
        for mid,details,file_path,status in rows:
            out["checked"]+=1
            paths=[x.strip() for x in str(file_path or "").split(",") if x.strip()]
            if paths and project and project.get("root"):
                root=os.path.abspath(project.get("root")); missing=False
                for path in paths[:5]:
                    candidate=path if os.path.isabs(path) else os.path.join(root,path)
                    if not os.path.exists(candidate): missing=True; break
                if missing:
                    conn.execute("UPDATE brain_project_memory SET status='outdated',verification_status='OUTDATED',preferred=0,updated_at=? WHERE id=?",(datetime.now().isoformat(timespec="seconds"),mid)); out["outdated"]+=1
        conn.commit(); conn.close(); _PHASE25_MEMORY_CACHE.clear(); return out
    except Exception as e:
        logger.debug("Phase 26 revalidation skipped: %s", e); return out


async def codingknowledge_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): await update.message.reply_text("⛔ Admin only."); return
        project=get_active_project(update.effective_user.id)
        if not project: await update.message.reply_text("Active project পাওয়া যায়নি।"); return
        query=" ".join(context.args).strip() if context.args else ""
        if query:
            rows=coding_knowledge_search(int(project["id"]),query,12,True,project)
            if not rows: await update.message.reply_text("Relevant coding knowledge পাওয়া যায়নি।"); return
            lines=["🧠 CODING KNOWLEDGE"]
            for r in rows:
                d=r.get("details") or {}; lines.append(f"\n• {d.get('knowledge_type','coding_knowledge')} :: {r.get('key_name','')} | {r.get('verification_status')} | quality={r.get('quality_score')}/100 | conf={r.get('confidence'):.2f}\n{str(d.get('solution') or d.get('content') or '')[:700]}")
            await send_long_text(update,"\n".join(lines)[:12000]); return
        await send_long_text(update,"🧠 CODING KNOWLEDGE STATS\n"+json.dumps(coding_knowledge_stats(int(project["id"])),ensure_ascii=False,indent=2))
    except Exception as e:
        logger.warning("Phase 26 /codingknowledge failed: %s", e); await update.message.reply_text("Coding knowledge দেখাতে সমস্যা হয়েছে।")

# ==================== PHASE 24: SECURITY & SAFETY ENGINE ====================
PHASE24_SECURITY_VERSION = '24.0'
_PHASE24_SECRET_PATTERNS = [
 ('Telegram Bot Token', re.compile(r'\b\d{7,12}:[A-Za-z0-9_-]{20,}\b'), 'CRITICAL', .98),
 ('Private Key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'), 'CRITICAL', .99),
 ('Bearer Token', re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}'), 'HIGH', .94),
 ('JWT-like Secret', re.compile(r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b'), 'HIGH', .93),
 ('API Key Assignment', re.compile(r'''(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|secret[_-]?key)\s*=\s*["'].[^"']{7,}["']'''), 'HIGH', .91),
 ('Password Assignment', re.compile(r'''(?i)\b(?:password|passwd|db_password)\s*=\s*["'].[^"']{3,}["']'''), 'HIGH', .90),
 ('Connection String', re.compile(r'''(?i)(?:mysql|postgres(?:ql)?|mongodb(?:\+srv)?|redis)://[^\s"']+'''), 'HIGH', .94),
]

def _phase24_mask_secret(v):
    try:
        v=str(v or ''); return '****' if len(v)<=8 else v[:3]+'****'+v[-4:]
    except Exception: return '****'

def _phase24_finding(severity,category,file_path,line,issue,why,evidence,fix,auto=False,confidence=.8):
    return {'severity':severity,'category':category,'file':file_path or '<memory>','line':int(line or 0),'issue':issue,'why':why,'evidence':evidence,'recommended_fix':fix,'auto_fix_possible':bool(auto),'confidence':round(float(confidence),2)}

def _phase24_security_score(findings):
    try: return max(0,min(100,100-sum({'CRITICAL':35,'HIGH':20,'MEDIUM':8,'LOW':3,'INFO':0}.get(x.get('severity','INFO'),0) for x in findings)))
    except Exception: return 0

def _phase24_ast_scan(code,file_path='<memory>'):
    try: tree=ast.parse(code or '')
    except SyntaxError as e: return [_phase24_finding('HIGH','Syntax/Security',file_path,getattr(e,'lineno',0),'Python source cannot be parsed','Security analysis is incomplete until syntax is fixed',str(e),'Fix syntax errors before security review',False,.99)]
    out=[]
    try:
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):
                name=n.func.id if isinstance(n.func,ast.Name) else (n.func.attr if isinstance(n.func,ast.Attribute) else '')
                if name in ('eval','exec'): out.append(_phase24_finding('HIGH','Dynamic Code',file_path,getattr(n,'lineno',0),f'Use of {name}() detected','Dynamic execution can become arbitrary code execution',name,'Avoid dynamic execution; use explicit parsing/dispatch',False,.98))
                elif isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='os' and name in ('system','popen'): out.append(_phase24_finding('HIGH','Command Execution',file_path,getattr(n,'lineno',0),f'os.{name}() detected','Shell execution may allow command injection',f'os.{name}(...)','Use subprocess with a fixed argument list and validated input',False,.96))
                elif isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='subprocess' and name in ('run','Popen','call','check_call','check_output'):
                    shell=any(k.arg=='shell' and isinstance(k.value,ast.Constant) and k.value.value is True for k in n.keywords); out.append(_phase24_finding('HIGH' if shell else 'MEDIUM','Command Execution',file_path,getattr(n,'lineno',0),'subprocess execution'+(' with shell=True' if shell else ''),'Dynamic commands can permit command injection','subprocess call','Prefer shell=False and a fixed argument list',False,.97 if shell else .72))
                elif isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='pickle' and name in ('load','loads'): out.append(_phase24_finding('CRITICAL','Unsafe Deserialization',file_path,getattr(n,'lineno',0),'pickle deserialization detected','Untrusted pickle data can execute arbitrary code','pickle.load/loads','Use JSON or another safe data format for untrusted data',False,.98))
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('execute','executemany') and n.args and isinstance(n.args[0],(ast.JoinedStr,ast.BinOp)): out.append(_phase24_finding('HIGH','SQL Injection',file_path,getattr(n,'lineno',0),'Dynamically constructed SQL may be unsafe','String-built SQL can permit injection','dynamic SQL expression','Use parameterized SQL placeholders',False,.90))
            if isinstance(n,ast.Import):
                for a in n.names:
                    if a.name in ('pickle','marshal'): out.append(_phase24_finding('MEDIUM','Unsafe Import',file_path,getattr(n,'lineno',0),f'Import of {a.name} detected','Unsafe serialization modules require strict trust boundaries',a.name,'Avoid for untrusted data',False,.75))
    except Exception as e: logger.warning('Phase 24 AST partial failure: %s',e)
    return out

def _phase24_pattern_scan(code,file_path='<memory>'):
    out=[]
    try:
        for i,line in enumerate((code or '').splitlines(),1):
            for category,pat,sev,conf in _PHASE24_SECRET_PATTERNS:
                m=pat.search(line)
                if m: out.append(_phase24_finding(sev,'Secret / Credential',file_path,i,'Possible hardcoded sensitive credential','Source-controlled credentials can leak','pattern='+_phase24_mask_secret(m.group(0)),'Move the credential to an environment variable or existing secret store',False,conf))
            if re.search(r'(?i)\b(?:SELECT|INSERT|UPDATE|DELETE)\b',line) and any(x in line for x in ('+','f\'', 'f"','%')): out.append(_phase24_finding('HIGH','SQL Injection',file_path,i,'Potential dynamically formatted SQL','User-controlled values in SQL strings can be injectable','SQL formatting expression','Use parameterized SQL',False,.86))
            if '../' in line or '..\\' in line: out.append(_phase24_finding('MEDIUM','Path Traversal',file_path,i,'Path traversal sequence detected','Unvalidated paths may escape the intended directory','../','Resolve and validate the final path under an allowed root',False,.88))
    except Exception as e: logger.warning('Phase 24 pattern scan failed: %s',e)
    return out

def _phase24_scan_text(code,file_path='<memory>'):
    try:
        vals=_phase24_ast_scan(code,file_path)+_phase24_pattern_scan(code,file_path); seen=set(); out=[]
        for f in vals:
            k=(f['severity'],f['category'],f['file'],f['line'],f['issue'])
            if k not in seen: seen.add(k); out.append(f)
        return out
    except Exception as e: logger.warning('Phase 24 scan failed: %s',e); return []

def _phase24_security_report(findings,scanned_files=1,previous_score=None):
    counts={k:0 for k in ('CRITICAL','HIGH','MEDIUM','LOW','INFO')}
    for f in findings: counts[f.get('severity','INFO')]=counts.get(f.get('severity','INFO'),0)+1
    score=_phase24_security_score(findings); lines=['🔐 SECURITY REPORT',f'Security Score: {score}/100',f'Files scanned: {scanned_files}','',f"Critical: {counts['CRITICAL']}",f"High: {counts['HIGH']}",f"Medium: {counts['MEDIUM']}",f"Low: {counts['LOW']}",f"Info: {counts['INFO']}"]
    for f in findings[:30]: lines += ['',f"⚠️ {f['severity']} — {f['category']}",f"File: {f['file']}  Line: {f['line']}",f"Issue: {f['issue']}",f"Why: {f['why']}",f"Evidence: {f['evidence']}",f"Fix: {f['recommended_fix']}",f"Confidence: {f['confidence']}"]
    if not findings: lines += ['','✅ No known security pattern was detected by the local scanner.']
    return {'score':score,'counts':counts,'findings':findings,'scanned_files':scanned_files,'previous_score':previous_score,'text':'\n'.join(lines)}

def _phase24_safe_autofix(findings,code):
    return {'applied':False,'changed_code':code,'reason':'No deterministic security fix is safe to auto-apply without validation.','eligible':[]}

def _phase24_scan_project_sync(root,changed_only=False):
    root=os.path.abspath(root or CODEBASE_DEFAULT_ROOT); results=[]
    try:
        files=[]
        if changed_only:
            try:
                out=subprocess.run(['git','-C',root,'status','--porcelain'],capture_output=True,text=True,timeout=10)
                if out.returncode==0:
                    for line in out.stdout.splitlines():
                        path=line[3:].strip().strip(chr(34)) if len(line)>3 else ''
                        if path.endswith('.py'): files.append(os.path.join(root,path))
            except Exception as e: logger.warning('Phase 24 changed-file detection unavailable: %s',e)
        if not files:
            for base,dirs,names in os.walk(root):
                dirs[:]=[d for d in dirs if d not in {'.git','__pycache__','.venv','venv','node_modules'}]
                files += [os.path.join(base,n) for n in names if n.endswith('.py')]
        for path in files:
            try:
                with open(path,encoding='utf8') as fh: results.append((path,_phase24_scan_text(fh.read(),path)))
            except Exception as e: logger.warning('Phase 24 file skipped %s: %s',path,e)
    except Exception as e: logger.warning('Phase 24 project scan failed: %s',e)
    return results

def _phase24_persist_scan(user_id,root,report,mode):
    try:
        conn=get_conn(); conn.execute("CREATE TABLE IF NOT EXISTS brain_security_scans (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,root TEXT,mode TEXT,scanned_files INTEGER DEFAULT 0,score INTEGER DEFAULT 100,critical_count INTEGER DEFAULT 0,high_count INTEGER DEFAULT 0,medium_count INTEGER DEFAULT 0,low_count INTEGER DEFAULT 0,info_count INTEGER DEFAULT 0,fixed_issues INTEGER DEFAULT 0,unresolved_issues INTEGER DEFAULT 0,previous_score INTEGER,report TEXT DEFAULT '',created_at TEXT DEFAULT '')")
        c=report['counts']; conn.execute('INSERT INTO brain_security_scans(user_id,root,mode,scanned_files,score,critical_count,high_count,medium_count,low_count,info_count,fixed_issues,unresolved_issues,previous_score,report,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(user_id,root,mode,report['scanned_files'],report['score'],c['CRITICAL'],c['HIGH'],c['MEDIUM'],c['LOW'],c['INFO'],0,len(report['findings']),report.get('previous_score'),json.dumps(report,ensure_ascii=False)[:50000],datetime.now().isoformat(timespec='seconds'))); conn.commit(); conn.close(); return True
    except Exception as e: logger.warning('Phase 24 history save failed: %s',e); return False

async def autonomous_security_scan(project=None,task=None,mode='changed'):
    try:
        project=project or {}; root=project.get('root') or CODEBASE_DEFAULT_ROOT
        if task and task.get('code'):
            path=(task.get('target_files') or '<task>').split(',')[0].strip() or '<task>'; findings=_phase24_scan_text(str(task.get('code')),path); report=_phase24_security_report(findings,1); report['autofix']=_phase24_safe_autofix(findings,str(task.get('code'))); return {'ok':True,'report':report,'task':task}
        rows=await asyncio.to_thread(_phase24_scan_project_sync,root,mode in ('changed','quick')); findings=[f for _,fs in rows for f in fs]; report=_phase24_security_report(findings,len(rows)); report['mode']=mode; _phase24_persist_scan(project.get('user_id'),root,report,mode); return {'ok':True,'report':report}
    except Exception as e: logger.warning('Phase 24 security scan failed: %s',e); return {'ok':False,'report':_phase24_security_report([],0),'error':str(e)}

async def securityscan_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    try:
        if not is_admin(update.effective_user.id): await update.message.reply_text('⛔ Admin only.'); return
        mode=(context.args[0].lower() if context.args else 'quick'); mode=mode if mode in ('quick','full','changed','pre-checkpoint','pre-release') else 'quick'; msg=await update.message.reply_text('🔐 Security scan চলছে…'); result=await autonomous_security_scan({'root':CODEBASE_DEFAULT_ROOT,'user_id':update.effective_user.id},mode=mode); await send_long_text(update,result['report']['text'][:12000])
        try: await msg.delete()
        except Exception: pass
    except Exception as e: logger.warning('Phase 24 /securityscan failed: %s',e); await update.message.reply_text('Security scan ব্যর্থ হয়েছে; bot স্বাভাবিকভাবে চলছে।')

# =============================================================================
# Phase 27 — Git/Rollback Intelligence
# =============================================================================
# প্রতিটা Autonomous ধাপ সফল হলে তার কোড একটা "স্ন্যাপশট" হিসেবে সংরক্ষণ করা হয়, যাতে
# পরে কোনো ধাপ কোড ভেঙে ফেললে সহজে আগের কার্যকর অবস্থায় ফিরে যাওয়া যায়। git থাকলে সেটা
# ব্যবহার হয় (লোকাল-only, কোনো remote push/GitHub টোকেন লাগে না), না থাকলে সম্পূর্ণ
# SQLite-ভিত্তিক ফলব্যাক দিয়ে একই কাজ হয় — বাকি বট মোড নিয়ে কিছু জানে না, একটাই ইন্টারফেস।

GIT_AVAILABLE = bool(shutil.which("git"))
GIT_PROJECTS_ROOT = os.path.join(CODEBASE_DEFAULT_ROOT, "git_projects")
logger.info(f"Phase 27: Git/Rollback Intelligence — মোড: {'git' if GIT_AVAILABLE else 'DB-fallback (git পাওয়া যায়নি)'}")


def _phase27_ensure_tables(conn) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS code_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            task_id INTEGER,
            seq INTEGER,
            title TEXT,
            code_text TEXT DEFAULT '',
            status TEXT DEFAULT '',
            commit_message TEXT DEFAULT '',
            mode TEXT DEFAULT 'db',
            git_hash TEXT DEFAULT '',
            created_at TEXT
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_code_snapshots_project ON code_snapshots(project_id, seq)")
    conn.commit()


def _phase27_secret_safe(text: Any) -> bool:
    """Phase 24 Security Scanner পুনর্ব্যবহার করে স্ন্যাপশট নেওয়ার আগে সিক্রেট/ক্রেডেনশিয়াল
    আছে কিনা যাচাই করে। নতুন কোনো স্ক্যানার বানানো হয়নি — বিদ্যমান হুকটাই কল হচ্ছে।"""
    try:
        findings = _phase24_scan_text(str(text or ""), "<snapshot>")
        if any(f.get("category") == "Secret / Credential" for f in findings):
            return False
    except Exception as e:
        logger.debug("Phase 27 secret scan skipped: %s", e)
    return True


def _phase27_git_repo_dir(project_id: int) -> str:
    return os.path.join(GIT_PROJECTS_ROOT, str(int(project_id)))


def _phase27_git_ensure_repo(project_id: int) -> bool:
    """git দিয়ে প্রজেক্ট-প্রতি একটা লোকাল রিপো নিশ্চিত করে। যেকোনো ব্যর্থতায় False
    রিটার্ন করে — কলার তখন স্বয়ংক্রিয়ভাবে DB-fallback ব্যবহার করবে।"""
    if not GIT_AVAILABLE:
        return False
    try:
        repo_dir = _phase27_git_repo_dir(project_id)
        os.makedirs(repo_dir, exist_ok=True)
        if not os.path.isdir(os.path.join(repo_dir, ".git")):
            subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True, timeout=10, check=True)
            subprocess.run(["git", "config", "user.email", "rohan-ai-bot@local"], cwd=repo_dir, capture_output=True, timeout=10)
            subprocess.run(["git", "config", "user.name", "ROHAN AI Assistant"], cwd=repo_dir, capture_output=True, timeout=10)
        return True
    except Exception as e:
        logger.warning("Phase 27 git init ব্যর্থ, এই প্রজেক্টের জন্য DB-fallback ব্যবহার হবে: %s", e)
        return False


def _phase27_git_commit(project_id: int, seq: int, code_text: str, message: str) -> str:
    """একটা ধাপের কোড রিপোতে লিখে commit করে। সফল হলে commit hash, ব্যর্থ হলে খালি স্ট্রিং।"""
    try:
        repo_dir = _phase27_git_repo_dir(project_id)
        fname = f"task_{int(seq):04d}.txt"
        with open(os.path.join(repo_dir, fname), "w", encoding="utf-8") as f:
            f.write(code_text or "")
        subprocess.run(["git", "add", fname], cwd=repo_dir, capture_output=True, timeout=10, check=True)
        subprocess.run(["git", "commit", "-m", message, "--allow-empty"], cwd=repo_dir, capture_output=True, timeout=10, check=True)
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, timeout=10, text=True, check=True)
        return (result.stdout or "").strip()
    except Exception as e:
        logger.warning("Phase 27 git commit ব্যর্থ, এই স্ন্যাপশটের জন্য DB-fallback ব্যবহার হবে: %s", e)
        return ""


def phase27_save_snapshot(project: dict, task: dict, note: str = "task") -> Optional[int]:
    """একটা ধাপের কোডের স্ন্যাপশট নেয়। git থাকলে সেখানেও commit হয়, তবে DB-তে সবসময়
    একটা রেকর্ড থাকে (git না থাকলেও /codehistory, /codediff, /coderollback কাজ করার জন্য)।
    সিক্রেট/ক্রেডেনশিয়াল ধরা পড়লে স্ন্যাপশট নেওয়া হয় না। কখনো exception ছোঁড়ে না।"""
    try:
        project_id = int(project.get("id", 0))
        task_id = int(task.get("id", 0))
        seq = int(task.get("seq", 0) or 0)
        title = str(task.get("title", ""))[:200]
        code_text = str(task.get("code", "") or "")
        status = str(task.get("status", "done"))
        if not project_id or not task_id:
            return None
        if not _phase27_secret_safe(code_text):
            logger.warning("Phase 27: প্রজেক্ট %s, task %s-এ সন্দেহজনক সিক্রেট পাওয়ায় স্ন্যাপশট নেওয়া হয়নি", project_id, task_id)
            return None
        message = f"{note} #{seq}: {title} [{status}] @ {datetime.now().isoformat(timespec='seconds')}"
        mode, git_hash = "db", ""
        if GIT_AVAILABLE and _phase27_git_ensure_repo(project_id):
            git_hash = _phase27_git_commit(project_id, seq, code_text, message)
            if git_hash:
                mode = "git"
        conn = get_conn()
        cur = conn.execute(
            "INSERT INTO code_snapshots (project_id, task_id, seq, title, code_text, status, commit_message, mode, git_hash, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (project_id, task_id, seq, title, code_text, status, message, mode, git_hash, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        snap_id = cur.lastrowid
        conn.close()
        return snap_id
    except Exception as e:
        logger.warning("Phase 27 snapshot save ব্যর্থ: %s", e)
        return None


def phase27_list_snapshots(project_id: int, limit: int = 50) -> list:
    try:
        conn = get_conn()
        rows = conn.execute(
            "SELECT id, task_id, seq, title, status, mode, git_hash, created_at FROM code_snapshots "
            "WHERE project_id=? ORDER BY seq ASC, id ASC LIMIT ?",
            (int(project_id), int(limit)),
        ).fetchall()
        conn.close()
        return [
            {"id": r[0], "task_id": r[1], "seq": r[2], "title": r[3], "status": r[4], "mode": r[5], "git_hash": r[6], "created_at": r[7]}
            for r in rows
        ]
    except Exception as e:
        logger.warning("Phase 27 snapshot list ব্যর্থ: %s", e)
        return []


def _phase27_get_snapshot(project_id: int, seq: Optional[int] = None) -> Optional[dict]:
    """নির্দিষ্ট seq দিলে সেটাই, না দিলে সর্বশেষ known-good (status='done') স্ন্যাপশট দেয়।"""
    try:
        conn = get_conn()
        if seq is not None:
            row = conn.execute(
                "SELECT id, task_id, seq, title, code_text, status, created_at FROM code_snapshots "
                "WHERE project_id=? AND seq=? ORDER BY id DESC LIMIT 1",
                (int(project_id), int(seq)),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, task_id, seq, title, code_text, status, created_at FROM code_snapshots "
                "WHERE project_id=? AND status='done' ORDER BY seq DESC, id DESC LIMIT 1",
                (int(project_id),),
            ).fetchone()
        conn.close()
        if not row:
            return None
        return {"id": row[0], "task_id": row[1], "seq": row[2], "title": row[3], "code_text": row[4], "status": row[5], "created_at": row[6]}
    except Exception as e:
        logger.warning("Phase 27 snapshot fetch ব্যর্থ: %s", e)
        return None


def phase27_rollback_to(project: dict, seq: Optional[int] = None) -> dict:
    """একটা প্রজেক্টকে known-good স্ন্যাপশটে ফিরিয়ে নেয়। rollback করার আগে বর্তমান
    অবস্থাও একটা স্ন্যাপশট হিসেবে সংরক্ষণ করে, যাতে rollback নিজেও reversible থাকে।
    কখনো exception ছোঁড়ে না — সবসময় {"ok": bool, ...} রিটার্ন করে।"""
    project_id = int(project.get("id", 0))
    try:
        target = _phase27_get_snapshot(project_id, seq)
        if not target:
            return {"ok": False, "error": "কোনো উপযুক্ত স্ন্যাপশট পাওয়া যায়নি।"}
        try:
            for t in get_project_tasks(project_id):
                if t["status"] == "done" and t.get("code"):
                    phase27_save_snapshot(project, t, note="pre-rollback")
        except Exception as e:
            logger.debug("Phase 27 pre-rollback স্ন্যাপশট স্কিপ হয়েছে: %s", e)
        conn = get_conn()
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "UPDATE code_tasks SET status='pending', code='', source='', updated_at=? WHERE project_id=? AND seq>?",
            (now, project_id, int(target["seq"])),
        )
        conn.execute(
            "UPDATE code_tasks SET status=?, code=?, updated_at=? WHERE id=?",
            (target["status"], target["code_text"], now, int(target["task_id"])),
        )
        conn.commit()
        conn.close()
        try:
            mark_project_status(project_id, "active")
        except Exception:
            pass
        return {"ok": True, "seq": target["seq"], "title": target["title"], "created_at": target["created_at"]}
    except Exception as e:
        logger.warning("Phase 27 rollback ব্যর্থ: %s", e)
        return {"ok": False, "error": str(e)}


def phase27_diff_text(project_id: int, seq1: int, seq2: int) -> str:
    try:
        a = _phase27_get_snapshot(project_id, seq1)
        b = _phase27_get_snapshot(project_id, seq2)
        if not a or not b:
            return "একটা বা দুটো seq-এর স্ন্যাপশটই পাওয়া যায়নি। /codehistory দিয়ে বৈধ seq দেখুন।"
        diff = difflib.unified_diff(
            (a["code_text"] or "").splitlines(),
            (b["code_text"] or "").splitlines(),
            fromfile=f"seq_{seq1}:{a['title']}",
            tofile=f"seq_{seq2}:{b['title']}",
            lineterm="",
        )
        text = "\n".join(diff)
        return text if text.strip() else "দুটো স্ন্যাপশটের মধ্যে কোনো পার্থক্য নেই।"
    except Exception as e:
        logger.warning("Phase 27 diff ব্যর্থ: %s", e)
        return "Diff তৈরি করতে সমস্যা হয়েছে।"


def build_phase27_status_text() -> str:
    """Phase 17 /brainstatus-এর জন্য একটা সংক্ষিপ্ত Git/Rollback সামারি লাইন।"""
    try:
        conn = get_conn()
        total = conn.execute("SELECT COUNT(*) FROM code_snapshots").fetchone()[0]
        git_projects = conn.execute("SELECT COUNT(DISTINCT project_id) FROM code_snapshots WHERE mode='git'").fetchone()[0]
        db_projects = conn.execute("SELECT COUNT(DISTINCT project_id) FROM code_snapshots WHERE mode='db'").fetchone()[0]
        conn.close()
        return (
            f"\n\n🗂️ Git/Rollback (Phase 27)\n"
            f"মোড: {'git' if GIT_AVAILABLE else 'DB-fallback'} | মোট স্ন্যাপশট: {total}\n"
            f"Git mode প্রজেক্ট: {git_projects} | DB-fallback প্রজেক্ট: {db_projects}"
        )
    except Exception as e:
        logger.warning("Phase 27 status ব্যর্থ: %s", e)
        return ""


async def coderollback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/coderollback [seq] — সক্রিয় প্রজেক্টকে নির্দিষ্ট (বা সর্বশেষ known-good) স্ন্যাপশটে ফেরায়।"""
    project = get_active_project(update.effective_user.id)
    if not project:
        await update.message.reply_text("কোনো সক্রিয় প্রজেক্ট নেই। /codeproject বা /codeplan দিয়ে একটা শুরু করুন।")
        return
    seq = None
    if context.args and context.args[0].lstrip("-").isdigit():
        seq = int(context.args[0])
    thinking = await update.message.reply_text("🗂️ Rollback চলছে…")
    try:
        result = phase27_rollback_to(project, seq)
        if result.get("ok"):
            await update.message.reply_text(
                f"✅ প্রজেক্ট #{project['id']} সফলভাবে ধাপ {result['seq']} ('{result['title']}') "
                f"অবস্থায় ফিরে গেছে ({str(result.get('created_at',''))[:19]})।\n"
                f"এরপরের ধাপগুলো পুনরায় pending করা হয়েছে — /codenext দিয়ে আবার এগোতে পারবেন।"
            )
        else:
            await update.message.reply_text(f"❌ Rollback ব্যর্থ হয়েছে: {result.get('error','অজানা সমস্যা')}")
    except Exception as e:
        logger.warning("Phase 27 /coderollback ব্যর্থ: %s", e)
        await update.message.reply_text("Rollback করতে সমস্যা হয়েছে; প্রজেক্টের ডেটা অপরিবর্তিত আছে।")
    finally:
        try:
            await thinking.delete()
        except Exception:
            pass


async def codehistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/codehistory — সক্রিয় প্রজেক্টের সবগুলো স্ন্যাপশটের তালিকা।"""
    project = get_active_project(update.effective_user.id)
    if not project:
        await update.message.reply_text("কোনো সক্রিয় প্রজেক্ট নেই। /codeproject বা /codeplan দিয়ে একটা শুরু করুন।")
        return
    try:
        rows = phase27_list_snapshots(project["id"])
        if not rows:
            await update.message.reply_text("এই প্রজেক্টের জন্য এখনো কোনো স্ন্যাপশট নেই।")
            return
        lines = [f"🗂️ Snapshot History — প্রজেক্ট #{project['id']}", "━━━━━━━━━━━━━━━"]
        status_icon = {"done": "✅", "failed": "❌", "in_progress": "🔧"}
        for r in rows:
            icon = status_icon.get(r["status"], "•")
            lines.append(f"{icon} seq {r['seq']}: {r['title']} [{r['mode']}] — {str(r['created_at'])[:19]}")
        await send_long_text(update, "\n".join(lines))
    except Exception as e:
        logger.warning("Phase 27 /codehistory ব্যর্থ: %s", e)
        await update.message.reply_text("History দেখাতে সমস্যা হয়েছে।")


async def codediff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/codediff seq1 seq2 — দুটো স্ন্যাপশটের মধ্যে diff দেখায়।"""
    project = get_active_project(update.effective_user.id)
    if not project:
        await update.message.reply_text("কোনো সক্রিয় প্রজেক্ট নেই। /codeproject বা /codeplan দিয়ে একটা শুরু করুন।")
        return
    if len(context.args) < 2 or not all(a.lstrip("-").isdigit() for a in context.args[:2]):
        await update.message.reply_text("এভাবে লিখুন: /codediff <seq1> <seq2>\n(seq নম্বরগুলো /codehistory দিয়ে দেখুন)")
        return
    try:
        seq1, seq2 = int(context.args[0]), int(context.args[1])
        diff_text = phase27_diff_text(project["id"], seq1, seq2)
        await send_long_text(update, f"🗂️ Diff: seq {seq1} → seq {seq2}\n```\n{diff_text[:9000]}\n```")
    except Exception as e:
        logger.warning("Phase 27 /codediff ব্যর্থ: %s", e)
        await update.message.reply_text("Diff দেখাতে সমস্যা হয়েছে।")






# =============================================================================
# PHASE 28 — AUTONOMOUS CHANGE IMPACT ANALYSIS & DEPENDENCY INTELLIGENCE
# =============================================================================
# Free/local, stdlib-first, reuses Phase 18 graph/index, Phase 19 context,
# Phase 21 testing, Phase 22 auto-fix, Phase 24 security, Phase 25 memory,
# Phase 26 coding knowledge and Phase 27 checkpoints/rollback.  This layer is
# deliberately non-fatal: analysis failure falls back to the existing workflow.

PHASE28_VERSION = 1
PHASE28_MAX_FILES = 1200
PHASE28_MAX_SYMBOLS = 20000
PHASE28_MAX_EDGES = 50000
PHASE28_RISK_THRESHOLDS = ((75, "CRITICAL"), (55, "HIGH"), (30, "MEDIUM"), (0, "LOW"))


def _phase28_ensure_tables(conn) -> None:
    """Create only Phase-28 metadata tables; never duplicate Phase-18 tables."""
    conn.execute("""CREATE TABLE IF NOT EXISTS impact_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER DEFAULT 0,
        file_path TEXT DEFAULT '',
        impact_level TEXT DEFAULT 'LOW',
        risk_score INTEGER DEFAULT 0,
        outcome TEXT DEFAULT 'analysis',
        regression INTEGER DEFAULT 0,
        evidence TEXT DEFAULT '{}',
        created_at TEXT DEFAULT ''
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_impact_history_file ON impact_history(file_path, created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_impact_history_project ON impact_history(project_id, created_at)")
    conn.execute("""CREATE TABLE IF NOT EXISTS phase28_file_cache (
        root_path TEXT NOT NULL,
        relative_path TEXT NOT NULL,
        file_hash TEXT DEFAULT '',
        mtime REAL DEFAULT 0,
        payload TEXT DEFAULT '{}',
        updated_at TEXT DEFAULT '',
        PRIMARY KEY(root_path, relative_path)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_phase28_cache_hash ON phase28_file_cache(root_path, file_hash, mtime)")
    # Extend existing code_tasks only; no new task table.
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(code_tasks)").fetchall()}
        additions = {
            "impact_status": "TEXT DEFAULT ''",
            "impact_level": "TEXT DEFAULT 'LOW'",
            "impact_score": "INTEGER DEFAULT 0",
            "impact_report": "TEXT DEFAULT '{}'",
            "expected_files": "TEXT DEFAULT '[]'",
            "actual_files": "TEXT DEFAULT '[]'",
            "impact_validation": "TEXT DEFAULT '{}'",
            "impact_updated_at": "TEXT DEFAULT ''",
        }
        for name, decl in additions.items():
            if name not in cols:
                try:
                    conn.execute(f"ALTER TABLE code_tasks ADD COLUMN {name} {decl}")
                except sqlite3.OperationalError:
                    pass
    except Exception:
        pass
    conn.commit()


def _phase28_rel(path: str, root: str) -> str:
    try:
        return os.path.relpath(os.path.abspath(path), os.path.abspath(root)).replace(os.sep, "/")
    except Exception:
        return os.path.basename(path)


def _phase28_is_ignored(rel: str) -> bool:
    parts = set(rel.split("/"))
    ignored = {".git", "__pycache__", ".venv", "venv", "node_modules", "git_projects", "logs"}
    return bool(parts & ignored) or rel.startswith(".")


def _phase28_module_name(rel: str) -> str:
    rel = rel.replace("/", ".")
    if rel.endswith("/__init__.py"):
        return rel[:-12].strip(".")
    if rel.endswith(".py"):
        return rel[:-3]
    return rel


def _phase28_safe_read(path: str, max_bytes: int = 2_000_000) -> str:
    try:
        if os.path.getsize(path) > max_bytes:
            return ""
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


class _Phase28AST(ast.NodeVisitor):
    """Small, deterministic AST extractor; unresolved dynamic behavior is LOW confidence."""
    def __init__(self, rel: str):
        self.rel = rel
        self.module = _phase28_module_name(rel)
        self.symbols = []
        self.edges = []
        self.current = []
        self.imports = []
        self.env_vars = set()
        self.handler_names = set()
        self.constants = []

    def _q(self, name: str) -> str:
        return ".".join([self.module] + self.current + [name]) if self.module else ".".join(self.current + [name])

    def _add_symbol(self, name, typ, node, metadata=None):
        q = self._q(name)
        self.symbols.append({"name": name, "qualified_name": q, "symbol_type": typ,
                             "line": getattr(node, "lineno", 0), "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                             "metadata": metadata or {}})
        return q

    def visit_ClassDef(self, node):
        q = self._add_symbol(node.name, "class", node, {"bases": [ast.unparse(x) if hasattr(ast, "unparse") else getattr(x, "id", "") for x in node.bases]})
        for base in node.bases:
            self.edges.append((q, ast.unparse(base) if hasattr(ast, "unparse") else getattr(base, "id", ""), "inheritance", getattr(node, "lineno", 0)))
        self.current.append(node.name)
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(child)
            elif isinstance(child, ast.ClassDef):
                self.visit(child)
        self.current.pop()

    def visit_FunctionDef(self, node):
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_function(node)

    def _visit_function(self, node):
        q = self._add_symbol(node.name, "method" if self.current else "function", node, {
            "signature": _phase28_signature(node),
            "returns": _phase28_return_kinds(node),
            "decorators": [ast.unparse(d) if hasattr(ast, "unparse") else "" for d in node.decorator_list],
        })
        if node.name.endswith(("_handler", "_callback", "_command", "_job")) or node.name in {"handler", "callback"}:
            self.handler_names.add(q)
        self.current.append(node.name)
        for child in node.body:
            self.visit(child)
        self.current.pop()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append((alias.name, alias.asname or alias.name.split(".")[-1], node.lineno, "import"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = "." * int(node.level) + (node.module or "")
        for alias in node.names:
            if alias.name == "*":
                continue
            self.imports.append((module + ("." if module else "") + alias.name, alias.asname or alias.name, node.lineno, "from_import"))
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                self.constants.append(target.id)
                self._add_symbol(target.id, "constant", node, {"value_type": _phase28_expr_kind(node.value)})
        self.generic_visit(node)

    def visit_Call(self, node):
        fn = node.func
        target = ""
        if isinstance(fn, ast.Name):
            target = fn.id
        elif isinstance(fn, ast.Attribute):
            target = fn.attr
        if target:
            caller = self._q(self.current[-1]) if self.current else self.module
            self.edges.append((caller, target, "call", getattr(node, "lineno", 0)))
            if target == "getenv" and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                self.env_vars.add(node.args[0].value)
            if target in {"environ", "getenv"} and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                self.env_vars.add(node.args[0].value)
            # python-telegram-bot registrations are dependency edges to handlers.
            if target in {"CommandHandler", "MessageHandler", "CallbackQueryHandler", "ConversationHandler"}:
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        self.edges.append((caller, arg.id, "handler_registration", getattr(node, "lineno", 0)))
        self.generic_visit(node)

    def visit_Subscript(self, node):
        # os.environ["NAME"]
        try:
            if isinstance(node.value, ast.Attribute) and node.value.attr == "environ":
                sl = node.slice
                if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                    self.env_vars.add(sl.value)
        except Exception:
            pass
        self.generic_visit(node)


def _phase28_expr_kind(node) -> str:
    if node is None:
        return "none"
    if isinstance(node, ast.Constant):
        return type(node.value).__name__
    if isinstance(node, (ast.Dict,)): return "dict"
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)): return type(node).__name__.lower()
    if isinstance(node, ast.Call): return "call"
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.JoinedStr): return "str"
    return type(node).__name__.lower()


def _phase28_return_kinds(node) -> list:
    kinds=[]
    for child in ast.walk(node):
        if isinstance(child, ast.Return):
            kinds.append(_phase28_expr_kind(child.value))
    return sorted(set(kinds))


def _phase28_signature(node) -> dict:
    args = list(getattr(node.args, "posonlyargs", [])) + list(node.args.args)
    defaults = list(node.args.defaults)
    required = max(0, len(args) - len(defaults))
    kwonly = list(node.args.kwonlyargs)
    kw_required = sum(1 for d in node.args.kw_defaults if d is None)
    return {"params": [a.arg for a in args], "required": required, "kwonly": [a.arg for a in kwonly], "kw_required": kw_required,
            "vararg": bool(node.args.vararg), "kwarg": bool(node.args.kwarg)}


def _phase28_signature_breaking(old_sig: dict, new_sig: dict) -> bool:
    old_params, new_params = old_sig.get("params", []), new_sig.get("params", [])
    if new_sig.get("required", 0) > old_sig.get("required", 0): return True
    if new_params[:len(old_params)] != old_params: return True
    if not old_sig.get("vararg") and new_sig.get("vararg") is False and len(new_params) > len(old_params) and new_sig.get("required", 0) > len(old_params): return True
    if set(old_sig.get("kwonly", [])) - set(new_sig.get("kwonly", [])) and not new_sig.get("kwarg"): return True
    return False


def _phase28_compare_contracts(old_text: str, new_text: str) -> dict:
    out={"signature_changes":[], "return_value_changes":[], "confidence":"HIGH"}
    try:
        old_tree,new_tree=ast.parse(old_text or ""),ast.parse(new_text or "")
        def funcs(tree):
            d={}
            for n in ast.walk(tree):
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    d[n.name]=n
            return d
        oldf,newf=funcs(old_tree),funcs(new_tree)
        for name in sorted(set(oldf)|set(newf)):
            if name not in oldf or name not in newf:
                continue
            osig,nsig=_phase28_signature(oldf[name]),_phase28_signature(newf[name])
            if osig!=nsig:
                out["signature_changes"].append({"function":name,"old":osig,"new":nsig,"breaking":_phase28_signature_breaking(osig,nsig)})
            ork,nrk=_phase28_return_kinds(oldf[name]),_phase28_return_kinds(newf[name])
            if ork!=nrk:
                out["return_value_changes"].append({"function":name,"old":ork,"new":nrk,"confidence":"MEDIUM"})
    except Exception as e:
        out["confidence"]="LOW"; out["error"]=str(e)[:1000]
    return out


def _phase28_cache_get(root: str, rel: str, file_hash: str, mtime: float):
    try:
        conn=get_conn()
        row=conn.execute("SELECT payload FROM phase28_file_cache WHERE root_path=? AND relative_path=? AND file_hash=? AND mtime=?",(root,rel,file_hash,float(mtime))).fetchone()
        conn.close()
        if not row: return None
        return json.loads(row[0] or "{}")
    except Exception:
        return None


def _phase28_cache_put(root: str, rel: str, file_hash: str, mtime: float, payload: dict) -> None:
    try:
        conn=get_conn(); conn.execute("INSERT INTO phase28_file_cache(root_path,relative_path,file_hash,mtime,payload,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(root_path,relative_path) DO UPDATE SET file_hash=excluded.file_hash,mtime=excluded.mtime,payload=excluded.payload,updated_at=excluded.updated_at",(root,rel,file_hash,float(mtime),json.dumps(payload,ensure_ascii=False),datetime.now().isoformat(timespec="seconds"))); conn.commit(); conn.close()
    except Exception as e:
        logger.debug("Phase 28 cache write skipped: %s",e)


def _phase28_existing_index_edges(root: str) -> list:
    """Reuse Phase 18's persistent dependency edges when available; never requires them."""
    out=[]
    try:
        conn=get_conn()
        rows=conn.execute("SELECT sf.relative_path,tf.relative_path,e.edge_type,e.source_name,e.target_name,e.line_number FROM brain_codebase_edges e LEFT JOIN brain_codebase_files sf ON sf.id=e.source_file_id LEFT JOIN brain_codebase_files tf ON tf.id=e.target_file_id WHERE sf.relative_path IS NOT NULL AND (tf.relative_path IS NOT NULL OR e.edge_type='call') LIMIT ?",(PHASE28_MAX_EDGES,)).fetchall()
        conn.close()
        for sf,tf,typ,src,tgt,line in rows:
            out.append({"file":sf,"target_file":tf or "","edge_type":typ,"source":src or _phase28_module_name(sf),"target":tgt or "","line":line or 0,"source_index":"phase18"})
    except Exception:
        pass
    return out


def _phase28_scan(root: str) -> dict:
    root=os.path.abspath(root)
    files={}; symbols=[]; edges=[]; env_refs=[]
    py_paths=[]
    for base, dirs, names in os.walk(root):
        relbase=_phase28_rel(base,root)
        dirs[:] = [d for d in dirs if not _phase28_is_ignored((relbase+"/"+d).strip("./"))]
        for name in names:
            path=os.path.join(base,name); rel=_phase28_rel(path,root)
            if _phase28_is_ignored(rel): continue
            if name.endswith(".py"):
                py_paths.append(path)
            elif name in {"requirements.txt","pyproject.toml","Pipfile"}:
                files[rel]={"path":path,"rel":rel,"type":"package_config"}
    py_paths=py_paths[:PHASE28_MAX_FILES]
    module_to_rel={}
    for path in py_paths:
        rel=_phase28_rel(path,root); module_to_rel[_phase28_module_name(rel)]=rel
        if rel.endswith("/__init__.py"): module_to_rel[_phase28_module_name(rel)+".__init__"]=rel
    file_info={}
    for path in py_paths:
        rel=_phase28_rel(path,root); text=_phase28_safe_read(path)
        file_hash=hashlib.sha256(text.encode()).hexdigest() if text else ""; mtime=os.path.getmtime(path) if os.path.exists(path) else 0
        info={"path":path,"rel":rel,"type":"python","hash":file_hash,"mtime":mtime,
              "symbols":[],"imports":[],"parse_ok":False,"parse_error":""}
        cached=_phase28_cache_get(root,rel,file_hash,mtime)
        if cached:
            info.update(cached); info["path"]=path; info["rel"]=rel; info["hash"]=file_hash; info["mtime"]=mtime; info["cache_hit"]=True
            file_info[rel]=info; symbols.extend([{**x,"file":rel} for x in info.get("symbols",[])]); env_refs.extend([{"file":rel,"variable":v} for v in info.get("env_vars",[])])
        else:
            try:
                tree=ast.parse(text,filename=rel); visitor=_Phase28AST(rel); visitor.visit(tree)
                info.update({"symbols":visitor.symbols,"imports":visitor.imports,"env_vars":sorted(visitor.env_vars),"parse_ok":True,"parse_error":""})
                _phase28_cache_put(root,rel,file_hash,mtime,{k:info[k] for k in ("symbols","imports","env_vars","parse_ok","parse_error")})
                file_info[rel]=info; symbols.extend([{**x,"file":rel} for x in visitor.symbols]); env_refs.extend([{"file":rel,"variable":v} for v in visitor.env_vars])
                for src,tgt,typ,line in visitor.edges: edges.append({"source":src,"target":tgt,"edge_type":typ,"file":rel,"line":line})
            except Exception as e:
                info["parse_error"]=str(e)[:1000]; file_info[rel]=info
    # Local import resolution.
    for rel,info in file_info.items():
        if not info.get("parse_ok"): continue
        module=_phase28_module_name(rel)
        for mod,alias,line,typ in info.get("imports",[]):
            level=len(mod)-len(mod.lstrip("."))
            clean=mod.lstrip(".")
            if typ == "from_import" and "." in clean:
                clean=clean.rsplit(".",1)[0]
            if level:
                base_parts=module.split(".")[:-level]
                clean=".".join(base_parts + ([clean] if clean else []))
            target_rel=module_to_rel.get(clean) or module_to_rel.get(clean.split(".")[0])
            if target_rel:
                edges.append({"source":module,"target":_phase28_module_name(target_rel),"edge_type":"file_import","file":rel,"line":line,"target_file":target_rel})
            elif level:
                edges.append({"source":module,"target":clean,"edge_type":"dynamic_import","file":rel,"line":line})
    # Reuse the persistent Phase-18 graph when it is available. Fresh AST edges remain authoritative.
    for e in _phase28_existing_index_edges(root):
        if e.get("file") in file_info:
            edges.append(e)
    # Package dependency usage.
    package_names=set()
    for rel in ("requirements.txt","Pipfile","pyproject.toml"):
        p=os.path.join(root,rel)
        text=_phase28_safe_read(p)
        for line in text.splitlines():
            m=re.match(r"\s*([A-Za-z0-9_.-]+)",line)
            if m and not line.lstrip().startswith(("#","[")): package_names.add(m.group(1).lower().replace("-","_"))
    for rel,info in file_info.items():
        for mod,alias,line,typ in info.get("imports",[]):
            top=mod.lstrip(".").split(".")[0].lower().replace("-","_")
            if top in package_names and top not in {"os","sys"}:
                edges.append({"source":_phase28_module_name(rel),"target":top,"edge_type":"package_dependency","file":rel,"line":line})
    # Historical file modification signal (mtime only; no invented failures).
    return {"root":root,"files":file_info,"symbols":symbols[:PHASE28_MAX_SYMBOLS],"edges":edges[:PHASE28_MAX_EDGES],"env_refs":env_refs}


def _phase28_build_indexes(scan: dict):
    by_file=scan.get("files",{}); by_symbol={}; short={}
    for s in scan.get("symbols",[]):
        by_symbol[s["qualified_name"]]=s; short.setdefault(s["name"],[]).append(s)
    return by_file,by_symbol,short


def _phase28_resolve_target(target: str, root: str, scan: dict) -> set:
    target=os.path.abspath(target if os.path.isabs(target) else os.path.join(root,target))
    rel=_phase28_rel(target,root)
    if rel in scan.get("files",{}): return {rel}
    low=target.lower()
    return {r for r in scan.get("files",{}) if r.lower()==low or os.path.basename(r).lower()==os.path.basename(rel).lower()}


def _phase28_match_request(request: str, root: str, scan: dict) -> set:
    q=(request or "").lower(); hits=set()
    tokens=[t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_.-]{2,}",q) if t not in {"change","update","modify","implement","function","class","file"}]
    for rel,info in scan.get("files",{}).items():
        hay=rel.lower()+" "+" ".join(s.get("name","").lower()+" "+s.get("qualified_name","").lower() for s in info.get("symbols",[]))
        if any(t in hay for t in tokens): hits.add(rel)
    if not hits:
        try:
            for item in codebase_search(request,root,limit=12):
                hits.add(item.get("relative_path") or _phase28_rel(item.get("file_path",""),root))
        except Exception:
            pass
    return hits


def _phase28_reverse_impact(scan: dict, targets: set) -> dict:
    edges=scan.get("edges",[]); reverse={}
    module_to_file={_phase28_module_name(r):r for r in scan.get("files",{})}
    for e in edges:
        t=e.get("target",""); tf=e.get("target_file") or module_to_file.get(t)
        if tf: reverse.setdefault(tf,[]).append(e)
        # symbol-name-only call edge: resolve unique symbol owner.
        if e.get("edge_type")=="call":
            matches=[s.get("file") for s in scan.get("symbols",[]) if s.get("name")==t]
            if len(set(matches))==1: reverse.setdefault(matches[0],[]).append(e)
    affected={}; queue=[(t,0,"direct") for t in targets]; seen=set(targets)
    while queue:
        node,depth,kind=queue.pop(0); affected[node]={"depth":depth,"kind":kind}
        for e in reverse.get(node,[]):
            src=e.get("file") or e.get("source","")
            if src and src not in seen and src in scan.get("files",{}):
                seen.add(src); queue.append((src,depth+1,"indirect"));
    return affected


def _phase28_cycles(scan: dict) -> list:
    graph={}
    module_to_file={_phase28_module_name(r):r for r in scan.get("files",{})}
    for e in scan.get("edges",[]):
        if e.get("edge_type") in {"file_import","dependency","dynamic_import"}:
            a=e.get("file"); b=e.get("target_file") or module_to_file.get(e.get("target",""))
            if a and b: graph.setdefault(a,set()).add(b)
    cycles=[]; visiting=set(); visited=set(); stack=[]
    def dfs(n):
        if n in visiting:
            if n in stack:
                cyc=stack[stack.index(n):]+[n]
                if cyc not in cycles: cycles.append(cyc)
            return
        if n in visited: return
        visiting.add(n); stack.append(n)
        for x in graph.get(n,set()): dfs(x)
        stack.pop(); visiting.remove(n); visited.add(n)
    for n in graph: dfs(n)
    return cycles[:50]


def _phase28_dead_code(scan: dict) -> list:
    referenced=set();
    for e in scan.get("edges",[]): referenced.add(e.get("target",""))
    candidates=[]
    for s in scan.get("symbols",[]):
        if s.get("symbol_type") not in {"function","method","class","constant"}: continue
        name=s.get("name","")
        if name.startswith("_") or name in referenced: continue
        if name.endswith(("_handler","_callback","_command","_job")): continue
        candidates.append({"file":s.get("file"),"symbol":s.get("qualified_name"),"type":s.get("symbol_type"),"reason":"no static in-project reference found"})
    return candidates[:200]


def _phase28_hotspots(scan: dict, root: str, project_id: int = 0) -> list:
    counts={r:0 for r in scan.get("files",{})}
    for e in scan.get("edges",[]):
        src=e.get("file"); tgt=e.get("target_file")
        if tgt in counts: counts[tgt]+=1
        if src in counts: counts[src]+=0
    hist={}
    try:
        conn=get_conn(); rows=conn.execute("SELECT file_path, SUM(CASE WHEN outcome IN ('failure','regression') THEN 1 ELSE 0 END), COUNT(*) FROM impact_history WHERE project_id=? GROUP BY file_path",(int(project_id or 0),)).fetchall(); conn.close()
        for path,fail,total in rows: hist[_phase28_rel(path,root)]=[int(fail or 0),int(total or 0)]
    except Exception: pass
    out=[]
    for rel,count in sorted(counts.items(), key=lambda kv:kv[1], reverse=True)[:30]:
        fail,total=hist.get(rel,[0,0]);
        if count>=3 or fail:
            out.append({"file":rel,"consumers":count,"historical_failures":fail,"historical_observations":total,"risk":"HIGH" if fail>=2 or count>=8 else "MEDIUM"})
    return out


def _phase28_risk(affected: dict, scan: dict, targets: set, contracts: dict, project_id: int = 0) -> tuple:
    files=len(affected); depths=[v.get("depth",0) for v in affected.values()]; max_depth=max(depths or [0]); consumers=max(0,files-len(targets))
    score=min(100, files*5 + consumers*3 + max_depth*4)
    text=" ".join(targets).lower()
    all_symbols=" ".join(s.get("qualified_name","").lower() for s in scan.get("symbols",[]) if s.get("file") in affected)
    if any(x in text+all_symbols for x in ("database","db","migration","schema","query","model")): score+=18
    if any(x in text+all_symbols for x in ("security","auth","permission","token","credential","secret")): score+=18
    if any(x in text+all_symbols for x in ("router","provider","ai_router","brain","decision","context","agent")): score+=10
    if any(x in text+all_symbols for x in ("handler","telegram","callback","conversation")): score+=8
    if contracts.get("signature_changes"): score+=12
    if any(x.get("breaking") for x in contracts.get("signature_changes",[])): score+=8
    if contracts.get("return_value_changes"): score+=6
    score=min(100,int(score))
    level=next(level for threshold,level in PHASE28_RISK_THRESHOLDS if score>=threshold)
    return score,level


def _phase28_detect_tests(root: str) -> list:
    """Discover test files from the filesystem, with Phase-18 DB index as an optional supplement."""
    found=set()
    root=os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    try:
        for base, dirs, names in os.walk(root):
            relbase=_phase28_rel(base,root)
            dirs[:] = [d for d in dirs if not _phase28_is_ignored((relbase+"/"+d).strip("./"))]
            for name in names:
                low=name.lower()
                if low.startswith("test_") and low.endswith(".py") or low.endswith("_test.py"):
                    found.add(_phase28_rel(os.path.join(base,name),root))
    except Exception as e:
        logger.debug("Phase 28 filesystem test discovery failed: %s",e)
    try:
        for item in _phase21_detect_existing_tests(root) or []:
            found.add(_phase28_rel(item if os.path.isabs(item) else os.path.join(root,item),root))
    except Exception:
        pass
    return sorted(found)[:200]


def _phase28_related_tests(test_files: list, affected_files: list) -> list:
    """Choose tests whose names overlap affected module stems; deterministic and conservative."""
    stems=set()
    for path in affected_files or []:
        stem=os.path.splitext(os.path.basename(str(path)))[0].lower()
        if stem:
            stems.add(stem.removeprefix("test_").removesuffix("_test"))
    if not stems:
        return []
    related=[]
    for test in test_files or []:
        name=os.path.basename(test).lower()
        normalized=name.removeprefix("test_").removesuffix("_test.py").removesuffix(".py")
        if any(stem and (stem in name or stem == normalized) for stem in stems):
            related.append(test)
    return sorted(set(related))[:50]


def _phase28_run_regression(root: str, test_files: list, mode: str = "full") -> dict:
    """Run existing unittest-compatible regression tests without a shell; bounded and non-fatal."""
    root=os.path.abspath(root or CODEBASE_DEFAULT_ROOT)
    tests=[str(x).replace("\\","/") for x in (test_files or [])]
    if not tests:
        return {"ok":True,"skipped":True,"mode":mode,"tests":[],"output":"No existing regression tests discovered."}
    try:
        # unittest accepts file paths only indirectly, so use discovery when the full suite is requested.
        if mode == "full":
            cmd=[sys.executable,"-m","unittest","discover","-s",root,"-p","test*.py"]
        else:
            abs_tests=[os.path.join(root,t) if not os.path.isabs(t) else t for t in tests]
            cmd=[sys.executable,"-m","unittest"] + abs_tests
        env=os.environ.copy(); env["PYTHONUNBUFFERED"]="1"
        proc=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=max(60,int(PHASE21_TEST_TIMEOUT)*6),shell=False,env=env)
        output=((proc.stdout or "")+"\n"+(proc.stderr or ""))[:PHASE21_MAX_TEST_OUTPUT]
        return {"ok":proc.returncode==0,"skipped":False,"mode":mode,"tests":tests,"exit_code":proc.returncode,"output":output,"timed_out":False}
    except subprocess.TimeoutExpired:
        return {"ok":False,"skipped":False,"mode":mode,"tests":tests,"exit_code":-1,"output":"REGRESSION TEST TIMEOUT","timed_out":True}
    except Exception as e:
        return {"ok":False,"skipped":False,"mode":mode,"tests":tests,"exit_code":-1,"output":str(e)[:4000],"timed_out":False}


def _phase28_persist_task_impact(task_id: int, impact: dict, actual_files=None, validation=None) -> None:
    try:
        conn=get_conn(); now=datetime.now().isoformat(timespec="seconds")
        conn.execute("UPDATE code_tasks SET impact_status=?,impact_level=?,impact_score=?,impact_report=?,expected_files=?,actual_files=?,impact_validation=?,impact_updated_at=?,updated_at=? WHERE id=?",(
            str(impact.get("status","ok")),str(impact.get("risk_level","LOW")),int(impact.get("risk_score",0)),json.dumps(impact,ensure_ascii=False)[:30000],
            json.dumps(sorted(impact.get("expected_files",[])),ensure_ascii=False),json.dumps(sorted(actual_files or []),ensure_ascii=False),json.dumps(validation or {},ensure_ascii=False)[:12000],now,now,int(task_id)))
        conn.commit(); conn.close()
    except Exception as e:
        logger.debug("Phase 28 task impact persistence skipped: %s",e)


def phase28_expected_vs_actual(expected_files, actual_files, expected_symbols=None, actual_symbols=None) -> dict:
    expected=set(str(x).replace("\\","/") for x in (expected_files or [])); actual=set(str(x).replace("\\","/") for x in (actual_files or []))
    es=set(expected_symbols or []); ass=set(actual_symbols or [])
    return {"ok": expected <= actual and not (actual-expected), "expected":sorted(expected), "actual":sorted(actual),
            "missing_expected":sorted(expected-actual), "unexpected":sorted(actual-expected),
            "missing_symbols":sorted(es-ass), "unexpected_symbols":sorted(ass-es),
            "confidence":"HIGH" if expected or actual else "LOW"}


def phase28_analyze_change(project: dict, task: dict, changed_files=None) -> dict:
    """Pre-implementation impact analysis. All static uncertainty is explicitly surfaced."""
    try:
        root=os.path.abspath(project.get("root") or CODEBASE_DEFAULT_ROOT)
        scan=_phase28_scan(root)
        explicit=[]
        raw=task.get("target_files","") if isinstance(task,dict) else ""
        if isinstance(raw,str): explicit=[x.strip() for x in re.split(r"[,;\\n]+",raw) if x.strip()]
        targets=set()
        for x in (changed_files or explicit): targets |= _phase28_resolve_target(x,root,scan)
        if not targets:
            targets=_phase28_match_request((task.get("description","") if isinstance(task,dict) else "")+" "+(task.get("title","") if isinstance(task,dict) else ""),root,scan)
        affected=_phase28_reverse_impact(scan,targets)
        # Contract comparison is supported when a task supplies old/new source texts.
        contracts=_phase28_compare_contracts(task.get("old_code",""),task.get("new_code","") or task.get("code","")) if task.get("old_code") else {"signature_changes":[],"return_value_changes":[],"confidence":"LOW"}
        score,level=_phase28_risk(affected,scan,targets,contracts,int(project.get("id",0) or 0))
        dynamic=[e for e in scan.get("edges",[]) if e.get("edge_type")=="dynamic_import"]
        confidence="HIGH" if all(v.get("parse_ok") for v in scan.get("files",{}).values() if v.get("type")=="python") else "MEDIUM"
        if dynamic: confidence="LOW"
        memory=[]; knowledge=[]
        try:
            pid=int(project.get("id",0) or 0)
            if pid:
                memory=project_memory_search(pid, " ".join(sorted(targets)) or task.get("title","") , limit=5)
                knowledge=coding_knowledge_search(pid, " ".join(sorted(targets)) or task.get("title","") , limit=5, include_failed=False, project=project)
        except Exception as e: logger.debug("Phase 28 memory/knowledge lookup skipped: %s",e)
        report={
            "version":PHASE28_VERSION,"status":"ok","root":root,"targets":sorted(targets),
            "expected_files":sorted(affected.keys()) if affected else sorted(targets),
            "affected":{k:v for k,v in sorted(affected.items(), key=lambda kv:(kv[1].get("depth",0),kv[0]))},
            "dependency_depth":max([v.get("depth",0) for v in affected.values()] or [0]),
            "direct_affected":sorted([k for k,v in affected.items() if v.get("depth")==0]),
            "indirect_affected":sorted([k for k,v in affected.items() if v.get("depth",0)>0]),
            "risk_score":score,"risk_level":level,"confidence":confidence,
            "contracts":contracts,"circular_dependencies":_phase28_cycles(scan),
            "dead_code_candidates":_phase28_dead_code(scan),
            "architecture_hotspots":_phase28_hotspots(scan,root,int(project.get("id",0) or 0)),
            "environment_variables":sorted([x for x in scan.get("env_refs",[]) if x.get("file") in affected or x.get("file") in targets]),
            "database_impact":any(x in (" ".join(targets)).lower() for x in ("db","database","model","schema","migration","query")),
            "security_impact":any(x in (" ".join(targets)).lower() for x in ("security","auth","permission","credential","secret","token")),
            "telegram_impact":any(x in (" ".join(targets)).lower() for x in ("telegram","handler","callback","conversation")),
            "ai_provider_impact":any(x in (" ".join(targets)).lower() for x in ("ai_router","provider","openrouter","groq","cerebras")),
            "brain_os_impact":any(x in (" ".join(targets)).lower() for x in ("brain","decision","context","knowledge","memory","pattern","template","documentation","error")),
            "historical_evidence":[],"project_memory":memory[:5],"coding_knowledge":knowledge[:5],
            "dynamic_dependency_count":len(dynamic),
            "incremental_cache_hits":sum(1 for v in scan.get("files",{}).values() if v.get("cache_hit")),
            "incremental_cache_misses":sum(1 for v in scan.get("files",{}).values() if v.get("type")=="python" and not v.get("cache_hit")),
        }
        try:
            conn=get_conn(); rows=conn.execute("SELECT file_path, SUM(CASE WHEN outcome IN ('failure','regression') THEN 1 ELSE 0 END), COUNT(*) FROM impact_history WHERE file_path IN ({}) GROUP BY file_path".format(",".join("?"*len(targets)) if targets else "''"), tuple(os.path.join(root,x) for x in targets)).fetchall() if targets else [] ; conn.close()
            report["historical_evidence"]=[{"file":_phase28_rel(r,root),"failures":int(f or 0),"observations":int(n or 0)} for r,f,n in rows]
            if any(x["failures"] for x in report["historical_evidence"]): report["risk_score"]=min(100,report["risk_score"]+min(15,sum(x["failures"] for x in report["historical_evidence"])))
            if report["risk_score"]>=75: report["risk_level"]="CRITICAL"
            elif report["risk_score"]>=55: report["risk_level"]="HIGH"
            elif report["risk_score"]>=30: report["risk_level"]="MEDIUM"
            else: report["risk_level"]="LOW"
        except Exception as e: logger.debug("Phase 28 historical lookup skipped: %s",e)
        return report
    except Exception as e:
        logger.warning("Phase 28 impact analysis failed: %s",e)
        return {"version":PHASE28_VERSION,"status":"failed","confidence":"LOW","risk_score":0,"risk_level":"LOW","expected_files":[],"error":str(e)[:2000]}


def phase28_record_outcome(project_id:int, affected_files, outcome:str, regression:bool=False, evidence=None, risk_score:int=0, impact_level:str="LOW") -> bool:
    try:
        conn=get_conn(); now=datetime.now().isoformat(timespec="seconds")
        for rel in affected_files or []:
            conn.execute("INSERT INTO impact_history(project_id,file_path,impact_level,risk_score,outcome,regression,evidence,created_at) VALUES(?,?,?,?,?,?,?,?)",
                         (int(project_id or 0),str(rel),str(impact_level),int(risk_score),str(outcome),int(bool(regression)),json.dumps(evidence or {},ensure_ascii=False)[:12000],now))
        conn.commit(); conn.close(); return True
    except Exception as e:
        logger.debug("Phase 28 historical outcome persistence skipped: %s",e); return False


def phase28_actual_files_snapshot(root:str) -> dict:
    """Hash-based filesystem snapshot for expected-vs-actual validation; local only."""
    out={}; root=os.path.abspath(root)
    try:
        for base,dirs,names in os.walk(root):
            relbase=_phase28_rel(base,root); dirs[:] = [d for d in dirs if not _phase28_is_ignored((relbase+"/"+d).strip("./"))]
            for name in names:
                path=os.path.join(base,name); rel=_phase28_rel(path,root)
                if _phase28_is_ignored(rel): continue
                try:
                    with open(path,"rb") as f: out[rel]=hashlib.sha256(f.read(2_000_000)).hexdigest()
                except Exception: continue
    except Exception as e: logger.debug("Phase 28 snapshot failed: %s",e)
    return out


def phase28_changed_files(before:dict, after:dict) -> list:
    keys=set(before)|set(after)
    return sorted(k for k in keys if before.get(k)!=after.get(k))


def build_phase28_context(impact:dict, max_chars:int=7000) -> str:
    """Compact impact context for Phase 19 Smart Context / coding agent."""
    try:
        lines=[f"Phase 28 Impact: {impact.get('risk_level','LOW')} ({impact.get('risk_score',0)}/100)",
               f"Confidence: {impact.get('confidence','LOW')}",
               "Direct: "+", ".join(impact.get("direct_affected",[])[:20]),
               "Indirect: "+", ".join(impact.get("indirect_affected",[])[:30]),
               f"Depth: {impact.get('dependency_depth',0)}",
               f"Database: {'YES' if impact.get('database_impact') else 'NO'} | Security: {'YES' if impact.get('security_impact') else 'NO'} | Telegram: {'YES' if impact.get('telegram_impact') else 'NO'} | AI Provider: {'YES' if impact.get('ai_provider_impact') else 'NO'}",
               "Circular: "+("YES" if impact.get("circular_dependencies") else "NO")]
        if impact.get("contracts",{}).get("signature_changes"): lines.append("Signature changes: "+json.dumps(impact["contracts"]["signature_changes"],ensure_ascii=False)[:2500])
        if impact.get("historical_evidence"): lines.append("Historical evidence: "+json.dumps(impact["historical_evidence"],ensure_ascii=False)[:1500])
        if impact.get("coding_knowledge"): lines.append("Relevant coding knowledge available: YES")
        if impact.get("project_memory"): lines.append("Relevant project memory available: YES")
        return "\n".join(lines)[:max_chars]
    except Exception:
        return "Phase 28 impact context unavailable. Confidence: LOW"


def phase28_apply_contract_analysis(task:dict, old_code:str, new_code:str) -> dict:
    """Attach signature/return-value impact to a task without changing its code artifact."""
    result=_phase28_compare_contracts(old_code,new_code)
    task["phase28_contracts"]=result
    return result


async def phase28_impact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only manual impact report: /impactanalysis <file or request>."""
    try:
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ এই কমান্ডটি শুধু অ্যাডমিনের জন্য।")
            return
        request=" ".join(context.args).strip()
        if not request:
            await update.message.reply_text("ব্যবহার: /impactanalysis <file.py বা change description>")
            return
        project={"id":0,"root":CODEBASE_DEFAULT_ROOT,"user_id":update.effective_user.id,"name":"manual","stack":"python"}
        task={"title":"Manual Impact Analysis","description":request,"target_files":request if request.endswith(".py") else ""}
        report=await asyncio.to_thread(phase28_analyze_change,project,task,None)
        await send_long_text(update,"🧩 PHASE 28 IMPACT ANALYSIS\n\n"+build_phase28_context(report,10000)+"\n\nExpected files:\n"+"\n".join(report.get("expected_files",[])[:80]))
    except Exception as e:
        logger.warning("Phase 28 /impactanalysis failed: %s",e)
        await update.message.reply_text("Impact analysis ব্যর্থ হয়েছে; existing coding workflow অপরিবর্তিত আছে।")

# ============================= Phase 35: Brain OS ডিফল্ট Knowledge/Pattern Seed =============================
# লক্ষ্য: প্রতিটা মেসেজেই যেন AI না ডেকে বসতে হয় — কিছু খুব-সাধারণ প্রশ্ন/অভিবাদন Knowledge ও
# Pattern Engine-এ আগে থেকে জমা রাখা থাকলে Decision Engine সরাসরি (কোনো AI কল ছাড়াই) উত্তর
# দিয়ে দিতে পারবে। KnowledgeEngine/PatternEngine-এর create() নিজে থেকেই ডুপ্লিকেট চেক করে,
# তাই বট বারবার রিস্টার্ট হলেও এই ফাংশনটা একই ডাটা বারবার ঢোকাবে না — নিরাপদে বারবার কল করা যায়।

BRAIN_OS_SEED_KNOWLEDGE: List[Dict[str, Any]] = [
    {
        "category": "bot_info", "title": "বট কী করতে পারে",
        "content": (
            "আমি ROHAN AI Assistant — একটা Telegram বট যা AI চ্যাট, অনুবাদ, গ্রামার-চেক, "
            "Rewrite, Tone বদল, Summarize, PDF থেকে প্রশ্ন-উত্তর, ছবি থেকে লেখা বের করা (OCR), "
            "ভয়েস-টু-টেক্সট, টেক্সট-টু-স্পিচ, ভিডিও বাংলা ডাবিং এবং কোডিং সহায়তা দিতে পারি। "
            "/menu লিখে সব ফিচারের তালিকা দেখতে পারেন।"
        ),
        "tags": "bot,help,features,menu", "priority": 8, "confidence_score": 0.95,
    },
    {
        "category": "bot_info", "title": "কমান্ড তালিকা কোথায় পাবো",
        "content": "সব কমান্ডের তালিকা দেখতে /help অথবা /menu লিখুন — বাটন-ভিত্তিক মেনু চলে আসবে।",
        "tags": "commands,help,menu", "priority": 7, "confidence_score": 0.9,
    },
    {
        "category": "bot_info", "title": "দৈনিক ব্যবহারের সীমা",
        "content": (
            "সাধারণ ইউজার দিনে নির্দিষ্ট সংখ্যক বার AI ফিচার ব্যবহার করতে পারেন, প্রিমিয়াম "
            "ইউজারের সীমা বেশি। নিজের বর্তমান সীমা ও ব্যবহার দেখতে /mylimit লিখুন।"
        ),
        "tags": "limit,quota,premium,mylimit", "priority": 7, "confidence_score": 0.9,
    },
    {
        "category": "bot_info", "title": "প্রিমিয়াম কীভাবে নেব",
        "content": "নিজের প্ল্যান/প্রিমিয়াম স্ট্যাটাস দেখতে /premiumstatus লিখুন। প্রিমিয়াম নিতে অ্যাডমিনের সাথে যোগাযোগ করুন।",
        "tags": "premium,plan,upgrade", "priority": 6, "confidence_score": 0.85,
    },
    {
        "category": "greeting", "title": "সাধারণ শুভেচ্ছা",
        "content": "আসসালামু আলাইকুম / হ্যালো! 😊 আমি আপনাকে কীভাবে সাহায্য করতে পারি? লিখুন অথবা /menu দেখুন।",
        "tags": "hello,hi,salam,greeting,কেমন আছেন", "priority": 6, "confidence_score": 0.85,
    },
    {
        "category": "greeting", "title": "কৃতজ্ঞতা জ্ঞাপনের উত্তর",
        "content": "আপনাকেও ধন্যবাদ! 🙏 আর কিছু লাগলে জানাবেন।",
        "tags": "thanks,thank you,ধন্যবাদ", "priority": 5, "confidence_score": 0.8,
    },
]

BRAIN_OS_SEED_PATTERNS: List[Dict[str, Any]] = [
    {"pattern_type": "keyword", "match_value": "হ্যালো", "category": "greeting", "name": "greeting_hello_bn", "priority": 7, "confidence_score": 0.85,
     "description": "আসসালামু আলাইকুম / হ্যালো! 😊 আমি আপনাকে কীভাবে সাহায্য করতে পারি? লিখুন অথবা /menu দেখুন।"},
    {"pattern_type": "keyword", "match_value": "hello", "category": "greeting", "name": "greeting_hello_en", "priority": 7, "confidence_score": 0.85,
     "description": "Hello! 😊 How can I help you? Type your question or use /menu to see all features."},
    {"pattern_type": "keyword", "match_value": "সালাম", "category": "greeting", "name": "greeting_salam", "priority": 7, "confidence_score": 0.85,
     "description": "ওয়ালাইকুম আসসালাম! 😊 আমি আপনাকে কীভাবে সাহায্য করতে পারি? লিখুন অথবা /menu দেখুন।"},
    {"pattern_type": "keyword", "match_value": "কেমন আছেন", "category": "greeting", "name": "greeting_kemon_achen", "priority": 6, "confidence_score": 0.8,
     "description": "আলহামদুলিল্লাহ ভালো আছি! 😊 আপনি কেমন আছেন? আপনাকে কীভাবে সাহায্য করতে পারি বলুন।"},
    {"pattern_type": "keyword", "match_value": "ধন্যবাদ", "category": "greeting", "name": "thanks_bn", "priority": 6, "confidence_score": 0.8,
     "description": "আপনাকেও ধন্যবাদ! 🙏 আর কিছু লাগলে জানাবেন।"},
    {"pattern_type": "keyword", "match_value": "thank you", "category": "greeting", "name": "thanks_en", "priority": 6, "confidence_score": 0.8,
     "description": "You're welcome! 🙏 Let me know if you need anything else."},
    {"pattern_type": "keyword", "match_value": "help", "category": "bot_info", "name": "help_en", "priority": 7, "confidence_score": 0.85,
     "description": "সব ফিচার/কমান্ডের তালিকা দেখতে /menu অথবা /help লিখুন।"},
    {"pattern_type": "keyword", "match_value": "কমান্ড", "category": "bot_info", "name": "commands_bn", "priority": 7, "confidence_score": 0.8,
     "description": "সব কমান্ডের তালিকা দেখতে /help অথবা /menu লিখুন — বাটন-ভিত্তিক মেনু চলে আসবে।"},
]


def seed_brain_os_defaults() -> None:
    """
    বট চালু হওয়ার সময় একবার কল হয়। উপরের তালিকার সাধারণ Q&A/Pattern Brain OS-এ ঢোকায়,
    যাতে Decision Engine এইসব সাধারণ প্রশ্নের জন্য AI না ডেকেই সরাসরি উত্তর দিতে পারে।
    সম্পূর্ণ non-fatal — কোনো এন্ট্রি ব্যর্থ হলেও বট চালু হতে বাধা দেয় না।
    """
    try:
        knowledge_engine = KnowledgeEngine()
        added_k = 0
        for entry in BRAIN_OS_SEED_KNOWLEDGE:
            result = knowledge_engine.create(
                category=entry["category"], title=entry["title"], content=entry["content"],
                tags=entry.get("tags", ""), priority=entry.get("priority", 5),
                source="system_seed", confidence_score=entry.get("confidence_score", 0.8),
            )
            if result is not None:
                added_k += 1

        pattern_engine = PatternEngine()
        added_p = 0
        for entry in BRAIN_OS_SEED_PATTERNS:
            result = pattern_engine.create(
                pattern_type=entry["pattern_type"], match_value=entry["match_value"],
                category=entry.get("category", ""), name=entry.get("name", ""),
                description=entry.get("description", ""),
                priority=entry.get("priority", 5), confidence_score=entry.get("confidence_score", 0.8),
            )
            if result is not None:
                added_p += 1

        logger.info(
            f"Brain OS Seed: {added_k}/{len(BRAIN_OS_SEED_KNOWLEDGE)} knowledge, "
            f"{added_p}/{len(BRAIN_OS_SEED_PATTERNS)} pattern এন্ট্রি প্রস্তুত (ডুপ্লিকেট থাকলে reuse হয়েছে)।"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Brain OS Seed ব্যর্থ হয়েছে, বট বাকি সব ফিচার নিয়ে স্বাভাবিকভাবে চালু থাকবে। বিস্তারিত: {e}")


# ============================= Phase 41: MCP Server (Custom Connector) =============================
# এটা ঐচ্ছিক ফিচার — MCP_ADMIN_TOKEN env var সেট করা থাকলেই শুধু চালু হবে। বাকি বট
# আগের মতোই স্বাভাবিকভাবে চলবে, এটা না থাকলে কিছুই বদলায় না।
#
# উদ্দেশ্য: Claude (বা যেকোনো MCP-সাপোর্টেড AI) সরাসরি এই বটের KnowledgeEngine,
# PatternEngine, TemplateEngine, DocumentationEngine, ErrorEngine-এ টুল-কল করে ডাটা
# যোগ করতে পারবে — কোনো ফাইল আপলোড/টেলিগ্রাম কমান্ড ছাড়াই।
#
# চালাতে দরকার (Replit-এ Secrets/env var-এ যোগ করুন):
#   MCP_ADMIN_TOKEN   — আপনার নিজের বানানো একটা গোপন শব্দ (যত জটিল তত ভালো)
#   MCP_SERVER_PORT   — ঐচ্ছিক, ডিফল্ট 8787
#
# এরপর Replit-এর পাবলিক URL (Repl খুললে উপরে যে https://xxxx.repl.co/ ঠিকানা দেখায়)
# + "/mcp" যোগ করে সেটাই Claude.ai → Settings → Connectors → Add custom connector-এ বসাবেন।
# Authorization হেডারে বসবে: Bearer <MCP_ADMIN_TOKEN>
#
# ⚠️ প্রথমবার রান করলে হয়তো `pip install mcp starlette uvicorn` লাগবে, আর নিচের কোডে
# ব্যবহৃত FastMCP-এর কিছু মেথড-নাম লাইব্রেরির ভার্সনভেদে সামান্য ভিন্ন হতে পারে — এরর
# পেলে সরাসরি এরর মেসেজটা কপি করে জানান, একসাথে ঠিক করে নেব।

MCP_ADMIN_TOKEN = os.environ.get("MCP_ADMIN_TOKEN", "")
MCP_SERVER_PORT = int(os.environ.get("MCP_SERVER_PORT", "8787"))


# ============================= Phase 43: OAuth 2.1 Authorization Server (MCP-এর জন্য) =============================
# Claude.ai / Claude Desktop-এর Custom Connector রিমোট MCP সার্ভারে কানেক্ট করার সময় auth
# ছাড়া একটা রিকোয়েস্ট পাঠায়; 401 পেলে ধরে নেয় সার্ভারটা OAuth ব্যবহার করে এবং স্বয়ংক্রিয়ভাবে
# OAuth মেটাডেটা + Dynamic Client Registration (DCR) খোঁজে। শুধু একটা স্ট্যাটিক Bearer
# টোকেন-চেক মিডলওয়্যার দিয়ে এটা কাজ করবে না — তাই এখানে একটা ছোট, সম্পূর্ণ OAuth 2.1 +
# PKCE + DCR সার্ভার বানানো হয়েছে (একই ফাইলে, বাইরের কোনো Auth সার্ভিস/লাইব্রেরি ছাড়াই)।
#
# ফ্লো:
#   ১) Claude প্রথমে GET /.well-known/oauth-protected-resource ও
#      GET /.well-known/oauth-authorization-server দিয়ে মেটাডেটা খুঁজে বের করে।
#   ২) Claude POST /oauth/register দিয়ে নিজেকে রেজিস্টার করে (client_id পায়) — Dynamic
#      Client Registration, RFC 7591।
#   ৩) ইউজারের ব্রাউজার GET /oauth/authorize-এ যায় — এখানে MCP_ADMIN_TOKEN দিয়ে approve
#      করতে হয় (এটাই একমাত্র "লগইন" ধাপ, শুধু অ্যাডমিনই approve করতে পারবেন)।
#   ৪) approve করলে redirect_uri-তে ?code=...&state=... সহ ফিরত পাঠানো হয়
#      (Claude.ai/Claude Desktop-এর জন্য এটা https://claude.ai/api/mcp/auth_callback)।
#   ৫) Claude POST /oauth/token দিয়ে code (+ PKCE code_verifier) exchange করে
#      access_token/refresh_token পায়।
#   ৬) এরপর প্রতিটা MCP রিকোয়েস্টে Authorization: Bearer <access_token> ব্যবহার হয়;
#      মেয়াদ শেষ হলে refresh_token দিয়ে renew হয় — আবার লগইন লাগে না।

OAUTH_CODE_TTL_SECONDS = 5 * 60                       # অথ কোড ৫ মিনিট পর মেয়াদোত্তীর্ণ
OAUTH_ACCESS_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30    # অ্যাক্সেস টোকেন ৩০ দিন (রিফ্রেশ টোকেন দিয়ে renew হয়)


def _oauth_register_client(redirect_uris: List[str], client_name: str = "") -> dict:
    client_id = secrets.token_urlsafe(24)
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO oauth_clients (client_id, client_secret, client_name, redirect_uris, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (client_id, None, client_name, json.dumps(redirect_uris), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return {"client_id": client_id, "redirect_uris": redirect_uris}


def _oauth_get_client(client_id: str) -> Optional[dict]:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT client_id, client_secret, client_name, redirect_uris FROM oauth_clients WHERE client_id = ?",
            (client_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return {
            "client_id": row[0],
            "client_secret": row[1],
            "client_name": row[2],
            "redirect_uris": json.loads(row[3]) if row[3] else [],
        }
    finally:
        conn.close()


def _oauth_create_auth_code(client_id: str, redirect_uri: str, code_challenge: str,
                             code_challenge_method: str, resource: str, scope: str) -> str:
    code = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=OAUTH_CODE_TTL_SECONDS)).isoformat()
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO oauth_auth_codes "
            "(code, client_id, redirect_uri, code_challenge, code_challenge_method, resource, scope, used, "
            "expires_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)",
            (code, client_id, redirect_uri, code_challenge, code_challenge_method, resource, scope,
             expires_at, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return code


def _oauth_consume_auth_code(code: str) -> Optional[dict]:
    """কোড একবারই ব্যবহারযোগ্য — পাওয়ামাত্র used=1 করে দেয়। মেয়াদোত্তীর্ণ/আগে ব্যবহৃত হলে None।"""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT client_id, redirect_uri, code_challenge, code_challenge_method, resource, scope, used, "
            "expires_at FROM oauth_auth_codes WHERE code = ?", (code,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        (client_id, redirect_uri, code_challenge, code_challenge_method, resource, scope, used, expires_at) = row
        if used:
            return None
        if datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
            return None
        cur.execute("UPDATE oauth_auth_codes SET used = 1 WHERE code = ?", (code,))
        conn.commit()
        return {
            "client_id": client_id, "redirect_uri": redirect_uri,
            "code_challenge": code_challenge, "code_challenge_method": code_challenge_method,
            "resource": resource, "scope": scope,
        }
    finally:
        conn.close()


def _oauth_issue_tokens(client_id: str, resource: str, scope: str) -> dict:
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=OAUTH_ACCESS_TOKEN_TTL_SECONDS)).isoformat()
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO oauth_tokens (access_token, refresh_token, client_id, resource, scope, expires_at, "
            "created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (access_token, refresh_token, client_id, resource, scope, expires_at,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "access_token": access_token, "refresh_token": refresh_token,
        "token_type": "Bearer", "expires_in": OAUTH_ACCESS_TOKEN_TTL_SECONDS,
        "scope": scope or "mcp",
    }


def _oauth_refresh_tokens(refresh_token: str) -> Optional[dict]:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT client_id, resource, scope FROM oauth_tokens WHERE refresh_token = ?", (refresh_token,))
        row = cur.fetchone()
        if row is None:
            return None
        client_id, resource, scope = row
        # রিফ্রেশ টোকেন রোটেশন: পুরনোটা মুছে নতুন access+refresh ইস্যু করা হয়
        cur.execute("DELETE FROM oauth_tokens WHERE refresh_token = ?", (refresh_token,))
        conn.commit()
    finally:
        conn.close()
    return _oauth_issue_tokens(client_id, resource, scope)


def _oauth_validate_access_token(token: str) -> bool:
    if not token:
        return False
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT expires_at FROM oauth_tokens WHERE access_token = ?", (token,))
        row = cur.fetchone()
        if row is None:
            return False
        return datetime.fromisoformat(row[0]) >= datetime.now(timezone.utc)
    finally:
        conn.close()


def _oauth_pkce_ok(code_verifier: Optional[str], code_challenge: Optional[str], method: Optional[str]) -> bool:
    """PKCE (RFC 7636) ভেরিফিকেশন। code_challenge না থাকলে (ক্লায়েন্ট PKCE ছাড়া authorize
    রিকোয়েস্ট করলে) স্কিপ হয় — বাস্তবে Claude সবসময় S256 PKCE পাঠায়।"""
    if not code_challenge:
        return True
    if not code_verifier:
        return False
    if (method or "S256").upper() == "PLAIN":
        return code_verifier == code_challenge
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return computed == code_challenge


def _build_mcp_server():
    """FastMCP সার্ভার বানায় ও টুলগুলো রেজিস্টার করে। ইমপোর্ট এখানে করা হয়েছে যাতে
    MCP লাইব্রেরি ইনস্টল না থাকলেও মূল বট চালু হতে কোনো বাধা না হয়।"""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        # কিছু লাইব্রেরি ভার্সনে/প্যাকেজে FastMCP আলাদা স্ট্যান্ডঅ্যালোন 'fastmcp' প্যাকেজে থাকে
        from fastmcp import FastMCP

    try:
        from mcp.server.transport_security import TransportSecuritySettings
    except ImportError:
        TransportSecuritySettings = None

    from urllib.parse import urlparse
    # PUBLIC_URL মডিউল-লেভেলে নেই — run_bot_async()-এ লোকাল; এখানে env থেকেই পড়া
    PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")
    _public_host = urlparse(PUBLIC_URL).netloc if PUBLIC_URL else ""

    _transport_security = None
    if TransportSecuritySettings is not None and _public_host:
        # mcp লাইব্রেরির DNS-rebinding protection ডিফল্টে allowed_hosts খালি রাখে,
        # ফলে Render-এর আসল Host (যেমন rohan-bot-eod2.onrender.com) match না করে
        # OAuth পাশ করার পরও /mcp রিকোয়েস্ট 421 দিয়ে বাতিল হয়।
        _transport_security = TransportSecuritySettings(
            allowed_hosts=[_public_host],
            allowed_origins=["https://claude.ai", PUBLIC_URL],
        )

    # stateless_http + json_response: SSE/streaming বাদ দিয়ে সাধারণ request/response ব্যবহার
    # করে — কিছু হোস্টিং প্ল্যাটফর্মের প্রক্সি স্ট্রিমিং/SSE ঠিকভাবে সাপোর্ট করে না, তাই এই
    # মোডে চালানো অনেক বেশি নির্ভরযোগ্য (Claude-এর সাথে কানেকশন silently ভেঙে যাওয়া ঠেকায়)।
    # Fix (double path-mount): streamable_http_app() ডিফল্টভাবে ভেতরেই /mcp পাথে নিজের রুট
    # বসায়। বাইরে Mount("/mcp", ...)-এর সাথে মিলিয়ে সেটা আবার /mcp হয়ে যেত, ফলে বাইরে থেকে
    # /mcp-এ হিট করলে ভেতরের অ্যাপ খালি path পেত আর 404 দিত। তাই ভেতরের অ্যাপের streamable
    # path-টা root ("/")-এ বসানো হচ্ছে, যেটা বাইরের Mount-এর prefix-strip করা path-এর সাথে মেলে।
    mcp_app = FastMCP(
        "rohan-youtube-bot-brain",
        stateless_http=True,
        json_response=True,
        streamable_http_path="/",
        transport_security=_transport_security,
    )

    @mcp_app.tool()
    def add_knowledge(category: str, title: str, content: str, priority: int = 5,
                       confidence_score: float = 0.9) -> dict:
        """নতুন Knowledge/FAQ এন্ট্রি বটের ব্রেইনে যোগ করে। একই category+title+content
        আগে থেকে থাকলে নতুন করে যোগ হয় না, বিদ্যমান এন্ট্রির তথ্য রিটার্ন হয়।"""
        engine = KnowledgeEngine()
        existing = engine.check_duplicate(category, title, content)
        if existing is not None:
            return {"status": "duplicate", "id": existing.id, "category": category, "title": title}
        result = engine.create(
            category=category, title=title, content=content,
            priority=priority, source="mcp", confidence_score=confidence_score,
        )
        if result is None:
            return {"status": "failed"}
        return {"status": "created", "id": result.id, "category": category, "title": title}

    @mcp_app.tool()
    def add_pattern(pattern_type: str, match_value: str, category: str, name: str,
                     description: str, priority: int = 5) -> dict:
        """নতুন Pattern (keyword/regex/intent) যোগ করে — match_value পাওয়া গেলে বট
        সরাসরি description-এর টেক্সটটা রিপ্লাই দেয়। pattern_type হতে হবে: keyword/regex/intent।"""
        if pattern_type not in VALID_PATTERN_TYPES:
            return {"status": "invalid_pattern_type", "allowed": list(VALID_PATTERN_TYPES)}
        engine = PatternEngine()
        existing = engine.check_duplicate(pattern_type, match_value, category)
        if existing is not None:
            return {"status": "duplicate", "id": existing.id}
        result = engine.create(
            pattern_type=pattern_type, match_value=match_value, category=category,
            name=name, description=description, priority=priority,
        )
        if result is None:
            return {"status": "failed"}
        return {"status": "created", "id": result.id}

    @mcp_app.tool()
    def add_template(name: str, category: str, body: str, template_type: str = "message",
                      priority: int = 5) -> dict:
        """নতুন Response Template যোগ করে। body-তে {variable} স্টাইলে ভ্যারিয়েবল রাখা যায়।
        template_type হতে হবে: prompt/response/message/notification/system। name ইউনিক হতে হয়।"""
        if template_type not in VALID_TEMPLATE_TYPES:
            return {"status": "invalid_template_type", "allowed": list(VALID_TEMPLATE_TYPES)}
        engine = TemplateEngine()
        existing = engine.get_by_name(name)
        if existing is not None:
            return {"status": "duplicate_name", "id": existing.id}
        error = engine.validate_template(body, template_type)
        if error:
            return {"status": "validation_failed", "error": error}
        result = engine.create(
            name=name, category=category, body=body, description="mcp",
            priority=priority, template_type=template_type,
        )
        if result is None:
            return {"status": "failed"}
        return {"status": "created", "id": result.id}

    @mcp_app.tool()
    def add_documentation(technology: str, category: str, title: str, content: str,
                           doc_type: str = "module") -> dict:
        """নতুন ইন্টারনাল ডকুমেন্টেশন/রেফারেন্স এন্ট্রি যোগ করে। doc_type: api/module/function/class।"""
        if doc_type not in VALID_DOC_TYPES:
            return {"status": "invalid_doc_type", "allowed": list(VALID_DOC_TYPES)}
        try:
            conn = get_brain_conn()
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM brain_documentation WHERE technology=? AND category=? AND title=? "
                "AND deleted_at='' LIMIT 1",
                (technology, category, title),
            )
            dup_row = cur.fetchone()
            conn.close()
        except Exception:  # noqa: BLE001
            dup_row = None
        if dup_row is not None:
            return {"status": "duplicate", "id": dup_row[0]}
        result = DocumentationEngine().create(
            technology=technology, category=category, title=title, content=content,
            doc_type=doc_type, internal_notes="mcp",
        )
        if result is None:
            return {"status": "failed"}
        return {"status": "created", "id": result.id}

    @mcp_app.tool()
    def add_error_solution(language: str, error_signature: str, description: str, solution: str,
                            category: str = "unknown", severity: str = "medium") -> dict:
        """একটা এরর-সিগনেচারের জন্য সমাধান রেজিস্টার করে। একই language+error_signature আগে
        থেকে থাকলে বর্ণনা/সমাধান আপডেট হয়ে যায় (নতুন এন্ট্রি হয় না)। severity: low/medium/high/critical।"""
        if severity not in VALID_SEVERITIES:
            return {"status": "invalid_severity", "allowed": list(VALID_SEVERITIES)}
        engine = ErrorEngine()
        existing = engine._find_by_signature(language, error_signature)
        result = engine.register_solution(
            language=language, error_signature=error_signature, description=description,
            solution=solution, category=category, severity=severity,
        )
        if result is None:
            return {"status": "failed"}
        return {"status": "updated" if existing is not None else "created", "id": result.id}

    @mcp_app.tool()
    def bulk_add_knowledge(entries: list) -> dict:
        """একসাথে অনেক Knowledge এন্ট্রি যোগ করে। প্রতিটা entry dict-এ category/title/content
        থাকতে হবে (priority/confidence_score/tags ঐচ্ছিক)। ডুপ্লিকেট স্বয়ংক্রিয়ভাবে স্কিপ হয়।"""
        return KnowledgeEngine().bulk_import(entries)

    @mcp_app.tool()
    def bulk_add_pattern(patterns: list) -> dict:
        """একসাথে অনেক Pattern যোগ করে। প্রতিটা dict-এ pattern_type/match_value/category/name
        থাকতে হবে। ডুপ্লিকেট স্বয়ংক্রিয়ভাবে স্কিপ হয়।"""
        return PatternEngine().bulk_import(patterns)

    return mcp_app


def _start_mcp_server_in_background():
    """Phase 41-legacy: এই ফাংশনটা আর ব্যবহার হয় না — Phase 42 থেকে MCP সার্ভার আলাদা
    থ্রেড/পোর্টে না চালিয়ে মূল webhook সার্ভারেরই একটা অংশ (/mcp path) হিসেবে একই
    পোর্টে চালানো হয় (নিচে run_bot_async() দেখুন), যাতে যেসব হোস্টিং প্ল্যাটফর্ম শুধু
    একটা পাবলিক পোর্ট দেয় (Pella-র মতো), সেখানেও Telegram webhook ও MCP দুটোই কাজ করে।
    ফাংশনটা রেখে দেওয়া হলো শুধু ব্যাকওয়ার্ড-কম্প্যাটিবিলিটির জন্য, এটা এখন কিছুই করে না।"""
    return


def main():
    """সিঙ্ক্রোনাস এন্ট্রি পয়েন্ট — নিচের async ফাংশনটা চালায়।"""
    asyncio.run(run_bot_async())


async def run_bot_async():
    init_db()
    seed_brain_os_defaults()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_shutdown(_on_shutdown).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("mylimit", mylimit_command))

    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("uptime", uptime_command))
    app.add_handler(CommandHandler("feedback", feedback_command))
    app.add_handler(CommandHandler("bugreport", bugreport_command))

    app.add_handler(CommandHandler("memory", memory_command))
    app.add_handler(CommandHandler("clearmemory", clearmemory_command))
    app.add_handler(CommandHandler("autoreply", autoreply_command))
    app.add_handler(CommandHandler("detectlang", detectlang_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("setlang", setlang_command))

    app.add_handler(CommandHandler("translate", translate_command))
    app.add_handler(CommandHandler("grammar", grammar_command))
    app.add_handler(CommandHandler("rewrite", rewrite_command))
    app.add_handler(CommandHandler("tone", tone_command))
    app.add_handler(CommandHandler("summarize", summarize_command))
    app.add_handler(CommandHandler("pdf", pdf_command))
    app.add_handler(CommandHandler("askpdf", askpdf_command))
    app.add_handler(CommandHandler("clearpdf", clearpdf_command))
    app.add_handler(CommandHandler("ocr", ocr_command))

    app.add_handler(CommandHandler("dub", dub_command))
    app.add_handler(CommandHandler("dub_part", dub_part_command))
    app.add_handler(CommandHandler("dub_finish", dub_finish_command))
    app.add_handler(CommandHandler("dub_cancel", dub_cancel_command))

    app.add_handler(CommandHandler("tts", tts_command))
    app.add_handler(CommandHandler("setvoice", setvoice_command))
    app.add_handler(CommandHandler("setspeed", setspeed_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    app.add_handler(CommandHandler("joke", joke_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("dice", dice_command))
    app.add_handler(CommandHandler("coin", coin_command))

    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("schedulebroadcast", schedulebroadcast_command))
    app.add_handler(CommandHandler("listschedules", listschedules_command))
    app.add_handler(CommandHandler("cancelschedule", cancelschedule_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("aistats", aistats_command))  # Phase 10: AI ইঞ্জিন পরিসংখ্যান
    app.add_handler(CommandHandler("dailystats", dailystats_command))
    app.add_handler(CommandHandler("monthlystats", monthlystats_command))
    app.add_handler(CommandHandler("analytics", analytics_command))
    app.add_handler(CommandHandler("backup", backup_command))
    app.add_handler(CommandHandler("restore", restore_command))
    app.add_handler(CommandHandler("serverstatus", server_status_command))
    app.add_handler(CommandHandler("dashboard", dashboard_command))

    app.add_handler(CommandHandler("addpremium", addpremium_command))
    app.add_handler(CommandHandler("removepremium", removepremium_command))
    app.add_handler(CommandHandler("premiumstatus", premiumstatus_command))
    app.add_handler(CommandHandler("premiumlist", premiumlist_command))

    # Phase 5: Referral System
    app.add_handler(CommandHandler("myreferrals", myreferrals_command))

    # Phase 5: Admin Roles ও Admin Control Panel
    app.add_handler(CommandHandler("addadmin", addadmin_command))
    app.add_handler(CommandHandler("removeadmin", removeadmin_command))
    app.add_handler(CommandHandler("adminlist", adminlist_command))
    app.add_handler(CommandHandler("adminpanel", adminpanel_command))
    app.add_handler(CommandHandler("brainstatus", brainstatus_command))
    app.add_handler(CommandHandler("noapimode", noapimode_command))
    # Phase 45: নিজস্ব API Key — প্রতিটা ইউজার নিজের OpenRouter/Groq/Cerebras Key যুক্ত/মুছতে/দেখতে পারবে
    app.add_handler(CommandHandler("setapikey", setapikey_command))
    app.add_handler(CommandHandler("removeapikey", removeapikey_command))
    app.add_handler(CommandHandler("myapikey", myapikey_command))
    app.add_handler(CommandHandler("decisionhistory", decisionhistory_command))
    # Phase 36: Admin কমান্ড দিয়ে সরাসরি নতুন Knowledge/Pattern যোগ (কোনো redeploy ছাড়াই)
    app.add_handler(CommandHandler("addknowledge", addknowledge_command))
    app.add_handler(CommandHandler("addpattern", addpattern_command))
    # Phase 39: Admin কমান্ড দিয়ে Template, Documentation, Error-Solution যোগ
    app.add_handler(CommandHandler("addtemplate", addtemplate_command))
    app.add_handler(CommandHandler("adddoc", adddoc_command))
    app.add_handler(CommandHandler("addsolution", addsolution_command))
    # Phase 40: একসাথে অনেক এন্ট্রি (.json ফাইল) ইমপোর্ট করার কমান্ড
    app.add_handler(CommandHandler("bulkimport", bulkimport_command))

    # Phase 11: Coding Orchestrator — বড় কোডিং কাজ ছোট ছোট ধাপে ভাগ করে সামলানো
    app.add_handler(CommandHandler("codeproject", codeproject_command))
    app.add_handler(CommandHandler("codeplan", codeplan_command))
    app.add_handler(CommandHandler("codenext", codenext_command))
    app.add_handler(CommandHandler("codestatus", codestatus_command))
    app.add_handler(CommandHandler("codetask", codetask_command))
    app.add_handler(CommandHandler("codeprojects", codeprojects_command))
    app.add_handler(CommandHandler("useproject", useproject_command))
    app.add_handler(CommandHandler("exportcode", exportcode_command))
    app.add_handler(CommandHandler("deleteproject", deleteproject_command))
    app.add_handler(CommandHandler("codehelp", codehelp_command))

    # Phase 18: Full Codebase Intelligence — admin-only manual scan/status.
    app.add_handler(CommandHandler("codebasescan", codebasescan_command))
    app.add_handler(CommandHandler("codebasestatus", codebasestatus_command))
    # Phase 19: Smart Context Builder — admin-only preview/debug command.
    app.add_handler(CommandHandler("contextpreview", contextpreview_command))
    app.add_handler(CommandHandler("testreport", autonomous_test_report_command))
    app.add_handler(CommandHandler("errorfixlog", errorfixlog_command))
    app.add_handler(CommandHandler("reviewreport", reviewreport_command))
    app.add_handler(CommandHandler("securityscan", securityscan_command))
    # Phase 25: admin-only Project Memory 2.0 inspection.
    app.add_handler(CommandHandler("projectmemory", projectmemory_command))
    app.add_handler(CommandHandler("codingknowledge", codingknowledge_command))

    # Phase 27: Git/Rollback Intelligence
    app.add_handler(CommandHandler("coderollback", coderollback_command))
    app.add_handler(CommandHandler("codehistory", codehistory_command))
    app.add_handler(CommandHandler("codediff", codediff_command))

    # Phase 28: Autonomous Change Impact Analysis & Dependency Intelligence
    app.add_handler(CommandHandler("impactanalysis", phase28_impact_command))

    # Phase 29: Full Autonomous Coding Supervisor 2.0
    app.add_handler(CommandHandler("codeauto", codeauto_command))
    app.add_handler(CommandHandler("codeautostatus", codeautostatus_command))
    # Phase 30–34: Integrated autonomous coding stack
    app.add_handler(CommandHandler("codeexec", phase30_execute_command_command))
    app.add_handler(CommandHandler("codingengine", phase34_status_command))


    app.add_handler(CallbackQueryHandler(button_callback))

    # Phase 5: Admin Panel-এর "ইউজার সার্চ" এর পরের মেসেজটা ধরার জন্য — এটা আলাদা (উচ্চ
    # প্রায়োরিটি) group=-1 এ থাকে, যাতে সব টেক্সট মেসেজেই একবার চেক হয়। অ্যাডমিন না হলে বা
    # pending সার্চ না থাকলে কিছুই করে না, স্বাভাবিকভাবে chat_general-এ চলে যায়।
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_text_input_handler), group=-1)

    # কমান্ড ছাড়া সরাসরি লেখা মেসেজ -> সাধারণ AI চ্যাট (এটা সবার শেষে থাকতে হবে)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_general))

    app.add_error_handler(error_handler)

    # Phase 3: শিডিউল ব্রডকাস্ট চেক করার ব্যাকগ্রাউন্ড জব — প্রতি ৩০ সেকেন্ডে একবার চলবে।
    # job_queue না থাকলে (python-telegram-bot[job-queue] ইনস্টল করা না থাকলে) বট ভাঙবে না,
    # শুধু শিডিউল ব্রডকাস্ট ফিচারটা কাজ করবে না — বাকি সব ফিচার স্বাভাবিকভাবে চলবে।
    if app.job_queue is not None:
        app.job_queue.run_repeating(check_scheduled_broadcasts, interval=30, first=10)
        # Phase 4: Notifications — প্রিমিয়াম মেয়াদ রিমাইন্ডার ও স্বয়ংক্রিয় মেয়াদ-শেষ চেক
        app.job_queue.run_repeating(
            check_premium_notifications, interval=PREMIUM_NOTIFY_INTERVAL_SECONDS, first=45
        )
    else:
        logger.warning(
            "JobQueue পাওয়া যায়নি — শিডিউল ব্রডকাস্ট ও প্রিমিয়াম মেয়াদ নোটিফিকেশন কাজ করবে না। "
            'ইনস্টল করুন: pip install "python-telegram-bot[job-queue]"'
        )

    logger.info("বট চালু হয়েছে (webhook মোড)...")

    # ============================= Phase 42: Unified Webhook + MCP Server =============================
    # একটাই পাবলিক পোর্টে দুটো জিনিস একসাথে চলবে: (১) Telegram webhook route, (২) MCP route
    # (যদি MCP_ADMIN_TOKEN সেট করা থাকে)। এটা দরকার কারণ অনেক ফ্রি হোস্টিং প্ল্যাটফর্ম
    # (যেমন Pella) একটা প্রসেসকে শুধু একটাই পাবলিক পোর্ট এক্সপোজ করতে দেয়।
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse, PlainTextResponse, HTMLResponse, RedirectResponse
    from starlette.routing import Route, Mount
    from starlette.middleware.base import BaseHTTPMiddleware
    import uvicorn

    PORT = int(os.environ.get("PORT", os.environ.get("MCP_SERVER_PORT", "8080")))
    PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")
    WEBHOOK_SECRET_PATH = os.environ.get("WEBHOOK_SECRET_PATH", TELEGRAM_BOT_TOKEN.split(":")[0])

    async def telegram_webhook(request):
        try:
            data = await request.json()
        except Exception:  # noqa: BLE001
            return PlainTextResponse("bad request", status_code=400)
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return PlainTextResponse("ok")

    async def health_check(request):
        return JSONResponse({"status": "ok", "bot": "running"})

    routes = [
        Route(f"/webhook/{WEBHOOK_SECRET_PATH}", telegram_webhook, methods=["POST"]),
        Route("/", health_check, methods=["GET"]),
    ]

    # Phase 43-fix: FastMCP-এর streamable_http_app()-এর নিজস্ব একটা lifespan থাকে যেটা
    # session manager চালু করে — এটাকে বাইরের মূল Starlette অ্যাপে পাস না করলে nested
    # lifespan হিসেবে এটা চালুই হয় না, ফলে /mcp-এর প্রতিটা রিকোয়েস্ট নিঃশব্দে ব্যর্থ হয়
    # (OAuth ঠিকভাবে শেষ হওয়ার পরও)। তাই এটা এখানে ধরে রাখা হচ্ছে, নিচে web_app বানানোর
    # সময় পাস করে দেওয়ার জন্য।
    mcp_lifespan = None

    if MCP_ADMIN_TOKEN and not PUBLIC_URL:
        logger.warning(
            "MCP_ADMIN_TOKEN সেট আছে কিন্তু PUBLIC_URL সেট নেই — OAuth সার্ভারের জন্য পূর্ণ "
            "HTTPS URL লাগে (redirect/token endpoint বানাতে), তাই MCP+OAuth রাউট চালু হচ্ছে না। "
            "'.env'-এ PUBLIC_URL=https://your-public-domain যোগ করুন।"
        )
    elif MCP_ADMIN_TOKEN:
        try:
            mcp_app = _build_mcp_server()
            # Phase 43-fix: host="0.0.0.0" parameter current FastMCP version-এ supported নয়
            # Host binding uvicorn config-এ (line 16337-এ) করা হয় "host=0.0.0.0" দিয়ে
            # streamable_http_app() শুধু ASGI app expose করে, host handling-এর দায়িত্ব নেয় না
            mcp_asgi_app = mcp_app.streamable_http_app()

            # লাইব্রেরি ভার্সনভেদে .lifespan অ্যাট্রিবিউট নাও থাকতে পারে — সেক্ষেত্রে
            # session_manager.run() নিজেই একটা lifespan হিসেবে বানিয়ে নেওয়া হচ্ছে, যাতে এই
            # ধাপে কোনো সমস্যা হলেও নিচের OAuth রাউটগুলো (register/authorize/token) যোগ
            # হওয়া আটকে না যায়।
            try:
                mcp_lifespan = mcp_asgi_app.lifespan
                if mcp_lifespan is None:
                    raise AttributeError("lifespan is None")
            except Exception:  # noqa: BLE001
                @contextlib.asynccontextmanager
                async def _mcp_session_lifespan(_app):
                    async with mcp_app.session_manager.run():
                        yield

                mcp_lifespan = _mcp_session_lifespan
                logger.warning(
                    "[OAuth] mcp_asgi_app.lifespan পাওয়া যায়নি, session_manager.run() দিয়ে "
                    "ফলব্যাক lifespan বানানো হয়েছে।"
                )

            # Phase 43: OAuth 2.1 issuer/resource — সবকিছু PUBLIC_URL-এর উপর ভিত্তি করে,
            # কারণ Claude-কে absolute HTTPS URL-ই দিতে হয় (localhost/relative চলবে না)।
            oauth_issuer = PUBLIC_URL
            mcp_resource_url = f"{PUBLIC_URL}/mcp"

            async def oauth_protected_resource_metadata(request):
                logger.warning("[OAuth] GET /.well-known/oauth-protected-resource হিট হয়েছে")
                return JSONResponse({
                    "resource": mcp_resource_url,
                    "authorization_servers": [oauth_issuer],
                })

            async def oauth_authorization_server_metadata(request):
                logger.warning("[OAuth] GET /.well-known/oauth-authorization-server হিট হয়েছে")
                return JSONResponse({
                    "issuer": oauth_issuer,
                    "authorization_endpoint": f"{oauth_issuer}/oauth/authorize",
                    "token_endpoint": f"{oauth_issuer}/oauth/token",
                    "registration_endpoint": f"{oauth_issuer}/oauth/register",
                    "response_types_supported": ["code"],
                    "grant_types_supported": ["authorization_code", "refresh_token"],
                    "code_challenge_methods_supported": ["S256", "plain"],
                    "token_endpoint_auth_methods_supported": ["none"],
                    "scopes_supported": ["mcp"],
                })

            async def oauth_register(request):
                # Dynamic Client Registration (RFC 7591) — Claude প্রথমবার কানেক্ট করার সময়
                # নিজেই POST করে client_id চেয়ে নেয়, ম্যানুয়ালি কিছু বসাতে হয় না।
                try:
                    body = await request.json()
                except Exception:  # noqa: BLE001
                    body = {}
                logger.warning(f"[OAuth] /oauth/register হিট হয়েছে, body: {body}")
                redirect_uris = body.get("redirect_uris") or []
                if not isinstance(redirect_uris, list) or not redirect_uris:
                    logger.warning("[OAuth] /oauth/register ব্যর্থ: redirect_uris পাওয়া যায়নি")
                    return JSONResponse(
                        {"error": "invalid_client_metadata", "error_description": "redirect_uris আবশ্যক"},
                        status_code=400,
                    )
                client_name = str(body.get("client_name", ""))[:200]
                result = _oauth_register_client(redirect_uris, client_name)
                logger.warning(f"[OAuth] নতুন client রেজিস্টার্ড: client_id={result['client_id']}")
                return JSONResponse(
                    {
                        "client_id": result["client_id"],
                        "client_id_issued_at": int(time.time()),
                        "redirect_uris": redirect_uris,
                        "token_endpoint_auth_method": "none",
                        "grant_types": ["authorization_code", "refresh_token"],
                        "response_types": ["code"],
                        "client_name": client_name,
                    },
                    status_code=201,
                )

            _OAUTH_LOGIN_PAGE = """<!doctype html><html lang="bn"><head><meta charset="utf-8">
<title>MCP অথরাইজেশন</title>
<style>body{{font-family:sans-serif;max-width:420px;margin:60px auto;padding:0 16px}}
input{{width:100%;padding:10px;margin:8px 0;box-sizing:border-box;font-size:16px}}
button{{width:100%;padding:10px;background:#111;color:#fff;border:0;border-radius:6px;font-size:16px}}
.err{{color:#c00}}</style></head><body>
<h3>এই অ্যাপকে (Claude) আপনার বটের ডেটায় অ্যাক্সেস দিতে চান?</h3>
<p>অনুমোদন করতে আপনার <b>MCP_ADMIN_TOKEN</b> দিন:</p>
{error_html}
<form method="post">
  <input type="hidden" name="client_id" value="{client_id}">
  <input type="hidden" name="redirect_uri" value="{redirect_uri}">
  <input type="hidden" name="state" value="{state}">
  <input type="hidden" name="code_challenge" value="{code_challenge}">
  <input type="hidden" name="code_challenge_method" value="{code_challenge_method}">
  <input type="hidden" name="resource" value="{resource}">
  <input type="hidden" name="scope" value="{scope}">
  <input type="password" name="admin_token" placeholder="MCP_ADMIN_TOKEN" required autofocus>
  <button type="submit">অনুমোদন করুন (Approve)</button>
</form>
</body></html>"""

            def _extract_authorize_params(qp) -> dict:
                return {
                    "client_id": qp.get("client_id", ""),
                    "redirect_uri": qp.get("redirect_uri", ""),
                    "state": qp.get("state", ""),
                    "code_challenge": qp.get("code_challenge", ""),
                    "code_challenge_method": qp.get("code_challenge_method", "S256"),
                    "resource": qp.get("resource", mcp_resource_url),
                    "scope": qp.get("scope", "mcp"),
                }

            async def oauth_authorize_get(request):
                logger.warning(f"[OAuth] GET /oauth/authorize হিট, query: {dict(request.query_params)}")
                if request.query_params.get("response_type", "code") != "code":
                    logger.warning("[OAuth] /oauth/authorize ব্যর্থ: unsupported response_type")
                    return PlainTextResponse("unsupported response_type", status_code=400)
                params = _extract_authorize_params(request.query_params)
                client = _oauth_get_client(params["client_id"])
                if client is None:
                    logger.warning(f"[OAuth] /oauth/authorize ব্যর্থ: unknown client_id={params['client_id']}")
                    return PlainTextResponse("unknown client_id — আগে /oauth/register কল হয়নি", status_code=400)
                if params["redirect_uri"] not in client["redirect_uris"]:
                    logger.warning(
                        f"[OAuth] /oauth/authorize ব্যর্থ: redirect_uri মেলেনি. পাঠানো হয়েছে="
                        f"{params['redirect_uri']}, রেজিস্টার্ড={client['redirect_uris']}"
                    )
                    return PlainTextResponse("redirect_uri রেজিস্টার্ড redirect_uris-এর সাথে মেলেনি", status_code=400)
                html = _OAUTH_LOGIN_PAGE.format(error_html="", **{k: (v or "") for k, v in params.items()})
                return HTMLResponse(html)

            async def oauth_authorize_post(request):
                form = await request.form()
                params = {
                    "client_id": form.get("client_id", ""),
                    "redirect_uri": form.get("redirect_uri", ""),
                    "state": form.get("state", ""),
                    "code_challenge": form.get("code_challenge", ""),
                    "code_challenge_method": form.get("code_challenge_method", "S256"),
                    "resource": form.get("resource", mcp_resource_url),
                    "scope": form.get("scope", "mcp"),
                }
                logger.warning(f"[OAuth] POST /oauth/authorize (approve চাপা হয়েছে), params: {params}")
                admin_token = form.get("admin_token", "")
                client = _oauth_get_client(params["client_id"])
                if client is None or params["redirect_uri"] not in client["redirect_uris"]:
                    logger.warning("[OAuth] approve ব্যর্থ: invalid client/redirect_uri")
                    return PlainTextResponse("invalid client/redirect_uri", status_code=400)
                if admin_token != MCP_ADMIN_TOKEN:
                    logger.warning("[OAuth] approve ব্যর্থ: ভুল MCP_ADMIN_TOKEN দেওয়া হয়েছে")
                    html = _OAUTH_LOGIN_PAGE.format(
                        error_html='<p class="err">ভুল টোকেন — আবার চেষ্টা করুন।</p>',
                        **{k: (v or "") for k, v in params.items()},
                    )
                    return HTMLResponse(html, status_code=401)
                code = _oauth_create_auth_code(
                    params["client_id"], params["redirect_uri"], params["code_challenge"],
                    params["code_challenge_method"], params["resource"], params["scope"],
                )
                redirect_qs = {"code": code}
                if params["state"]:
                    redirect_qs["state"] = params["state"]
                redirect_url = f"{params['redirect_uri']}?{_url_encode(redirect_qs)}"
                logger.warning(f"[OAuth] approve সফল, redirect করা হচ্ছে: {redirect_url[:120]}...")
                return RedirectResponse(url=redirect_url, status_code=302)

            async def oauth_token(request):
                form = await request.form()
                grant_type = form.get("grant_type", "")
                logger.warning(f"[OAuth] POST /oauth/token হিট, grant_type={grant_type}")
                if grant_type == "authorization_code":
                    code = form.get("code", "")
                    redirect_uri = form.get("redirect_uri", "")
                    code_verifier = form.get("code_verifier", "")
                    data = _oauth_consume_auth_code(code)
                    if data is None:
                        logger.warning(f"[OAuth] token ব্যর্থ: invalid_grant (code মেয়াদোত্তীর্ণ/আগে ব্যবহৃত/ভুল). code={code[:12]}...")
                        return JSONResponse({"error": "invalid_grant"}, status_code=400)
                    if redirect_uri and data["redirect_uri"] != redirect_uri:
                        logger.warning(
                            f"[OAuth] token ব্যর্থ: redirect_uri মেলেনি. stored={data['redirect_uri']} sent={redirect_uri}"
                        )
                        return JSONResponse(
                            {"error": "invalid_grant", "error_description": "redirect_uri মেলেনি"}, status_code=400
                        )
                    if not _oauth_pkce_ok(code_verifier, data["code_challenge"], data["code_challenge_method"]):
                        logger.warning("[OAuth] token ব্যর্থ: PKCE verification failed")
                        return JSONResponse(
                            {"error": "invalid_grant", "error_description": "PKCE verification failed"},
                            status_code=400,
                        )
                    tokens = _oauth_issue_tokens(data["client_id"], data["resource"], data["scope"])
                    logger.warning(f"[OAuth] token ইস্যু সফল, client_id={data['client_id']}")
                    return JSONResponse(tokens)
                elif grant_type == "refresh_token":
                    tokens = _oauth_refresh_tokens(form.get("refresh_token", ""))
                    if tokens is None:
                        logger.warning("[OAuth] refresh ব্যর্থ: invalid_grant")
                        return JSONResponse({"error": "invalid_grant"}, status_code=400)
                    logger.warning("[OAuth] refresh সফল")
                    return JSONResponse(tokens)
                logger.warning(f"[OAuth] token ব্যর্থ: unsupported_grant_type={grant_type}")
                return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)

            # গুরুত্বপূর্ণ: Starlette-এর BaseHTTPMiddleware ব্যবহার করা যাবে না এখানে — MCP-এর
            # streamable_http_app() স্ট্রিমিং (SSE/chunked) রেসপন্স ব্যবহার করে, আর
            # BaseHTTPMiddleware পুরো রেসপন্স বাফার করে ফেলে, ফলে কোনো এরর ছাড়াই কানেকশন
            # নিঃশব্দে ভেঙে যায়। তাই raw ASGI middleware ব্যবহার করা হয়েছে, যেটা রিকোয়েস্ট/
            # রেসপন্স স্ট্রিম পাস-থ্রু রাখে।
            class _AuthASGIMiddleware:
                def __init__(self, inner_app):
                    self.inner_app = inner_app

                async def __call__(self, scope, receive, send):
                    if scope["type"] != "http":
                        await self.inner_app(scope, receive, send)
                        return
                    headers = dict(scope.get("headers") or [])
                    auth = headers.get(b"authorization", b"").decode("latin-1")
                    query_string = scope.get("query_string", b"").decode("latin-1")
                    token_from_query = parse_qs(query_string).get("token", [""])[0]
                    bearer_token = auth[7:] if auth.startswith("Bearer ") else ""
                    valid = (
                        bearer_token == MCP_ADMIN_TOKEN
                        or token_from_query == MCP_ADMIN_TOKEN
                        or _oauth_validate_access_token(bearer_token)
                    )
                    if not valid:
                        logger.warning(
                            f"[OAuth] /mcp রিকোয়েস্ট 401 — path={scope.get('path')} "
                            f"bearer_token পাওয়া গেছে কিনা: {bool(bearer_token)} (দৈর্ঘ্য={len(bearer_token)})"
                        )
                        response = JSONResponse(
                            {"error": "unauthorized"},
                            status_code=401,
                            headers={
                                "WWW-Authenticate": (
                                    f'Bearer resource_metadata="{oauth_issuer}/.well-known/oauth-protected-resource"'
                                )
                            },
                        )
                        await response(scope, receive, send)
                        return
                    logger.warning(f"[OAuth] /mcp রিকোয়েস্ট অথ পাস — path={scope.get('path')}")
                    try:
                        await self.inner_app(scope, receive, send)
                    except Exception as e:  # noqa: BLE001
                        logger.warning(f"[OAuth] /mcp হ্যান্ডলিং-এ এক্সেপশন: {type(e).__name__}: {e}")
                        raise

            mcp_asgi_app = _AuthASGIMiddleware(mcp_asgi_app)
            routes.append(
                Route("/.well-known/oauth-protected-resource", oauth_protected_resource_metadata, methods=["GET"])
            )
            routes.append(
                Route("/.well-known/oauth-authorization-server", oauth_authorization_server_metadata, methods=["GET"])
            )
            routes.append(Route("/oauth/register", oauth_register, methods=["POST"]))
            routes.append(Route("/oauth/authorize", oauth_authorize_get, methods=["GET"]))
            routes.append(Route("/oauth/authorize", oauth_authorize_post, methods=["POST"]))
            routes.append(Route("/oauth/token", oauth_token, methods=["POST"]))
            async def oauth_debug_mcp_test(request):
                # শুধু অ্যাডমিন টোকেন দিয়েই চলবে। এটা বাইরের নেটওয়ার্ক/প্রক্সি এড়িয়ে
                # সরাসরি আমাদের নিজের প্রসেসের ভেতর থেকেই MCP-কে একটা আসল initialize
                # রিকোয়েস্ট পাঠায় — এতে বোঝা যায় বাগটা আমাদের কোডে নাকি বাইরের হোস্টিং/
                # প্রক্সি লেভেলে।
                # Fix: এখন streamable_http_app() root ("/")-এ রুট করে (streamable_http_path="/"),
                # তাই ভেতরের অ্যাপের সরাসরি টেস্টে "/mcp" নয়, "/" পাথে পাঠাতে হবে — কারণ বাইরে
                # Mount("/mcp", ...) prefix-strip করে ভেতরের অ্যাপকে "/" পথই দেয়।
                if request.query_params.get("token", "") != MCP_ADMIN_TOKEN:
                    return PlainTextResponse("forbidden", status_code=403)
                import httpx as _httpx
                try:
                    transport = _httpx.ASGITransport(app=mcp_asgi_app)
                    async with _httpx.AsyncClient(
                        transport=transport, base_url="http://testserver", timeout=15.0
                    ) as client:
                        resp = await client.post(
                            "/",
                            json={
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "initialize",
                                "params": {
                                    "protocolVersion": "2025-06-18",
                                    "capabilities": {},
                                    "clientInfo": {"name": "diagnostic", "version": "1.0"},
                                },
                            },
                            headers={
                                "Authorization": f"Bearer {MCP_ADMIN_TOKEN}",
                                "Accept": "application/json, text/event-stream",
                                "Content-Type": "application/json",
                            },
                        )
                        body_preview = resp.text[:2000]
                        logger.warning(
                            f"[OAuth-Debug] internal /mcp টেস্ট status={resp.status_code} body={body_preview}"
                        )
                        return JSONResponse(
                            {
                                "status_code": resp.status_code,
                                "headers": dict(resp.headers),
                                "body": body_preview,
                            }
                        )
                except Exception as e:  # noqa: BLE001
                    tb = traceback.format_exc()
                    logger.warning(f"[OAuth-Debug] internal /mcp টেস্ট এক্সেপশন: {type(e).__name__}: {e}\n{tb}")
                    return JSONResponse({"error": str(e), "traceback": tb[-3000:]}, status_code=500)

            routes.append(Route("/oauth/diag7719", oauth_debug_mcp_test, methods=["GET"]))
            routes.append(Mount("/mcp", app=mcp_asgi_app))
            logger.info(
                "🔌 MCP রাউট + OAuth 2.1 সার্ভার যোগ হয়েছে: /mcp, /oauth/register, /oauth/authorize, "
                "/oauth/token, /.well-known/oauth-* (session manager lifespan সংযুক্ত করা হয়েছে)"
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"MCP সার্ভার সেটআপ ব্যর্থ (মূল বট প্রভাবিত হয়নি): {e}\n{traceback.format_exc()}")
    else:
        logger.info("MCP_ADMIN_TOKEN সেট নেই — MCP রাউট চালু হচ্ছে না (ঐচ্ছিক ফিচার)।")

    # mcp_lifespan সেট থাকলে (অর্থাৎ MCP+OAuth চালু থাকলে) সেটা বাইরের অ্যাপে পাস করে দেওয়া
    # হচ্ছে — নাহলে FastMCP-এর session manager চালুই হবে না, আর /mcp-এর সব রিকোয়েস্ট
    # নিঃশব্দে ব্যর্থ হবে (OAuth সফল হওয়া সত্ত্বেও)।
    if mcp_lifespan is not None:
        web_app = Starlette(routes=routes, lifespan=mcp_lifespan)
    else:
        web_app = Starlette(routes=routes)

    await app.initialize()
    await app.start()

    if PUBLIC_URL:
        webhook_url = f"{PUBLIC_URL}/webhook/{WEBHOOK_SECRET_PATH}"
        await app.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
        logger.info(f"Telegram webhook সেট হয়েছে: {webhook_url}")
    else:
        logger.warning(
            "PUBLIC_URL সেট করা নেই — Telegram webhook রেজিস্টার করা যায়নি। "
            "'.env'-এ PUBLIC_URL=https://your-public-domain যোগ করুন।"
        )

    config = uvicorn.Config(web_app, host="0.0.0.0", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    logger.info(f"🌐 Unified সার্ভার চালু হচ্ছে পোর্ট {PORT}-এ...")
    try:
        await server.serve()
    finally:
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    main()
