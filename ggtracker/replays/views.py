from django.shortcuts import render, redirect, get_object_or_404
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import RequestContext

from ajaxuploader.views import AjaxFileUploader
from upload import StringUploadBackend
from replay_persister import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

replayPersister = ReplayPersister()
uploader = AjaxFileUploader(backend=StringUploadBackend, completeListener=replayPersister)

def json_uploader(request):
    if request.method != "GET":
        return HttpResponseBadRequest("AJAX request not valid")
    id = request.GET['id']
    if replayPersister.upload_from_ruby(id):
        return HttpResponse("no problem")
    else:
        return HttpResponseServerError("problem")

def dj_uploader(request):
    try:
        result = uploader(request)
    except Exception, e:
        print "Exception! ", e
    return result

def start(request):
    csrf_token = get_token(request)
    return render_to_response('import.html',
        {'csrf_token': csrf_token}, context_instance = RequestContext(request))

def upload(request):
    return render(request, 'replays/upload.html')
