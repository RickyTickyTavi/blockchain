from flask import Flask, jsonify, request
import json
from uuid import uuid4 
import hashlib
import requests
from time import time
from urllib.parse import urlparse

class Blockchain:
    def __init__(myBC):
        myBC.current = []
        myBC.bChain = []
        myBC.nodes = set()
        myBC.newBlock(prevHash='1', pow=100)

    def newBlock(myBC, pow, prevHash):
        block = {
            'index': len(myBC.bChain) + 1,
            'timestamp': time(),
            'transactions': myBC.current,
            'pow': pow,
            'prevHash': prevHash or myBC.hashItOut(myBC.bChain[-1]),
        }
        myBC.current=[]
        myBC.bChain.append(block)
        return block
        
        
    def newTrans(myBC, theSender, theRecipient, theAmount):
        myBC.current.append({
            'theSender': theSender,
            'theRecipient': theRecipient,
            'theAmount': theAmount,})
        return myBC.prevBlock['index'] + 1

    @property
    def prevBlock(myBC):
        return myBC.bChain[-1]


    @staticmethod
    def hashItOut(block):
        blockStr = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockStr).hexdigest()
        
    def proofOfWork(myBC, prevBlock):
        prevProof = prevBlock['pow']
        prevHash = myBC.hashItOut(prevBlock)
        pow = 0
        
        while myBC.validate(prevProof, pow, prevHash) is False:
            pow += 1

        return pow
       
    @staticmethod
    def validate(prevProof, pow, prevHash):
        singleGuess = f'{prevProof}{pow}{prevHash}'.encode()
        singleGuessHash = hashlib.sha256(singleGuess).hexdigest()
        return singleGuessHash[:4] == "0000"

        
# ###################################################################################################        

        
project = Flask(__name__)
project.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
nodeId = str(uuid4()).replace('-', '')
myFirstChain = Blockchain()


# ###################################################################################################



@project.route('/wholechain', methods=['GET'])
def full_chain():
    response = {
        'Block chain': myFirstChain.bChain,
        'chain length': len(myFirstChain.bChain),
    }
    return jsonify(response), 200

# ###################

@project.route('/new', methods=['POST'])
def newTrans():
    values = request.get_json()
    required = ['theSender', 'theRecipient', 'theAmount']

    index = myFirstChain.newTrans(values['theSender'], values['theRecipient'], values['theAmount'])

    response = {'message': f'The new transaction has been added to block {index}'}
    return jsonify(response), 201

# ###############

@project.route('/mineblock', methods=['GET'])
def mine():
    prevBlock = myFirstChain.prevBlock
    pow = myFirstChain.proofOfWork(prevBlock)
    myFirstChain.newTrans(
        theSender="0",
        theRecipient = nodeId,
        theAmount=1,
    )

    prevHash = myFirstChain.hashItOut(prevBlock)
    block = myFirstChain.newBlock(pow, prevHash)
    response = {
        'message': "New Block Completed",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof of work': block['pow'],
        'previous hash': block['prevHash'],
    }
    return jsonify(response), 200

# ###########################

if __name__ == '__main__':
    from argparse import ArgumentParser

    argParse = ArgumentParser()
    argParse.add_argument('-p', '--port', default=5000, type=int, help='the listening port')
    args = argParse.parse_args()
    portNum = args.port

    project.run(host='127.0.0.1', port=portNum)