#!/usr/bin/env python3

import asyncio
import ssl
from getpass import getpass
import sys

import aiohttp
from aiohttp import ClientSession
import certifi

from pyportify import app
from pyportify.google import Mobileclient
from pyportify.spotify import SpotifyClient
from pyportify.hypem import HypemClient
from pyportify.util import uprint

try:
    input = raw_input
except NameError:
    pass

@asyncio.coroutine
def start():

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl_context=sslcontext)

    with ClientSession(connector=conn) as session:

        google_email = input("Enter Google email address: ")
        google_pass = getpass("Enter Google password: ")

        g = Mobileclient(session)

        logged_in = yield from g.login(google_email, google_pass)
            
        if not logged_in:
            uprint("Invalid Google username/password")
            sys.exit(1)

        user_id = input("Enter Hypem username: ")
        password = getpass("Enter Hypem password: ")

        explicit = input("Enter Y if you want to include explicit songs: ")
        if explicit == 'Y':
            content_type = 'E'
        else:
            content_type = 'R'

        h = HypemClient(session, user_id, password)
        
        # now fetch the json for the hypem popular top 50
        playlist = yield from h.fetch_popular()
#        uprint("playlist", playlist)
        yield from app.transfer_hypem_playlist(None, h, g, playlist, content_type)


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    finally:
        loop.close()

if __name__ == '__main__':
    main()
