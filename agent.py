from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from state import AgentState
from tools import get_verified_nutrition

tools = [get_verified_nutrition]
tool_node = ToolNode(tools)
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)

def classify_intent(state: AgentState):
    messages = state["messages"]
    latest_message = messages[-1].content
    
    query_text = latest_message
    if isinstance(latest_message, list):
        query_text = " ".join([item.get("text", "") for item in latest_message if item.get("type") == "text"])
        if not query_text:
            query_text = "Uploaded food image for analysis"

    classification_prompt = (
        "Classify the user's input into one of the following exact categories: "
        "1. 'LOG_MEAL' (User is uploading a photo or naming food to track/analyze macros), "
        "2. 'ALLERGY_CHECK' (User is asking if a specific ingredient is safe given their restrictions), "
        "3. 'MEAL_PLAN' (User wants recipe suggestions or meal planning advice), "
        "4. 'GENERAL_QUERY' (General nutritional education or questions).\n\n"
        f"User Input: {query_text}\n"
        "Return ONLY the category name."
    )
    
    response = model.invoke([HumanMessage(content=classification_prompt)])
    detected_intent = response.content.strip()
    return {"intent": detected_intent}

def call_model(state: AgentState):
    messages = state["messages"]
    current_goal = state.get("dietary_goal", "General Health")
    current_allergies = state.get("allergies", "None specified")
    current_intent = state.get("intent", "GENERAL_QUERY")
    
    system_prompt = (
        f"You are an expert clinical dietitian and agentic nutrition assistant. "
        f"Detected User Intent: {current_intent}. "
        f"Active dietary goal: {current_goal}. "
        f"Active allergies/restrictions: {current_allergies}. "
        "CRITICAL: If the food contains ingredients listed in the user's allergies/restrictions, you MUST explicitly flag it as dangerous immediately. "
        "Tailor your response format directly to the user's intent (e.g., provide macro breakdowns for LOG_MEAL, safety alerts for ALLERGY_CHECK). "
        "Analyze any attached images and answer ongoing user questions. Use the get_verified_nutrition tool "
        "to look up individual ingredients found in the food when exact metrics are needed. Do not guess values if you can query the tool."
    )
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = model.invoke(full_messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    if state["messages"][-1].tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("classifier", classify_intent)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("classifier")
workflow.add_edge("classifier", "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

app_graph = workflow.compile()
