from mongoengine import IntField
from app import mongo

#Model for Stats Data
class Stats(mongo.Document):
    total_ips = IntField()
    total_users = IntField()
    total_views = IntField()
    total_links = IntField()