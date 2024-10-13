from swarm import Swarm, Agent
from openai import OpenAI
from websearch import scrape_web
import os
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = Swarm(client=openai_client)

# Define domain expert agents using lambda functions
python_expert = Agent(
    name="Python Expert",
    instructions="I am an expert in Python programming. I can help with Python syntax, best practices, and advanced concepts.",
)

math_expert = Agent(
    name="Math Expert",
    instructions="I specialize in math. I can explain, analyze, and solve various mathematical problems with clear and concise reasoning",
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

quantum_systems_expert = Agent(
    name="Quantum Systems Expert",
    instructions="I am an expert in quantum systems. I can assist with quantum algorithms, model selection, and implementation details.",
)

# Add the new context-adding expert
context_adding_expert = Agent(
    name="Context Adding Expert",
    instructions="""
    I am a specialized agent that adds the user's question and the suggested answer to the context without redirecting to other experts.
    My primary responsibility is to:
    1. Accept the user's question and the suggested answer.
    2. Add this information to the context without any modifications or redirections.
    3. Return the combined context (question + answer) as is.
    I do not provide any additional analysis or redirection to other experts. 
    """,
)

# google_search_agent = Agent(
#     name="Google Search Agent",
#     instructions="I am an expert in using Google Search to find relevant information. I can help with web searches and summarizing search results.",
#     functions=[web_search],
# )

# search_results_decider_analyzer = Agent(
#     name="Search Results Decider and Analyzer",
#      instructions="I am an expert in analyzing search results and deciding which results to use for their html text. I can help with analyzing search results and deciding which results to use for their html text.",
#      functions=[get_html_content],
# )

# web_information_extractor = Agent(
#     name="Web Information Extractor",
#     instructions="I am an expert in extracting information from web pages. I can help with extracting information from web pages.",
# )
web_scraper_agent = Agent(
    name="Web Scraper Agent",
    instructions="""
    I am a specialized web scraper agent capable of gathering information from the internet using the "scrape_web" function.
    My primary responsibilities include:
    1. Executing web searches using 'scrape_web' to find relevant online content.
    2. Scraping and extracting useful data from the search results.
    3. Processing and summarizing the scraped information to provide concise and relevant answers.
    4. Handling various types of queries that require up-to-date or specific online information.
    IF THE RESPONSE IF VERY LONG, SUMMARIZE IT AND CITE THE SOURCES IF YOU CAN.
    I will always utilize the "scrape_web" function when tasked with retrieving current data or answering questions that necessitate web-based research.
    """,
    functions=[scrape_web],
)


expert_agents = [
    python_expert,
    math_expert,
    data_structures_expert,
    algorithms_expert,
    web_development_expert,
    database_expert,
    machine_learning_expert,
    quantum_systems_expert,
    context_adding_expert,  # Add the new expert to the list
    # web_scraper_agent,
]

router_agent = Agent(
    name="Router Agent",
    instructions="""I am a router agent. I analyze the user's query and direct it to the most appropriate domain expert from the list of experts defined above (Python Expert, Math Expert, Data Structures Expert, Algorithms Expert, Web Development Expert, Database Expert, Machine Learning Expert, and Web Scraper Agent for getting information). If the query spans multiple domains, I can involve multiple experts from this list. My primary role is to ensure that queries are routed to the most relevant expert(s) for comprehensive and accurate responses.
    If the user specifically asks for up-to-date information or if their query requires real-time data, I will use the web scraper agent.
    If I cannot route the query to any of the specific domain experts, I will default to using the web scraper agent to answer the question.""",
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
