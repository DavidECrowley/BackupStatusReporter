#!/usr/bin/python3
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from table_creator import Database
from datetime import date, timedelta
from operator import itemgetter
from selenium import webdriver
from bs4 import BeautifulSoup
import argparse
from collections import defaultdict
import datetime
import hashlib
import sys
import os
import re
import time
from pprint import pprint

"""BackupScraper
    An automation tool designed to be used with the Ahsay Backup systems
    Reads in credentials from an external file.
    supports argparsing on command line

    Simple stuff
"""

class BackupScraper(object):

    BAKUP_ERROR   = "https:// REMOVED URL FOR SECURITY REASONS"
    RESTORED_FILE = "https:// REMOVED URL FOR SECURITY REASONS"
    MANAGED_USER  = ""
    USER_PROFILE  = ""
    BACKUP_SET    = ""
    STATISTICS    = ""

    def __init__(self):
        """Constructor for AhsayScraper class."""
        self.db = Database()
        self.URL = "https://REMOVED URL FOR SECURITY REASONS"
        self.link_text = "Backup Job"
        self.link_error = "Backup Error"
        self.file = args.file
        self.password = None
        self.driver = None
        self.full_name = ""
        self.row_data = {}
        self.table_dict = {}
        self.missed_lst = []
        self.error_lst = []
        self.new_lst = []

        
    def setupDriver(self):
        """Setup headless chrome driver for selenium."""
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")

        # trying to get rid of SSL cert issue on command line
        # but this doesnt seem to work when headless is active
        desired_capabilities = options.to_capabilities()
        desired_capabilities['acceptSslCerts'] = True
        desired_capabilities['acceptInsecureCerts'] = True
        
        self.driver = webdriver.Chrome(chrome_options=options, desired_capabilities = desired_capabilities,
                executable_path=os.path.abspath("C:/windows/chromedriver"))

    def setupfirefoxDriver(self):
        options = Options()
        options.set_headless(headless=True)
        self.driver = webdriver.Firefox(executable_path=r"C:/windows/geckodriver")
    
    def getCurrentDate(self):
        """Get the yesterday's date in yyyy-mm-dd format"""
        yesterday = date.today() - timedelta(1)
        print(yesterday)

    def getPageBackupError(self):
        """Get's the Backup Error page and opens it with the driver
        Used the hard link instead of partial text location due to the fact
        that switching frames is causing issues when also changing link clicks on selenium.
        """
        self.driver.get(BACKUP_ERROR)

    def getPageRestoredFile(self):
        """Gets the restored file page and opens it"""
        self.driver.get("REMOVED URL FOR SECURITY REASONS")

    def getPageManagedUser(self):
        """Gets managed users page"""
        self.driver.get(MANAGED_USER)

    def getPageUserProfile(self):
        """Gets users profile"""
        self.driver.get(USER_PROFILE)

    def getPageBackupSet(self):
        """Outputs the BackupSet to user"""
        self.driver.get(BACKUP_SET)

    def getPageStatistics(self): 
        """Gets page statistics"""
        self.driver.get(STATISTICS)

    def getPage(self):
        """Go to given URL."""
        self.driver.get(self.URL)

    def getCredentials(self):
        """ Gets password from stored file and saved to class attr."""
        with open(self.file, "r") as f:
            self.password = f.read()
        return self.password

    def switchFrame(self, frameNumber):
        """Switches frame, useful for jsp rendered pages."""
        self.driver.switch_to.frame(frameNumber)

    def clickPartialLink(self, text):
        """Finds a link and click's it."""
        self.driver.find_element_by_partial_link_text(text).click()

    def findElementAtXpath(self, xpath):
        element = self.driver.find_element_by_xpath(xpath)
        element.click()

    def systemLogin(self):
        """Access Login panel and submit credentials."""
        username = self.driver.find_element_by_name("systemLoginName")
        password = self.driver.find_element_by_name("systemPassword")
        submit = self.driver.find_element_by_name("submit")
        username.send_keys("fdc_admin")
        password.send_keys(self.password)
        submit.click()
        
    def createDictDataRestoredFile(self, rows):
        """Takes row data from HTML and reforms with dict type."""
        error_lst = [] # Local list for this funct

        for row in rows:
            headerTest = len(row.find_all('select'))
            hfTest = len(row.find_all('td', attrs={'class':'adminlog_field'}))
            if headerTest > 0 or hfTest > 0:
                continue
            #get data in row
            data = row.find_all('td', recursive=False)

            if "No" in str(data):
                print("-"*90)
                print(" "*35,"Restored File Report")
                print("-"*90)
                print("{:<3} {:<45} {:<13} {:<10} {:<5} {}"
                    .format('No.','Restore Time','Login Name', 'Owner', 'Size', 'IP'))
                print("[*] No files have been downloaded today.\n")
                ## SHOULD MOVE ON TO THE NEXT FUNCTION CALL HERE FOR THE NEXT PAGE
                return # We no longer need to run through this function

            # Parse out time data
            time_data = data[1].string.split(' - ')
            if len(time_data) >= 2:
                time_start = time_data[0]
                time_end = time_data[1]
            else:
                time_start = '???'
                time_end = '???'

            row_data = {}
            table_dict = {}
            row_data['number'] = data[0].string
            row_data['restore_time'] = data[1].string
            row_data['login_name'] = data[2].string
            row_data['owner'] = data[3].string
            row_data['size'] = data[4].string
            row_data['ip'] = data[5].string
            table_dict[ row_data['number'] ] = row_data

        print(table_dict)
        
        for m,n in table_dict.items():
            print(m, n)
            error_lst.append([m, n['restore_time'], 
                n['login_name'],
                n['owner'], 
                n['size'], 
                n['ip']])

        if not error_lst:
            # missed backup list is empty
            print("[*] No Error Reports today.")
        else:
            for error in error_lst:
                # for each list of reports within the error list, print the contents of each error list
                print("{:<3} {:<45} {:<13} {:<10} {:<5} {}".format(error[0], 
                    error[1], 
                    error[2], 
                    error[3], 
                    error[4], 
                    error[5]))
  
    def fixMalformedHTML(self, backup=False, restored=False):
        """Function to fix very specific malformed HTML table."""
        html = self.driver.page_source
        html = re.sub('<td>\s+<td valign="middle">', '<td valign="middle">', html, flags=re.I)
        html = re.sub('</td>\s+<td>', '</td>', html, flags=re.I)
        # Parse the (hopefully) not-busted HTML
        soup = BeautifulSoup(html, "html5lib")
        # Extract info from table rows..
        rows = soup.table.table.tbody.find_all('tr', recursive=False)
        
        if backup:
            self.createDictData(rows)
        elif restored:
            self.createDictDataRestoredFile(rows) # some new function here for doing 
        else:
            return None

    def createDictData(self, rows):
        """Takes row data from HTML and reforms with dict type."""
        for row in rows:
            # Test for header / footer / junk-data rows.
            headerTest = len(row.find_all('select'))
            hfTest = len(row.find_all('td', attrs={'class':'adminlog_field'}))

            if headerTest > 0 or hfTest > 0:
                continue
            # get the data in this row
            data = row.find_all('td', recursive=False)
            # Parse out time data..
            time_data = data[1].string.split(' - ')
            if len(time_data) >= 2:
                time_start = time_data[0]
                time_end = time_data[1]
            else:
                time_start = '???'
                time_end = '???'
            # Parse out login, job name & number..
            job_data = data[2].find_all('td')
            if len(job_data) >= 3:
                # Check for links as some types
                if job_data[0].string:
                    job_number = job_data[0].string
                else:
                    job_number = job_data[0].a.string
                login_name = job_data[2].string

               # print("[*] : ",job_data[4].a.string, "[*]", job_data[4].string)
                if job_data[4].string:
                    # cell doesn't have a link in the date-time
                    backup_name = job_data[4].string
                else:
                    # cell has a link for the date-time
                    backup_name = job_data[4].a.string
            else:
                job_number = '???'
                login_name = '???'
                backup_name = '???'

            # Create dictionary for rows
            row_data = {}
            row_data['number'] = data[0].string
            row_data['time_start'] = time_start
            row_data['time_end'] = time_end
            row_data['backup_set'] = login_name
            row_data['backup_date'] = backup_name.replace('\n','').strip()
            row_data['login_name'] = job_number
            row_data['owner_name'] = data[3].string
            row_data['client_version'] = data[4].string.replace('\n','').strip()
            row_data['size'] = data[5].string
            row_data['status'] = data[6].b.font.string
            self.table_dict[ row_data['number'] ] = row_data
        self.printBackupStates(self.table_dict)

    def printBackupStates(self, dictionary):
        """COPY FUNCTION FOR THE RESTORED FILE PRINTING AND FORMATTING, EASIER METHOD THIS ONE"""
        print("-"*90)
        print(" "*35,"Restored File Report")
        print("-"*90)
        # Sort the list based on the User index
        self.new_lst = sorted(self.missed_lst, key=itemgetter(1))
        print("{:<3} {:<17} {:<20} {:<15} {:<12} {}"
            .format('No.','Restore Time','Login Name', 'Owner', 'Size', 'IP'))
        for missed_backup in self.new_lst:
            self.full_name = self.db.get_employee_from_alias(missed_backup[1])
            if len(self.full_name) > 0:
                # A name was found matching that id e.g;(fdc_cas-012)
                for name in self.full_name:
                    # For each tupled name in the full_name list.
                    self.print_backup_choice(missed_backup, name, self.full_name)  


    def printBackupStates(self, dictionary):
        """A function to create simple formatted data with dictionary type objects."""
        self.db.open()
        for m,n in dictionary.items():
            for x,y in n.items():
                if y == str("Missed Backup"):
                    self.missed_lst.append([m, n['login_name'], n['backup_date'], n['time_start']])
                elif y == str("Error"):
                    self.error_lst.append([m, n['login_name'], n['backup_date'], n['time_start']])
        if not self.missed_lst:
            # missed backup list is empty
            print("[*] No Missed Backups")
        else:
            # missed backup list is not empty
            print("-"*90)
            print(" "*35,"Ahsay Missed Backups")
            print("-"*90)           
            # Sort the list based on the User index
            self.new_lst = sorted(self.missed_lst, key=itemgetter(1))
            print("{:<3} {:<17} {:<20} {:<15} {:<12} {}"
                .format('No.','User','Date & Backup Time', 'Time', 'Firstname', 'LastName'))
            for missed_backup in self.new_lst:
                self.full_name = self.db.get_employee_from_alias(missed_backup[1])
                if len(self.full_name) > 0:
                    # A name was found matching that id e.g;(fdc_cas-012)
                    for name in self.full_name:
                        # For each tupled name in the full_name list.
                        self.print_backup_choice(missed_backup, name, self.full_name)
        if self.error_lst:
            # if an error exists then the error_lst has data in it.
            # not printing error reports, just check vault1.providentit.com to find the user.
            print("[!] Errors have been found in the backups report. Check the Backup Job page.")


    def print_backup_choice(self, missed_backup, name, full_name):
        """Method to select print choice based on list length input."""
        if len(full_name) > 0:
            print("{:<3} {:<17} {:<20} {:<15} {:<12} {}".format(missed_backup[0], 
                                                            missed_backup[1],
                                                            missed_backup[2],
                                                            missed_backup[3],
                                                            name[0],
                                                            name[1]))
        else:   
            print("{:<3} {:<17} {:<20} {:<8}".format(missed_backup[0],
                                                missed_backup[1],
                                                missed_backup[2],
                                                missed_backup[3]))

    def close(self):
        self.db.close()
        self.driver.close()
        self.driver.quit()

if __name__ == "__main__":
    # Grab arguments when script is running
    parser = argparse.ArgumentParser(description="Make things happen.", epilog='Thanks for using Backup Scraper!')
    parser.add_argument('-f', '--file', help='File selected to be read in from', required=True)
    args = parser.parse_args() # assign arguments
    scraper = BackupScraper() # Create backupscraper object
    scraper.getCredentials()   # Read credentials from file
    scraper.getCurrentDate()
    scraper.setupDriver() # Setup the chrome driver
    scraper.getPage() # Serve the login page
    scraper.switchFrame(1) # Switching frames to access elements
    scraper.systemLogin() # Login to the system
    scraper.switchFrame(0)  
    scraper.clickPartialLink("Backup Job") # Click the Backup Job text/link
    scraper.switchFrame(1)
    scraper.fixMalformedHTML(True) # Start reading in and serving out data
    scraper.getPageRestoredFile()
    scraper.switchFrame(1)
    scraper.fixMalformedHTML(False, True) # Restored file reporter part of the program
                                          # we give it boolean to indicate that it's Report we are doing.
    scraper.close()





