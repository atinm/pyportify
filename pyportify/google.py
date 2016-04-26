import json
import uuid
import urllib

import asyncio
from pyportify import gpsoauth
from pyportify.util import uprint

SJ_DOMAIN = "mclients.googleapis.com"
SJ_URL = "/sj/v1.11"

FULL_SJ_URL = "https://{0}{1}".format(SJ_DOMAIN, SJ_URL)


def encode(values):
    return urllib.parse.urlencode(values)


class Mobileclient(object):

    def __init__(self, session, token=None):
        self.token = token
        self.session = session

    @asyncio.coroutine
    def login(self, username, password):
        android_id = "asdkfjaj"
        res = gpsoauth.perform_master_login(username, password, android_id)

        if "Token" not in res:
            return None

        self._master_token = res['Token']
        res = gpsoauth.perform_oauth(
            username, self._master_token, android_id,
            service='sj', app='com.google.android.music',
            client_sig='38918a453d07199354f8b19af05ec6562ced5788')
        if 'Auth' not in res:
            return None
        self.token = res["Auth"]
        return self.token

    @asyncio.coroutine
    def search_all_access(self, search_query, max_results=30):
        params = {"q": search_query, "max_items": max_results, 'type': 1}
        query = encode(params)
        url = "/query?{0}".format(query)
        data = yield from self._http_get(url)
        return data

    @asyncio.coroutine
    def find_best_track(self, search_query, content_type):
        data = yield from self.search_all_access(search_query)
        if "entries" not in data:
            return None
        s = search_query.split(" / ")
        artist = None
        title = None
        album = None
        if len(s) > 2:
            artist = s[0]
            title = s[1]
            album = s[2]
        elif len(s) > 1:
            artist = s[0]
            title = s[1]
        else:
            title = s[0]

        for entry in data["entries"]:
            # only get songs, skip explicit ones if necessary
            # uprint("\nchecking {0} for {1}".format(entry, search_query))
            if entry["type"] == "1":
                if content_type != 'E' and entry["track"]["contentType"] == "1":
                    continue
                # match album, title
                if album != None:
                    if entry["track"]["album"] == album:
                        if title != None:
                            if entry["track"]["title"] in title or title in entry["track"]["title"]:
                                return entry["track"]
                        else:
                            return entry["track"]
                else:
                    if title != None:
                        if entry["track"]["title"] in title or title in entry["track"]["title"]:
                            return entry["track"]
                    else:
                        return entry["track"]

        return None

    @asyncio.coroutine
    def create_playlist(self, name, public=False):
        mutations = build_create_playlist(name, public)
        data = yield from self._http_post("/playlistbatch?alt=json", {
            "mutations": mutations,
        })
        return data["mutate_response"][0]["id"]  # playlist_id

    @asyncio.coroutine
    def add_songs_to_playlist(self, playlist_id, track_ids):
        mutations = build_add_tracks(playlist_id, track_ids)
        yield from self._http_post("/plentriesbatch?alt=json", {
            "mutations": mutations,
        })

    @asyncio.coroutine
    def _http_get(self, url):
        headers = {
            "Authorization": "GoogleLogin auth={0}".format(self.token),
            "Content-type": "application/json",
        }

        res = yield from self.session.request(
            'GET',
            FULL_SJ_URL + url,
            headers=headers
        )
        data = yield from res.json()
        return data

    @asyncio.coroutine
    def _http_post(self, url, data):
        data = json.dumps(data)
        headers = {
            "Authorization": "GoogleLogin auth={0}".format(self.token),
            "Content-type": "application/json",
        }
        res = yield from self.session.request(
            'POST',
            FULL_SJ_URL + url,
            data=data,
            headers=headers,
        )
        ret = yield from res.json()
        return ret


def build_add_tracks(playlist_id, track_ids):
    mutations = []
    prev_id = ""
    cur_id = str(uuid.uuid4())
    next_id = str(uuid.uuid4())

    for i, track_id in enumerate(track_ids):
        details = {
            "create": {
                "clientId": cur_id,
                "creationTimestamp": -1,
                "deleted": False,
                "lastModifiedTimestamp": "0",
                "playlistId": playlist_id,
                "source": 1,
                "trackId": track_id,
            }
        }

        if track_id.startswith("T"):
            details["create"]["source"] = 2  # AA track

        if i > 0:
            details["create"]["precedingEntryId"] = prev_id

        if i < len(track_ids) - 1:
            details["create"]["followingEntryId"] = next_id

        mutations.append(details)

        prev_id = cur_id
        cur_id = next_id
        next_id = str(uuid.uuid4())
    return mutations


def build_create_playlist(name, public):
    return [{
        "create": {
            "creationTimestamp": "-1",
            "deleted": False,
            "lastModifiedTimestamp": 0,
            "name": name,
            "type": "USER_GENERATED",
            "accessControlled": public,
        }
    }]


def parse_auth_response(s):
    # SID=DQAAAGgA...7Zg8CTN
    # LSID=DQAAAGsA...lk8BBbG
    # Auth=DQAAAGgA...dk3fA5N
    res = {}
    for line in s.split("\n"):
        if not line:
            continue
        k, v = line.split("=", 1)
        res[k] = v
    return res
