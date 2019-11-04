"""
"""

# Prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

# io.open is needed for projects supporting Python 2.7
# ensures open() deafults to text mode with universal newline
#from io import open

here = path.abspath(path.dir_name(__file__))

# Get long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	# Name of the project. Name registers when package is published
	name='BackupScraper', #required
	version='1.2.0',
	description='A Custom Backups Scraper',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/DavidECrowley',
	author='David E Crowley',
	author_email='davidcrowley1990@gmail.com',

	)