#! /usr/bin/env python3

from urllib import request

import os
import subprocess

HEROKU_AUTH_TOKEN = os.environ.get('HEROKU_AUTH')
WEB_DOCKER_IMAGE_ID = subprocess.run([
    'docker',
    'inspect',
    'registry.heroku.com/asana-fastapi/web:latest',
    '--format={{.Id}}'], capture_output=True, encoding='utf-8').stdout

data = {"updates": [{"type": "web", "docker_image": f"{WEB_DOCKER_IMAGE_ID}"}]}
headers = {
    "Content-Type": "application/json",
    "Accept": "application/vnd.heroku+json; version=3.docker-releases",
    "Authorization": f"Bearer {HEROKU_AUTH_TOKEN}"}

req = request.Request(
    url='https://api.heroku.com/apps/asana-fastapi/formation',
    data=data,
    method='PATCH',
    headers=headers)

print(req)