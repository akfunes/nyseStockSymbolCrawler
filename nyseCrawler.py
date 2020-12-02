import requests
import json
import time

'''
curl 'https://www.nyse.com/api/quotes/filter' \
  -H 'Connection: keep-alive' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36' \
  -H 'Content-Type: application/json' \
  -H 'Accept: */*' \
  -H 'Origin: https://www.nyse.com' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Referer: https://www.nyse.com/listings_directory/stock' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  --data-binary '{"instrumentType":"EQUITY","pageNumber":1,"sortColumn":"NORMALIZED_TICKER","sortOrder":"ASC","maxResultsPerPage":10,"filterToken":""}' \
  --compressed
'''

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

    def sendHTTPRequestForTickerSymbols(self,currentPageNumber):
        response = None
        try:
            response = requests.post(url=self.url, data=self.data.format(currentPageNumber), headers=self.headers, timeout=1)
        except ValueError:
            print("Error retrieving response: {0}".formmat(ValueError))

        return response

    def getSinglePage(self, currentPageNumber):
        response = self.sendHTTPRequestForTickerSymbols(currentPageNumber)

        # use exponential backoff if bad request received
        if response.ok == False:
            n = 0
            currWaitTime = math.pow(2,n)+random.random()
            MAX_BACKOFF_TIME = 32

            while response != None and response.ok == False and math.pow(2,n) <= MAX_BACKOFF_TIME and response.text != EMPTY_RESPONSE:
                print("Bad response received for page {0}, waiting {1} seconds to retry".format(currentPageNumber, currWaitTime))
                time.sleep(currWaitTime)
                response = self.sendHTTPRequestForTickerSymbols(currentPageNumber)

                n += 1
                currWaitTime = math.pow(2,n)+random.random()

        return response

    def getSymbolAndName(self, response):
        resJson = response.json()
        for item in resJson:
            ticker = item['symbolEsignalTicker']
            name = item['instrumentName']
            self.tickerDict[ticker] = name
            
    def writeDictionaryToFile(self):
        with open('tickerSymbols.txt', 'w') as f:
            for k, v in self.tickerDict.items():
                f.write("{0}\t{1}\n".format(k,v))

    def getAllPages(self):
        currentPageNumber = 1
        response = self.getSinglePage(currentPageNumber)
        while response != None and response.ok and response.text != EMPTY_RESPONSE:
            print("Retrieving page: {0}. Status code: {1}".format(currentPageNumber,response.status_code))
            self.getSymbolAndName(response)
            currentPageNumber += 1
            response = self.getSinglePage(currentPageNumber)
        self.writeDictionaryToFile()
        return self.tickerDict
