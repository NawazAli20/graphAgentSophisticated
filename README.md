
# A simple StateGraph Example 
A MessageState graph with tools is created inside Agents/graphAgentWithTools.py


### How to run 

uv run LangGraphExample.py (for .py file)

run all cells in jupyter notebook (for .ipynb file)


# Repo and Dependencies Installations commands 

Resource Links:
- [Complete youtube playlist](https://www.youtube.com/playlist?list=PLfpB0rPkNb_8)
- [Langgraph docs](https://docs.langchain.com/oss/python/langgraph/overview)
- [Langchain's Pre-build Middlware](https://docs.langchain.com/oss/python/langchain/middleware/built-in)
- [Langchain's middleware](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [Langgraph's short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory) 
- [Langchain Agent](https://docs.langchain.com/oss/python/langchain/agents)
- [DuckDuckGoSearch](https://reference.langchain.com/python/langchain-community/tools/ddg_search/tool/DuckDuckGoSearchRun)
- [Youdotcom API Key](https://you.com/platform/api-keys) 
- [OpenWeatherMap](https://openweathermap.org/)
- [UV github repo](https://github.com/astral-sh/uv)
- [langchain docs]()
- [Groq API Key](https://console.groq.com/keys)
- [OpenAI API Key](https://platform.openai.com/api-keys)

## Install uv On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

## Install uv On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# for a fresh repo
### create a project directory and issue the following commands in the project directory:

uv init

uv venv  

source .venv/bin/activate (#activate .venv)

### then install all the dependecies

uv add *packagename*

Examples: 

uv add langchain

uv add langchain-openai 

uv add langchain-groq 

uv add ipykernel

uv add python-dotenv

#### or if you have listed all the required packages in the requirements.txt, issue: 

uv add -r requirements.txt


# Installations for a cloned repo

git clone https://github.com/NawazAli20/LLMsIntro

if you have .toml and/or .lock file just issue

uv sync 
