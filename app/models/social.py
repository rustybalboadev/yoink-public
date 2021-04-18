from mongoengine import StringField, EmbeddedDocument, EmbeddedDocumentField
from .socials import *

#Model for Social Information
class Social(EmbeddedDocument):
    github = EmbeddedDocumentField(Github)
    twitter = EmbeddedDocumentField(Twitter)
    discord = EmbeddedDocumentField(Discord)
    spotify = EmbeddedDocumentField(Spotify)