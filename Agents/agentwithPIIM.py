import os 
from dotenv import load_dotenv 
load_dotenv() 
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
Weather_API_Key = os.getenv("OPENWEATHER_API_KEY")

import warnings

warnings.filterwarnings("ignore",category=DeprecationWarning)

from langchain.chat_models import init_chat_model

#llm = init_chat_model(model="qwen/qwen3-32b", model_provider="Groq")
llm_primary = init_chat_model(model="llama-3.3-70b-versatile", model_provider="Groq")
llm_fallback_1 = init_chat_model(model="gpt-5.4-nano", model_provider="OpenAI")
llm_fallback_2 = init_chat_model(model="gpt-5.4-mini", model_provider="OpenAI")

#print(llm.invoke("Hi").content)
#print("llm profile",llm.profile)

## Create a weather tool 
from langchain.tools import tool
import requests

from groq import RateLimitError as GroqRateLimitError 
from openai import RateLimitError as OPenAIRateLimitError

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

## Add memory 

from langgraph.checkpoint.memory import InMemorySaver

#Create LLM Agent 

from langchain.agents import create_agent 

tools = [getWeather,web_search,ddg_search]

##apply middleware 
from langchain.agents.middleware import SummarizationMiddleware, ModelFallbackMiddleware, PIIMiddleware

 
agent = create_agent(
    model=llm_primary,
    tools=tools,
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model=llm_fallback_1,trigger=("tokens",8000),keep=("messages",5)
        ),
        ModelFallbackMiddleware(
            llm_fallback_1, llm_fallback_2
        ),
        PIIMiddleware(pii_type="email",strategy="redact",apply_to_input=True),
        PIIMiddleware(pii_type="credit_card",strategy="redact",apply_to_input=True), 
         PIIMiddleware(pii_type="api_key",strategy="mask",detector=r"g?sk[a-zA-Z0-9_-]{16,32}", apply_to_input=True)
    ],
    system_prompt="""
    You are an helpful chatbot assistant. Use getWeather tool for answering weather related 
    questies. Use web_search tool for recent event, finance, news and internet search. 
    use ddg_search when web_search is not available. 
    For normal chat conversion don't use a tool, just answer of your own.
    """
)

#Create a thread ID

thread_config = {"configurable":{"thread_id":1}}

##Create the weather app 
from langchain.messages import HumanMessage, SystemMessage, AIMessage

while True:
    messages = []
    user_input = input("What is your query? ")

    if(user_input.lower() in ["bye","exit"]):
        print("Bye!")
        exit()

    messages.append(HumanMessage(content=user_input))

    try: 
        final_result = agent.invoke({"messages":messages},thread_config)
        print(final_result["messages"][-1].content)
        #print("\nMeta information",final_result["messages"][-1].response_metadata)
    except (GroqRateLimitError, OPenAIRateLimitError) as error:
        print(f"Rate limit exception happened. Error: {error}")
    except Exception as e: 
        print(f"Details error: {e}")



