import os 
from dotenv import load_dotenv 
load_dotenv() 
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
Weather_API_Key = os.getenv("OPENWEATHER_API_KEY")

from langchain.chat_models import init_chat_model

#llm = init_chat_model(model="llama-3.3-70b-versatile", model_provider="Groq")
llm = init_chat_model(model="gpt-5.4-mini", model_provider="OpenAI")
print(llm.invoke("Hi").content)

## Create a weather tool 
from langchain.tools import tool
import requests

@tool
def getWeather(location:str, zipcode:str)->str:
    """Return the weather information based on the given location and or zipcode"""
    url = "https://api.openweathermap.org/data/2.5/weather?"

    params={
        "q":location,
        "zip":zipcode,
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

llm_with_tools = llm.bind_tools([getWeather,web_search])

##Create the weather app 
from langchain.messages import HumanMessage, SystemMessage, AIMessage

messages = [
    SystemMessage(content="You are an helpful assistant. " \
    "Please respond the weather information based on the getWeather tool call" \
    "For internet search and current information and news use web_search tool" \
    "For other information you don't need to call a tool")
]

user_input = input("What is your query? ")
messages.append(HumanMessage(content=user_input))

aiMessage = llm_with_tools.invoke(messages)
#print("AIMessage: ",aiMessage)
messages.append(aiMessage)

#tool message 

tool_name=""
for tool_call in aiMessage.tool_calls:
    if(tool_call["name"]==getWeather.name):
        toolMessage = getWeather.invoke(tool_call)
        tool_name = getWeather.name
    elif(tool_call["name"]==web_search.name):
        toolMessage = web_search.invoke(tool_call)
        tool_name = web_search.name

    messages.append(toolMessage)

final_reponse = llm_with_tools.invoke(messages)
print("Tool name: ", tool_name)
print(final_reponse.content)

# structured op

# from pydantic import BaseModel 

# class structuredWeather(BaseModel):
#     location:str
#     Min_tempature:float
#     Max_temperature:float
#     wind:str
#     pressure:str
#     humidity:str

# llm_with_structured_op = llm.with_structured_output(structuredWeather)

# final_stutured_response = llm_with_structured_op.invoke(messages)

# print(final_stutured_response)