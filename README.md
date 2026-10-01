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

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

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
