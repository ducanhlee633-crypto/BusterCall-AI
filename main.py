from fastapi import FastAPI
import requests
import json
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from bounty_evaluator_prompt import SYSTEM_PROMPT
app = FastAPI()
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
class Format(BaseModel):
    name : str
    crew_name : str
    devil_fruit : str
    observation_haki : bool
    armament_haki: bool
    conqueror_haki : bool
    achievement : str
@app.get("/")
def home():
    return {"message":"BusterCall-AI"}
@app.post("/bounty")
def bounty_evaluator(message:Format):
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
    })
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]