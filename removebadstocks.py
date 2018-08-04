brokenList = []

#open file and put all stock symbols in a list, then clear contents of file
with open('data/brokenstocks.txt','r+') as file:
	line = file.readline()
	while line:
		brokenList.append(line)
		line = file.readline()
	file.truncate(0)

#delete each symbol from the main list
with open('data/tickerlist.txt') as stockList:
	lines = stockList.readlines()

with open('data/tickerlist.txt','w') as newStockList:
	for x in lines:
		if x not in brokenList:
			newStockList.write(x)
		else:
			print('Success with ' + x[:-1])
