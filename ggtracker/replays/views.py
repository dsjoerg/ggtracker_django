import traceback

from django.shortcuts import render, redirect, get_object_or_404
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import RequestContext

from ajaxuploader.views import AjaxFileUploader
from upload import StringUploadBackend
from replay_persister import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from buildnodes import *


replayPersister = ReplayPersister()
buildNodes = BuildNodes()
uploader = AjaxFileUploader(backend=StringUploadBackend, completeListener=replayPersister)

def json_uploader(request):
    if request.method != "GET":
        return HttpResponseBadRequest("AJAX request not valid")
    id = request.GET['id']
    try:
      if replayPersister.upload_from_ruby(id):
          return HttpResponse("no problem")
      else:
          return HttpResponseServerError("problem")
    except Exception, e:
      print "Exception! ", e
      return HttpResponseServerError("big problem. check the logs.")

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

def buildnodes_v1(request):
    file = buildNodes.stream_file(request.GET.get("id"))
    response = HttpResponse(mimetype="application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename=%s' % "foo.SC2Replay"
    response.write(file.getvalue())
    return response

def buildnodes(request):
    try:
        buildNodes.populate_bo_for_game(request.GET.get("id"))
        response = HttpResponse("Done.<br>")
    except Exception, e:
        print "Exception!"
        traceback.print_exc()
        response = HttpResponseServerError("problem var")

    return response
