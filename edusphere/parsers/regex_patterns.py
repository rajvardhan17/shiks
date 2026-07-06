from __future__ import annotations

import re

URL_PATTERN = re.compile(
    r"https?://[A-Za-z0-9\-\.]+(?:\:[0-9]+)?(?:/[\w\-\./?%&=]*)?"
)

EMAIL_PATTERN = re.compile(
    r"[\w.+-]+@[\w.-]+\.[a-z]{2,}|"
    r"[\w.+-]+\s*(?:\[at\]|\(at\))\s*[\w.-]+\s*(?:\[dot\]|\(dot\))\s*[a-z]{2,}",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4,5}"
)

DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}|"
    r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4})\b",
    re.IGNORECASE,
)

# Generic fee pattern - matches any currency amount
FEE_PATTERN = re.compile(
    r"(?:Rs\.?|INR|₹|USD)\s?[\d,]+(?:\.\d+)?|"
    r"[\d,]+(?:\.\d+)?\s?(?:lakh|lakhs|crore|crores)",
    re.IGNORECASE,
)

# Specific fee type patterns
TOTAL_FEE_PATTERN = re.compile(
    r"\b(?:total\s+(?:course\s+)?fees?|total\s+(?:academic\s+)?fees?|total\s+cost|course\s+fee|full\s+course\s+fee)\s*[:\-]?\s*(?:Rs\.?|INR|₹|USD)?\s?[\d,]+(?:\.\d+)?|"
    r"(?:Rs\.?|INR|₹|USD)\s?[\d,]+(?:\.\d+)?\s*(?:per\s+(?:semester|year|program))?",
    re.IGNORECASE,
)

REGISTRATION_FEE_PATTERN = re.compile(
    r"\b(?:registration\s+(?:fees?|charges?)|enrollment\s+(?:fees?|charges?)|application\s+(?:fees?|charges?))\s*[:\-]?\s*(?:Rs\.?|INR|₹|USD)?\s?[\d,]+(?:\.\d+)?",
    re.IGNORECASE,
)

TUITION_FEE_PATTERN = re.compile(
    r"\b(?:tuition\s+(?:fees?|charges?)|academic\s+(?:fees?|charges?)|course\s+(?:fees?|charges?))\s*[:\-]?\s*(?:Rs\.?|INR|₹|USD)?\s?[\d,]+(?:\.\d+)?",
    re.IGNORECASE,
)

ADMISSION_FEE_PATTERN = re.compile(
    r"\b(?:admission\s+(?:fees?|charges?)|entrance\s+(?:fees?|charges?))\s*[:\-]?\s*(?:Rs\.?|INR|₹|USD)?\s?[\d,]+(?:\.\d+)?",
    re.IGNORECASE,
)

DEGREE_TERMS = r"(?:B\.?Tech|M\.?Tech|MBA|B\.?E\.?|BE|B\.?Sc|B\.?A\.?|LLB|MBBS|BDS|BPharm|MPharm|MCA|BCA|BBA|BArch|MSc|MA|BA|BCom|BDes|Ph\.?D|Doctor of Philosophy|Master of Technology|Master of Science|Master of Arts|Bachelor of Technology|Bachelor of Science|Bachelor of Arts|Bachelor of Commerce|Bachelor of Laws)"

COURSE_PATTERN = re.compile(
    r"\b(?:" + DEGREE_TERMS + r")\b"
    r"(?:\s+(?:in|of|for)\s+[^.;,\n]*?(?=\s+(?:and|or)\s+(?:" + DEGREE_TERMS + r")\b|[.;,\n]|$))?",
    re.IGNORECASE,
)

RANKING_PATTERN = re.compile(
    r"((?:JEE(?:\s*Advanced|\s*Main)?|CAT|NEET|GATE|CLAT|CUET|XAT|MAT|NATA|BITSAT|IITJEE|SRMJEEE|NMAT|CMAT|All India Rank|AIR)[^\n\r]{0,80}?\d{1,6}(?:,\d{3})?(?:\s*%?))",
    re.IGNORECASE,
)

RANK_KEYWORD_PATTERN = re.compile(
    r"\b(?:opening|closing|minimum|maximum)?\s*(?:rank|ranking|cut[- ]?off|closing rank|opening rank|minimum rank|required rank|cutoff rank|closing cutoff|minimum cutoff|opening cutoff|maximum cutoff)\b[^\n\r]{0,80}?\d{1,6}(?:,\d{3})?(?:\s*%?)",
    re.IGNORECASE,
)
