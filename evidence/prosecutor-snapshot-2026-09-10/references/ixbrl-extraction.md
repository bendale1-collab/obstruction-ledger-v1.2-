# iXBRL Filing Text Extraction

## Problem

SEC filings in inline XBRL (iXBRL) format embed human-readable content inside XML tags. The raw HTML looks like:

```html
<ix:nonNumeric name="dei:EntityCentralIndexKey">0001655210</ix:nonNumeric>
<div style="display:none">...</div>
<p>On <span>July 25, 2026</span>, the company...</p>
```

A naive `re.findall(r"...")` or `"keyword" in text` on the raw HTML finds the keyword in the XBRL header metadata, not in the actual filing content. The actual deadline dates are in the visible body text.

## Fix

Strip all HTML/XML tags before searching:

```python
import re
clean = re.sub(r'<[^>]+>', ' ', raw_html)
clean = re.sub(r'\s+', ' ', clean).strip()
# Now search for dates in clean text
```

This produces readable text like:
```
On July 25, 2026 , the company...
```

## Index Page Document Links

The index page (`{adsh}-index.htm`) has TWO types of document links:

1. **ix?doc links** — for iXBRL/inline XBRL filings: `href="/ix?doc=/Archives/edgar/data/{CIK}/{adsh}/{file}.htm"`
2. **Plain href links** — for traditional HTML filings: `href="/Archives/edgar/data/{CIK}/{adsh}/{file}.htm"`

Parse BOTH:
```python
doc_links = re.findall(r'ix\?doc=([^"&\s]+\.(?:htm|html))', html)
if not doc_links:
    doc_links = re.findall(r'href="([^"]*\.htm)"', html)
    doc_links = [d for d in doc_links if "index" not in d.lower()]
```

## Filing Types and Typical Content

| Filing Type | Contains Deadline? | Typical Deadline Type |
|------------|-------------------|---------------------|
| 8-K item 3.02 | Yes | Warrant redemption date |
| 8-K item 8.01 | Yes | Record date, dividend date |
| 8-K item 3.01 | Yes | Cure period deadline |
| 8-K item 5.03 | Yes | Stock split / dividend record date |
| 424B5 | Yes | Offering closing / settlement date |
| SC TO-I | Yes | Tender offer expiration |
| DEFA14A | Yes | Record date, meeting date |
| 10-K/Q | No | Historical only |

## Pitfalls

- **Header contamination**: The XBRL header contains `dei:EntityCentralIndexKey`, `dei:DocumentType`, etc. that match "keyword" searches. Strip tags first.
- **Hidden divs**: `<div style="display:none">` contains XBRL metadata. The `re.sub('<[^>]+>', ' ', text)` approach handles this.
- **Exhibit files**: The primary iXBRL filing may be the 8-K form itself, but the warrant agreement or redemption notice is often in an `ex-` file. Check both the primary doc and the exhibit files.
- **Rate limiting**: SEC archive server requires ≥1.0s between requests. EFTS (efts.sec.gov) is ≥0.3s.
- **User-Agent**: Required for ALL requests to SEC servers. Without it → HTTP 403.