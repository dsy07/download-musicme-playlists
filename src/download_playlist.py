#---------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# Python: 3.12
# Author: Killian Nallet
# Date: 21/05/2025
#---------------------------------------------------------------------------------


# imports
import logging
from pytubefix import YouTube, Search


# disable logger (for not needed warning messages by pytubefix)
logging.disable()


# download a music
def download_url_from_youtube(url:str, playlist_dir:str, name_prefix:str=""):
    """Download a music from his youtube url."""

    # download url
    yt = YouTube(url)
    ys = yt.streams.get_audio_only()
    ys.download(playlist_dir, name_prefix+ys.default_filename)


# search a music
def _search_on_youtube(search_query:str):
    """Search a video on youtube with a query"""

    # search the music
    search = Search(search_query)

    # check search
    if search.videos == []:
        return None

    # return first element of the search (the must pertinent)
    return search.videos[0].watch_url

def search_music_on_youtube(music:dict):
    """Search a music on youtube with multiple ways with his name and his autors"""

    # create multiple queries for find the music to counter not found music
    queries = [
        f"{music["title"]} - {" & ".join(music["authors"])}",
        f"{music["title"]} - {music["authors"][0]}",
        f"{music["title"]} - music"
    ]

    # search the music
    for query in queries:
        music_url = _search_on_youtube(query)
        if music_url is not None: break

    # check search and return music url
    if music_url is None:
        raise Exception(f"Music '{music["title"]}' give no results on Youtube !")

    return music_url


# download a playlist of musics
def download_musics_from_youtube(musics:dict[list[dict]], path_download_dir, numbered_names=True):
    """Download a playlist of musics from youtube (from list of urls or music names)."""

    # enumerate musics
    nb_musics = len(musics)
    musics_download_cnt = 0

    for music in musics:
        # find music url
        print(f"- searching '{music["title"]}' ...")
        url_music = search_music_on_youtube(music)

        # update download musics count
        musics_download_cnt += 1

        # create new name
        name_prefix = f"{musics_download_cnt} - " if numbered_names else ""
        
        # download music from url
        print(f"-> {musics_download_cnt}/{nb_musics} downloading '{music["title"]}' ({url_music}) ...")
        try:
            download_url_from_youtube(url_music, path_download_dir, name_prefix)
        except Exception as err:
            return False, f"({type(err).__name__}: {err})"            
        except KeyboardInterrupt:
            return False, "(KeyboardInterrupt)"

    # if no error occured
    return True, None


# download a playlist of musics and actualize changes
def actualize_playlist(playlist:dict):
    """download a playlist of musics and actualize changes"""
    pass

    # check "to_download" and "to_remove", "to_move"

    result, err_txt = download_musics_from_youtube(playlist["data"], playlist["download_dir"])
