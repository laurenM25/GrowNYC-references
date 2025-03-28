# Purpose
_Project started March 2025_\
To make operations more efficient for my work at GrowNYC, I decided to create a hub for materials I use often. One feature of this hub is a "seed look-up", where the user can search for a seed variety, obtain its image and QR code linking to the webpage about the variety, and the user will have the option to print a label sheet pdf in the dimensions of Avery 5160 30-count sheet.

## The Data Base

### Naming procedures
The seedList.txt file contains all seed varieties in the database. Each seed type occupies it's own line on the file, and specific varieties of that seed are separated by commas put after the generic name with a colon. For example:
- sunflower: autumn beauty, teddy bear

For easy access to photos and QR codes for each variety, the files will be named as such:
- {specific variety}{general}{QR/icon}, with hyphens in between each word. E.g., "black-cherry-tomato.jpg"
- The default will be Johnny's Seeds for QR codes unless otherwise specified.
- Use adobe to create QR codes: https://new.express.adobe.com/tools/generate-qr-code
- JPG files.

## Next steps
Next steps for pdf viewer:
- allow for user to edit the size of text on labels (dynamic css stylesheet)
- add in customize date and company, QR code vs plant photo (perhaps take to intermediary page or have pop-up to ask user for these decisions)
- maybe: allow user to specify other label sheet dimensions (not Avery 5160)
- maybe: allow user to specify number of labels needed (e.g., only 15 and not the full 30)
Next steps for seed info page:
- fix file upload, processing and saving the file.
