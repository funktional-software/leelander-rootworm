__author__ = "mikba"


class cmdtyApiHelper():
	def __init__(self):
		# setup dict to map the market name of cmdty to the api (exchange?) name
		self.commoditySymbolByNameDict = dict()

		self.commoditySymbolByNameDict["Corn"] = "ZC"
		self.commoditySymbolByNameDict["Soybeans"] = "ZS"
		self.commoditySymbolByNameDict["Wheat"] = "ZW"
		self.commoditySymbolByNameDict["Cotton #2"] = "CT"
		self.commoditySymbolByNameDict["Oats"] = "ZO"
		self.commoditySymbolByNameDict["Canola"] = "RS"
		self.commoditySymbolByNameDict["Soybean Meal"] = "ZM"
		self.commoditySymbolByNameDict["Soybean Oil"] = "ZL"
		self.commoditySymbolByNameDict["Soybean Crush"] = "CS"
		self.commoditySymbolByNameDict["Rough Rice"] = "ZR"
		self.commoditySymbolByNameDict["Spring Wheat"] = "MW"
		self.commoditySymbolByNameDict["SRWI Soft Red Wheat"] = "IW"
		self.commoditySymbolByNameDict["HRSI Hard Red Spring"] = "IP"
		self.commoditySymbolByNameDict["HRWI Hard Red"] = "IH"
		self.commoditySymbolByNameDict["KCBT Red Wheat"] = "KE"
		self.commoditySymbolByNameDict["NCI National Corn"] = "IC"
		self.commoditySymbolByNameDict["Ethanol Futures (P)"] = "AK"
		self.commoditySymbolByNameDict["Ethanol Forward"] = "FZ"
		self.commoditySymbolByNameDict["Crude Oil WTI"] = "CL"
		self.commoditySymbolByNameDict["Heating Oil"] = "HO"
		self.commoditySymbolByNameDict["Gasoline RBOB"] = "RB"
		self.commoditySymbolByNameDict["Natural Gas"] = "NG"
		self.commoditySymbolByNameDict["Crude Oil Brent"] = "CB"
		self.commoditySymbolByNameDict["Ethanol Futures"] = "ZK"
		self.commoditySymbolByNameDict["Live Cattle"] = "LE"
		self.commoditySymbolByNameDict["Feeder Cattle"] = "GF"
		self.commoditySymbolByNameDict["Lean Hogs"] = "HE"
		self.commoditySymbolByNameDict["Class III Milk"] = "DL"


		# setup map from Month number to api date character, e.g. GFK14 for feeder's in 
		self.commodityDateCharByMonth = dict()
		self.commodityDateCharByMonth[1] = "F"
		self.commodityDateCharByMonth[2] = "G"
		self.commodityDateCharByMonth[3] = "H"
		self.commodityDateCharByMonth[4] = "J"
		self.commodityDateCharByMonth[5] = "K"
		self.commodityDateCharByMonth[6] = "M"
		self.commodityDateCharByMonth[7] = "N"
		self.commodityDateCharByMonth[8] = "Q"
		self.commodityDateCharByMonth[9] = "U"
		self.commodityDateCharByMonth[10] = "V"
		self.commodityDateCharByMonth[11] = "X"
		self.commodityDateCharByMonth[12] = "Z"

		# setup map from Month number to api date character, e.g. GFK14 for feeder's in 
		self.commodityMonthByDateChar = dict()
		self.commodityMonthByDateChar["F"] = "Jan"
		self.commodityMonthByDateChar["G"] = "Feb"
		self.commodityMonthByDateChar["H"] = "Mar"
		self.commodityMonthByDateChar["J"] = "Apr"
		self.commodityMonthByDateChar["K"] = "May"
		self.commodityMonthByDateChar["M"] = "Jun"
		self.commodityMonthByDateChar["N"] = "Jul"
		self.commodityMonthByDateChar["Q"] = "Aug"
		self.commodityMonthByDateChar["U"] = "Sep"
		self.commodityMonthByDateChar["V"] = "Oct"
		self.commodityMonthByDateChar["X"] = "Nov"
		self.commodityMonthByDateChar["Z"] = "Dec"

	def getDateFromSymbol(self, symbol):
		return self.commodityMonthByDateChar[symbol[2]] + symbol[-2:]


	def getApiStr(self, symbol, month, year):
		return self.commoditySymbolByNameDict[symbol] + self.commodityDateCharByMonth[month] + str(year)[-2:]

	def getFDKey(self, capidict):
		fname = capidict["name"]
		fmonth = capidict["month"]
		fyear = capidict["year"]
		return self.getApiStr(fname,fmonth,fyear)
