"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── query parsing ─────────────────────────────────────────────────────────────

_PRICE_RE = re.compile(r"(?:under|below|less than|max)\s*\$?(\d+(?:\.\d+)?)", re.I)
_SIZE_RE = re.compile(r"\bsize\s+([A-Za-z0-9/.]+)", re.I)


def _parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a max_price out of a free-text query.

    Regex, not the model — the phrasing this project uses is narrow enough
    ("... under $30", "... size M") that a couple of patterns cover it, and a
    regex is something you can test without spending a model call on it.

    "under $30" / "below 30" / "less than $30" / "max $30" sets max_price.
    "size M" (or "size S/M", "size XXS", ...) sets size.
    Whatever's left, with those phrases and stray commas/$ stripped, is the
    description handed to search_listings.
    """
    max_price = None
    match = _PRICE_RE.search(query)
    if match:
        max_price = float(match.group(1))

    size = None
    match = _SIZE_RE.search(query)
    if match:
        size = match.group(1)

    description = _PRICE_RE.sub(" ", query)
    description = _SIZE_RE.sub(" ", description)
    description = re.sub(r"[,$]", " ", description)
    description = re.sub(r"\s+", " ", description).strip()

    return {"description": description, "size": size, "max_price": max_price}


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    trace.start_trace()
    session = new_session(query, wardrobe)
    count = 0

    count += 1
    trace.check_iterations(count)
    session["parsed"] = _parse_query(query)

    search_inputs = {
        "description": session["parsed"]["description"],
        "size": session["parsed"]["size"],
        "max_price": session["parsed"]["max_price"],
    }
    results = call_tool("search_listings", search_inputs)
    session["search_results"] = results
    trace.step("search_listings (via MCP)", inputs=search_inputs, returned=results)

    if not results:
        session["error"] = (
            "No listings matched — try raising max_price or dropping the "
            "size filter."
        )
        trace.step(
            "branch", note="search_results empty — stopping before suggest_outfit"
        )
        return session

    session["selected_item"] = results[0]

    try:
        count += 1
        trace.check_iterations(count)
        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"], session["wardrobe"]
        )
        trace.step(
            "suggest_outfit",
            inputs=session["selected_item"],
            returned=session["outfit_suggestion"],
            note=f"wardrobe: {len(session['wardrobe'].get('items') or [])} item(s)",
        )

        count += 1
        trace.check_iterations(count)
        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"], session["selected_item"]
        )
        trace.step(
            "create_fit_card",
            inputs=session["outfit_suggestion"],
            returned=session["fit_card"],
            note=f"item: {session['selected_item']['title']}",
        )
    except ModelUnavailable as exc:
        session["error"] = str(exc)
        trace.step("model call", note=f"ModelUnavailable — stopping: {exc}")

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
