from flask_restful import Resource, reqparse
from flask import session, redirect
from app import app
from app.models import User
from urllib.parse import quote_plus
import requests

def discord_callback_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("code")
    return parser

class DiscordCallback(Resource):
    def get(self):
        parser = discord_callback_parser()
        args = parser.parse_args()
        code = args["code"]
        data = {
            "client_id": app.config["DISCORD_CLIENT_ID"],
            "client_secret": app.config["DISCORD_CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": app.config["BASE_URL"] + "/discord_callback",
            "scope": "identify email"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        req = requests.post("https://discord.com/api/v8/oauth2/token", data=data, headers=headers).json()
        access_token = req["access_token"]
        refresh_token = req["refresh_token"]
        headers = {'Authorization': 'Bearer ' + access_token}
        
        mem_req = requests.get("https://discord.com/api/v8/users/@me", headers=headers).json()
        print(mem_req)
        username = mem_req["username"]
        discriminator = mem_req["discriminator"]
        email = mem_req["email"]

        user = User.objects(username=session.get("username")).first()
        user.update(
            set__socials__discord__connected=True,
            set__socials__discord__username=username,
            set__socials__discord__discriminator=discriminator,
            set__socials__discord__email=email,
            set__socials__discord__access_token=access_token,
            set__socials__discord__refresh_token=refresh_token
        )
        return redirect(app.config["BASE_URL"] + "/")

class DiscordAuthorization(Resource):
    def get(self):
        url = "https://discord.com/oauth2/authorize"
        formed_url = url + "?client_id=" + app.config["DISCORD_CLIENT_ID"] + "&redirect_uri=" + quote_plus(app.config["BASE_URL"] + "/discord_callback") + "&response_type=code&scope=identify%20email"

        return redirect(formed_url)