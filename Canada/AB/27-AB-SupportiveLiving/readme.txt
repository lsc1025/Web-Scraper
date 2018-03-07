CSV columns definitions

 - Accommodation Name
 - Address Line 1
 - City
 - Postal Code/Zip
 - Province/State Code
 - Accommodation Type
 - Number of Units
 - Funding Source
 - Operator
 - Phone
 - Fax
 - Last Visit Date
 - Last Visit Type
 - Original Issue Date
 - Licence Issue Date
 - Licence Expiry Date
 - Licence Type
 - ASL Facility ID

*Note*

1. Empty directory 'details' under 'input' directory is required prior to running the script
2. Some of the facilities do not have postal code or license related data 

Scraping Process

1. download json from /ibi_apps/WFServlet?IBIAPP=public_reporting&IBIF_ex=search.fex&xform=wf_xmlr_to_json_datatable
3. download_details
4. parse_directory
5. Looking for csv in output folder