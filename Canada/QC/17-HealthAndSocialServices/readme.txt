CSV columns definitions

 - Num�ro au permis / License Number
 - Nom l�gal / Legal Name
 - Nom abr�g� / Short Name
 - Adresse / Address
 - Case postale / PO Box (Nullable)
 - Municipalit� / Municipality
 - Code postal / Postal Code
 - T�l�phone / Phone
 - R�gion sociosanitaire / Health Region
 - Territoire C.L.S.C. / Territory CLSC
 - M.R.C.
 - Circ. �lectorale provinciale / Circ. Provincial Election
 - Services au permis / Licensing Services
 - T�l�copieur / Fax (Nullable)
 - Dir. g�n�ral	/ Dir. General (Nullable)
 - Pr�sident du C.A. / Chairman of the Board (Nullable)
 - Commissaire aux plaintes et � la qualit� des services / Complaints and Quality of Service Commissioner
 - Statut / Status
 - Loi / Law
 - Mode de constitution / Incorpporation	
 - Mission(s)
 - D�signation minist�rielle / Ministerial designation	
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
