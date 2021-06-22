from . import views


def setup_routes(app):
    app.router.add_view('/', views.IndexEndPoint)
    app.router.add_view('/search', views.Search)