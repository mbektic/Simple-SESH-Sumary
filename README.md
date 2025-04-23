# Simple-SESH-Summary
Generates a simple HTML page from your Spotify extended streaming history just by telling it where the directory is.

Example page [mbektic.com/SESH](https://mbektic.com/SESH/)

## Before you start
 - If you want to get a copy of your Spotify extended streaming history, you can get it [HERE](https://www.spotify.com/us/account/privacy/)
 - I wrote this using python 3.11.6, but any recent version of python _should_ work.


## Running
 - Run the script using `python.exe .\GenerateHTMLSummary.py`  
   - A gui like the one below will pop up. 
   - ![Image](https://github.com/user-attachments/assets/9a3a6dba-8583-4624-af91-2e94e6166606)
 - After altering the settings to your liking, click "Generate Summary"
   - You should get a confirmation screen like so, clicking "Open Report" _should_ open it in your web browser.
   - ![Image](https://github.com/user-attachments/assets/9804fe5d-7e23-4a8d-a02e-528ede041b65)
   - The file will have generated in the same folder as the script if you wish to revisit it later.
   - After opening the page, you can switch between playtime and play count as well as theme by clicking the settings button at the top right of the page.
     - ![Image](https://github.com/user-attachments/assets/8aadf1ed-289b-4e0b-95bd-a3e9b2928084)
 - If you wish to change the default settings, they are found in the `Config.py` file.
   - You can also run the script like so `python.exe .\GenerateHTMLSummary.py True`
   - It will skip the GUI and just generate the report with the values in `Config.py`


## IMPORTANT NOTES
- When you first open the HTML page, it can take a few seconds to load depending on how many years of history you have.
  - For example, with 10 years of history mine sometimes takes 2–3 seconds. 
- The resulting `.html` file can be shared without any of the other scripts or style files as everything is all built into it.
- None of your data ever leaves your system or is uploaded anywhere, this all stays on your machine.

## Images
### Artist (Dark Mode and Play Time)


### Tracks (Dark Mode and Play Time Mode True)
![Image](https://github.com/user-attachments/assets/a2b84762-d564-44f0-90c4-3235670fb64a)

### Albums (Light Mode and Play Time Mode False)
![Image](https://github.com/user-attachments/assets/40cc2892-69db-4ca8-b669-429ac6042b0e)

### Search
![Image](https://github.com/user-attachments/assets/c35b0412-c7da-4acb-9202-6736c198a3ca)