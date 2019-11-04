#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This program is to take a plain text file
# and to write the contents into a databasefile 'example.db'
# This program assumes that a plain text file is being read

# structure of the file is as follows:
#

import os
import sys
import sqlite3

class Database(object):
    """
    The Database Wrapper for all operations needed for
    the selenium scraper (AhsayACB system)

    author: David E.Crowley BSc Computer Science @ UCC
    email: davidcrowley1990 at gmail dot com
    """

    def __init__(self, name=None):
        """The constructor of the Database class.
        Args:
            name: name of database file.
            functional parameter assigned None as default.
        """
        self.conn         = None
        self.cursor       = None
        self.filename     = 'employees_info.txt'
        self.database     = "employees.db"
        self.employee_lst = []

        if name:
            self.open(name)

    def open(self):
        """Manually opens a new database connection.
        The database can also be opened in the constructor
        or as context manager.
        """
        try:
            self.conn = sqlite3.connect(self.database)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as error:
            print("Error connecting to database!")


    def get(self, table, columns, limit=None):
        """Function to fetch/query data from a database.
        Args:
            table: the given table you want to do operations with
            columns: the given columns you will be operating on
            limit: default None param used in list comprehension generator
        """
        query = "Select {0} FROM {1};".format(columns, table)
        self.cursor.execute(query)
        # Fetch data
        rows = self.cursor.fetchall()

        return rows[len(rows)-limit if limit else 0:]

    def write(self, table, columns, data):
        """Function to write data to the database."""
        query = "INSERT INTO {0} ({1}) VALUES ({2});".format(table, columns, data)
        self.cursor.execute(query)

    def get_employee_from_alias(self, alias):
        """function to return firstname, lastname with a given alias."""
        # If we are confident in getting a certain result, we can use fetchone()
        # we add [0] at the end since fetch*() methods always return a sequence
        # Even though the query only returns a single item
        employee = []
        self.cursor.execute("""SELECT first_name, last_name FROM employees WHERE id=?""", (alias,))
        data = self.cursor.fetchall()
        for row in data:
            employee.append(row)

        return employee

    def query(self, sql):
        """Function to query any other SQL statement."""
        return self.cursor.execute(sql)

    def close(self):
        """Close database connection and commit last execution. """
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def create_table(self, table_name):
        """Function to create a table with given table_name parameter"""
        try:
            self.cursor.execute("""CREATE TABLE employees (id, first_name, last_name)""")
            print("Success, table does not already exist. Creating record now.")
        except sqlite3.DataError as e:
            print("[!] create_table : Exception Caught -> ", e)

    def create_table_auto_increment(self):
        """Function to create a table using Primary Key."""
        try:
            self.cursor.execute('''CREATE TABLE employees 
                                    (id varchar(50) PRIMARY KEY, 
                                    first_name varchar(50) NOT NULL, 
                                    last_name varchar(50) NOT NULL)''')
            print("Success, table does not already exist. Creating record now.")
        except sqlite3.Error as error:
            print("[!] create_table_auto_increment : Exception caught -> {}".format(error))

    def insert(self, alias, firstname, lastname):
        """Insert values into three rows of a table"""
        try:
            self.cursor.execute("""INSERT OR IGNORE INTO employees 
                (id, first_name, last_name) values(?, ?, ?)""", 
                (alias, firstname, lastname))
        except sqlite3.Error as error:
            print("[!] create_table_auto_increment : Exception caught -> {}".format(error))

    def print_table(self, table, verbose=True):
        """Function to show the rows of the table specified in arg."""
        if verbose:
            for row in self.cursor.execute("SELECT * FROM {0}".format(table)):
                print(row)
        else:
            print("NON VERBOSE : print_table")

    def print_table_row_count(self, table, verbose=True):
        """Function to show the number of rows currently in the table."""
        if verbose:
            self.cursor.execute("SELECT count() FROM {0}".format(table))
        else:
            print("NON VEROSE : table_row_count")

    def split_lines_in_file(self):
        """Open a file and split contents on each line."""
        with open(self.filename, 'r') as db_file:
            contents = db_file.read()
        list_of_lines = [line.split('\t') for line in contents.split('\n')[1:]]
        
        return list_of_lines

    def populate_db_with_file(self):
        """While there is a connection, populate database."""
        with self.conn:
            employees = self.split_lines_in_file() # returns list
            self.cursor.execute("PRAGMA cache_size= -512")
            for employee in employees:
                if employee == ['']:
                    print('\n Empty Tuple Found; Skipping.\n')
                    continue
                for information in employee:
                    split_employees = information.split(' ')
                    self.employee_lst.append(split_employees)
            for employee_info in self.employee_lst:
                print(employee_info)
                self.cursor.execute("""INSERT OR IGNORE INTO employees VALUES (?,?,?);""",
                    (employee_info[0],employee_info[1],employee_info[2]))

    def delete(self, verbose=True):
        """Function to delete an entire table, use with caution."""
        if verbose:
            for row in self.cursor.execute("DELETE FROM employees"):
                print(row)

    def __enter__(self):
        """Returns self so that other methods of the class can be called
        on the context
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Makes sure tha the db connection gets closed
        """
        self.close()

    def create_database(self):
        """Use this function to create a fresh database."""
        print("[!] Creating Database")
        #db = Database()
        db.open()
        db.create_table_auto_increment()
        db.populate_db_with_file()
        db.print_table("employees")
        db.close()

# Uncomment below to create and populate new DB
#if __name__ == "__main__":
    #db = Database()
    #db.create_database()