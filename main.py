from fastapi import FastAPI
import requests
import json
from dotenv import load_dotenv
import os
import re
from schemas import Bounty_evaluator_input, Devil_fruit_evalutor, Bounty_evaluator_output
from bounty_evaluator_prompt import SYSTEM_PROMPT

app = FastAPI()
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")



@app.get("/")
def home():
    return {"message":"BusterCall-AI"}



@app.post("/api/v1/bounty/assess", response_model = Bounty_evaluator_output) #áp dụng response model
def bounty_evaluator(message:Bounty_evaluator_input):
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    },
    data=json.dumps({
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "messages": [
        {
            "role": "user",
            "content": f"{SYSTEM_PROMPT}. Follow the instruction and the pirate is {message.name}, which in {message.crew_name}. Devil fruit : {message.devil_fruit}; observation_haki: {message.observation_haki}; armament_haki:{message.armament_haki}; conqueror_haki:{message.conqueror_haki}; achievement:{message.achievement}"
        }
        ]
    }),
    timeout = 30
    )
    data = response.json()
    result =  data["choices"][0]["message"]["content"]
    result = json.loads(result)
    return result



@app.post("/api/v1/encyclopedia/query") 
def encyclopedia(message:Devil_fruit_evalutor):
    url = "https://api.api-onepiece.com/v2/fruits/en"
    response = requests.get(url)
    data = response.json()
    for fruit in data:
        if fruit.get("roman_name") == message.devil_fruit:
            return fruit
