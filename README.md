# starred-repos-be

Retrieves a user's starred repositories from GitHub and display them neatly.

## Instructions

1. Create a new [OAuth](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) application in GitHub developer settings.
2. Set homepage URL to: http://localhost:8000
3. Set authorization callback URL to: http://localhost:8000/callback
4. Generate a new client secrets and copy it
5. Rename .envexample to .env and insert client id and client secrets values from the created OAuth application

### Normal installation:
1. (optional) python -m venv venv
2. (optional) source venv/bin/activate or source venv/Scripts/activate
3. pip install -r requirements.txt
4. python -m uvicorn main:app

### Or with docker:
1. docker build -t starred-be .
2. docker run -d --name starredcontainer -p 8000:8000 starred-be

### After installation:
http://localhost:8000


## References
https://www.youtube.com/watch?v=Pm938UxLEwQ
- For async with httpx.AsyncClient(), headers and params

https://stackoverflow.com/questions/70617258/session-object-in-fastapi-similar-to-flask
- For FastAPI sessions
