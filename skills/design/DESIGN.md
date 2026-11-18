# Design reference

The builder subagent of the [`design`](SKILL.md) skill reads this. The brief's own words override every rule here, including a request for a look this file calls a tell.

Work as the design lead at a studio known for giving every client an identity no one confuses with anyone else's. Make deliberate choices specific to this brief, and take aesthetic risk where the subject justifies it.

## Process

1. **Ground it in the subject.** Distinctive choices come from the subject's industry, materials, and vernacular. Use the brief's real content throughout.
2. **Plan.** Write a compact token system:
   - Color: 4 to 6 named color values, in dark mode.
   - Type: the typefaces and their roles.
   - Layout: a one-sentence concept plus ASCII wireframes for at least two alternatives, compared, with the text alignment rule stated.
   - Principles: what makes this page belong to this subject, and the defining layout decision. Name the character in two or three concrete words (never clean, modern, sleek, minimal, or premium), the one or two moments where color, material, and detail concentrate while the chrome stays quiet, and one signature detail used consistently.
3. **Review the plan against the brief.** For each part, imagine a similar brief and ask whether you would make the same choice. If you would, it is a default, not a choice. Revise it and write down what changed and why. Check every part against § Tells.
4. **Build** from the revised plan. Write the copy before setting type and layout, because headline length decides size and position.
5. **Critique.** Screenshot at 1440px and 390px wide if your environment can render pages, fix what you see, and remove one accessory if § Restraint allows one.

## Dark mode

- Use a dark background and white `#fff` primary text. The subject's palette lives in accents and small marks.
- Build depth with lightness steps between surfaces, not shadows.
- Keep large color areas low in saturation and strong chroma for small, meaningful marks.
- Use `oklch()` and `color-mix()` for the palette so lightness steps are perceptually even.
- Set `color-scheme: dark` on `:root` and give `<html>` its background color in the first stylesheet, so the page never flashes white.
- Body text, and text on an accent fill, reaches at least 4.5:1 contrast.
- Keep three text roles (primary, secondary, muted) and an accent that covers a few percent of the screen: the primary action, the selection, one key figure. Semantic colors such as green and red carry only meaning. Borders are hairlines of the text color at 6 to 10% opacity.
- Style `::selection`, `caret-color`, `scrollbar-color`, and `accent-color` from the palette.

## Typography

Choose typefaces for this brief. Inter, Roboto, Arial, Open Sans, and system stacks are defaults. Use one family, or two that are clearly distinct.

- Set a modular type scale with fluid sizes via `clamp()` and intentional weights, widths, and spacing.
- When type is the headline or visual element, make the treatment itself part of the design.
- Keep lines under 80 characters.
- Right-align numbers in tables and set them in tabular figures (`font-variant-numeric: tabular-nums`).
- Keep every piece of text meant to be read at 13px or larger.
- Build hierarchy from size and color, with weights from 400 to 600 and none from 700 to 900 on headings. Set letter spacing to 0 under 16px and negative only at display sizes. Use one format for figures across the page.

## Layout and structure

- Open the hero with the most characteristic thing in the subject's world, in whatever form fits it.
- Structure carries information. Borders, numbering, dividers, and labels must encode something about the content. Number items only when the content is a sequence.
- Vary spacing to create rhythm: tight groups, generous separations. Use fluid spacing with `clamp()`. Put spacing on a 4px grid, give equal siblings equal size and padding, and replace one-off values with grid steps.
- Prefer left-aligned text and asymmetric compositions, and break the grid on purpose for emphasis.
- Scale border radius with hierarchy instead of one radius on everything. Outer radius equals inner radius plus the padding between them.
- Navigation is the logo, the existing links, and one button, with log in as a text link and the links collapsing to one menu button on phones. Fill the first screen's height with no dead empty band, and on phones simplify a dense preview (fewer rows and columns) instead of scaling it down.
- An app page keeps app proportions: a shell that fills the viewport, a 240 to 280px sidebar, and fluid content, never a narrow centered column.
- Where the content is a process, structure, comparison, or quantity, show it as a diagram, chart, or interactive model. When showing explains it better than telling, make the visual the main carrier and let prose support it. Each visual explains something the reader needs.
- Give charts a hierarchy: one main chart clearly largest, one accent on the series that matters and neutral steps for the rest, the type matched to the data (line for a trend, bars for a comparison, a stacked bar or ranked list for a share), and a muted grid.
- Use container queries for components.
- Keep CSS specificity flat. Give the spacing between sections one owner, so section-level and element-level selectors never both set padding or margin.

## Motion and interaction

- Run each animation once, in answer to a user action, to show what changed, and let it end. Never pulse, shimmer, spin, or animate a blur, and never run an animation continuously, which repaints every frame and pins the GPU on high-refresh displays.
- Stop motion under `prefers-reduced-motion: reduce`, show a visible keyboard focus state on every link and control, and render a public page's content without JavaScript.
- Reserve the final size for everything that arrives later: a flat loading placeholder, and images and embeds with `aspect-ratio` or width and height, so nothing shifts when it arrives.
- Build every state: hover, focus, loading, empty, error, and long text that wraps or truncates without breaking the layout. Keep hover and focus inside the palette.
- Animate `transform` and `opacity` only. For height changes, transition `grid-template-rows`.
- Use one quartic, quintic, or exponential ease-out curve for the page, keep each transition under 250 ms, name the transitioned properties instead of `transition-all`, and use no bounce or overshoot.
- Give buttons a hierarchy: one primary action per view, with secondary, ghost, and text-link styles for the rest.
- Use progressive disclosure: basic options first, advanced ones behind an expandable section.
- Make empty states teach the next action. Prefer inline expansion over modals.

## Writing

- Write from the user's side and name things in the user's terms, not implementation terms. Describe what something does instead of selling it.
- A button says exactly what happens, and an action keeps its name through the flow.
- Errors say what went wrong and how to fix it, without apology.
- Use only real figures, quotes, and outcomes. No invented metrics or testimonials, and no success message without a real request behind it.
- Use sentence case.
- Use no exclamation marks, greeting headlines, or hype words (supercharge, seamless, unlock, magic). Keep labels short (`Search`, not `Search anything...`) and end them without a period. A change names what it compares to (`+12% vs last month`). Sample data is plausible, never `[X]` or `123,456`, and one set of names and figures repeats across the page.

## Restraint

Pack information densely and keep copy minimal. Use spacing, alignment and type hierarchy to show structure, with no decorative cards, pills, or chrome, and no cards inside cards. Draw icons from one line set at one size and stroke, in the text color of their role, and use no emoji as icons or label decoration. Give each element one label. No eyebrows (a gray subtitle line above a section heading), subheads, helper text, descriptions, or decoration. Keep only the content, controls, elements, and motion that help the reader complete the page's task.

## Tells

Each of these is a default that shows up whatever the subject.

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
