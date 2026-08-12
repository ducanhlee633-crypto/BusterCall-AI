from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
import requests
import json
from dotenv import load_dotenv
import os
from schemas import Bounty_evaluator_input, Devil_fruit_evalutor, Bounty_evaluator_output, UserBase, UserResponse
from bounty_evaluator_prompt import SYSTEM_PROMPT
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from db import Base, get_db, engine


Base.metadata.create_all(bind = engine)
app = FastAPI()
load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")



@app.post("/api/users", response_model = UserResponse, status_code = status.HTTP_201_CREATED)
def create_user(user : UserBase, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.user_name == user.user_name),)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User already exists")
    result = db.execute(select(models.User).where(models.User.email == user.email),)
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User already exists")
    new_user = models.User(
        user_name = user.user_name,
        email = user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/users/{id}", response_model = UserResponse)
def get_user(id : int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == id),)
    existing_user = result.scalars().first()
    if existing_user:
        return existing_user
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Not Found")


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
