import codecs

class transObj:
    def __init__(self, raw, parent, w3=False):
        self.raw = raw
        self.parent = parent
        if w3 == False:
            self._populate()
        else:
            self._populateW3()

    def _populate(self):
        self.__dict__['blockHash'] = self.raw['blockHash']
        self.__dict__['blockNumber'] = int(self.raw['blockNumber'])
        self.__dict__['confirmations'] = int(self.raw['confirmations'])
        self.__dict__['contractAddress'] = self.raw['contractAddress']
        self.__dict__['cumulativeGasUsed'] = int(self.raw['cumulativeGasUsed'])
        self.__dict__['from'] = self.raw['from']
        self.__dict__['gas'] = int(self.raw['gas'])
        self.__dict__['gasPrice'] = int(self.raw['gasPrice'])
        self.__dict__['gasUsed'] = int(self.raw['gasUsed'])
        self.__dict__['hash'] = self.raw['hash']
        self.__dict__['input'] = self.raw['input']
        self.__dict__['isError'] = int(self.raw['isError'])
        self.__dict__['nonce'] = int(self.raw['nonce'])
        self.__dict__['timeStamp'] = int(self.raw['timeStamp'])
        self.__dict__['to'] = self.raw['to']
        self.__dict__['transactionIndex'] = int(self.raw['transactionIndex'])
        self.__dict__['txreceipt_status'] = int(self.raw['txreceipt_status'])
        self.__dict__['value'] = int(self.raw['value'])
        if self.input != '0x':
            self.message = self.inputToMsg(self.input)
        else:
            self.message = None

    def _populateW3(self):
        self.__dict__['blockHash'] = self.raw['blockHash']
        self.__dict__['blockNumber'] = self.raw['blockNumber']
        self.__dict__['from'] = self.raw['from']
        self.__dict__['gas'] = self.raw['gas']
        self.__dict__['gasPrice'] = self.raw['gasPrice']
        self.__dict__['hash'] = self.raw['hash']
        self.__dict__['input'] = self.raw['input']
        self.__dict__['nonce'] = self.raw['nonce']
        self.__dict__['r'] = self.raw['r']
        self.__dict__['s'] = self.raw['s']
        self.__dict__['to'] = self.raw['to']
        self.__dict__['transactionIndex'] = self.raw['transactionIndex']
        self.__dict__['type'] = self.raw['type']
        self.__dict__['v'] = self.raw['v']
        self.__dict__['value'] = self.raw['value']
        if self.input != '0x':
            self.message = self.inputToMsg(self.input)
        else:
            self.message = None

    def inputToMsg(self, input, rbin=False):
        raw = input[2:]
        binString = codecs.decode(raw, "hex")
        if rbin == False:
            try:
                string = binString.decode('utf-8')
                return string
            except:
                return binString
        else:
            return binString
