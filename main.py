import os
import httpx
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory='templates')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name='index.html', context={'client_id': CLIENT_ID}
    )

@app.get('/callback')
async def callback(code: str):
    params = {
        'client_id':CLIENT_ID,
        'client_secret':CLIENT_SECRET,
        'code': code
    }

    headers = {'Accept': 'application/json'}

    # Get Access token
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://github.com/login/oauth/access_token', params=params, headers=headers)
        response_json = response.json()
    access_token = response_json['access_token']

    # Get data for username
    async with httpx.AsyncClient() as client:
        headers['Authorization'] = f'Bearer {access_token}'
        response = await client.get('https://api.github.com/user', headers=headers)
    response_json = response.json()
    username = response_json['login']

    # Get all starred repositories
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://api.github.com/users/{username}/starred', headers=headers)

    response_json = response.json()
    starred_data = get_starred_data(response_json)
    return starred_data


def get_starred_data(raw_json: json):
    starred_data = {'number of starred repositories': 0, 'starred repositories': []}
    for starred in raw_json:
        # Skip if private since we only want the public repositories
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
