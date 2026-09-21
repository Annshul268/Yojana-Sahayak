"""Admin Dashboard view for scheme registry and sync operations."""

from typing import Callable
import streamlit as st
from frontend.services.api_client import api_client
from frontend.utils.i18n import t


def render_admin_dashboard(navigate_to: Callable[[str], None]) -> None:
    st.markdown("## ⚙️ " + t("nav_admin", "Admin Dashboard"))
    st.caption("Protected administration portal for managing welfare schemes, triggering data ingestion, and viewing sync audit logs.")

    tab_sync, tab_schemes, tab_new_scheme = st.tabs([
        "🔄 Data Synchronization & Logs",
        "📋 Scheme Management",
        "➕ Add New Government Scheme",
    ])

    with tab_sync:
        st.subheader("Government Source Synchronization")
        st.write("Trigger the automated ingestion pipeline to fetch, clean, validate, and vector-index scheme records.")

        if st.button("🚀 Trigger Ingestion Pipeline Now", type="primary"):
            with st.spinner("Running ingestion and vector indexing pipeline..."):
                sync_res = api_client.admin_sync()
                if sync_res["ok"]:
                    st.success("Synchronization pipeline executed successfully! 🎉")
                    st.json(sync_res["data"])
                else:
                    st.error(f"Sync error: {sync_res['error']}")

        st.markdown("### 📜 Recent Synchronization Audit Logs")
        logs_res = api_client.admin_sync_logs()
        if logs_res["ok"]:
            logs = logs_res["data"]
            if logs:
                st.dataframe(logs, use_container_width=True)
            else:
                st.info("No sync logs recorded yet.")
        else:
            st.error(f"Error loading logs: {logs_res['error']}")

    with tab_schemes:
        st.subheader("Active Scheme Registry")
        schemes_res = api_client.admin_list_schemes()
        if schemes_res["ok"]:
            schemes = schemes_res["data"]
            st.write(f"Total registered schemes: **{len(schemes)}**")
            for s in schemes:
                with st.expander(f"🏛️ {s.get('name')} ({s.get('slug')}) — {'Active' if s.get('active') else 'Inactive'}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Category:** {s.get('category')}")
                        st.write(f"**Ministry:** {s.get('ministry')}")
                        st.write(f"**Official URL:** [{s.get('official_url')}]({s.get('official_url')})")
                    with col2:
                        st.write(f"**Last Verified:** {s.get('last_verified_at')}")
                        st.write(f"**Status:** {s.get('verification_status')}")
                        is_active = s.get("active", True)
                        btn_label = "Deactivate Scheme" if is_active else "Activate Scheme"
                        if st.button(btn_label, key=f"toggle_{s.get('id')}"):
                            up_res = api_client.admin_update_scheme(
                                scheme_id=s.get("id"),
                                payload={"active": not is_active},
                            )
                            if up_res["ok"]:
                                st.toast(f"Scheme status updated to {'Active' if not is_active else 'Inactive'}")
                                st.rerun()

    with tab_new_scheme:
        st.subheader("Add a Verified Government Scheme")
        with st.form("new_scheme_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_slug = st.text_input("Scheme Slug (unique id)", placeholder="e.g. pm-poshan-shakti")
                new_name = st.text_input("Scheme Name (English)", placeholder="e.g. PM POSHAN")
                new_name_hi = st.text_input("Scheme Name (Hindi)", placeholder="e.g. पीएम पोषण")
                new_category = st.text_input("Category", placeholder="Education & Learning")
                new_ministry = st.text_input("Ministry", placeholder="Ministry of Education")

            with col_b:
                new_desc = st.text_area("Description (English)")
                new_official_url = st.text_input("Official Government Portal URL", placeholder="https://pmposhan.education.gov.in/")
                new_source = st.text_input("Source Name", value="Ministry Official Portal")

            new_submit = st.form_submit_button("➕ Register Scheme", type="primary", use_container_width=True)

        if new_submit:
            payload = {
                "slug": new_slug.strip().lower(),
                "name": new_name.strip(),
                "name_hi": new_name_hi.strip(),
                "description": new_desc.strip(),
                "category": new_category.strip(),
                "ministry": new_ministry.strip(),
                "official_url": new_official_url.strip(),
                "source_name": new_source.strip(),
                "active": True,
                "eligibility_rules": {},
                "benefits": [],
                "documents": [],
                "application_steps": [],
            }
            create_res = api_client.admin_create_scheme(payload)
            if create_res["ok"]:
                st.success("New scheme successfully registered in database! 🎉")
                st.rerun()
            else:
                st.error(f"Failed to create scheme: {create_res['error']}")
