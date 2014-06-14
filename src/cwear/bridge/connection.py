import requests
import time

SUCCESSFUL_STATUS_CODES = [
    200,
    201
]


class HttpConnection(object):
    def __init__(self, auth, base_url):
        self._auth = auth
        self._base_url = base_url

    def _make_url(self, path):
        if not path.startswith("/"):
            path = "/" + path
        return "%s%s" % (self._base_url, path)

    def _make_request(self, retries, method, url, **kwargs):
        remaining_attempts = retries + 1
        while remaining_attempts > 0:
            response = requests.request(method, url, auth=self._auth, **kwargs)
            if response.status_code in SUCCESSFUL_STATUS_CODES:
                return response
            remaining_attempts -= 1
            time.sleep(1)

        err = "%s to %s failed - HTTP(%s)" % (method, url, response.status_code)
        raise Exception(response, err)

    #---------------------------------------------------------------------------
    # HTTP Methods
    #---------------------------------------------------------------------------
    def get(self, path, retries=0, **kwargs):
        url = self._make_url(path)
        return self._make_request(retries, "GET", url, **kwargs)

    def post(self, path, data, retries=0, **kwargs):
        url = self._make_url(path)
        return self._make_request(retries, "POST", url, data=data, **kwargs)

    def put(self, path, data, retries=0, **kwargs):
        url = self._make_url(path)
        return self._make_request(retries, "PUT", url, data=data, **kwargs)

    def delete(self, path, retries=0):
        url = self._make_url(path)
        return self._make_request(retries, "DELETE", url)
