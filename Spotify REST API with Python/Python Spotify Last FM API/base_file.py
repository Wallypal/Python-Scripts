import json
import requests
import secrets

import sys

class lastFmSpotify:

    def __init__(self):
        self.token = secrets.spotify_token()
        self.api_key = secrets.last_fm_api_key()
        self.user_id = secrets.spotify_user_id()
        self.spotify_headers = {"Content-Type": "application/json",
                                "Authorization": f"Bearer {self.token}"}
        self.playist_id = ''
        self.song_info = {}
        self.uris = []

    def fetch_songs_from_lastfm(self):
        params = {'limit': 10, 'api_key': self.api_key}
        url = f'http://ws.audioscrobbler.com/2.0/?method=chart.gettoptracks&format=json'
        response = requests.get(url, params=params)
        if response.status_code != 200:
            self.exceptionalExceptions(response.status_code, response.text())
        res = response.json()
        print("Top Songs are: ")
        for item in res['tracks']['track']:
            song = item['name'].title()
            artist = item['artist']['name'].title()
            print(f"{song} by {artist}")
            self.song_info[song] = artist
        print("Getting Songs URI\n")
        self.get_uri_from_spotify()
        print("Creating a playlist!\n")
        self.create_spotify_playlist()
        print("Adding Songs!\n")
        self.add_songs_to_playlist()
        print("Songs are as follows: \n")
        self.list_songs_in_playlist()


    def get_uri_from_spotify(self):
        for song_name, artist in self.song_info.items():
            url = f"https://api.spotify.com/v1/search?query=track%3A{song_name}+artist%3A{artist}&type=track&offset=0&limit=10"
            response = requests.get(url, headers=self.spotify_headers)
            res = response.json()
            output_uri = res['tracks']['items']
            uri = output_uri[0]['uri']
            self.uris.append(uri)




    def create_spotify_playlist(self):
        data = {
            "name": "LastFM top songs 123",
            "description": "Songs from the topcharts of Last FM created via an API",
            "public": True
        }
        data = json.dumps(data)
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        response = requests.post(url, data=data, headers=self.spotify_headers)

        if response.status_code == 201:
            res = response.json()
            print("Playlist Created")
            self.playist_id = res['id']
        else:
            self.exceptionalExceptions(response.status_code,response.text())

    def add_songs_to_playlist(self):
        uri_list = json.dumps(self.uris)
        url = f"https://api.spotify.com/v1/playlists/{self.playist_id}/tracks"
        response = requests.post(url, data=uri_list, headers=self.spotify_headers)
        if response.status_code == 201:
            print("Songs Added Successfully.")
        else:
            self.exceptionalExceptions(response.status_code, response.text())

    def list_songs_in_playlist(self):
        url = f"https://api.spotify.com/v1/playlists/{self.playist_id}/tracks"
        response = requests.get(url, headers=self.spotify_headers)
        if response.status_code != 200:
            self.exceptionalExceptions(response.status_code, response.text())
        else:
            res = response.json()
            for item in res['items']:
                print(item['track']['name'])

    def exceptionalExceptions(self, status_code, err):
        print("Exception Occured with status_code", status_code)
        print("Error: ", err)
        sys.exit(0)


if __name__ == '__main__':
    d = lastFmSpotify()
    d.fetch_songs_from_lastfm()