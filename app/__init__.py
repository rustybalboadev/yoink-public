from flask import Flask, request, render_template, session, redirect, send_file, Blueprint, send_from_directory, make_response
from flask_restful import Api, reqparse
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO
from flask_recaptcha import ReCaptcha
from requests_oauthlib.oauth1_auth import Client, OAuth1
from app.utils import Encryption
from app.config import create_app
from .log import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import json, random, string, requests, qrcode, io, os

mongo = MongoEngine()

app = create_app()
app.register_blueprint(logger)
recap = ReCaptcha(app=app)
recap.secret_key = app.config["RECAPTCHA_SITE_SECRET"]
recap.site_key = app.config["RECAPTCHA_SITE_KEY"]

api = Api(app)

oauth = Client(app.config["TWITTER_API_KEY"], client_secret=app.config["TWITTER_API_SECRET"])

mongo.init_app(app)

socket = SocketIO(app, cors_allowed_origins="*")
e = Encryption(app.config["ENCRYPTION_KEY"])

from app.models import Stats
views = Stats.objects().first().total_views

def generate_codes():
    letters = string.ascii_letters
    trackid = ''.join(random.choice(letters) for i in range(6))
    urlcode = ''.join(random.choice(letters) for i in range(6))
    return trackid, urlcode


@app.errorhandler(500)
def error500(e):
    return render_template("500.html"), 500

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if recap.verify():
            from app.models import User, Social
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]

            user = User.objects(email=email)
            if len(user) > 0:
                #Email Exists
                return redirect(app.config["BASE_URL"] + "/register?error=Email+With+Account+Exists")

            user = User.objects(username=username)
            if len(user) > 0:
                #User exists
                return redirect(app.config["BASE_URL"] + "/register?error=Username+Already+Exists")

            personalData = json.dumps({"password": password})
            enc, nonce, mac = e.encrypt(personalData)
            avatar_bytes = open(os.path.join(app.root_path, "static/avatar.png"), "rb")
            newUserData = {
                "username": username,
                "bio": "",
                "avatar": avatar_bytes,
                "email": email,
                "data": enc,
                "nonce": nonce,
                "mac": mac,
                "password_reset_id": None,
                "socials": {
                    "github": {"connected": False},
                    "twitter": {"connected": False},
                    "discord": {"connected": False},
                    "spotify": {"connected": False}
                },
                "is_admin": False
            }
            user = User(**newUserData)
            user.save()
            session["logged_in"] = True
            session["username"] = username
            return redirect(app.config["BASE_URL"] + '/dashboard')
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if recap.verify():
            from app.models import User
            username = request.form["username"]
            password = request.form["password"]
            user = User.objects(username=username)
            if len(user) == 0:
                #no user with that username, show error.
                return redirect(app.config["BASE_URL"] + "/login?error=User+Doesn't+Exist")
            data = user[0].data
            nonce = user[0].nonce
            mac = user[0].mac
            data = e.decrypt(data, nonce, mac)
            if password == data["password"]:
                session["logged_in"] = True
                session["username"] = username
                return redirect(app.config["BASE_URL"] + '/dashboard')
            else:
                #Incorrect Password, show error.
                return redirect(app.config["BASE_URL"] + "/login?error=Incorrect+Password")
    return render_template("login.html")

@app.route('/')
def root():
    if session.get("logged_in"):
        return redirect(app.config["BASE_URL"] + '/dashboard')
    return render_template("welcome.html")

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if session.get("logged_in"):
        global views
        from app.models import Stats, User, Links
        views += 1
        if request.method == "POST":
            redirectURL = request.form["inputURL"]
            if redirectURL == "":
                #Link is blank
                return redirect(app.config["BASE_URL"] + "/dashboard?error=Link+Cannot+Be+Blank")
            tracking_id, url_id = generate_codes()
            user = User.objects(username=session.get("username")).first()
            new_link = {"creator": user.id, "track_id": tracking_id, "url_code": url_id, "redirect_url": redirectURL, "full_url": "https://yoink.rip/" + url_id, "grab_info": []}
            link = Links(**new_link)
            link.save()
            return redirect(app.config["BASE_URL"] + "/track/"+tracking_id)
        stats = Stats.objects().first()

        return render_template("index.html", stats=stats)
    return redirect(app.config["BASE_URL"] + '/')

@app.route("/search", methods=["GET", "POST"])
def search():
    if session.get("logged_in"):
        from app.models import User
        parser = reqparse.RequestParser()
        parser.add_argument("q")
        parser.add_argument("page")
        args = parser.parse_args()
        query = args["q"]
        page = 1 if args["page"] == None else int(args["page"])
        if page < 1:
            return redirect(app.config["BASE_URL"] + "/search")
        requestedUser = User.objects(username=session.get("username")).first()

        if args["q"] != None:
            users = User.objects.filter(username__contains=query).all()
            users = users.paginate(page=page, per_page=10)
            return render_template("search.html", users=users.items, requestUser=requestedUser)
        users = User.objects.paginate(page=page, per_page=10)

        return render_template("search.html", users=users.items, requestUser=requestedUser)
    return redirect(app.config["BASE_URL"] + "/")

@app.route("/iplookup", methods=["GET", "POST"])
def iplookup():
    if session.get("logged_in"):
        if request.method == "POST":
            ipaddress = request.form["inputIP"]
            data = requests.get("http://ip-api.com/json/" + ipaddress).json()
            location = {"lat": data["lat"], "lon": data["lon"]}
            return render_template("iplookup.html", data=data, location=location)
        return render_template("iplookup.html")
    return redirect(app.config["BASE_URL"] + "/")

@app.route("/tracking")
def tracking():
    from app.models import Links, User
    if session.get("logged_in"):
        user = User.objects(username=session.get("username")).first()
        links = Links.objects(creator=user.id).all()
        return render_template("tracking.html", links=links)
    return redirect(app.config["BASE_URL"] + "/")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if session.get("logged_in"):
        from app.models import User
        if request.method == "POST":
            uploaded_file = request.files["file"]
            user = User.objects(username=session.get("username")).first()
            if user.avatar == None:
                user.avatar.put(uploaded_file)
            else:
                user.avatar.delete()
                user.avatar.put(uploaded_file)
            user.save()
        user = User.objects(username=session.get("username")).first()
        social = user.socials
        return render_template("settings.html", user=user, social=social, json=json)
    return redirect(app.config["BASE_URL"] + "/")

@app.route('/track/<id>', methods=["GET", "POST"])
def track(id):
    if session.get("logged_in"):
        from app.models import Links
        link = Links.objects(track_id=id).first()
        if request.method == "POST":
            url = link.full_url
            file_ = qrcode.make(url)
            buf = io.BytesIO()
            file_.save(buf)
            buf.seek(0)
            return send_file(buf, mimetype="image/jpeg", as_attachment=True, attachment_filename=id + ".jpeg")
        return render_template("track.html", track=link, json=json)
    return redirect(app.config["BASE_URL"] + "/")

@app.route("/user/<userid>/photo")
def userPhoto(userid):
    user = User.objects(id=userid).first()
    req = make_response(send_file(user.avatar, mimetype="image"))
    req.headers.set("Cache-Control", "max-age=0")
    return req

@app.route("/user/<userid>")
def userProfile(userid):
    user = User.objects(id=userid).first()
    social = user.socials
    return render_template("profile.html", user=user, social=social, json=json)

@app.route("/password_reset", methods=["GET", "POST"])
def passwordReset():
    if request.values.has_key("code"):
        uuidStr = request.values["code"]
        if request.method == "POST":
            new_pass = request.form["pass_value"]   
            user = User.objects(password_reset_id=uuidStr).first()
            new_data = json.dumps({"password": new_pass})
            enc, nonce, mac = e.encrypt(new_data)
            user.update(
                set__data=enc,
                set__nonce=nonce,
                set__mac=mac,
                set__password_reset_id=None
            )
            if session.get("logged_in"):
                return redirect(app.config["BASE_URL"] + "/logout")
            return redirect(app.config["BASE_URL"] + "/login")
        return render_template("reset.html", new_pass=True)
    return render_template("reset.html")

@app.route("/admin/<userid>")
def admin(userid):
    from app.models import User, Links
    if session.get("logged_in"):
        requestUser = User.objects(username=session.get("username")).first()
        if requestUser.is_admin:
            user = User.objects(id=userid).first()
            if user == None:
                return redirect(app.config["BASE_URL"] + "/")
            userID = user.id
            links = Links.objects(creator=userID).all()

            return render_template("admin.html", user=user, links=links)

from app.resources.functionality import Logout, DeleteLink, DeleteUser, ProfileInfo, MakeAdmin
from app.resources.spotify_login import SpotifyCallback, SpotifyAuthorization
from app.resources.discord_login import DiscordCallback, DiscordAuthorization
from app.resources.twitter_login import TwitterCallback, TwitterAuthorization
from app.resources.github_login import GithubCallback, GithubAuthorization

api.add_resource(Logout, "/logout")
api.add_resource(DeleteLink, "/api/delete_link")
api.add_resource(DeleteUser, "/api/delete_user")
api.add_resource(ProfileInfo, "/api/change_settings")
api.add_resource(MakeAdmin, "/api/give_admin")

api.add_resource(SpotifyCallback, "/spotify_callback")
api.add_resource(SpotifyAuthorization, "/spotifyauth")

api.add_resource(DiscordCallback, "/discord_callback")
api.add_resource(DiscordAuthorization, "/discordauth")

api.add_resource(TwitterCallback, "/twitter_callback")
api.add_resource(TwitterAuthorization, "/twitterauth")

api.add_resource(GithubCallback, "/github_callback")
api.add_resource(GithubAuthorization, "/githubauth")

from app.sockets.socket_functions import *
from app.scheduler.update_stats import updateStats

sched = BackgroundScheduler()

sched.add_job(updateStats, IntervalTrigger(minutes=30))
sched.start()