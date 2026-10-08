# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** `search_listings` scores matches by plain keyword
overlap, not meaning — a query that a human would call a match can still miss
every listing if it phrases things differently than the data does (a
synonym, a brand name not in any `style_tags`). That's where the slack
belongs. Once an item is actually selected, the rest of the loop is
deterministic code, so I'm not using this number to excuse a flaky
`suggest_outfit` or `create_fit_card` — the looseness is specifically about
keyword matching, nothing downstream of it.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** Unlike criterion 1, this path never involves keyword
ambiguity or the model — it's a single deterministic branch in `run_agent`:
either `search_results` is empty or it isn't. There's nothing probabilistic
for the 5th try to fail on, so if this ever misses, it's a bug in the branch
itself (e.g. calling `suggest_outfit` anyway, or forgetting to set
`session["error"]`), not expected variance.

---

## 3. Something about state

Given a matching query, the `id` of the listing in `session["selected_item"]`
is identical to the `id` of the listing dict actually passed as `new_item` to
`suggest_outfit` and to `create_fit_card` — in 5 of 5 tries.

**Why this target:** This is plain data plumbing, not a model call — there's
no source of randomness that would make the id change on the way from
`search_listings` to the other two tools. If this ever fails, it isn't noise,
it's a bug in the loop (e.g. re-running search, or indexing the wrong
result), so 4 of 5 would just be hiding a real defect behind a passing grade.

---

## 4. Something about the fit card

For the same item run through `create_fit_card` five separate times, with
caching off so each try is a real generation, every resulting caption
mentions the item's price and its platform at least once each, and is 2 to 4
sentences long — in 5 of 5 tries. The wording itself is allowed to differ
every time.

**Why this target:** Wording is supposed to vary — that's `TEMPERATURE` doing
its job, and five word-for-word identical captions would actually be the
failure mode (the cache serving a stored answer instead of generating a new
one). But mentioning price, mentioning platform, and staying within a
sentence range are instructions I give the model in the prompt, not creative
choices I'm leaving up to it, so I expect the model to follow them every
time, not just most of the time.

> **Revised before running (unit 4, Milestone 3):** Originally written as "5
> different items." Changed to "the same item, 5 separate generations"
> because that's what the test harness (`run_eval.py`) actually produces —
> it reruns one scenario N times, it doesn't run N different scenarios as
> one criterion. Testing repeated generations of one item is still a fair
> test of whether the model reliably follows the prompt's structural
> instructions; it just fits the tool that measures it.

---

## 5. Your choice

Given a `max_price`, every listing dict `search_listings` returns has
`price <= max_price` — in 5 of 5 tries, across at least 3 different price
ceilings.

**Why this target:** This is a plain numeric comparison in code that never
touches the model, so there's no reasonable way for it to pass sometimes and
fail other times — if it misses even once, that's a filtering bug (e.g. the
comparison direction is backwards, or the check is skipped for one listing),
not variability I should tolerate.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
