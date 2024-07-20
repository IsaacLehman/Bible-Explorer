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


# Serve static files
router.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html for the root URL and all other paths (except static files)
@router.get("/{full_path:path}")
async def serve_file(full_path: str):
    file_path = os.path.join(static_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        # Serve index.html for all other paths to handle client-side routing
        return FileResponse(os.path.join(static_dir, "index.html"))