# 🔎 Multi-Agent Research Assistant

A professional multi-agent AI system that researches any topic automatically using a pipeline of specialized AI agents. Built with **LangChain**, **Mistral AI**, and **Streamlit**.

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

## 🏗️ Architecture

```mermaid
flowchart TD
    User(["👤 User\nEnters a Topic"])
    style User fill:#7c3aed,color:#fff,stroke:#5b21b6

    UI["🖥️ Streamlit UI\napp2.py"]
    style UI fill:#6d28d9,color:#fff,stroke:#4c1d95

    subgraph Pipeline ["⚙️ Multi-Agent Pipeline"]
        direction TB

        A["🔍 Search Agent\n─────────────\nTool: web_search\nAPI: Tavily\nFinds top 3 sources"]
        style A fill:#1d4ed8,color:#fff,stroke:#1e3a8a

        B["📄 Reader Agent\n─────────────\nTool: scrape_url\nLib: BeautifulSoup4\nScrapes best URL"]
        style B fill:#0369a1,color:#fff,stroke:#075985

        C["✍️ Writer Chain\n─────────────\nLLM: Mistral AI\nGenerates structured\nresearch report"]
        style C fill:#065f46,color:#fff,stroke:#064e3b

        D["🧐 Critic Chain\n─────────────\nLLM: Mistral AI\nScores and reviews\nthe report"]
        style D fill:#92400e,color:#fff,stroke:#78350f

        A -->|"Search results"| B
        B -->|"Scraped content"| C
        C -->|"Draft report"| D
    end

    M["🤖 Mistral AI\nmistral-small-2603"]
    style M fill:#be185d,color:#fff,stroke:#9d174d

    R["📝 Final Report\nCritic Feedback"]
    style R fill:#374151,color:#fff,stroke:#1f2937

    DL["⬇️ Download\nMarkdown or PDF"]
    style DL fill:#374151,color:#fff,stroke:#1f2937

    User --> UI
    UI --> Pipeline
    A & C & D -.->|"LLM calls"| M
    D --> R
    R --> DL
```

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
streamlit run app.py
```

Or run via command line (no UI):

```bash
python pipeline.py
```

---

## 📁 Project Structure

```
Multi_Agent_System/
├── app.py           # Streamlit UI — live agent step tracker + PDF/MD download
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
