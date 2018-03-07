CSV columns definitions

 - Numéro au permis / License Number
 - Nom légal / Legal Name
 - Nom abrégé / Short Name
 - Adresse / Address
 - Case postale / PO Box (Nullable)
 - Municipalité / Municipality
 - Code postal / Postal Code
 - Téléphone / Phone
 - Région sociosanitaire / Health Region
 - Territoire C.L.S.C. / Territory CLSC
 - M.R.C.
 - Circ. électorale provinciale / Circ. Provincial Election
 - Services au permis / Licensing Services
 - Télécopieur / Fax (Nullable)
 - Dir. général	/ Dir. General (Nullable)
 - Président du C.A. / Chairman of the Board (Nullable)
 - Commissaire aux plaintes et à la qualité des services / Complaints and Quality of Service Commissioner
 - Statut / Status
 - Loi / Law
 - Mode de constitution / Incorpporation	
 - Mission(s)
 - Désignation ministérielle / Ministerial designation	
 - Instance locale / Local authority
 - Mode de financement / Funding method	

*Note*

1. Empty directory 'regions', 'establishments' and 'installations' under 'input' directory are required prior to running the script
2. Some of the fax number uses an invalid code (000) 000-0000 to represent null

Scraping Process

1. download landing page
2. parse_region
3. download_establishments
3. download_installations
4. parse_directory
5. Looking for csv in output folder
