Normalizer:
A universal script to normalize, sanitize and organize the output of scrapers.

Pre-production steps:
First, we need to extract all the column names from all the scrapers, decide on a master column list, See https://stackoverflow.com/questions/17246563/opening-all-files-in-a-directory-for-csv-and-reading-each-line-python for some help

Processing Pipeline Summary:
1) Check field names of input CSV (first row) and change them to standardized format and organization/order (i.e. every output file should have the same first row after this stage)

2) For each field, define a normalization pipeline. Things to consider inlcude:
- All Caps versus Camel Case versus all lowercase
- Address & Phone number formatting
- what to put in a blank field (i.e. replacing N/A with nothing)
- Stripping whitespace before and after values
- Field that contains reference to the scraper used
- Field that contains generic information about the whole list (i.e. some lists only contain nursing homes, but that information isn't contained as a field in the output.csv file )
- Method of referencing a parent/child relationship for a home (i.e. one org. can open and operate multiple homes) 

3) Step through all "mandatory" fields for each row that are null (i.e. longitude and latitude), use a 3rd party API to populate their values

...3) Figure out a way to deal with de-duplication of rows

4) setup Drupal import function