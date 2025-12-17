# Download MusicMe Playlists

This project is created for extract a playlist from [MusicMe](https://www.musicme.com/) and download his equivalent on [Youtube](https://www.youtube.com/) with python.

## Small Disclaimer

Be careful, YouTube does not allow you to download music by any means other than their services. I will not be responsible for your actions, if you use this code, at your own risk ! To download musics from Youtube, you must also check the laws of your country so as not to violate them by downloading music !

## Features

- [x] Extract a MusicMe playlist
- [x] Download a playlist of musics (from MusicMe) in Youtube
- [ ] Actualizes changes of a playlist downloaded (added, moved or removed music)

## Requirements

- python3

## Installation

Install python requirements

``` shell
python -m pip install -r requirements.txt
```

## Usage

### Use a list of playlist urls to download from musicme

- Create the file "data/musicme_playlists/playlists.txt" and put into all urls (separated by line break) of the musicme playlists (like 'https://www.musicme.com/#/playlist/3x41x64') that you want to download

### Run the main program

``` shell
python main.py
```
