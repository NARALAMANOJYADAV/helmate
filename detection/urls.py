from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    path('login', views.login_view, name='login'),
    path('login.html', views.login_view, name='login_html'),
    path('logout', views.logout_view, name='logout'),
    path('dash-home.html', views.dashboard_home, name='dashboard_home'),
    path('dashboard.html', views.violations_history, name='violations_history'),
    path('graph.html', views.statistics, name='statistics'),
    path('messages.html', views.messages, name='messages'),
    path('about.html', views.about, name='about'),
    path('files.html', views.files_view, name='files_view'),
    path('notification.html', views.notifications, name='notifications'),
    
    # API endpoints
    path('api/stats', views.get_stats, name='get_stats'),
    path('api/challans', views.get_challans, name='get_challans'),
    path('api/camera-status', views.camera_status, name='camera_status'),
    path('api/process_frame', views.process_frame_api, name='process_frame_api'),
    path('api/challans/delete/<int:challan_id>', views.delete_violation, name='delete_violation'),
    path('video_feed', views.video_feed, name='video_feed'),
]
