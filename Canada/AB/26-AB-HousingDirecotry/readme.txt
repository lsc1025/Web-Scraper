CSV columns definitions

 - Facility Name
 - Address Line 1
 - City
 - Postal Code/Zip
 - Province/State Code
 - Terms of Occupancy
 - Housing Type
 - Number of Units
 - Eligibility Criteria
 - Application Procedure
 - Additional Criteria
 - Minimum Rate $
 - Maximum Rate $
 - RGI Rent Rate
 - Service Package Rate
 - Unit Square Footage Minimum
 - Unit Square Footage Maximum
 - Additional Suite Information
 - Additional Suite Features
 - Additional Services
 - Additional Building Information
 - List of booleans: (Stored in the python list formate i.e.[True, False])
    - Priority Rating
    - Pets Allowed
    - Smoking Allowed
    - Studio/Bachelor
    - 1 Bedroom
    - 2 Bedroom
    - 3 Bedroom
    - Damage Deposit Required
    - Rent Geared to Income (RGI)
    - Kitchenette
    - Wheel Chair Accessible Suites
    - Emergency Response System
    - In-Suite Laundry Equipment
    - Meals Available
    - Snacks and Beverages
    - Personal Laundry
    - Specialized Dementia Care
    - 24 Hour Hospitality Staff
    - 24 Hour Health Care Staff
    - Wheelchair Accessible Building
    - Security System
    - Elevator
    - Parking
    - Scooter Parking/Garage
    - On-Site Laundry
 - Site Contact Name
 - Site Phone
 - Site Email
 - Facebook
 - Twitter
 - Site Website
 - Site Description

*Note*

1. Empty directory 'pages' and 'details' under 'input' directory are required prior to running the script
2. Some of the facilities do not have a postal code

Scraping Process

1. download landing page
2. parse_pages
3. download_details
4. parse_directory
5. Looking for csv in output folder

*Row 641 has an invalid data in its site phone column, consider remove it manually*