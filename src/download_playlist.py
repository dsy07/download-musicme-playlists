#---------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# Python: 3.12
# Author: Killian Nallet
# Date: 21/05/2025
#---------------------------------------------------------------------------------


# imports
import logging
from pytubefix import YouTube, Search
from progressbar import pbar


# configure logger
log = logging.getLogger("__main__")


# download a music
def download_url_from_youtube(url:str, playlist_dir:str, name_prefix:str=""):
    """Download a music from his youtube url."""

    # init yt
    yt = YouTube(url)
    ys = yt.streams.get_audio_only()
    filename = name_prefix+ys.default_filename

    # download url
    log.info(f"downloading {url} ({filename}) from youtube")
    ys.download(playlist_dir, filename)


# search a music
def _search_on_youtube(search_query:str):
    """Search a video on youtube with a query and return 5 videos"""

    # search the music
    log.debug(f"searching \"{search_query}\" on youtube")
    search = Search(search_query)

    # check search
    if search.videos == []:
        return None

    # return first element of the search (the must pertinent)
    return search.videos[:5]

def search_music_on_youtube(music:dict):
    """Search a music on youtube with multiple ways with his name and his autors"""

    # create multiple queries for find the music to counter not found music
    query_authors = music["authors"][:2] # more than 2 authors can falsify research
    queries = [
        f"{music["title"]} - {" & ".join(query_authors)}",
        f"{music["title"]} - {music["authors"][0]}",
        f"{music["title"]} - music"
    ]

    # search the music
    for query in queries:
        # launch query
        musics_searched = _search_on_youtube(query)

        # filter search
        for music_searched in musics_searched:
            if "Official Video" in music_searched.title:
                pass # sometimes "Official Lyric" (only music) is better than "Official Video" (with extended clip)
            elif "extended mix" not in music["title"].lower() and "extended mix" in music_searched.title.lower():
                pass # sometimes, the "extended" version appears before the original version when the "extended" version is not requested
            elif "rework" not in music["title"].lower() and "rework" in music_searched.title.lower():
                pass # sometimes, the "rework" version appears before the original version when the "rework" version is not requested
            else:
                music_url = music_searched.watch_url
                break

        else:
            # no music passed through the filters
            if len(music_searched) > 0: music_url = musics_searched[0].watch_url # if no music found : choose the first
            else: music_url = None

        # break if a music is found
        if music_url is not None: break

    # check search and return music url
    if music_url is None:
        raise Exception(f"Music '{music_searched["title"]}' give no results on Youtube !")

    return music_url


# download a playlist of musics
def download_musics_from_youtube(musics:dict[list[dict]], path_download_dir, numbered_names=True):
    """Download a playlist of musics from youtube (from list of urls or music names)."""

    # enumerate musics
    log.info(f"start downloading playlist to \"{path_download_dir}\"")
    nb_musics = len(musics)
    musics_download_cnt = 0

    try:
        for music in musics:
            # find music url
            pbar(musics_download_cnt, nb_musics, text=f"searching '{music["title"]}' ...")
            url_music = search_music_on_youtube(music)

            # create new name
            name_prefix = f"{musics_download_cnt} - " if numbered_names else ""
            
            # download music from url
            pbar(musics_download_cnt, nb_musics, text=f"downloading '{music["title"]}' ...")
            download_url_from_youtube(url_music, path_download_dir, name_prefix)

            # update download musics count
            musics_download_cnt += 1

    except Exception as err:
        return False, f"({type(err).__name__}: {err})"            
    except KeyboardInterrupt:
        return False, "(KeyboardInterrupt)"
    
    # hide text
    pbar(musics_download_cnt, nb_musics)

    # if no error occured
    return True, None


# download a playlist of musics and actualize changes
def actualize_playlist(playlist:dict):
    """download a playlist of musics and actualize changes"""
    pass

    # check "to_download" and "to_remove", "to_move"

    result, err_txt = download_musics_from_youtube(playlist["data"], playlist["download_dir"])
