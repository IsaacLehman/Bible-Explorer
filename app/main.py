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
from router.api.ai_routes import router as ai_router
app.include_router(ai_router)


""""
====================================================== STATIC FILES =======================================================
"""
# Mount the static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html for the root URL
@app.get("/")
async def read_root():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)

# Serve other HTML files in the static directory directly by their paths
@app.get("/{file_path:path}")
async def serve_file(file_path: str):
    file_path = os.path.join(static_dir, file_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return FileResponse(os.path.join(static_dir, "404.html"))  # Assuming you have a 404.html for not found pages