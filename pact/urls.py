from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from text_app.views import home_view
from authorization_app.views import user_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authorization_app.urls')),
    path('text/', include('text_app.urls')),
    path('students/', include('students_app.urls')),
    path('years_groups/', include('years_and_groups_app.urls')),
    path('statistics/', include('statistics_app.urls')),
    path('', user_login, name='user_login'),
    path('home/', home_view, name='home_view')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
