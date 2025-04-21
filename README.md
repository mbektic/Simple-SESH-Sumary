# Simple-SESH-Sumary
Generates a simple HTML page from you Spotify extended streaming history just by telling it where the directory.

Example page [mbektic.com/SESH](https://mbektic.com/SESH/)

## Before you start
 - If you want to get a copy of your Spotify extended streaming history you can get it [HERE](https://www.spotify.com/us/account/privacy/)
 - I wrote this using python 3.11.6, but any recent version of python _should_ work.

![Image](https://github.com/user-attachments/assets/bdbe03ff-fc2f-45aa-afb1-e548a675f36a)

## Running
 - Just run the script using `python.exe .\GenerateHTMLSummary.py`  
   - A gui like the one below will pop up. 
   - ![Image](https://github.com/user-attachments/assets/bdbe03ff-fc2f-45aa-afb1-e548a675f36a)
 - After altering the settings to your liking, click "Generate Summary"
   - You should get a confirmation screen like so, clicking "Open Report" _should_ open it in your web browser.
   - ![Image](https://github.com/user-attachments/assets/9804fe5d-7e23-4a8d-a02e-528ede041b65)
   - The file will have generated in the same folder as the script, if you wish to revisit it later.
 - If you wish to change the default settings they are found in the `Config.py` file.
   - You can also run the script like so `python.exe .\GenerateHTMLSummary.py True`
   - It will skip the GUI and just generate the report with the values in `Config.py`


## IMPORTANT NOTES
- When you first open the html page it can take a few seconds to render pagination (the multiple pages for tables). Just wait until you see the page update and everything will work smoothly.
- The resulting `.html` file can be shared without any of the other scripts or style files as everything is all built into it.
- None of your data ever leaves your system or is uploaded anywhere, this all stays on your machine.

## Images
### Artist (Dark Mode and Play Time Mode False)
![Image](https://github.com/user-attachments/assets/6f6a0e29-e55f-4653-a7a8-5347242712be)

### Tracks (Dark Mode and Play Time Mode True)
![Image](https://github.com/user-attachments/assets/1f762850-4ee1-4fd5-94c3-5a9f47f70cef)

### Albums (Light Mode and Play Time Mode False)
![Image](https://github.com/user-attachments/assets/d895f6ea-8a90-4c9f-9ed6-f7753bc59cb7)

### Search
![Image](https://github.com/user-attachments/assets/4f78775f-5420-4ff8-be78-3fcacc7c8fe6)