#%%
from config import Config
import os

if Config.LOCAL_TEST:
    from dotenv import load_dotenv
    load_dotenv()

# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
LLMAAS_OPENAI_API_KEY = os.environ.get("LLMAAS_OPENAI_API_KEY")

#%%
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    api_key=LLMAAS_OPENAI_API_KEY,
    openai_api_base=Config.LLMAAS_BASEURL,
    model="gpt-4o-mini-prd-gcc2-lb",
    temperature=0.2 ,
    extra_body={
        "llmaas": {
            "guardrails": {
                "enforced": False,
                "sentinel": {
                    "input": {
                        "lionguard-binary": {
                            "threshold": 0.95
                        }
                    },
                    "output": {
                        "lionguard-binary": {
                            "threshold": 0.95
                        }
                    }
                }
            }
        }
    }
)

#%%
for chunk in model.stream("Write me a 1 verse song about goldfish on the moon"):
    print(chunk.content, end="|", flush=True)
# %%
async for chunk in model.astream("Write me a 1 verse song about goldfish on the moon"):
    print(chunk.content, end="|", flush=True)
# %%
