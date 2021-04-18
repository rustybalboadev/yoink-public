import requests
from flask_restful import Resource, reqparse
from flask import redirect, session
from app import app
from app.models import User
from urllib.parse import quote_plus

def github_callback_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("code")
    return parser

class GithubCallback(Resource):
    def get(self):
        parser = github_callback_parser()
        args = parser.parse_args()
        code = args["code"]
        url = "https://github.com/login/oauth/access_token?client_id=" + app.config["GITHUB_CLIENT_ID"] + "&client_secret=" + app.config["GITHUB_CLIENT_SECRET"] + "&code=" + code
        headers = {"Accept" : "application/json"}
        req = requests.post(url, headers=headers).json()
        access_token = req["access_token"]
        
        headers = {"Authorization" : "token " + access_token}
        req = requests.get("https://api.github.com/user", headers=headers).json()
        username = req["login"]
        profile_url = req["html_url"]
        email = req["email"]

        user = User.objects(username=session.get("username")).first()
        user.update(
            set__socials__github__connected=True,
            set__socials__github__username=username,
            set__socials__github__profile_url=profile_url,
            set__socials__github__email=email,
            set__socials__github__access_token=access_token
        )
        return redirect(app.config["BASE_URL"] + "/")

class GithubAuthorization(Resource):
    def get(self):
        url = "https://github.com/login/oauth/authorize?client_id=" + app.config["GITHUB_CLIENT_ID"] + "&redirect_uri=" + quote_plus(app.config["BASE_URL"] + "/github_callback") + "&scopes=user user:email"
        print(url)
        return redirect(url)