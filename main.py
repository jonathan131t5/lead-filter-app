from fastapi import FastAPI
from pydantic import BaseModel
from service.service_upgrade import ServiceLayer

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

service_layer = ServiceLayer()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def serve_chat():
    return FileResponse("chat2.html")


class MessageRequirements(BaseModel):
    name: str
    content: str | None = None


@app.post("/message")
def run_message_flow(data : MessageRequirements):
    try:
        result = service_layer.run_lead_flow(
            phone_number=data.phone_number , 
            name=data.name , 
            content=data.content
        )
        return {
            "content": result["message"]
            }
    
    except Exception as e:
        return {
            "content": str(e),
            "status": "error"
        }
    

