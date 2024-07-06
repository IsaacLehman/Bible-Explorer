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
@app.get("/")
def read_root():
    return "Welcome to the Bible Explorer API!"


from router.api.ai_routes import router as ai_router
app.include_router(ai_router)

