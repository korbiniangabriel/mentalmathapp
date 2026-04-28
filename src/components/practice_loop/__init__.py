"""Custom Streamlit component that owns the practice question/answer loop.

This replaces the prior inline-JS hacks living inside ``practice_session.py``.
The component owns the entire client-side game loop: timer, current question,
input field, score / combo, skip and quit. Python only does setup (pre-generate
questions, configure mode) and teardown (persist results, route to results
page).

Hot-reload caveat (v1):
    Streamlit caches the served frontend assets aggressively. While iterating
    on ``frontend/index.html`` you must restart Streamlit (or clear its cache)
    to see your changes; a hard browser refresh alone is not enough.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

# ``declare_component`` with a ``path`` makes Streamlit serve the directory
# as static assets (index.html + anything you reference). No npm/yarn build.
_practice_loop_component = components.declare_component(
    name="practice_loop",
    path=_FRONTEND_DIR,
)


def practice_loop(
    *,
    questions: List[Dict[str, Any]],
    mode: str,
    duration_seconds: Optional[int] = None,
    question_count: Optional[int] = None,
    category_label: str = "",
    difficulty_label: str = "",
    key: str = "practice_loop",
    height: int = 640,
) -> Optional[Dict[str, Any]]:
    """Render the practice loop component.

    Args:
        questions: Pre-generated, JSON-safe questions. Each dict contains
            ``id``, ``text``, ``acceptable_answers`` (list[str]),
            ``correct_answer``, and ``needs_fraction_keyboard`` (bool).
        mode: One of ``"sprint"``, ``"marathon"``, ``"targeted"``.
        duration_seconds: Sprint duration. Required for sprint mode.
        question_count: Marathon/targeted count. Required for those modes.
        category_label: Display label (e.g. ``"Arithmetic"``).
        difficulty_label: Display label (e.g. ``"Adaptive"``).
        key: Streamlit component key. Bump it to force a fresh mount when a
            new session starts.
        height: iframe height in pixels.

    Returns:
        ``None`` while the loop is still running. Once the user finishes
        (timer hits 0, question count met, quit), returns a dict shaped::

            {
              "completed": True,
              "reason": "completed" | "quit" | "timeout",
              "results": [
                {"question_id": int, "user_answer": str, "is_correct": bool,
                 "was_skipped": bool, "time_taken": float},
                ...
              ],
            }
    """
    return _practice_loop_component(
        questions=questions,
        mode=mode,
        duration_seconds=duration_seconds,
        question_count=question_count,
        category_label=category_label,
        difficulty_label=difficulty_label,
        key=key,
        default=None,
        height=height,
    )
