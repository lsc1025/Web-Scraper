import re

def expr_list_of_options(list_of_options):
	return '(' + '|'.join(list_of_options) + ';?)+'

def compile_list_of_options(list_of_options):
	return re.compile(expr_list_of_options(list_of_options))

alzhemers_care_regex = compile_list_of_options([
	"Alzheimer's Care"])

assisted_living_regex = compile_list_of_options([
	'ASSISTED LIVING.*',
	'Assisted ?Living(.*)',
	'ALF?P?',
	'Retirement Home',
	'SUPPORTIVE HOUSING - RETIREMENT HOMES.*',
	'Supportive Living.*',
	'Combined Living',
	'Special Care Homes',
	"Special Care Home",
	'Adult Family( Care)? Home',
	'AFH',
	'AH',
	'EHP',
	'Shelter Care Home', 
	'Personal Care Home', 
	'Shelter Care',
	'ARCP', 
	'Adult Residential Care', 
	'shelter Care',
	"RCFE-CONTINUING CARE RETIREMENT COMMUNITY",
	"RESIDENTIAL CARE & HOSPICES - .+",
	'RCAC',
	'Community Care',
	'Community Based Residential Facility',
	'Community Living Arrangements',
	'CBRF',
	'Supportive Living Accomodation'])

congregate_living_regex = compile_list_of_options([
	"Coopérative d'habitation"])

continuing_care_regex = compile_list_of_options([
	'RESIDENTIAL CARE ELDERLY',
	'RCF',
	"(Adult )?Residential( Health)? Care( Facility)?",
	"RHCF",
	"Continuing Care"])

dementia_care_regex = compile_list_of_options([
	'SS',
	'DU',
	'ALP/D',
	'Care Bed Services',
	'Dementia Care'])

home_care_and_hospice_regex = compile_list_of_options([
	"RESIDENTIAL CARE & HOSPICES - .+",
	'Home Care.*',
	'^Home.*',
	'HP'])

independent_living_regex = compile_list_of_options([
	"Independent Living",
	'Combined Living'])

memory_care_regex = compile_list_of_options([
	'Memory Care'])

nursing_care_regex = compile_list_of_options([
	"NH",
	"Nursing Home",
	"Free Standing NF/SNF",
	"Free Standing NF",
	"Free Standing SNF",
	"NF",
	"LTCU",
	"NURSING",
	"Nursing Facility",
	"Long(-| )(T|t)erm Care( Accomm?odation)?"])

skilled_nursing_regex = compile_list_of_options([
	"SNF/NF"])

fifty_five_plus_community_regex = compile_list_of_options([
	"Senior(s')? Apartments",
	"Senior Housing",
	"Transitional Living Facility",
	"CBO",
	"EHP"])

adult_day_care_regex = compile_list_of_options([
	'Adult Day( Care)?( Center)?( Support Program)?',
	'ADC',
	'Day Care services'])

type_of_care_regex_map = {
	"Active Lifestyle": None,
	"Alzheimer’s Care": None,
	"Assisted Living": assisted_living_regex,
	"Congregate Living": congregate_living_regex,
	"Continuing Care": continuing_care_regex,
	"Dementia Care": dementia_care_regex,
	"Golf Communities": None,
	"Home Care and Hospice": home_care_and_hospice_regex,
	"Independent Living": independent_living_regex,
	"Manufactured Homes": None,
	"Memory Care": memory_care_regex,
	"Nursing Care": nursing_care_regex,
	"Personal Care": None,
	"Rehabilitation Care": None,
	"Respite": None,
	"Skilled Nursing": skilled_nursing_regex,
	"55+ Community": fifty_five_plus_community_regex,
	"Adult Day Care": adult_day_care_regex
}

def get_types_of_care(data_list):
	new_data_list = []
	for data in data_list:
		returned_type_of_care = get_type_of_care(data.strip())
		if returned_type_of_care != None and returned_type_of_care not in new_data_list:
			new_data_list.append(returned_type_of_care)
	return ';'.join(new_data_list)

def get_type_of_care(data):
	types_of_care = []
	for (key, value) in type_of_care_regex_map.items():
		if value != None and value.search(data):
			types_of_care.append(key)
	result = ';'.join(types_of_care) if len(types_of_care) > 0 else None
	return result