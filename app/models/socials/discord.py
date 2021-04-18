from mongoengine import StringField, BooleanField, EmbeddedDocument

#Model for Discord link
class Discord(EmbeddedDocument):
    connected = BooleanField()
    username = StringField()
    discriminator = StringField()
    email = StringField()
    access_token = StringField()
    refresh_token = StringField()