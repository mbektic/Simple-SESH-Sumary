# Simple-SESH-Sumary
Generates a simple HTML page from you Spotify extended streaming history just by telling it where the directory.

## Before you start
 - If you want to get a copy of your Spotify extended streaming history you can get it [HERE](https://www.spotify.com/us/account/privacy/)
 - I wrote this with python 3.11.6, but any recent version of python _should_ work.

## Parameters
At the top of the `GenerateHTMLSumary.py` script you can alter these parameters to your liking.
#### Minimum number of milliseconds that you listened to the song. Changing this can drastically alter counts
`MIN_MILLISECONDS = 20000`
#### Directory where your json files are, easiest method is to just drop them in the sesh folder.
`INPUT_DIR = "sesh"`
#### Name/path of the output file. if you don't change this it will be in the same folder as this script with the name summary.html
`OUTPUT_FILE = "summary.html"`
#### The number of items per table page.
`ITEMS_PER_PAGE = 10`

## Running
 - Just run the script using `python.exe .\GenerateHTMLSummary.py`  
   - You should see the response `✅ HTML report generated: summary.html`
 - After that just open the `summary.html` file or whatever you named it

![Image](https://github.com/user-attachments/assets/32bd114e-822e-42bd-8b07-69e143ef10e6)


## IMPORTANT NOTES!!!!
- When you first open the html page it will take a few seconds to render pagination (the multiple pages for tables). Just wait until you see the page update and everything will work smoothly.
- None of your data ever leaves your system or is uploaded anywhere, this all stays on your machine.


### Artist
![Image](https://github.com/user-attachments/assets/1ed71a9b-3fc3-4d64-b755-ed837a5c4d10)

### Tracks
![Image](https://github.com/user-attachments/assets/f8c87a13-ab21-486a-8722-b0c674c812b3)

### Albums
![Image](https://github.com/user-attachments/assets/e21120d1-32be-467d-8089-36e91f15eb5f)



### Conclusion/Rambling
This originally started with me trying to upload historic data to last.fm, but since you cant scrobble anything older than two weeks, and I didn't want to mess up the dates on my music, I decided against that. Anyway, I might add more to this if anyone actually uses it but who knows.

[My Last.fm, Say hi!](https://www.last.fm/user/Mbektic)