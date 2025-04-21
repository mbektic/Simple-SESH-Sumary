# How you want to rank the songs.
#      True: Ranked on how long you time listened to each Artist/Song/Album.
#            When True, the script ignores the `MIN_MILLISECONDS` value.
#     False: Ranked on how many times you listened to each Artist/Song/Album.
PLAYTIME_MODE = False


# Minimum number of milliseconds that you listened to the song.
#     Changing this will drastically alter the final counts.
MIN_MILLISECONDS = 20000


# Directory, or folder, on your computer where your Spotify json files are located.
#     Easiest method is to just put them in the sesh folder.
INPUT_DIR = "sesh"


# Name/path of the output file. If you don't change this it will be in the same folder
#     as this script with the name summary.html
OUTPUT_FILE = "summary.html"


# The number of items per table page.
ITEMS_PER_PAGE = 10


# If you want the result to be a dark theme or light
#      True: Dark Theme on
#     False: Dark Theme off
#     (See screenshots here: https://github.com/mbektic/Simple-SESH-Sumary)
DARK_MODE = True