# Bible Explorer Repo

## Virtual Environment
1. Setup: `python -m venv bible_explorer_env`
2. Activate: `.\bible_explorer_env\Scripts\activate`
3. Deactivate: `deactivate`

## Install Dependencies
```bash
pip install fastapi numpy pandas openai sqlmodel
```

## Add your `app/shared/env.json` file at 
```json
{
    "OPENAI_API_KEY": "your_openai_api_key"
}
```

## Run locally
```bash
fastapi dev .\app\main.py
```

Interesting articles:
- https://fastapi.tiangolo.com/tutorial/bigger-applications/

