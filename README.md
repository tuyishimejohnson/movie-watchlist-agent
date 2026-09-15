# Watchlist Agent

This project is a small agentic CLI application for managing a personal movie watchlist. It uses natural language to understand user requests and can add, remove, list, or randomly select movies.

## Architecture

The application uses the following flow:

```text
User input
    |
Anthropic Claude
    |
LangGraph workflow
    |
Watchlist tool
    |
SQLite database
    |
Tool result returned to Claude
    |
Natural-language response
```

### Main architectural decisions

- **Claude handles natural-language understanding and tool selection.**
- **LangChain provides the model and tool integration.**
- **LangGraph manages the agent workflow.**
- **Python functions enforce application rules especially on empty movie list or duplicates.**
- **SQLite stores the watchlist.**
- **Short-term conversation state is managed by LangGraph.**

## Prerequisites

* Python 3.10 or newer
* An Anthropic API key
* uv or pip


If you are setting up the dependencies manually with `uv`, install:

```bash
uv add langchain langgraph langchain-anthropic langgraph-checkpoint-sqlite python-dotenv
````

Alternatively, install the required packages with pip:

```bash
pip install langchain langgraph langchain-anthropic langgraph-checkpoint-sqlite python-dotenv
```

## Environment configuration

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Replace `your_anthropic_api_key` with your actual Anthropic API key.

The application loads this value using `python-dotenv`. Do not commit the `.env` file to version control. Add it to `.gitignore`:

```text
.env
```

## Running the application

With `uv`:

```bash
uv run python agent.py
```

With Python directly:

```bash
python agent.py
```

The application starts an interactive command-line session.

## Interacting with the agent

Once the application is running, enter requests in natural language:

```text
Your question: Add Inception to my watchlist
Agent: Inception added to your list

Your question: What movies are on my watchlist?
Agent: Your movie list:
Inception

Your question: Pick something for me
Agent: Random movie suggestion: Inception

Your question: Remove Inception
Agent: Inception removed from your list
```

Other supported examples include:

```text
Add Interstellar
Save The Matrix to my list
Show me all my movies
What should I watch?
Delete Titanic from my watchlist
```

To stop the application, enter:

```text
quit
```

or:

```text
exit
```

## Data storage

The watchlist is stored in a local SQLite database named:

```text
watchlist.db
```

The database is created automatically when the application starts or when a watchlist tool is first used.

## Tech stack

- **Python**
- **LangChain**
- **LangGraph**
- **Anthropic Claude**
- **SQLite**
- **python-dotenv**
- **uv**
