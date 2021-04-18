import requests, json
from flask_restful import Resource, reqparse
from flask import redirect, session
from urllib.parse import parse_qs
from app import app, oauth, OAuth1
from app.models import User


def twitter_callback_parser():
    parser = reqparse.RequestParser()
    parser.add_argument("oauth_token")
    parser.add_argument("oauth_verifier")
    return parser

class TwitterCallback(Resource):
    def get(self):
        parser = twitter_callback_parser()
        args = parser.parse_args()
        req = requests.post('https://api.twitter.com/oauth/access_token?oauth_token=' + args['oauth_token'] + '&oauth_verifier=' + args['oauth_verifier'])
        data = parse_qs(req.text)
        oauth_token = data["oauth_token"][0]
        oauth_token_secret = data["oauth_token_secret"][0]
        auth = OAuth1(app.config["TWITTER_API_KEY"], app.config["TWITTER_API_SECRET"], oauth_token, oauth_token_secret) 
        req = requests.get("https://api.twitter.com/1.1/account/verify_credentials.json?include_email=true", auth=auth).json()
        username = req["screen_name"]
        url = "https://twitter.com/" + req["screen_name"]
        email = req["email"]
        user = User.objects(username=session.get("username"))
        user.update(
            set__socials__twitter__connected=True,
            set__socials__twitter__username=username,
            set__socials__twitter__profile_url=url,
            set__socials__twitter__email=email,
            set__socials__twitter__oauth_token=oauth_token,
            set__socials__twitter__oauth_token_secret=oauth_token_secret
        )
        return redirect(app.config["BASE_URL"] + "/")

class TwitterAuthorization(Resource):
    def get(self):
        uri, headers, body = oauth.sign('https://twitter.com/oauth/request_token')

        req = requests.get(uri, headers=headers, data=body)
        data = parse_qs(req.text)
        oauth_token = data["oauth_token"][0]
        return redirect('https://api.twitter.com/oauth/authenticate?oauth_token=' + oauth_token)