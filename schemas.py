from pydantic import BaseModel, ConfigDict, Field, EmailStr



class UserBase(BaseModel):
    user_name : str
    email: EmailStr

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes = True)
    id : int
class Bounty_evaluator_input(BaseModel):
    name : str
    crew_name : str
    devil_fruit : str
    observation_haki : bool
    armament_haki: bool
    conqueror_haki : bool
    achievement : str

class Bounty_evaluator_output(BaseModel):
    bounty : int = Field(ge = 1000, le = 10000000000)
    threat_level : str = Field(min_length = 1, max_length = 3)
    reasoning : str = Field(min_length = 1)

class Devil_fruit_evalutor(BaseModel):
    devil_fruit : str

class Battle_simulator(BaseModel):
    character_1: str
    character_2: str
    location : str

class Update_user(BaseModel):
    user_name : str
    email : EmailStr