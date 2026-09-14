# 🥗 AI Nutrition Studio

**AI Nutrition Studio** is an advanced agentic, intent-aware clinical nutrition assistant built using **Streamlit**, **LangGraph**, and **OpenAI GPT-4o**. It empowers users to track macros, scan meal photos via vision capabilities, verify ingredient safety against custom allergy/dietary restrictions, and query live public nutrition registries.

---

## 📂 Project Structure

```text
nutrition_app/
├── app.py               # Main Streamlit UI, custom styling, and chat event loop
├── agent.py             # LangGraph state graph topology, intent classifier, and agent node
├── tools.py             # External API tools (Open Food Facts registry lookups)
├── state.py             # TypedDict agent state definitions and history types
├── requirements.txt     # Python package dependencies
└── .env                 # Environment variables configuration (API keys)
```

---

## 🛠️ Key Components

1. **Intent Classifier Node (`agent.py`)**: Automatically categorizes user queries into intents (`LOG_MEAL`, `ALLERGY_CHECK`, `MEAL_PLAN`, `GENERAL_QUERY`) before routing to the clinical dietitian agent.
2. **Verified Database Tool (`tools.py`)**: Connects to the Open Food Facts API to retrieve precise macro breakdowns (calories, protein, carbs, fats per 100g) for verified items.
3. **Agentic Workflow (`agent.py`)**: Managed via LangGraph with state persistence and conditional tool-calling loops.
4. **Interactive UI (`app.py`)**: Styled Streamlit interface supporting sidebar profile settings (dietary goals, allergy restrictions) and multi-modal image/text input.

---

## 🚀 Getting Started & Installation

### 1. Clone or Setup Repository
Ensure all modular files (`app.py`, `agent.py`, `tools.py`, `state.py`, `requirements.txt`) are placed together in your local project root directory.

### 2. Install Dependencies
Run the following command in your terminal to install all required packages:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a file named `.env` in the root directory of your project folder and add your OpenAI API key:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

---

## ▶️ Running the Application

Launch the Streamlit web interface locally from your terminal:
```bash
streamlit run app.py
```

Open the local development URL provided in your terminal output (typically `http://localhost:8501`) to interact with your AI Nutrition Studio.

---

## 🎯 Usage Guide
- **Sidebar Configuration**: Set your target *Dietary Goal* (e.g., Weight Loss, Keto, Muscle Gain) and enter any *Allergies / Restrictions*.
- **Meal Logging**: Upload an image of your plate or type a food description to get an automated macro breakdown and intent analysis.
- **Safety Alerts**: The agent will explicitly flag dangerous ingredients if they violate your configured allergy profile.
