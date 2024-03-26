from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from os import getenv
from src.utils.app import get_api
from src.wrapper.lanbot import Langbot
import time
import json
from langchain_core.runnables import RunnableLambda, chain
# fastapi instance declaration
app = FastAPI()

# get tables path
load_dotenv()
TABLES_PATH = getenv('TABLES_PATH')
# api functions
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/wrap/{query}")
async def wrap(query):
    return StreamingResponse(Langbot(query, get_api, [], TABLES_PATH), media_type="application/json")

@app.get("/query/{query}")
async def read_item(query: str):
    api_url, data, text_response = get_api(query, TABLES_PATH)

    return {
            "query":
                {
                    "question": query, 
                    "answer": text_response, 
                    "url": api_url
                }
            }


#test 
@chain
def just(input):
    for w in input['input'].split(' '):
        yield w 
    #return {'data': 'abcd', 'data2':'wxyz'}

@chain
def fn(input):
    print(input)
    yield json.dumps({'msg':input})
    time.sleep(4)
    yield json.dumps({'msg':input})

def fn2():
    chain = just | fn
    time.sleep(2)
    for val in just.stream({'input':'the jumping flying fox'}):
        yield val

@app.get("/num/")
async def num():
    return StreamingResponse(fn2(), media_type="application/json")

