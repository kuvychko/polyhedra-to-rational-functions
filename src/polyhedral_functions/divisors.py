"""Divisors on the Riemann sphere: signed points with integer orders.

A recipe's output is a `Divisor`, not a function. It determines the rational function up to a
nonzero constant, and this module never chooses that constant (see `normalization`).

- **Orders are integers.** Positive orders are zeros and negative orders are poles. A divisor
  is the divisor of a rational function iff it is **balanced** (total order 0). Balance is
  counted over the whole sphere, including a point at the north pole, which is ``inf`` in the
  chart.
- **Cancellation is explicit.** `coalesced` merges points that coincide within an angular
  tolerance, sums their orders and reports what cancelled. Points that are merely *near* each
  other are never merged; `near_pairs` reports them so they can be examined.
- **Group operations.** Divisors add, subtract, negate and scale by integers, which is how
  identities such as ``D_R2 = D_R4ve - D_R4fe`` are checked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from math import gcd

import numpy as np

from .chart import chordal_distance, to_chart

# Points closer than this (chordal distance, which is about the angle in radians for small
# angles) are treated as the same point: algebraic coincidence that floating point has blurred.
# Fixture constructions agree to about 1e-15. Anything farther apart is a distinct feature and is
# not merged.
COINCIDENCE_TOL = 1e-9


@dataclass(frozen=True, eq=False)
class Divisor:
    """Points on the unit sphere with nonzero integer orders.

    ``labels`` records where each point came from (e.g. ``"vertex 3"``), for provenance. After
    `coalesced`, a merged point's label joins its sources with ``+``.
    """

    points: np.ndarray
    orders: np.ndarray
    labels: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        points = np.array(self.points, dtype=float).reshape(-1, 3)
        orders = np.array(self.orders).reshape(-1)
        if not np.all(np.equal(np.mod(orders, 1), 0)):
            raise ValueError("orders must be integers")
        orders = orders.astype(np.int64)
        if len(points) != len(orders):
            raise ValueError("one order per point")
        if np.any(orders == 0):
            raise ValueError("orders must be nonzero; drop the point instead")
        if len(points) and not np.allclose(np.linalg.norm(points, axis=1), 1.0, atol=1e-12):
            raise ValueError("points must be unit vectors")
        labels = tuple(self.labels) or tuple(f"p{i}" for i in range(len(points)))
        if len(labels) != len(points):
            raise ValueError("one label per point")
        points.setflags(write=False)
        orders.setflags(write=False)
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "orders", orders)
        object.__setattr__(self, "labels", labels)

    # --- construction ------------------------------------------------------------------

    @classmethod
    def from_sets(
        cls, zeros, zero_orders, poles, pole_orders, zero_label="zero", pole_label="pole"
    ) -> Divisor:
        """Zeros on one point set and poles on another. Orders are given as positive numbers."""
        zero_orders = np.broadcast_to(np.asarray(zero_orders), (len(zeros),))
        pole_orders = np.broadcast_to(np.asarray(pole_orders), (len(poles),))
        if np.any(zero_orders <= 0) or np.any(pole_orders <= 0):
            raise ValueError("give zero and pole orders as positive integers")
        return cls(
            np.vstack([np.reshape(zeros, (-1, 3)), np.reshape(poles, (-1, 3))]),
            np.concatenate([zero_orders, -pole_orders]),
            tuple(f"{zero_label} {i}" for i in range(len(zeros)))
            + tuple(f"{pole_label} {j}" for j in range(len(poles))),
        )

    @classmethod
    def empty(cls) -> Divisor:
        return cls(np.zeros((0, 3)), np.zeros(0, dtype=np.int64), ())

    # --- basic properties -------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.orders)

    @property
    def total_order(self) -> int:
        return int(self.orders.sum())

    @property
    def is_balanced(self) -> bool:
        return self.total_order == 0

    @property
    def degree(self) -> int:
        """Total zero order. It is the degree of the rational map only after `coalesced`."""
        return int(self.orders[self.orders > 0].sum())

    @property
    def zeros(self) -> Divisor:
        keep = self.orders > 0
        return Divisor(self.points[keep], self.orders[keep], self._labels_where(keep))

    @property
    def poles(self) -> Divisor:
        keep = self.orders < 0
        return Divisor(self.points[keep], self.orders[keep], self._labels_where(keep))

    def _labels_where(self, keep) -> tuple[str, ...]:
        return tuple(lab for lab, k in zip(self.labels, keep, strict=True) if k)

    def require_balanced(self) -> None:
        if not self.is_balanced:
            poles = self.degree - self.total_order
            raise ValueError(f"divisor is unbalanced: zero order {self.degree}, pole order {poles}")

    # --- group operations ---------------------------------------------------------------

    def __add__(self, other: Divisor) -> Divisor:
        return Divisor(
            np.vstack([self.points, other.points]),
            np.concatenate([self.orders, other.orders]),
            self.labels + other.labels,
        )

    def __neg__(self) -> Divisor:
        return Divisor(self.points, -self.orders, self.labels)

    def __sub__(self, other: Divisor) -> Divisor:
        return self + (-other)

    def __mul__(self, k: int) -> Divisor:
        if int(k) != k:
            raise ValueError("divisors scale by integers only")
        if k == 0:
            return Divisor.empty()
        return Divisor(self.points, self.orders * int(k), self.labels)

    __rmul__ = __mul__

    def reduced(self) -> tuple[Divisor, int]:
        """Divide every order by their common gcd. Returns ``(divisor, gcd)``."""
        g = reduce(gcd, np.abs(self.orders).tolist(), 0) or 1
        return Divisor(self.points, self.orders // g, self.labels), g

    def rotated(self, rotation) -> Divisor:
        return Divisor(self.points @ np.asarray(rotation, dtype=float).T, self.orders, self.labels)

    # --- cancellation and comparison --------------------------------------------------

    def coalesced(self, tol: float = COINCIDENCE_TOL) -> tuple[Divisor, list[dict]]:
        """Merge coincident points, summing orders and dropping any that cancel to zero.

        Returns ``(divisor, cancellations)``. Each cancellation records the merged labels, the
        orders that met, and what survived. A pure merge of same-sign orders is not a
        cancellation and is not reported.
        """
        n = len(self)
        parent = list(range(n))

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        if n:
            close = chordal_distance(self.points, self.points) <= tol
            for i, j in zip(*np.nonzero(np.triu(close, k=1)), strict=True):
                parent[find(int(i))] = find(int(j))

        groups: dict[int, list[int]] = {}
        for i in range(n):
            groups.setdefault(find(i), []).append(i)

        points, orders, labels, cancellations = [], [], [], []
        for members in groups.values():
            members.sort()
            total = int(self.orders[members].sum())
            signs = set(np.sign(self.orders[members]).tolist())
            if len(signs) > 1:
                cancellations.append(
                    {
                        "labels": [self.labels[i] for i in members],
                        "orders": self.orders[members].tolist(),
                        "remaining": total,
                    }
                )
            if total != 0:
                # A merged point sits at the first member. Members agree to `tol`.
                points.append(self.points[members[0]])
                orders.append(total)
                labels.append("+".join(self.labels[i] for i in members))

        if not points:
            return Divisor.empty(), cancellations
        return Divisor(np.array(points), np.array(orders), tuple(labels)), cancellations

    def near_pairs(self, radius: float, tol: float = COINCIDENCE_TOL) -> list[dict]:
        """Zero-pole pairs closer than ``radius`` but not coincident: near-cancellations.

        These are kept as distinct features. They matter for numerical evaluation and for print
        geometry (a spike next to a pit).
        """
        zeros, poles = self.zeros, self.poles
        if not len(zeros) or not len(poles):
            return []
        d = chordal_distance(zeros.points, poles.points)
        pairs = []
        for i, j in zip(*np.nonzero((d > tol) & (d < radius)), strict=True):
            pairs.append(
                {
                    "zero": zeros.labels[i],
                    "pole": poles.labels[j],
                    "chordal_distance": float(d[i, j]),
                }
            )
        return pairs

    def same_as(self, other: Divisor, tol: float = 1e-8) -> bool:
        """Equal as divisors: after coalescing, the same points (within ``tol``) and orders."""
        a, _ = self.coalesced()
        b, _ = other.coalesced()
        if len(a) != len(b):
            return False
        if not len(a):
            return True
        d = chordal_distance(a.points, b.points)
        match = d.argmin(axis=1)
        return bool(
            np.all(d[np.arange(len(a)), match] <= tol)
            and len(set(match.tolist())) == len(a)
            and np.array_equal(a.orders, b.orders[match])
        )

    # --- the chart --------------------------------------------------------------------

    def chart_form(self) -> tuple[np.ndarray, np.ndarray, int]:
        """``(finite_points, finite_orders, order_at_infinity)`` in the stereographic chart.

        Coalesce first if the divisor may hold coincident points.
        """
        z = to_chart(self.points)
        finite = np.isfinite(z)
        return z[finite], self.orders[finite], int(self.orders[~finite].sum())

    def summary(self) -> dict:
        """Counts for manifests."""
        zeros, poles = self.zeros, self.poles
        return {
            "n_zeros": len(zeros),
            "n_poles": len(poles),
            "degree": self.degree,
            "balanced": self.is_balanced,
            "zero_orders": sorted(set(zeros.orders.tolist())),
            "pole_orders": sorted(set((-poles.orders).tolist())),
        }
