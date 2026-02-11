import re
import unicodedata
from html import unescape
from typing import Any

from src.util.logger_config import get_logger

logger = get_logger(__name__)

COUNTRY_MAP = {
    "cl": "Chile",
    "chile": "Chile",
    "chile, chile": "Chile",
    "remote": "Remote",
}

SENIORITY_MAP = {
    # General
    "jr": "Junior",
    "junior": "Junior",
    "ssr": "Semi-Senior",
    "semi senior": "Semi-Senior",
    "mid": "Mid",
    "senior": "Senior",
    "sr": "Senior",
    "lead": "Lead",
    "staff": "Staff",
    "principal": "Principal",
    # GetOnBoard
    "1": "No experience",
    "2": "Junior",
    "3": "Semi Senior",
    "4": "Senior",
    "5": "Expert",
}

MODALITY_MAP = {
    "remote": "Remote",
    "remote_local": "Remote",
    "remoto": "Remote",
    "hybrid": "Hybrid",
    "hibrido": "Hybrid",
    "híbrido": "Hybrid",
    "onsite": "Onsite",
    "presencial": "Onsite",
}


def _safe_str(value: Any) -> str:
    """Convert any value to clean string safely."""
    try:
        if value is None:
            return ""
        if isinstance(value, (list, tuple, set)):
            value = next(iter(value), "")
        return str(value).strip()
    except Exception as e:
        logger.error(f"Normalizer failed converting value: {value} | {e}")
        return ""


def _normalize_text(text: str) -> str:
    """Lowercase, remove accents, strip."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return text


def normalize_location(raw: Any) -> str:
    val = _normalize_text(_safe_str(raw))
    if not val:
        return "No especificado"

    normalized = COUNTRY_MAP.get(val, val.title())
    if normalized == val.title() and val not in COUNTRY_MAP:
        logger.warning(f"Unknown country value: {raw}")

    return normalized


def normalize_seniority(raw: Any) -> str:
    val = _normalize_text(_safe_str(raw))
    if not val:
        return "No especificado"

    normalized = SENIORITY_MAP.get(val, val.title())
    if normalized == val.title() and val not in SENIORITY_MAP:
        logger.warning(f"Unknown seniority value: {raw}")

    return normalized


def normalize_modality(raw: Any) -> str:
    val = _normalize_text(_safe_str(raw))
    if not val:
        return "No especificado"

    normalized = MODALITY_MAP.get(val, val.title())
    if normalized == val.title() and val not in MODALITY_MAP:
        logger.warning(f"Unknown modality value: {raw}")

    return normalized


# def normalize_job_text(raw: str) -> str:
#     # 1) Fix encoding / weird chars
#     raw = raw.replace("\xa0", " ").strip()
#
#     # 2) Parse HTML
#     soup = BeautifulSoup(raw, "html.parser")
#
#     # 3) Convert HTML → Markdown
#     h = html2text.HTML2Text()
#     h.ignore_links = True
#     h.ignore_images = True
#     md = h.handle(str(soup))
#
#     # 4) Cleanup Markdown noise
#     md = re.sub(r"\n{3,}", "\n\n", md)  # collapse blank lines
#     md = re.sub(r"[ \t]+", " ", md)  # collapse spaces
#     md = md.strip()
#
#     return md


def html_to_markdown_basic(text: str) -> str:
    text = unescape(text)

    replacements = {
        r"<strong>(.*?)</strong>": r"**\1**",
        r"<li>(.*?)</li>": r"- \1\n",
        r"<br\s*/?>": "\n",
        r"</p>": "\n\n",
        r"<.*?>": "",  # remove remaining tags
    }

    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.S)

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
