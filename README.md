# Simple-SESH-Sumary
Generates a simple HTML page from you Spotify extended streaming history just by telling it where the directory.

## Before you start
 - If you want to get a copy of your Spotify extended streaming history you can get it [HERE](https://www.spotify.com/us/account/privacy/)
 - I wrote this with python 3.11.6, but any recent version of python _should_ work.

## Options
At the top of the `GenerateHTMLSumary.py` script you can alter these options to your liking.
#### How you want to rank the songs. If True, it will base the rankings on how long you listened to the track/artist/album. This also ignores the `MIN_MILLISECONDS` FLAG
`PLAYTIME_MODE = True` or `PLAYTIME_MODE = False`
#### Minimum number of milliseconds that you listened to the song. Changing this can drastically alter counts
`MIN_MILLISECONDS = 20000`
#### Directory where your json files are, easiest method is to just drop them in the sesh folder.
`INPUT_DIR = "sesh"`
#### Name/path of the output file. if you don't change this it will be in the same folder as this script with the name summary.html
`OUTPUT_FILE = "summary.html"`
#### The number of items per table page.
`ITEMS_PER_PAGE = 10`
#### If you want the result to be styled with darker colors. (See screenshots on the GitHub page)
`DARK_MODE = False`

## Running
 - Just run the script using `python.exe .\GenerateHTMLSummary.py`  
   - You should see the response `✅ HTML report generated: summary.html`
 - After that just open the `summary.html` file or whatever you named it

![Image](https://github.com/user-attachments/assets/32bd114e-822e-42bd-8b07-69e143ef10e6)


## IMPORTANT NOTES!!!!
- When you first open the html page it will take a few seconds to render pagination (the multiple pages for tables). Just wait until you see the page update and everything will work smoothly.
- The resulting `summary.html` file can be shared without any of the other scripts or style files as it is all built into it.
- None of your data ever leaves your system or is uploaded anywhere, this all stays on your machine.


### Artist (Dark Mode True and Play Time Mode False)
![Image](https://github.com/user-attachments/assets/3612d0f4-74de-4663-99ee-438bd32670d6)

### Tracks (Dark Mode True and Play Time Mode True)
![Image](https://github.com/user-attachments/assets/49c5aaa3-c603-456a-a890-f0784ab3e8cf)

### Albums (Dark Mode False and Play Time Mode False)
![Image](https://github.com/user-attachments/assets/b295dcd5-7980-497d-86a5-56f3608e1e9f)


### Conclusion/Rambling
This originally started with me trying to upload historic data to last.fm, but since you cant scrobble anything older than two weeks, and I didn't want to mess up the dates on my music, I decided against that. Anyway, I might add more to this if anyone actually uses it but who knows.

[My Last.fm, Say hi!](https://www.last.fm/user/Mbektic)