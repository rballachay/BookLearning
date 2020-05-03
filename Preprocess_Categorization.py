#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 15:32:35 2020

@author: RileyBallachay
"""
import numpy as np
import re
from nltk.corpus import stopwords

class PreCategorize:
    
    """Init function which takes the dataframe as
    an input and performs all required operations.
    Only other public function exists to return the
    dataframe which is processed by this function."""
    def __init__(self,df):
        self.stop_words = set(stopwords.words('english'))
        self.df = df
        self.df.Description = df.Description.apply(self.__remove_text_inside_brackets)
        self.df = self.__strip_string(self.df)
        self.df['Publication Date'] = df['Publication Date'].apply(self.__publication_year)
        self.__keyword_search()
        
    """Returns the processed dataframe to the user"""
    def processedDF(self):
        return self.df
     
    """This function takes a list of words from a sentence 
    and removes all commonly used words, known as 
    'stop words' from the list, returning a new list"""
    def  __drop_stop_words(self,listofwords):
        
        splitString = []
        for string in listofwords:
            if string not in self.stop_words:
                splitString.append(string)
        
        return splitString
    
    """ Some of the text contains information inside of 
    <> brackets. This function removes the brackets and
    everything contained within them. After that, it 
    removes special characters and removes 'stop words',
    which are commonly used English words."""
    def __remove_text_inside_brackets(self,text, brackets="<>",):
        count = [0] * (len(brackets) // 2) # count open/close brackets
        saved_chars = []
        
        # Exception hanlder if the book description
        # returns nan, prints warning
        try:
            for character in text:
                for i, b in enumerate(brackets):
                    if character == b: # found bracket
                        kind, is_close = divmod(i, 2)
                        count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                        if count[kind] < 0: # unbalanced bracket
                            count[kind] = 0  # keep it
                        else:  # found bracket to remove
                            break
                else: # character is not a [balanced] bracket
                    if not any(count): # outside brackets
                        saved_chars.append(character)
        except: 
            print("This Book Doesn't Have a Description!!!")
         
        string = ''.join(saved_chars)
        
    
        finalString = " ".join(re.findall(r"[a-zA-Z0-9]+", string))
        finalString = re.sub(r'\b\w{1,2}\b', '', finalString).split()

        splitString = self.__drop_stop_words(finalString)
        
        return splitString
    
    """Don't want to repeat the title or authors in the book 
    description, so this function removes those words from the 
    description. The function then converts every word to 
    lowercase and drops stop words."""
    def __strip_string(self,df):
        
        for index, row in df.iterrows():
            dropList = row['Author'].split() + row['Title'].split()
            dropList = [re.sub('\W+','', string ) for string in dropList]
            
            try:
                returnList = [x for x in row['Description'] if x not in dropList]
                returnList  = [x.lower() for x in returnList]
            except:
                print("This Book Doesn't Have a Description!!!")

            splitString = self.__drop_stop_words(returnList)       
            df.at[index,'Description'] = splitString
        
        return df
    
    """Converts the publication date from YYYY-MM-DD format
    to a YYYY format. Replaces empty cells with np.nans in 
    cases where the publication date isn't supplied"""
    def __publication_year(self,date):
        
        try:
            year = date[:4]
        except:
            year = np.nan
        
        return year
    
    def __check_keys(self,keys):
        
        returnArray =[]
        for description in self.descriptions:
            minilist = [x for x in description if x in keys]
            if len(minilist)>0:
                returnArray.append(minilist)
            else:
                returnArray.append(np.nan) 
        
        return returnArray
        
    """Function which searches for certain keywords in the 
    description and returns a new column which contains the
    keyword based on the category. Contains functions for 
    Awards, Bestselling and humorous"""
    def __keyword_search(self):
        self.descriptions = self.df.Description
        
        # This portion of the code tests to see if any of 
        # the key prizes are contained in the description
        prizes = ['pulitzer','award','nobel']
        prizeArray = self.__check_keys(prizes)
        
        # This portion of the code tests to see if the words
        # in bestsell are contained, or if they are contained
        # as two separate strings in sequence. 
        bestsell = ['bestselling','bestseller']
        sellerArray = self.__check_keys(bestsell)       
        
        for index,description in enumerate(self.descriptions):
            for subindex,string in enumerate(description):
                if string=='best':
                    if description[subindex+1] in['selling','seller']:
                        if ~np.isnan(sellerArray[index]):
                            sellerArray[index].append('best seller')
                        else:
                            sellerArray[index] = ['best seller']
            
        # This portion of the code checks to see if any of the following 
        # indicators of humor are provided in the description
        funnyWords = ['humor','comic','hilarious','funny','comical','humorous',
                      'satire','satirical','witty','hysterical','absurd']
        funnyArray = self.__check_keys(funnyWords)   
        
        # This portion of the code checks if any of the descriptors 
        # of dark, gloomy, sad etc.
        darkWords = ['dark','sad','heart','deep','melancholic','sorrow','gloomy',
                     'low','blue','woe','miserable','sadness','glum','profound',
                     'moving']
        darkArray = self.__check_keys(darkWords)
        
        intelligentWords = ['smart','intellectual','intelligent','scholar',
                            'clever','bright','sharp','apt','astute']
        smartArray = self.__check_keys(intelligentWords)

        self.df['Awards'] = prizeArray
        self.df['Bestselling'] = sellerArray
        self.df['Humorous'] = funnyArray
        self.df['Moving'] = darkArray
        self.df['Intelligent'] = smartArray
        
        return  