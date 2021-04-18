import requests
from flask_restful import Resource, reqparse
from flask import Response, session, redirect
from app import socket, app
from urllib.parse import unquote_plus

#Logout of website
class Logout(Resource):
    def get(self):
        session.pop("username", None)
        session["logged_in"] = False
        return redirect(app.config["BASE_URL"] + "/")

#Deleting tracking link
class DeleteLink(Resource):
    def post(self):
        from app.models import Links, User

        parser = reqparse.RequestParser()
        parser.add_argument("id")
        args = parser.parse_args()
        
        link = Links.objects(track_id=args["id"]).first()
        userObject = link.creator

        user = User.objects(id=userObject).first()
        requestUser = User.objects(username=session.get("username")).first()
        if requestUser.is_admin:
            link.delete()
            socket.emit("refresh")
        elif session.get("username") == user.username:
            link.delete()
            socket.emit("refresh")

#Delete user
class DeleteUser(Resource):
    def post(self):
        from app.models import User, Links, ImageFile, ImageChunks
        parser = reqparse.RequestParser()
        parser.add_argument("userid")
        args = parser.parse_args()
        requester = User.objects(username=session.get("username")).first()
        user = User.objects(id=args["userid"]).first()
        if requester.is_admin and not user.is_admin:
            links = Links.objects(creator=user.id).all()
            for link in links:
                link.delete()
                
            avatar_id = user.avatar.grid_id
            image_file = ImageFile.objects(id=avatar_id).first()
            image_chunk = ImageChunks.objects(files_id=avatar_id).first()
            image_file.delete()
            image_chunk.delete()
            user.delete()
            socket.emit("refresh")

#Make User Admin
class MakeAdmin(Resource):
    def post(self):
        from app.models import User
        parser = reqparse.RequestParser()
        parser.add_argument("userid")
        args = parser.parse_args()
        requesterUser = User.objects(username=session.get("username")).first()
        user = User.objects(id=args["userid"]).first()
        if requesterUser.is_admin:
            user.update(
                set__is_admin=True
            )
            user.save
            socket.emit("refresh")

#Update Profile Information
class ProfileInfo(Resource):
    def get(self):
        from app.models import User
        parser = reqparse.RequestParser()
        parser.add_argument("username")
        parser.add_argument("bio")
        args = parser.parse_args()

        user = User.objects(username=session.get("username")).first()
        username = user.username if args["username"] == "" else args["username"]
        bio = user.bio if args["bio"] == "" else args["bio"]
        bio = unquote_plus(bio)
        session["username"] = username
        user.update(
            username=username,
            bio=bio
        )
        return redirect(app.config["BASE_URL"] + "/settings")