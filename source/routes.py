from . import views


def setup_routes(app):
    app.router.add_view('/', views.IndexEndPoint)
    app.router.add_view('/posts/search', views.Search)
    app.router.add_view('/posts/{document_id}', views.Post)