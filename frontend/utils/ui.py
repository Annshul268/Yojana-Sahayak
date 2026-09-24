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
