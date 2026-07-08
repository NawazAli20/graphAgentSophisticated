import os

from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["YOU_API_KEY"] = os.getenv("YOU_API_KEY")

OPENWEATHER_API_KEY =os.getenv("OPENWEATHER_API_KEY")

#suppress warning
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


#Get the llm model
from langchain.chat_models import init_chat_model

llm = init_chat_model(model="qwen/qwen3-32b", model_provider="Groq", temperature=0.8, max_tokens=1000)
#llm = init_chat_model(model="gpt-5.4-mini", model_provider="OpenAI", temperature=0.8, max_tokens=1000)
# test_message = llm.invoke("hi").content
# print(test_message)


##Creating tools 

import requests
# getWeather tool 
from langchain.tools import tool

url = "https://api.openweathermap.org/data/2.5/weather?"

@tool
def getWeather(location:str)->str:
    """Returns weather information based on the city and/or given zipcode"""
    params={
        "q":location,
        "appid":OPENWEATHER_API_KEY,
        "units":"imperial" #imperial
    }
    try:
        response = requests.get(url,params=params,timeout=10)
        return response.json()
    except:
        return f"Does not have the weather information"

## Add Tavily Search tool 

from langchain_tavily import TavilySearch 

web_search = TavilySearch(
    max_results=3,
    topic="general",
    seatch_depth="basic"
)

## Add duckduckgosearchrun 

from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults

duck_search = DuckDuckGoSearchResults(); 



tools = [getWeather,web_search,duck_search]

#create an agent 
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""You are an helpfull assistant who gives the answer concisely and to the point. 
    use getWeather tool for weather related query, use web_search 
    for currents news, finance, recent events, stock price, and internet search, 
    use duck_search tool only when web_search is not available;
    for other cases 
    just answer yourlself without invoking a tool."""
)

## Message formatting 
from langchain.messages import AIMessage, HumanMessage, SystemMessage
messages = []
user_input = input("What is your query: ")

# messages.append({
#     "role":"user",
#     "content":user_input
# })

messages.append(HumanMessage(content=user_input))


## Respons with tool calls 
final_response = agent.invoke(
    {"messages":messages})

print("\n..................")
print(final_response["messages"][-1].content)
#print(final_response["messages"][-1].content)
print("\n..................")

