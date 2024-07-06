"""
Router File:
- Handles routes related to general AI functionality
"""
from typing import Union, List, Dict, Any
from fastapi import APIRouter, HTTPException, Request

from shared.ai import ai_chat, Message, AI_Response

router = APIRouter(
    prefix="/api/ai", # This will be the prefix of the API
    tags=["ai"], # This will be the tag for the API documentation
)

@router.post("/chat", response_model=AI_Response)
def chat_with_ai(messages: List[Message], model: str = "gpt-3.5-turbo") -> AI_Response:
    """
    Route to chat with the AI
    """
    try:
        response = ai_chat('api docs', messages, model=model)
        if isinstance(response, dict) and "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
