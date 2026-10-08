# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user types a plain-language query — "vintage graphic tee under $30, size M"
— and FitFindr searches a mock thrift-listings dataset for the best match,
suggests an outfit that pairs the item with pieces from the user's existing
wardrobe, and writes a short social-post-style caption about the find. If
nothing in the data matches the query, the agent stops and says what to
loosen (price ceiling or size) instead of guessing.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the loaded listings data for items matching a free-text description, optionally narrowed by size and a maximum price, and scores what's left by keyword overlap.
- **Inputs:** `description` (str) — keywords describing what the user wants (e.g. "vintage graphic tee"); `size` (str | None) — a size string matched case-insensitively against the listing's size field ("M" must match "S/M" but not "US 9" or "XL" via substring tricks), or `None` to skip size filtering; `max_price` (float | None) — inclusive price ceiling, or `None` to skip price filtering.
- **Returns:** A list of matching listing dicts, best match first, capped at `config.SEARCH_RESULT_LIMIT`. Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or `None`), `platform`.
- **When it has nothing:** Returns `[]` — an empty list, never `None` and never an exception — when no listing survives the filters or scores zero keyword overlap.

### `suggest_outfit`

- **What it does:** Calls the model to suggest one or two outfits pairing a candidate thrifted item with pieces from the user's existing wardrobe.
- **Inputs:** `new_item` (dict) — a listing dict for the item being considered; `wardrobe` (dict) — a wardrobe dict with an `items` key holding a list of owned-item dicts; the list may be empty.
- **Returns:** A non-empty string of outfit suggestions naming specific wardrobe pieces the user already owns.
- **When it has nothing:** If `wardrobe['items']` is empty, returns a non-empty string of general styling advice for the item instead — never `""` and never a raised exception.

### `create_fit_card`

- **What it does:** Calls the model to write a short caption, in the voice of a real social post rather than a product listing, about the item and its suggested outfit.
- **Inputs:** `outfit` (str) — the suggestion string returned by `suggest_outfit`; `new_item` (dict) — the listing dict for the item.
- **Returns:** A two-to-four sentence caption string that mentions the item, its price, and its platform exactly once each.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns the fixed string `"Can't create a fit card without an outfit suggestion."` instead of calling the model or raising.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` telling the user what to loosen (price ceiling or size), and stop — return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise, take the first result as `session["selected_item"]` and continue on to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::_parse_query`. One pattern
looks for `under`/`below`/`less than`/`max` followed by a number to set
`max_price`; another looks for the literal word `size` followed by a token
to set `size` (handles `"size M"`, `"size S/M"`, `"size XXS"`). Whatever text
is left over, with those matched phrases and stray `,`/`$` characters
stripped, becomes `description`.

**What moves through the session:** `query` and `wardrobe` are set once, at
the start, by `new_session()`. Then, in order: `parsed` (after parsing the
query), `search_results` (after `search_listings`), `selected_item` (the
first search result, or the loop stops here on empty), `outfit_suggestion`
(after `suggest_outfit`), `fit_card` (after `create_fit_card`). `error` stays
`None` unless the branch triggers.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two specific outfit ideas using the new Y2K baby tee and pieces from their existing wardrobe:

**Outfit 1: Casual Y2K Streetwear**
*   **Top:** Y2K Baby Tee (Butterfly Print)
*   **Bottoms:** Baggy straight-leg jeans, dark wash
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* This leans fully into the early 2000s aesthetic. The fitted, cropped butterfly tee creates a great Y2K-approved proportion balance when paired with baggy, dark-wash denim. Throwing on the black denim jacket and chunky white sneakers ties the color palette together effortlessly.

**Outfit 2: Elevated Retro-Casual**
*   **Top:** Y2K Baby Tee (Butterfly Print)
*   **Bottoms:** Wide-leg khaki trousers
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt, Black crossbody bag
*   *Why it works:* Pairing the ultra-feminine, pink-and-purple butterfly baby tee with wide-leg khaki trousers gives off a cool, high-low vintage vibe. Adding the black combat boots and brown leather belt grounds the lighter, pastel tones of the shirt and adds a nice edge to the outfit.

  Fit card: Found this cute Y2K baby tee on depop for just $18, and it's giving major early-2000s mall-goth nostalgia. I'm obsessed with the butterfly print and can't wait to style it with baggy low-rise jeans. It's the ultimate throwback piece for my summer rotation!

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'price': 18.0, 'size': 'S/M', 'platform': 'depop', ...}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'price': 24.0, 'size': 'L', 'platform': 'depop', ...}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'price': 15.0, 'size': 'S/M', 'platform': 'depop', ...}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'price': 19.0, 'size': 'L', 'platform': 'depop', ...}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'price': 27.0, 'size': 'W29', 'platform': 'poshmark', ...}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'price': 26.0, 'size': 'L', 'platform': 'depop', ...}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two specific outfit ideas using the vintage Levi's 501s and pieces from their existing wardrobe:

**Outfit 1: Casual & Sporty**
*   **Top:** White ribbed tank top
*   **Outerwear:** Black cropped zip hoodie (worn open or layered over the tank)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* The medium-wash Levi's add a nice contrast to the black hoodie and bag while matching the fresh, casual vibe of the white tank and sneakers.

**Outfit 2: Streetwear Edge**
*   **Top:** Oversized grey crewneck sweatshirt
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt (to pull the look together and define the waist with the tucked-in or semi-tucked sweatshirt)
*   *Why it works:* Pairing the classic 501s with the black denim jacket creates a cool, cohesive denim-on-denim look, while the combat boots and oversized grey crewneck give it an effortless, edgy streetwear feel.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Scored these vintage Levi's 501 jeans for just $38.0 on depop and I am officially never taking them off. Paired them with crisp white sneakers for that effortlessly cool '90s campus vibe. Breaking in old denim is a journey, but this wash is already pure perfection.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Help figuring out criteria 3–5 in `criteria.md` — I
  wasn't sure what to check for "state" (how do you even catch the
  same-item-reached-the-next-tool problem?) or for the fit card, since the
  model's wording changes every run.
- *What came back:* At first, clarifying questions instead of written
  criteria — "what would you compare to prove `suggest_outfit` got the same
  item `search_listings` picked?" and "of everything in the fit card spec,
  which part stays true regardless of wording?" — since the assignment says
  not to have a model write these outright. When I asked directly for drafts
  anyway, it gave three with reasoning attached.
- *What I changed:* Used the drafts as a starting point, not a final answer
  — went back through each one and adjusted the wording and numbers so I
  could actually defend them if asked "why this target and not a stricter
  one," since that part has to be mine.

**Moment 2**

- *What I asked for:* To test `create_fit_card` by running it three times on
  the same item, per the milestone instructions.
- *What came back:* Three word-for-word identical captions — which looked
  like a bug in the prompt, but the response identified it as one of two
  known causes in `config.py`: `CACHE_ENABLED` reusing an identical prompt's
  stored answer, or `TEMPERATURE` being `0.0`.
- *What I changed:* Nothing in the code — `TEMPERATURE` was already `0.9`,
  so I reran the same test with `AI201_CACHE=0` to isolate the cause. That
  produced three genuinely different captions, confirming the sameness was
  the cache working as designed while building, not a problem with
  `create_fit_card` itself.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

Produced by `run_eval.py::main`, full report committed at
`results/run_2026-10-07_2117_before.md` (53 model calls, 15606 prompt +
10523 output tokens). Criterion 5's scenario runs the full agent loop on one
query; the "across at least 3 different price ceilings" part of that
criterion is additionally checked directly against `tools.py::search_listings`
below, since `search_listings` is deterministic and reruns of one query
through `run_eval` can't exercise more than one ceiling value.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions price/platform, 2-4 sentences | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Price ceiling respected | 5 of 5 (≥3 ceilings) | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output, one try per criterion, as text:**

**Criterion 1** — `agent.py::run_agent`, Try 1, query `"vintage graphic tee under $30"`:

```
[1] search_listings (via MCP)
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] suggest_outfit
      out: Here are two specific outfit ideas using the new Y2K butterfly baby tee and pieces from your existing wardrobe…
[3] create_fit_card
      out: Scored the ultimate Y2K butterfly baby tee on depop for just $18.0! It's giving total early 2000s mall rat ene…

Fit card: Scored the ultimate Y2K butterfly baby tee on depop for just $18.0! It's giving total early 2000s mall rat energy, and I am so ready to live out my pop princess dreams.
```

**Criterion 2** — `agent.py::run_agent`, Try 1, query `"designer ballgown size XXS under $5"`:

```
[1] search_listings (via MCP)
      out: [] (empty)
[2] branch
      →    search_results empty — stopping before suggest_outfit

stopped early: yes — No listings matched — try raising max_price or dropping the size filter.
selected_item: (none)
search_results: 0
```

**Criterion 3** — `agent.py::run_agent` + `tools.py::suggest_outfit`. `run_eval.py` doesn't instrument what `suggest_outfit` actually receives, so this was checked directly with a spy standing in for `suggest_outfit`, 5 separate tries, query `"90s track jacket in size M"`:

```
try 1: session.selected_item.id='lst_004'  suggest_outfit received='lst_004'  SAME=True
try 2: session.selected_item.id='lst_004'  suggest_outfit received='lst_004'  SAME=True
try 3: session.selected_item.id='lst_004'  suggest_outfit received='lst_004'  SAME=True
try 4: session.selected_item.id='lst_004'  suggest_outfit received='lst_004'  SAME=True
try 5: session.selected_item.id='lst_004'  suggest_outfit received='lst_004'  SAME=True
```

**Criterion 4** — `tools.py::create_fit_card`, all 5 tries on the same item (`Y2K Baby Tee — Butterfly Print`, $18.0, depop), caching off:

```
Try 1: Scored the ultimate Y2K butterfly baby tee on depop for just $18.0! It's giving total early 2000s mall rat energy, and I am so ready to live out my pop princess dreams.
Try 2: Found the ultimate Y2K butterfly baby tee on depop for just $18.0, and I am obsessed with the nostalgic early-2000s mall-goth energy it brings to my closet. It's giving major 2004 pop-star-off-duty vibes when paired with baggy jeans and chunky sneakers. Can't wait to wear this tiny top on repeat all season!
Try 3: Scored this butterfly print Y2K baby tee on depop for just $18.0, and I am officially leaning all the way into the early-2000s off-duty model aesthetic. It fits like an absolute dream and goes with everything from baggy denim to utilitarian trousers. Trust me, you'll be seeing this in every mirror selfie for the foreseeable future.
Try 4: Found this exact Y2K baby tee with the cutest butterfly print scrolling on Depop for just $18. Honestly living out my early 2000s pop star dreams with how fitted and nostalgic it is. Going to style it with baggy low-rise denim and chunky sneakers for the ultimate casual street vibe.
Try 5: Score! Found this adorable butterfly print Y2K baby tee on depop for just $18.0, and it is giving major 2000s mall-rat energy. Can't wait to style it with baggy low-rise jeans and chunky sneakers for the ultimate nostalgic streetwear fit.
```

Every try names the price ($18/$18.0) and the platform (depop/Depop) and runs
2-3 sentences — within the 2-to-4 range — while the wording differs each time.

**Criterion 5** — `tools.py::search_listings`, direct calls (no model), 5 different price ceilings:

```
max_price=15   query='tee'        -> 1 results, prices=[15.0],             all <= ceiling: True
max_price=28   query='hoodie'     -> 1 results, prices=[26.0],             all <= ceiling: True
max_price=35   query='dress'      -> 1 results, prices=[30.0],             all <= ceiling: True
max_price=40   query='jeans'      -> 3 results, prices=[38.0, 36.0, 30.0], all <= ceiling: True
max_price=60   query='sneakers'   -> 2 results, prices=[48.0, 20.0],       all <= ceiling: True
```

Plus one full-loop confirmation, `agent.py::run_agent`, query `"jeans under $40"`,
all 5 tries: `search_results: 3`, `selected_item: Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)` — consistent with the direct check above.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Full three-tool run returns a fit card | 4 of 5 | MET (5/5) | All 5 tries in the "matching query completes" scenario show `stopped early: no` and a non-empty fit card in `results/run_2026-10-07_2117_before.md`. 5 passes clears the 4-of-5 bar with one to spare. |
| 2 | Empty search stops before tool 2 | 5 of 5 | MET (5/5) | All 5 tries show `stopped early: yes`, `search_results: 0`, `selected_item: (none)`, and the named-change message — never the fit card. |
| 3 | Item in session matches item passed on | 5 of 5 | MET (5/5) | A spy standing in for `suggest_outfit` recorded the id it actually received on 5 separate runs; compared against `session["selected_item"]["id"]` each time, all 5 matched. |
| 4 | Fit card mentions price/platform, 2-4 sentences | 5 of 5 | MET (5/5) | Read all 5 caption texts by hand: every one names the price ($18 or $18.0) and the platform (depop/Depop), and runs 2-3 sentences — inside the 2-4 range every time, with different wording each try. |
| 5 | Price ceiling respected | 5 of 5 (≥3 ceilings) | MET (5/5) | Checked `search_listings` directly at 5 different price ceilings ($15/$28/$35/$40/$60) — every returned listing's price was ≤ its ceiling — plus one full-loop rerun at $40, consistent across all 5 tries. |

**Diagnoses**

Nothing missed this run, so there's nothing to trace to a tool, a branch, the
session, or the model's output — but "nothing missed" isn't the same as
"every target was well-chosen," and it's worth being honest about which ones
actually earned their pass.

- **Criteria 2, 3, and 5** are checking deterministic code (the branch, the
  session plumbing, the price filter) with no model involved. A 5/5 there
  isn't luck — there's no mechanism by which they'd ever come out otherwise
  unless the code itself were broken. These targets are appropriately tight
  (5 of 5) and the passes are meaningful.
- **Criterion 4** targets 5 of 5 on model output and got it — the prompt's
  structural instructions (mention price, mention platform, stay 2-4
  sentences) held across 5 independent generations. That's a real signal
  about prompt reliability, not a guaranteed outcome.
- **Criterion 1 is the one I'd tighten.** I set its target at 4 of 5
  specifically because I expected *keyword-matching* misses — a matching
  query phrased in a way that doesn't share vocabulary with the listing
  data. But `run_eval.py` reruns the exact same query text 5 times, and
  `search_listings` is deterministic: the same query will always produce
  the same keyword overlap, every time. So this scenario, as built, can
  only ever show 5/5 or 0/5 — it was never actually capable of landing on
  3/5 or 4/5, which means the slack I built into the target was never
  being exercised by this test. If I were tightening one thing, I'd either
  raise this target to 5 of 5 (since the deterministic parts can't
  legitimately produce a partial score) or change the scenario to run 5
  *different* phrasings of a matching query instead of rerunning one — the
  second option is the one that would actually test what I originally
  meant by "some phrasings will miss."

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are two specific outfit ideas using the new Y2K baby tee and pieces from their existing wardrobe:  **Outf…
      →    wardrobe: 10 item(s)
[3] create_fit_card
      in:  Here are two specific outfit ideas using the new Y2K baby tee and pieces from their existing wardrobe:  **Outf…
      out: Found this cute Y2K baby tee on depop for just $18, and it's giving major early-2000s mall-goth nostalgia. I'm…
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] branch
      →    search_results empty — stopping before suggest_outfit

  No listings matched — try raising max_price or dropping the size filter.
```

The empty-search trace stops at step 2 — the branch — instead of continuing to
`suggest_outfit` and `create_fit_card` the way the happy path does.

**On the MCP move:** `search_listings` is now called through
`mcp_client.call_tool("search_listings", ...)` in `agent.py::run_agent`
instead of being imported directly from `tools.py`. The trace step is
labeled `search_listings (via MCP)` so the MCP hop is visible in the trace
itself, not just in the source. Behavior was unchanged — the happy-path and
empty-search example runs produced byte-identical output before and after
the move.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** Added a small category-synonym table to
`tools.py::_listing_text` (`_CATEGORY_SYNONYMS`), scoped to exactly the gap
found in testing: for listings in the `"shoes"` category, the words
`"footwear"`, `"trainers"`, `"sneaker"`, and `"shoe"` are now included in the
text `search_listings` scores keyword overlap against, alongside the
title/description/category/style_tags/colors that were already there. No
other category got a synonym table — only the one the diagnosis actually
found broken.

**Which failure it was meant to fix:** Criterion 1, diagnosed in Milestone 4.
Once the test was corrected to use 5 different realistic phrasings instead
of rerunning one, it surfaced a real miss (3/5, pre-fix): `"trainers for
walking"` and `"footwear for everyday"` both returned zero results from
`search_listings`, even though the catalog has four shoe listings, because
neither word ever appears in those listings' title, description, or
style_tags — plain keyword overlap has no way to know "trainers" means
"sneakers."

**Before (pre-fix), criterion 1 only — 5 different phrasings, one try each,**
`tools.py::search_listings` (direct calls, no model):

```
'vintage graphic tee'        -> 10 results, top: Y2K Baby Tee — Butterfly Print
'a nice pair of jeans'       -> 3 results,  top: Vintage Levi's 501 Jeans — Medium Wash
'90s track jacket'           -> 10 results, top: 90s Track Jacket — Navy/White Stripe
'trainers for walking'       -> 0 results  (NO MATCH)
'footwear for everyday'      -> 0 results  (NO MATCH)
```
3/5 — MISSED against the 4-of-5 target.

**After (post-fix), same 5 phrasings, run through the full loop,**
`agent.py::run_agent`:

```
PASS: 'vintage graphic tee under $30'      -> item='Y2K Baby Tee — Butterfly Print'
PASS: 'a nice pair of jeans under $40'     -> item="Vintage Levi's 501 Jeans — Medium Wash"
PASS: '90s track jacket in size M'         -> item='90s Track Jacket — Navy/White Stripe'
PASS: 'trainers for walking under $50'     -> item='Platform Sneakers — White Chunky Sole'
PASS: 'footwear for everyday under $50'    -> item='Platform Sneakers — White Chunky Sole'
5/5 passed
```
5/5 — MET, and this time the number means something: the test can actually
land anywhere from 0/5 to 5/5 depending on phrasing, and it came out on top
because the specific gap found was fixed, not because the test is incapable
of failing.

### Run Log — After (criteria 2–5, full suite rerun)

Produced by `run_eval.py::main`, full report committed at
`results/run_2026-10-07_2131_after.md` (42 model calls, 9988 prompt + 7625
output tokens).

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card (5 phrasings — see above) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions price/platform, 2-4 sentences | 5 of 5 | PASS | **FAIL** | PASS | PASS | PASS | MISSED (4/5) |
| 5. Price ceiling respected | 5 of 5 (≥3 ceilings) | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

This run happened to land during a stretch of **real 503 "model currently
experiencing high demand" errors** from the Gemini API — 10 of the 30 model-
calling tries across all scenarios in this run hit one. That's not something
I caused or could control, and it's not what the unit 4 "model unavailable"
failure mode normally simulates (a bad key) — it's the same `ModelUnavailable`
path, triggered by a real transient outage instead of a corrupted key.

**Criterion 3** still came back 5/5 despite two of its tries hitting a 503,
because the state criterion only asks whether the same item reached
`suggest_outfit` — and it did, in both cases, before the model call itself
failed. `session["selected_item"]` is passed into `suggest_outfit` as a
plain Python argument before `generate()` ever runs, so a failure inside the
model call can't retroactively change what was passed in.

**Criterion 4 genuinely missed (4/5)**, and this is a real diagnosis, not a
dismissal: try 2's `create_fit_card` call hit the 503, so `session["fit_card"]`
stayed `None` for that try — no caption was produced to check against the
"mentions price and platform, 2-4 sentences" rule at all. The other 4 tries
all passed cleanly (checked by hand, same as the before run). The mechanism
here is `generate.py`'s retry logic: `_retry_delay`'s `rate_limited` check
only matches 429/"rate limit" messages, so a 503 is raised as
`ModelUnavailable` immediately, with no retry — reasonable for a bad API key
(retrying forever is wrong), but it means a transient, recoverable outage is
currently treated the same as a permanent one. That's a real, separate
finding — see **What's Still Broken**.

**Did it help, and how do I know:** Yes, on the thing it targeted. The real
test for criterion 1 (5 different phrasings, not 5 reruns of one) went from
3/5 to 5/5 after adding the shoe-category synonyms — a measured improvement
on the actual failure found, not a guess. Criteria 2, 3, and 5 are unaffected
by the change in principle (none of them touch `_listing_text` or the shoes
category) and stayed at 5/5. Criterion 4's miss this run is unrelated to the
fix — same prompt, same tool, no code touched there — and traces to a
transient external outage rather than anything the improvement broke or was
meant to address.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
