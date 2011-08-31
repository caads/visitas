from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'visitas.aplicacao.views.index', name='index'),
    url(r'^sucesso/', 'visitas.aplicacao.views.sucesso', name='sucesso'),
    url(r'^agendar_visita/', 'visitas.aplicacao.views.agendar_visita', name='agendar_visita'),
    url(r'^consulta/', 'visitas.aplicacao.views.consulta', name='consulta'),
    url(r'^media/(.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),
    (r'^login/', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^logout/', 'django.contrib.auth.views.logout', {'template_name': 'logout.html', 'next_page': '/login'}),
    url(r'^relatorio', 'visitas.aplicacao.views.relatorio', name='relatorio'),    
)
