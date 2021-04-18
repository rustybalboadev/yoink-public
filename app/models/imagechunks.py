from mongoengine import IntField, BinaryField, ObjectIdField
from app import mongo

#Model for Image Chunks Data
class ImageChunks(mongo.Document):
    meta = {"collection": "images.chunks"}
    files_id = ObjectIdField()
    n = IntField()
    data = BinaryField()