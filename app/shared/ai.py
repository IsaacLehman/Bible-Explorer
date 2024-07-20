from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union
import json, time

from openai import OpenAI
from shared.secrets import get_secret

from db.models import AI_Log
from db.controller import get_db

"""
======================================================= MODELS =======================================================
"""
class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender. Can be 'system', 'user', or 'assistant'.")
    content: str = Field(..., description="The content of the message.")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                },
                {
                    "role": "assistant",
                    "content": "I am doing well, thank you for asking."
                },
                {
                    "role": "user",
                    "content": "Can you tell me a joke?"
                }
            ]
        }


class AI_Response(BaseModel):
    output: Union[str, Dict[str, Any], List[Any]] = Field(..., description="The output of the AI response. Can be a string or a dictionary if the output is JSON.")
    chat_history: List[Message] = Field(..., description="The full chat history.")
    runtime_seconds: float = Field(..., description="The runtime of the API call in seconds.")
    prompt_tokens: int = Field(..., description="The number of tokens in the prompt.")
    completion_tokens: int = Field(..., description="The number of tokens in the completion.")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "output": "I am doing well, thank you for asking.",
                    "chat_history": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant."
                        },
                        {
                            "role": "user",
                            "content": "Hello, how are you?"
                        },
                        {
                            "role": "assistant",
                            "content": "I am doing well, thank you for asking."
                        }
                    ],
                    "runtime_seconds": 0.5,
                    "prompt_tokens": 100,
                    "completion_tokens": 200
                }
            ]
        }

"""
======================================================= FUNCTIONS =======================================================
"""
# Global OpenAI client
client = OpenAI(api_key=get_secret('OPENAI_API_KEY'))
def ai_chat(source: str, messages: List[Message], model: str = "gpt-4o-mini", config: Dict[str, Any] = {
    "stream": False,
    "temperature": 0.65,
}) -> Union[AI_Response, Dict[str, str]]:
    """
    This function sends a message to the OpenAI API and returns the response.
    - source: The source of the chat. | str
    - messages: The chat history to send to the API. | [{role: str, content: str}] where role is either "system", "user", or "assistant"
    - model: The model to use for the chat. | str
    - config: The configuration for the chat. | dict
    """
    try:
        if config.get('stream', False):
            # Implement streaming logic here
            return {"error": "Streaming not implemented yet."}
        
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[message.dict() for message in messages],
            **config
        )
        runtime_seconds = time.time() - start  # Calculate the runtime of the API call in seconds
        output = response.choices[0].message.content
        full_chat_history = messages + [Message(role="assistant", content=output)]

        # Save the chat log to the database
        with get_db() as db:
            log = AI_Log(
                source=source,
                messages=json.dumps([message.dict() for message in messages]),
                model=model,
                config=json.dumps(config),
                response=output,
                runtime_seconds=runtime_seconds,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens
            )
            db.add(log)
            db.commit()

        return AI_Response(
            output=output,
            chat_history=[Message(**message.dict()) for message in full_chat_history],
            runtime_seconds=runtime_seconds,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens
        )
    except Exception as e:
        return {"error": str(e)}