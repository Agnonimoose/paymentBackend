"""
Stub snippet of payment backend
"""

import requests, xmltodict, time, json, datetime, pickle
from web3 import Web3
from web3.exceptions import TransactionNotFound
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import slow_gas_price_strategy, fast_gas_price_strategy
from utils import *
from threading import Thread
from fiats import CurrencyRates

url = "https://eth-goerli.g.alchemy.com/v2/{yout_API_key}"
w3 = Web3(Web3.HTTPProvider(url))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.set_gas_price_strategy(slow_gas_price_strategy)



class client:
    def __init__(self, apikey):
        self.apikey = apikey
        self.f = "https://api-goerli.etherscan.io/api?module=account&action=txlist&address={your_address}&startblock=0&endblock=99999999&sort=asc&apikey={your_api_key_token}"
        self.r = None
        self.balance = w3.eth.get_balance("your_wallet_address")
        self.blockNo = {}
        self.transDict = {}
        self.transDDict = {}
        self.transWDict = {}
        self.latestBlock = 0
        self.cycle = True
        self.getPrice()

        
    def getBalance(self):
        """Simply returns your wallet balance"""
        return w3.eth.get_balance("{your_wallet_address}")

    def getAccountTrans(self, address, start=0, end=99999999999):
        """Gets all transactions associated with this waller"""
        url = "https://api-goerli.etherscan.io/api?module=account&action=txlist&address={0}&startblock={1}&endblock={2}&sort=asc&apikey={3}".format(
            address, start, end, self.apikey)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.rawTrans = self.requestorGet(url, headers=headers)
        self.latestBlock = 0

    def getSpecificTrans(self, transNo):
        """Get a specific wallet transaction"""
        self.specTrans = dict(w3.eth.get_transaction(transNo))
        self.specTransObj = transObj(self.specTrans, self, w3=True)

    def getRates(self):
        """Get current fiat rates from European Central Bank"""
        rates = requests.get("http://www.ecb.int/stats/eurofxref/eurofxref-daily.xml").content.decode()
        responseDict = xmltodict.parse(rates)['gesmes:Envelope']['Cube']['Cube']['Cube']
        EURrates = {}
        for item in responseDict:
            EURrates[item["@currency"]] = float(item["@rate"])
        EURrates['EUR'] = 1.0000

        eur = 1 / EURrates['GBP']
        GBPrates = {}
        for fiat in EURrates:
            if fiat == 'EUR':
                pass
            elif fiat == 'GBP':
                pass
            else:
                GBPrates[fiat] = EURrates[fiat] * eur
        GBPrates['EUR'] = eur
        GBPrates['GBP'] = 1.0000

        usd = 1 / EURrates['USD']
        USDrates = {}
        for fiat in EURrates:
            if fiat == 'EUR':
                pass
            elif fiat == 'USD':
                pass
            else:
                USDrates[fiat] = EURrates[fiat] * usd
        USDrates['EUR'] = usd
        USDrates['USD'] = 1.0000

        return {'EUR': EURrates, 'GBP': GBPrates, 'USD': USDrates}

    def getPrice(self, verbose=False):
        """Get current crypto price from Etherscan, Coingecko and Binance"""
        url = "https://api-goerli.etherscan.io/api?module=stats&action=ethprice&apikey={0}".format(self.apikey)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.priceRaw = self.requestorGet(url, headers=headers)
        if isinstance(self.priceRaw['result'], str):
            time.sleep(1)
            self.getPrice()
        else:
            self.ethUSD = float(self.priceRaw['result']['ethusd'])
            self.weiUSD = self.ethUSD / 10 ** 18
            self.fiatRates = self.getRates()
            self.GBPX = self.fiatRates['GBP']
            if verbose == True:
                print("eth USD = ", self.ethUSD)
                print("wei USD = ", self.weiUSD)
            try:
                BTCurl = "https://api.coingecko.com/api/v3/exchange_rates"
                r = requests.get(BTCurl, headers=headers)
                c = json.loads(r.content)
                self.geckoRates = c['rates']
            except:
                self.geckoRates = None

            try:
                u = "https://api.binance.com/api/v3/avgPrice?symbol=BTCGBP"
                r = requests.get(u, headers=headers)
                c = json.loads(r.content)
                self.binanceRates = c
            except:
                pass

    def blockByTime(self, time):
        """Get blockchain block by time"""
        startUnixTime = datetime.datetime(*time, 0, 0)
        startUnixTime = int(startUnixTime.timestamp())
        url = "https://api-goerli.etherscan.io/api?module=block&action=getblocknobytime&timestamp={0}&closest=before&apikey={1}".format(
            startUnixTime, self.apikey)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        blockinfo = json.loads(r.content.decode())
        blockNo = {}
        if blockinfo['message'] == 'OK':
            blockNo["start"] = int(blockinfo['result'])
        endUnixTime = datetime.datetime(*time, 23, 59)
        endUnixTime = int(endUnixTime.timestamp())
        url = "https://api-goerli.etherscan.io/api?module=block&action=getblocknobytime&timestamp={0}&closest=before&apikey={1}".format(
            endUnixTime, self.apikey)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        blockinfo = json.loads(r.content.decode())
        if blockinfo['message'] == 'OK':
            blockNo["end"] = int(blockinfo['result'])
        return blockNo

    def getAccountTransDate(self, time):
        """Get wallet transactions by date"""
        blocks = self.blockByTime(time)
        self.getAccountTrans('your_wallet_address', start=blocks['start'],
                             end=blocks['end'])

    def upDate(self, interval=300):
        """Updates prices every 5 mins."""
        while self.cycle == True:
            latest = w3.eth.get_block('latest')
            self.getAccountTrans('your_wallet_address', start=self.latestBlock, end=latest.number)
            self.getPrice()
            self.maxWithdrawal = 50 / self.ethUSD
            time.sleep(interval)

    def updateThread(self):
        x = Thread(target=self.upDate, daemon=True)
        x.start()

    def requestorGet(self, resource, info=None, headers=None):
        """Standard request getter model. Returning content/data only."""
        if info == None:
            if headers == None:
                res = requests.get(resource)
            else:
                res = requests.get(resource, headers=headers)
        else:
            if headers == None:
                res = requests.get(resource, info)
            else:
                res = requests.get(resource, info, headers=headers)
        return self.decodeRequest(res)

    def decodeRequest(self, res):
        """Request content decoder"""
        if res.content.startswith(b'\x80'):
            return pickle.loads(res.content)
        else:
            return json.loads(res.content)


class _dataCache:
    def __init__(self):
        self._gasPrice = w3.eth.generateGasPrice()
        self.update()

    def _update(self):
        while True:
            try:
                self._gasPrice = w3.eth.generateGasPrice()
                time.sleep(900)
            except Exception as e:
                print(e)

    def update(self):
        x = Thread(target=self._update, daemon=True)
        x.start()

    @property
    def gasPrice(self):
        return self._gasPrice


dataCache = _dataCache()

class newTransfer:
    """This is your standard transfer object for your records. Use it to handle your transactions,
    then call store on it to store to DB."""
    def __init__(self):
        self.my_address = Web3.toChecksumAddress("your_wallet_address")
        self.my_key = "your_wallet_key"
        self.apikey = "you_API_key"

        self.getPrice()

    def usdToEth(self, USD):
        wei = float(USD / self.weiUSD)
        return int(wei)

    def estimateGas(self, transaction):
        estimate = w3.eth.estimate_gas(transaction)
        gasPrice = dataCache.gasPrice
        self.gasEstimateEth = estimate * gasPrice
        self.gasEstimateUSD = self.ethToUSD(self.gasEstimateEth)

    def ethToUSD(self, ETH):
        return ETH * self.weiUSD

    def getPrice(self, verbose=False):
        self.priceRaw = c.priceRaw
        self.ethUSD = c.ethUSD
        self.weiUSD = c.weiUSD
        self.fiatRates = c.fiatRates
        self.GBPX = c.GBPX
        self.geckoRates = c.geckoRates
        self.binanceRates = c.binanceRates

    def msgToHex(self, s):
        b = s.encode('utf-8')
        return b.hex()

    def generateTrans(self, to, amount, message):
        """Generate transaction"""
        transaction = {'to': to,
                       'from': self.my_address,
                       'value': int(w3.toWei(amount, 'ether')),
                       'gasPrice': int(dataCache.gasPrice * 1.2),
                       'gas': 35000,
                       'nonce': w3.eth.get_transaction_count(self.my_address),
                       'chainId': 5,
                       'data': self.msgToHex(message)}
        self.t = transaction
        try:
            self.desired = transaction['value']
            transaction['value'] = transaction['value'] - (transaction['gasPrice'] * transaction['gas'])
            if transaction['value'] < 0:
                return "Transfer amount too little, please increase the amount to account for gas (est. {0} ETH)".format(
                    w3.fromWei(transaction['gasPrice'] * transaction['gas'], 'ether'))
            signed_tx = w3.eth.account.sign_transaction(transaction, self.my_key)
            self.transObj = signed_tx
            self.trans = transaction
            return None
        except Exception as e:
            return str(e)

    def sendTrans(self, trans):
        try:
            self.txn_hash = w3.eth.send_raw_transaction(trans.rawTransaction)
            self.recp = w3.eth.wait_for_transaction_receipt(self.txn_hash)
            return self.recp
        except Exception as e:
            self.txn_hash = None
            self.recp = None
            return None

    def checkRecp(self):
        return w3.eth.get_transaction_receipt(self.txn_hash)

    def store(self):
        """Call this to store the transaction in JSONable format"""
        storable = {
            'transaction_hash': self.txn_hash,
            'transaction reciept': self.recp,
            'transaction': self.t
        }
        return storable

class getfiat:
    def get(self):
        """Get current Fiat rates"""
        rates = c.GBPX
        returnable = {'USD': 1 / rates['USD'], 'AUD': 1 / rates['AUD'], 'CAD': 1 / rates['CAD'],
                      'CNY': 1 / rates['CNY'], 'EUR': 1 / rates['EUR'], 'GBP': 1 / rates['GBP'],
                      'INR': 1 / rates['INR'], 'JPY': 1 / rates['JPY']}
        return returnable


class getETH:
    def get(self):
        """Get ETH rates from Etherscan"""
        url = " https://api-goerli.etherscan.io/api?module=stats&action=ethprice&apikey={your_API_key}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r = requests.get(url, headers=headers)
        ethPrice = json.loads(r.content.decode())
        return float(ethPrice['result']['ethusd'])


class createWIthdrawTransaction:
    """"""
    def __init__(self, addy, amount):
        self.address = addy
        self.amount = amount
        self.nt = newTransfer()

    def createTransfer(self):
        if Web3.isChecksumAddress(self.address) == False:
            self.address = Web3.toChecksumAddress(self.address)
        self.msgID = "{optional message}"
        result = self.nt.generateTrans(self.address, self.amount, self.msgID)
        if result == None:
            pass
        else:
            return result

    def sendTransfer(self):
        sent = self.nt.sendTrans(self.nt.transObj)
        if sent == None:
            return 0
        else:
            if self.nt.recp.status == 1:
                returnable = {"gasUsed": self.nt.recp.gasUsed, "gasPrice": self.nt.trans["gasPrice"],
                              "value": self.nt.trans["value"],
                              'ethusd': self.nt.priceRaw['result']['ethusd'],
                              'ethusd_timestamp': self.nt.priceRaw['result']['ethusd_timestamp'],
                              "txn_receipt": self.nt.recp}
                return returnable
            else:
                return 0


def checkForTrans(txn):
    try:
        return w3.eth.get_transaction(txn)
    except Exception as e:
        if isinstance(e, TransactionNotFound):
            return (1,
                    "Transaction not found, it may take up to 30 minuets for funds to be credited - be patient. The email address registered to the depositing wallet will be notified when the transaction is varified. If funds arent credited, open a ticket at on the discord server.")
        elif isinstance(e, ValueError):
            return (2, "Invalid transaction receipt, please try again")
        else:
            return (3, "Error not caught, try again")


u = CurrencyRates()
c = client('{your_API_key}')
c.updateThread()