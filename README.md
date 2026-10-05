# 🥗 AI Nutrition Studio & Clinical RAG Assistant

An agentic, multi-modal nutrition tracking assistant powered by **LangGraph**, **LangChain**, and **Streamlit**. The application combines computer vision for meal analysis with Retrieval-Augmented Generation (RAG) to query clinical diet protocols (e.g., Keto, Oncology/Cancer diets, Low Sodium) and live macro databases.

---

## 🎨 UI Overview
<img width="1895" height="954" alt="image" src="https://github.com/user-attachments/assets/6cf9a792-ca23-49f5-a5f3-96ced75026f6" />


---

## ✨ Features

- 📸 **Visual Meal Logging**: Upload photos of meals for instant ingredient identification and macro breakdown.
- 🎯 **Intent Classification**: Automatically detects user intent (`LOG_MEAL`, `ALLERGY_CHECK`, `MEAL_PLAN`, `GENERAL_QUERY`).
- 📚 **Clinical RAG Integration**: Queries localized medical PDF guidelines (Keto, Renal, Cancer Protocols, Low Sodium) embedded via **ChromaDB**.
- 🔍 **Live Macro Verification**: Queries public open databases (OpenFoodFacts) for accurate metric lookup per 100g.
- ⚠️ **Automated Allergen Warnings**: Direct alerts when flagged restrictions are detected in user queries or uploads.

---

## 🏗️ Agentic Architecture Flow

```
                     ┌────────────────────────┐
                     │   User Query / Photo   │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │   Intent Classifier    │
                     └───────────┬────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │      LLM Agent         │
                     │   (GPT-4o + System)    │
                     └───────────┬────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
        ┌─────────────────────┐     ┌─────────────────────┐
        │ Verified Nutrition  │     │ Hospital Guideline  │
        │   Tool (API Search) │     │  RAG Tool (Chroma)  │
        └──────────┬──────────┘     └──────────┬──────────┘
                   │                           │
                   └─────────────┬─────────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │  Final Response & UI   │
                     └────────────────────────┘
```

---

## 🚀 Quickstart Guide

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ai-nutrition-studio.git
cd ai-nutrition-studio

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Ingest Clinical Guidelines (RAG)

1. Place your medical PDFs or text documents inside the `./data` directory (e.g., `keto_guidelines.pdf`, `cancer_nutrition.pdf`).
2. Run the ingestion script to split, embed, and store vectors in ChromaDB:

```bash
python ingest_docs.py
```

### 4. Launch the Application

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
├── app.py              # Streamlit dashboard interface & CSS styling
├── agent.py            # LangGraph workflow, nodes, and conditional edges
├── tools.py            # RAG ChromaDB lookup and OpenFoodFacts API tool
├── state.py            # LangGraph state schema definition
├── ingest_docs.py      # PDF parsing and vector database creation script
├── requirements.txt    # Project dependencies
└── data/               # Folder containing diet & hospital PDF guidelines
```

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM Orchestration**: LangGraph, LangChain Core, LangChain OpenAI
- **Vector Database**: ChromaDB (`langchain-chroma`)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Vision Model**: OpenAI `gpt-4o`
- **External Data**: OpenFoodFacts API

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
