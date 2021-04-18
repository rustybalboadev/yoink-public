import requests
from flask_restful import Resource, reqparse
from flask import redirect, session
from base64 import b64encode
from app import app
from urllib.parse import quote_plus
from app.models import User


def spotify_callback_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('code')
    return parser

class SpotifyCallback(Resource):
    def get(self):
        parser = spotify_callback_parser()
        args = parser.parse_args()
        code = args["code"]
        auth_code_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "scope": "user-library-read user-top-read playlist-read-private playlist-read-collaborative user-read-playback-state user-read-currently-playing user-read-email user-read-private",
            "redirect_uri": app.config["BASE_URL"] + "/spotify_callback"
        }
        token_bytes = str(app.config["SPOTIFY_CLIENT_ID"] + ":" + app.config["SPOTIFY_CLIENT_SECRET"]).encode("ascii")
        b64_token = b64encode(token_bytes).decode("ascii")
        headers = {"Authorization": "Basic " + b64_token}
        req = requests.post(auth_code_url, data=data, headers=headers).json()
        access_token = req["access_token"]
        refresh_token = req["refresh_token"]
        
        mem_req = requests.get('https://api.spotify.com/v1/me', headers={'Accept': 'application/json','Content-Type': 'application/json','Authorization': 'Bearer ' + access_token}).json()
        username = mem_req["id"]
        email = mem_req["email"]
        profile_url = mem_req["external_urls"]["spotify"]

        user = User.objects(username=session.get("username")).first()
        user.update(
            set__socials__spotify__connected=True,
            set__socials__spotify__username=username,
            set__socials__spotify__email=email,
            set__socials__spotify__profile_url=profile_url,
            set__socials__spotify__access_token=access_token,
            set__socials__spotify__refresh_token=refresh_token
        )
        return redirect(app.config["BASE_URL"] + "/")

class SpotifyAuthorization(Resource):
    def get(self):
        url = "https://accounts.spotify.com/authorize"
        formed_url = url + "?client_id=" + app.config['SPOTIFY_CLIENT_ID'] + "&response_type=code&redirect_uri=" + app.config['BASE_URL'] + "/spotify_callback" + "&show_dialog=true&scope=" + quote_plus("user-read-email user-read-private")
        return redirect(formed_url)