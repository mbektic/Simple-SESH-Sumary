# Simple-SESH-Summary
Generates a simple HTML page from your Spotify extended streaming history just by telling it where the directory is.

Example page [mbektic.com/SESH](https://mbektic.com/SESH/)

## Before you start
 - If you want to get a copy of your Spotify extended streaming history, you can get it [HERE](https://www.spotify.com/us/account/privacy/)
 - I wrote this using python 3.11.6, but any recent version of python _should_ work.


## Running
 - Double click `GenerateHTMLSummary.py` or run the script via terminal using `python.exe .\GenerateHTMLSummary.py`  
   - A gui like the one below will pop up. 
   - ![Image](https://github.com/user-attachments/assets/0a23c2f8-5a51-46e6-a2c9-770fc4f90093)
   - Click browse and select the folder that contains your extracted JSON files.
   - After altering the settings to your liking, click "Generate Summary"
   - It will take a few seconds to generate the report, you can see the progress with the progress bar.
   - ![Image](https://github.com/user-attachments/assets/2b06553c-8a3a-4cec-8f26-cab54e7c10ba)
   - You should get a confirmation screen like so, clicking "Open Report" _should_ open it in your web browser.
   - ![Image](https://github.com/user-attachments/assets/9804fe5d-7e23-4a8d-a02e-528ede041b65)
   - The file will have generated in the same folder as the script if you wish to revisit it later.
   - After opening the page, you can switch between playtime and play count as well as theme by clicking the settings button at the top right of the page.
     - ![Image](https://github.com/user-attachments/assets/569ae55d-8d09-4141-bbbb-4539b9c6b3dc)
 - If you wish to change the default settings, they are found in the `config.py` file.
   - You can also run the script like so `python.exe .\GenerateHTMLSummary.py --skip-gui`
   - It will skip the GUI and just generate the report with the values in `config.py`
     - You will need to set the default directory in the `config.py`.


## IMPORTANT NOTES
- When you first open the HTML page, it can take a few seconds to load depending on how many years of history you have.
  - For example, with 10 years of history mine sometimes takes 2–3 seconds. 
- The resulting `.html` file can be shared without any of the other scripts or style files as everything is all built into it.
- None of your data ever leaves your system or is uploaded anywhere, this all stays on your machine.

## Images
### Year Selector
![Image](https://github.com/user-attachments/assets/0fa47626-5256-4a3e-a7cb-423226da9878)

### Artist (Dark Mode and Play Time)
![Image](https://github.com/user-attachments/assets/a2b84762-d564-44f0-90c4-3235670fb64a)

### Tracks (Light Mode and Play Count)
![Image](https://github.com/user-attachments/assets/40cc2892-69db-4ca8-b669-429ac6042b0e)

### Albums (Search)
![Image](https://github.com/user-attachments/assets/1a9ba192-1fc5-4cc6-b115-a5f57ebef6db)

### Stats
![Image](https://github.com/user-attachments/assets/d58bf131-180e-4bab-ab78-2ad2246ed5ca)
![Image](https://github.com/user-attachments/assets/bfa47186-ae50-4c73-a2b4-77e7fdf0b0db)
![Image](https://github.com/user-attachments/assets/29c716bd-3300-4ade-afdf-1f97cb6d92fd)