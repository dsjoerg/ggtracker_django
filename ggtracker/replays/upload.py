from ajaxuploader.backends.base import AbstractUploadBackend
from StringIO import StringIO

class StringUploadBackend(AbstractUploadBackend):
      def __init__(self, *args, **kwargs):
            self._completeListener = kwargs.pop('completeListener')
            super(StringUploadBackend, self).__init__(*args, **kwargs)

      def upload_chunk(self, chunk):
            self._localbuf.write(chunk)

      def setup(self, filename):
            self._localbuf = StringIO()

      def upload_complete(self, request, filename):
            self._completeListener.upload_complete(filename, self._localbuf)
            self._localbuf.close()
