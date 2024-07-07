"""
Router File:
- Handles routes related to general Web functionality
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../static")
router = APIRouter(
    prefix="", # This will be the prefix of the API
    tags=["Web"], # This will be the tag for the API documentation
)


# Serve index.html for the root URL
@router.get("/")
async def read_root():
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)

# Serve other HTML files in the static directory directly by their paths
@router.get("/{file_path:path}")
async def serve_file(file_path: str):
    file_path = os.path.join(static_dir, file_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return FileResponse(os.path.join(static_dir, "404.html"))  # Assuming you have a 404.html for not found pages