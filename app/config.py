from flask import Flask
from omegaconf import OmegaConf

def create_app():
    conf = OmegaConf.load("config.yaml")
    
    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {'db': 'yoink', 'host': conf["yoink"]["mongo-uri"], 'connect': False}
    app.config['SECRET_KEY'] = conf["yoink"]["secret-key"]
    app.config["BASE_URL"] = conf["yoink"]["base-url"]
    app.config["ENCRYPTION_KEY"] = conf["yoink"]["encryption-key"]

    app.config["EMAIL_ADDRESS"] = conf["yoink"]["email"]["address"]
    app.config["EMAIL_PASSWORD"] = conf["yoink"]["email"]["app-password"]

    app.config['RECAPTCHA_SITE_KEY'] = conf["yoink"]["recaptcha"]["key"]
    app.config['RECAPTCHA_SITE_SECRET'] = conf["yoink"]["recaptcha"]["secret"]
    app.config['RECAPTCHA_ENABLED'] = True
    app.config['RECAPTCHA_THEME'] = 'dark'
    
    app.config["SPOTIFY_CLIENT_ID"] = conf["yoink"]["spotify"]["client_id"]
    app.config["SPOTIFY_CLIENT_SECRET"] = conf["yoink"]["spotify"]["secret"]

    app.config["DISCORD_CLIENT_ID"] = conf["yoink"]["discord"]["client_id"]
    app.config["DISCORD_CLIENT_SECRET"] = conf["yoink"]["discord"]["secret"]

    app.config["TWITTER_API_KEY"] = conf["yoink"]["twitter"]["key"]
    app.config["TWITTER_API_SECRET"] = conf["yoink"]["twitter"]["secret"]

    app.config["GITHUB_CLIENT_ID"] = conf["yoink"]["github"]["client_id"]
    app.config["GITHUB_CLIENT_SECRET"] = conf["yoink"]["github"]["secret"]
    return app
