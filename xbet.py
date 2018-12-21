from selenium import webdriver
import csv
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.action_chains import ActionChains
import time
import ConfigParser
from time import sleep
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--headless')
browser = webdriver.Chrome()

#1xbet login xpaths
xPathLogin = '//*[@id="loginout"]/div[2]/div/div/div[1]/span[1]'
xPathEmail =  '//*[@id="userLogin"]'
xPathPassword = '//*[@id="userPassword"]'
xPathSubmitLogin = '//*[@id="userConButton"]'

#1xbet login successful confirmation xpath
xPathMyAccount = '//*[@id="user-money"]/div/div/a/div/p[1]'

#1xbet currency confirmation xpath
xPathConfirmCurrency = '//*[@id="approve_accept"]'

#Baccarat navigation xpaths
xPathIframe = '//*[@id="game-iframe"]'
xPathBaccart = '//div[@data-game="baccarat"]'
xPathIframeGame = '//*[@id="container"]/div/div/iframe'
xPathSpeedBaccartB = '//div[@data-tableid="lv2kzclunt2qnxo5"]'

#Baccarat game status xpaths
xPathPlaceBets = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[1]/div/div/div[contains(string(), "PLACE YOUR BETS")]'
xPathPlayerWon = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[1]/div/div/div[contains(string(), "PLAYER WINS")]'
xPathBankWon = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[1]/div/div/div[contains(string(), "BANKER WINS")]'
xPathTie = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[1]/div/div/div[contains(string(), "TIE")]'
xPathPlayerBankTie = xPathPlayerWon + '|' + xPathBankWon + '|' + xPathTie
xPathWaitForNextGame = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[1]/div/div/div[contains(string(), "WAIT FOR NEXT GAME")]'

#Baccarat bet placing xpaths
xPath1Dollar = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[3]/div/div/div/div[1]/div/ul/li[2][div/span[contains(text(), "$ 1")]]'
xPathDouble = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[3]/div/div/div/div[1]/div/ul/li[button/span[contains(text(), "DOUBLE")]]'
xPathPlayerSubmit = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[2]/div/div/div/div[1]/div[1][contains(@class, "player--3F1-C")]'
xPathBankSubmit = '//*[@id="root"]/div/div[1]/div/div/div[6]/div[3]/div/div[2]/div/div/div/div[1]/div[2][contains(@class, "banker--11HzV")]'

#load configurations from  config.ini 
config = ConfigParser.ConfigParser()
config.read("config.ini")
email = config.get('LoginCredentials', 'Email')
password = config.get('LoginCredentials', 'Password')
sequence = config.get('BotConfig', 'BetPattern').split(",")
betInitial = int(config.get('BotConfig', 'InitialBet'))
betUpperLimit = int(config.get('BotConfig', 'upperLimit'))

length = len(sequence)
headers = ['Round','Player/Bank','Amount','Double','Result']

def getFileName():
	ts = time.time()
	return 'betting-results-' + str(ts) + '.csv'

filename = getFileName()
outfile  = open(filename, "wb")
writer = csv.writer(outfile, delimiter=',', quotechar='', quoting=csv.QUOTE_NONE)
writer.writerow(headers)

#initial values

print '===Betting bot has been initialized with the following values==='
print 'Betting Sequence:',sequence
print 'Initial Bet:', betInitial, '$'
print 'Bet limit:', betUpperLimit, '$'

def placeInitialBet(xpathSubmit):
	for i in range(betInitial):
		browser.find_elements_by_xpath(xpathSubmit)[0].click()

def doubleBets(d):
	for i in range(d):
    		browser.find_elements_by_xpath(xPathDouble)[0].click()	
	
#utility functions
def placeBets(d, selection):
	xpathSubmit = xPathPlayerSubmit if selection == 'P' else xPathBankSubmit
	WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH, xPath1Dollar)))
	browser.find_elements_by_xpath(xPath1Dollar)[0].click()
	WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH, xpathSubmit)))
	placeInitialBet(xpathSubmit)
	WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH, xPathDouble)))
	doubleBets(d)
	print 'Bet submitted'

def getBetAmount(double):
	currentBet = betInitial
	for i in range(double):
		currentBet *= 2
	if currentBet < betUpperLimit:
		return currentBet, double
	else:
		return betInitial, 0

def startPlaying(double,count):
	WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH, xPathWaitForNextGame)))
	print 'Waiting to place bets..'
	result = 'won'
	try:
		while True:
			print '===================Round ' + str(count+1) + '==================='
			index = count%length
			selection = sequence[index].strip()
			selectionText = 'PLAYER WINS' if selection == 'P' else 'BANKER WINS'
			amount,double = getBetAmount(double)
			currDouble = double
			WebDriverWait(browser, 60).until(EC.element_to_be_clickable((By.XPATH, xPathPlaceBets)))
			print 'Bet to be placed for:', selection
			print 'Initial bet:', betInitial, '$'
			print 'Double:', currDouble, 'x'
			print 'Bet amount:', amount, '$'
			placeBets(double, selection)
		
			WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, xPathPlayerBankTie)))
			playertext = None if len(browser.find_elements_by_xpath(xPathPlayerWon)) == 0 else   browser.find_elements_by_xpath(xPathPlayerWon)[0].text
			banktext = None if len(browser.find_elements_by_xpath(xPathBankWon)) == 0 else browser.find_elements_by_xpath(xPathBankWon)[0].text
			if playertext:
				if playertext == selectionText:
					print 'Congrats. Player won'
					double = 0
					result = 'won'
				else:
					print 'Oops. Player won'
					double += 1
					result = 'loss'
			elif banktext:
				if banktext == selectionText:
					print 'Congrats. Bank won'
					double = 0
					result = 'won'
				else:
					print 'Oops. Bank won'
					double += 1
					result = 'loss'
			else:
				print 'Tied.'
				result = 'tied'
			count += 1
			result = [(count),selection,amount,str(currDouble) + 'x',result]
			writer.writerow(result)
	except KeyboardInterrupt:
	    	print('Session ended.')
	except Exception,e: 
		print e
		print 'Something went wrong. Reloading the game..'
		navigateToBaccarat(double,count)

def navigateToBaccarat(double,count):
	browser.get('https://1xbet.com/en/tvgames/show/livecasino?casino=livecasinoevolution&game=18335')
	browser.find_elements_by_xpath(xPathConfirmCurrency)[0].click()

	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xPathIframe)))
	iframe = browser.find_element_by_xpath(xPathIframe)
	browser.switch_to.frame(iframe)
	WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, xPathBaccart)))
	browser.find_elements_by_xpath(xPathBaccart)[0].click()
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xPathSpeedBaccartB)))
	browser.find_elements_by_xpath(xPathSpeedBaccartB)[0].click()

	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xPathIframeGame)))
	iframeGame = browser.find_element_by_xpath(xPathIframeGame)
	browser.switch_to.frame(iframeGame)
	startPlaying(double,count)

def login():
	browser.find_elements_by_xpath(xPathLogin)[0].click()
	usernameEl = browser.find_elements_by_xpath(xPathEmail)[0]
	passwordEl = browser.find_elements_by_xpath(xPathPassword)[0]
	usernameEl.send_keys(email)
	passwordEl.send_keys(password)
	browser.find_elements_by_xpath(xPathSubmitLogin)[0].click()
	WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.XPATH, xPathMyAccount)))
	double = 0
	count = 0
	navigateToBaccarat(double,count)

# navigate to login page
url = 'https://1xbet.com/en/'
browser.get(url)
login()

