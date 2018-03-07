import scrapy
import os, sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

module_name = "95-ResidentialCare"
sys.path.insert(0, os.path.abspath(sys.argv[0][:-len(module_name + ".py")] + "../../../../.."))

from scrapers.pqcq_scrapy.pqcq_scrapy.spiders.LA95ResidentialCareSpider import LA95ResidentialCareSpider

path_to_script = sys.argv[0][:-len(module_name + ".py")]
output_filename = path_to_script + "../output/" + module_name + ".csv"

settings = get_project_settings()
settings.set('FEED_FORMAT', 'csv',priority='cmdline')
settings.set('FEED_URI', output_filename, priority='cmdline')

with open(output_filename, 'w') as f:
	f.write('')
	f.close()

process = CrawlerProcess(settings)
process.crawl(LA95ResidentialCareSpider)
process.start()
