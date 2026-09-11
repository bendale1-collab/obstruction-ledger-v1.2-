"""C1 negative-space properties. Written from the sealed section 2 definition only.
No check code is imported or referenced. Each property yields fixture TEXT that
must produce no C1 finding.
"""
from decimal import Decimal, ROUND_HALF_UP
from hypothesis import strategies as st, assume
MIN_EXAMPLES = 200
LABELS = ["phi at large L", "strip edge", "lambda-second", "runtime", "manifest files"]

def round_sig(d, n):
    if d == 0:
        return Decimal(0)
    q = Decimal(1).scaleb(d.adjusted() - n + 1)
    return d.quantize(q, rounding=ROUND_HALF_UP)

def render(label, prose_value, table_value, unit=""):
    ucol = " | unit" if unit else ""
    usep = "|---" if unit else ""
    urow = f" | {unit}" if unit else ""
    prose = f"{label} is {prose_value}{(' ' + unit) if unit else ''}."
    return f"{prose}\n\n| label | value{ucol} |\n|---|---{usep}|\n| {label} | {table_value}{urow} |\n"

@st.composite
def same_value_rendered_two_ways(draw):
    """Prose is the table value rounded to k <= its sig digits under section 2 -> SILENT."""
    label = draw(st.sampled_from(LABELS))
    mant = draw(st.integers(min_value=1, max_value=99999999))
    exp = draw(st.integers(min_value=-6, max_value=3))
    sign = draw(st.sampled_from(["", "-"]))
    table = Decimal(f"{sign}{mant}e{exp}")
    ntab = len(str(mant).rstrip("0")) or 1
    k = draw(st.integers(min_value=1, max_value=ntab))
    prose = round_sig(table, k)
    # Second ambiguity (filed pre-run): rounding that carries across a decade
    # (0.98 -> 1.0) changes the rendered digit count, and section 2 counts
    # rendered digits. Stay out of that region too.
    assume(prose.adjusted() == table.adjusted())
    ps, ts = format(prose, "f"), format(table, "f")
    # Section 2 does not say how integer trailing zeros count as significant
    # digits (filed pre-run). Stay out of the ambiguous region: neither side
    # may be an integer rendering ending in zero.
    assume(not (("." not in ps) and ps.endswith("0")))
    assume(not (("." not in ts) and ts.endswith("0")))
    return render(label, ps, ts)

@st.composite
def identical_strings(draw):
    """Prose and table carry the identical numeral string and unit -> SILENT."""
    label = draw(st.sampled_from(LABELS))
    places = draw(st.integers(min_value=0, max_value=6))
    v = draw(st.decimals(min_value=Decimal("-1000000"), max_value=Decimal("1000000"),
                         places=places, allow_nan=False, allow_infinity=False))
    unit = draw(st.sampled_from(["", "s", "ms"]))
    return render(label, format(v, "f"), format(v, "f"), unit)

PROPERTIES = {
    "same_value_rendered_two_ways": same_value_rendered_two_ways(),
    "identical_strings": identical_strings(),
}
