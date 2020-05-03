#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 19:47:29 2020

@author: RileyBallachay
"""
import seaborn as sns
from Goodreads_Extension import AccessGoodReads
import matplotlib.pyplot as plt
import numpy as np

class VisualizeBookData:
    
    """Initialize the Visualize Book Class with the 
    Google Sheets info, the output CSV file name and the 
    boolean for loading the CSV from disk"""
    def __init__(self,ID,RANGE,OUT,loadfromCSV=True):
        self.SPREADSHEET_ID = ID
        self.RANGE_NAME = RANGE
        AGR = AccessGoodReads(self.SPREADSHEET_ID,self.RANGE_NAME,OUT)
        self.DF = AGR.loadGoodReads(loadfromCSV=loadfromCSV)
        self.DF['Net Month'] = self.__dateParser(self.DF['Date Read'])
        self.DF['Rating'] = self.DF['Rating']*2
    
    # Function for returning the dataframe after initialization    
    def getData(self):
        return self.DF
    
    """ Returns three different plots based on subjets. 
    The first of which plots the average book score by 
    category. The second plot shows the number of books 
    read in each book category."""
    def subjects(self):
        sns.set(style="darkgrid")
        sns.catplot(x='Topic',y='Score',data=self.DF,kind='violin',aspect=2)
        plt.show()
        
        count = self.DF.groupby('Topic').count().sort_values('Title', ascending=False)
        plt.figure(figsize=(10,5))
        plt.title('Books Read by Category')
        ax = sns.barplot(x=count.index,y=count.Title)
        ax.set(ylabel='Total Number of Books Read')
        plt.xticks(rotation=45)
        plt.show()
        
        sns.set(style="darkgrid")
        sns.catplot(x='Topic',y='Pages',data=self.DF,kind='violin',aspect=2)
        plt.show()        
        
        return self.DF

    """Returns three different plots based on time read
    data.The first plot contains the average Goodreads 
    and my rating for that month since 2017. The second
    plot is the average book length by month. The third 
    is the number of pages read by month and color coding
    for the season in which the reading comes."""
    def dates(self):
        sns.set(style="darkgrid")
        plt.figure(figsize=(12,5))
        sns.lineplot(x='Net Month',y='Score',data=self.DF,color='orange',label='My Rating')
        sns.lineplot(x='Net Month',y='Rating',data=self.DF,color='purple',label='Goodreads')
        plt.xlabel('Month Read')
        plt.xticks(rotation=45)
        plt.show()       
        
        plt.figure(figsize=(12,5))
        sns.lineplot(x='Net Month',y='Pages',data=self.DF,color='green')
        plt.xticks(rotation=45)
        plt.xlabel('Month Read')
        plt.show()          
        
        count = self.DF.groupby('Net Month', as_index=False).sum()
        plt.figure(figsize=(12,5))
        sns.lineplot(x='Net Month',y='Pages',data=count,color='black')
        
        datelist  = list(count['Net Month'])

        # For loop which adds month color coding to a list which is then
        # fed to the function axvspan
        for index,date in enumerate(datelist[:-1]):
            month = int(date[5:7])
            if month >=3 and month <=5:
                monthcolor = 'hotpink'
            elif month >=6 and month <=8:
                monthcolor = 'olive'
            elif month >=9 and month<=11:
                monthcolor = 'sienna'
            else:
                monthcolor = 'darkslategray'
            plt.axvspan(datelist[index],datelist[index+1], facecolor=monthcolor, alpha=0.25)
        plt.xticks(rotation=45)
        plt.xlabel('Month Read')
        plt.ylabel('Number of Pages Read')
        plt.show()         
        
        return self.DF
    
    """ Function which converts the date from format string 
    and year number to the format YYYY/MM/DD, where DD is 
    always 1 because it isn't specified by me in the Google
    sheet."""
    def __dateParser(self,dates):
        months = {'January' : 1,'February' : 2,'March' : 3,'April' : 4,'May' : 5,
            'June' : 6,'July' : 7,'August' : 8,'September' : 9, 'October' : 10,
            'November' : 11,'December' : 12}
        datelist=[]
        for date in dates:
            try:
                month,year = date.split()
                dateTime = str(year) + '/' 
                if len(str(months[month]))>1:
                    dateTime += str(months[month]) + '/' + '1'  
                else:   
                    dateTime += '0' + str(months[month]) + '/' + '1'
                
                datelist.append(dateTime)
            
            except:
                datelist.append(np.nan)  
        return datelist