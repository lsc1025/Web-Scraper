CSV columns definitions

 - Facility Name
 - Region
 - Address Line 1
 - Address Line 2 (Nullable)
 - City
 - Province/State Code
 - Postal Code/Zip
 - Primary Phone Number
 - Secondary Phone Number (Nullable)
 - Fax Number
 - Language
 - Approved Spaces

*Note*

1. Empty directory 'regions' and 'details' under 'input' directory are required prior to running the script
2. Some of the phone/fax number doesn't come with an area code

Scraping Process

1. download landing page
2. parse_region
3. download_details
4. parse_direction
5. Looking for csv in output folder
