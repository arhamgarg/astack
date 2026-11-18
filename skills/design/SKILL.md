---
name: design
description: Use when asked to design, build, or mock up a webpage, HTML page, landing page, site, or page component.
---

# Frontend design

## 1. Write the brief

- Subject: what the page is for, who reads it, and its main job. Where the request leaves something open, choose a concrete answer consistent with `DESIGN.md` and note it as an assumption.
- Content: the real copy, data, and links the user supplied. The subagent writes everything else.
- Constraints: the stack, required sections, and visual direction the user set. Follow the existing project's stack, design tokens, components, and asset conventions, and reuse them before adding new ones. A standalone page defaults to one self-contained `index.html` with inline CSS and JS and web fonts from a CDN.
- Phones: adapt the layout and main task for phones by default. Text stays readable, touch targets are at least 44px, controls stay usable in a short viewport with the keyboard open, main actions stay reachable within safe areas, and narrow screens cause no horizontal scrolling.
- Output: the path the user asked for, or the project's routes and components. A standalone page with no requested location goes in a new folder named after the page, with its assets beside it.

## 2. Send it to the subagent

Start one worker on the newest Claude Fable or Opus model (the `fable` or `opus` alias where the harness accepts one, otherwise the highest Fable version listed) at high reasoning effort. Include the absolute path of `DESIGN.md` and send the brief with this:

> Read the design reference at the path in this brief in full and follow its process, building at the output path. Report in at most five lines: the output path, the defining layout decision, the palette values and typefaces, what the plan review changed, and anything unfinished.

## 3. Check the result

- The page exists at the requested path or route and opens without console errors.
- It meets `DESIGN.md` § Dark mode.
- It reads at 1920, 1440, 390, and 320px wide with no horizontal scroll and no wrapped button label, and meets the brief's Phones constraints.
- Every control has hover and keyboard focus states, and every data region has loading, empty, error, and long-text states.
- Motion stops under `prefers-reduced-motion: reduce`.
- No text meant to be read is under 13px.
- It meets `DESIGN.md` § Motion and interaction, and the CSS has no `infinite` iteration count.
- On a public page, the content is visible with JavaScript off.
- None of the tells in `DESIGN.md` § Tells appear, unless the brief asked for them.

Use a browser or preview tool for the rendering checks when you have one, and otherwise record them as not performed. Send failures back to the same subagent with the failing check and its evidence, then check again.

## 4. Report

Give the output path, the assumptions from step 1, the subagent's summary, and each check with its result.
