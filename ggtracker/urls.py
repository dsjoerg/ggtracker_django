from django.conf.urls.defaults import patterns, include, url

import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'replays.views.upload', name='home'),
    # url(r'^ggtracker/', include('ggtracker.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
#    url(r'start$', 'replays.views.start', name="start"),
    url(r'ajax-upload$', 'replays.views.dj_uploader', name="my_ajax_upload"),
    url(r'^upload.json$', 'replays.views.json_uploader', name="whatever"),
    url(r'^buildnodes$', 'replays.views.buildnodes', name="buildnodes"),
    url(r'^hirefireapp/test$', 'replays.views.hirefireapp', name="hirefireapp"),
    url(r'^hirefireapp/', 'replays.views.hirefireappinfo', name="hirefireappinfo"),
)

urlpatterns += patterns('',
(r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)

#
# only installed on dev server as of 20120214
#
#urlpatterns += patterns('',
#    (r'^dowser/', include('django_dowser.urls')),
#)
#
