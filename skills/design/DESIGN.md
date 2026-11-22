# Design reference

The [`design`](SKILL.md) skill and its builder read this. § Hard rules always apply. Every other section is a default. The brief, the host's rendering contract, and the project's design system override a default, in that order, including a request for a look this file calls a tell.

For a new identity, work as the design lead at a studio known for giving every client an identity no one confuses with anyone else's, and take aesthetic risk where the subject justifies it. For an app UI inside a system, work as the system's maintainer: match it, extend it with named tokens, and spend novelty only where it makes the data easier to read.

## Hard rules

- Body text, and text on any fill, reaches at least 4.5:1 contrast. Large text, icons, chart marks, borders that identify a control, and focus rings reach at least 3:1 against what is next to them.
- No text meant to be read is under 13px. Lines of prose stay under 80 characters.
- Every link and control works by keyboard, in a logical order, with a visible focus state.
- Motion stops under `prefers-reduced-motion: reduce`. No animation runs continuously, and transitions stay under 250 ms.
- Late content reserves its size, so nothing shifts when it arrives.
- Every data region has hover and focus, loading, empty, error, and long-text states, plus stale and unknown states for live data.
- Color is never the only signal: pair state colors with a word, a shape, or a position.
- Numbers in tables are right-aligned in tabular figures, and the page uses one format for each kind of figure.
- Use only real figures, quotes, and outcomes. Show no success message without a real request behind it.
- A public page shows its content with JavaScript off. A page that owns its background sets it on `<html>` in the first stylesheet, so it never flashes.

## Process

1. **Ground it in the subject.** Distinctive choices come from the subject's industry, materials, and vernacular. Use the brief's real content throughout.
2. **Plan.** Inside an existing system, list the tokens and components you reuse and any you add, then skip to step 4. Otherwise write a compact token system:
   - Color: 4 to 6 identity colors, plus the semantic set the content needs (such as ok, warning, error, stale, and chart series), for each color scheme you support.
   - Type: the typefaces and their roles.
   - Layout: a one-sentence concept plus ASCII wireframes for at least two alternatives, compared, with the text alignment rule stated.
   - Principles: what makes this page belong to this subject, and the defining layout decision. Name the character in two or three concrete words (never clean, modern, sleek, minimal, or premium), the one or two moments where color, material, and detail concentrate while the chrome stays quiet, and one signature detail used consistently.
3. **Review the plan against the brief.** For each part, imagine a similar brief and ask whether you would make the same choice. If you would, it is a default, not a choice. Revise it and write down what changed and why. Check every part against § Tells.
4. **Build** from the revised plan. Write the copy before setting type and layout, because headline length decides size and position.
5. **Critique.** Screenshot at the widths and color schemes the skill checks, if your environment can render pages. Fix what you see, and remove one accessory if § Restraint allows one.

## Color and theme

- Inside a host frame, use the host's theme variables and leave the page background to the host. Otherwise support the color schemes the brief or project sets. A standalone page with no stated scheme defaults to dark plus a light variant under `prefers-color-scheme`.
- In dark mode, primary text is white or near white. The subject's palette lives in accents and small marks.
- Build depth with lightness steps between surfaces, not shadows.
- Keep large color areas low in saturation and strong chroma for small, meaningful marks.
- Use `oklch()` and `color-mix()` for the palette so lightness steps are perceptually even.
- Set `color-scheme` on `:root` to match the schemes you support.
- Keep three text roles (primary, secondary, muted) and an accent that covers a few percent of the screen: the primary action, the selection, one key figure. Semantic colors such as green and red carry only meaning. Borders are hairlines of the text color at 6 to 10% opacity.
- Style `::selection`, `caret-color`, `scrollbar-color`, and `accent-color` from the palette.
- Name tokens by role (`--text-2`, `--stop`), not by hue, and test their contrast in code when the project has a test suite.

## Typography

For a new identity, choose typefaces for this brief, and treat Inter, Roboto, Arial, Open Sans, and system stacks as defaults to beat. For an app UI, a neutral sans with tabular figures, including those faces, is a sound choice. Use one family, or two that are clearly distinct.

- Set a modular type scale. Use fluid sizes via `clamp()` for display text, and fixed sizes for tables and controls.
- When type is the headline or visual element, make the treatment itself part of the design.
- Build hierarchy from size and color first, with weights from 400 to 600 by default. Set letter spacing to 0 under 16px and negative only at display sizes.

## Layout and structure

- Structure carries information. Borders, numbering, dividers, and labels must encode something about the content. Number items only when the content is a sequence.
- Vary spacing to create rhythm: tight groups, generous separations. Use fluid spacing with `clamp()`. Put spacing on a 4px grid, give equal siblings equal size and padding, and replace one-off values with grid steps.
- Prefer left-aligned text and asymmetric compositions, and break the grid on purpose for emphasis.
- Scale border radius with hierarchy instead of one radius on everything. Outer radius equals inner radius plus the padding between them.
- Where the content is a process, structure, comparison, or quantity, show it as a diagram, chart, or interactive model. When showing explains it better than telling, make the visual the main carrier and let prose support it. Each visual explains something the reader needs.
- Use container queries for components.
- Keep CSS specificity flat. Give the spacing between sections one owner, so section-level and element-level selectors never both set padding or margin.

### Landing pages and sites

- Open the hero with the most characteristic thing in the subject's world, in whatever form fits it.
- Navigation is the logo, the existing links, and one button, with log in as a text link and the links collapsing to one menu button on phones. Fill the first screen's height with no dead empty band, and on phones simplify a dense preview (fewer rows and columns) instead of scaling it down.

### Apps, dashboards, and data-dense UI

- Keep app proportions: a shell that fills the viewport (except inside a host frame), a sidebar of about 200 to 320px, and fluid content, never a narrow centered column.
- Density beats breathing room. Use compact rows (28 to 36px on desktop), group with alignment and hairlines, and keep 44px targets on phones.
- Keep the text that changes what the operator does: units, as-of times, data source and provenance, and the consequence of an action. § Restraint does not remove it.
- Live data shows its as-of time and a distinct stale state. An update changes the value in place, without shifting its width, and without more than one brief highlight.
- Tables: sticky header, sortable columns with `aria-sort`, right-aligned numbers, truncation that keeps the full value reachable, a fixed column order, and on phones the priority columns with the rest of each row behind an expand control.
- Charts:
  - Give charts a hierarchy: one main chart clearly largest, one accent on the series that matters and neutral steps for the rest, and a muted grid.
  - Match the type to the data: a line for a trend, bars for a comparison, a stacked bar or ranked list for a share.
  - Label the axes with units, show the zero or baseline, and give time axes only the sessions that exist.
  - Use sign colors only for sign.
  - Make the tooltip or crosshair reachable by keyboard, and give each chart a text or table alternative.
  - Draw with SVG up to a few thousand points and with canvas beyond.
- Keyboard: give frequent actions shortcuts declared with `aria-keyshortcuts`, and add a command palette when there are more than about 7 destinations.
- Several equal controls may share one style. Keep a single primary style for the action that commits money or state.

## Motion and interaction

- Run each animation once, in answer to a user action, to show what changed, and let it end. Never pulse, shimmer, spin, or animate a blur. A determinate progress bar is allowed.
- Use a flat loading placeholder, and give images and embeds `aspect-ratio` or width and height.
- Keep hover and focus inside the palette.
- Animate `transform` and `opacity` only. For height changes, transition `grid-template-rows`.
- Name the transitioned properties instead of `transition-all`. By default, use one quartic, quintic, or exponential ease-out curve for the page, with no bounce or overshoot.
- Give buttons a hierarchy: by default, one primary action per view, with secondary, ghost, and text-link styles for the rest.
- Use progressive disclosure: basic options first, advanced ones behind an expandable section.
- Make empty states teach the next action. Prefer inline expansion over modals.

## Writing

- Write from the user's side and name things in the user's terms, not implementation terms. Describe what something does instead of selling it.
- A button says exactly what happens, and an action keeps its name through the flow.
- Errors say what went wrong and how to fix it, without apology.
- Use sentence case.
- Use no exclamation marks, greeting headlines, or hype words (supercharge, seamless, unlock, magic). Keep labels short (`Search`, not `Search anything...`) and end them without a period. A change names what it compares to (`+12% vs last month`). Sample data is plausible, never `[X]` or `123,456`, and one set of names and figures repeats across the page.

## Restraint

Pack information densely and keep copy minimal. Use spacing, alignment and type hierarchy to show structure, with no decorative cards, pills, or chrome, and no cards inside cards. Draw icons from one line set at one size and stroke, in the text color of their role, and use no emoji as icons or label decoration. Give each element one label. No eyebrows (a gray subtitle line above a section heading) or decoration. Add helper text only where it changes what the reader does: an empty state's next step, an error's fix, units, as-of times, provenance, or an action's consequence. Keep only the content, controls, elements, and motion that help the reader complete the page's task.

## Tells

Each of these is a default that shows up whatever the subject. Check them when building a new identity. Inside an existing system or an app UI, the system wins, and dense columns, hairline rules, monospace identifiers, and green and red signs for gains and losses are conventions there, not tells.

**Palettes**
- warm cream background (near `#F4F1EA`) with a high-contrast serif and a terracotta accent (near `#D97757`)
- near-black with one acid-green or vermilion accent
- cyan-on-dark, purple-to-blue gradients, or neon glow on dark
- gray text on a colored background instead of a shade of that background
- gradient text on headings or metrics.

**Layout**
- the big-number hero (large figure, small label, supporting stats, gradient accent), unless it really is the best option
- fade-and-slide-up on every section and hover effects on every card
- the SaaS card kit: identical rounded cards (icon, heading, text) in a grid, one radius everywhere, the same soft shadow (`rgba(0,0,0,.1)`) under each, gradient washes as decoration
- broadsheet layout with hairline rules, zero radius, and dense newspaper columns
- everything centered
- a large rounded icon above every heading
- a rounded box with a thick colored border on one side
- glossy blobs, orbs, floating cubes, glowing grids, or holographic brains and robots as hero filler.

**Chrome**
- one word in a headline set apart by italic, bold, or color
- meta strings joined with middle dots and labels built as a capitalized word, a dash, and a fragment
- monospace for small data labels
- tiny uppercase letter-spaced labels
- `→` appended to link and button text
- glassmorphism, blur, glow borders, grain, and noise used as decoration
- decorative sparklines that convey no data
- emoji in labels, badges, and a pill badge above the headline
- a logo as a gradient or sparkle tile instead of the name as text with a flat mark.

Final check: if you showed this page to someone and said "AI made this", would they believe it at once? If so, find the default that gave it away and replace it.
