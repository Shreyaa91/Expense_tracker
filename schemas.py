from pydantic import BaseModel
from datetime import date

class Validate(BaseModel):
    id:int
    date:date
    amount:int
    description:str =None
    category:str