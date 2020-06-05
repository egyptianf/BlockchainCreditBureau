import json
import os
import platform
from web3 import Web3

from CreditHistorySite.settings import BASE_DIR


class TransactionDictionary:
    def __init__(self, gas, sender, web3):
        self.gas = gas
        self.sender = sender
        self.web3 = web3

    def __new__(cls, gas, sender, web3):
        cls.gas = gas
        cls.sender = sender
        cls.web3 = web3
        return dict({
            'gas': cls.gas,
            'gasPrice': cls.web3.toWei('1', 'gwei'),
            'from': cls.sender,
            'nonce': cls.web3.eth.getTransactionCount(cls.sender)
        })


class Web3Handler:
    def __init__(self, ganache_url):
        self.ganache_url = ganache_url
        self.web3 = Web3(Web3.HTTPProvider(ganache_url))
        operating_system = platform.system()
        self.d = '/'
        if operating_system == 'Windows':
            self.d = '\\'
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.defaultKey = 'bc068f3928c573101f35ecd9dc773a8f76a482665941247eb2f1b607079e893c'

    def getContractABI(self, filename):
        with open(os.path.join(BASE_DIR, (
                'Solidity' + self.d + 'build' + self.d + 'contracts' + self.d + filename))) as contractFile:
            contractJson = json.load(contractFile)
            contractABI = contractJson['abi']
            return contractABI

    def getContractAddress(self, filename):
        with open(os.path.join(BASE_DIR, (
                'Solidity' + self.d + 'build' + self.d + 'contracts' + self.d + filename))) as contractFile:
            contractJson = json.load(contractFile)
            contractAdd = self.web3.toChecksumAddress(contractJson['networks']['5777']['address'])
            return contractAdd

    def getContract(self, filename):
        contractABI, contractAdd = self.getContractABI(filename), self.getContractAddress(filename)
        contract = self.web3.eth.contract(address=contractAdd, abi=contractABI)
        return contract

    def transact(self, transaction, private_key):
        signed_txn = self.web3.eth.account.signTransaction(transaction, private_key=private_key)
        transaction_hash = self.web3.eth.sendRawTransaction(self.web3.toHex(signed_txn.rawTransaction))
        return transaction_hash

    def getTransactionReceipt(self, transaction_hash):
        return self.web3.eth.getTransactionReceipt(transaction_hash)

    def getAccount(self, index):
        return self.web3.eth.accounts[index]


class AccountsHandler:
    def __init__(self, web3Handler, accountsContract):
        self.web3Handler = web3Handler
        self.accountsContract = accountsContract

    def addAccount(self, public_key, account_type):
        self.accountsContract.functions.add(public_key, account_type).transact()


class PendingLoan:
    def __init__(self, amount, loanerAddress, id, installmentsNum, interest):
        self.amount = amount
        self.loanerAddress = loanerAddress
        self.installmentsNum = installmentsNum
        self.interest = interest
