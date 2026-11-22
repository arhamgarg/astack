---
name: design
description: Use for any web UI, chart, or HTML output, before writing it: a request to design, build, restyle, mock up, or judge a page, site, landing page, app screen, dashboard, table, chart, data visualization, HTML artifact, inline HTML render, or UI component.
---

# Frontend design

## 1. Find what already decides the look

Settle the look in this order, from strongest to weakest:

1. The user's words.
2. The host's rendering contract: T3 `html_render` theme variables and frame rules, or the Artifact page contract and its `artifact-design` skill.
3. The project's design system: its tokens, components, and screenshot and contrast tests.
4. [`DESIGN.md`](DESIGN.md).

The hard rules in `DESIGN.md` hold at every level. Its defaults apply only where nothing above sets the matter.

## 2. Write the brief

- Subject: what the page is for, who reads it, and its main job. Where the request leaves something open, choose a concrete answer consistent with [`DESIGN.md`](DESIGN.md) and note it as an assumption.
- Content: the real copy, data, and links the user supplied. The builder writes everything else.
- Constraints: the stack, required sections, and visual direction the user set, plus whatever step 1 found. Reuse existing tokens and components before adding new ones, and name each token you add. A standalone page defaults to one self-contained `index.html` with inline CSS and JS. Load fonts only from sources the host and the project's CSP allow.
- Kind: a new identity (a landing page, site, or explainer) or an app UI inside a system (a dashboard, console, or tool). The kind decides which `DESIGN.md` sections apply.
- Phones: adapt the layout and main task for phones by default. Text stays readable, touch targets are at least 44px, controls stay usable in a short viewport with the keyboard open, main actions stay reachable within safe areas, and narrow screens cause no horizontal scrolling.
- Output: the path the user asked for, or the project's routes and components. A standalone page with no requested location goes in a new folder named after the page, with its assets beside it.

## 3. Build it

Build a change to existing UI, a single component, or an inline chart yourself. For a new page or a multi-screen build, start one worker on the newest Claude Fable or Opus model (the `fable` or `opus` alias where the harness accepts one) at high reasoning effort. Include the absolute path of `DESIGN.md` and send the brief with this:

> Read the design reference at the path in this brief in full and follow its process, building at the output path. Report in at most five lines: the output path, the defining layout decision, the palette values and typefaces, what the plan review changed, and anything unfinished.

## 4. Check the result

Run the rendering checks in a browser or preview tool when the host allows one, and record any check you cannot run as not performed.

- The page exists at the requested path or route and opens without console errors.
- It meets `DESIGN.md` § Hard rules in every color scheme the host or project supports.
- It reads at 1920, 1440, 390, and 320px wide, or at the host's frame widths, with no horizontal scroll and no wrapped button label, and meets the brief's Phones constraints.
- It meets `DESIGN.md` § Motion and interaction, and the CSS has no `infinite` iteration count.
- For a new identity, none of the tells in `DESIGN.md` § Tells appear, unless the brief asked for them.

Send failures back to the same subagent, or fix them yourself if you built the page, with the failing check and its evidence. Then check again.

## 5. Report

Give the output path, the assumptions from step 1, the builder's summary, and each check with its result.
