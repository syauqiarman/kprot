from django.shortcuts import render

from django.shortcuts import render
from django.urls import reverse, NoReverseMatch

def get_app_endpoints():
    """ Fetches main endpoints for the registered apps dynamically """
    apps = {
        "PendaftaranMahasiswa": [
            "daftar",  # Example view names

        ],
    }
    
    app_urls = {}
    for app, views in apps.items():
        urls = []
        for view in views:
            try:
                urls.append((view, reverse(view)))
            except NoReverseMatch:
                urls.append((view, "#"))  # Placeholder if not found
        app_urls[app] = urls
    
    return app_urls

def dashboard_view(request):
    """ Main dashboard view """
    context = {
        "app_endpoints": get_app_endpoints()
    }
    return render(request, "dashboard.html", context)

