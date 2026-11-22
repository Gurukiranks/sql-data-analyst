# 🔍 AI SQL Data Analyst Agent

A Streamlit app that lets you query any CSV file using plain English.  
Powered by **Groq (LLaMA 3.3-70b)** + **SQLite** + **Plotly**.

---

## Architecture

```
User Input (CSV + Question)
       ↓
Pandas → SQLite (in-memory temp file)
       ↓
Natural Language → Groq LLaMA 3.3-70b
       ↓
JSON response: { sql, explanation, chart_suggestion }
       ↓
SQLite execution → DataFrame
       ↓
Answer + SQL + Plotly Chart
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a free Groq API key
Visit https://console.groq.com → sign up → create API key (free tier: 14,400 req/day)

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Use it
1. Enter your Groq API key in the sidebar
2. Upload any CSV file (try `sample_data.csv`)
3. Ask questions like:
   - *"What is the total revenue by category?"*
   - *"Show me the top 5 customers by spending"*
   - *"How many orders were delivered vs pending?"*
   - *"What is the average order value per region?"*

---

## Tech Stack

| Component     | Technology                     |
|---------------|-------------------------------|
| Frontend      | Streamlit                      |
| LLM           | Groq — LLaMA 3.3-70b-versatile |
| Database      | SQLite (via Python `sqlite3`)  |
| Data Handling | Pandas                         |
| Visualization | Plotly Express                 |

---

## Features

- **Natural language → SQL** — powered by LLaMA 3.3-70b via Groq's fast inference
- **Auto-visualization** — the LLM suggests bar/line/pie/scatter/histogram charts
- **Conversation history** — maintains context across multiple questions
- **Schema introspection** — automatically detects column types and sample data
- **One-click suggestions** — preset questions to get started fast
- **Dark theme UI** — polished cyberpunk aesthetic

---

## Sample Questions for `sample_data.csv`

```
What is the total revenue by category?
Show top 3 customers by total spending
How many orders per region?
What percentage of orders were delivered?
What is the average unit price per category?
Show monthly revenue trend
Which product has the highest total sales?
```
