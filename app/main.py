from typing import Union, List, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel, Field
from shared.ai import ai_chat, Message

"""
======================================================= FASTAPI =======================================================
"""
app = FastAPI()

"""
====================================================== DATABASE INTI =======================================================
"""
import db.models as models
from db.controller import create_db_and_tables, engine
create_db_and_tables()

"""
====================================================== ROUTES =======================================================
"""




class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

# Post route to send an AI chat message
@app.post("/ai/chat")
def chat_with_ai(messages: List[Message], model: str = "gpt-3.5-turbo"):
    print('Received chat history:', messages)    
    response = ai_chat('api docs', messages, model=model)
    
    return response