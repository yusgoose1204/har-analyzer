import json
import streamlit as st
import pandas as pd
from har_parser import extract_requests
from visualizer import plot_top_slowest_requests, plot_status_code_distribution, plot_domain_load_time
from rule_engine import analyze_request
from llm_summary import summarize_issues

st.set_page_config(page_title="HAR Analyzer", layout="wide")

# --- Header
st.title("🧪 HAR File Analyzer")
st.markdown("Upload a `.har` file to visualize performance data and issues.")

# --- File Uploader
uploaded_file = st.file_uploader("Upload HAR file", type=["har"])

if uploaded_file:
    try:
        # --- Load HAR content
        har_data = json.load(uploaded_file)
        requests = extract_requests(har_data)

        st.success(f"✅ Successfully loaded {len(requests)} requests.")

        # --- Convert to DataFrame
        df = pd.DataFrame(requests)
        df['status_category'] = df['status'].apply(lambda s: f"{s // 100}xx")
        df['is_slow_ttfb'] = df['wait_time'] > 500
        df['mime_group'] = df['mime_type'].apply(lambda m: m.split('/')[0] if isinstance(m, str) else 'other')

        # --- Set filter defaults
        status_options = ['2xx', '3xx', '4xx', '5xx']
        mime_options = sorted(df['mime_group'].dropna().unique())

        if 'status_filter' not in st.session_state:
            st.session_state.status_filter = status_options
        if 'ttfb_filter' not in st.session_state:
            st.session_state.ttfb_filter = False
        if 'mime_filter' not in st.session_state:
            st.session_state.mime_filter = mime_options

        # --- Sidebar Filters
        with st.expander("🔍 Show Filters", expanded=False):
            st.session_state.status_filter = st.multiselect(
                "Status Categories",
                options=status_options,
                default=st.session_state.status_filter
            )

            st.session_state.ttfb_filter = st.checkbox(
                "Show only slow TTFB (>500ms)",
                value=st.session_state.ttfb_filter
            )

            st.session_state.mime_filter = st.multiselect(
                "MIME Types",
                options=mime_options,
                default=st.session_state.mime_filter
            )

        # --- Apply Filters
        filtered_df = df[
            df['status_category'].isin(st.session_state.status_filter) &
            df['mime_group'].isin(st.session_state.mime_filter)
        ]
        if st.session_state.ttfb_filter:
            filtered_df = filtered_df[filtered_df['is_slow_ttfb']]

        st.markdown("---")
        st.metric(label="🎯 Filtered Requests", value=len(filtered_df))

        # --- Charts
        # --- User control for how many requests to show in charts
        top_n = st.slider("Number of requests to show in charts", min_value=5, max_value=100, value=20, step=5)

        st.markdown("---")
        st.subheader("📊 Request Performance Charts")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Top Slowest Requests")
            fig1 = plot_top_slowest_requests(filtered_df, top_n=top_n, return_fig=True)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("#### Status Code Distribution")
            fig2 = plot_status_code_distribution(filtered_df, return_fig=True)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("🌐 Top Domains by Total Load Time")

        fig3 = plot_domain_load_time(filtered_df, return_fig=True)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")
        st.subheader("🧠 Rule-Based Insights")
        # --- Rule Analysis + Expanders
        requests_with_issues = []

        for req in filtered_df.to_dict(orient="records"):
            issues = analyze_request(req)
            if issues:
                req['issues'] = issues
                requests_with_issues.append(req)
                title = f"{req['method']} {req['url'][:90]}"
                with st.expander(title):
                    for issue in sorted(issues, key=lambda i: i['severity']):
                        rule_name = issue.get("rule_id", issue["message"].split(":")[0])

                        # Issue Summary
                        st.markdown(f"** {issue['severity'].capitalize()}** — {issue['message']}")

                        # General Suggestion
                        if 'suggestion' in issue:
                            st.markdown(f"🧠 **Suggestion:** {issue['suggestion']}")
                            st.markdown(" ")

                        # Salesforce Context
                        if 'sf_context' in issue:
                            st.markdown(f"💼 **SF Context:** {issue['sf_context']}")
                            st.markdown(" ")

                        # Suggested Next Steps
                        if "next_step" in issue:
                            st.markdown("🔍 **Suggested Next Steps:**")
                            for line in issue["next_step"].split("\n"):
                                st.markdown(f"- {line.strip()}")
                            st.markdown(" ")

                        # Visual Divider Between Issues
                        st.markdown("---")

                    # Request Summary Footer
                    st.markdown(f"`Status: {req['status']} | Time: {req['time_ms']} ms | TTFB: {req['wait_time']} ms`")

        # --- AI Summary Toggle
        st.markdown("---")
        st.subheader("🤖 AI-Powered Summary")
        st.info("⚠️ AI feature is temporarily disabled.")

        # col_ai1, col_ai2 = st.columns([4, 1])
        # with col_ai1:
        #     st.subheader("🤖 AI-Powered Summary")
        # with col_ai2:
        #     use_ai_summary = st.checkbox("Enable", value=True)

        # if use_ai_summary and requests_with_issues:
        #     with st.spinner("Analyzing with GPT..."):
        #         try:
        #             summary = summarize_issues(requests_with_issues)
        #             st.markdown(summary)
        #         except Exception as e:
        #             st.error(f"❌ GPT summary failed: {e}")
        # elif not requests_with_issues:
        #     st.info("No issues found — nothing to summarize.")
        # elif not use_ai_summary:
        #     st.caption("💡 AI summary is disabled.")

    except Exception as e:
        st.error(f"❌ Error loading HAR file: {e}")
else:
    st.info("Please upload a `.har` file to begin.")
