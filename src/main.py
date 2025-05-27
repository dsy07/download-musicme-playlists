#---------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# Python: 3.12
# Author: Killian Nallet
# Date: 21/05/2025
#---------------------------------------------------------------------------------


#TODO: en faire une app customtkinter


# imports
import os
import json
from extract_playlist import extract_playlist_from_url
from download_playlist import download_musics_from_youtube


# consts
path_project = os.path.dirname(os.path.dirname(__file__))
path_data = os.path.join(path_project, "data")
path_musicme_playlists = os.path.join(path_data, "musicme_playlists")
path_download_playlist_dir = os.path.join(path_data, "downloaded")
path_playlists_url_file = os.path.join(path_musicme_playlists, "playlists.txt")

# check dir paths
if not os.path.exists(path_download_playlist_dir):
    os.makedirs(path_download_playlist_dir)


# save playlist in a .json
def save_playlist_json(playlist:dict):
    """Save playlist metadata is a json file"""

    # save playlist data
    with open(os.path.join(path_musicme_playlists, playlist["name"]+".json"), "w") as w_file:
        json.dump(playlist, w_file, indent=2)


# check if playlists.txt exists
if os.path.exists(path_playlists_url_file):
    # use playlists urls
    print("Use 'playlist.txt' file of urls for download playlists\nLoad 'playlist.txt' ...")
    with open(path_playlists_url_file, "r") as r_file:
        playlist_urls = r_file.readlines()

else:
    # file not found
    print("Error : 'playlists.txt' file not found !\nPlease create this file with the urls of the playlists to download.")


# get playlists from html extracts
print("Extracting playlists ...")
playlists = []

for playlist_url in playlist_urls:

    # extract the playlist from the html file
    playlist, playlist_name = extract_playlist_from_url(playlist_url)
    print(f"- playlist '{playlist_name}' extracted")

    # create new_playlist
    new_playlist = {
        "name": playlist_name,
        "nb_musics": len(playlist),
        "download_dir": os.path.join(path_download_playlist_dir, playlist_name),
        "downloaded": False,
        "data": playlist
    }

    # append and save the new playlist
    playlists.append(new_playlist)
    save_playlist_json(new_playlist)


# download playlists
for playlist in playlists:

    # get and check download playlist path
    path_download_dir = playlist["download_dir"]
    if not os.path.exists(path_download_dir):
        os.mkdir(path_download_dir)

    # download playlist
    pl_name = playlist["name"]
    print(f"\nDownloading playlist '{pl_name}' ({playlist["nb_musics"]} musics) ...")
    result, err_txt = download_musics_from_youtube(playlist["data"], path_download_dir)

    # check playlist downloaded
    playlist["downloaded"] = result
    if result:
        print(f"=> Playlist '{pl_name}' downloaded")
    else:
        print(f"=> Playlist '{pl_name}' not downloaded ! "+err_txt)

    # save the new data actualized for the playlist
    save_playlist_json(playlist)
