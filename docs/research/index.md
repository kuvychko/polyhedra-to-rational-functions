# The question

How can a convex polyhedron be encoded in a rational function so that its geometry and
combinatorics stay recognizable, in the function and in its pictures?

There need not be one right answer, and this is not a story of one. The research compared
several recipes and measured what each one preserves and what it costs. It also recorded where
each one fails.

## What we found

These are findings for the solids tested, not theorems about every polyhedron;
[Limitations](limitations.md) gives their reach.

- **R2 is the default recipe.** It puts a zero at each vertex, of order equal to the number of
  edges meeting there, and a pole at each face direction, of order equal to the face's number of
  sides. On the polar dual it gives exactly the reciprocal function **[D]**. Its relief keeps
  the solid's full symmetry, mirrors included, in all 55 runs of the comparison atlas **[N]**.
  It has the lowest degree on most of the tested solids **[N]**.
- **R4 is genuinely different, not a variant.** It pairs vertices (R4ve) or faces (R4fe) with
  edges. It was the only recipe that changed continuously across a combinatorial transition,
  and then only across its matching one: R4ve when a vertex is truncated. R2 jumped at every
  transition tested **[N]**. The relief of R4ve correlates with R2's at only 0.48–0.92
  **[N]**. The recipes are tied by an exact identity, \(D_{R2} = D_{R4ve} - D_{R4fe}\)
  **[D]**.
- **The display can disguise or exaggerate differences.** Under one fixed relief sharpness, the
  uniform recipe R1 and R2 look very different. Tuning the sharpness to each recipe's highest
  order removes most of the gap: on the deltoidal icositetrahedron the relief correlation rises
  from 0.950 to 0.991 **[N]**. The phase difference remains: R1 winds about three times as often.

Labels: **[D]** derived here, **[N]** numerical observation, as in
[the exploration](narrative.md).

## The pages

- **[The recipes](recipes.md):** the construction in brief, the selected default (R2), its
  alternative (R4), and a complete worked example.
- **[Compare recipes](compare.md):** an interactive 3D comparison of where each recipe puts its
  zeros and poles, for any two solids and recipes side by side.
- **[The exploration](narrative.md):** the full account. It covers how the question was set up
  and which experiments changed the picture. Every claim is labelled as
  established background, derived here, numerical observation, conjecture, or design
  preference.
- **[Experiments](experiments.md):** the comparison atlas and the controlled experiments, with
  their figures.
- **[Limitations](limitations.md):** how far each result reaches, what the construction gives
  up, the known weaknesses, and the open questions.
- **[Decisions](../decisions/README.md):** short records of each convention and choice, with the
  reasons for it and what would reopen it.
