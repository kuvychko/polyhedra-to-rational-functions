# 0003: Chordal normalization and chart phase as the defaults

Date: 2026-10-01. Status: accepted.

## Context

A divisor fixes its rational function only up to a nonzero constant `C`. `|C|` changes the
relief, because sea level is `|f| = 1`, and `arg C` rotates the phase palette. The baseline fixed
`|C|` by sampling the sphere's geometric mean of `|f|`. That sampling is off by up to 0.55% (audit
finding 1) and must be refitted whenever the function changes.

## Decision

1. **Magnitude:** `log|f(x)| = Σ mᵢ log χ(x, aᵢ)`, where `χ` is the Euclidean distance between unit
   vectors (`normalization.py`). This is:
   - exactly self-dual (`−D` gives `1/f`);
   - exactly rotation-covariant;
   - chart-free;
   - of geometric mean 1 over the sphere, because the mean of `log χ(x, a)` is `log 2 − 1/2` for
     every `a` and the orders sum to zero.

   It equals the baseline's normalization at the baseline's own exact constant. That is verified
   to 1e-8 on all six R0 pieces (`tests/test_normalization.py`), so no existing result changes
   meaning, apart from the baseline's sampling error.
2. **Phase:** in complexplorer's chart, `f(z) = C ∏ (z − aᵢ)^mᵢ` over finite points, with
   `C > 0`. The phase is a chart convention, not an invariant, so compare phases only within a
   chart and only up to a global shift.
3. **Evaluation:** log-domain and factored, never via expanded coefficients
   (`evaluation.py`). Infinity is the order at the north pole, read off the divisor.

## Consequences

- No module fits a normalization constant by sampling. Sphere quadrature is used only to *check*
  results (`fibonacci_sphere`).
- Display mappings (`|f|^(1/d)`, radial transfers) stay separate settings on top of this
  magnitude.

## Reopen if

A recipe needs sea level somewhere other than the geometric mean. The baseline's pole flowers
did, normalizing along the equator. If that happens, add a named alternative convention rather
than changing this default.
