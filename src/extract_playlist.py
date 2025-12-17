#---------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# Python: 3.12
# Author: Killian Nallet
# Date: 21/05/2025
#---------------------------------------------------------------------------------


# imports
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver


# configure logger
log = logging.getLogger("__main__")


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
    log.info("init webdriver")
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--log-level=1")
    _webdriver = webdriver.Chrome(options=opts)


# extract playlist from html
def _html_extract_in_logged(soup:BeautifulSoup):
    """Extract the playlist from a html like a musicme (logged page)"""

    #NOTE: this function is used when the user is logged on musicme website and use a htmlfile

    # find a div with the playlist title
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


def _html_extract_in_not_logged(soup:BeautifulSoup):
    """Extract the playlist from a html like a musicme (not logged page)"""
    
    # find a div with the playlist title
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
def _extract_playlist_from_html(html_playlist:str):
    """Extract the titles, authors in a playlist of musics from musicme website"""  

    # load html playlist with beautiful soup
    log.info(f"extracting playlist from html")
    soup = BeautifulSoup(html_playlist, 'html.parser')

    #NOTE: if the user are logged on musicme website, a different page (of the playlist) is displayed
    not_logd_div = soup.body.find( # if are in logged, playlist data is stored in a div with 'playlist' id
        'div', attrs={'class':'tracks-container'}
    )
    html_musicme_is_logged = True if not_logd_div is None else False

    # extract playlist
    playlist, playlist_name = _html_extract_in_logged(soup) if html_musicme_is_logged else _html_extract_in_not_logged(soup)

    # return playlist
    return playlist, playlist_name


def extract_playlist_from_url(url_playlist:str):
    """Extract the titles, authors in a playlist of musics from musicme website"""

    # init webdriver (chrome)
    _init_webdriver()

    try:
        # load url
        _webdriver.get(url_playlist)
        time.sleep(2) # sleep a little
        
        # switch src html to iframe 'frmmain' which contain playlist data
        _webdriver.switch_to.frame(_webdriver.find_element("id", "frmmain"))
    
    # error
    except Exception as err:
        raise type(err) (str(err).split("\n")[:1][0]) # raise the same Exception but with some lines removed

    # extract playlist from html and return this
    log.info(f"extracting html from musicme ({url_playlist})")
    return _extract_playlist_from_html(_webdriver.page_source)
