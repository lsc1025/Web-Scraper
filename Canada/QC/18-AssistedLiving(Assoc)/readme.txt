CSV columns definitions

 - Facility Name (Facility ID)
 - Adresse / Address
 - City (Region)
 - Code postal / Postal Code
 - T�l�phone / Phone
 - Province
 - Nom de la compagnie / Nom des exploitants / Company Name / Name of operators (Multiple)
 - Nombre d'unit�s locatives dans l'immeuble / Number of rental units in the building
 - Nombre d'unit�s locatives dans la r�sidence priv�e pour a�n�s / Number of rental units in private residence for seniors
 - Type de r�sidence / Type of residence
 - Ann�e d'ouverture / Year of opening
 - Date de prise de possession / Date of possession
 - Date de mise � jour / Updated on
 - Membre d'une association / Member of an association (Multiple)
 - Certification Date de d�livrance / Certification Date of issue 
 - Services offerts / Offered services (Multiple)
 - Lien vers Informations compl�tes sur la r�sidence / Complete residence information (Link)

*Note*

1. Empty directory 'details' under 'input' directory are required prior to running the script
2. Columns with multiple entries are stored in semicolon seprated format
3. The column Services offerts / Offered services consists of the fowllowing entries:
	- Repas / Meal
	- Soins infirmiers / Medical care
	- Assistance personnelle / Personal assistance
	- Aide domestique / Home help
	- Loisirs / Spare-time activities
	- S�curit� / Serurity

Scraping Process

1. download landing page
2. download_detail()
3. parse_directory()
4. Looking for csv in output folder
