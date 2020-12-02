import nyseCrawler

crawler = nyseCrawler.nyseCrawler()
print(crawler.getAllPages())
#if crawler.getSinglePage(675).text == '[]':
#    print(True)
