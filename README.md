# Simple-SESH-Sumary
Generates a simple HTML page from you Spotify extended streaming history just by telling it where the directory.

Example page [mbektic.com/SESH](https://mbektic.com/SESH/)

## Before you start
 - If you want to get a copy of your Spotify extended streaming history you can get it [HERE](https://www.spotify.com/us/account/privacy/)
 - I wrote this using python 3.11.6, but any recent version of python _should_ work.

## Options
In the `Config.py` file you can find configuration options and alter these options to your liking.

- `PLAYTIME_MODE = True`
  - How you want to rank the songs.
    -  True: Ranked on how long you time listened to each Artist/Song/Album. 
       - When True, the script ignores the `MIN_MILLISECONDS` value.
    - False: Ranked on how many times you listened to each Artist/Song/Album.

- `MIN_MILLISECONDS = 20000`
  - Minimum number of milliseconds that you listened to the song.
  - Changing this will drastically alter the final counts.

- `INPUT_DIR = "sesh"`
  - Directory, or folder, on your computer where your Spotify json files are located.
  - Easiest method is to just put them in the sesh folder.

- `OUTPUT_FILE = "summary.html"`
  - Name/path of the output file. If you don't change this it will be in the same folder
  - as this script with the name summary.html

- `ITEMS_PER_PAGE = 10`
  - The number of items per table page. 

- `DARK_MODE = False`
  - If you want the result to be a dark theme or light (See screenshots below)
    - True: Dark Theme on
    - False: Dark Theme off

## Running
 - Just run the script using `python.exe .\GenerateHTMLSummary.py`  
   - You should see the response `✅ HTML report generated: summary.html`
 - After that just open the `summary.html` file or whatever you named it

![Image](https://github.com/user-attachments/assets/32bd114e-822e-42bd-8b07-69e143ef10e6)


## IMPORTANT NOTES
- When you first open the html page it will take a few seconds to render pagination (the multiple pages for tables). Just wait until you see the page update and everything will work smoothly.
- The resulting `summary.html` file can be shared without any of the other scripts or style files as it is all built into it.
- None of your data ever leaves your system or is uploaded anywhere, this all stays on your machine.


### Artist (Dark Mode True and Play Time Mode False)
![Image](https://github.com/user-attachments/assets/cf98a426-ac6c-48b1-b21b-a53e35322d62)

### Tracks (Dark Mode True and Play Time Mode True)
![Image](https://github.com/user-attachments/assets/d575b7f9-7b61-43a5-9785-4a116a88ed50)

### Albums (Dark Mode False and Play Time Mode False)
![Image](https://github.com/user-attachments/assets/4cff5ae1-0ba6-409c-a7af-731958900921)


### Conclusion/Rambling
This originally started with me trying to upload historic data to last.fm, but since you cant scrobble anything older than two weeks, and I didn't want to mess up the dates on my music, I decided against that. Anyway, I might add more to this if anyone actually uses it but who knows.

[My Last.fm, Say hi!](https://www.last.fm/user/Mbektic)