from mongoengine import StringField, BooleanField, EmbeddedDocument

#Model for Twitter link
class Twitter(EmbeddedDocument):
    connected = BooleanField()
    username = StringField()
    profile_url = StringField()
    email = StringField()
    oauth_token = StringField()
    oauth_token_secret = StringField()