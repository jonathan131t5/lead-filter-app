from fastapi import FastAPI
from pydantic import BaseModel
from service.service_upgrade import ServiceLayer

from fastapi import Request, Response
import uuid

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

service_layer = ServiceLayer()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def serve_chat():
    return FileResponse("chat2.html")


class MessageRequirements(BaseModel):
    name: str | None = None
    content: str | None = None
    

@app.post("/message")
def run_message_flow(
    data: MessageRequirements,
    request: Request,
    response: Response
):
    try:
        session_id = request.cookies.get("session_id")

        if session_id is None:
            session_id = str(uuid.uuid4())
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                samesite="lax"
            )

        result = service_layer.process_lead_message(
            session_id=session_id,
            name=data.name,
            content=data.content
        )

        return {
            "content": result["message"],
            "status": result.get("status")
        }

    except Exception as e:
        return {
            "content": str(e),
            "status": "error"
        }

