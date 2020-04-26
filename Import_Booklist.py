#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 17:24:12 2020

@author: RileyBallachay
"""

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import numpy as np
import pandas as pd
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsReader:

    def  __init__(self,ID,RANGE):
        """ Initializes the GoogleSheetsReader object with the ID, range and 
        raw gsheet read from Google Sheets.
        """
        self.ID = ID
        self.RANGE = RANGE

        # Call class to establish API credentials
        self.creds = self.__get_creds()
        
        # Call class to invoke GoogleSheetsReader API
        self.gsheet = self.__get_google_sheet()
    
    def __get_creds(self):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        logging.debug("Retrieve and Save credentials for GoogleSheetsReader API")
 
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds
    
    def __get_google_sheet(self):
        """Private module for loading the 
        google sheet from the given destination
        """
        creds = self.creds
        logging.debug("Initialize and Invoke GoogleSheetsReader API")

        # Initialize AAPI with credentials
        service = build('sheets', 'v4', credentials=creds)
    
        # Call the Sheets API
        sheet = service.spreadsheets()
        
        logging.debug("Getting Google Sheet from Provided Key Location")
        result = sheet.values().get(spreadsheetId=self.ID,
                                    range=self.RANGE).execute()
        return result
    
    def gsheet2df(self):
        """ Converts Google sheet data to a Pandas DataFrame.
        Note: This script assumes that your data contains a header file on the first row!
        Also note that the Google API returns 'none' from empty cells - in order for the code
        below to work, you'll need to make sure your sheet doesn't contain empty cells,
        or update the code to account for such instances.
        """
        logging.debug("Converting Google Sheet Into Pandas Format")

        header = self.gsheet.get('values', [])[0]   # Assumes first line is header!
        values = self.gsheet.get('values', [])[1:]  # Everything else is data.
        
        if not values:
            print('No data found.')
        else:
            all_data = []
            for col_id, col_name in enumerate(header):
                column_data = []
                for row in values:
                    try:
                        column_data.append(row[col_id])
                    except:
                        column_data.append(np.nan)
                ds = pd.Series(data=column_data, name=col_name)
                all_data.append(ds)
            df = pd.concat(all_data, axis=1)
        return df
        
 
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1OwfIKyqPnVan0Ab8H7ztstXxqfu-wI4oFnds_AUoP-4'
RANGE_NAME = 'A1:I3000'

# Read Google Sheet and pass into pandas dataframe
Sheet = GoogleSheetsReader(SPREADSHEET_ID,RANGE_NAME)
df = Sheet.gsheet2df()

print('Dataframe size = ', df.shape)
print(df.head())

