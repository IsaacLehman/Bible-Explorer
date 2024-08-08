# Bible Explorer Repo

## Virtual Environment
1. Setup: `python -m venv bible_explorer_env`
2. Activate: `.\bible_explorer_env\Scripts\activate`
3. Deactivate: `deactivate`

## Install Dependencies
```bash
pip install fastapi numpy pandas openai sqlmodel vertexai numba
```

## Add your `app/shared/env.json` file at 
```json
{
    "OPENAI_API_KEY": "your_openai_api_key",
    "GROQ_API_KEY": "your_groq_api_key",
    "VERTEX_AI_SERVICE_ACCOUNT": "your_vertex_ai_service_account", // Ensure this service account has access to the Vertex AI embeddings
}
```

## Add in the bible versions w/ embeddings
1. Download the bible versions from [Google Drive](https://drive.google.com/drive/folders/1Wyzaj6QTEpYmaqpJV-Livib13G-zAYkH?usp=sharing)
2. Add the `bibles` folder to the `app/shared` directory (i.e. `app/shared/bibles`)
3. Move all of the `.json` files you downloaded to the `app/shared/bibles` directory

## Run locally
```bash
fastapi dev .\app\main.py
```

- [Local Docs: http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Interesting articles:
- https://fastapi.tiangolo.com/tutorial/bigger-applications/
- [Bible versions in the public domain](https://support.biblegateway.com/hc/en-us/articles/360001403507-What-Bibles-on-Bible-Gateway-are-in-the-public-domain)
- [Download Bible Versions](https://www.biblesupersearch.com/bible-downloads/)

## Other Tips:
- Install the `lit-html` extension in VS Code to get syntax highlighting for `html` template literals.
