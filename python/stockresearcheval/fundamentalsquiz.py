# NOTE: the ticker list used here is not the same list as what was outputted from the 
# Jupyter Notebook, I discovered that half of the symbols on that list didn't exist 
# and found a better list, which did not require any formatting. I left in the Notebook
# bc it could be a good resource for file manipulation problems in the future.

import random
import urllib.request

def getHTML(url):
	site = urllib.request.urlopen(url)
	return site.read()

class tickerQuiz:
	
	#set up all of the non game-specifc data and start a game
	def __init__(self,startScreen,stockData):
		self.getTickerList()
		print(startScreen)
		self.stockData = stockData
		self.startQuiz()

	#create list of all ticker symbols by reading from file
	def getTickerList(self):
		with open('data/tickerlist.txt') as file:
			self.tickerList = []
			line = file.readline()
			while line:
				self.tickerList.append(line)
				line = file.readline()
	
	#get a random stock ticker from the list
	def randomTicker(self):
		tickerIndex = random.randint(0,len(self.tickerList) - 1)
		ticker = self.tickerList[tickerIndex]

		if ticker in self.blacklist:
			return selfrandomTicker() #ISSUE: test MEEE

		return ticker

	#copy down a variable length number
	def getNum(self,page,position,number):
		if page[position].isnumeric() or page[position] == '.':
			number += page[position]
			return self.getNum(page,position + 1,number)

		return number
		

	#grab and clean online trading info into relevant values
	def getResearch(self,ticker):
		#grab fidelity detailed quote, shorten it, and put it in utf-8 format for ease of readability
		fidelityHTML = getHTML('https://eresearch.fidelity.com/eresearch/evaluate/quote.jhtml?symbols=' + ticker)
		fidelityHTML = fidelityHTML[38500:-26750].decode("utf-8")

		#choose another ticker symbol if error page was recieved
		try:
			priceLandmark = fidelityHTML.index('Ask<') #ISSUE: test me when done
		except:
			return 'redo'

		self.stockData['price'] = self.getNum(fidelityHTML,priceLandmark + 81,'')
		print(self.stockData['price'])


	#set up all of the game specific variables and start questions
	def startQuiz(self):
		x = input('#######################################################################')
		self.blacklist = []
		self.counter = 0
		self.question()

	def question(self):
		self.counter += 1
		if self.counter > 10:
			self.endQuiz()

		ticker = self.randomTicker()

		error = self.getResearch(ticker)
		if error == 'redo':
			self.counter -= 1
			self.question()

		#print(self.qSec1 + counter + self.qSec2 + ticker + self.qSec3 + self.stockData['price'])

	#ISSUE: going to want to escape the function within a function loop with endQuiz
	def endQuiz(self):
		print('end')







#all of the larger data pieces are stored below this comment
#they are passed to the game class as parameters of the __init__ function

asciiStart = '''#######################################################################
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
#  If your opinion matches that of Thomson Reuter Starmine, you will  #
#  win the round.                                                     #
#                                                                     #
#  There are ten rounds and you will see a scoresheet at the end of   #
#  the game.                                                          #
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
#######################################################################
#                                                                     #
#                              START GAME                             #
#                                                                     #
#                     Hit enter to start the game.                    #
#                                                                     #'''


emptyStockData = {
	'Price':'',
	'P/E':'', #TTM
	'PEG':'', #Forward 5 year
	'MktCap':'',
	'Gross Margin':'', #TTM
	'EPS TTM Growth':'', #TTM vs prior TTM
	'P/B':'',
	'Free Cash Flow':'', #TTM
	'Debt/Equity':'',
	'Insider Buys':'', #shares bought last 12 months
	'Insider Sells':'' #shares sold last 12 months
}

quiz = tickerQuiz(asciiStart,emptyStockData)
