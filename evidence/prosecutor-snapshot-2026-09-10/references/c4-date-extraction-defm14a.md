# C4 Date Extraction from DEFM14A — Sentence-Boundary Signing Rejection

## Date Extraction Patterns (for meeting/vote/outside dates)

When extracting deadline dates from DEFM14A filings, these regex patterns match the typical wording:

```python
patterns = [
    ("vote_date", r'(?:annual|special|general)\s+meeting\s+(?:shall|will|to)\s+be\s+held\s+(?:on\s+)?(\w+\s+\d{1,2},?\s*\d{4})'),
    ("vote_date", r'meeting\s+(?:date|will\s+be\s+held)\s+(?:on\s+)?(\w+\s+\d{1,2},?\s*\d{4})'),
    ("outside_date", r'outside\s+date\s+(?:of|is|shall\s+be)\s+(\w+\s+\d{1,2},?\s*\d{4})'),
    ("outside_date", r'(?:termination|outside)\s+date\s+(?::|of|is)\s+(\w+\s+\d{1,2},?\s*\d{4})'),
    ("closing_date", r'(?:closing|consummation)\s+(?:of|date\s+of)\s+(?:the\s+)?(?:transaction|merger)\s+(?:shall\s+)?occur\s+(?:on\s+)?(\w+\s+\d{1,2},?\s*\d{4})'),
    ("record_date", r'record\s+date\s+(?:for|of|is)\s+(?:the\s+)?(?:meeting|vote)\s+(?:set\s+as\s+)?(\w+\s+\d{1,2},?\s*\d{4})'),
]
```

## HTML Preprocessing

Before matching, strip HTML tags and decode entities:

```python
plain = re.sub(r'<[^>]+>', ' ', text)
plain = re.sub(r'\s+', ' ', plain)
plain = plain.replace('&nbsp;', ' ').replace('&#160;', ' ')
plain = plain.replace('&#8220;', '"').replace('&#8221;', '"')
plain = plain.replace('&#8217;', "'")
```

iXBRL filings (12MB+) need this — raw HTML contains XBRL metadata that contaminates date searches.

## Sentence-Boundary Signing Rejection

**Problem:** A 250-char sliding window before the date match picks up signing/execution keywords from unrelated lines in a 12MB filing, falsely rejecting valid meeting dates.

**Fix:** Use sentence-boundary detection — find the `.` or `;` before and after the match, then check ONLY that sentence:

```python
s = max(0, plain.rfind('.', 0, m.start()) + 1)
e = min(len(plain), plain.find('.', m.end()))
if e <= s:
    e = min(len(plain), m.end() + 200)
sentence = plain[s:e].lower()
if any(w in sentence for w in ["signed", "executed", "entered into", "dated as of", "date of this"]):
    results.append((label, date_iso, "REJECTED_SIGNING", m.group(0)[:120]))
else:
    results.append((label, date_iso, "ACCEPTED", m.group(0)[:120]))
```

## Pacing Enforcement

```python
class Pacing:
    def __init__(self, min_gap=1.0):
        self.min_gap = min_gap
        self.last = 0.0
        self.log = []
    
    def wait(self, label=""):
        now = time.time()
        gap = now - self.last
        ts = datetime.now().isoformat()
        if gap < self.min_gap:
            time.sleep(self.min_gap - gap)
            now = time.time()
            gap = now - self.last
        self.log.append(f"  {ts} {label}: gap {gap:.2f}s")
        assert gap >= self.min_gap, f"Pacing VIOLATION: {gap:.3f}s < {self.min_gap}s"
        self.last = now
        return gap
```

- EFTS: ≥0.3s spacing. Filing text: ≥1.0s spacing.
- 3x retry with exponential backoff (2^attempt s) on HTTP 503/500.
- All requests timestamp-logged; `assert` enforced in code, never by convention.

## CIK Resolution for Filing Access

1. Query EFTS by adsh to get issuer CIK (`ciks` field in response)
2. Strip leading zeros from issuer CIK for archive path
3. Fallback: filing-agent CIK from adsh prefix (first 10 chars, stripped)
4. Index page URL: `sec.gov/Archives/edgar/data/{CIK_stripped}/{adsh_no_dashes}/{adsh}-index.htm`
5. Extract doc path from **BOTH** `/ix?doc=` links AND `<a href>` links in the index page:
   - Some index pages have ZERO `ix?doc=` links and use only regular `<a href="...htm">` links
   - The href path contains the correct issuer CIK (which may differ from filing-agent CIK)
   - Parse `<a href="([^"]+\.(?:htm|html))"` for regular links
   - Skip index pages, companysearch, privacy pages
   - Build full URL from href path (absolute if starts with `/`, relative if just filename)
6. Fetch filing document DIRECTLY (not through ix viewer); full iXBRL can be 12MB+