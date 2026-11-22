import streamlit as st
import pandas as pd
import sqlite3
import os
import re
import json
import tempfile
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq

st.set_page_config(
    page_title="SQL Analyst Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 50%, #0a0e1a 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(13, 17, 23, 0.95) !important;
    border-right: 1px solid rgba(99, 210, 255, 0.15) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Main container */
.main .block-container {
    max-width: 1200px;
    padding: 2rem 2rem;
}

/* Headers */
h1, h2, h3 { color: #f0f6fc !important; letter-spacing: -0.02em; }

/* Cards */
.card {
    background: rgba(22, 27, 34, 0.8);
    border: 1px solid rgba(99, 210, 255, 0.12);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 0.75rem 0;
    backdrop-filter: blur(10px);
}

.card-accent {
    background: rgba(22, 27, 34, 0.8);
    border: 1px solid rgba(99, 210, 255, 0.3);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 0.75rem 0;
    box-shadow: 0 0 20px rgba(99, 210, 255, 0.05);
}

/* SQL code block */
.sql-block {
    background: #0d1117;
    border: 1px solid rgba(99, 210, 255, 0.2);
    border-left: 3px solid #63d2ff;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #79c0ff;
    white-space: pre-wrap;
    overflow-x: auto;
    margin: 0.5rem 0;
}

/* Answer block */
.answer-block {
    background: rgba(99, 210, 255, 0.04);
    border: 1px solid rgba(99, 210, 255, 0.15);
    border-radius: 12px;
    padding: 1.25rem;
    color: #e2e8f0;
    font-size: 1rem;
    line-height: 1.7;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-blue  { background: rgba(99,210,255,0.12); color: #63d2ff; border: 1px solid rgba(99,210,255,0.25); }
.badge-green { background: rgba(80,250,123,0.1);  color: #50fa7b; border: 1px solid rgba(80,250,123,0.2); }
.badge-amber { background: rgba(255,184,77,0.1);  color: #ffb84d; border: 1px solid rgba(255,184,77,0.2); }
.badge-red   { background: rgba(255,85,85,0.1);   color: #ff5555; border: 1px solid rgba(255,85,85,0.2); }

/* Metric row */
.metric-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 0.5rem 0;
}
.metric-item {
    flex: 1;
    min-width: 120px;
    background: rgba(99,210,255,0.04);
    border: 1px solid rgba(99,210,255,0.1);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    text-align: center;
}
.metric-val  { font-size: 1.4rem; font-weight: 700; color: #63d2ff; }
.metric-lbl  { font-size: 0.72rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 4px; }

/* Streamlit overrides */
.stButton > button {
    background: rgba(99,210,255,0.08) !important;
    border: 1px solid rgba(99,210,255,0.3) !important;
    color: #63d2ff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: rgba(99,210,255,0.15) !important;
    border-color: rgba(99,210,255,0.5) !important;
    transform: translateY(-1px) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(13,17,23,0.8) !important;
    border: 1px solid rgba(99,210,255,0.2) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(99,210,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(99,210,255,0.1) !important;
}

[data-testid="stFileUploader"] {
    border: 2px dashed rgba(99,210,255,0.25) !important;
    border-radius: 12px !important;
    background: rgba(99,210,255,0.02) !important;
}

.stDataFrame {
    border: 1px solid rgba(99,210,255,0.15) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(99,210,255,0.12) !important;
    border-radius: 10px !important;
    background: rgba(13,17,23,0.4) !important;
}

.stSuccess { background: rgba(80,250,123,0.08) !important; border: 1px solid rgba(80,250,123,0.2) !important; border-radius: 8px !important; }
.stError   { background: rgba(255,85,85,0.08)  !important; border: 1px solid rgba(255,85,85,0.2)  !important; border-radius: 8px !important; }
.stWarning { background: rgba(255,184,77,0.08) !important; border: 1px solid rgba(255,184,77,0.2) !important; border-radius: 8px !important; }
.stInfo    { background: rgba(99,210,255,0.05) !important; border: 1px solid rgba(99,210,255,0.15) !important; border-radius: 8px !important; }

/* Divider */
hr { border-color: rgba(99,210,255,0.1) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: rgba(99,210,255,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,210,255,0.4); }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [
    ("db_path", None),
    ("table_name", None),
    ("df", None),
    ("schema_info", None),
    ("history", []),
    ("groq_client", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_groq_client(api_key: str):
    return Groq(api_key=api_key)


def sanitize_table_name(name: str) -> str:
    name = os.path.splitext(name)[0]
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if name[0].isdigit():
        name = "t_" + name
    return name.lower()


def csv_to_sqlite(df: pd.DataFrame, table_name: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    conn = sqlite3.connect(tmp.name)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return tmp.name


def get_schema_info(db_path: str, table_name: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    # Sample 3 rows
    sample_df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
    conn.close()
    
    schema_lines = [f"Table: {table_name}", f"Total rows: {row_count}", "Columns:"]
    for col in cols:
        schema_lines.append(f"  - {col[1]} ({col[2]})")
    schema_lines.append("\nSample rows:")
    schema_lines.append(sample_df.to_string(index=False))
    return "\n".join(schema_lines)


def run_sql(db_path: str, query: str):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)


SYSTEM_PROMPT = """You are an expert SQL data analyst. Your job is to:
1. Understand the user's natural language question about their data
2. Write a correct SQLite SQL query to answer it
3. Provide a clear, concise interpretation of what the query will return

Table schema and sample data will be provided in the user message.

IMPORTANT RULES:
- Always respond with VALID JSON only. No markdown, no preamble.
- Use only SQLite-compatible SQL syntax
- Always use the exact table name and column names from the schema
- For text searches use LIKE with % wildcards
- Avoid subqueries when possible; use CTEs if needed

Response format (strict JSON):
{
  "sql": "SELECT ... FROM ...",
  "explanation": "This query will ...",
  "chart_suggestion": {
    "type": "bar|line|pie|scatter|histogram|none",
    "x_col": "column_name_or_null",
    "y_col": "column_name_or_null",
    "title": "Chart title"
  }
}
"""


def ask_groq(client, question: str, schema_info: str, history: list) -> dict:
    messages = []
    
    # Include last 4 turns of history for context
    for h in history[-4:]:
        messages.append({"role": "user",    "content": h["question"]})
        messages.append({"role": "assistant","content": json.dumps(h["response"])})
    
    messages.append({
        "role": "user",
        "content": f"Schema:\n{schema_info}\n\nQuestion: {question}"
    })
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        temperature=0.1,
        max_tokens=800,
    )
    
    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def build_chart(df: pd.DataFrame, suggestion: dict):
    chart_type = suggestion.get("type", "none")
    x_col = suggestion.get("x_col")
    y_col = suggestion.get("y_col")
    title = suggestion.get("title", "")

    if chart_type == "none" or df is None or df.empty:
        return None

    # Validate columns
    if x_col and x_col not in df.columns:
        x_col = df.columns[0] if len(df.columns) > 0 else None
    if y_col and y_col not in df.columns:
        # Pick first numeric column
        num_cols = df.select_dtypes(include="number").columns.tolist()
        y_col = num_cols[0] if num_cols else (df.columns[1] if len(df.columns) > 1 else None)

    colors = ["#63d2ff","#50fa7b","#ffb84d","#ff5555","#bd93f9","#ff79c6","#8be9fd"]

    template = dict(
        layout=go.Layout(
            paper_bgcolor="rgba(13,17,23,0)",
            plot_bgcolor="rgba(22,27,34,0.5)",
            font=dict(family="Space Grotesk", color="#e2e8f0"),
            title_font_color="#f0f6fc",
            xaxis=dict(gridcolor="rgba(99,210,255,0.08)", linecolor="rgba(99,210,255,0.15)"),
            yaxis=dict(gridcolor="rgba(99,210,255,0.08)", linecolor="rgba(99,210,255,0.15)"),
            colorway=colors,
        )
    )

    try:
        if chart_type == "bar" and x_col and y_col:
            fig = px.bar(df, x=x_col, y=y_col, title=title, template=template,
                         color_discrete_sequence=colors)
            fig.update_traces(marker_color="#63d2ff", marker_line_width=0)

        elif chart_type == "line" and x_col and y_col:
            fig = px.line(df, x=x_col, y=y_col, title=title, template=template,
                          color_discrete_sequence=colors)
            fig.update_traces(line_color="#63d2ff", line_width=2)

        elif chart_type == "pie" and x_col and y_col:
            fig = px.pie(df, names=x_col, values=y_col, title=title,
                         color_discrete_sequence=colors)

        elif chart_type == "scatter" and x_col and y_col:
            fig = px.scatter(df, x=x_col, y=y_col, title=title, template=template,
                             color_discrete_sequence=colors)
            fig.update_traces(marker_color="#63d2ff", marker_size=8)

        elif chart_type == "histogram" and x_col:
            fig = px.histogram(df, x=x_col, title=title, template=template,
                               color_discrete_sequence=colors)
            fig.update_traces(marker_color="#63d2ff")
        else:
            return None

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(22,27,34,0.4)",
            margin=dict(l=20, r=20, t=50, b=20),
            height=380,
        )
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <span style="font-size:2rem">🔍</span>
        <h2 style="margin:0.25rem 0 0; font-size:1.15rem; color:#63d2ff; letter-spacing:-0.01em;">SQL Analyst Agent</h2>
        <p style="font-size:0.75rem; color:#8b949e; margin:0;">Powered by Groq × LLaMA 3</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Get your free key at console.groq.com"
    )
    if groq_key:
        st.session_state.groq_client = get_groq_client(groq_key)
        st.markdown('<span class="badge badge-green">✓ API Key Set</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Upload CSV**")
    uploaded = st.file_uploader("", type=["csv"], label_visibility="collapsed")
    
    if uploaded:
        with st.spinner("Loading data..."):
            try:
                df = pd.read_csv(uploaded)
                table_name = sanitize_table_name(uploaded.name)
                db_path = csv_to_sqlite(df, table_name)
                schema_info = get_schema_info(db_path, table_name)
                
                st.session_state.df = df
                st.session_state.db_path = db_path
                st.session_state.table_name = table_name
                st.session_state.schema_info = schema_info
                st.session_state.history = []
                
                st.success(f"Loaded: **{uploaded.name}**")
            except Exception as e:
                st.error(f"Error: {e}")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        st.markdown("---")
        st.markdown("**Dataset Info**")
        
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:6px;">
            <div class="card" style="padding:0.6rem 0.9rem;">
                <span style="color:#8b949e;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.07em;">Rows</span>
                <div style="color:#63d2ff;font-size:1.1rem;font-weight:600;">{len(df):,}</div>
            </div>
            <div class="card" style="padding:0.6rem 0.9rem;">
                <span style="color:#8b949e;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.07em;">Columns</span>
                <div style="color:#63d2ff;font-size:1.1rem;font-weight:600;">{len(df.columns)}</div>
            </div>
            <div class="card" style="padding:0.6rem 0.9rem;">
                <span style="color:#8b949e;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.07em;">Table</span>
                <div style="color:#50fa7b;font-size:0.85rem;font-family:'JetBrains Mono',monospace;">{st.session_state.table_name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Column Types"):
            for col, dtype in df.dtypes.items():
                type_color = "#63d2ff" if "int" in str(dtype) or "float" in str(dtype) else \
                             "#50fa7b" if "object" in str(dtype) else "#ffb84d"
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;margin:4px 0;">'
                    f'<span style="color:#e2e8f0;font-size:0.82rem;">{col}</span>'
                    f'<code style="color:{type_color};font-size:0.72rem;">{dtype}</code></div>',
                    unsafe_allow_html=True
                )
        
        if st.session_state.history:
            if st.button("🗑 Clear History"):
                st.session_state.history = []
                st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#8b949e;line-height:1.7;">
    <strong style="color:#e2e8f0;">Example questions:</strong><br>
    • How many rows are there?<br>
    • Show top 10 by [column]<br>
    • What is the average [column]?<br>
    • Group by [column] and count<br>
    • Find rows where [column] > 100
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

# Hero header
st.markdown("""
<div style="margin-bottom:1.5rem;">
    <h1 style="font-size:2rem;font-weight:700;margin:0;background:linear-gradient(135deg,#63d2ff,#50fa7b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        AI SQL Data Analyst
    </h1>
    <p style="color:#8b949e;margin:0.25rem 0 0;font-size:0.95rem;">
        Ask questions in plain English → get SQL queries, answers, and charts
    </p>
</div>
""", unsafe_allow_html=True)

# ── No data yet ────────────────────────────────────────────────────────────────
if st.session_state.df is None:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="font-size:4rem;margin-bottom:1rem;opacity:0.4;">📂</div>
        <h3 style="color:#8b949e;font-weight:400;">Upload a CSV file to get started</h3>
        <p style="color:#5a6270;font-size:0.9rem;">Use the sidebar to upload your data and enter your Groq API key</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Data Preview ───────────────────────────────────────────────────────────────
with st.expander("📊 Data Preview", expanded=False):
    st.dataframe(
        st.session_state.df.head(10),
        use_container_width=True,
        hide_index=True
    )

# ── Schema ─────────────────────────────────────────────────────────────────────
with st.expander("🗄 Database Schema", expanded=False):
    st.code(st.session_state.schema_info, language="sql")

st.markdown("---")

# ── Query input ────────────────────────────────────────────────────────────────
st.markdown("### 💬 Ask a Question")

# Suggested queries
df = st.session_state.df
col1, col2, col3, col4 = st.columns(4)
suggestions = [
    f"How many rows are there?",
    f"Show the first 5 rows",
    f"What are the column statistics?",
    f"Count distinct values per column",
]
for col, sug in zip([col1, col2, col3, col4], suggestions):
    with col:
        if st.button(sug, key=f"sug_{sug[:15]}", use_container_width=True):
            st.session_state.preset_q = sug
            st.rerun()

# Text input
if "preset_q" not in st.session_state:
    st.session_state.preset_q = ""

default_val = st.session_state.preset_q
st.session_state.preset_q = ""

question = st.text_input(
    "Your question",
    value=default_val,
    placeholder="e.g. What are the top 5 categories by total sales?",
    label_visibility="collapsed",
    key="question_input"
)

run_col, clear_col = st.columns([5, 1])
with run_col:
    run_btn = st.button("▶  Run Query", use_container_width=True)
with clear_col:
    if st.button("Clear", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ── Execute ────────────────────────────────────────────────────────────────────
if run_btn and question.strip():
    if not st.session_state.groq_client:
        st.error("Please enter your Groq API key in the sidebar.")
    else:
        with st.spinner("🤖 Thinking..."):
            try:
                result = ask_groq(
                    st.session_state.groq_client,
                    question,
                    st.session_state.schema_info,
                    st.session_state.history
                )
                sql_query = result.get("sql", "")
                explanation = result.get("explanation", "")
                chart_suggestion = result.get("chart_suggestion", {"type": "none"})
                
                result_df, error = run_sql(st.session_state.db_path, sql_query)
                
                st.session_state.history.append({
                    "question": question,
                    "response": result,
                    "result_df": result_df.to_dict() if result_df is not None else None,
                    "error": error,
                    "chart_suggestion": chart_suggestion,
                })
            except json.JSONDecodeError:
                st.error("The AI returned an unexpected response. Please try rephrasing your question.")
            except Exception as e:
                st.error(f"Error: {e}")

# ── History / Results ──────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📋 Results")
    
    for i, item in enumerate(reversed(st.session_state.history)):
        is_latest = (i == 0)
        
        with st.container():
            st.markdown(f"""
            <div class="{'card-accent' if is_latest else 'card'}" style="margin-top:1rem;">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                    {'<span class="badge badge-green">Latest</span>' if is_latest else ''}
                    <span style="color:#f0f6fc;font-size:1rem;font-weight:500;">Q: {item['question']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            resp_col, sql_col = st.columns([1, 1])
            
            with resp_col:
                st.markdown("**💡 Answer**")
                explanation = item["response"].get("explanation", "")
                st.markdown(f'<div class="answer-block">{explanation}</div>', unsafe_allow_html=True)
            
            with sql_col:
                st.markdown("**⚡ Generated SQL**")
                sql_query = item["response"].get("sql", "")
                st.markdown(f'<div class="sql-block">{sql_query}</div>', unsafe_allow_html=True)
            
            if item.get("error"):
                st.error(f"SQL Error: {item['error']}")
            elif item.get("result_df") is not None:
                result_df = pd.DataFrame.from_dict(item["result_df"])
                
                if not result_df.empty:
                    # Metrics row for single-value results
                    if len(result_df) == 1 and len(result_df.columns) <= 4:
                        cols = st.columns(len(result_df.columns))
                        for j, col_name in enumerate(result_df.columns):
                            with cols[j]:
                                val = result_df.iloc[0][col_name]
                                if isinstance(val, float):
                                    display_val = f"{val:,.2f}"
                                elif isinstance(val, int):
                                    display_val = f"{val:,}"
                                else:
                                    display_val = str(val)
                                st.markdown(f"""
                                <div class="metric-item">
                                    <div class="metric-val">{display_val}</div>
                                    <div class="metric-lbl">{col_name}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        # Show result table
                        with st.expander(f"📄 Result Table ({len(result_df):,} rows)", expanded=is_latest):
                            st.dataframe(result_df, use_container_width=True, hide_index=True)
                    
                    # Chart
                    chart_suggestion = item.get("chart_suggestion", {"type": "none"})
                    fig = build_chart(result_df, chart_suggestion)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
                else:
                    st.info("Query returned no results.")
        
        if i < len(st.session_state.history) - 1:
            st.markdown("<hr style='border-color:rgba(99,210,255,0.06);margin:0.5rem 0;'>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#5a6270;font-size:0.78rem;">
    SQL Analyst Agent · Groq LLaMA 3.3-70b · SQLite · Streamlit
</div>
""", unsafe_allow_html=True)
