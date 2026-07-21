
# Cretae environment
import os 
from dotenv import load_dotenv 
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") 
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


# Get LLM model 
from langchain.chat_models import init_chat_model 

primary_llm = init_chat_model(model="llama-3.3-70b-versatile", model_provider="Groq")

fallback_llm_1 = init_chat_model(model="gpt-5.4-nano", model_provider="openai",
                 model_kwargs={"temperature": 0.5, "max_tokens": 1000})
fallback_llm_2 = init_chat_model(model="gpt-5.4-mini", model_provider="openai",
                 model_kwargs={"temperature": 0.5, "max_tokens": 1000})


from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.messages import SystemMessage, HumanMessage, AIMessage

# def llm node 

def llm_node(state: MessagesState) -> str:
    response = primary_llm.invoke(
        [
            SystemMessage(content="you are a helpful assistant")
        ] + state["messages"] # extract the messages field (list) from the state graph (dictionary)
    )
    return {"messages":[response]}

#Create graph 

graph = StateGraph(MessagesState)
graph.add_node(llm_node)
graph.add_edge(START,"llm_node")
graph.add_edge("llm_node",END)

graph = graph.compile() 

#Display graph 

from IPython.display import Image, display
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# Display result 

response = graph.invoke({
    "messages": [
        HumanMessage(content="What is AI?")
    ]
})

for m in  response["messages"]: 
    m.pretty_print()

