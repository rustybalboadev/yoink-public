from mongoengine import StringField, BooleanField, EmbeddedDocument

#Model for Github link
class Github(EmbeddedDocument):
    connected = BooleanField()
    username = StringField()
    profile_url = StringField()
    email = StringField()
    access_token = StringField()