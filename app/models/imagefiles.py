from mongoengine import StringField, IntField, DateField
from app import mongo

#Model for Image File Data
class ImageFile(mongo.Document):
    meta = {"collection": "images.files"}
    width = IntField()
    height = IntField()
    format = StringField()
    thumbnail_id = StringField()
    contentType = StringField()
    md5 = StringField()
    chunkSize = IntField()
    length = IntField()
    uploadDate = DateField()