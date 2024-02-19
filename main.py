import os
from getpass import getpass
import psycopg2
from langchain.sql_database import SQLDatabase
from langchain_openai import OpenAI
from langchain_experimental.sql import SQLDatabaseChain
from dotenv import load_dotenv


load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')

if (openai_key == None):
    openai_key = getpass('Provide your OpenAI API key: ')

if (not openai_key):
    raise Exception('No OpenAI API key provided. Please set the OPENAI_API_KEY environment variable or provide it when prompted.')

print('OpenAI API key set.')


def prepare_agent_prompt(input_text):
    agent_prompt = f"""
    Query the database using PostgreSQL syntax.

    Use the shoe_color enum to query the color. Do not query this column with any values not found in the shoe_color enum.
    Use the shoe_width enum to query the width. Do not query this column with any values not found in the shoe_width enum.

    The color and width columns are array types. The name column is of type VARCHAR.
    An example query using an array columns would be:
    SELECT * FROM products, unnest(color) as col WHERE col::text % SOME_COLOR;
    or
    SELECT * FROM products, unnest(width) as wid WHERE wid::text % SOME_WIDTH;

    An example query using the name column would be:
    select * from products where name ILIKE '%input_text%';

    It is not necessary to search on all columns, only those necessary for a query. 
    
    Generate a PostgreSQL query using the input: {input_text}. 
    
    Answer needs to be in the format of a JSON object. 
    This object needs to have the key "query" with the SQL query and "query_response" as a JSON array of the query response.
    """

    return agent_prompt




# Initialize the OpenAI's agent
openai = OpenAI(
    api_key=openai_key,
    temperature=0, # the model's creativity. 0 = deterministic output with minimal creativity. 1 = very diverse and creative.
    max_tokens=-1 # the maximum number of tokens to generate in the completion. -1 returns as many tokens as possible given the prompt and the models maximal context size
    )

# Initialize LangChain's database agent
database = SQLDatabase.from_uri(
    "postgresql+psycopg2://sql_agent:password@localhost:5432/postgres", 
    include_tables=["products", "users", "purchases", "product_inventory"]);

# Initialize LangChain's database chain agent
db_chain = SQLDatabaseChain.from_llm(openai, db=database, verbose=True, use_query_checker=True, return_intermediate_steps=True)


user_prompt=input("Ask a question: ")
agent_prompt = prepare_agent_prompt(user_prompt)

try:
    result = db_chain.invoke(agent_prompt)

    print(f"Answer: {result['result']}")
except (Exception, psycopg2.Error) as error:
    print(error)