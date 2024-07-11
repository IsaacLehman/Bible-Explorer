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
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    distance = (np.dot(a, b) / norm) if norm != 0 else 0
    normalized_distance = (distance + 1) / 2 # Normalize to [0, 1]
    return normalized_distance

def get_bible():
    # Get the list of Bible versions
    versions_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "formatted_versions")
    versions = os.listdir(versions_abs_path)

    # ask the user which version they want to search
    print("Available Bible Versions:")
    for i, version in enumerate(versions):
        print(f"{i}: {version}")
    version_index = int(input("Enter the index of the Bible version you want to search: "))

    # Load the Bible version
    with open(f"{versions_abs_path}/{versions[version_index]}", "r") as f:
        print(f"- Loading Bible version: {versions[version_index]}")
        bible = json.load(f)

        # Convert the embeddings to numpy arrays
        for verse in bible["verses"]:
            verse["embedding"] = np.array(verse["embedding"])

        print(f"- Bible version: {bible['metadata']['name']} {bible['metadata']['year']} Loaded!")

    # Return the Bible
    return bible

def search_bible(bible, query, limit=10, include_context=False, debug=False):
    # Embed the query
    start = time.time()
    query_embedding = embed_text([query], "RETRIEVAL_QUERY")[0]
    if debug:
        end = time.time()
        print(f"Embedding Time: {end - start:.2f}s")

    # Calculate the similarity of the query to each verse
    verses = bible["verses"]
    start = time.time()
    for verse in verses:
        verse["similarity"] = cosine_similarity(query_embedding, verse["embedding"])
    if debug:
        end = time.time()
        print(f"Similarity Time: {end - start:.2f}s")

    # Sort the verses by similarity
    start = time.time()
    verses = sorted(verses, key=lambda x: x["similarity"], reverse=True)
    if debug:
        end = time.time()
        print(f"Sorting Time: {end - start:.2f}s")

    # Get the top N verses
    top_n_verses = verses[:limit]

    # Add relative matching score (i.e. first is 100% match, last is 0% match)
    max_similarity = top_n_verses[0]["similarity"]
    min_similarity = top_n_verses[-1]["similarity"]
    for verse in top_n_verses:
        verse["relative_similarity"] = (verse["similarity"] - min_similarity) / (max_similarity - min_similarity) if max_similarity - min_similarity != 0 else 0


    if include_context:
        # Include the context of the verses
        for verse in top_n_verses:
            verse["context"] = ""
            book_name = verse["book_name"]
            chapter = verse["chapter"]
            verse_number = verse["verse"]
            # Get the verses around the current verse. Make sure they are in the same book - add last 2 and next 2 verses
            for i in range(-2, 3):
                # Get the verse number
                current_verse_number = verse_number + i
                # Check if the verse number is valid
                if current_verse_number > 0:
                    # Get the verse
                    current_verse = next((v for v in verses if v["book_name"] == book_name and v["chapter"] == chapter and v["verse"] == current_verse_number), None)
                    # Add the verse text to the context
                    if current_verse:
                        verse["context"] += f"\t{current_verse['book_name']} {current_verse['chapter']}:{current_verse['verse']} - {current_verse['text']}\n"
    
    # Return the top N verses
    return top_n_verses

if __name__ == "__main__":
    #format_bible_versions()

    # Load the Bible
    print('Welcome to the Bible Explorer')
    print('=' * 100)
    bible = get_bible()
    print('=' * 100)
    print('Search the Bible')
    include_context = input('Do you want to include context for the verses? (y/n): ').lower() == 'y'
    debug_mode = input('Do you want to enable debug mode? (y/n): ').lower() == 'y'
    search = None
    while search != 'q' and search != 'quit':
        print('=' * 100)
        search = input('Enter a search query (type "q" or "quit" to exit): ')
        if search == 'q' or search == 'quit':
            break
        print('---')
        verses = search_bible(bible, search, 10, include_context=include_context, debug=debug_mode)
        print('Top 10 verses:')
        print('=' * 100)
        for i, verse in enumerate(verses):
            print(f"{i + 1}. {verse['book_name']} {verse['chapter']}:{verse['verse']} - Similarity: {verse['similarity']:.2f} ({100*verse['relative_similarity']:.2f}% Relative Match)")
            print(verse['text'])
            if include_context:
                print('-' * 3)
                print('Context:') 
                print(verse['context'])
            if i < len(verses) - 1:
                print('-' * 30)

    print('Goodbye!')
