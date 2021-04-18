from mongoengine import StringField, DateTimeField, FloatField, EmbeddedDocument

#Model for IP Information
class Data(EmbeddedDocument):
    ip = StringField()
    useragent = StringField()
    country = StringField()
    datetime = StringField()
    lat = FloatField()
    lon = FloatField()