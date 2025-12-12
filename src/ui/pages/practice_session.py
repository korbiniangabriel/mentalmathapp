"""Practice session page - core game interface."""
import json
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from src.models.session import SessionConfig
from src.game_logic.session_manager import SessionManager
from src.ui.components import (
    question_display, combo_meter, feedback_display,
    countdown_timer, progress_bar_with_label
)


def show_practice_session(db_manager):
    """Display practice session page.
    
    Args:
        db_manager: Database manager instance
    """
    # Initialize session manager
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager(db_manager)
    
    # Initialize or get session state
    if 'active_session' not in st.session_state or st.session_state.active_session is None:
        # Get config from either mode selection or quick mode
        if 'session_config' in st.session_state:
            config_dict = st.session_state.session_config
        elif 'quick_mode' in st.session_state:
            config_dict = st.session_state.quick_mode
        else:
            st.error("No session configuration found")
            if st.button("← Home"):
                st.session_state.page = "home"
                st.rerun()
            return
        
        # Create SessionConfig object
        config = SessionConfig(
            mode_type=config_dict['mode_type'],
            category=config_dict['category'],
            difficulty=config_dict['difficulty'],
            duration_seconds=config_dict.get('duration_seconds'),
            question_count=config_dict.get('question_count')
        )
        
        # Start session
        st.session_state.active_session = st.session_state.session_manager.start_session(config)
        st.session_state.last_result = None
        st.session_state.show_feedback = False
        st.session_state.feedback_time = None
    
    session = st.session_state.active_session
    
    # Check if session is complete
    if session.is_complete:
        summary = st.session_state.session_manager.end_session(session)
        st.session_state.session_summary = summary
        st.session_state.active_session = None
        st.session_state.page = "results"
        st.rerun()
    
    # Top Bar - simplified 3 columns for mobile
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if session.config.mode_type == 'sprint':
            elapsed = (datetime.now() - session.start_time).total_seconds()
            remaining = int(session.config.duration_seconds - elapsed)
            if remaining <= 0:
                session.is_complete = True
                st.rerun()
            countdown_timer(remaining)
        else:
            elapsed = int((datetime.now() - session.start_time).total_seconds())
            st.metric("⏱️", f"{elapsed//60}:{elapsed%60:02d}")
    
    with col2:
        if session.config.mode_type in ['marathon', 'targeted']:
            total = session.config.question_count
            current = len(session.questions_answered)
            st.metric("📝", f"{current}/{total}")
        else:
            st.metric("📝", len(session.questions_answered))
    
    with col3:
        if st.button("❌", help="Quit"):
            if st.session_state.get('confirm_quit', False):
                session.is_complete = True
                st.rerun()
            else:
                st.session_state.confirm_quit = True
                st.rerun()
    
    # Score display - compact
    st.markdown(f"**🏆 {session.total_score:,}**")
    
    if st.session_state.get('confirm_quit', False):
        st.warning("⚠️ Click ❌ again to quit")
    
    # Combo meter
    if session.combo_count > 0:
        combo_meter(session.combo_count)
    
    st.markdown("---")
    
    # Show feedback if available (only used for incorrect/skip flows)
    if st.session_state.show_feedback and st.session_state.last_result:
        result = st.session_state.last_result

        # If somehow a correct result lands here, immediately continue.
        # (Streamlit won't auto-rerun on a timer, so we avoid "press Next" for correct answers.)
        if result.is_correct:
            st.session_state.show_feedback = False
            st.session_state.last_result = None
            st.session_state.feedback_time = None
            st.session_state.confirm_quit = False
            st.toast("✅ Correct!")
            st.rerun()

        feedback_display(
            result.is_correct,
            result.question.correct_answer,
            result.time_taken
        )

        # Manual next button (kept for incorrect/skip)
        if st.button("➡️ Next", use_container_width=True):
            st.session_state.show_feedback = False
            st.session_state.last_result = None
            st.session_state.feedback_time = None
            
            if st.session_state.session_manager.check_session_end(session):
                session.is_complete = True
            
            st.rerun()
    
    else:
        # Show current question
        if session.current_question:
            question_display(session.current_question)

            # If the text-input on_change callback already submitted an answer in this rerun,
            # we must NOT also submit via the Enter button, otherwise the same answer can be
            # applied to the *next* question (appearing like "correct answer graded wrong").
            mm_skip_enter_submit = st.session_state.pop("_mm_skip_enter_submit", False)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Answer input with auto-submit on correct answer
            def _normalize_answer(raw: str) -> str:
                """Normalize raw input into something the validator expects."""
                if raw is None:
                    return ""
                s = str(raw).strip()
                # Normalize common locale punctuation variants (e.g. iOS numpad in some locales)
                s = (
                    s.replace("，", ",")  # full-width comma
                    .replace("،", ",")   # arabic comma
                    .replace("٬", ",")   # arabic thousands separator
                    .replace("٫", ".")   # arabic decimal separator
                )
                # Safety: if the ",," shortcut leaked into the backend somehow, strip only the trailing token.
                if s.endswith(",,"):
                    s = s[:-2].rstrip()
                if s.endswith(".."):
                    s = s[:-2].rstrip()
                # Most important: if the submit shortcut was caught on keydown, the input often ends with a single
                # trailing ',' or '.' (because we prevent the 2nd key from being inserted). Strip that too.
                if s.endswith(",") or s.endswith("."):
                    s = s[:-1].rstrip()

                # Heuristic: treat a single comma as decimal separator when it looks like "12,3" / "12,34".
                # (Avoid converting thousands like "1,000".)
                if s.count(",") == 1 and "." not in s:
                    left, right = s.split(",", 1)
                    if left.lstrip("-").isdigit() and right.isdigit() and len(right) <= 2:
                        s = f"{left}.{right}"
                return s

            def soft_check_answer():
                """Auto-advance ONLY when the current input is correct (never penalize partial input)."""
                answer = _normalize_answer(st.session_state.answer_input_field)
                if not answer:
                    return

                is_correct = st.session_state.session_manager.validator.validate(
                    answer,
                    session.current_question,
                )
                if not is_correct:
                    return

                # Correct answer: immediately go to next question (no "Next" step)
                # Also: if this rerun was triggered by clicking the Enter button, suppress the
                # button handler later in the script to avoid a double-submit.
                st.session_state._mm_skip_enter_submit = True
                st.session_state.session_manager.submit_answer(session, answer)
                st.session_state.confirm_quit = False
                # Streamlit (1.52+) disallows modifying widget state after instantiation,
                # so we schedule a clear for the next rerun.
                st.session_state._mm_next_answer_value = ""
                st.session_state._mm_clear_answer = True
                st.toast("✅ Correct!")
                st.rerun()

            def submit_current_answer(answer_value: str | None = None):
                """Explicit submit (Enter / ,,) — submits even if wrong, showing feedback if needed."""
                raw = st.session_state.answer_input_field if answer_value is None else answer_value
                answer = _normalize_answer(raw)
                result = st.session_state.session_manager.submit_answer(session, answer)
                st.session_state.confirm_quit = False
                # Schedule clear for next rerun (safe with Streamlit widget rules)
                st.session_state._mm_next_answer_value = ""
                st.session_state._mm_clear_answer = True

                if result.is_correct:
                    st.toast("✅ Correct!")
                    st.rerun()
                else:
                    st.session_state.last_result = result
                    st.session_state.show_feedback = True
                    st.session_state.feedback_time = datetime.now()
                    st.rerun()

            def handle_answer_change():
                """Single handler for input commits (Enter / blur / JS-triggered commit).

                - If user ends with ',,' or '..', treat it as explicit submit.
                - Otherwise, do a soft-check auto-advance only when correct.
                """
                raw = st.session_state.get("answer_input_field", "")
                raw_str = "" if raw is None else str(raw)
                trimmed = raw_str.strip()
                if trimmed.endswith(",,") or trimmed.endswith(".."):
                    # This is an explicit submit triggered by the input itself. If the user also clicked
                    # the Enter button in the same frontend interaction, suppress the button handler.
                    st.session_state._mm_skip_enter_submit = True
                    submit_current_answer(raw_str)
                elif trimmed.endswith(",") or trimmed.endswith("."):
                    # On some mobile keyboards, typing punctuation can trigger a "commit" event.
                    # If we auto-advance on a single trailing comma/dot (e.g. "838,"), the session can advance
                    # before the user finishes the ",," shortcut, causing the *next* question to be graded wrong.
                    return
                else:
                    soft_check_answer()

            def _should_allow_fraction_keyboard() -> bool:
                """Return True if this question likely needs '/' input."""
                q = session.current_question
                try:
                    acceptable = q.acceptable_answers or []
                except Exception:
                    acceptable = []
                # If any acceptable answer contains a '/', user needs the full keyboard.
                return any('/' in str(a) for a in acceptable)
            
            # Answer input without form (for auto-submit functionality)
            # If we need to programmatically change the widget's value, do it BEFORE instantiating the widget.
            # This avoids StreamlitAPIException in newer Streamlit versions.
            if "_mm_next_answer_value" in st.session_state:
                st.session_state.answer_input_field = st.session_state.pop("_mm_next_answer_value")

            # One-shot "clear DOM input" flag used by the small JS patch below.
            mm_clear_answer = st.session_state.pop("_mm_clear_answer", False)

            answer = st.text_input(
                "Answer:",
                key="answer_input_field",
                placeholder="Enter answer...",
                label_visibility="collapsed",
                help="Type your answer - it will auto-submit when correct!",
                on_change=handle_answer_change
            )

            # Mobile UX: force iOS to open numeric keypad for numeric answers.
            # Streamlit doesn't expose input attributes like inputmode/type directly,
            # so we patch the rendered DOM input via a tiny HTML component.
            if _should_allow_fraction_keyboard():
                desired_type = "text"
                desired_inputmode = "text"
                desired_step = ""
            else:
                # Use type="text" + inputmode="decimal" to keep the numeric keypad
                # without triggering browser "invalid number" behavior (which can drop the value on commas).
                desired_type = "text"
                desired_inputmode = "decimal"
                desired_step = ""

            components.html(
                f"""
                <script>
                (function() {{
                  const LABEL = "Answer:";
                  const MODE = {json.dumps(desired_inputmode)};
                  const TYPE = {json.dumps(desired_type)};
                  const STEP = {json.dumps(desired_step)};
                  const SHOULD_CLEAR = {json.dumps(mm_clear_answer)};
                  const EXPECTED_ANSWERS = {json.dumps([str(a) for a in (session.current_question.acceptable_answers or [])])};
                  const QUESTION_TOKEN = {json.dumps(f"{session.current_question.question_text}|{session.current_question.correct_answer}")};

                  function _mmNormalizeForCompare(raw) {{
                    try {{
                      if (raw === null || raw === undefined) return '';
                      let s = String(raw).trim();
                      // Match server-side locale punctuation normalization
                      // (Avoid replaceAll for older Safari)
                      s = s.replace(/，/g, ",")
                           .replace(/،/g, ",")
                           .replace(/٬/g, ",")
                           .replace(/٫/g, ".");
                      return s;
                    }} catch (e) {{
                      return String(raw || '').trim();
                    }}
                  }}

                  function _mmParseFraction(text) {{
                    try {{
                      const s = _mmNormalizeForCompare(text);
                      if (!s.includes('/')) return null;
                      const parts = s.split('/');
                      if (parts.length !== 2) return null;
                      const n = Number(parts[0].trim());
                      const d = Number(parts[1].trim());
                      if (!Number.isFinite(n) || !Number.isFinite(d) || d === 0) return null;
                      return n / d;
                    }} catch (e) {{
                      return null;
                    }}
                  }}

                  function _mmExtractPct(text) {{
                    try {{
                      const s0 = _mmNormalizeForCompare(text);
                      if (!s0) return null;
                      if (s0.endsWith('%')) {{
                        const n = Number(s0.slice(0, -1));
                        return Number.isFinite(n) ? n : null;
                      }}
                      const n = Number(s0.replace(/,/g, ''));
                      if (!Number.isFinite(n)) return null;
                      if (n >= 0 && n <= 1) return n * 100;
                      if (n >= -100 && n <= 100) return n;
                      return null;
                    }} catch (e) {{
                      return null;
                    }}
                  }}

                  function _mmParseNumber(text) {{
                    try {{
                      let s = _mmNormalizeForCompare(text);
                      if (!s) return null;
                      // Heuristic: if a single comma looks like decimal separator (12,3 / 12,34), convert to dot.
                      if ((s.split(',').length - 1) === 1 && !s.includes('.')) {{
                        const [left, right] = s.split(',', 2);
                        const leftOk = /^[+-]?\d+$/.test(left.trim());
                        const rightOk = /^\d+$/.test(right.trim()) && right.trim().length <= 2;
                        if (leftOk && rightOk) s = `${{left.trim()}}.${{right.trim()}}`;
                      }}
                      s = s.replace(/,/g, '');
                      const n = Number(s);
                      return Number.isFinite(n) ? n : null;
                    }} catch (e) {{
                      return null;
                    }}
                  }}

                  function _mmIsCorrectLocally(userRaw, expectedList) {{
                    const user = _mmNormalizeForCompare(userRaw);
                    if (!user) return false;

                    const expList = Array.isArray(expectedList) ? expectedList : [];

                    // Exact match (case-insensitive)
                    for (const expRaw of expList) {{
                      const exp = _mmNormalizeForCompare(expRaw);
                      if (exp && user.toLowerCase() === exp.toLowerCase()) return true;
                    }}

                    // Percentage formats
                    for (const expRaw of expList) {{
                      const up = _mmExtractPct(user);
                      const ep = _mmExtractPct(expRaw);
                      if (up !== null && ep !== null) {{
                        if (Math.abs(up - ep) < 0.1) return true;
                      }}
                    }}

                    // Fractions
                    for (const expRaw of expList) {{
                      if (!user.includes('/') || !String(expRaw || '').includes('/')) continue;
                      const uf = _mmParseFraction(user);
                      const ef = _mmParseFraction(expRaw);
                      if (uf !== null && ef !== null) {{
                        if (Math.abs(uf - ef) < 0.001) return true;
                      }}
                    }}

                    // Numeric tolerance (mirrors server validator)
                    for (const expRaw of expList) {{
                      const un = _mmParseNumber(user);
                      const en = _mmParseNumber(expRaw);
                      if (un === null || en === null) continue;
                      if (Math.abs(en) > 10) {{
                        if (Math.abs(un - en) / Math.abs(en) < 0.01) return true;
                      }} else {{
                        if (Math.abs(un - en) < 0.1) return true;
                      }}
                    }}

                    return false;
                  }}

                  function _mmFindEnterButton() {{
                    try {{
                      const buttons = Array.from(window.parent.document.querySelectorAll('button'));
                      return buttons.find(b => ((b.innerText || '').trim().includes('Enter'))) || null;
                    }} catch (e) {{
                      return null;
                    }}
                  }}

                  function _mmClickEnterButton(input) {{
                    try {{
                      const enterBtn = _mmFindEnterButton();
                      if (!enterBtn) return false;

                      // Try to trigger the same pre-commit logic as a real tap.
                      try {{
                        const w = enterBtn.ownerDocument && enterBtn.ownerDocument.defaultView ? enterBtn.ownerDocument.defaultView : window.parent;
                        if (w && typeof w.PointerEvent === 'function') {{
                          enterBtn.dispatchEvent(new w.PointerEvent('pointerdown', {{ bubbles: true, cancelable: true }}));
                          enterBtn.dispatchEvent(new w.PointerEvent('pointerup', {{ bubbles: true, cancelable: true }}));
                        }}
                      }} catch (e) {{}}

                      // Ensure Streamlit sees the current value before rerun.
                      try {{
                        const w = (input && input.ownerDocument && input.ownerDocument.defaultView) ? input.ownerDocument.defaultView : window.parent;
                        const InEv = (w && typeof w.InputEvent === 'function') ? w.InputEvent : w.Event;
                        input.dispatchEvent(new InEv('input', {{ bubbles: true }}));
                        input.dispatchEvent(new w.Event('change', {{ bubbles: true }}));
                      }} catch (e) {{}}

                      // Delay the click slightly so Streamlit's own input handler can update its internal widget state.
                      // (On iPhone, clicking too fast can submit a stale/empty answer.)
                      setTimeout(() => {{
                        try {{ enterBtn.click(); }} catch (e) {{}}
                      }}, 75);
                      return true;
                    }} catch (e) {{
                      return false;
                    }}
                  }}

                  function _mmDispatchEnter(input) {{
                    try {{
                      const w = (input.ownerDocument && input.ownerDocument.defaultView) ? input.ownerDocument.defaultView : window.parent;
                      const evDown = new w.KeyboardEvent('keydown', {{
                        key: 'Enter',
                        code: 'Enter',
                        which: 13,
                        keyCode: 13,
                        bubbles: true,
                        cancelable: true
                      }});
                      const evUp = new w.KeyboardEvent('keyup', {{
                        key: 'Enter',
                        code: 'Enter',
                        which: 13,
                        keyCode: 13,
                        bubbles: true,
                        cancelable: true
                      }});
                      input.dispatchEvent(evDown);
                      input.dispatchEvent(evUp);
                    }} catch (e) {{}}
                  }}

                  function wireAutoAdvanceOnCorrect(input) {{
                    try {{
                      if (!input || input.getAttribute('data-mm-auto-advance') === '1') return;
                      input.setAttribute('data-mm-auto-advance', '1');

                      let inHandler = false;
                      input.addEventListener('input', () => {{
                        try {{
                          window.__mm_focus_answer = true;
                          if (inHandler) return;

                          // Pull the *current* question config from the input element.
                          // This is updated on every rerun, and avoids the "first question only" bug
                          // caused by closures capturing the initial EXPECTED_ANSWERS/QUESTION_TOKEN.
                          const cfg = input.__mm_autoAdvanceConfig || {{}};
                          const expected = Array.isArray(cfg.expected) ? cfg.expected : EXPECTED_ANSWERS;
                          const token = typeof cfg.token === 'string' && cfg.token ? cfg.token : QUESTION_TOKEN;

                          const v = String(input.value || '');
                          if (!_mmIsCorrectLocally(v, expected)) return;

                          // Reset per-question so we can auto-advance again after the question changes.
                          const prevToken = input.getAttribute('data-mm-qtoken') || '';
                          if (prevToken !== token) {{
                            input.setAttribute('data-mm-qtoken', token);
                            input.removeAttribute('data-mm-auto-advanced');
                          }}
                          if (input.getAttribute('data-mm-auto-advanced') === '1') return;
                          input.setAttribute('data-mm-auto-advanced', '1');

                          inHandler = true;
                          // Force a Streamlit "commit" while trying to KEEP the iOS keyboard open.
                          //
                          // - We need a commit event so Python `on_change` runs and submits.
                          // - iOS keyboard closes when an input blurs; to reduce that, we blur+refocus
                          //   immediately within the same user input event.
                          window.__mm_keep_focus = true;
                          try {{
                            const w = (input && input.ownerDocument && input.ownerDocument.defaultView) ? input.ownerDocument.defaultView : window.parent;
                            input.dispatchEvent(new w.Event('change', {{ bubbles: true }}));
                          }} catch (e) {{}}

                          try {{ input.blur(); }} catch (e) {{}}
                          try {{
                            // Re-focus immediately to keep the keypad open across the rerun.
                            input.focus({{ preventScroll: true }});
                          }} catch (e) {{
                            try {{ input.focus(); }} catch (e2) {{}}
                          }}

                          inHandler = false;
                        }} catch (e) {{
                          inHandler = false;
                        }}
                      }});
                    }} catch (e) {{}}
                  }}

                  function wireCommaCommaAsEnter(input) {{
                    try {{
                      if (!input || input.getAttribute('data-mm-comma-enter') === '1') return;
                      input.setAttribute('data-mm-comma-enter', '1');

                      let inHandler = false;
                      let lastPunct = null;
                      let lastPunctAt = 0;

                      function commitAsEnterWithPunct(punct) {{
                        try {{
                          // Persist a "refocus after rerun" intent. Streamlit updates the DOM in-place,
                          // so this global survives reruns and lets us restore focus for fast play.
                          window.__mm_focus_answer = true;
                          if (inHandler) return;
                          inHandler = true;

                          const dbl = punct + punct;
                          const v0 = String(input.value || '');
                          let v = v0;

                          // Some mobile decimal keypads won't insert a second decimal separator.
                          // If the value doesn't end with ",," / "..", force it to, then commit.
                          if (!v.endsWith(dbl)) {{
                            if (v.endsWith(punct)) {{
                              v = v + punct;
                            }} else {{
                              v = v + dbl;
                            }}

                            try {{
                              const proto = input.ownerDocument?.defaultView?.HTMLInputElement?.prototype;
                              const setter = proto && Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                              if (setter) setter.call(input, v);
                              else input.value = v;
                            }} catch (e) {{
                              input.value = v;
                            }}

                            try {{
                              input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                              input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }} catch (e) {{}}
                          }}

                          // Important: don't click the Enter button (race condition: button click can arrive
                          // before Streamlit commits the latest input value). Instead, simulate pressing Enter
                          // on the input itself, which is Streamlit's normal "commit" path.
                          const w = input.ownerDocument?.defaultView || window.parent;
                          const evDown = new w.KeyboardEvent('keydown', {{
                            key: 'Enter',
                            code: 'Enter',
                            which: 13,
                            keyCode: 13,
                            bubbles: true,
                            cancelable: true
                          }});
                          const evUp = new w.KeyboardEvent('keyup', {{
                            key: 'Enter',
                            code: 'Enter',
                            which: 13,
                            keyCode: 13,
                            bubbles: true,
                            cancelable: true
                          }});
                          input.dispatchEvent(evDown);
                          input.dispatchEvent(evUp);
                        }} catch (err) {{}}
                        finally {{
                          inHandler = false;
                        }}
                      }}

                      input.addEventListener('input', () => {{
                        try {{
                          // Persist a "refocus after rerun" intent. Streamlit updates the DOM in-place,
                          // so this global survives reruns and lets us restore focus for fast play.
                          window.__mm_focus_answer = true;

                          if (inHandler) return;
                          const v = String(input.value || '');
                          if (v.endsWith(',,')) commitAsEnterWithPunct(',');
                          else if (v.endsWith('..')) commitAsEnterWithPunct('.');
                        }} catch (err) {{}}
                      }}, true);

                      // Fallback for mobile numeric keypads: detect a quick double-press of ',' or '.'
                      // even if the second separator isn't inserted into the input value.
                      input.addEventListener('keydown', (e) => {{
                        try {{
                          window.__mm_focus_answer = true;
                          const k = e && e.key;
                          if (k !== ',' && k !== '.') return;

                          const now = Date.now();
                          const isDouble = (lastPunct === k) && (now - lastPunctAt) < 450;
                          lastPunct = k;
                          lastPunctAt = now;

                          // Only treat as shortcut when the current value already ends with the separator
                          // (i.e., user is "at the end" and intentionally repeating it).
                          const v = String(input.value || '');
                          if (!isDouble) return;
                          if (!v.endsWith(k)) return;

                          e.preventDefault();
                          e.stopPropagation();
                          // Reset so repeated presses don't cascade
                          lastPunct = null;
                          lastPunctAt = 0;

                          commitAsEnterWithPunct(k);
                        }} catch (err) {{}}
                      }}, true);
                    }} catch (err) {{}}
                  }}

                  function wireEnterButtonFocusFlag(input) {{
                    try {{
                      const buttons = Array.from(window.parent.document.querySelectorAll('button'));
                      const enterBtn = buttons.find(b => ((b.innerText || '').trim().includes('Enter')));
                      if (!enterBtn || enterBtn.getAttribute('data-mm-enter-focus') === '1') return;
                      enterBtn.setAttribute('data-mm-enter-focus', '1');
                      enterBtn.addEventListener('pointerdown', () => {{
                        window.__mm_focus_answer = true;
                        // Ensure the current input value is committed before Streamlit handles the button click.
                        try {{
                          const w = (input && input.ownerDocument && input.ownerDocument.defaultView) ? input.ownerDocument.defaultView : window.parent;
                          const InEv = (w && typeof w.InputEvent === 'function') ? w.InputEvent : w.Event;
                          input.dispatchEvent(new InEv('input', {{ bubbles: true }}));
                          input.dispatchEvent(new w.Event('change', {{ bubbles: true }}));
                        }} catch (e) {{}}
                      }}, true);
                    }} catch (e) {{}}
                  }}

                  function apply() {{
                    try {{
                      // Target only the answer input (avoid touching other text inputs on the page).
                      const input =
                        window.parent.document.querySelector(`input[aria-label="${{LABEL}}"]`) ||
                        window.parent.document.querySelector('div[data-testid="stTextInput"] input[placeholder="Enter answer..."]') ||
                        window.parent.document.querySelector('div[data-testid="stTextInput"] input');

                      if (!input) return;

                      // Track question identity on the input element (used for auto-advance one-shot).
                      try {{
                        const prevToken = input.getAttribute('data-mm-qtoken') || '';
                        if (prevToken !== QUESTION_TOKEN) {{
                          input.setAttribute('data-mm-qtoken', QUESTION_TOKEN);
                          input.removeAttribute('data-mm-auto-advanced');
                          // New question: keep keyboard open by focusing the input.
                          window.__mm_keep_focus = true;
                          window.__mm_focus_answer = true;
                        }}
                      }} catch (e) {{}}

                      // Update the per-input auto-advance config every rerun so the handler always
                      // uses the current question's expected answers.
                      try {{
                        input.__mm_autoAdvanceConfig = {{
                          expected: EXPECTED_ANSWERS,
                          token: QUESTION_TOKEN,
                        }};
                      }} catch (e) {{}}

                      // Apply mobile keyboard hints
                      input.setAttribute('inputmode', MODE);
                      input.setAttribute('type', TYPE);
                      input.setAttribute('enterkeyhint', 'done');
                      if (MODE === 'decimal') {{
                        input.setAttribute('pattern', '[-0-9.,]*');
                      }} else {{
                        input.removeAttribute('pattern');
                      }}
                      if (STEP) {{
                        input.setAttribute('step', STEP);
                      }} else {{
                        input.removeAttribute('step');
                      }}

                      // Reduce annoying mobile auto-changes
                      input.setAttribute('autocomplete', 'off');
                      input.setAttribute('autocapitalize', 'none');
                      input.setAttribute('autocorrect', 'off');
                      input.setAttribute('spellcheck', 'false');

                      // (Disabled) Shortcut: ",," behaves like Enter
                      // wireCommaCommaAsEnter(input);
                      // Auto-advance as soon as the typed answer matches
                      wireAutoAdvanceOnCorrect(input);

                      // If Python cleared the answer field this run, force-clear the DOM value too.
                      // This avoids the "old answer sticks around" issue on some mobile browsers.
                      if (SHOULD_CLEAR) {{
                        if (typeof input.value === 'string' && input.value !== '') {{
                          input.value = '';
                          try {{
                            const w = (input && input.ownerDocument && input.ownerDocument.defaultView) ? input.ownerDocument.defaultView : window.parent;
                            const InEv = (w && typeof w.InputEvent === 'function') ? w.InputEvent : w.Event;
                            input.dispatchEvent(new InEv('input', {{ bubbles: true }}));
                            input.dispatchEvent(new w.Event('change', {{ bubbles: true }}));
                          }} catch (e) {{}}
                        }}
                        // After advancing, re-focus to keep the keypad open.
                        window.__mm_keep_focus = true;
                        window.__mm_focus_answer = true;
                      }}

                      // If we just advanced (or the user interacted), restore focus so mobile keeps the keypad open.
                      // iOS may ignore programmatic focus unless it follows a user gesture; we gate this with a
                      // global flag that is set by key presses / Enter taps.
                      const keepFocus = !!window.__mm_keep_focus;
                      const shouldFocus = keepFocus || !!window.__mm_focus_answer;
                      if (shouldFocus && window.parent.document.activeElement !== input) {{
                        try {{ input.focus({{ preventScroll: true }}); }} catch (e) {{ try {{ input.focus(); }} catch (e2) {{}} }}
                      }}
                      // Clear one-shot focus intent; keepFocus stays until we actually hold focus.
                      if (window.__mm_focus_answer) window.__mm_focus_answer = false;
                      if (keepFocus && window.parent.document.activeElement === input) window.__mm_keep_focus = false;

                      // Make sure tapping the on-screen Enter also restores focus after rerun.
                      wireEnterButtonFocusFlag(input);
                    }} catch (e) {{}}
                  }}
                  apply();
                  setTimeout(apply, 0);
                  setTimeout(apply, 50);
                  setTimeout(apply, 250);
                  const obs = new MutationObserver(apply);
                  obs.observe(window.parent.document.body, {{ childList: true, subtree: true }});
                  setTimeout(() => obs.disconnect(), 1000);
                }})();
                </script>
                """,
                height=0,
                width=0,
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Action buttons
            col_enter, col_skip = st.columns(2)
            with col_enter:
                enter_clicked = st.button(
                    "⏎ Enter",
                    key="enter_button",
                    help="Same as pressing Enter",
                    use_container_width=True,
                    type="primary",
                )
            with col_skip:
                skip_clicked = st.button(
                    "⏭️ Skip",
                    key="skip_button",
                    help="Skip this question",
                    use_container_width=True,
                    type="secondary",
                )

            if enter_clicked:
                # If an on_change callback already submitted this rerun (common when the click on the Enter
                # button forces a text-input commit), do not submit again.
                if not mm_skip_enter_submit:
                    st.session_state.confirm_quit = False
                    # Read from session_state (more reliable than the local `answer` var on mobile,
                    # especially when a click happens before the widget value is fully committed).
                    submit_current_answer()

            if skip_clicked:
                # Submit empty/wrong answer to move to next question
                result = st.session_state.session_manager.submit_answer(session, "")
                st.session_state.last_result = result
                st.session_state.show_feedback = True
                st.session_state.feedback_time = datetime.now()
                st.session_state.confirm_quit = False
                st.session_state._mm_next_answer_value = ""
                st.session_state._mm_clear_answer = True
                st.rerun()
    
    # Stats in expander instead of sidebar (better for mobile)
    with st.expander("📊 Stats"):
        total_q = len(session.questions_answered)
        if total_q > 0:
            correct = sum(1 for r in session.questions_answered if r.is_correct)
            accuracy = correct / total_q * 100
            avg_time = sum(r.time_taken for r in session.questions_answered) / total_q
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Accuracy", f"{accuracy:.0f}%")
                st.metric("Correct", f"{correct}/{total_q}")
            with col2:
                st.metric("Avg Time", f"{avg_time:.1f}s")
                st.metric("Combo", f"x{session.combo_count}")
        else:
            st.info("Answer questions to see stats")
