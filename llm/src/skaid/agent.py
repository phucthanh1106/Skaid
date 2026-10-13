from langchain.agents import create_agent
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from src.skaid.tools import multiply, get_weather

# Create the Groq-hosted model.
model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

# Create the agent using Groq-hosted model
agent = create_agent(
    model=model, 
    tools=[multiply, get_weather],
    checkpointer=InMemorySaver(),
)

def main():
    config = {"configurable": {"thread_id": str(uuid7())}}
    questions = ["Use a tool to calculate 23 multiplied by 17.", "Multiply today's weather temperature in Boston with 10", "Say hello without using a tool."]

    for question in questions:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": f"{question}"}]},
            config=config,
        )

        messages = result["messages"]

        for message in messages:
            message.pretty_print()

# Only start the conversation when executed directly
if __name__ == "__main__":
    main()
