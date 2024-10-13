from swarm import Swarm, Agent
from openai import OpenAI


OPENAI_API_KEY = "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"
openai_client = OpenAI(api_key=OPENAI_API_KEY)
client = Swarm(client=openai_client)

python_expert = Agent(
    name="Python Expert",
    instructions="I am an expert in Python programming. I can help with Python syntax, best practices, and advanced concepts.",
)

data_structures_expert = Agent(
    name="Data Structures Expert",
    instructions="I specialize in data structures. I can explain various data structures and their implementations in different programming languages.",
)

algorithms_expert = Agent(
    name="Algorithms Expert",
    instructions="I am well-versed in algorithms. I can help with algorithm design, analysis, and optimization techniques.",
)

web_development_expert = Agent(
    name="Web Development Expert",
    instructions="I am knowledgeable in web development. I can assist with frontend and backend technologies, frameworks, and best practices.",
)

database_expert = Agent(
    name="Database Expert",
    instructions="I specialize in database systems. I can help with database design, SQL queries, and database management.",
)

machine_learning_expert = Agent(
    name="Machine Learning Expert",
    instructions="I am an expert in machine learning. I can assist with ML algorithms, model selection, and implementation details.",
)

expert_agents = [
    python_expert,
    data_structures_expert,
    algorithms_expert,
    web_development_expert,
    database_expert,
    machine_learning_expert,
]

router_agent = Agent(
    name="Router Agent",
    instructions="I am a router agent. I analyze the user's query and direct it to the most appropriate domain expert from the list of experts defined above (Python Expert, Data Structures Expert, Algorithms Expert, Web Development Expert, Database Expert, and Machine Learning Expert). If the query spans multiple domains, I can involve multiple experts from this list. My primary role is to ensure that queries are routed to the most relevant expert(s) for comprehensive and accurate responses.",
)

for expert in expert_agents:

    def expert_wrapper():
        return expert

    router_agent.functions.append(expert_wrapper)


def get_response(content):
    return client.run(
        agent=router_agent,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content},
        ],
    )


if __name__ == "__main__":
    for part in get_response("What is Machine Learning?"):
        print(part)
