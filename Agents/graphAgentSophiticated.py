# %% [markdown]
# # Create a simple langchain graph

# %%
import os 
from dotenv import load_dotenv 
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") 
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

OPENWEATHER_API_KEY =os.getenv("OPENWEATHER_API_KEY")

# %%
## ratelmit error 
from openai import RateLimitError as OpenAIRateLimitError 
from groq import RateLimitError as GroqRateLimitError



# %%
# response = llm_gemma.invoke("What is LangGraph?")
# print(response.content)

# %%
from langchain.chat_models import init_chat_model 

primary_llm = init_chat_model(model="llama-3.3-70b-versatile", model_provider="Groq")

llm_gemma = init_chat_model(model="gemma4:latest", model_provider="ollama")

fallback_llm_1 = init_chat_model(model="gpt-5.4-nano", model_provider="openai",
                 model_kwargs={"temperature": 0.5, "max_tokens": 1000})
fallback_llm_2 = init_chat_model(model="gpt-5.4-mini", model_provider="openai",
                 model_kwargs={"temperature": 0.5, "max_tokens": 1000})

# %% [markdown]
# # Create a graph Agent

# %%
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.messages import SystemMessage, HumanMessage, AIMessage

# %% [markdown]
# # Create weather tool

# %%
# Create weather tool
from langchain.tools import tool
import requests

url = "https://api.openweathermap.org/data/2.5/weather?"

@tool
def getWeather(location:str)->str:
    """Returns weather information based on the city and/or zipcode"""
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

# %% [markdown]
# # Create Tavily search tool 

# %%
## Add Tavily Search tool 

from langchain_tavily import TavilySearch 

web_search = TavilySearch(
    max_results=3,
    topic="news",
    search_depth="basic"
)

# %%
#web_search.invoke("Top US news today")

# %% [markdown]
# # Cretae duckduckgosearch

# %%
## Add duckduckgosearchrun 

from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults

duck_search = DuckDuckGoSearchResults(); 

# %% [markdown]
# # Create tools set

# %%
tools = [getWeather, web_search, duck_search]
tool_names = {tool.name: tool for tool in tools}
tool_names

# %% [markdown]
# # Create llm_node

# %%
# def llm node 

llm_with_tools = primary_llm.bind_tools([getWeather, web_search])
def llm_node(state: MessagesState) -> str:
    response = llm_with_tools.invoke(
        [
            SystemMessage(content="you are a helpful assistant. Use getWeather tool call for weather related query, use duck_search tool current news, affairs, and stocks, summerize the result and then give the natural response; otherwise, just answer yourself")
        ] + state["messages"] # extract the messages field (list) from the state graph (dictionary)
    )
    return {"messages":[response]}

# %% [markdown]
# # Create alternative tool_node

# %%
from langgraph.prebuilt import ToolNode, tools_condition 

tool_node_pre = ToolNode(tools)



# %% [markdown]
# # Generate the graph

# %%
## Add short-term memory 
from langgraph.checkpoint.memory import InMemorySaver

# %%
graph = StateGraph(MessagesState)
graph.add_node("llm_node",llm_node)
#graph.add_node(tool_node)
graph.add_node("tools", tool_node_pre) #in built tool node

graph.add_edge(START,"llm_node")
# graph.add_conditional_edges(
#     "llm_node", should_continue, ["tool_node", END]
# )
#conditional edge for in-built tool node
graph.add_conditional_edges( 
    "llm_node", tools_condition, ["tools",END]
)
graph.add_edge("tools","llm_node")

memory = InMemorySaver()
graph = graph.compile(checkpointer=memory) #with memory 
#graph = graph.compile() #without memory
graph

# %%
# from IPython.display import Image, display
# display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# %%
config = {"configurable":{"thread_id":1}}

# %%
try:
    response = graph.invoke({
        "messages": [
            HumanMessage(content="My name is Nawaz.")
        ]
    },config=config)


    for m in  response["messages"]: 
        m.pretty_print()


    response = graph.invoke({
        "messages": [
            HumanMessage(content="What is my name?")
        ]
    },config=config)


    for m in  response["messages"]: 
        m.pretty_print()

except (OpenAIRateLimitError, GroqRateLimitError) as limiterror:
    print("LLM rate limit exceeds. Error:",limiterror)
except Exception as e:
    print("Could not process your request. Error:",e)

# %% [markdown]
# # Get the state of the graph

# %%
graph.get_state(config).values["messages"]


