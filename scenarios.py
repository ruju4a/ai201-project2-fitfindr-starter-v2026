"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match — rerun 5 times by run_eval. Kept as a
        # sanity check (completes without crashing), but demoted from
        # criterion 1: search_listings is deterministic, so rerunning this
        # exact text 5 times can only ever show 5/5 or 0/5 — it can't
        # exercise the "some phrasings will miss" risk the criterion is
        # actually about. See criteria.md's revision note under criterion 1
        # and the Loop Trace / Improvement sections in the README for the
        # real criterion-1 evidence (5 different phrasings, run once each).
        "name": "matching query completes (sanity check, not criterion 1)",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": None,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # State: does session["selected_item"] stay the one thing that
        # reaches suggest_outfit and create_fit_card. Any matching query
        # works here — what's being checked is what ends up in the session,
        # not what the user typed. Criterion 3.
        "name": "state: selected item consistent",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Fit card structure: same item, regenerated five separate times
        # with caching off, so wording differs each try but the structural
        # requirements (price, platform, 2-4 sentences) should hold every
        # time regardless. Criterion 4.
        "name": "fit card mentions price, platform, stays 2-4 sentences",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Price ceiling respected, full loop. Criterion 5. search_listings is
        # deterministic, so 5 reruns of one query are 5 identical checks of
        # the <= comparison, not 5 independent ones — the "at least 3
        # different price ceilings" part of this criterion is additionally
        # verified with a direct, model-free call to search_listings at five
        # ceilings (tee<=15, hoodie<=28, dress<=35, jeans<=40, sneakers<=60),
        # pasted as real output under this criterion in the README. This
        # scenario exists so the claim also holds through the full agent
        # loop, not only when the tool is called directly.
        "name": "price ceiling respected, full loop",
        "query": "jeans under $40",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
