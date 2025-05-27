#---------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# Python: 3.12
# Author: Killian Nallet
# Date: 21/05/2025
#---------------------------------------------------------------------------------

# imports
import os
from bs4 import BeautifulSoup
from selenium import webdriver


# init webrother driver
_webdriver = None

def _init_webdriver():
    """Initialise a Chrome webdriver and return this"""
    #NOTE: chrome webdriver is closed with the program
    global _webdriver
    
    # check if the webdriver isn't initialized
    if _webdriver is not None:
        return

    # init the webdriver
    print("Init webdriver ...")
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    _webdriver = webdriver.Chrome(options=opts)


# extract playlist from html
def _html_extract_in_logged(soup:BeautifulSoup, playlist_name=None):
    """Extract the playlist from a html like a musicme (logged page)"""

    # find a div with the playlist title
    if playlist_name is None: # if playlist name not gived
        playlist_name = soup.body.find('div', attrs={'class':'plmenutxt'}).text

    # find the playlist data div
    playlist_div = soup.body.find('div', attrs={'id':'playlist'})

    # find musics in the soup
    nb_musics = 0
    playlist = []

    while True:
        # try to find a div with the content of the music
        music_div = playlist_div.find('div', attrs={'class':'trk', 'id':f'trk-{nb_musics}'})

        # if the music div exists
        if music_div is not None:
            # find metadata of this music
            music_title = music_div.find(
                'div', attrs={'class':'trktitle cell txtcell'}
            ).text
            
            music_authors = music_div.find(
                'div', attrs={'class':'trkart cell txtcell'}
            ).text.split(" / ")

            # append music to playlist
            playlist.append({"id": nb_musics, "title":music_title, "authors":music_authors, "downloaded": None})

            # actualize musics count
            nb_musics += 1

        # if next music not found : break the loop and return this playlist
        else:
            break
    
    # check playlist length
    if len(playlist) == 0:
        raise Exception(f"The playlist '{playlist_name}' extracted is empty !")

    # return the playlist
    return playlist, playlist_name


def _html_extract_in_not_logged(soup:BeautifulSoup, playlist_name=None):
    """Extract the playlist from a html like a musicme (not logged page)"""
    
    # find a div with the playlist title
    if playlist_name is None: # if playlist name not gived
        playlist_name = soup.body.find('h1', attrs={'class':'album-name'}).text

    # find the playlist data div
    playlist_div = soup.body.find('div', attrs={'class':'tracks-container'})

    # find musics in the soup
    nb_musics = 0
    playlist = []

    while True:
        # try to find a div with the content of the music
        music_div = playlist_div.find('tr', attrs={'data-airplay-index':f'{nb_musics}'})

        # if the music div exists
        if music_div is not None:
            # find metadata of this music
            music_title = music_div.find(
                'td', attrs={'class':'trktnm'}
            ).text.strip()

            music_authors = []
            for author_lnk in music_div.find('td', attrs={'class':'trktart'}).find_all('a'):
                music_authors.append(author_lnk.attrs["href"].split("/")[1])

            # "," " / " or "-X-" separate the authors in text
            contrl_chr = "%$%"
            authors_txt = contrl_chr.join(music_authors)
            authors_txt.replace(",", contrl_chr)
            authors_txt.replace(" / ", contrl_chr)
            authors_txt.replace("-X-", contrl_chr)
            music_authors = authors_txt.split(contrl_chr)

            # append music to playlist
            playlist.append({"id": nb_musics, "title":music_title, "authors":music_authors, "downloaded": None})

            # actualize musics count
            nb_musics += 1

        # if next music not found : break the loop and return this playlist
        else:
            break

    # check playlist length
    if len(playlist) == 0:
        raise Exception(f"The playlist '{playlist_name}' extracted is empty !")

    # return the playlist
    return playlist, playlist_name


# extract playlist
def _extract_playlist_from_html(html_playlist:str, playlist_name:str=None):
    """Extract the titles, authors in a playlist of musics from musicme website"""  

    # load html playlist with beautiful soup
    soup = BeautifulSoup(html_playlist, 'html.parser')

    #NOTE: if the user are logged on musicme website, a different page (of the playlist) is displayed
    not_logd_div = soup.body.find( # if are in logged, playlist data is stored in a div with 'playlist' id
        'div', attrs={'class':'tracks-container'}
    )
    html_musicme_is_logged = True if not_logd_div is None else False

    # extract playlist
    if html_musicme_is_logged:
        playlist, playlist_name = _html_extract_in_logged(soup, playlist_name)
    else:
        playlist, playlist_name = _html_extract_in_not_logged(soup, playlist_name)

    # return playlist
    return playlist, playlist_name


def extract_playlist_from_htmlfile(html_playlist_path:str):
    """Extract the titles, authors in a playlist of musics from musicme website"""

    # get name by name
    playlist_basename = os.path.basename(html_playlist_path)
    playlist_name = os.path.splitext(playlist_basename)[0]

    # format the html for bs4
    with open(html_playlist_path, "r", encoding="utf-8") as r_file:
        html_playlist = r_file.read()

    # format the html_playlist (with 'body' like a html)
    html_playlist = f"""<!doctype html><html><body><div id="playlist">{html_playlist}</div></body></html>"""

    # extract playlist from html and retur this
    return _extract_playlist_from_html(html_playlist, playlist_name)


def extract_playlist_from_url(url_playlist:str):
    """Extract the titles, authors in a playlist of musics from musicme website"""

    # init webdriver (chrome)
    _init_webdriver()

    try:
        # load url
        _webdriver.get(url_playlist)
        
        # switch src html to iframe 'frmmain' which contain playlist data
        _webdriver.switch_to.frame(_webdriver.find_element("id", "frmmain"))
    
    # error
    except Exception as err:
        raise type(err) (str(err).split("\n")[:1][0]) # raise the same Exception but with some lines removed

    # extract playlist from html and return this
    return _extract_playlist_from_html(_webdriver.page_source)
