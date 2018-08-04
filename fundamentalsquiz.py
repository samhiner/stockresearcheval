#ticker list is generated from the wilshire5000cleaner.py script which is in this folder

import random
import urllib.request

def getHTML(url):
	try:
		site = urllib.request.urlopen(url)
	except:
		return 'redo'
	return site.read()

#make sure strings are the right length so the vertical border is a straight line
def addSpace(string,targetSize):
	if len(string) < targetSize:
		string += ' '
		return addSpace(string,targetSize)
	
	return string

#copy down a variable length number
def getNum(page,position,number):
	if page[position].isnumeric() or page[position] in ['.','B','/',]:
		number += page[position]
		return getNum(page,position + 1,number)

	if number == '':
		number = 'N/A'

	return number

#if not yet in utf8 format put page in that format
def utf8(page):
	if type(page) is not str:
		page = page.decode('utf-8')

	return page

class tickerQuiz:
	
	#set up the list for the game
	def __init__(self,startScreen):
		self.getTickerList()
		print(startScreen)

	#create list of all ticker symbols by reading from file
	def getTickerList(self):
		with open('data/tickerlist.txt') as file:
			self.tickerList = []
			line = file.readline()
			while line:
				self.tickerList.append(line[:-2])
				line = file.readline()

	def addBrokenStocks(self):
		stockList = ''
		for x in range(0,len(self.brokenStocks)):
			stockList += self.brokenStocks[x] + '\n'

		with open('data/brokenstocks.txt','a') as file:
			file.write(stockList)
	

	#get a random stock ticker from the list
	def randomTicker(self):
		tickerIndex = random.randint(0,len(self.tickerList) - 1)
		ticker = self.tickerList[tickerIndex]

		if ticker in self.blacklist:
			return self.randomTicker() #ISSUE: test MEEE

		#grab fidelity detailed quote, shorten it, and put it in utf-8 format for ease of readability
		fidelityHTML = getHTML('https://eresearch.fidelity.com/eresearch/evaluate/quote.jhtml?symbols=' + ticker)
		if fidelityHTML == 'redo':
			self.brokenStocks.append(ticker)
			return self.randomTicker()
		
		self.fidelityHTML = utf8(fidelityHTML[38500:-20000])

		if 'Ask<' not in self.fidelityHTML:
			self.brokenStocks.append(ticker)
			return self.randomTicker() #ISSUE: test me too

		#just contains analyst recommendations in a JSON format
		self.analysisPage = utf8(getHTML('https://query2.finance.yahoo.com/v10/finance/quoteSummary/' + ticker + '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&modules=recommendationTrend'))
		if self.analysisPage == 'redo':
			self.brokenStocks.append(ticker)
			return self.randomTicker()

		if 'strongBuy' not in self.analysisPage or '"period":"0m","strongBuy":0,"buy":0,"hold":0,"sell":0,"strongSell":0' in self.analysisPage:
			self.brokenStocks.append(ticker)
			return self.randomTicker() #ISSUE: TEST TEST TEST (mostly the long string, UG is a good stock for that)

		return ticker

	#find number on fidelity site based on a nearby text "landmark" and the offset from that landmark
	def fidelityLookup(self,landmarkStr,offset):
		landmark = self.fidelityHTML.index(landmarkStr)
		return getNum(self.fidelityHTML,landmark + offset,'')

	#grab and clean online trading info into relevant values with spacing to work with border
	def getResearch(self):
		self.stockData['price'] = addSpace(self.fidelityLookup('Ask<',81),15)
		self.stockData['MktCap'] = addSpace(self.fidelityLookup('Capitalization<',67),15)
		self.stockData['P/E'] = addSpace(self.fidelityLookup('Months)',49),8)
		self.stockData['PEG'] = addSpace(self.fidelityLookup('PEG Ratio (5-Year Projected)<',70),8)
		#print(self.fidelityHTML)

	#get the average analyst rating for a stock
	def getAnalysis(self,ticker):
		strongBuys = int(getNum(self.analysisPage,self.analysisPage.index('strongBuy') + 11,''))
		buys = int(getNum(self.analysisPage,self.analysisPage.index('buy') + 5,''))
		holds = int(getNum(self.analysisPage,self.analysisPage.index('hold') + 6,''))
		sells = int(getNum(self.analysisPage,self.analysisPage.index('sell') + 6,''))
		strongSells = int(getNum(self.analysisPage,self.analysisPage.index('strongSell') + 12,''))

		#strongBuys is a rating of 5 so to get total 'stars' you just do number of reqs at that level times 5
		totalStars = strongBuys * 5 + buys * 4 + holds * 3 + sells * 2 + strongSells
		return totalStars / (strongBuys + buys + holds + sells + strongSells)

	#set up all of the game specific variables and start questions
	def startQuiz(self):
		print(self.gameStart)
		x = input('#######################################################################')
		self.blacklist = []
		self.counter = 0
		self.numCorrect = 0
		self.brokenStocks = []
		nextGame = self.question()

		if nextGame == 'y' or nextGame == 'Y':
			self.startQuiz()
		else:
			print(self.shutDown)

	def question(self):
		self.counter += 1
		if self.counter > 10:
			return self.endQuiz()

		ticker = self.randomTicker()
		self.getResearch()
		
		showCounter = addSpace(str(self.counter),2)
		showTicker = addSpace(ticker,10)

		print(self.qSec1 + showCounter + self.qSec2 + showTicker + self.qSec3 + self.stockData['price'] + self.qSec4 + self.stockData['MktCap'] + self.qSec5 + self.stockData['P/E'] + self.qSec6 + self.stockData['PEG'] + self.qEnd, end='')
		opinion = input()

		avgRating = self.getAnalysis(ticker)
		avgRatingName = addSpace(self.positionList[int(round(avgRating,0)) - 1],10)

		if (opinion == '1' and avgRating >= 3) or (opinion == '0' and avgRating <= 3):
			endQuestion = self.winScreen
			self.numCorrect += 1
		else:
			endQuestion = self.loseScreen

		print(self.aSec1 + endQuestion + avgRatingName + self.aSec2)

		return self.question()

	#ends quiz and gives option to start another one
	def endQuiz(self):
		self.addBrokenStocks()

		if self.numCorrect == 10:
			outOfTen = self.tenCorrect
		else:
			outOfTen = self.belowTenCorrect

		playAgain = input(self.endQuiz1 + str(self.numCorrect) + outOfTen + self.endQuiz2)
		print(self.endQuiz3)

		return playAgain		


#all of the larger data pieces are stored below this comment

startScreen = '''#######################################################################
#                                                                     #
#                     Stock Market Research Quiz:                     #
#                        Fundamentals Edition                         #
#                                                                     #
#######################################################################
#                                                                     #
#                        RULES AND INFORMATION                        #
#                                                                     #
#  You will have to evaluate a random stock based on the information  #
#  given to you (focusing on the fundamentals of the stock) and your  #
#  previous knowledge of the stock.                                   #
#                                                                     #
#  You will submit whether you are bullish or bearish on the stock.   #
#  If your opinion matches that of Yahoo Finance analysts, you will   #
#  win the round.                                                     #
#                                                                     #
#  There are ten rounds and you will see a scoresheet at the end of   #
#  the game. *Please be patient, the sites from which the game grabs  #
#  data can take a while to load*                                     #
#                                                                     #
#######################################################################
#                                                                     #
#                         PROJECT INFORMATION                         #
#                                                                     #
#  Get the source code at the link below:                             #
#  www.github.com/smhnr27/code/tree/master/python/stockresearcheval.  #
#                                                                     #
#  This project is licensed under the MIT License, so you may use it  #
#  in any way you like.                                               #
#                                                                     #
#######################################################################'''

#Start program using above start page (only displays start page and configures ticker list)
quiz = tickerQuiz(startScreen)

quiz.gameStart = '''#                                                                     #
#                              START GAME                             #
#                                                                     #
#                     Hit enter to start the game.                    #
#                                                                     #'''

#ISSUE: Test truth of this comment \/
#can be removed without consquence. mostly just for documentation
quiz.stockData = { 
	#'Price':'',
	#'P/E':'', #TTM
	#'PEG':'', #Forward 5 year
	#'MktCap':'',
	'Gross Margin':'', #TTM
	'EPS TTM Growth':'', #TTM vs prior TTM
	'P/B':'',
	'Free Cash Flow':'', #TTM
	'Debt/Equity':'',
	'Insider Buys':'', #shares bought last 12 months
	'Insider Sells':'' #shares sold last 12 months
}

quiz.positionList = ['Strong Sell', 'Sell', 'Hold', 'Buy', 'Strong Buy']

quiz.qSec1 = '''#                                                                     #
#                             QUESTION '''

quiz.qSec2 = '''                             #
#                                                                     #
#                  Ticker Symbol: '''

quiz.qSec3 = '''                          #
#                    Stock Price: $'''

quiz.qSec4 = '''                    #
#                     Market Cap: $'''

quiz.qSec5 = '''                    #
#                P/E Ratio (TTM): '''

quiz.qSec6 = '''                            #
#             PEG Ratio (5y Fwd): '''

quiz.qEnd = '''                            #
#                                                                     #
#                    Bullish (1) or Bearish (0)?                      '''

quiz.aSec1 = '''#                                                                     #
#######################################################################
#                                                                     #\n'''

quiz.winScreen = '''#                               YOU WIN                               #
#                                                                     #
#                       Analyst Opinion: '''

quiz.loseScreen = '''#                               YOU LOSE                              #
#                                                                     #
#                       Analyst Opinion: '''

quiz.aSec2 = '''                   #
#                                                                     #
#######################################################################'''

quiz.endQuiz1 = '''#                                                                     #
#                             END OF QUIZ                             #
#                                                                     #
#                   You got '''

quiz.belowTenCorrect = '''/10 questions correct!                   #\n'''

#contains one less space to account for extra digit
quiz.tenCorrect = '''/10 questions correct!                  #\n'''

quiz.endQuiz2 = '''#                   Do you want to play again? (Y/N)                  '''

quiz.endQuiz3 = '''#                                                                     #
#######################################################################'''

quiz.shutDown = '''#                                                                     #
#                        THANK YOU FOR PLAYING                        #
#                                                                     #
#######################################################################'''

#start the first round of the game
quiz.startQuiz()