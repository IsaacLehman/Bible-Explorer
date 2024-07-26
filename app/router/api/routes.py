"""
Router File:
- Handles routes related to general AI functionality
"""
from typing import Union, List, Dict, Any
from fastapi import APIRouter, HTTPException, Request
import json

from shared.ai import ai_chat, Message, AI_Response
from shared.bible import BibleVerse, BibleSearchResponse, search_bible, get_bible_versions

ai_router = APIRouter(
    prefix="/api/ai", # This will be the prefix of the API
    tags=["AI"], # This will be the tag for the API documentation
)

bible_router = APIRouter(
    prefix="/api/bible", # This will be the prefix of the API
    tags=["Bible"], # This will be the tag for the API documentation
)

"""
======================================================= AI ROUTES =======================================================
"""
@ai_router.post("/chat", response_model=AI_Response)
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
    
@ai_router.post("/object-lesson-ideas", response_model=AI_Response)
def object_lesson_ideas(topic: str, age_group: str = "1st through 6th Grade", model: str = "gpt-3.5-turbo") -> AI_Response:
    """
    Route to generate object lesson ideas
    """
    try:
        system_prompt = """\
        You are an expert at the Bible and at teaching/engaging people. Your job is to generate practical and Biblical object lesson ideas for a teacher.
        - Note, an object lesson is a teaching method that uses a physical object to demonstrate a spiritual truth.
        You will be provided with a lesson topic and an age group. Respond with a JSON list of object lesson ideas in the following format:

        Example Format:
        ```json
        {
            "object_lesson_ideas": [
                {
                    "title": "{{title}}",
                    "description": "{{description}}", // What the object lesson is about and how it relates to the lesson topic
                    "how_to": "{{how_to}}", // Step-by-step instructions on how to conduct the object lesson. Be detailed and clear in exactly how the teacher should teach/present the object lesson.
                    "engagement_tips": ["{{tip1}}", "{{tip2}}", ...], // Tips to engage the students
                    "materials": ["{{material1}}", "{{material2}}", ...], // List of materials needed
                    "time_estimate": "{{time_estimate}}" // e.g., "15-20 minutes". Valid Options: "0-5 minutes", "5-10 minutes", "10-15 minutes", "15-20 minutes", "20-30 minutes"
                },
                ... // More object lesson ideas here, repeat as needed
            ]
        }
        ```
        
        Instructions:
        Generate between 2 and 5 object lesson ideas for the teacher. Vary the ideas to cover different aspects of the lesson topic and age group.
        - Ensure the object lessons are age-appropriate, practical, engaging, and Biblically sound. 
        - Include clear instructions and tips for the teacher.

        
        Respond only with the object lesson ideas JSON object, do not add any commentary.
        """
        user_prompt = f"Lesson Topic: {topic}\nAge Group: {age_group}"
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]
        
        response = ai_chat('object lesson ideas', messages, model=model)
        if isinstance(response, dict) and "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        # Parse the response to get the object lesson ideas
        try:
            # Strip everything before the first { and after the last }
            response_text = response.output
            response_text = response_text[response_text.index("{"):]
            response_text = response_text[:response_text.rindex("}") + 1]
            response_dict = json.loads(response_text)
            object_lesson_ideas = response_dict.get("object_lesson_ideas", [])
            response.output = object_lesson_ideas
        except Exception as e:
            response.output = str(e)
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

"""
======================================================= BIBLE ROUTES =======================================================
"""
@bible_router.get("/versions", response_model=List[str])
def get_bible_versions_route() -> List[str]:
    """
    Route to get a list of all available Bible versions
    """
    try:
        return get_bible_versions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@bible_router.get("/search", response_model=BibleSearchResponse)
def search_bible_verses(search_text: str, bible_version: str = "kjv", max_results: int = 5, add_context: bool = False, context_size: int = 2) -> BibleSearchResponse:
    """
    Route to search the Bible for verses
    """
    try:
        response, notes = search_bible(search_text, bible_version, max_results, add_context, context_size)
        return BibleSearchResponse(verses=response, notes=notes)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))