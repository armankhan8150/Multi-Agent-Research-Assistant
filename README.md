# 🔎 Multi-Agent Research Assistant

A professional multi-agent AI system that researches any topic automatically using a pipeline of specialized AI agents. Built with **LangChain**, **LangGraph**, **Mistral AI**, and **Streamlit**.

---

## 🧠 How It Works

The pipeline runs **4 agents in sequence**:

| Step | Agent | Role |
|------|-------|------|
| 1 | 🔍 Search Agent | Finds recent, reliable sources using Tavily web search |
| 2 | 📄 Reader Agent | Scrapes the most relevant URL for deeper content |
| 3 | ✍️ Writer Chain | Drafts a structured research report (Intro → Findings → Conclusion) |
| 4 | 🧐 Critic Chain | Reviews and scores the report with strengths & improvements |

---

## 🖥️ Demo

> Enter any research topic → The pipeline runs live with status updates → Download the final report as **Markdown or PDF**

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Multi-Agent-Research-Assistant.git
cd Multi-Agent-Research-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install streamlit reportlab
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
MISTRAL_API_KEY="your_mistral_api_key"
TAVILY_API_KEY="your_tavily_api_key"
OPENAI_API_KEY="your_openai_api_key"   # optional, if switching to GPT
```

> Get your keys:
> - Mistral: https://console.mistral.ai/
> - Tavily: https://app.tavily.com/
> - OpenAI: https://platform.openai.com/

### 5. Run the Streamlit app

```bash
streamlit run app2.py
```

Or run via command line (no UI):

```bash
python pipeline.py
```

---

## 📁 Project Structure

```
Multi_Agent_System/
├── app2.py           # Streamlit UI — live agent step tracker + PDF/MD download
├── agents.py         # Agent & chain definitions (Search, Reader, Writer, Critic)
├── tools.py          # LangChain tools: web_search (Tavily) + scrape_url (BS4)
├── pipeline.py       # CLI pipeline runner (no UI)
├── requirements.txt  # Python dependencies
├── .env.example      # Template for environment variables
└── .gitignore        # Ignores .env, venv, __pycache__, etc.
```

---

## 🛠️ Tech Stack

- [LangChain](https://python.langchain.com/) — Agent orchestration & chains
- [LangGraph](https://langchain-ai.github.io/langgraph/) — Agent graph framework
- [Mistral AI](https://mistral.ai/) — LLM backbone (`mistral-small`)
- [Tavily](https://tavily.com/) — AI-powered web search API
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — Web scraping
- [Streamlit](https://streamlit.io/) — Interactive web UI
- [ReportLab](https://www.reportlab.com/) — PDF report generation

---

## 📄 License

MIT License — feel free to use and modify.

---

## 🙌 Author

Made with ❤️ — contributions and feedback welcome!
