from fastapi import FastAPI
from pydantic import BaseModel
from service.service_layer import ServiceLayer

service_layer = ServiceLayer()

app = FastAPI()

class MessageRequirements(BaseModel):
    phone_number : str
    name: str | None = None
    content: str | None = None



@app.post("/message")
def run_message_flow(data : MessageRequirements):
    try:
        result = service_layer.run_lead_flow(
            phone_number=data.phone_number , 
            name=data.name , 
            content=data.content
        )
        return result
    
    except Exception as e:
        return {
            "status" : "error" , 
            "message" : str(e)
        }