from tqdm import trange
from datetime import datetime
from millify import millify
from termcolor import colored
import requests
from web3 import Web3
import json
import config
import time
import pyfiglet
import os

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

contract_address = '0xce93F9827813761665CE348e33768Cb1875a9704'

abi = json.loads(
    '[{"constant":true,"inputs":[],"name":"ceoAddress","outputs":[{"name":"","type":"address"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getMyMiners","outputs":[{'
    '"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,'
    '"inputs":[],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"initialized","outputs":[{'
    '"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,'
    '"inputs":[{"name":"rt","type":"uint256"},{"name":"rs","type":"uint256"},{"name":"bs","type":"uint256"}],'
    '"name":"calculateTrade","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view",'
    '"type":"function"},{"constant":true,"inputs":[{"name":"eth","type":"uint256"},{"name":"contractBalance",'
    '"type":"uint256"}],"name":"calculateEggBuy","outputs":[{"name":"","type":"uint256"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"marketEggs","outputs":[{'
    '"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,'
    '"inputs":[],"name":"sellEggs","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},'
    '{"constant":true,"inputs":[{"name":"amount","type":"uint256"}],"name":"devFee","outputs":[{"name":"",'
    '"type":"uint256"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[],'
    '"name":"seedMarket","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},'
    '{"constant":false,"inputs":[{"name":"ref","type":"address"}],"name":"hatchEggs","outputs":[],"payable":false,'
    '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getMyEggs","outputs":[{'
    '"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,'
    '"inputs":[{"name":"","type":"address"}],"name":"lastHatch","outputs":[{"name":"","type":"uint256"}],'
    '"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"",'
    '"type":"address"}],"name":"claimedEggs","outputs":[{"name":"","type":"uint256"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],'
    '"name":"hatcheryMiners","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view",'
    '"type":"function"},{"constant":true,"inputs":[],"name":"EGGS_TO_HATCH_1MINERS","outputs":[{"name":"",'
    '"type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{'
    '"name":"eth","type":"uint256"}],"name":"calculateEggBuySimple","outputs":[{"name":"","type":"uint256"}],'
    '"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"eggs",'
    '"type":"uint256"}],"name":"calculateEggSell","outputs":[{"name":"","type":"uint256"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],'
    '"name":"referrals","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view",'
    '"type":"function"},{"constant":true,"inputs":[],"name":"ceoAddress2","outputs":[{"name":"","type":"address"}],'
    '"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"adr",'
    '"type":"address"}],"name":"getEggsSinceLastHatch","outputs":[{"name":"","type":"uint256"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"ref","type":"address"}],'
    '"name":"buyEggs","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"inputs":[],'
    '"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')

contract = web3.eth.contract(address=contract_address, abi=abi)


def sellcheck():
    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd,gbp")
    usd_price = response.json()['binancecoin']['usd']

    yours_bal = web3.eth.getBalance(config.my_address)
    yours_bal = web3.fromWei(yours_bal, "ether")

    contracts_bal = contract.functions.getBalance().call()
    contracts_bal = web3.fromWei(contracts_bal, 'ether')

    minerss_bal = contract.functions.hatcheryMiners(config.my_address).call()
    minerss_bal = web3.fromWei(minerss_bal, 'Wei')

    barrels_bal = contract.functions.getEggsSinceLastHatch(config.my_address).call()
    barrels_bal = web3.fromWei(barrels_bal, 'Finney')

    usd = float(usd_price) * float(barrels_bal)

    if usd > config.barrel_limit:
        for _ in trange(10, desc="Selling...", ascii=True,
                        bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
            time.sleep(1)
        nonce = web3.eth.getTransactionCount(config.my_address)
        token_tx = contract.functions.sellEggs().buildTransaction({
            'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce
        })
        sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
        web3.eth.sendRawTransaction(sign_tx.rawTransaction)
        autocompound()
    elif usd < config.barrel_limit:
        clearConsole()
        print("                                          Made by Graymonkey + help from onedevv")
        print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
        print(f"Bnb Balance {yours_bal}")
        print(f"Contract balance: {contracts_bal}")
        print(f"Total Miners: {minerss_bal}\n")
        print(f"${millify(usd, precision=2)} / ${config.barrel_limit}")
        for _ in trange(int(config.sell_check) * 60, desc=f"Waiting for sell check ${config.barrel_limit}", ascii=True,
                        bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
            time.sleep(1)
        autocompound()


def singlecompound():
    clearConsole()
    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd,gbp")
    usd_price = response.json()['binancecoin']['usd']
    gbp_price = response.json()['binancecoin']['gbp']

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    yours_bal = web3.eth.getBalance(config.my_address)
    yours_bal = web3.fromWei(yours_bal, "ether")
    yours_bal = round(yours_bal, 4)

    contracts_bal = contract.functions.getBalance().call()
    contracts_bal = web3.fromWei(contracts_bal, 'ether')
    contracts_bal = round(contracts_bal, 2)

    minerss_bal = contract.functions.hatcheryMiners(config.my_address).call()
    minerss_bal = web3.fromWei(minerss_bal, 'wei')

    barrels_bal = contract.functions.getEggsSinceLastHatch(config.my_address).call()
    barrels_bal = web3.fromWei(barrels_bal, 'Finney')
    barrels_bal = round(barrels_bal, 4)

    usd = float(usd_price) * float(barrels_bal)
    gbp = float(gbp_price) * float(barrels_bal)
    print("                                          Made by Graymonkey + help from onedevv")
    print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
    print(f"Miners compounded at {current_time}\n")
    print(f"Bnb Balance {yours_bal}")
    print(f"Contract balance: {contracts_bal}")
    print(f"Total Miners: {millify(minerss_bal, precision=2)}")
    print(f"Added to TVL: {barrels_bal} ${usd} / £{gbp}")
    nonce = web3.eth.getTransactionCount(config.my_address)
    token_tx = contract.functions.hatchEggs(config.my_address).buildTransaction({
        'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce
    })
    sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
    web3.eth.sendRawTransaction(sign_tx.rawTransaction)


def autocompound():
    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd,gbp")
    usd_price = response.json()['binancecoin']['usd']
    gbp_price = response.json()['binancecoin']['gbp']

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    yours_bal = web3.eth.getBalance(config.my_address)
    yours_bal = web3.fromWei(yours_bal, "ether")
    yours_bal = round(yours_bal, 4)

    contracts_bal = contract.functions.getBalance().call()
    contracts_bal = web3.fromWei(contracts_bal, 'ether')
    contracts_bal = round(contracts_bal, 2)

    minerss_bal = contract.functions.hatcheryMiners(config.my_address).call()
    minerss_bal = web3.fromWei(minerss_bal, 'Wei')

    barrels_bal = contract.functions.getEggsSinceLastHatch(config.my_address).call()
    barrels_bal = web3.fromWei(barrels_bal, 'Finney')
    barrels_bal = round(barrels_bal, 4)

    usd = float(usd_price) * float(barrels_bal)
    your_usd = float(usd_price) * float(yours_bal)
    gbp = float(gbp_price) * float(barrels_bal)

    if your_usd < config.sell_amount:
        if usd > config.barrel_limit:
            nonce = web3.eth.getTransactionCount(config.my_address)
            token_tx = contract.functions.sellEggs().buildTransaction({
                'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce
            })
            sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
            web3.eth.sendRawTransaction(sign_tx.rawTransaction)
            for _ in trange(10, desc="Selling...", ascii=True,
                            bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
                time.sleep(1)
            autocompound()

        else:
            clearConsole()
            print("                                          Made by Graymonkey + help from onedevv")
            print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
            print(f"Bnb Balance {yours_bal}")
            print(f"Contract balance: {contracts_bal}")
            print(f"Total Miners: {minerss_bal}\n")
            print(f"${millify(usd, precision=2)} / ${config.barrel_limit}")
            for _ in trange(int(config.sell_check) * 60, desc=f"Waiting for sell check ${config.barrel_limit}",
                            ascii=True,
                            bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
                time.sleep(1)
            autocompound()

    else:
        clearConsole()
        print("                                          Made by Graymonkey + help from onedevv")
        print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
        print(f"Miners compounded at {current_time}\n")
        print(f"Wallet Balance: {yours_bal} BNB")
        print(f"Contract Balance: {contracts_bal} BNB")
        print(f"Total Miners: {millify(minerss_bal, precision=2)}")
        print(f"Estimated Added to TVL: {barrels_bal} BNB  ${usd} / £{gbp}")
        for _ in trange(config.time * 60, desc="Time left", ascii=True,
                        bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
            time.sleep(1)
        print("Compounding miners...")
        nonce = web3.eth.getTransactionCount(config.my_address)
        token_tx = contract.functions.hatchEggs(config.my_address).buildTransaction({
            'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce
        })
        sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
        web3.eth.sendRawTransaction(sign_tx.rawTransaction)
        autocompound()


def firstautocompound():
    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd,gbp")
    usd_price = response.json()['binancecoin']['usd']

    your_bal = web3.eth.getBalance(config.my_address)
    your_bal = web3.fromWei(your_bal, "ether")
    your_bal = round(your_bal, 4)

    contract_bal = contract.functions.getBalance().call()
    contract_bal = web3.fromWei(contract_bal, 'ether')
    contract_bal = round(contract_bal, 2)

    miners_bal = contract.functions.hatcheryMiners(config.my_address).call()
    miners_bal = web3.fromWei(miners_bal, 'Wei')

    barrel_bal = contract.functions.getEggsSinceLastHatch(config.my_address).call()
    barrel_bal = web3.fromWei(barrel_bal, 'Finney')
    barrel_bal = round(barrel_bal, 4)

    usd = float(usd_price) * float(barrel_bal)
    your_usd = float(usd_price) * float(your_bal)

    if your_usd < config.sell_amount:
        if usd > config.barrel_limit:
            nonce = web3.eth.getTransactionCount(config.my_address)
            token_tx = contract.functions.sellEggs().buildTransaction({
                'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce
            })
            sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
            web3.eth.sendRawTransaction(sign_tx.rawTransaction)
            print("                                          Made by Graymonkey + help from onedevv")
            print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
            print(f"Bnb Balance {your_bal}")
            print(f"Contract balance: {contract_bal}")
            print(f"Total Miners: {miners_bal}\n")
            for _ in trange(10, desc="Selling...", ascii=True,
                            bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
                time.sleep(1)
            firstautocompound()

        else:
            clearConsole()
            print("                                          Made by Graymonkey + help from onedevv")
            print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
            print(f"Bnb Balance {your_bal}")
            print(f"Contract balance: {contract_bal}")
            print(f"Total Miners: {miners_bal}\n")
            print(f"${millify(usd, precision=2)} / ${config.barrel_limit}")
            for _ in trange(int(config.sell_check) * 60, desc=f"Waiting for sell check ${config.barrel_limit}",
                            ascii=True,
                            bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
                time.sleep(1)
            autocompound()
    else:
        clearConsole()
        print("                                          Made by Graymonkey + help from onedevv")
        print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
        print(f"Wallet Balance: {your_bal} BNB")
        print(f"Contract Balance: {contract_bal} BNB")
        print(f"Total Miners: {millify(miners_bal, precision=2)}\n")
        for _ in trange(config.time * 60, desc="Time left", ascii=True,
                        bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
            time.sleep(1)
        print("Compounding miners...")
        nonce = web3.eth.getTransactionCount(config.my_address)
        token_tx = contract.functions.hatchEggs(config.my_address).buildTransaction({
            'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce
        })
        sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
        web3.eth.sendRawTransaction(sign_tx.rawTransaction)
        autocompound()


def sell():
    clearConsole()
    a = input("Are you sure you want to sell? Y/N ").upper()
    if a == "Y":
        print("a")
        nonce = web3.eth.getTransactionCount(config.my_address)
        token_tx = contract.functions.sellEggs().buildTransaction({
            'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce
        })
        sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
        web3.eth.sendRawTransaction(sign_tx.rawTransaction)
        for _ in trange(10, desc="Selling...", ascii=True,
                        bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
            time.sleep(1)
        clearConsole()
        run()
    elif a == "N":
        clearConsole()
        run()


def donate():
    clearConsole()
    print("                                          Made by Graymonkey + help from onedevv")
    print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
    amount = input("Amount of BNB you wish to donate: ")
    confirm = input(f"Are you sure you want to donate {amount} Y/N: ").upper()
    if confirm == "Y":
        print("a")
        nonce = web3.eth.getTransactionCount(config.my_address)
        token_tx = {
            'chainId': 56, 'gas': config.gas_limit, 'gasPrice': web3.toWei(config.gas_price, 'gwei'), 'nonce': nonce,
            'to': "0x3173BD2e04eD839b6eA3CccE0179f77A3C39dd4f", 'value': web3.toWei(amount, 'ether')
        }
        sign_tx = web3.eth.account.signTransaction(token_tx, private_key=config.private)
        web3.eth.sendRawTransaction(sign_tx.rawTransaction)
        for _ in trange(10, desc="Sending donation...", ascii=True,
                        bar_format="{l_bar}{remaining} {bar} ETA: {eta}", ncols=100):
            time.sleep(1)
        clearConsole()
        run()
    elif confirm == "N":
        clearConsole()
        run()


def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def run():
    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids=binancecoin&vs_currencies=usd,gbp")
    usd_price = response.json()['binancecoin']['usd']
    gbp_price = response.json()['binancecoin']['gbp']

    your_bal = web3.eth.getBalance(config.my_address)
    your_bal = web3.fromWei(your_bal, "ether")
    your_bal = round(your_bal, 4)
    contract_bal = contract.functions.getBalance().call()
    contract_bal = web3.fromWei(contract_bal, 'ether')
    contract_bal = round(contract_bal, 2)

    miners_bal = contract.functions.hatcheryMiners(config.my_address).call()
    miners_bal = web3.fromWei(miners_bal, 'wei')

    barrel_bal = contract.functions.getEggsSinceLastHatch(config.my_address).call()
    barrel_bal = web3.fromWei(barrel_bal, 'Finney')
    barrel_bal = round(barrel_bal, 4)
    usd = float(usd_price) * float(barrel_bal)
    gbp = float(gbp_price) * float(barrel_bal)
    print(colored(pyfiglet.figlet_format("BNB COMPOUNDER", justify="center"), 'yellow'))
    print(f"Wallet Balance: {your_bal} BNB")
    print(f"Contract Balance: {contract_bal} BNB")
    print(f"Total Miners: {millify(miners_bal, precision=2)}")
    print(f"Estimated Barrel Balance: {barrel_bal} BNB")
    print("\nPress 1 to do a single compound")
    print(f"Press 2 to autocompound every {config.time} minutes")
    print(f"Press 3 to sell your barrel EST {barrel_bal} ${millify(usd, precision=2)} / £{millify(gbp, precision=2)}")
    print("Press 4 to donate")
    print("Press 5 to quit")
    choice = input("Input: ")
    if choice == "1":
        singlecompound()
    elif choice == "2":
        firstautocompound()
    elif choice == "3":
        sell()
    elif choice == "4":
        donate()
    elif choice == "5":
        quit()
    run()


clearConsole()
print("                                          Made by Graymonkey + help from onedevv")
run()
