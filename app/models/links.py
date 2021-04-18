from mongoengine import StringField, EmbeddedDocumentListField, ObjectIdField
from app import mongo
from .data import Data

#Model for Links
class Links(mongo.Document):
    creator = ObjectIdField()
    track_id = StringField()
    url_code = StringField()
    redirect_url = StringField()
    full_url = StringField()
    grab_info = EmbeddedDocumentListField(Data)