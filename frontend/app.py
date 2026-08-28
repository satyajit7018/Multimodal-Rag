"""Streamlit Interactive Grounding Demo & Benchmark Dashboard.
Features:
- Side-by-side Visual Grounding (Rendered Tables + Cropped Pinouts)
- Live Confidence Gauges & Attribution Citations
- Dual Pipeline Selector (Multimodal CTO Squad vs Baseline)
- Benchmark Scorecard & Results Visualizer
- Corpus & Datasheet Inspector
"""

import os
import json
import requests
import streamlit as st

st.set_page_config(
    page_title="Datasheet Assistant — Multimodal RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Custom CSS for polished aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .badge-pass {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-refusal {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/integrated-circuit.png", width=64)
    st.title("Datasheet RAG")
    st.caption("Executive CTO: Claude Opus 4.6\nSubagents: Gemini 3.7 Flash")
    st.divider()

    mode = st.radio(
        "Retrieval Pipeline Mode:",
        ["Multimodal (3 Stores + CTO)", "Baseline (Text-Only)"],
        index=0,
    )
    api_mode = "multimodal" if "Multimodal" in mode else "baseline"

    st.divider()
    st.subheader("💡 Quick Sample Questions")
    samples = {
        "📊 Table: LM7805 Voltage Range": "What is the recommended operating input voltage range for the LM7805 regulator?",
        "🔌 Diagram: DHT22 Pinout": "Which pin on the DHT22 4-pin package is the digital data I/O pin?",
        "⚡ Table: LM358 Max Voltage": "What is the absolute maximum supply voltage rating for the LM358 dual op-amp?",
        "📐 Diagram: LM7805 Output Pin": "In the standard LM7805 TO-220 pinout diagram, which pin is the Output pin?",
        "📝 Text: ESP32 CPU Core": "What type of CPU core is used in the ESP32 microcontroller?",
        "🛡️ Refusal Test (Unrelated)": "What is the capital of France?",
    }
    
    selected_sample = st.selectbox("Load sample query:", ["-- Choose a question --"] + list(samples.keys()))
    sample_query = samples[selected_sample] if selected_sample != "-- Choose a question --" else ""

# Main Content Tabs
tab_qa, tab_benchmark, tab_corpus = st.tabs([
    "⚡ Interactive Grounded Assistant",
    "📈 Dual Benchmark Scorecard",
    "📚 Datasheet Corpus & Architecture",
])

# ----------------- TAB 1: INTERACTIVE ASSISTANT -----------------
with tab_qa:
    st.markdown('<div class="main-header">Electronics Datasheet Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask technical questions across text specs, multi-column tables, and circuit pinout diagrams.</div>', unsafe_allow_html=True)

    default_q = sample_query if sample_query else ""
    user_query = st.text_input("Enter engineering question:", value=default_q, placeholder="e.g. What is the maximum output current for the LM7805?")

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        ask_clicked = st.button("🚀 Query Assistant", type="primary", use_container_width=True)

    if (ask_clicked or default_q) and user_query:
        with st.spinner("CTO Squad executing parallel retrieval & cross-modality synthesis..."):
            try:
                resp = requests.post(f"{API_URL}/query", json={"question": user_query, "mode": api_mode}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    
                    st.divider()
                    
                    # Top Metric Row
                    col_score, col_status = st.columns([1, 3])
                    with col_score:
                        conf = data.get("confidence_score", 0.0)
                        st.metric("Retrieval Confidence", f"{conf:.2f}", delta=f"{'Above' if conf >= 0.55 else 'Below'} 0.55 Threshold")
                    with col_status:
                        if data.get("is_refusal"):
                            st.markdown('<span class="badge-refusal">⚠️ Calibrated Refusal Guardrail Triggered</span>', unsafe_allow_html=True)
                            st.info("The system politely refused to speculate because the verified context score is below the 0.55 threshold.")
                        else:
                            st.markdown('<span class="badge-pass">✅ Grounded Answer Generated</span>', unsafe_allow_html=True)

                    # Answer Card
                    st.markdown("### 🤖 CTO Synthesized Answer")
                    st.success(data["answer"])

                    # Grounding Columns
                    has_table = bool(data.get("source_table"))
                    has_img = bool(data.get("source_image_url"))

                    if has_table or has_img:
                        st.markdown("### 🔍 Verified Source Grounding")
                        col_tbl, col_diag = st.columns(2)

                        with col_tbl:
                            if has_table:
                                st.markdown("#### 📊 Extracted Specification Table")
                                meta = data.get("source_table_meta") or {}
                                if meta.get("doc_name"):
                                    st.caption(f"Source: `{meta['doc_name']}` (Page {meta.get('page', '?')})")
                                st.markdown(data["source_table"])
                            else:
                                st.info("No primary tabular match required for this query.")

                        with col_diag:
                            if has_img:
                                st.markdown("#### 📐 Extracted Pinout / Diagram")
                                meta = data.get("source_image_meta") or {}
                                if meta.get("doc_name"):
                                    st.caption(f"Source: `{meta['doc_name']}` (Page {meta.get('page', '?')}) — Bounding Box Grounded")
                                img_url = f"{API_URL}{data['source_image_url']}"
                                st.image(img_url, use_container_width=True)
                            else:
                                st.info("No diagram match required for this query.")

                    # User Feedback Section
                    st.divider()
                    st.markdown("##### Was this answer correct and helpful?")
                    fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 4])
                    with fb_col1:
                        if st.button("👍 Correct"):
                            requests.post(f"{API_URL}/feedback", json={"question": user_query, "answer": data["answer"], "is_correct": True})
                            st.toast("Feedback recorded: Correct!", icon="✅")
                    with fb_col2:
                        if st.button("👎 Incorrect"):
                            requests.post(f"{API_URL}/feedback", json={"question": user_query, "answer": data["answer"], "is_correct": False})
                            st.toast("Feedback recorded: Incorrect", icon="⚠️")

                else:
                    st.error(f"API Error ({resp.status_code}): {resp.text}")
            except Exception as e:
                st.error(f"Failed to connect to API at {API_URL}. Is the server running? Error: {e}")

# ----------------- TAB 2: BENCHMARK SCORECARD -----------------
with tab_benchmark:
    st.markdown("### 📈 Baseline (Text-Only) vs. Multimodal (CTO Squad) Evaluation Benchmark")
    st.caption("Tested against 40 hand-curated questions in `data/eval_set.json` (15 Text, 15 Table, 10 Diagram).")

    eval_file = "data/eval_results.json"
    if os.path.exists(eval_file):
        with open(eval_file, "r") as f:
            eval_data = json.load(f)
        
        summary = eval_data.get("summary", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Text Accuracy", f"{summary.get('text', {}).get('multimodal_accuracy', 0)}%", delta=f"+{summary.get('text', {}).get('improvement', 0)}% vs Baseline")
        with col2:
            st.metric("Table Accuracy", f"{summary.get('table', {}).get('multimodal_accuracy', 0)}%", delta=f"+{summary.get('table', {}).get('improvement', 0)}% vs Baseline")
        with col3:
            st.metric("Diagram Accuracy", f"{summary.get('diagram', {}).get('multimodal_accuracy', 0)}%", delta=f"+{summary.get('diagram', {}).get('improvement', 0)}% vs Baseline")
        with col4:
            st.metric("Overall Accuracy", f"{summary.get('overall', {}).get('multimodal_accuracy', 0)}%", delta=f"+{summary.get('overall', {}).get('improvement', 0)}% vs Baseline")

        st.markdown("#### 📋 Detailed Category Comparison Table")
        table_rows = []
        for cat in ["text", "table", "diagram", "overall"]:
            s = summary.get(cat, {})
            table_rows.append({
                "Category": cat.upper(),
                "Questions": s.get("total", 0),
                "Baseline (Text-Only)": f"{s.get('baseline_accuracy', 0)}%",
                "Multimodal (CTO Squad)": f"{s.get('multimodal_accuracy', 0)}%",
                "Accuracy Gain": f"+{s.get('improvement', 0)}%",
            })
        st.dataframe(table_rows, use_container_width=True)

    else:
        st.info("Benchmark has not been run yet. Run `python3 -m src.eval.run_eval` to generate benchmark metrics.")

# ----------------- TAB 3: CORPUS & ARCHITECTURE -----------------
with tab_corpus:
    st.markdown("### 📚 Ingested Datasheet Corpus")
    datasheets = [
        ("ESP32-WROOM-32", "2.4 GHz Wi-Fi + Bluetooth Dual-Core SoC", "Espressif"),
        ("LM7805", "3-Terminal Positive 5V 1.5A Voltage Regulator", "Texas Instruments / ST"),
        ("LM358", "Dual Low-Power Single-Supply Operational Amplifier", "TI / ON Semi"),
        ("BME280", "Combined Humidity, Barometric Pressure & Temperature Sensor", "Bosch Sensortec"),
        ("DHT22 (AM2302)", "Digital Temperature & Relative Humidity Sensor", "Aosong"),
        ("NE555", "Precision Monostable / Astable Timing IC", "TI / Signetics"),
        ("L298N", "Dual Full-Bridge 2A Inductive Motor Driver", "STMicroelectronics"),
        ("MAX485", "Low-Power 2.5 Mbps RS-485 / RS-422 Transceiver", "Maxim Integrated / Analog Devices"),
        ("STM32F103", "ARM Cortex-M3 32-bit Microcontroller (72 MHz)", "STMicroelectronics"),
        ("PCA9685", "16-Channel 12-bit PWM LED / Servo I2C Controller", "NXP Semiconductors"),
    ]

    st.table([{"Component": d[0], "Description": d[1], "Manufacturer": d[2]} for d in datasheets])

    st.markdown("### 🏗️ Multi-Model Parallel Architecture")
    st.markdown("""
    - **Executive CTO (Claude Opus 4.6)**: Handles query intent decomposition, cross-modality synthesis, confidence refusal gating (< 0.55), and exact source citations.
    - **Vision Specialist (Gemini 3.7 Flash)**: Pinout analysis, schematic diagram parsing, and OpenCV contour/BBox validation.
    - **Table Specialist (Gemini 3.7 Flash)**: PDF table parsing, header alignment, limit range extraction, and natural-language Markdown summarization.
    - **Text Specialist (Gemini 3.7 Flash)**: Layout-aware section partitioning and semantic chunking.
    - **Vector Storage**: Qdrant (3 Collections: `multimodal_text`, `multimodal_tables`, `multimodal_images`) with Cross-Encoder precision reranking (`ms-marco-MiniLM-L-6-v2`).
    """)
