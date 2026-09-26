"""UI helpers and client-side viewport navigation for Streamlit."""

import streamlit as st
import streamlit.components.v1 as components


def get_scroll_to_top_js(anchor_id: str = "questionnaire-top") -> str:
    """Generates cross-browser JavaScript to reset scroll position to the top of the questionnaire."""
    return f"""
    <script>
    (function() {{
        function performScroll() {{
            try {{
                const pWin = (window.parent && window.parent !== window) ? window.parent : window;
                const pDoc = pWin.document || document;
                
                // 1. Scroll anchor element into view if present
                const anchor = pDoc.getElementById('{anchor_id}') || 
                               pDoc.getElementById('{anchor_id}-anchor') ||
                               pDoc.querySelector('.main .block-container');
                if (anchor) {{
                    anchor.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
                
                // 2. Also reset scroll position of all standard Streamlit scroll containers
                const containers = [
                    pDoc.querySelector('section.main'),
                    pDoc.querySelector('.main'),
                    pDoc.querySelector('[data-testid="stAppViewContainer"]'),
                    pDoc.querySelector('[data-testid="stMain"]'),
                    pDoc.querySelector('[data-testid="stAppViewBlockContainer"]')
                ];
                containers.forEach(function(el) {{
                    if (el && el.scrollTop !== 0) {{
                        try {{
                            el.scrollTo({{ top: 0, left: 0, behavior: 'smooth' }});
                        }} catch (e) {{
                            el.scrollTop = 0;
                        }}
                    }}
                }});
                
                // 3. Document level fallback
                if (pDoc.documentElement && pDoc.documentElement.scrollTop !== 0) {{
                    pDoc.documentElement.scrollTop = 0;
                }}
                if (pDoc.body && pDoc.body.scrollTop !== 0) {{
                    pDoc.body.scrollTop = 0;
                }}
                
                // 4. Window level fallback
                try {{
                    pWin.scrollTo({{ top: 0, left: 0, behavior: 'smooth' }});
                }} catch (e) {{
                    pWin.scrollTo(0, 0);
                }}
            }} catch (err) {{
                // Fallback for isolated window context
                window.scrollTo({{ top: 0, left: 0, behavior: 'smooth' }});
            }}
        }}

        // Execute immediately upon DOM script execution
        performScroll();
        // Execute on animation frame when layout paints
        requestAnimationFrame(performScroll);
        // Execute with short delay to catch any late layout updates
        setTimeout(performScroll, 50);
        setTimeout(performScroll, 150);
    }})();
    </script>
    """


def inject_scroll_to_top(anchor_id: str = "questionnaire-top", key: str = "scroll_to_top") -> None:
    """Injects client-side script to reset viewport scroll position to the top of the questionnaire.
    
    Safe, non-disruptive, does not reload the page or alter session state.
    """
    js_code = get_scroll_to_top_js(anchor_id=anchor_id)
    
    # 1. Primary mechanism: components.html iframe with same-origin parent access
    components.html(js_code, height=0, width=0)
    
    # 2. Secondary direct DOM injection via st.html if supported
    if hasattr(st, "html"):
        try:
            st.html(js_code, unsafe_allow_javascript=True)
        except Exception:
            pass


def get_scheme_details_scroll_js(anchor_id: str = "scheme-detail-top") -> str:
    """Generates cross-browser script to reset viewport scroll position strictly to the top on Scheme Detail page."""
    import time
    ts = int(time.time() * 1000)
    js_body = f"""
        function resetSchemePageScroll() {{
            try {{
                if ('scrollRestoration' in history) {{
                    history.scrollRestoration = 'manual';
                }}
                const win = window;
                const doc = document;

                // 1. Reset standard window and document
                if (win.scrollTo) {{
                    try {{ win.scrollTo({{ top: 0, left: 0, behavior: 'instant' }}); }}
                    catch(e) {{ try {{ win.scrollTo(0, 0); }} catch(e2) {{}} }}
                }}
                if (doc.documentElement && doc.documentElement.scrollTop !== 0) {{
                    doc.documentElement.scrollTop = 0;
                }}
                if (doc.body && doc.body.scrollTop !== 0) {{
                    doc.body.scrollTop = 0;
                }}

                // 2. Scroll anchor element into view if present
                const anchor = doc.getElementById('{anchor_id}') ||
                               doc.getElementById('scheme-detail-top') ||
                               doc.querySelector('.main .block-container') ||
                               doc.querySelector('[data-testid="stAppViewContainer"]');
                if (anchor && anchor.scrollIntoView) {{
                    try {{
                        anchor.scrollIntoView({{ behavior: 'instant', block: 'start' }});
                    }} catch (e) {{
                        try {{ anchor.scrollIntoView(true); }} catch (e2) {{}}
                    }}
                }}

                // 3. Reset all standard Streamlit scroll containers
                const selectors = [
                    'section.main',
                    '.main',
                    '[data-testid="stAppViewContainer"]',
                    '[data-testid="stMain"]',
                    '[data-testid="stAppViewBlockContainer"]',
                    '.block-container'
                ];

                selectors.forEach(function(sel) {{
                    const els = doc.querySelectorAll(sel);
                    els.forEach(function(el) {{
                        if (el) {{
                            if (typeof el.scrollTo === 'function') {{
                                try {{ el.scrollTo({{ top: 0, left: 0, behavior: 'instant' }}); }}
                                catch(e) {{ try {{ el.scrollTo(0, 0); }} catch(e2) {{}} }}
                            }}
                            if (el.scrollTop !== undefined && el.scrollTop !== 0) {{
                                el.scrollTop = 0;
                            }}
                        }}
                    }});
                }});

                // 4. Parent window fallback if nested
                try {{
                    if (win.parent && win.parent !== win) {{
                        const pWin = win.parent;
                        const pDoc = pWin.document;
                        if (pWin.scrollTo) {{
                            try {{ pWin.scrollTo({{ top: 0, left: 0, behavior: 'instant' }}); }}
                            catch(e) {{ try {{ pWin.scrollTo(0, 0); }} catch(e2) {{}} }}
                        }}
                        if (pDoc.documentElement && pDoc.documentElement.scrollTop !== 0) {{
                            pDoc.documentElement.scrollTop = 0;
                        }}
                        if (pDoc.body && pDoc.body.scrollTop !== 0) {{
                            pDoc.body.scrollTop = 0;
                        }}
                        selectors.forEach(function(sel) {{
                            const els = pDoc.querySelectorAll(sel);
                            els.forEach(function(el) {{
                                if (el && el.scrollTop !== 0) el.scrollTop = 0;
                            }});
                        }});
                    }}
                }} catch(e) {{}}
            }} catch(err) {{
                try {{ window.scrollTo(0, 0); }} catch(e) {{}}
            }}
        }}

        // Run immediately
        resetSchemePageScroll();

        // Run on animation frames after browser layout paint
        if (window.requestAnimationFrame) {{
            window.requestAnimationFrame(resetSchemePageScroll);
            window.requestAnimationFrame(function() {{
                window.requestAnimationFrame(resetSchemePageScroll);
            }});
        }}

        // Run on staggered timeouts to defeat any late layout paint or scroll restoration
        setTimeout(resetSchemePageScroll, 10);
        setTimeout(resetSchemePageScroll, 50);
        setTimeout(resetSchemePageScroll, 120);
        setTimeout(resetSchemePageScroll, 250);
        setTimeout(resetSchemePageScroll, 500);
    """

    return f"""
    <div style="display: none; width: 0; height: 0; margin: 0; padding: 0; overflow: hidden;">
        <script id="scheme-scroll-{ts}">
        (function() {{
            {js_body}
        }})();
        </script>
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E"
             onload="(function(img){{
                 var s = img.previousElementSibling;
                 if (s && s.tagName === 'SCRIPT') {{
                     try {{ eval(s.textContent); }} catch(e) {{}}
                 }}
             }})(this)"
             style="display: none;" />
    </div>
    """


def inject_scheme_details_scroll_to_top(anchor_id: str = "scheme-detail-top") -> None:
    """Injects client-side script using Streamlit's native st.html to reset viewport scroll position to top.
    
    Avoids deprecated st.components.v1.html and executes directly in the main document.
    """
    html_code = get_scheme_details_scroll_js(anchor_id=anchor_id)
    if hasattr(st, "html"):
        try:
            st.html(html_code, unsafe_allow_javascript=True)
            return
        except Exception:
            pass
    # Fallback only if st.html is unavailable
    components.html(html_code, height=0, width=0)

