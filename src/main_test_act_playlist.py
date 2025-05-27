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
from download_playlist import actualize_playlist, download_musics_from_youtube


# consts
path_project = os.path.dirname(os.path.dirname(__file__))
path_playlists_url_file = os.path.join(path_project, "data", "musicme_playlists", "playlists.txt")
path_download_playlist_dir = os.path.join(path_project, "data", "downloaded")

# check dir paths
if not os.path.exists(path_download_playlist_dir):
    os.makedirs(path_download_playlist_dir)


# get a data playlist path
def get_playlist_data_path(playlist:dict):
    """Get a path of the playlist data"""
    return os.path.join(path_download_playlist_dir, playlist["name"]+".json")

# check playlist changes
def check_playlist_changes(playlist:dict):
    """Check playlist changes compared to old version and choose if redownload this"""

    playlist_modified = False
    to_download = []
    to_remove = []
    to_move = []

    # load old version of playlist (actual playlist not saved)
    try:
        with open(get_playlist_data_path(playlist), "r") as r_file:
            old_playlist = json.load(r_file)

    # if old playlist not found -> download all
    except:
        playlist_modified = True 
        to_download = playlist["data"]

    # if old playlist loaded : compare
    else:
        # check music dir exists
        if not os.path.exists(playlist["download_dir"]):
            playlist_modified = True 
            to_download = playlist["data"]

        # search musics added
        
        # search musics moved

        # search musics removed
        # check if all musics exists
    
    # save temp change data in the playlist
    if to_download != []: playlist["to_download"] = to_download
    if to_remove != []: playlist["to_remove"] = to_remove
    if to_move != []: playlist["to_move"] = to_move

    # return if the playlist has changed
    return playlist_modified

# save playlist in a .json
def save_playlist_json(playlist:dict):
    """Save playlist metadata is a json file"""
    
    # split temp change data of the playlist for save
    for i in ["to_download", "to_remove", "to_move"]:
        if i in playlist: playlist.pop(i)
    
    # save playlist data
    with open(get_playlist_data_path(playlist), "w") as w_file:
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

    # check playlist changes
    if check_playlist_changes(new_playlist):
        # TODO: after, redownload only changes
        print(f"Playlist '{new_playlist['name']}' is modified -> actualize changes")
        # append and save the new playlist
        playlists.append(new_playlist)
        save_playlist_json(new_playlist)

    else:
        print(f"Playlist '{new_playlist['name']}' is unchanged -> skip this")


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
#    save_playlist_json(playlist)
