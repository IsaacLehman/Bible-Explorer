"""
    Database models for the application
"""
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json

class AI_Log(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    source: str
    messages: str
    model: str
    config: str
    response: str
    runtime_seconds: float
    prompt_tokens: int
    completion_tokens: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})


class Bible_Search_Log(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    search_text: str
    bible_version: str
    max_results: int
    add_context: bool
    context_size: int
    response: str
    runtime_seconds: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})
