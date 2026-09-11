from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from watchlist_tools import (
    add_movies,
    remove_movie,
    list_movies,
    random_movie,
)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


class State(TypedDict):
    messages: Annotated[list, add_messages]


system_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that can manage a movie watchlist. You can add movies, remove movies, list all movies, and suggest a random movie from the watchlist. Respond politely to the user and avoid explaining what you don't have information about.",
        )
    ]
)


model = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0.2,
    anthropic_api_key=anthropic_api_key,
)

tools = [add_movies, remove_movie, list_movies, random_movie]
model_with_tools = model.bind_tools(tools)


tool_node = ToolNode(tools)

# response = model.invoke("what is machine learning?")
# print(response)


graph_builder = StateGraph(State)


def chatbot(state):
    return {"messages": [model_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")


graph = graph_builder.compile()

while True:
    user_input = input("Your question: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    state = graph.invoke({"role": "user", "messages": [user_input]})

    print(f"Agent: {state['messages'][-1].content}")
