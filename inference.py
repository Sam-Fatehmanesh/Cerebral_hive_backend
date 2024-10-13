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
    data_structures_expert,
    algorithms_expert,
    web_development_expert,
    database_expert,
    machine_learning_expert,
    context_adding_expert,  # Add the new expert to the list
    # web_scraper_agent,
]

security_expert = Agent(
    name="Security Expert",
    instructions="I specialize in cybersecurity. I can help with encryption, defensive programming, and security best practices."
)
devops_expert = Agent(
    name="DevOps Expert",
    instructions="I am experienced in DevOps practices, including CI/CD, containerization, and managing cloud infrastructure."
)
mobile_development_expert = Agent(
    name="Mobile Development Expert",
    instructions="I specialize in mobile app development for both Android and iOS. I can assist with various frameworks such as Flutter and React Native."
)

# Add the new experts to the list
expert_agents.extend([security_expert, devops_expert, mobile_development_expert])

router_agent = Agent(
    name="Router Agent",
    instructions="""As the router agent, my role is to analyze the user's query and select the most appropriate domain expert from the available list (Python Expert, Data Structures Expert, Algorithms Expert, Web Development Expert, Database Expert, Machine Learning Expert, and more). I will consider the content and context of the query to determine the best expert to send it to. If a query relates to multiple domains, I will involve all relevant experts.

- For queries related to Python, I refer them to the 'Python Expert.'
- For data structure inquiries, I route them to the 'Data Structures Expert.'
- Algorithm-related questions go to the 'Algorithms Expert.'
- Queries about web development are directed to the 'Web Development Expert.'
- Database-related questions are sent to the 'Database Expert.'
- Machine learning queries are handled by the 'Machine Learning Expert.'
- For real-time data or up-to-date information requests, I will utilize the 'Web Scraper Agent.'
- If a query involves exploratory or outside knowledge like current technologies or techniques not covered directly, I may consult with the 'Web Scraper Agent.'

I fall back on providing a query to the 'Web Scraper Agent' if the precise domain isn't clear or if the inquiry requires specific real-time data or updates. I ensure to derive expert advice collaboratively to offer a comprehensive response.""" 
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
