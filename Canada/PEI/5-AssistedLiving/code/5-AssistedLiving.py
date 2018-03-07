from subprocess import call
import sys
import os

old_dir = os.getcwd()
module_name = "5-AssistedLiving"
path_to_script = sys.argv[0][:-len(module_name + ".py")]

os.chdir(path_to_script + "../../../../pqcq_scrapy")
call(["scrapy", "crawl", module_name, "-o", "../" + path_to_script + "../output/" + module_name + ".csv"])
os.chdir(old_dir)
