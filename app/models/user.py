from mongoengine import StringField, BooleanField, ListField, EmbeddedDocumentField, ImageField
from app import mongo
from .social import Social

#Model for User Data
class User(mongo.Document):
    meta = {"collection": "users"}
    username = StringField()
    bio = StringField()
    avatar = ImageField()
    email = StringField()
    data = StringField()
    nonce = StringField()
    mac = StringField()
    password_reset_id = StringField()
    socials = EmbeddedDocumentField(Social)
    is_admin = BooleanField()
