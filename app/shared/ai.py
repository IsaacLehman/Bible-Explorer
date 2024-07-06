from pydantic import BaseModel, Field
from typing import List, Dict, Any

from openai import OpenAI
from shared.secrets import get_secret

"""
======================================================= MODELS =======================================================
"""
class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender. Can be 'system', 'user', or 'assistant'.")
    content: str = Field(..., description="The content of the message.")

    class Config:
        schema_extra = {
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


"""
======================================================= FUNCTIONS =======================================================
"""
# Global OpenAI client
client = OpenAI(api_key=get_secret('OPENAI_API_KEY'))
def ai_chat(messages: List[Message], model: str = "gpt-3.5-turbo", config: Dict[str, Any] = {
    "stream": False,
    "temperature": 0.65,
}) -> Dict[str, Any]:
    """
    This function sends a message to the OpenAI API and returns the response.
    - messages: The chat history to send to the API. | [{role: str, content: str}] where role is either "system", "user", or "assistant"
    - model: The model to use for the chat. | str
    - config: The configuration for the chat. | dict
    """
    try:
        if config.get('stream', False):
            # Implement streaming logic here
            return {"error": "Streaming not implemented yet."}
        
        print(messages)
        print([message.dict() for message in messages])
        
        response = client.chat.completions.create(
            model=model,
            messages=[message.dict() for message in messages],
            **config
        )
        output = response.choices[0].message.content
        
        return {
            "output": output,
            "chat_history": messages + [Message(role="assistant", content=output)],
            "usage": response.usage
        }
    except Exception as e:
        return {"error": str(e)}