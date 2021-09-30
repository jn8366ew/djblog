from django.urls import path
from portfolio import views


app_name = 'portfolio'
urlpatterns = [

    path('', views.PortfolioLV.as_view(), name='index'),

    path('<int:pk>/', views.PortfolioDV.as_view(), name='detail'),

    # /portfolio/add
    path('add/', views.PortfolioCreateView.as_view(), name='add',),

    # /portfolio/change/
    path('change/', views.PortfolioChangeLV.as_view(), name='change',),

    # /portfolio/99/update
    path('<int:pk>/update/', views.PortfolioUpdateView.as_view(), name='update', ),

    # /portfolio/99/delete
    path('<int:pk>/delete/', views.PortfolioDeleteView.as_view(), name='delete', ),

]