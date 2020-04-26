#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 13:19:52 2020

@author: RileyBallachay
"""
import pandas as pd
from Import_Booklist import GoogleSheetsReader
from betterreads import client
from os import path
  
class AccessGoodReads:
    
    # This function initializes the class with the 
    # Google Sheet info and stores all the input keys for 
    # GoodReads locally. Also takes the name of the CSV
    # as an output.
    def __init__(self,ID,RANGE,OUT):
        self.api_key = '3C0gT4Ultg3Rmn5zPaBA'
        self.api_secret = 'yaHyn17KtUCl6HQgkZQEHcQJg81XF7qicVS6GvA7A3Q'
        self.oauth_token='kfRoaAgMT8dZwHUNjO8rw'
        self.oauth_signature='%2BZVIsFfCJNsSb2D50haCpIePlRg%3D'       
        self.SPREADSHEET_ID = ID
        self.RANGE_NAME = RANGE
        self.OutputFile = OUT
        
        self.__authClient()
    
    # Calling the GoodReads client and authenticating using tokens
    def __authClient(self):
        self.gc = client.GoodreadsClient(self.api_key,self.api_secret)
        self.gc.authenticate(self.oauth_token,self.oauth_signature)
    
    # Function which uses authenticated client to load GoodReads info.
    # Takes two parameters, one which chooses whether or not to load the 
    # data from CSV and the other to choose if we want to save it to CSV.
    def loadGoodReads(self,savetocsv=True,loadfromCSV=True): 
    
        if not loadfromCSV or not path.exists(self.OutputFile):
            # Read Google Sheet and pass into pandas dataframe
            Sheet = GoogleSheetsReader(self.SPREADSHEET_ID,self.RANGE_NAME)
            self.df = Sheet.gsheet2df()
        
            print('Dataframe size = ', self.df.shape)
            print(self.df.head())
            
            # Iterates over each of the rows in the dataframe and fills the 
            # Goodreads ID, description, rating and Num ratings. This is then
            # saved to an output CSV file. 
            for index, row in self.df.iterrows():
               
                try:
                    book = self.gc.book(isbn=row['ISBN13'])
                    self.df.loc[index,'Goodreads ID'] = book.gid
                    self.df.loc[index,'Description'] = book.description
                    self.df.loc[index,'Rating'] = book.average_rating
                    self.df.loc[index,'Num Ratings'] = book.ratings_count
                    self.df.loc[index,'Pages'] = book.num_pages
                    
                except:
                    print('Trouble processing', row['Title'])
            
            if savetocsv:
                self.__saveDataFrame()
        
        else:
            self.df = pd.read_csv(self.OutputFile)
        
        self.df.Score = pd.to_numeric(DF.Score)

        return self.df

    # Function which saves to a CSV file at the name OutputFile
    def saveDataFrame(self):
        self.df.to_csv(self.OutputFile)
    
    # Iterates over each row in the dataframe and checks if the number of pages
    # is an available input. If not, it determines that the info isn't populated,
    # so it fills in all the empty areas.
    def populateEmpty(self):
        
        self.loadGoodReads()
        
        for index,row in self.df.iterrows():
            
            if pd.isnull(row['Pages']):
                books = self.gc.search_books(row['Title'])
                
                # Iterates over the first ten search results, and asks the user
                # if it is the correct book title.
                for i in range(0,10):
                    isTitle = input('Is this the correct title? (y/n)\n'+str(books[i])+'\n')
                    if isTitle=='y':
                        self.df.loc[index,'ISBN13'] = books[i].isbn13
                        self.df.loc[index,'Author'] = books[i].authors
                        self.df.loc[index,'Pages'] = books[i].num_pages
                        self.df.loc[index,'Goodreads ID'] = books[i].gid
                        self.df.loc[index,'Description'] = books[i].description
                        self.df.loc[index,'Rating'] = books[i].average_rating
                        self.df.loc[index,'Num Ratings'] = books[i].ratings_count
                        print(row)
                        break
                    else:
                        print('Trying the next book in the search list')
                    
            self.saveDataFrame()
        
        return self.df
        
SPREADSHEET_ID = '1OwfIKyqPnVan0Ab8H7ztstXxqfu-wI4oFnds_AUoP-4'
RANGE_NAME = 'A1:I3000'

AGR = AccessGoodReads(SPREADSHEET_ID,RANGE_NAME,'Final Data.csv')
DF = AGR.loadGoodReads()
DF = AGR.populateEmpty()
