---
name: unslop
description: Use whenever writing prose for a person, such as a reply, commit message, PR or issue text, doc, readme, email, or message.
---

# Unslop

Write so a tired reader understands on the first read. Check each sentence against the rules below and rewrite it in plain language. If a rule makes a sentence worse, fix it another way or leave it. Cut any sentence that names neither a mechanism nor a number, would be true in another project, puts the reasoning before the decision, or tells the reader what they already know. You are done when no sentence breaks a rule and every fact survives.

## Words

1. **AI vocabulary.** Additionally, crucial, delve, enhance, fostering, garner, interplay, intricate, landscape, pivotal, showcase, tapestry, testament, underscore, vibrant. Use plain words.
2. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, nexus, primitive, harness, surface, bedrock, scaffolding, paradigm, gold-plating, ratchet, endgame, north star, flywheel. Use the concrete word: "ratchet" becomes "a limit that only tightens". A named pattern is fine once the text says what it means.
3. **Mannered prose.** Aphorisms, rhetorical fragments, personified objects ("the plan holds it"), figurative verbs ("rides along"), idioms, Latin abbreviations, and stock framing. Say what you mean.
4. **The plain word.** "Utilize" becomes "use", "facilitate" becomes "help", "in the event that" becomes "if". Undo nominalizations and phrasal verbs: "perform validation" becomes "validate", "spin up" becomes "start".
5. **Fancy ways to say "is".** "Serves as", "stands as", "boasts", "features". Say "is" or "has".
6. **Filler.** "In order to" becomes "to". Delete "it is important to note that". Never write "simply", "easy", "quickly", or "please" in an instruction.
7. **Hedging.** "Could potentially possibly be argued that it might" becomes "may".
8. **Adverbs propping up verbs.** "Runs quickly" becomes "is fast" or the number. "Significantly improves" becomes the measured change.
9. **Trailing -ing phrases.** "Highlighting...", "ensuring...", "reflecting...". Delete them or state the fact. Avoid any "-ing" word that reads two ways.
10. **One name per thing.** Calling one meeting "the sync" and "the weekly review" teaches two things. Pick a name and repeat it. Give each word one meaning too.

## Sentences

11. **What it does, not how it feels.** "A friendly form" names a feeling. Name the mechanism or a number: "the form keeps what you typed after an error".
12. **Active voice and direct commands.** "Invoices are approved" becomes "the finance lead approves invoices". Write instructions as commands: "Install the component", not "the component must be installed". Use the passive only when the actor is unknown or doesn't matter.
13. **One idea per sentence.** Split any sentence the reader has to backtrack through, any instruction over about 20 words, and any other sentence over about 25.
14. **Over-compression.** Dropped articles, verbless fragments, arrows, and abbreviations make the reader decode. "Form rejects bad date → error shown" becomes "The form rejects a bad date and shows an error." Keep small structural words such as "that".
15. **Conditions first.** Put the condition, warning, or common case before the instruction: "To delete the document, click Delete."
16. **"Only" and "not" in place.** Keep them next to the word they change. "Only fails on growth" and "fails only on growth" mean different things.
17. **Clear pronouns.** Every "it", "they", and "this" points at one obvious noun. Never use "this" or "which" for a whole clause.
18. **Complete series.** "Week 1 moves the files and week 2 the contacts" leaves week 2 without a verb. "The editor and author" reads as one thing, so repeat the article when there are two.
19. **Unambiguous "and" and "or".** When a sentence can group two ways, use "both...and", "either...or", or "if...then".
20. **Long noun strings.** "The travel expense approval policy document" becomes "the document that sets the policy for approving travel expenses".
21. **Slashes and "(s)".** Write "a, b, or both", not "a/b" or "and/or", and a real plural, not "file(s)".
22. **Forced patterns.** Use the natural number of items instead of three, list topics instead of "from X to Y", and state the point instead of "not just X but Y".
23. **Vague sources and generic endings.** "Experts believe" and "the future looks bright" say nothing. Name the source or state the fact. Cut a closing sentence that adds no fact.
24. **Monotony.** Vary sentence length on purpose, and don't start consecutive sentences with the same words.
25. **Define a term the reader may not know** once, in passing, where it first matters.

## Punctuation and formatting

26. **No dashes as punctuation.** No em dashes or en dashes anywhere you write, and no hyphens used as dashes. End the sentence or use a comma. Use periods, not semicolons. Remove every em or en dash in a file you edit.
27. **Colons** go only before a list or an example, or after a bold lead-in.
28. **Parentheses** hold a complete phrase or become a sentence.
29. **Bold sparingly.** Don't bold every proper noun, and never pair a bold label and colon with a line that repeats it ("**Performance:** Performance improved"). Bold a lead-in only when the text after its colon adds what the lead-in doesn't say.
30. **Headings** are in sentence case and carry the point ("Pick the mode first", not "Modes"). A task heading is a verb phrase and a concept heading a noun phrase. Use one h1 and don't skip levels.
31. **Lists** are numbered for sequences and bulleted otherwise, introduced by a full sentence, with parallel items. No "etc.". Say up front when a list is partial.
32. **Bold for UI elements.** Link text names the destination, never "click here". Prefer a sentence of context over a link away.

## Tone

33. **Chatbot phrases.** Delete "I hope this helps!", "Let me know if...", "Certainly!", and "Found the smoking gun!".
34. **Announcements.** Delete "we will soon support". Use "will" only for what actually happens later.

## Documents

35. **One document, one purpose.** A tutorial teaches by doing, a how-to solves one task for someone competent, a reference describes completely and without opinion, and an explanation answers one real "why" with the decisions and trade-offs. Don't mix them. Split and link.
36. **Leave unchanged sentences alone** between edits.

## Re-explaining

37. **When the reader did not follow** ("what do you mean", "explain"), explain it as you would to a smart colleague who missed the conversation. Open with the point and what it means for them: what happened, where things stand, and what they need to decide or do. Explain the source rather than rewriting it, and make the explanation shorter.
38. **Keep everything that changes what the reader would do:** exact names, commands, and values, and every failure, caveat, and open question. Sound no more certain or positive than the source. If rereading shows the earlier message was wrong, say so and correct it.
