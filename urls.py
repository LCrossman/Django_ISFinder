#use include() to add paths from the catalog application
from django.urls import include
#adding URL maps to redirect the base URL to our application
from django.views.generic import RedirectView
#static() to add URL mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    path('', RedirectView.as_view(url='catalog/', permanent=True)),
]
urlpatterns += [
    path('catalog/', include('catalog.urls')),
]
