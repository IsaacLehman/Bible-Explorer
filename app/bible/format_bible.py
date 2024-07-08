"""
One off script to format the Bible versions in the ./versions folder

They start off in the format of:
{
    "metadata": {
        "name": {{name}},
        "shortname": {{shortname}},
        "year": {{year}},
        ...
    },
    "verses": [
        {
            "book_name": {{book_name}},
            "book_number": {{book_number}},
            "chapter": {{chapter}},
            "verse": {{verse}},
            "text": {{text}}
        },
        ...
    ]
}

We want to add a vector embedding for each verse under the key "embedding".
Output the updated JSON fiels in a new folder called ./formatted_versions
"""
import os, json, requests, time
import numpy as np
from typing import List, Optional
import google.auth
import google.auth.transport.requests


service_account = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gcp-service.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account

def get_gcp_bearer_token():
    credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)
    return credentials.token

def embed_text(
    texts: List[str],
    task: str = "RETRIEVAL_DOCUMENT",
    model_name: str = "text-embedding-004",
    dimensionality: Optional[int] = 256,
) -> List[List[float]]:
    """Embeds texts with a pre-trained, foundational model."""
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

def format_bible_versions(batch_size=250):
    """
    Format the Bible versions in the ./versions folder
    For each verse, add a vector embedding under the key "embedding"
    Output the updated JSON files in a new folder called ./formatted_versions
    """
    formatted_versions_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "formatted_versions")
    versions_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "versions")

    # Create the formatted_versions folder if it doesn't exist
    if not os.path.exists(formatted_versions_abs_path):
        os.makedirs(formatted_versions_abs_path)

    # Get the list of Bible versions
    versions = os.listdir(versions_abs_path)
    
    for version in versions:
        # Load the Bible version (Try the formatted one first)
        with open(f"{formatted_versions_abs_path}/{version}", "r") as f:
            print(f"Loading Pre-Formated Bible version: {version}")
            bible = json.load(f)
            print(f"Bible version: {bible['metadata']['name']} {bible['metadata']['year']} Loaded!")

        if not bible:
            print(f"Loading Bible version: {version}")
            with open(f"{versions_abs_path}/{version}", "r") as f:
                print(f"Loading Bible version: {version}")
                bible = json.load(f)
                print(f"Bible version: {bible['metadata']['name']} {bible['metadata']['year']} Loaded!")
        
        verses = bible["verses"]
        for i in range(0, len(verses), batch_size):
            batch = verses[i:i+batch_size]
            # Skip verses that already have embeddings (i.e. all in batch)
            if all("embedding" in verse for verse in batch):
                continue

            print(f"Processing batch {i // batch_size} of {len(verses) // batch_size}")
            texts = [f"{verse['book_name']} {verse['chapter']}:{verse['verse']} {verse['text']}" for verse in batch]
            embeddings = embed_text(texts)
            
            for j, verse in enumerate(batch):
                verse["embedding"] = embeddings[j]
            
            # Save the updated Bible version periodically
            if (i > 0 and i // batch_size) % 30 == 0:
                with open(f"{formatted_versions_abs_path}/{version}", "w") as f:
                    print(f"Saving Bible version: {version} at batch {i // batch_size}")
                    json.dump(bible, f, indent=4)
                    print(f"Saved Bible version: {version} at batch {i // batch_size}")

        # Save the updated Bible version
        with open(f"{formatted_versions_abs_path}/{version}", "w") as f:
            print(f"Saving Bible version: {version}")
            json.dump(bible, f, indent=4)

        print(f"Saved Bible version: {version}")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)) if np.linalg.norm(a) * np.linalg.norm(b) != 0 else 0

def search_bible(query, limit=10):
    query_embedding = embed_text([query], "RETRIEVAL_QUERY")[0]
    versions_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "formatted_versions")
    versions = os.listdir(versions_abs_path)
    # ask the user which version they want to search
    print("Available Bible Versions:")
    for i, version in enumerate(versions):
        print(f"{i}: {version}")
    version_index = int(input("Enter the index of the Bible version you want to search: "))
    with open(f"{versions_abs_path}/{versions[version_index]}", "r") as f:
        print(f"- Loading Bible version: {versions[version_index]}")
        bible = json.load(f)
        print(f"- Bible version: {bible['metadata']['name']} {bible['metadata']['year']} Loaded!")
    verses = bible["verses"]
    # Calculate the similarity of the query to each verse
    for verse in verses:
        verse["similarity"] = cosine_similarity(query_embedding, verse["embedding"])
    # Sort the verses by similarity
    verses = sorted(verses, key=lambda x: x["similarity"], reverse=True)
    # Return the top 10 verses
    return verses[:limit]

if __name__ == "__main__":
    #format_bible_versions()
    print('Welcome to the Bible Explorer')
    print('=' * 100)
    print('Search the Bible')
    search = input('Enter a search query: ')
    verses = search_bible(search)
    print('Top 10 verses:')
    print('=' * 100)
    for i, verse in enumerate(verses):
        print(f"{i + 1}. {verse['book_name']} {verse['chapter']}:{verse['verse']} - Similarity: {verse['similarity']:.2f}")
        print(verse['text'])
        print('-' * 30)
