"""
Streamlit UI for the multi-agent research pipeline.

Shows each of the 4 agent steps updating live (pending -> running -> done),
uses a colourful theme, and lets you download the final report as
Markdown or PDF.

Run with:
    streamlit run app.py

Place this file in the SAME folder as agents.py and tools.py.
Requires: pip install streamlit reportlab --break-system-packages
"""

import io
import re
import time

import streamlit as st
from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# ==========================================================================
# Page + theme setup
# ==========================================================================
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f5f3ff 0%, #ffffff 35%);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7c3aed, #db2777, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-sub {
        color: #6b7280;
        font-size: 1.02rem;
        margin-top: 0.2rem;
    }
    .step-card {
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 10px;
        border: 1px solid rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .step-pending {
        background: #f3f4f6;
        color: #9ca3af;
    }
    .step-running {
        background: linear-gradient(90deg, #ede9fe, #fce7f3);
        color: #7c3aed;
        box-shadow: 0 0 0 2px rgba(124,58,237,0.25);
    }
    .step-done {
        background: linear-gradient(90deg, #d1fae5, #ecfccb);
        color: #047857;
    }
    .step-error {
        background: #fee2e2;
        color: #b91c1c;
    }
    .badge {
        font-size: 0.75rem;
        padding: 2px 10px;
        border-radius: 999px;
        margin-left: auto;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="hero-title">🔎 Multi-Agent Research Assistant</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Search Agent → Reader Agent → Writer → Critic, working together on your topic.</p>',
    unsafe_allow_html=True,
)
st.write("")

# ==========================================================================
# Session state
# ==========================================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_run" not in st.session_state:
    st.session_state.selected_run = None

STEP_LABELS = [
    ("🔍", "Search Agent", "Finding recent, reliable sources"),
    ("📄", "Reader Agent", "Scraping the most relevant source"),
    ("✍️", "Writer", "Drafting the report"),
    ("🧐", "Critic", "Reviewing the report"),
]

# ==========================================================================
# Sidebar: history
# ==========================================================================
with st.sidebar:
    st.header("🕘 Past runs")
    if not st.session_state.history:
        st.write("No runs yet.")
    else:
        for i, run in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - 1 - i
            if st.button(f"📌 {run['topic'][:40]}", key=f"hist_{idx}"):
                st.session_state.selected_run = idx

    st.divider()
    if st.button("🗑️ Clear history"):
        st.session_state.history = []
        st.session_state.selected_run = None
        st.rerun()

# ==========================================================================
# Helpers
# ==========================================================================
def render_step_html(icon, name, desc, status):
    """status: 'pending' | 'running' | 'done' | 'error'"""
    css_class = f"step-{status}"
    badge = {
        "pending": "WAITING",
        "running": "RUNNING…",
        "done": "DONE",
        "error": "FAILED",
    }[status]
    return f"""
    <div class="step-card {css_class}">
        <span style="font-size:1.4rem;">{icon}</span>
        <span>{name} — <span style="font-weight:400;">{desc}</span></span>
        <span class="badge" style="background:rgba(0,0,0,0.08);">{badge}</span>
    </div>
    """


def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md_line_to_reportlab_html(line: str) -> str:
    """Escape XML then re-apply **bold** / *italic* as reportlab tags."""
    escaped = escape_xml(line)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"<i>\1</i>", escaped)
    return escaped


def build_pdf_bytes(report_text: str, topic: str) -> bytes:
    """Convert a markdown-ish report string into a styled PDF, in memory."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        topMargin=54,
        bottomMargin=50,
        leftMargin=54,
        rightMargin=54,
        title=f"Research Report - {topic}",
    )

    base_styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=base_styles["Title"],
        textColor=colors.HexColor("#5b21b6"), fontSize=20, spaceAfter=16,
    )
    h1_style = ParagraphStyle(
        "H1Custom", parent=base_styles["Heading1"],
        textColor=colors.HexColor("#7c3aed"), fontSize=15, spaceBefore=14, spaceAfter=8,
    )
    h2_style = ParagraphStyle(
        "H2Custom", parent=base_styles["Heading2"],
        textColor=colors.HexColor("#db2777"), fontSize=12.5, spaceBefore=10, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyCustom", parent=base_styles["Normal"],
        fontSize=10.5, leading=15, spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "BulletCustom", parent=body_style, leftIndent=14,
    )

    story = [Paragraph(f"Research Report: {escape_xml(topic)}", title_style), Spacer(1, 10)]

    for raw_line in report_text.split("\n"):
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue

        if line.startswith("### "):
            story.append(Paragraph(md_line_to_reportlab_html(line[4:]), h2_style))
        elif line.startswith("## "):
            story.append(Paragraph(md_line_to_reportlab_html(line[3:]), h1_style))
        elif line.startswith("# "):
            story.append(Paragraph(md_line_to_reportlab_html(line[2:]), h1_style))
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph("• " + md_line_to_reportlab_html(line[2:]), bullet_style))
        elif re.match(r"^\d+\.\s", line):
            story.append(Paragraph(md_line_to_reportlab_html(line), bullet_style))
        else:
            story.append(Paragraph(md_line_to_reportlab_html(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def run_pipeline_live(topic: str, step_placeholders):
    """Runs the 4 agent steps one by one, updating step_placeholders live."""
    state = {}
    statuses = ["pending"] * 4

    def redraw():
        for i, ph in enumerate(step_placeholders):
            icon, name, desc = STEP_LABELS[i]
            ph.markdown(render_step_html(icon, name, desc, statuses[i]), unsafe_allow_html=True)

    redraw()

    # Step 1: Search agent
    statuses[0] = "running"
    redraw()
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result["messages"][-1].content
    statuses[0] = "done"
    redraw()

    # Step 2: Reader agent
    statuses[1] = "running"
    redraw()
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [(
            "user",
            (f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape if for deeper content.\n\n"
            f"Search Result:\n{state['search_results'][:800]}")
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content
    statuses[1] = "done"
    redraw()

    # Step 3: Writer chain
    statuses[2] = "running"
    redraw()
    research_combined = (
        f"Search Results : \n {state['search_results']} \n\n"
        f"Detailed Scraped Content: \n {state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
    statuses[2] = "done"
    redraw()

    # Step 4: Critic chain
    statuses[3] = "running"
    redraw()
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    statuses[3] = "done"
    redraw()

    return state


# ==========================================================================
# Input form
# ==========================================================================
with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Latest advances in solid-state batteries",
    )
    submitted = st.form_submit_button("🚀 Run research pipeline")

# ==========================================================================
# Run pipeline with live step tracker
# ==========================================================================
if submitted:
    if not topic or not topic.strip():
        st.warning("Please enter a topic before running the pipeline.")
    else:
        st.write("")
        step_placeholders = [st.empty() for _ in STEP_LABELS]
        start_time = time.time()

        try:
            result_state = run_pipeline_live(topic.strip(), step_placeholders)
            duration = time.time() - start_time
            st.success(f"✅ All 4 steps completed in {duration:.1f} seconds!")
            st.session_state.history.append(
                {"topic": topic.strip(), "state": result_state, "duration": duration}
            )
            st.session_state.selected_run = len(st.session_state.history) - 1
        except Exception as e:
            st.error("❌ Pipeline failed — see details below.")
            st.exception(e)

# ==========================================================================
# Display selected run
# ==========================================================================
selected_idx = st.session_state.selected_run

if selected_idx is not None and st.session_state.history:
    run = st.session_state.history[selected_idx]
    state = run["state"]

    st.divider()
    st.subheader(f"📊 Results for: *{run['topic']}*")
    st.caption(f"Completed in {run['duration']:.1f} seconds")

    tab_report, tab_feedback, tab_search, tab_scrape = st.tabs(
        ["📝 Final Report", "🧐 Critic Feedback", "🔍 Search Results", "📄 Scraped Content"]
    )

    with tab_report:
        report_text = str(state.get("report", ""))
        st.markdown(report_text if report_text else "_No report generated._")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇️ Download as Markdown (.md)",
                data=report_text,
                file_name=f"{run['topic'][:40].replace(' ', '_')}_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col2:
            try:
                pdf_bytes = build_pdf_bytes(report_text, run["topic"])
                st.download_button(
                    "⬇️ Download as PDF (.pdf)",
                    data=pdf_bytes,
                    file_name=f"{run['topic'][:40].replace(' ', '_')}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Could not generate PDF: {e}")

    with tab_feedback:
        st.markdown(str(state.get("feedback", "")) or "_No feedback generated._")

    with tab_search:
        st.text_area("Raw search agent output", value=str(state.get("search_results", "")), height=400)

    with tab_scrape:
        st.text_area("Raw scraped content", value=str(state.get("scraped_content", "")), height=400)
else:
    st.info("Enter a topic above and click **Run research pipeline** to get started.")