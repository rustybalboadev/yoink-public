from app.models import User, Links, Stats

def updateStats():
    from app import views
    total_ips = 0
    links = Links.objects().all()
    for link in links:
        total_ips += len(link.grab_info)
    total_users = User.objects.count()
    total_links = Links.objects.count()
    total_views = views

    stats = Stats.objects().all()
    stats.update(
        total_ips=total_ips,
        total_users=total_users,
        total_views=total_views,
        total_links=total_links
    )
