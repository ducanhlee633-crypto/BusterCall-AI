from pydantic import BaseModel, ConfigDict, Field, EmailStr



class UserBase(BaseModel):
    user_name : str
    email: EmailStr
class Update_user_fully(UserBase):
    id : int
class Update_user_partial(BaseModel):
    user_name : str|None = Field(default = None, min_length = 1, max_length = 100)
    email: EmailStr|None = Field(default = None, min_length = 1, max_length = 100)
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
    character_1: Bounty_evaluator_input
    character_2: Bounty_evaluator_input
    location : str

