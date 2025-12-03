"""
URL configuration for booksearch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from books import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('cadastrar/', views.cadastrar_livro, name='cadastrar_livro'),
    path('salvar/', views.salvar_livro, name='salvar_livro'),
    path('listar/', views.listar_livros, name='listar_livros'),
    path('buscar/', views.buscar_livro, name='buscar_livro'),
    path('limpar-cache/', views.limpar_cache, name='limpar_cache'),
]

