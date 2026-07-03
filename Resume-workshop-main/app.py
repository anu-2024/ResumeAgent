# app.py
# ─────────────────────────────────────────────
# Resume Builder Agentic System
# Streamlit Frontend — 5 tabs
# ─────────────────────────────────────────────

# app.py
import sys
import os

# Add project root to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.pdf_extractor import extract_resume_text
from utils.jd_scraper import fetch_jd_from_url
from utils.resume_generator import generate_resume_docx
from graph.pipeline import run_pipeline

# ── Page Config ──
st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0; }
    .agent-badge {
        display: inline-block;
        background: #4f46e5;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .gap-card {
        border-left: 4px solid #ef4444;
        padding-left: 1rem;
        margin: 0.5rem 0;
        background: #fef2f2;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
    }
    .project-card {
        background: #f0fdf4;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #22c55e;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div class="main-header">
    <h1>📄 AI Resume Builder</h1>
    <p style="color: #6b7280;">
        4-agent system that tailors your resume to any job description
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Session State Init ──
# Persists data when user switches between tabs
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

# ── 5 Tabs ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Input",
    "🔍 JD Analysis",
    "⭐ Score Card",
    "💡 Suggestions",
    "✅ Final Resume"
])


# ════════════════════════════════════════
# TAB 1 — INPUT
# ════════════════════════════════════════
with tab1:
    st.markdown("### Step 1 — Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"],
        help="Upload your current resume in PDF or DOCX format"
    )

    if uploaded_file:
        try:
            st.session_state.resume_text = extract_resume_text(uploaded_file)
            st.success(
                f"✅ Resume loaded — "
                f"{len(st.session_state.resume_text)} characters extracted"
            )
            with st.expander("👀 Preview extracted text"):
                st.text(st.session_state.resume_text[:1500] + "...")
        except Exception as e:
            st.error(f"❌ Could not read file: {e}")

    st.divider()

    st.markdown("### Step 2 — Target Role")
    target_role = st.text_input(
        "What role are you targeting?",
        placeholder="e.g. Data Scientist, ML Engineer, Backend Developer"
    )

    st.divider()

    st.markdown("### Step 3 — Job Description")
    jd_mode = st.radio(
        "How do you want to provide the JD?",
        ["🔗 Paste a Job URL", "📋 Paste JD Text Directly"],
        horizontal=True
    )

    if jd_mode == "🔗 Paste a Job URL":
        job_url = st.text_input(
            "Job posting URL",
            placeholder="https://linkedin.com/jobs/view/..."
        )
        if job_url and st.button("🌐 Fetch JD from URL"):
            with st.spinner("Fetching job description..."):
                try:
                    st.session_state.jd_text = fetch_jd_from_url(job_url)
                    st.success("✅ JD fetched successfully!")
                    with st.expander("👀 Preview fetched JD"):
                        st.text(st.session_state.jd_text[:1000] + "...")
                except Exception as e:
                    st.error(f"❌ {e}")
    else:
        jd_paste = st.text_area(
            "Paste the full Job Description here",
            height=200,
            placeholder="Copy and paste the complete job description..."
        )
        if jd_paste:
            st.session_state.jd_text = jd_paste
            st.success(f"✅ JD received — {len(jd_paste)} characters")

    st.divider()

    st.markdown("### Step 4 — Options")
    include_projects = st.checkbox(
        "Include suggested projects in final resume",
        value=True,
        help="Agent 3 suggests projects — check this to include them"
    )

    st.divider()

    # ── Readiness check ──
    ready = (
        st.session_state.resume_text
        and st.session_state.jd_text
        and target_role
    )

    if not ready:
        missing = []
        if not st.session_state.resume_text:
            missing.append("resume")
        if not target_role:
            missing.append("target role")
        if not st.session_state.jd_text:
            missing.append("job description")
        st.info(f"⏳ Still needed: {', '.join(missing)}")

    # ── Run Button ──
    if st.button(
        "🚀 Analyze & Build My Resume",
        disabled=not ready,
        type="primary",
        use_container_width=True
    ):
        with st.status(
            "🤖 Running 4-agent pipeline...",
            expanded=True
        ) as status:
            st.write("🔍 Agent 1: Parsing job description...")
            st.write("⭐ Agent 2: Evaluating your resume...")
            st.write("💡 Agent 3: Analyzing gaps...")
            st.write("✍️ Agent 4: Writing tailored resume...")

            try:
                result = run_pipeline(
                    resume_text=st.session_state.resume_text,
                    jd_text=st.session_state.jd_text,
                    include_suggested_projects=include_projects
                )

                if result.get("error"):
                    status.update(
                        label=f"❌ Error occurred",
                        state="error"
                    )
                    st.error(result["error"])
                else:
                    st.session_state.pipeline_result = result
                    status.update(
                        label="✅ All 4 agents completed!",
                        state="complete"
                    )
                    st.success("Done! Check the other tabs →")

            except Exception as e:
                status.update(label="❌ Pipeline failed", state="error")
                st.error(f"Error: {e}")


# ── Helper function ──
def no_results():
    st.info(
        "👈 Complete the **Input** tab first "
        "and click **Analyze & Build My Resume**"
    )


# ════════════════════════════════════════
# TAB 2 — JD ANALYSIS
# ════════════════════════════════════════
with tab2:
    st.markdown("## 🔍 JD Analysis")
    st.markdown(
        '<span class="agent-badge">AGENT 1 — JD PARSER</span>',
        unsafe_allow_html=True
    )

    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        jd = result["parsed_jd"]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Role:** {jd.get('role', 'N/A')}")
            st.markdown(f"**Company:** {jd.get('company', 'N/A')}")
            st.markdown(f"**Experience:** {jd.get('experience_years', 'N/A')}")
            st.markdown(f"**Education:** {jd.get('education', 'N/A')}")
        with col2:
            st.markdown("**Summary:**")
            st.info(jd.get("summary", "N/A"))

        st.divider()

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### ✅ Required Skills")
            for skill in jd.get("required_skills", []):
                st.markdown(f"- {skill}")
        with col4:
            st.markdown("#### 🌟 Preferred Skills")
            for skill in jd.get("preferred_skills", []):
                st.markdown(f"- {skill}")

        st.divider()
        st.markdown("#### 📋 Responsibilities")
        for r in jd.get("responsibilities", []):
            st.markdown(f"- {r}")

        st.divider()
        st.markdown("#### 🏷️ ATS Keywords")
        keywords = jd.get("keywords", [])
        if keywords:
            st.markdown(" ".join([f"`{k}`" for k in keywords]))


# ════════════════════════════════════════
# TAB 3 — SCORE CARD
# ════════════════════════════════════════
with tab3:
    st.markdown("## ⭐ Resume Score Card")
    st.markdown(
        '<span class="agent-badge">AGENT 2 — RESUME EVALUATOR</span>',
        unsafe_allow_html=True
    )

    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        ev = result["evaluation"]
        overall = ev.get("overall_score", 0)

        # ── Big score display ──
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            color = (
                "#22c55e" if overall >= 7
                else "#f59e0b" if overall >= 5
                else "#ef4444"
            )
            st.markdown(f"""
            <div style="text-align:center; padding:2rem;
                        background:{color}20; border-radius:16px;
                        border:2px solid {color}">
                <div style="font-size:4rem; font-weight:800;
                            color:{color}">{overall}/10</div>
                <div style="color:#6b7280">Overall Resume Score</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── Score breakdown ──
        st.markdown("#### 📊 Score Breakdown")
        breakdown = ev.get("breakdown", {})
        for metric, score in breakdown.items():
            label = metric.replace("_", " ").title()
            st.markdown(f"**{label}**")
            st.progress(score / 10, text=f"{score}/10")

        st.divider()

        col5, col6 = st.columns(2)
        with col5:
            st.markdown("#### ✅ Matched Skills")
            for s in ev.get("matched_skills", []):
                st.markdown(f"✅ {s}")
            st.markdown("#### 💪 Strengths")
            for s in ev.get("strengths", []):
                st.markdown(f"- {s}")
        with col6:
            st.markdown("#### ❌ Missing Skills")
            for s in ev.get("missing_skills", []):
                st.markdown(f"❌ {s}")
            st.markdown("#### ⚠️ Weaknesses")
            for s in ev.get("weaknesses", []):
                st.markdown(f"- {s}")

        st.divider()
        st.markdown("#### 🧑‍⚖️ Hiring Manager Verdict")
        st.warning(ev.get("verdict", "N/A"))


# ════════════════════════════════════════
# TAB 4 — SUGGESTIONS
# ════════════════════════════════════════
with tab4:
    st.markdown("## 💡 Gap Analysis & Suggestions")
    st.markdown(
        '<span class="agent-badge">AGENT 3 — GAP ANALYST</span>',
        unsafe_allow_html=True
    )

    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        gap = result["gap_analysis"]

        st.markdown("#### 🎯 What They're Really Looking For")
        for item in gap.get("what_they_want", []):
            st.markdown(f"- {item}")

        st.divider()

        st.markdown("#### 🔴 Critical Gaps")
        for g in gap.get("critical_gaps", []):
            importance = g.get("importance", "Medium")
            color = (
                "#ef4444" if importance == "High"
                else "#f59e0b" if importance == "Medium"
                else "#6b7280"
            )
            st.markdown(f"""
            <div class="gap-card" style="border-color:{color}">
                <strong>{g.get('gap')}</strong><br/>
                <span style="color:{color}; font-size:0.8rem">
                    ⚠️ {importance} Priority
                </span><br/>
                💡 <em>{g.get('how_to_fix')}</em>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.markdown("#### 🚀 Suggested Projects")
        for p in gap.get("suggested_projects", []):
            tech = ", ".join(p.get("tech_stack", []))
            st.markdown(f"""
            <div class="project-card">
                <strong>🛠️ {p.get('title')}</strong><br/>
                <span style="color:#6b7280; font-size:0.85rem">
                    {tech}
                </span><br/><br/>
                {p.get('description')}<br/><br/>
                <strong>Why it helps:</strong>
                {p.get('why_it_helps')}<br/>
                <strong>Sample metric:</strong>
                <code>{p.get('sample_metric')}</code>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### ⚡ Quick Wins")
        for qw in gap.get("quick_wins", []):
            st.markdown(f"✅ {qw}")


# ════════════════════════════════════════
# TAB 5 — FINAL RESUME
# ════════════════════════════════════════
with tab5:
    st.markdown("## ✅ Your Tailored Resume")
    st.markdown(
        '<span class="agent-badge">AGENT 4 — RESUME WRITER</span>',
        unsafe_allow_html=True
    )

    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        final_resume = result.get("final_resume", "")

        if final_resume:
            # ── Download button ──
            try:
                docx_bytes = generate_resume_docx(final_resume)
                st.download_button(
                    label="📥 Download Resume as DOCX",
                    data=docx_bytes,
                    file_name="tailored_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument"
                         ".wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"DOCX generation failed: {e}")

            st.divider()
            st.markdown("#### 📄 Resume Preview")
            st.text_area(
                "Final Resume",
                value=final_resume,
                height=600
            )
        else:
            st.error("Resume writer returned empty output. Please try again.")