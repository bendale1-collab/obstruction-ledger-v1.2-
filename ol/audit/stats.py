"""Wilson score interval. Every rate in a result file carries one."""

from __future__ import annotations

import math

Z_95 = 1.959963984540054


def wilson_ci(numerator: int, denominator: int, z: float = Z_95) -> tuple[float, float]:
    if denominator <= 0:
        return (0.0, 0.0)
    n = float(denominator)
    p = numerator / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    margin = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))
