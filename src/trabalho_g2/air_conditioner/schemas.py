from pydantic import BaseModel


class Temperatures(BaseModel):
    normal_celcius: int
    eco_celcius: int
    
    
