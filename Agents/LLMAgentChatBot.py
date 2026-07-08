import os 
from dotenv import load_dotenv 
load_dotenv() 
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
#os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
Weather_API_Key = os.getenv("OPENWEATHER_API_KEY")

from langchain.chat_models import init_chat_model

llm = init_chat_model(model="qwen/qwen3-32b", model_provider="Groq")
#llm = init_chat_model(model="gpt-5.4-mini", model_provider="OpenAI")
print(llm.invoke("Hi").content)

## Create a weather tool 
from langchain.tools import tool
import requests

@tool
def getWeather(location:str)->str:
    """Return the weather information based on the given location and or zipcode"""
    url = "https://api.openweathermap.org/data/2.5/weather?"

    params={
        "q":location,
        "appid":Weather_API_Key,
        "units":"imperial"
    }

    try:
        response = requests.get(url,params=params,timeout=10)
        return response.json()
    except:
        return f"The requested weather information is not available"



# Search tool using Tavily 
from langchain_tavily import TavilySearch

web_search = TavilySearch(
    max_results=3, 
    topic="general",
    search_depth="basic"
)


# Create duckduckgosearch 

from langchain_community.tools import DuckDuckGoSearchRun 

ddg_search = DuckDuckGoSearchRun()

#Create LLM Agent 

from langchain.agents import create_agent 

tools = [getWeather,ddg_search]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    You are an helpful chatbot assistant. Use getWeather tool for answering weather related 
    questies. Use web_search tool for recent event, finance, news and internet search. 
    use ddg_search when web_search is not available. 
    For normal chat conversion don't use a tool, just answer of your own.
    """
)

##Create the weather app 
from langchain.messages import HumanMessage, SystemMessage, AIMessage

messages = []
user_input = input("What is your query? ")
messages.append(HumanMessage(content=user_input))

final_result = agent.invoke({"messages":messages})

print(final_result["messages"][-1].content)



