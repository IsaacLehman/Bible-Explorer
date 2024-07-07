from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os


"""
======================================================= FASTAPI =======================================================
"""
app = FastAPI()


"""
====================================================== DATABASE INTI =======================================================
"""
import db.models # Need to be imported first before creating the tables
from db.controller import create_db_and_tables
create_db_and_tables()


"""
====================================================== ROUTES =======================================================
"""
from router.api.routes import router as ai_router
app.include_router(ai_router)

from router.web.routes import router as web_router
app.include_router(web_router)


""""
====================================================== STATIC FILES =======================================================
"""
# Mount the static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
