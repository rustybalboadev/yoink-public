import ssl, uuid, smtplib
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.mime.text import MIMEText
from flask import session, redirect
from app import socket, app
from app.models import Links, User, ImageChunks, ImageFile
from app.utils import Encryption

@socket.on("update_link")
def updateLink(data):
    url = data["url"]
    trackID = data["track_id"]
    link = Links.objects(track_id=trackID).first()
    link.update(full_url=url)

@socket.on("account_delete")
def accountDelete():
    user = User.objects(username=session.get("username")).first()
    user_id = user.id
    avatar_id = user.avatar.grid_id
    image_file = ImageFile.objects(id=avatar_id).first()
    image_chunk = ImageChunks.objects(files_id=avatar_id).first()
    image_file.delete()
    image_chunk.delete()
    user.delete()
    links = Links.objects(creator=user_id).all()
    for link in links:
        link.delete()
    socket.emit("redirect", {"path": "/logout"})

@socket.on("send_reset_link")
def sendResetLink(data):
    email = data["email"]
    user = User.objects(email=email).first()

    uuidStr = str(uuid.uuid4())
    user.update(
        set__password_reset_id = uuidStr
    )
    context = ssl.create_default_context()
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset Password Link"
    message["From"] = app.config["EMAIL_ADDRESS"]
    message["To"] = email
    message.attach(MIMEText("Reset Password URL: https://yoink.rip/password_reset?code={}".format(uuidStr), "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(app.config["EMAIL_ADDRESS"], app.config["EMAIL_PASSWORD"])
        
        server.sendmail(app.config["EMAIL_ADDRESS"], email, message.as_string())