# References
# https://www.youtube.com/watch?v=Pm938UxLEwQ [1]
# https://stackoverflow.com/questions/70617258/session-object-in-fastapi-similar-to-flask [2]

import os
import httpx
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.urandom(32)) # [2]

templates = Jinja2Templates(directory='templates')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    if 'access_token' not in request.session.keys():
        user = False
    else:
        user = True
    return templates.TemplateResponse(
        request=request, name='index.html', context={'client_id': CLIENT_ID, 'user': user}
    )

@app.get('/callback')
async def callback(code: str, request: Request):
    # [1] params and headers
    params = {
        'client_id':CLIENT_ID,
        'client_secret':CLIENT_SECRET,
        'code': code
    }
    headers = {'Accept': 'application/json'}

    # [1] Get Access token
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://github.com/login/oauth/access_token', params=params, headers=headers)
        response_json = response.json()
    access_token = response_json['access_token']
    request.session['access_token'] = access_token
    return RedirectResponse('/')

@app.get('/github/starred')
async def starred_data(request: Request):
    if 'access_token' not in request.session.keys():
        return RedirectResponse('/')

    # [1] headers
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {request.session["access_token"]}'}

    # [1] Get all starred repositories
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.github.com/user/starred', headers=headers)

    # If the access code has expired, delete saved data and redirect to home page
    if response.status_code != 200:
        del request.session['access_token']
        return RedirectResponse('/')

    response_json = response.json()
    starred_data = convert_starred(response_json)
    return starred_data

def convert_starred(raw_json: json):
    starred_data = {'number of starred repositories': 0, 'starred repositories': []}
    for starred in raw_json:
        # Skip if private since we only want the public repositories. This is useless since we only have access to public repositories
        if starred['private']:
            continue

        starred_data['number of starred repositories'] += 1
        starred_dict = {
            'name': starred['name'],
            'description': starred['description'],
            'url': starred['url'],
            'topics': starred['topics']
        }
        if starred['license'] is not None:
            starred_dict['license'] = starred['license']
        starred_data['starred repositories'].append(starred_dict)    

    return starred_data
