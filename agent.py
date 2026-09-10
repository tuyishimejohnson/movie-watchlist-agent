from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from watchlist_tools import add_movies, remove_movies, list_movies, random_movie
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Annotated

load_dotenv()


anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


class State(TypedDict):
    messages: Annotated[list, add_messages]


model = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0.2,
    anthropic_api_key=anthropic_api_key,
)

tools = [add_movies, remove_movies, list_movies, random_movie]
model_with_tools = model.bind_tools(tools)


# response = model.invoke("what is machine learning?")
# print(response)


graph_builder = StateGraph(State)


def chatbot(State):
    return {"messages": [model.invoke(State["messages"])]}


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)


graph = graph_builder.compile()

while True:
    user_input = input("Your question: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    state = graph.invoke({"messages": [user_input]})

    print(state["messages"][-1].content)
    print(state["messages"])
