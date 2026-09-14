from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from watchlist_tools import (
    add_movie,
    remove_movie,
    list_movies,
    random_movie,
)
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage

load_dotenv()


anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


class State(TypedDict):
    messages: Annotated[list, add_messages]


SYSTEM_PROMPT = (
    "You are a helpful assistant that can manage a movie watchlist. You can add movies, remove movies, list all movies, and suggest a random movie from the watchlist. "
    "Respond politely to the user and avoid explaining what you don't have information about. "
    "Tell the user that you can only help with movie watchlist-related queries, if they ask you something that is not movie watchlist related."
)


model = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0.2,
    anthropic_api_key=anthropic_api_key,
)

tools = [add_movie, remove_movie, list_movies, random_movie]
model_with_tools = model.bind_tools(tools)


tool_node = ToolNode(tools)

graph_builder = StateGraph(State)


def chatbot(state):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    return {"messages": [model_with_tools.invoke(messages)]}


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

# persist the graph state to a SQLite database

with SqliteSaver.from_conn_string("watchlist.sqlite") as checkpointer:

    thread_config = {
        "configurable": {
            "thread_id": "user_johnson",
        }
    }

    graph = graph_builder.compile(checkpointer=checkpointer)

    while True:
        user_input = input("Your question: ")

        if user_input.lower() in ["quit", "exit"]:
            break

        for message, metadata in graph.stream(
            {"messages": [("user", user_input)]},
            config=thread_config,
            stream_mode="messages",
        ):
            if isinstance(message.content, str):
                print(message.content, end="", flush=True)

            elif isinstance(message.content, list):
                for content_block in message.content:
                    if (
                        isinstance(content_block, dict)
                        and content_block.get("type") == "text"
                    ):
                        print(
                            content_block["text"],
                            end="",
                            flush=True,
                        )

        print()
