import scrapy
import os, sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

module_name = "43-NursingHomes"
sys.path.insert(0, os.path.abspath(sys.argv[0][:-len(module_name + ".py")] + "../../../../.."))

from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.USA43NursingHomes import USA43NursingHomes
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.USA43NursingHomesB import USA43NursingHomesB
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.USA43NursingHomesC import USA43NursingHomesC
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.USA43NursingHomesD import USA43NursingHomesD
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.USA43NursingHomesE import USA43NursingHomesE
from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.USA43NursingHomesF import USA43NursingHomesF

path_to_script = sys.argv[0][:-len(module_name + ".py")]
output_filename = path_to_script + "../output/" + module_name + ".csv"

settings = get_project_settings()
settings.set('FEED_FORMAT', 'csv',priority='cmdline')
settings.set('FEED_URI', output_filename, priority='cmdline')

with open(output_filename, 'w') as f:
	f.write('')
	f.close()

process = CrawlerProcess(settings)
process.crawl(USA43NursingHomes)
process.crawl(USA43NursingHomesB)
process.crawl(USA43NursingHomesC)
process.crawl(USA43NursingHomesD)
process.crawl(USA43NursingHomesE)
process.crawl(USA43NursingHomesF)
process.start()

with open(output_filename, 'r') as f:
	lines = f.readlines()
	f.close()

with open(output_filename, 'w') as f:
	for line in lines:
		if line is lines[0] or line != "name,license_num,licensure_status,care_level,owner,number_of_floors,number_of_suites,size_of_suites,facilities,services,website,contact,phone,cell,fax,email,participation,ownership_type,number_of_beds,council_type,facility_type,street_address,po_box,city,province,postal_code,country" + "\n":
			f.write(line)