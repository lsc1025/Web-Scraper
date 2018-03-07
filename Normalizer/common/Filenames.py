import glob

canada_original_csv_filenames = "Canada/*/*/output/*.csv"
usa_original_csv_filenames = "USA/*/*/output/*.csv"

normalized_csv_filenames = '2-FinalizedData/*-NORMALIZED.csv'

download_original_csv_filenames = "./*.csv"

back_folder = "../"

#sample_csv_filename = "Normalizer/" + back_folder + 'USA/AK/70-AK-AssistedLiving/output/output.csv'
#sample_csv_filename = "Normalizer/" + back_folder + 'Canada/AB/27-AB-SupportiveLiving/output/output.csv'
#sample_csv_filename = "Normalizer/" + back_folder + 'Canada/ON/1-ON-AssistedLiving/output/output.csv'
sample_csv_filename = "Normalizer/" + back_folder + 'Canada/AB/28-AB-ContinuingAndLongTermCare/output/output.csv'

tmp_normalized_csvs = "2-FinalizedData/*-TMP.csv"

source_file_csvs = "1-ConsolidatedData/*.csv"

def get_mappings():
	return [
	'contact_column_mappings.csv',
	'type_column_mappings.csv',
	'specialization_column_mappings.csv',
	'cost_column_mappings.csv',
	'lat_long_column_mappings.csv',
	'description_column_mappings.csv',
	'administative_column_mappings.csv',
	'address_column_mappings.csv']

def generate_normalized_filename(filename, output_to_tmp=False):
	csv_filename_split = filename.split('/')
	return '2-FinalizedData/' + csv_filename_split[2] + "-" + csv_filename_split[3] + "-" + csv_filename_split[4] + "-" + csv_filename_split[6][:-4] + ("-NORMALIZED.csv" if not output_to_tmp else "-NORMALIZED-TMP.csv")

def get_blacklisted_original_csvs(path_to_script, back_folder):
	return [
	path_to_script + back_folder + 'USA/National/42-NursingHomes/output/Deficiencies_Download.csv',
	path_to_script + back_folder + 'USA/National/42-NursingHomes/output/Ownership_Download.csv',
	path_to_script + back_folder + 'USA/National/42-NursingHomes/output/Penalties_Download.csv',
	path_to_script + back_folder + 'USA/National/42-NursingHomes/output/ProviderInfo_Download.csv',
	path_to_script + back_folder + 'USA/National/42-NursingHomes/output/QualityMsrClaims_Download.csv',
	path_to_script + back_folder + 'USA/National/42-NursingHomes/output/QualityMsrMDS_Download.csv',
	path_to_script + back_folder + 'USA/National/42-NursingHomes/output/State_Averages_Download.csv',
	path_to_script + back_folder + 'USA/NY/46-NursingHomes/output/46-NursingHomes.csv']

def get_csv_filenames(path_to_script, get_original=True):
	can_output_filenames = glob.glob(canada_original_csv_filenames) # if get_original else canada_normalized_csv_filenames)
	usa_output_filenames = glob.glob(usa_original_csv_filenames)# if get_original else usa_normalized_csv_filenames)
	normalized_output_filenames = glob.glob(normalized_csv_filenames)
	all_filenames = (can_output_filenames + usa_output_filenames) if get_original else normalized_output_filenames
	all_filenames = list(map((lambda filename: path_to_script + back_folder + filename), all_filenames))

	blacklisted = get_blacklisted_original_csvs(path_to_script, back_folder)

	return [filename for filename in all_filenames if not filename in blacklisted]

def get_csv_download_filenames(path_to_script, get_original=True):
	download_filenames = glob.glob(download_original_csv_filenames)
	return download_filenames

def get_csv_sample_filenames(path_to_script, get_original=True):
	normalized_filename = generate_normalized_filename(sample_csv_filename)
	return [sample_csv_filename if get_original else normalized_filename]

def get_tmp_normalized_csvs(path_to_script):
	return [path_to_script + back_folder + filename for filename in glob.glob(tmp_normalized_csvs)]

def get_normalized_geo_equivalent(filename):
	return '0-GeoData/' + filename.split('/')[-1]

def get_source_files_equivalent(filename):
	return '1-ConsolidatedData/' + filename.split('/')[-1]

def get_source_files_filenames(path_to_script):
	return [path_to_script + back_folder + filename for filename in glob.glob(source_file_csvs)]