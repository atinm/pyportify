import asyncio
import urllib

HYPEM_API = \
    "https://api.hypem.com/v2"
HYPEM_POPULAR = \
    "/popular?mode=now&page=1&count=50&key=swagger"
HYPEM_GET_TOKEN = \
    "/get_token"

class HypemQuery():

    def __init__(self, i, hy_playlist_uri, hy_track, track_count):
        self.i = i
        self.playlist_uri = hy_playlist_uri
        self.hy_track = hy_track
        self.track_count = track_count

    def search_query(self):
        search_query = "{0} / {1}".format(
            self.hy_track['artist'],
            self.hy_track['title'])
        return search_query


def encode(values):
    return urllib.parse.urlencode(values)


class HypemClient(object):

    def __init__(self, session, user_id=None, password=None):
        self.session = session
        self.token = None
        self.user_id = user_id
        self.password = password

    @asyncio.coroutine
    def _http_post(self, url, data):
        data = json.dumps(data)
        headers = {
            "Content-type": "application/json",
        }
        res = yield from self.session.request(
            'POST',
            HYPEM_API + url,
            data=data,
            headers=headers,
        )
        ret = yield from res.json()
        return ret

    @asyncio.coroutine
    def _http_get_all(self, url):
        ret = []
        while True:
            data = yield from self._http_get(url)
            url = data['next']
            ret.extend(data['items'])
            if url is None:
                break
        return ret

    @asyncio.coroutine
    def _http_get(self, url):
        headers = {
            "Content-type": "application/json",
        }
        res = yield from self.session.request(
            'GET',
            url,
            headers=headers,
        )
        data = yield from res.json()
        if "error" in data:
            raise Exception("Error: {0}, url: {1}".format(data, url))
        return data

    @asyncio.coroutine
    def fetch_popular(self):
        url = HYPEM_API + HYPEM_POPULAR
        ret = yield from self._http_get(url)
        return ret
    
#    @asyncio.coroutine
#    def get_token(self):
#        url = HYPEM_API + HYPEM_GET_TOKEN
#        playlists = yield from self._http_post(
#           url, {
#                "username": self.user_id,
#                "password": self.password,
#                }
#        )
#        if "error" in playlists:
#            return False
#        return True


