"""Phase 47: Data Source Attribution — উত্তরের তথ্য কোথা থেকে এলো তার ট্র্যাকিং।

Rohan-bot-এর প্রতিটা তথ্যবহ উত্তরের সাথে একটা **source badge** যুক্ত হয়, যাতে ইউজার
স্পষ্ট দেখতে পায় উত্তরটা এসেছে:

* 🔵 **Groq API** — LLM (Groq/OpenRouter/Cerebras) থেকে তৈরি লেখা
* 🌐 **Browser Search** — লাইভ ওয়েব সার্চ (DuckDuckGo Instant Answer / Wikipedia)
* 💾 **Database** — বটের নিজের Brain OS Knowledge/Pattern/Template Engine
* 🔄 **Hybrid** — একাধিক সোর্স মিলিয়ে (যেমন Browser-এর কাঁচা তথ্য Groq দিয়ে গুছানো)

মডিউলটা ইচ্ছে করেই Telegram/AI/DB থেকে সম্পূর্ণ স্বাধীন রাখা হয়েছে — তাই এটা একা একা
import করে দ্রুত unit-test করা যায় এবং যেকোনো handler-এ নিরাপদে ব্যবহার করা যায়।

Usage::

    from rohan_bot.utils.source_tracker import DataSource, SourceMetadata, format_with_source

    meta = SourceMetadata(DataSource.BROWSER, confidence_score=0.85)
    meta.add_url("https://bn.wikipedia.org/wiki/ঢাকা")
    reply = format_with_source(answer_text, meta, command="search")
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # প্যাকেজ হিসেবে import হলে relative, স্ক্রিপ্ট হিসেবে চালালে absolute
    from .. import config as attribution_config
except (
    ImportError,
    ValueError,
):  # pragma: no cover - স্ক্রিপ্ট/ফাইল-পাথ লোডের জন্য fallback
    import config as attribution_config  # type: ignore

__all__ = [
    "DataSource",
    "SourceMetadata",
    "SOURCE_BN_LABELS",
    "SOURCE_KEYS",
    "coerce_source",
    "confidence_level",
    "confidence_percent",
    "build_metadata",
    "metadata_from_browse_result",
    "metadata_from_decision",
    "format_with_source",
    "load_settings",
    "resolve_command_settings",
    "RULE",
]

RULE = "━" * 34
_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S UTC"
_SHORT_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"


class DataSource(Enum):
    """উত্তরের তথ্যের উৎস।"""

    GROQ = "🔵 Groq API"
    BROWSER = "🌐 Browser Search"
    DATABASE = "💾 Database"
    HYBRID = "🔄 Hybrid"


#: বাংলা লেবেল (UI_LANG_CHOICES-এর "bn" ডিফল্ট ভাষার জন্য)।
SOURCE_BN_LABELS: Dict[DataSource, str] = {
    DataSource.GROQ: "🔵 Groq API",
    DataSource.BROWSER: "🌐 ব্রাউজার সার্চ",
    DataSource.DATABASE: "💾 ডাটাবেজ",
    DataSource.HYBRID: "🔄 সম্মিলিত",
}

#: সহজ স্ট্রিং-কী থেকে enum — main.py যাতে enum import না করেও সোর্স বলতে পারে।
SOURCE_KEYS: Dict[str, DataSource] = {
    "groq": DataSource.GROQ,
    "ai": DataSource.GROQ,
    "llm": DataSource.GROQ,
    "browser": DataSource.BROWSER,
    "web": DataSource.BROWSER,
    "browse": DataSource.BROWSER,
    "search": DataSource.BROWSER,
    "database": DataSource.DATABASE,
    "db": DataSource.DATABASE,
    "brain": DataSource.DATABASE,
    "knowledge": DataSource.DATABASE,
    "hybrid": DataSource.HYBRID,
    "mixed": DataSource.HYBRID,
}

_CONFIDENCE_HIGH_MIN = attribution_config.CONFIDENCE_HIGH_MIN
_CONFIDENCE_MEDIUM_MIN = attribution_config.CONFIDENCE_MEDIUM_MIN
#: সোর্সভেদে ডিফল্ট confidence — প্রতিবার env পড়া এড়াতে মডিউল লেভেলেই রাখা।
_DEFAULT_CONFIDENCE = dict(attribution_config.DEFAULT_CONFIDENCE)


def coerce_source(source: Any) -> DataSource:
    """যেকোনো ইনপুট (DataSource / "groq" / "Groq API" / enum-ভ্যালু) থেকে DataSource বানায়।

    Args:
        source: `DataSource`, এর নাম (``"GROQ"``), সহজ কী (``"browser"``) বা ডিসপ্লে ভ্যালু।

    Returns:
        DataSource: মিলে যাওয়া enum সদস্য।

    Raises:
        ValueError: কোনোভাবেই চেনা না গেলে।
    """
    if isinstance(source, DataSource):
        return source
    if source is None:
        raise ValueError("source দেওয়া হয়নি")
    text = str(source).strip()
    lowered = text.lower()
    if lowered in SOURCE_KEYS:
        return SOURCE_KEYS[lowered]
    for member in DataSource:
        if (
            member.name.lower() == lowered
            or member.value == text
            or member.value.lower() == lowered
        ):
            return member
    # ইমোজি দিয়েও চেনার চেষ্টা ("🌐 ..." অথবা শুধু "🌐")
    for member in DataSource:
        emoji = member.value.split(" ", 1)[0]
        if emoji and emoji in text:
            return member
    raise ValueError(f"অচেনা source: {source!r}")


def confidence_percent(score: float) -> int:
    """0.0–1.0 স্কোরকে পূর্ণসংখ্যা শতাংশে বদলায় (সীমার বাইরে গেলে clip করে)।"""
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0
    if value != value:  # NaN
        return 0
    return int(round(max(0.0, min(1.0, value)) * 100))


def confidence_level(score: float, lang: str = "bn") -> Tuple[str, str]:
    """Confidence স্কোর থেকে (লেবেল, রঙ-ইমোজি) জোড়া ফেরত দেয়।

    সীমা (spec অনুযায়ী): 🟢 High ৮৫–১০০% · 🟡 Medium ৬০–৮৫% · 🔴 Low < ৬০%

    Args:
        score: 0.0–1.0 এর মধ্যে confidence।
        lang: ``"bn"`` হলে বাংলা লেবেল, অন্য কিছু হলে ইংরেজি।

    Returns:
        tuple[str, str]: ``(emoji, label)`` — যেমন ``("🟢", "উচ্চ")``।
    """
    try:
        value = float(score)
    except (TypeError, ValueError):
        value = 0.0
    if value != value:  # NaN
        value = 0.0
    value = max(0.0, min(1.0, value))

    if value >= _CONFIDENCE_HIGH_MIN:
        return ("🟢", "উচ্চ" if lang == "bn" else "High")
    if value >= _CONFIDENCE_MEDIUM_MIN:
        return ("🟡", "মাঝারি" if lang == "bn" else "Medium")
    return ("🔴", "নিম্ন" if lang == "bn" else "Low")


def _utc_now() -> datetime:
    """Timezone-aware বর্তমান UTC সময় (``datetime.utcnow()`` deprecated, তাই এটা)।"""
    return datetime.now(timezone.utc)


def _as_utc(value: Optional[datetime]) -> datetime:
    """Naive datetime-কে UTC ধরে নিয়ে aware বানায়; None হলে এখনকার সময়।"""
    if value is None:
        return _utc_now()
    if not isinstance(value, datetime):
        raise TypeError(
            f"timestamp হতে হবে datetime, পাওয়া গেছে {type(value).__name__}"
        )
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class SourceMetadata:
    """একটা উত্তরের উৎস-তথ্য রাখে এবং তার থেকে badge তৈরি করে।

    Attributes:
        primary_source: মূল উৎস (`DataSource`)।
        timestamp: উত্তর তৈরির UTC সময়।
        confidence_score: 0.0–1.0 নির্ভুলতার অনুমান।
        secondary_sources: অতিরিক্ত উৎসের তালিকা (থাকলে উত্তর Hybrid ধরা হয়)।
        urls: মূল সোর্সের লিংক।
        cache_hit: ডাটাবেজ/ক্যাশ থেকে সরাসরি এসেছে কিনা।
        note: ছোট অতিরিক্ত ব্যাখ্যা (যেমন "AI দিয়ে গুছিয়ে লেখা")।
        breakdown: ``{"groq": 0.5, "browser": 0.3}`` — detailed ব্যাজের শতাংশ ভাগ।
        checked_sources: কোন কোন সোর্স চেষ্টা করা হয়েছিল (সফল/ব্যর্থ নির্বিশেষে)।
        query: ইউজারের মূল প্রশ্ন/কুয়েরি (ডায়াগনস্টিকের জন্য)।
    """

    def __init__(
        self,
        primary_source: Any,
        timestamp: Optional[datetime] = None,
        confidence_score: Optional[float] = None,
        secondary_sources: Optional[Iterable[Any]] = None,
        urls: Optional[Iterable[str]] = None,
        cache_hit: bool = False,
        note: str = "",
        breakdown: Optional[Dict[str, float]] = None,
        checked_sources: Optional[Iterable[str]] = None,
        query: str = "",
    ) -> None:
        self.primary_source = coerce_source(primary_source)
        self.timestamp = _as_utc(timestamp)
        if confidence_score is None:
            confidence_score = _DEFAULT_CONFIDENCE.get(
                self.primary_source.name.lower(), 0.8
            )
        try:
            self.confidence_score = max(0.0, min(1.0, float(confidence_score)))
        except (TypeError, ValueError):
            self.confidence_score = 0.8
        self.secondary_sources: List[DataSource] = []
        for item in secondary_sources or []:
            self.add_secondary(item)
        self.urls: List[str] = []
        self.add_urls(urls or [])
        self.cache_hit = bool(cache_hit)
        self.note = (note or "").strip()
        self.breakdown: Dict[str, float] = {}
        if breakdown:
            for key, weight in breakdown.items():
                try:
                    member = coerce_source(key)
                except ValueError:
                    continue
                try:
                    self.breakdown[member.name] = max(0.0, float(weight))
                except (TypeError, ValueError):
                    continue
        self.checked_sources: List[str] = [
            str(item).strip() for item in (checked_sources or []) if str(item).strip()
        ]
        self.query = (query or "").strip()

    # ------------------------------------------------------------------ helpers

    def add_url(self, url: str) -> None:
        """একটা সোর্স-লিংক যোগ করে (খালি/ডুপ্লিকেট বাদ)।"""
        cleaned = (url or "").strip()
        if cleaned and cleaned not in self.urls:
            self.urls.append(cleaned)

    def add_urls(self, urls: Iterable[str]) -> None:
        """কয়েকটা সোর্স-লিংক একসাথে যোগ করে।"""
        for url in urls or []:
            self.add_url(url)

    def add_secondary(self, source: Any) -> None:
        """একটা অতিরিক্ত উৎস যোগ করে — প্রাইমারির সাথে মিললে বা ডুপ্লিকেট হলে বাদ।"""
        member = coerce_source(source)
        if member is DataSource.HYBRID:
            return
        if member is not self.primary_source and member not in self.secondary_sources:
            self.secondary_sources.append(member)

    def add_checked_source(self, name: str) -> None:
        """কোন সোর্স চেক করা হয়েছিল তার তালিকায় নাম যোগ করে (ডুপ্লিকেট বাদ)।"""
        cleaned = (name or "").strip()
        if cleaned and cleaned not in self.checked_sources:
            self.checked_sources.append(cleaned)

    @property
    def all_sources(self) -> List[DataSource]:
        """প্রাইমারি + সব সেকেন্ডারি উৎস (ক্রম অনুযায়ী, ডুপ্লিকেট ছাড়া)।"""
        ordered = [self.primary_source]
        for member in self.secondary_sources:
            if member not in ordered:
                ordered.append(member)
        return ordered

    @property
    def is_hybrid(self) -> bool:
        """একাধিক ভিন্ন উৎস জড়িত থাকলে True।"""
        return len(self.all_sources) > 1

    @property
    def effective_source(self) -> DataSource:
        """ব্যাজে দেখানোর উৎস — একাধিক সোর্স থাকলে `HYBRID`, নইলে প্রাইমারি।"""
        if self.primary_source is DataSource.HYBRID:
            return DataSource.HYBRID
        return DataSource.HYBRID if self.is_hybrid else self.primary_source

    def label(self, source: Optional[DataSource] = None, lang: str = "bn") -> str:
        """একটা উৎসের ডিসপ্লে লেবেল (ডিফল্ট: কার্যকর উৎস)।"""
        member = source or self.effective_source
        if lang == "bn":
            return SOURCE_BN_LABELS.get(member, member.value)
        return member.value

    def _effective_breakdown(self) -> List[Tuple[DataSource, float]]:
        """Detailed ব্যাজের জন্য (উৎস, শতাংশ) তালিকা — breakdown না দিলে নিজে ভাগ করে।

        নিয়ম: প্রাইমারি ৭০%, বাকি ৩০% সেকেন্ডারিগুলোর মধ্যে সমান ভাগ। একক উৎস হলে ১০০%।
        """
        if self.breakdown:
            total = sum(self.breakdown.values())
            rows: List[Tuple[DataSource, float]] = []
            for name, weight in sorted(self.breakdown.items(), key=lambda kv: -kv[1]):
                member = DataSource[name]
                share = (weight / total) if total > 0 else 0.0
                rows.append((member, share))
            if rows:
                return rows

        sources = self.all_sources
        if len(sources) == 1:
            return [(sources[0], 1.0)]
        remainder = 0.30 / max(1, len(sources) - 1)
        return [(sources[0], 0.70)] + [(member, remainder) for member in sources[1:]]

    # -------------------------------------------------------------------- badge

    def to_badge(self, format_type: str = "compact", lang: str = "bn") -> str:
        """উৎস-ব্যাজের টেক্সট তৈরি করে।

        Args:
            format_type: ``minimal`` | ``compact`` | ``full`` | ``detailed``।
            lang: ``"bn"`` হলে বাংলা লেবেল, অন্য কিছু হলে ইংরেজি।

        Returns:
            str: ব্যাজের টেক্সট (ফরম্যাট অচেনা হলে ``compact`` ব্যবহার হয়)।
        """
        fmt = (format_type or "compact").strip().lower()
        if fmt == "minimal":
            return self._minimal_badge(lang)
        if fmt == "full":
            return self._full_badge(lang)
        if fmt == "detailed":
            return self._detailed_badge(lang)
        return self._compact_badge(lang)

    def _minimal_badge(self, lang: str) -> str:
        """শুধু ইমোজি + উৎসের নাম (একাধিক উৎস থাকলে 🔄 সম্মিলিত)।"""
        return self.label(lang=lang)

    def _compact_badge(self, lang: str) -> str:
        """দুই লাইনের ছোট ব্যাজ — সাধারণ উত্তরের জন্য ডিফল্ট।

        প্রথম লাইনে সব উৎস পাইপ দিয়ে আলাদা করা থাকে
        (যেমন ``_উৎস: 🌐 ব্রাউজার সার্চ | 🔵 Groq API_``), দ্বিতীয় লাইনে সময়/লিংক/নির্ভুলতা।
        """
        bn = lang == "bn"
        parts = [self.label(source=member, lang=lang) for member in self.all_sources]

        emoji, level = confidence_level(self.confidence_score, lang=lang)
        stamp = self.timestamp.strftime(_SHORT_TIMESTAMP_FORMAT)
        if bn:
            head = f"_উৎস: {' | '.join(parts)}_"
            meta_bits = [
                f"🕐 {stamp} UTC",
                f"🔗 {len(self.urls)} লিংক",
                f"নির্ভুলতা: {emoji} {level}",
            ]
            if self.cache_hit:
                meta_bits.append("💾 ক্যাশ")
        else:
            head = f"_Source: {' | '.join(parts)}_"
            meta_bits = [
                f"🕐 {stamp} UTC",
                f"🔗 {len(self.urls)} links",
                f"Confidence: {emoji} {level}",
            ]
            if self.cache_hit:
                meta_bits.append("💾 cache")
        return head + "\n_[" + "] [".join(meta_bits) + "]_"

    def _full_badge(self, lang: str) -> str:
        """বক্স-স্টাইল পূর্ণাঙ্গ ব্যাজ — /search-এর মতো সোর্স-গুরুত্বপূর্ণ উত্তরের জন্য।"""
        bn = lang == "bn"
        emoji, level = confidence_level(self.confidence_score, lang=lang)
        stamp = self.timestamp.strftime(_TIMESTAMP_FORMAT)

        if bn:
            lines = [
                RULE,
                "📊 উৎস তথ্য",
                f"├─ মূল উৎস: {self.label(source=self.primary_source, lang=lang)}",
            ]
        else:
            lines = [
                RULE,
                "📊 Source Information",
                f"├─ Primary Source: {self.label(source=self.primary_source, lang='en')}",
            ]

        extra: List[Tuple[str, str, str]] = []
        if self.secondary_sources:
            joined = " | ".join(
                self.label(source=member, lang=lang)
                for member in self.secondary_sources
            )
            extra.append(("অন্য উৎস", "Also Used", joined))
        if self.is_hybrid:
            extra.append(
                ("ধরন", "Result Type", self.label(source=DataSource.HYBRID, lang=lang))
            )
        if self.cache_hit:
            extra.append(("ক্যাশ", "Cache", "হিট 💾" if bn else "hit 💾"))
        if self.checked_sources:
            extra.append(
                ("চেক করা হয়েছে", "Checked", " → ".join(self.checked_sources))
            )
        if self.note:
            extra.append(("নোট", "Note", self.note))

        for bn_label, en_label, value in extra:
            lines.append(f"├─ {bn_label if bn else en_label}: {value}")

        confidence_text = (
            f"{emoji} {level} ({confidence_percent(self.confidence_score)}%)"
        )
        if bn:
            lines.append(f"├─ সময়: {stamp}")
            lines.append(f"└─ নির্ভুলতা: {confidence_text}")
        else:
            lines.append(f"├─ Timestamp: {stamp}")
            lines.append(f"└─ Confidence: {confidence_text}")

        if self.urls:
            lines.append("")
            lines.append("🔗 মূল সোর্স:" if bn else "🔗 Original Sources:")
            lines.extend(f"  • {url}" for url in self.urls[:8])

        lines.append("")
        lines.append(
            "[আরও জানুন] [যাচাই করুন] [সমস্যা জানান]"
            if bn
            else "[Learn More] [Verify] [Report Issue]"
        )
        lines.append(RULE)
        return "\n".join(lines)

    def _detailed_badge(self, lang: str) -> str:
        """শতাংশসহ ভাঙন + নির্ভুলতা-সতর্কতা + মূল লিংক — সংবেদনশীল তথ্যের জন্য।"""
        bn = lang == "bn"
        emoji, level = confidence_level(self.confidence_score, lang=lang)
        rows = self._effective_breakdown()

        lines = [RULE]
        lines.append("📊 উৎসের ভাঙন:" if bn else "📊 Data Sources Breakdown:")
        for member, share in rows:
            percent = confidence_percent(share)
            lines.append(f"  • {percent}% - {self.label(source=member, lang=lang)}")

        lines.append("")
        stamp = self.timestamp.strftime("%Y-%m-%d")
        if bn:
            lines.append(
                f"⚠️ নির্ভুলতা নোট: তথ্যটি {stamp} পর্যন্ত হালনাগাদ · {emoji} {level} "
                f"({confidence_percent(self.confidence_score)}%)"
            )
        else:
            lines.append(
                f"⚠️ Accuracy Note: This information is current as of {stamp} · {emoji} {level} "
                f"({confidence_percent(self.confidence_score)}%)"
            )

        if self.urls:
            lines.append("🔗 মূল সোর্স:" if bn else "🔗 Original Sources:")
            lines.extend(f"  • {url}" for url in self.urls[:8])
        elif bn:
            lines.append("🔗 মূল সোর্স: সংরক্ষিত নেই")
        else:
            lines.append("🔗 Original Sources: none recorded")

        lines.append(RULE)
        return "\n".join(lines)

    # -------------------------------------------------------------- (de)serialize

    def to_dict(self) -> Dict[str, Any]:
        """JSON-সেভযোগ্য dict — লগ/ডাটাবেজ/মেট্রিকসে রাখার জন্য।"""
        return {
            "primary_source": self.primary_source.name,
            "effective_source": self.effective_source.name,
            "secondary_sources": [member.name for member in self.secondary_sources],
            "timestamp": self.timestamp.isoformat(),
            "confidence_score": round(self.confidence_score, 4),
            "urls": list(self.urls),
            "cache_hit": self.cache_hit,
            "note": self.note,
            "breakdown": dict(self.breakdown),
            "checked_sources": list(self.checked_sources),
            "query": self.query,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SourceMetadata":
        """`to_dict()`-এর ফলাফল থেকে আবার SourceMetadata বানায়।"""
        payload = payload or {}
        raw_stamp = payload.get("timestamp")
        timestamp: Optional[datetime] = None
        if isinstance(raw_stamp, datetime):
            timestamp = raw_stamp
        elif isinstance(raw_stamp, str) and raw_stamp:
            try:
                timestamp = datetime.fromisoformat(raw_stamp)
            except ValueError:
                timestamp = None
        return cls(
            primary_source=payload.get("primary_source") or "hybrid",
            timestamp=timestamp,
            confidence_score=payload.get("confidence_score"),
            secondary_sources=payload.get("secondary_sources") or [],
            urls=payload.get("urls") or [],
            cache_hit=bool(payload.get("cache_hit", False)),
            note=payload.get("note", ""),
            breakdown=payload.get("breakdown") or None,
            checked_sources=payload.get("checked_sources") or [],
            query=payload.get("query", ""),
        )

    def __repr__(self) -> str:  # pragma: no cover - ডিবাগ সহায়ক
        return (
            f"SourceMetadata(primary={self.primary_source.name!r}, "
            f"secondary={[m.name for m in self.secondary_sources]!r}, "
            f"confidence={self.confidence_score:.2f}, urls={len(self.urls)})"
        )


# --------------------------------------------------------------------- builders


def build_metadata(
    source: Any,
    *,
    confidence_score: Optional[float] = None,
    urls: Optional[Iterable[str]] = None,
    secondary_sources: Optional[Iterable[Any]] = None,
    cache_hit: bool = False,
    note: str = "",
    breakdown: Optional[Dict[str, float]] = None,
    timestamp: Optional[datetime] = None,
    checked_sources: Optional[Iterable[str]] = None,
    query: str = "",
) -> SourceMetadata:
    """কীবোর্ড-আর্গুমেন্ট দিয়ে দ্রুত `SourceMetadata` বানানোর শর্টকাট।"""
    return SourceMetadata(
        source,
        timestamp=timestamp,
        confidence_score=confidence_score,
        secondary_sources=secondary_sources,
        urls=urls,
        cache_hit=cache_hit,
        note=note,
        breakdown=breakdown,
        checked_sources=checked_sources,
        query=query,
    )


def metadata_from_browse_result(
    found: Optional[Dict[str, Any]],
    *,
    organized_by_ai: bool = False,
    query: str = "",
    confidence_score: Optional[float] = None,
) -> Optional[SourceMetadata]:
    """`browse_web_search()`-এর ফলাফল dict থেকে source metadata বানায়।

    Args:
        found: ``{"text", "source", "url", "tried_sources", "matched_source"}`` বা None।
        organized_by_ai: কাঁচা ওয়েব-তথ্য Groq দিয়ে গুছিয়ে লেখা হয়েছে কিনা — True হলে
            উত্তরটা Hybrid (🌐 Browser + 🔵 Groq) হিসেবে দেখানো হয়।
        query: ইউজারের মূল প্রশ্ন।
        confidence_score: নিজের মান দিলে সেটাই, নইলে সোর্সভেদে ডিফল্ট।

    Returns:
        SourceMetadata | None: ফলাফল খালি/অবৈধ হলে None।
    """
    if not found:
        return None
    text = (found.get("text") or "").strip()
    if not text:
        return None

    metadata = SourceMetadata(
        DataSource.BROWSER,
        confidence_score=confidence_score,
        checked_sources=found.get("tried_sources") or [],
        query=query,
        note="কাঁচা ওয়েব-তথ্য AI দিয়ে গুছিয়ে লেখা" if organized_by_ai else "",
    )
    url = (found.get("url") or "").strip()
    if url:
        metadata.add_url(url)
    matched = (found.get("matched_source") or found.get("source") or "").strip()
    if matched:
        metadata.add_checked_source(matched)
    if organized_by_ai:
        metadata.add_secondary(DataSource.GROQ)
    return metadata


def metadata_from_decision(
    decision: Optional[Dict[str, Any]], *, query: str = ""
) -> Optional[SourceMetadata]:
    """Brain OS Decision Engine-এর direct উত্তরের জন্য DATABASE metadata বানায়।

    Args:
        decision: ``_phase17_decide()``/``api_decision_execute()``-এর রিটার্ন dict।
        query: ইউজারের মূল প্রশ্ন।

    Returns:
        SourceMetadata | None: decision direct না হলে/পে-লোড না থাকলে None।
    """
    if not decision or decision.get("strategy") != "direct":
        return None
    confidence = decision.get("confidence")
    try:
        confidence_value: Optional[float] = (
            float(confidence) if confidence is not None else None
        )
    except (TypeError, ValueError):
        confidence_value = None
    metadata = SourceMetadata(
        DataSource.DATABASE,
        confidence_score=confidence_value,
        cache_hit=True,
        query=query,
        note=str(decision.get("stage") or "brain_os"),
    )
    return metadata


# --------------------------------------------------------------------- formatting


#: `rohan_bot.config`-এর হেল্পারগুলো এখান থেকেও পাওয়া যায় (একটাই ইমপোর্ট-পয়েন্ট রাখতে)।
load_settings = attribution_config.load_settings
resolve_command_settings = attribution_config.resolve_command_settings


def format_with_source(
    text: str,
    metadata: Optional[SourceMetadata],
    format_type: Optional[str] = None,
    lang: str = "bn",
    command: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
) -> str:
    """মূল উত্তরের সাথে উৎস-ব্যাজ যুক্ত করে (কনফিগ মেনে)।

    কোনো অবস্থাতেই exception তোলে না — ব্যাজ বানানো সম্ভব না হলে মূল লেখাই ফেরত যায়,
    যাতে চ্যাট-ফ্লো কখনো ভাঙে না।

    Args:
        text: বটের আসল উত্তর।
        metadata: `SourceMetadata`; None হলে শুধু মূল লেখা ফেরত যায়।
        format_type: ``minimal``/``compact``/``full``/``detailed``; None দিলে কমান্ডের ডিফল্ট।
        lang: ``"bn"`` (ডিফল্ট) হলে বাংলা লেবেল।
        command: কমান্ডের নাম (``"search"``/``"/search"``) — per-command enable/format এর জন্য।
        settings: `load_settings()`-এর ফলাফল (বারবার লোড এড়াতে)।

    Returns:
        str: ব্যাজসহ (বা ব্যাজ ছাড়া) চূড়ান্ত টেক্সট।
    """
    body = (text or "").rstrip()
    if metadata is None:
        return body

    settings = settings or attribution_config.load_settings()
    if not settings.get("enabled", True):
        return body

    command_settings = attribution_config.resolve_command_settings(command, settings)
    if not command_settings.get("enabled", True):
        return body

    badge_lang = (lang or settings.get("lang", "bn") or "bn").strip().lower()
    badge_lang = (
        "bn"
        if badge_lang.startswith("bn") or badge_lang in {"bangla", "বাংলা"}
        else "en"
    )
    fmt = (
        format_type
        or command_settings.get("format")
        or settings.get("format", "compact")
    )
    try:
        badge = metadata.to_badge(format_type=fmt, lang=badge_lang)
    except Exception:  # প্রতিরক্ষামূলক: ব্যাজ কখনো মূল উত্তর ভাঙবে না (টেস্ট: Boom)
        return body
    if not badge:
        return body
    return f"{body}\n\n{badge}" if body else badge
