# E004-display: how much of the visible difference is the display?

- **Question:** how much of the visible difference between recipes is created by the relief
  display, rather than by the functions?
- **Hypothesis:**
  - Under a fixed sharpness, R1 (high local orders) renders blunter than R2, and the reliefs
    differ.
  - An order-tuned or degree-compressed display removes most of the R1/R2 difference.
  - R2/R4ve stays different under every display.
- **Changed factor:** only the logistic scale `k` in `r = depth + (1 − depth) logistic(log|f| / k)`.
  The functions and `depth = 0.2` are fixed. Three mappings:
  - **fixed:** `k = 4` for every recipe, as in E001;
  - **order-tuned:** `k = 2 × max |order|`, the baseline's rule, which gives every recipe tip
    exponent 1/2;
  - **degree-compressed:** `k = degree / 6`, calibrated so that the cube's R2 equals the fixed
    display.
- **Method:**
  - Relief radius fields are computed with `rendering.relief_radius`, which matches
    complexplorer's mesh to 1e-6 (tested).
  - They are compared on 20,000 Fibonacci samples. Radii are bounded, so no caps are needed.
  - Neutral reliefs are rendered for the DI and irregular-9.
- **Status:** complete. Run from clean commit `6284280`; its code is identical to `7c929c7`.
  Reproduce with `uv run python scripts/e004_display.py --publish`.
- **Files:**
  - `display.csv`: correlations, RMS, tip exponents and spreads;
  - `display.jpg`: correlation bars;
  - `reliefs-*.jpg`: recipe × display grids;
  - `manifest.json`.

## Results: confirmed

Relief-radius correlation:

| fixture | R1~R2 fixed | order-tuned | degree-compressed | R2~R4ve (all displays) |
|---|---|---|---|---|
| cube | 1.000 | 1.000 | 1.000 | 0.54 |
| deltoidal icositetrahedron | **0.950** | **0.991** | **0.991** | 0.68 |
| irregular-9 | 0.959 | 0.984 | 0.985 | 0.75–0.76 |
| triakis tetrahedron | 0.955 | 0.956 | 0.957 | 0.89–0.90 |
| hexagonal pyramid | 0.837 | 0.829 | 0.835 | 0.74–0.75 |

- **High-order inputs (DI, irregular-9):**
  - **Fixed display:** R1 has local orders up to 13 and 14, so its tip exponent is up to 3.5;
    it renders as rounded lobes.
  - **Tuned or compressed display:** R1 and R2 are visually almost indistinguishable
    (`reliefs-deltoidal-icositetrahedron.jpg`).
  - **Size of the effect:** the scalar correlation understates it, because the difference
    lives in the tips, a small fraction of the sphere.
- **Low-order inputs (triakis tetrahedron, pyramid):** the display changes nothing, and the R1/R2
  difference that remains there is real (E003).
- **R2 vs R4ve:** unaffected by the display. It is a difference between functions.

## What this means

- **R1 vs R2 is decided by degree economy and phase readability.** The appearance of the relief
  can be equalized by a display rule. Phase readability (winding density) cannot: phase has no
  display knob.
- **The baseline's order-tuned rule should be the default *display* for comparisons across
  recipes**, labelled as tuned. Fixed-display panels stay as the controlled view. Degree
  compression gives nearly the same result here, but needs a calibration constant.
