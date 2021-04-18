from mongoengine import StringField, BooleanField, EmbeddedDocument

#Model for Spotify link
class Spotify(EmbeddedDocument):
    connected = BooleanField()
    username = StringField()
    email = StringField()
    profile_url = StringField()
    access_token = StringField()
    refresh_token = StringField()