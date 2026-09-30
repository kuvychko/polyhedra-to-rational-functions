# Polyhedra as Complex Functions: Research Program and Repository Specification

Version: 2.2 — 2026-09-30

Status: Program specification. The repository is developed in the open and kept public-ready from its first commit: nothing committed should need scrubbing before release. This document does not itself authorize changing repository visibility, deploying the site, or publishing other existing work; each of those remains an explicit owner action.

This revision supersedes the exhibition-first v1 specification. It was first drafted as `KLEIN_DUALS_PROJECT_SPEC.md`; “Klein duals” is no longer the proposed umbrella name. v2.1 replaces the private-first stance of v2.0 with public-ready development and records the site stack and license decisions (see `docs/decisions/0001-public-ready-conventions.md`).

## 1. Purpose and central question

Develop, compare, and explain recipes that turn a convex three-dimensional polyhedron into a rational function on the Riemann sphere. Use complexplorer to investigate the functions through domain coloring and radial relief, then turn selected results into physical objects and a public mathematical exhibition.

**Research question:** How can we encode a convex polyhedron in a rational function so that meaningful aspects of its geometry and combinatorics remain recognizable in the resulting function and its visualizations?

There need not be a unique or universally best recipe. A good outcome is one justified default, perhaps one useful alternative, and an honest account of their strengths, limitations, and failures.

The work should remain an enjoyable, bounded exploration. Do not turn the initial research into a general geometry platform or make public presentation a prerequisite for experimentation.

## 2. Two phases, with separate outcomes

| Phase | Work | Required outcome |
| --- | --- | --- |
| 1 — Investigation (in the open, unpublished) | Audit existing code, define representations, compare recipes, derive properties, run controlled experiments | Reproducible research corpus, comparison report, selected recipe(s), limitations, and an exploration narrative |
| 2 — Explanation and capstone | Develop the research story into an accessible technical treatment; curate models, animations, photographs, and print recipes | Public research narrative and visual exhibition, backed by reproducible source |

Visualization has two roles: inexpensive diagnostic views throughout Phase 1, and polished communication as the final capstone. The exploration story is a first-class deliverable, not an appendix to the gallery.

Phase 1 ends with a decision record, not a website. Phase 2 begins when a recipe is sufficiently understood to explain and reproduce. Publication remains a later, explicit action.

## 3. Naming and mathematical scope

Working title: **Polyhedra as Complex Functions**.

Suggested repository name: `polyhedra-to-rational-functions`; shorter alternatives can be chosen later. Avoid names that prematurely promise a unique canonical transformation.

“Klein duals” has not been established here as standard terminology for the sculptures. Preserve it only as a historical label for existing assets where needed. Reserve references to Klein for specific classical constructions whose formulas and attribution have been checked.

Distinguish:

- Polyhedral geometry and combinatorics.
- The signed point configuration of zeros and poles, including multiplicities (the divisor).
- The rational function, determined by that divisor up to a nonzero complex constant.
- Symmetry of the divisor, magnitude, and full complex function.
- Domain coloring and the chosen radial mapping.
- The final mesh and its fabrication modifications.

A radial relief is not a geometric dual polyhedron. Exact symmetry, topological type, and visual resemblance are different properties. A continuous, finite, strictly positive radial graph over the sphere remains topologically a sphere; spikes and depressions alone do not create handles or through-holes.

## 4. Start from existing work

The owner already has generating code in a separate repository. Inspect and reuse it before designing interfaces or rewriting algorithms. Bring in only the parts this program needs, with provenance, and only under this repository's licenses.

Initial audit deliverables:

1. Inventory exact functions, model variants, coordinate conventions, and dependencies.
2. Record zero/pole locations and orders, treatment of infinity, normalization, and radial mappings.
3. Identify reusable geometry, evaluation, rendering, mesh, and export components.
4. Preserve at least one existing result as a regression reference, including its parameters and matching photo if known.
5. Identify any unreleased complexplorer dependency and record its exact revision.
6. Separate established formulas, implementation choices, and unverified historical labels.

Keep existing generators available as baselines. Add adapters where useful; do not require an architectural rewrite before the first experiment. The investigation may extend or replace individual recipes without discarding the original evidence.

## 5. What should a useful recipe preserve?

| Criterion | Operational question |
| --- | --- |
| Geometric correspondence | Can we explain what each zero and pole represents? |
| Rotation consistency | Does rotating the input rotate the magnitude field and relief without changing their shape? |
| Symmetry preservation | Does an input symmetry survive in the divisor and magnitude? Is full function invariance stronger or absent? |
| Duality | Does applying the recipe to the polar dual exchange zeros and poles and yield a reciprocal function up to normalization? |
| Degree economy | How much degree and phase winding are required to encode the selected data? |
| Stability | What changes under small perturbations, and what changes when combinatorics change? |
| Numerical reliability | Can the function be evaluated near singularities and infinity without avoidable artifacts? |
| Interpretability and aesthetics | Are features understandable and visually useful in coloring and relief? |
| Reproducibility | Does a stored configuration regenerate the same construction and comparable outputs? |

Report these criteria separately. Do not invent a single weighted score that hides tradeoffs. Separate measurable errors from human judgments of recognizability and visual appeal.

The function need not encode the full polyhedron injectively. Explicitly identify discarded information, such as distances lost through radial projection; do not claim reconstruction of the original solid without demonstrating it.

## 6. Geometry contract

Initial input: a full-dimensional convex polyhedron with vertices, genuine polygonal faces, and incidence data; an origin strictly inside it; and recorded scale and orientation conventions.

- Validate convexity, consistent face orientation, closed incidence, and the interior origin.
- Preserve polygonal faces. Triangles introduced solely for rendering must not change face sizes, vertex valences, or recipe multiplicities. Merge coplanar hull facets when necessary, with documented tolerance.
- Begin with deliberately centered fixtures. Treat automatic centering as a separate design choice rather than silently recentering every intermediate object.
- Compare projected vertex directions with point sets derived from the dual.
- For a face plane `n · x = h`, with outward unit normal and `h > 0`, the unit-sphere polar dual has vertex `n/h`. Its spherical direction is `n`.
- Projected face centroids are a separate candidate; they generally differ from polar-dual directions.
- Keep the same origin and polarity convention when testing duality. Independently recentering the dual can break the intended reciprocal relation.
- Store the original geometry as well as the spherical point sets; neither substitutes for the other.

Near degeneracies, record whether a perturbation preserves the face lattice. A generic vertex perturbation can split planar faces and change incidence weights discontinuously. Include separate experiments for fixed-combinatorics deformation and hull/combinatorial transitions.

## 7. Candidate recipes

All candidates must be expressed as point-placement and integer-multiplicity rules before selecting a renderer.

### R0. Existing implementations

Retain current Platonic examples as reference constructions. Determine their relationship to the new recipes algebraically or through divisor comparison, not by visual similarity alone.

### R1. Uniform balanced multiplicities

For `V` vertex directions and `F` dual-vertex directions, put zeros at vertices with order `F/gcd(V,F)` and poles at dual vertices with order `V/gcd(V,F)`.

Before cancellations, degree is `lcm(V,F)`. This is a simple baseline with potentially large degree. The reciprocal orientation is an equally valid convention.

### R2. Incidence-based multiplicities

Put a zero at each vertex with order equal to its valence. Put a pole at each dual vertex with order equal to the number of sides of the associated primal face.

Both totals are `2E`, by counting edge endpoints and face-edge incidences. Divide every multiplicity by their common integer gcd when possible. This preserves integrality and reduces the degree.

This proposed recipe connects local combinatorics to local function behavior and naturally exchanges weights under polar duality. It is a candidate to investigate, not an established optimal method or a claim of novelty.

Examples before coincident-point cancellation:

| Polyhedron | Uniform recipe degree | Incidence recipe degree after common-gcd reduction |
| --- | ---: | ---: |
| Tetrahedron | 4 | 4 |
| Cube | 24 | 24 |
| Icosahedron | 60 | 60 |
| Deltoidal icositetrahedron | 312 | 96 |

Verify these against the geometry fixtures. Coinciding zero and pole locations require explicit cancellation and a report of the resulting degree.

### R3. Small integer weights on symmetry orbits

As a bounded follow-up, seek lower positive integer multiplicities constant on each chosen symmetry orbit, subject to equal total zero and pole orders. Record the optimization criterion and tie-breaking rule. Investigate whether duality survives the selection rule.

Do not use fractional multiplicities while claiming a globally single-valued rational function. A real-valued potential or multivalued function would be a different construction and must be labeled separately.

### R4. Edge-incidence recipes

Added in v2.2 (decision 0002) because the baseline audit showed that the existing crown and star pieces are a construction worth studying deliberately. They generalize R2 from the vertex–face pair to the other pairs of cells in the face lattice, with multiplicities given by incidence counts:

- **Vertex–edge:** order `valence(v)` at each vertex and order 2 at each edge point. Both totals are `2E`.
- **Face–edge:** order `sides(f)` at each face's dual direction and order 2 at each edge point. Both totals are `2E`.

Divide by the common gcd as in R2. Polar duality exchanges vertices and faces and maps edges to edges, so the vertex–edge recipe of a polyhedron should be the face–edge recipe of its polar dual. On Platonic inputs these recipes should reproduce the baseline octahedral crown, icosahedral crown and icosidodecahedral star. Both statements are derived by hand and still to be verified.

Edge point placement is its own question. Compare the foot of the perpendicular from the origin to the edge line with the projected edge midpoint. The foot is self-dual under polarity: an edge and its dual edge share its direction. For a canonical polyhedron it is the midsphere tangency point.

Variants that use all three point sets (for example, vertices and faces against edges) are recorded as an open question, not a candidate to implement.

### Point-placement experiments

Compare polar-dual directions with projected face centroids using the same weights, and, for R4, edge tangency points with projected edge midpoints. Add other point sets only to answer a specific unresolved question. Do not start with an exhaustive product of all possible options.

## 8. Rational-function representation and normalization

In an affine chart, a recipe has the form:

`f(z) = C * product((z-a_i)^m_i) / product((z-b_j)^n_j)`.

Across the entire sphere, including infinity, total zero and pole multiplicities must agree. Chart degree differences can encode infinity; they must not accidentally introduce an unintended feature there.

Prefer a divisor-first representation and a stable evaluator. Investigate homogeneous coordinates with equal-degree numerator and denominator to avoid treating a chosen projection pole as a special geometric feature. Keep expanded polynomial coefficients optional: they can be poorly conditioned and are unnecessary for most renders.

Evaluation requirements:

- Provide complex evaluation for compatibility with complexplorer, plus a stable log-magnitude/phase route where needed.
- Use factored or homogeneous evaluation and log-domain accumulation when products overflow or underflow.
- Treat exact zeros, poles, cancellations, infinity, and near collisions explicitly.
- Separate algebraic cancellation from numerical near-coincidence. Record tolerances; do not silently cancel nearby distinct features.
- Distinguish rotating the object from changing the coordinate chart.

Normalization is part of the research. The modulus of `C` changes the relief and its argument rotates the phase palette. Choose and test a rotation-consistent magnitude convention; compare phase only up to a global shift when the convention leaves that freedom.

A promising magnitude baseline uses products of spherical chordal distances with balanced integer weights. Derive and verify its correspondence to a rational function's modulus up to a constant. Do not mistake a magnitude-only field for a complete complex function. Any numerical normalization over the sphere must document sampling and convergence.

Keep magnitude normalization, phase convention, degree-based display compression, and radial transfer function independently configurable. If displaying `|f|^(1/d)`, label it as a display mapping rather than changing the rational function's multiplicities.

## 9. Phase 1 experiment program

### Initial corpus

- Tetrahedron.
- Cube/octahedron pair.
- Icosahedron/dodecahedron pair.
- Deltoidal icositetrahedron and its polar dual.
- One irregular convex example with a well-defined interior origin.
- A fixed-combinatorics deformation of a symmetric example.
- A separately labeled combinatorial-transition case.

Record coordinate sources, construction steps, and geometry checks. Origami photographs can later provide a physical connection when they match the investigated geometry.

### Sequence

1. Reproduce the existing baseline and audit its formula.
2. Implement R1, R2 and R4 with polar-dual (and edge-tangency) point placement.
3. Check balancing, duality, rotation behavior, and numerical evaluation before judging aesthetics.
4. Generate a standardized comparison atlas across the small corpus.
5. Compare point placement while holding weights and display settings fixed.
6. Investigate R3 or other alternatives only where a concrete weakness remains.
7. Compare a small number of radial mappings on the strongest candidates.
8. Select a default and, if justified, one alternative; document failures and unresolved questions.

Each experiment starts with a question or hypothesis and changes a controlled factor. Keep both fixed-display comparisons and explicitly labeled individually tuned views, so rendering choices cannot masquerade as mathematical improvements.

### Standard outputs

For each case: original geometry with point markers; plane domain coloring; colored sphere; colored radial relief; neutral relief; degree and multiplicity summary; evaluation diagnostics; and a short observation.

Use static comparison panels initially. Record camera, color convention, projection extent, radial mapping, and sampling resolution. Print only selected candidates after numerical and visual screening.

### Targeted checks and diagnostics

- Divisor balance and degree before/after cancellation.
- Local zero/pole orders, optionally verified by phase winding on small loops.
- Rotation residual of normalized log-magnitude, evaluated away from singularities.
- Dual reciprocal residual in log-magnitude and phase, allowing the documented global constant.
- Consistency between coordinate charts and direct/evaluation paths.
- Perturbation sensitivity on matched spherical samples, with exclusion neighborhoods and their radii reported.
- Sampling convergence, seams, nonfinite values, and mesh resolution effects.

Define tolerances appropriate to precision and conditioning. Excluding singular neighborhoods must not conceal failures: report behavior near those features separately. Numerical evidence is not a proof of a universal property.

## 10. Repository architecture from day one

Use a small Python package and configuration-driven scripts. Adapt existing code into these responsibilities rather than rigidly enforcing the proposed filenames.

| Path | Responsibility |
| --- | --- |
| `README.md` | Research question, phase/status, quick start, and current findings |
| `PROGRAM.md` | This program and evolving scope |
| `pyproject.toml`, lock file | Reproducible environment, pinned complexplorer dependency |
| `src/polyhedral_functions/geometry.py` | Polyhedra, incidence, polarity, centering conventions |
| `src/polyhedral_functions/recipes.py` | Point placement and multiplicity rules |
| `src/polyhedral_functions/divisors.py` | Signed point sets, balancing, cancellation, provenance |
| `src/polyhedral_functions/evaluation.py` | Stable function, log-magnitude, phase, infinity |
| `src/polyhedral_functions/normalization.py` | Explicit magnitude and phase conventions |
| `src/polyhedral_functions/diagnostics.py` | Mathematical/numerical comparisons |
| `src/polyhedral_functions/rendering.py` | Thin complexplorer adapters and diagnostic panels |
| `src/polyhedral_functions/meshes.py` | Existing mesh/export integration and print adaptations |
| `data/polyhedra/` | Small geometry fixtures and provenance |
| `configs/recipes/`, `configs/experiments/` | Reusable presets and controlled experiment definitions |
| `notebooks/` | Exploration and interpretation; reusable logic lives in source modules |
| `experiments/` | Experiment index, manifests, small summaries, selected diagnostic assets |
| `notes/` | Dated observations, hypotheses, derivations, and negative results |
| `docs/decisions/` | Why particular conventions/recipes were selected or rejected |
| `docs/research/` | Curated exploration narrative and mathematical treatment |
| `scripts/` | Reproduce, compare, render, export; concrete commands set after code audit |
| `tests/` | Focused mathematical, numerical, and regression checks |
| `site/` | Phase 2 presentation source, created when needed |
| `.github/workflows/` | Lightweight checks initially; deployment only in Phase 2 |

Geometry/recipes must not depend on plotting or website code. Domain coloring and relief must consume the same mathematical result. Diagnostic output should be reusable in the eventual research narrative.

Avoid databases, services, and orchestration platforms. JSON/YAML configurations, JSON/CSV summaries, compact numerical files, and Markdown notes are sufficient. Keep large regenerable outputs and intermediate animation frames out of git; retain selected evidence and manifests. Preserve expensive or irreproducible assets in durable project storage.

## 11. Experiment record and provenance

Each run records:

- Stable experiment ID, question, hypothesis, status, and changed factor.
- Geometry ID/hash, provenance, origin, face representation, and transformations.
- Recipe name/version, placement rule, multiplicities, cancellation decisions, and resulting degree.
- Normalization, phase convention, evaluation method, precision, and tolerances.
- Random seed where used, code commit, dirty-tree status, and dependency versions.
- Sampling, camera, coloring, radial mapping, and mesh settings.
- Output paths/hashes, metrics, observations, failure modes, and conclusion.
- Links to preceding experiments and decisions that used the result.

Preserve compact configuration snapshots so changing defaults does not reinterpret an old run. Use the same manifest to connect a selected function to its renders, exported model, photograph, and eventual Printables listing.

## 12. The exploration story is its own deliverable

Maintain short notes during the work, then curate a standalone technical narrative:

1. **The question:** what does it mean to turn a polyhedron into a function?
2. **The construction space:** point placement, weights, duality, and information loss.
3. **The first obstacle:** balancing zeros and poles without arbitrary extra features.
4. **Competing recipes:** what each preserves and what it costs.
5. **Experiments that changed our view:** matched comparisons, failures, and counterexamples.
6. **Symmetry and deformation:** magnitude versus phase, geometric changes versus combinatorial changes.
7. **The selected recipe:** derivation, assumptions, reproducible worked example, and limitations.
8. **From analysis to object:** display compression, meshing, fabrication, and selected results.
9. **Open questions:** what remains conjectural or unexplored.

This is an outline, not a predetermined success story. Revise it to match the evidence. Label claims as established background, derived result, numerical observation, conjecture, or design preference. Do not claim novelty without a targeted literature review.

The narrative must remain readable independently of the sculpture gallery. Readers should be able to reproduce a comparison and understand why an attractive alternative was rejected.

## 13. Phase 1 exit criteria

- [ ] Existing source audited and baseline preserved.
- [ ] Geometry/face-incidence contract implemented and verified on fixtures.
- [ ] R1, R2 and R4 compared across the core corpus; additional candidates justified by findings.
- [ ] Balancing, infinity, normalization, rotation, duality, and cancellation handled explicitly.
- [ ] At least one irregular case and one controlled deformation investigated.
- [ ] Mathematical properties distinguished from rendering choices and numerical evidence.
- [ ] Comparison atlas and compact run records reproducible from a clean checkout.
- [ ] Default recipe and optional alternative selected, or a clear limitation explains why selection is premature.
- [ ] Decision record includes tradeoffs, failure cases, and unresolved questions.
- [ ] Exploration narrative draft exists separately from presentation material.

Stop expanding the candidate space once these questions are sufficiently answered. A limited, well-supported recipe is a valid result.

## 14. Phase 2: explanation and visual capstone

Build two complementary reader paths: **the research story** and **the object exhibition**. They may share one static site, but should have distinct pages/sections and navigation. The reader can start from an appealing object or from the mathematical question.

### Research treatment

Publish the curated narrative, a concise mathematical recipe, selected comparison panels, limitations, references, and commands to reproduce the key experiments. Keep detailed derivations available without placing them ahead of the introductory explanation.

### Exhibition

Include a strong photograph; a gallery extending beyond Platonic examples where supported; a brief introduction; one complete worked example; print links; and credits. Every object should link to its recipe, experiment lineage, and print status.

Coordinated views: polyhedron/dual markers → plane domain coloring → colored sphere → colored relief → monochrome model and photograph. Use matching phase palettes, sphere orientation, and cameras. Include legends, axes/extents, zero/pole markers, and explicit explanations of magnitude and phase.

Primary animation: colored sphere → colored radial relief → neutral sculpture. Optional research animations: controlled symmetry breaking, reciprocal duality, or comparison of recipes. Clearly distinguish changing the function from changing only its rendering. Verify mathematical meaning before animating.

Use complexplorer for scientific renders. Real photos document prints and origami; generated imagery must not substitute for experimental evidence. Provide static alternatives, video controls, reduced-motion behavior, captions, alt text, and mobile-readable layouts.

### Publication architecture

Default to a lightweight GitHub Pages site. Use MkDocs Material, matching complexplorer's documentation setup (strict builds, Markdown with MathJax math, rendered notebooks). Precompute scientific assets and separate their expensive generation from ordinary site builds. Keep project-subpath links correct, defer large media, and add a browser 3D viewer only if useful.

| Destination | Role |
| --- | --- |
| GitHub repository | Reproducible research, selected experiments, source, and presets |
| Website | Research narrative plus visual exhibition |
| Printables | Tested files, printing/assembly details, community makes |
| complexplorer | General visualization and export machinery |
| Personal website | Durable project entry linking to both narrative and gallery |

The repository is kept public-ready throughout, so release means flipping visibility rather than extracting a clean subset. The flip is an explicit owner action after review. Nothing committed may expose unrelated private work, and a public recipe must not depend on unavailable private code or data.

## 15. Phase 2 acceptance criteria

- [ ] Narrative, mathematical claims, and references match the actual findings.
- [ ] Selected comparisons and at least one complete example reproduce from the public source.
- [ ] Function, colors, relief, mesh, and photo have traceable provenance.
- [ ] Printable meshes checked for finite geometry, watertightness, orientation, dimensions, and relevant intersections; slicer preview inspected.
- [ ] Physically tested settings distinguished from proposed settings and digital-only models.
- [x] Code, media, and model licenses explicitly selected by the owner (MIT for code; CC BY 4.0 for media, meshes, and prose).
- [ ] Website works on desktop/mobile, under the repository subpath, and without motion-dependent explanations.
- [ ] Printables links to the relevant explanation; the site links back to printable files and source.
- [ ] Visibility/publication action explicitly authorized at the time of release.

## 16. References and immediate implementation inputs

Starting references already identified in discussion; verify applicability to each eventual claim:

- Oliver Nash, [On Klein's Icosahedral Solution of the Quintic](https://arxiv.org/abs/1308.0955), especially the classical polyhedral invariants. This does not establish the proposed general recipe's novelty.
- Gaurav Goel, [An Introduction to Modular Jacobians](https://gdmgoel.github.io/notes/Introduction_to_Modular_Jacobians.pdf), for background on divisors and the Riemann sphere; use a suitable focused reference in the final exposition.
- [David McCooey's deltoidal icositetrahedron data](https://dmccooey.com/polyhedra/java/DeltoidalIcositetrahedron.html), as a potential geometry reference; verify coordinate conventions and reuse terms.
- [complexplorer](https://github.com/kuvychko/complexplorer).
- [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), for Phase 2 deployment; check current instructions then.

Immediate inputs: access to the existing generating code; its baseline model parameters; available geometry fixtures; required complexplorer revision (3.1.0, public on PyPI); and this repository. Photos, final branding, and hosting choices can be resolved later without blocking recipe exploration.

**Definition of success:** A reproducible investigation explains what a polyhedron-to-function recipe preserves, why the selected recipe is useful, and where it fails. A public narrative tells that exploration story; the final visual and physical exhibition makes the results tangible.
