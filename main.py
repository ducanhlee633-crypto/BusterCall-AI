from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
import requests
import json
from dotenv import load_dotenv
import os
from schemas import Bounty_evaluator_input, Devil_fruit_evalutor, Bounty_evaluator_output, UserBase, UserResponse, Battle_simulator,Update_user_partial, Update_user_fully
from bounty_evaluator_prompt import SYSTEM_PROMPT_BOUNTY
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from db import Base, get_db, engine
from battle_simulator_prompt import SYSTEM_PROMPT_BATTLE
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException



Base.metadata.create_all(bind = engine)
app = FastAPI()
load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class LLM:
    def analyze(self, prompt):
        try:
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
                    "content": f"{prompt}"
                }
                ]
            }),
            timeout = 30
            )
            response.raise_for_status()
            data = response.json()
            result =  data["choices"][0]["message"]["content"]
            result = json.loads(result)
            return result
        except requests.exceptions.HTTPError as http_err:
            status_code = response.status_code

            try: 
                error_detail = response.json().get("error", {})
                error_msg = error_detail.get("message", response.text)
            except Exception:
                error_msg = response.text
            if status_code == 401:
                raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = error_msg)
            elif status_code == 402:
                raise HTTPException(status_code = status.HTTP_402_PAYMENT_REQUIRED, detail = error_msg)
            elif status_code == 400:
                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = error_msg)
            elif status_code == 429:
                raise HTTPException(status_code = status.HTTP_429_TOO_MANY_REQUESTS, detail = error_msg)
            elif status_code in (502, 503):
                raise HTTPException(status_code = status.HTTP_502_BAD_GATEWAY, detail = error_msg)
            else:
                print(f"Lỗi HTTP {status_code}: {error_msg}")
        except requests.exceptions.Timeout:
            raise HTTPException(status_code = status.HTTP_504_GATEWAY_TIMEOUT, detail = "Timeout, try again")
        except requests.exceptions.ConnectionError:
            print("Lỗi ConnectionError: Mất kết nối internet, DNS hỏng hoặc OpenRouter down.")
        except requests.exceptions.RequestException as e:
            print(f"Lỗi chung hệ thống requests: {e}")


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


@app.put("/api/users/{id}", response_model = UserResponse)
def update_user_fully(id : int,update_user:Update_user_fully, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == id),)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Not Found")
    user.user_name = update_user.user_name
    user.email = update_user.email
    user.id = update_user.id
    db.commit()
    db.refresh(user)
    return user

@app.patch("/api/users/{id}", response_model = UserResponse)
def update_user_partly(id : int,update_user:Update_user_partial, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == id),)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Not Found")
    update_data = update_user.model_dump(exclude_unset = True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user



@app.delete("/api/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id : int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == id),)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Not Found")
    db.delete(user)
    db.commit()






@app.post("/api/v1/bounty/assess", response_model = Bounty_evaluator_output) #áp dụng response model
def bounty_evaluator(message:Bounty_evaluator_input):
    bounty_evaluator = LLM()
    prompt = f"{SYSTEM_PROMPT_BOUNTY}. Follow the instrution above to analyze.The character is {message.name}, which is in {message.crew_name}. There is some stat and achievement of this character: Devil_Fruit: {message.devil_fruit}; observation_haki:{message.observation_haki}; armament_haki:{message.armament_haki}; conqueror_haki:{message.conqueror_haki}; achievement:{message.achievement}. "
    result = bounty_evaluator.analyze(prompt)
    return result
@app.post("/api/v1/battle/simulate")
def battle_simulator(message : Battle_simulator):
    battle_simulate = LLM()
    prompt = f"{SYSTEM_PROMPT_BATTLE}. Follow the instrution above to analyze. {message.character_1}vs{message.character_2} in {message.location}"
    result = battle_simulate.analyze(prompt)
    return result
@app.post("/api/v1/encyclopedia/query") 
def encyclopedia(message:Devil_fruit_evalutor):
    try:
        url = "https://api.api-onepiece.com/v2/fruits/en"
        response = requests.get(url, timeout = 20)
        data = response.json()
        for fruit in data:
            if fruit.get("roman_name") == message.devil_fruit:
                return fruit
    except requests.exceptions.Timeout:
        raise HTTPException(status_code = status.HTTP_504_GATEWAY_TIMEOUT, detail = "Timeout, try again")




@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request:Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "Some issue occur during the analyzation"
    )
    if request.url.path.startswith("/docs"):
        return JSONResponse(
            status_code = exception.status_code,
            content =  {"detail": message}
        )