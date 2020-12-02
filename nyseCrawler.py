import requests
import json
import time
import math
import random

EMPTY_RESPONSE = '[]'

class nyseCrawler:
    def __init__(self):
        self.url = "https://www.nyse.com/api/quotes/filter"
        self.headers = {'Connection': 'keep-alive', \
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36', \
                        'Content-Type': 'application/json', \
                        'Accept': '*/*', \
                        'Origin': 'https://www.nyse.com', \
                        'Sec-Fetch-Site': 'same-origin', \
                        'Sec-Fetch-Mode': 'cors', \
                        'Sec-Fetch-Dest': 'empty', \
                        'Referer': 'https//www.nyse.com/listings_directory/stock', \
                        'Accept-Language': 'en-US,en;q=0.9'\
                        }
        self.data = '{{"instrumentType":"EQUITY","pageNumber":{0},"sortColumn":"NORMALIZED_TICKER","sortOrder":"ASC","maxResultsPerPage":10,"filterToken":""}}'
        self.tickerDict = {}

    # Wrapper around requests.post to handle exceptions for timeouts
    # input: 
    #       currentPageNumber : page to request from https://www.nyse.com/listings_directory/stock
    # Return:
    #       response : response from site or None if timed out
    def sendHTTPRequestForTickerSymbols(self,currentPageNumber):
        response = None
        try:
            response = requests.post(url=self.url, data=self.data.format(currentPageNumber), headers=self.headers, timeout=1)
        except requests.exceptions.RequestException as e:
            print("Error retrieving response: {0}".format(e))
            response = None

        return response

    # Retrieves a single page of ticker symbols and names from nyse site.
    # input: 
    #       currentPageNumber : page to request from https://www.nyse.com/listings_directory/stock
    # Return:
    #       response : response from site or None if timed out
    def getSinglePage(self, currentPageNumber):
        response = self.sendHTTPRequestForTickerSymbols(currentPageNumber)
        print("SinglePage res: {0}".format(response))

        # use exponential backoff if bad request received
        if response == None or response.ok == False:
            n = 0
            currWaitTime = math.pow(2,n)+random.random()
            MAX_BACKOFF_TIME = 32

            while (response == None or (response != None  and response.ok == False)) and math.pow(2,n) <= MAX_BACKOFF_TIME:
                print("Bad response received for page {0}, waiting {1} seconds to retry".format(currentPageNumber, currWaitTime))
                time.sleep(currWaitTime)
                response = self.sendHTTPRequestForTickerSymbols(currentPageNumber)

                n += 1
                currWaitTime = math.pow(2,n)+random.random()

        return response

    # Processes the response received and inputs data into dictionary in case it is needed later
    # input: 
    #       response : response from site, assumed to be valid when entering this function
    # Return:
    #       None
    def getSymbolAndName(self, response):
        resJson = response.json()
        for item in resJson:
            ticker = item['symbolEsignalTicker']
            name = item['instrumentName']
            self.tickerDict[ticker] = name
            
    # Writes the values in the dictionary to a file 'tickerSymbols.txt' 
    # input: 
    #       None
    # Return:
    #       None
    def writeDictionaryToFile(self):
        with open('tickerSymbols.txt', 'w') as f:
            for k, v in self.tickerDict.items():
                f.write("{0}\t{1}\n".format(k,v))

    # Retrieves each stock symbol and name from the NYSE site and writes the data to a file
    # input: 
    #       None
    # Return:
    #       None
    def getAllPages(self):
        currentPageNumber = 1
        response = self.getSinglePage(currentPageNumber)

        # Request will generate an '[]' as a response if there is no more data
        while response != None and response.ok and response.text != EMPTY_RESPONSE:
            print("Retrieving page: {0}. Status code: {1}".format(currentPageNumber,response.status_code))
            self.getSymbolAndName(response)
            currentPageNumber += 1
            response = self.getSinglePage(currentPageNumber)
        self.writeDictionaryToFile()
        return self.tickerDict
