import csv
import re
import os, sys

module_name = "49-All"
sys.path.insert(0, os.path.abspath(sys.argv[0][:-len(module_name + ".py")] + "../../../../.."))
path_to_script = sys.argv[0][:-len(module_name + ".py")]

from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.GenericOutput import get_blank_information
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.Parsers import parse_city_province_zip_code
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.common.Regexes import unit_street_regex, city_province_required_zip_code_regex, po_box_regex, phone_number_regex, street_address_regex

forbidden_entries = [
	"DIRECTORY OF LICENSED WISCONSIN NURSING HOMES - ALPHABETICAL BY COUNTY AND CITY",
	"STATE OF WISCONSIN", 
	'Tuesday, August 15, 2017',
	"Department of Health Services",
	"Page \d of \d",
	"PROVIDER/ADDRESS",
	"Wisconsin Department",
	"of Health Services",
	"Facility Name and Address",
	"Phone Number / Contact Person",
	"\*The Adult Day Care \(ADC\) facility directory is updated quarterly. It is possible that a facility's certification fee due date may appear to have passed since the directory was last",
	"updated, when in fact that facility's required fee has been paid and its certification has been renewed without this being reflected on the directory.",
	"\*The Adult Family Homey \(AFH\) directory is updated monthly. It is possible that a facility's license renewal fee due date may appear to have passed since the directory was last",
	"updated, when in fact that facility's required fee has been paid and its license has been renewed without this being reflected on the directory.",
	"\*The Community Based Residential Facility \(CBRF\) directory is updated monthly. It is possible that a facility's license renewal fee due date may appear to have passed since the",
	"directory was last updated, when in fact that facility's required fee has been paid and its license has been renewed without this being reflected on the directory.",
	"\*The Residential Care Apartment Complex \(RCAC\) directory is updated monthly. It is possible that a facility's license renewal fee due date may appear to have passed since the",
	"directory was last updated, when in fact that facility's required fee has been paid and its certification has been renewed without this being reflected on the directory.",
	"\*The Residential Care Apartment Complex \(RCAC\) directory is updated quarterly. It is possible that a facility's certification fee due date may appear to have passed since the"]

forbidden_entries_row_2 = [
	"Public Directory",
	"By County, City",
	"For Adult Day Care Facilities",
	"For Adult Family Home Facilities",
	"For Community-Based Residential Facilities",
	"Licensee Name and Phone",
	"Mailing Address"]

forbidden_entries_regex = [re.compile(entry) for entry in forbidden_entries]

def row_is_permissable(row):
	if row[-2] == "Owner, Ownership, Certification" or row[-3] == "Owner, Ownership, Certification":
		return False

	if row == [''] * len(row):
		return False

	for regex in forbidden_entries_regex:
		if regex.search(row[0]):
			return False
	
	for entry in forbidden_entries_row_2:
		if row[1] == entry or row[2] == entry:
			return False

	return True

with open(path_to_script + '../output/49-NursingHomes.csv', 'w') as csv_output:
	with open(path_to_script + '../input/nh-ALL.csv', 'r') as csv_input:
		csv_reader = csv.reader(csv_input)
		csv_writer = csv.writer(csv_output)
		info = get_blank_information()
		csv_writer.writerow(info.keys())
		row_number = 0
		for row in csv_reader:
			if row_is_permissable(row):
				print(str(row) + " " + str(row_number))
				if row_number == 0:
					row_number += 1
					info["name"] = row[0]
					info["phone"] = row[1]
					info["dqa_region"] = row[2]
					info["license_number"] = row[3].split('. ')[1]
					info["owner"] = row[4] if row[4] != "" else row[5]
				elif row[2] == "" and row_number == 1:
					info["name"] = info["name"] + " " + row[0] if row[0] != "" else info["name"] 
					info["owner"] = info["owner"] + " " + row[4]
				elif row_number == 1:
					row_number += 1
					info["street_address"] = row[0]
					info["fax"] = row[1].split(': ')[1] if row[1] != "" else None
					info["dqa_region_category"] = row[2]
					info["license_level"] = row[3]
					info["ownership"] = row[4]
				elif row_number == 2:
					row_number += 1
					info = {**info, **parse_city_province_zip_code(row[0], province_required=True)}
					contact_info = row[1].split(': ') if row[1] != "" else row[2].split(': ')
					info["contact_occupation"] = contact_info[0]
					info["contact"] = contact_info[1]
					info["number_of_beds"] = row[3].split(' ')[0]
					info["provider_number"] = row[4]
					info["certification_types"] = row[5] if row[6] is "" else row[5] + "; " + row[6]

				if row_number == 3:
					info["province"] = "WI"
					info["country"] = "USA"
					info["type"] = "NH"
					csv_writer.writerow([info[key] for key in get_blank_information().keys()])
					info = get_blank_information()
					row_number = 0


name_license_num_regex = re.compile("(.+) \((\d{2}\d*)(\)?)")
list_of_specialties = [
	"ADVANCED AGED",
	"ALCOHOL/DRUG DEPENDENT",
	"CORRECTIONAL CLIENTS",
	"DEMENTIA/ALZHEIMER'S",
	"DEVELOPMENTALLY DISABLED",
	"EMOTIONALLY DISTURBED(/MENTAL|/MENTAL ILLNESS)?",
	"(MENTAL )?ILLNESS",
	"IRREVERSIBLE( DEMENTIA/ALZHEIMER'S)?",
	"PUBLIC FUNDING",
	"PHYSICALLY DISABLED",
	"TERMINALLY ILL",
	"TRAUMATIC BRAIN INJURY"]
gender_capacity_regex = re.compile("(?:Gender - Total Apartments:  )?(M/F|M|F)?(?: ?- ?)?(\d+)")
specialty_regex = re.compile("(" + "|".join(list_of_specialties) + ")")
date_regex = re.compile("\d\d?/\d\d?/\d{4}")
name_regex = re.compile("^([a-zA-Z]+\.?(-|/| / | & |   |  | )?)+$")
low_high_rate_regex = re.compile("(\d|,)+/(\d|,)+")
county_label = "County: "
type_regex = re.compile("(ADC|AFH|CBRF|NH|RCAC)")
class_regex = re.compile("(CNA)")

def get_row_information(info, row, row_number):
	if row_number == 0:
		for row_item in row:
			if info["name"] is None and name_license_num_regex.search(row_item) is not None:
				name_license_num_matches = name_license_num_regex.search(row_item)
				info["name"] = name_license_num_matches.group(1)
				info["license_num"] = name_license_num_matches.group(2) if name_license_num_matches.group(3) else None
			elif info["name"] is None and row_item == "OREGON AREA SENIOR CENTER'S ADULT DAY PROGRAMVILLAGE OF OREGON":
				info["name"] = "OREGON AREA SENIOR CENTER'S ADULT DAY PROGRAM"
				info["licensee_name"] = "VILLAGE OF OREGON"
			elif info["name"] is None and row_item == "MADISON AREA REHABILITATION CENTERS STOUGHTON":
				info["name"] = row_item
			elif info["name"] is None and row_item == "BROWN CO COMMUNITY TREATMENT CENTER BAY HAVEBROWN COUNTY COMMUNITY TREATMENT CEN":
				info["name"] = "BROWN CO COMMUNITY TREATMENT CENTER BAY HAVE"
				info["licensee_name"] = "BROWN COUNTY COMMUNITY TREATMENT CEN"
			elif info["type"] is None and type_regex.match(row_item):
				info["type"] = row_item
			elif info["licensee_name"] is None and name_regex.match(row_item) and specialty_regex.match(row_item) is None:
				info["licensee_name"] = row_item
			elif info["specialty_programs"] is None and specialty_regex.match(row_item):
				info["specialty_programs"] = row_item
	elif row_number == 1:
		for row_item in row:
			if info["po_box"] is None and po_box_regex.match(row_item):
				info["po_box"] = row_item
			elif info["street_address"] is None and (street_address_regex.search(row_item) or unit_street_regex.search(row_item)):
				info["street_address"] = row_item
			elif info["licensee_phone"] is None and phone_number_regex.search(row_item):
				info["licensee_phone"] = row_item
			elif info["class"] is None and class_regex.match(row_item):
				info["class"] = row_item
			elif specialty_regex.match(row_item):
				info["specialty_programs"] = info["specialty_programs"] + "; " + row_item if info["specialty_programs"] is not None else row_item
	elif row_number == 2:
			for row_item in row:
				if info["po_box"] is None and po_box_regex.match(row_item):
					info["po_box"] = row_item
				elif info['licensee_contact'] is None and name_regex.match(row_item) and specialty_regex.match(row_item) is None:
					print("licensee_contact " + row_item + " added")
					info['licensee_contact'] = row_item
				elif info["contact"] is None and name_regex.match(row_item) and specialty_regex.match(row_item) is None:
					print("licensee_name is " + info["licensee_name"])
					print("contact " + row_item + " added in row_number " + str(row_number))
					info["contact"] = row_item
				elif info['gender'] is None and info['number_of_beds'] is None and gender_capacity_regex.match(row_item):
					gender_capacity_matches = gender_capacity_regex.match(row_item)
					info['gender'] = gender_capacity_matches.group(1)
					info['number_of_beds'] = gender_capacity_matches.group(2)
				elif info["city"] is None and info["province"] is None and info["postal_code"] is None and city_province_required_zip_code_regex.match(row_item):
					info = {**info, **parse_city_province_zip_code(row_item, province_required=True)}
				elif specialty_regex.match(row_item):
					info["specialty_programs"] = info["specialty_programs"] + "; " + row_item
	elif row_number == 3:
			for row_item in row:
				if info["city"] is None and info["province"] is None and info["postal_code"] is None and city_province_required_zip_code_regex.match(row_item):
					info = {**info, **parse_city_province_zip_code(row_item, province_required=True)}
				elif info["phone"] is None and phone_number_regex.match(row_item):
					info["phone"] = row_item
				elif info["contact"] is None and name_regex.match(row_item) and specialty_regex.match(row_item) is None:
					print("contact " + row_item + " added in row_number " + str(row_number))
					info["contact"] = row_item
				elif info["county"] is None and row_item[:len(county_label)] == county_label:
					info["county"] = row_item[len(county_label):]
				elif info["po_box"] is None and po_box_regex.match(row_item):
					info["po_box"] = row_item
				elif info["licensee_street_address"] is None and (street_address_regex.search(row_item) or unit_street_regex.search(row_item)):
					info["licensee_street_address"] = row_item
				elif info["low_high_rate"] is None and low_high_rate_regex.match(row_item):
					info["low_high_rate"] = row_item
				elif specialty_regex.match(row_item):
					info["specialty_programs"] = info["specialty_programs"] + "; " + row_item
	elif row_number == 4:
		for row_item in row:
			if info["county"] is None and row_item[:len(county_label)] == county_label:
				info["county"] = row_item[len(county_label):]
			elif info["phone"] is None and phone_number_regex.match(row_item):
				info["phone"] = row_item
			elif info["contact"] is None and name_regex.match(row_item) and specialty_regex.match(row_item) is None:
				print("contact " + row_item + " added in row_number " + str(row_number))
				info["contact"] = row_item
			elif info["po_box"] is None and po_box_regex.match(row_item):
				info["po_box"] = row_item
			elif info["licensee_city"] is None and info["licensee_province"] is None and info["licensee_postal_code"] is None and city_province_required_zip_code_regex.match(row_item):
				licensee_address = parse_city_province_zip_code(row_item, province_required=True)
				info["licensee_city"] = licensee_address["city"]
				info["licensee_province"] = licensee_address["province"]
				info["licensee_postal_code"] = licensee_address["postal_code"]
				print("Licensee City/Province/Zip Code Detected! Set to " + str(licensee_address))
			elif info["initial_license"] is None and date_regex.match(row_item):
				info["initial_license"] = row_item
			elif specialty_regex.match(row_item):
				info["specialty_programs"] = info["specialty_programs"] + "; " + row_item
	elif row_number == 5:
		for row_item in row:
			if info["county"] is None and row_item[:len(county_label)] == county_label:
				info["county"] = row_item[len(county_label):]
			elif info["po_box"] is None and po_box_regex.match(row_item):
				info["po_box"] = row_item
			elif info["certification_fee_due"] is None and date_regex.match(row_item.replace(',', '')):
				info["certification_fee_due"] = row_item
			elif specialty_regex.match(row_item):
				info["specialty_programs"] = info["specialty_programs"] + "; " + row_item
	elif row_number == 6:
		if get_number_of_non_empty_strings_in_list(row) > 1:
			for row_item in row:
				if date_regex.match(row_item):
					info["license_renewal_fee_due"] = row_item
		elif get_number_of_non_empty_strings_in_list(row) == 1:
			for row_item in row:
				if specialty_regex.match(row_item):
					info["specialty_programs"] = info["specialty_programs"] + "; " + row_item
	return info

def get_number_of_non_empty_strings_in_list(str_list):
	return len([string for string in str_list if string != ""])

def if_info_attributes_arent_none_increment_i(info, attribute_list, alternate_attribute_list, i):
	if i < 6:
		for attribute in attribute_list:
			if info[attribute] == None:
				if alternate_attribute_list == []:
					return i
				else:
					for alt_attribute in alternate_attribute_list:
						if info[alt_attribute] == None:
							return i
					return i + 1
		return i + 1
	else:
		return i

def generic_csv_parsing(csv_input, csv_output, title_exceptions=[]):
	csv_reader = csv.reader(csv_input)
	csv_writer = csv.writer(csv_output)

	info = get_blank_information()
	csv_writer.writerow(info.keys())
	row_number = 0
	for row in csv_reader:
		if row_is_permissable(row):
			print(str(row) + " " + str(row_number))
			info = get_row_information(info, row, row_number)

			attribute_list = {
				0: ["name", "type"],
				1: ["street_address"],
				2: ["number_of_beds"],
				3: ["contact"],
				4: ["licensee_city"],
				5: ["county"]
			}.get(row_number, [])
			
			alternate_attribute_list = {
				3: ["low_high_rate"]
			} .get(row_number, [])

			row_number = if_info_attributes_arent_none_increment_i(info, attribute_list, alternate_attribute_list, row_number)

			if row_number == 6 and get_number_of_non_empty_strings_in_list(row) > 2:
				for row_item in row:
					if name_license_num_regex.search(row_item) or row_item in title_exceptions:
						print("row_item " + row_item + " got in!")
						info["country"] = "USA"
						csv_writer.writerow([info[key] for key in get_blank_information().keys()])
						info = get_blank_information()
						row_number = 0
						info = get_row_information(info, row, row_number)
						row_number += 1

with open(path_to_script + '../output/49-AdultDayCare.csv', 'w') as csv_output:
	with open(path_to_script + '../input/ad-ALL.csv', 'r') as csv_input:
		title_exceptions = ["OREGON AREA SENIOR CENTER'S ADULT DAY PROGRAMVILLAGE OF OREGON", 'MADISON AREA REHABILITATION CENTERS STOUGHTON']
		generic_csv_parsing(csv_input, csv_output, title_exceptions)


with open(path_to_script + '../output/49-AdultFamilyHome.csv', 'w') as csv_output:
	with open(path_to_script + '../input/afh-ALL.csv', 'r') as csv_input:
		generic_csv_parsing(csv_input, csv_output)

with open(path_to_script + '../output/49-CommunityBasedResidentialFacility.csv', 'w') as csv_output:
	with open(path_to_script + '../input/cbrf-ALL.csv', 'r') as csv_input:
		title_exceptions = ["BROWN CO COMMUNITY TREATMENT CENTER BAY HAVEBROWN COUNTY COMMUNITY TREATMENT CEN"]
		generic_csv_parsing(csv_input, csv_output, title_exceptions)

with open(path_to_script + '../output/49-ResidentialCareApartmentComplex.csv', 'w') as csv_output:
	with open(path_to_script + '../input/rcac-ALL.csv', 'r') as csv_input:
		generic_csv_parsing(csv_input, csv_output)
