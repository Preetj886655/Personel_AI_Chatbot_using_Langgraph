from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# ⚠️ DO NOT hardcode token
# HF Spaces injects HUGGINGFACEHUB_API_TOKEN automatically

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V3.2",
    task="text-generation"
)

model = ChatHuggingFace(llm=llm)

# -------------------------
# LangGraph State
# -------------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------------
# Node
# -------------------------
def chat_node(state: ChatState):
    messages = state["messages"]
    response = model.invoke(messages)

    # MUST return AIMessage
    return {"messages": [AIMessage(content=response.content)]}

# -------------------------
# Graph
# -------------------------
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

checkpointer = MemorySaver()
workflow = graph.compile(checkpointer=checkpointer)
