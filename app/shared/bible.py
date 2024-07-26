import json, time, os, requests
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
import numpy as np

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union, Optional
from numba import njit


from shared.secrets import get_secret

"""
======================================================= CONFIG =======================================================
"""
# All the {version}.json files live in the bibles directory
bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./bibles")
all_bibles = os.listdir(bible_dir)

# GCP Service Account Key
gcp_key = get_secret("VERTEX_AI_SERVICE_ACCOUNT")


"""
======================================================= GOOGLE HELPERS =======================================================
"""
def get_gcp_bearer_token() -> str:
    """
    Get a Google Cloud Platform (GCP) Bearer Token for authentication

    Returns a GCP Bearer Token
    """
    credentials = service_account.Credentials.from_service_account_info(gcp_key)
    credentials = credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(google.auth.transport.requests.Request())
    token = credentials.token
    return token


def get_text_embeddings(
    texts: List[str],
    task: str = "RETRIEVAL_DOCUMENT",
    model_name: str = "text-embedding-004",
    dimensionality: Optional[int] = 256,
) -> List[List[float]]:
    """
    Get text embeddings from a Google Cloud Platform (GCP) model
    - texts: List of texts to get embeddings for
    - task: The task type of the model
    - model_name: The name of the embedding model to use
    - dimensionality: The dimensionality of the embeddings to return. Default is 256 (max is 756 for text-embedding-004)

    Returns a list of embeddings for each text
    """
    location = "us-central1"
    project_id = "bible-explorer-gcp-project"
    endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_name}:predict"
    headers = {
        "Authorization": f"Bearer {get_gcp_bearer_token()}",
        "Content-Type": "application/json",
    }
    data = {
        "instances": [{
            "task_type": task,
            "content": text,
        } for text in texts],
        "parameters": {"outputDimensionality": dimensionality},
    }
    response = requests.post(endpoint, headers=headers, json=data)
    response.raise_for_status()
    response = response.json()
    embeddings = [prediction["embeddings"]["values"] for prediction in response["predictions"]]
    return embeddings

"""
======================================================= SEARCH HELPERS =======================================================
"""
@njit(parallel=True)
def cosine_distance_numba(search_vector, verse_vectors) -> np.ndarray:
    """
    Calculate the cosine distance between a search vector and a list of verse vectors
    - search_vector: The search vector to compare to
    - verse_vectors: The list of verse vectors to compare to

    Returns a list of cosine distances
    """
    similarities = np.zeros(len(verse_vectors))
    for i in range(len(verse_vectors)):
        # Cosine Distance = sqrt(sum((a - b)^2)
        cur_vector = verse_vectors[i]
        distance = 0
        for j in range(len(search_vector)):
            distance += (search_vector[j] - cur_vector[j]) ** 2
        similarities[i] = np.sqrt(distance)
    return similarities


"""
======================================================= MODELS =======================================================
"""
class BibleVerse(BaseModel):
    book_name: str = Field(..., description="The name of the book of the Bible")
    book_number: int = Field(..., description="The book number of the Bible")
    chapter: int = Field(..., description="The chapter of the Bible")
    verse: int = Field(..., description="The verse of the Bible")
    text: str = Field(..., description="The text of the Bible verse")
    similarity: float = Field(..., description="The similarity score of the Bible verse")
    relative_similarity: float = Field(..., description="The relative similarity score of the Bible verse")
    context: Optional[List[str]] = Field(None, description="The context of the Bible verse")

class BibleSearchResponse(BaseModel):
    verses: List[BibleVerse] = Field(..., description="The list of Bible verses that match the search text")
    notes: List[Dict[str, Any]] = Field(..., description="The notes from the search process")


"""
======================================================= FUNCTIONS =======================================================
"""
# Idea: 
'''
A search function that is used for the search endpoint with paramaters:
- search_text: str
- bible_version: str
- max_results: int
- add_context: bool // If we return just the verse or the verse with context
- context_size: int // the number of surrounding verses to include in the context (default is 2)

As each bible version gets loaded, we want to cache it in memory so that we don't have to reload it each time
'''
bible_cache = {}
def search_bible(search_text: str, bible_version: str, max_results: int = 5, add_context: bool = True, context_size: int = 2) -> BibleSearchResponse:
    """
    Search the Bible for a specific text
    - search_text: The text to search for
    - bible_version: The Bible version to search in
    - max_results: The maximum number of results to return
    - add_context: Whether to include context around the search text
    - context_size: The number of verses to include before and after the search text

    Returns a list of verses that match the search text
    """
    notes = []
    start = time.time()
    def add_note(note):
        notes.append({
            "note": note,
            "elapsed_time": time.time() - start,
        })

    bible = None
    # Check if the Bible version is already loaded
    if bible_version in bible_cache:
        bible = bible_cache[bible_version]
    else:
        # Load the Bible version
        bible_path = os.path.join(bible_dir, f"{bible_version}.json")
        print(f"Loading Bible version: {bible_version}")
        with open(bible_path, "r") as file:
            bible = json.load(file)
        bible_cache[bible_version] = bible  # Cache the Bible version
        print(f"Loaded Bible version: {bible_version}")
    add_note(f"Loaded Bible version: {bible_version}")
    
    # Get the embeddings for the search text
    search_embedding = get_text_embeddings([search_text], "RETRIEVAL_QUERY")[0]
    add_note("Got search text embeddings")
    
    # Get the embeddings for all the verses in the Bible
    verses = bible["verses"]
    verse_embeddings = np.array([verse["embedding"] for verse in verses]) # array of verse embeddings [[...], [...], ...]
    similarities = cosine_distance_numba(np.array(search_embedding), verse_embeddings)
    add_note("Calculated cosine distances")

    # Map the similarities back to the verses
    for i, verse in enumerate(verses):
        verse["similarity"] = 1 - similarities[i]

    # Sort the verses by similarity
    verses = sorted(verses, key=lambda x: x["similarity"], reverse=True)
    add_note("Sorted verses by similarity")

    # Get the top matching verses
    top_verses = verses[:max_results]

    # Add relative matching score (i.e. first is 100% match, last is 0% match)
    max_similarity = top_verses[0]["similarity"]
    min_similarity = top_verses[-1]["similarity"]
    for verse in top_verses:
        verse["relative_similarity"] = (verse["similarity"] - min_similarity) / (max_similarity - min_similarity) if max_similarity - min_similarity != 0 else 0
    add_note("Added relative similarity scores")
    
    # Get the context for the top matching verses
    if add_context:
        for verse in top_verses:
            book_number = verse["book"]
            chapter = verse["chapter"]
            verse_number = verse["verse"]
            context = []
            # Get the surrounding verses (context_size before and after)
            for i in range(verse_number - context_size, verse_number + context_size + 1): 
                current_verse_number = i
                # Skip if the verse number is invalid - happens when the verse is at the beginning or end of a chapter
                if current_verse_number < 1:
                    continue
                # Find the verse in the Bible
                current_verse = next((v for v in bible["verses"] if v["book"] == book_number and v["chapter"] == chapter and v["verse"] == current_verse_number), None)
                if current_verse:
                    context.append(current_verse["text"])
            verse["context"] = context
        add_note("Added context to verses")

    # Format and return the response
    print([f"note: {note['note']}, elapsed_time: {note['elapsed_time']:0.2f}s" for note in notes])
    return [
        BibleVerse(
            book_name=verse["book_name"],
            book_number=verse["book"],
            chapter=verse["chapter"],
            verse=verse["verse"],
            text=verse["text"],
            similarity=verse["similarity"],
            relative_similarity=verse["relative_similarity"],
            context=verse.get("context"),
        ) for verse in top_verses
    ], notes



def get_bible_versions() -> List[str]:
    """
    Get a list of all available Bible versions

    Returns a list of Bible versions
    """
    return [bible.replace(".json", "") for bible in all_bibles]
