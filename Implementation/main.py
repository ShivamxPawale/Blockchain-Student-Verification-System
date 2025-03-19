from flask import Flask, request, jsonify
from web3 import Web3

app = Flask(__name__)

# Connect to Ganache Local Blockchain
ganache_url = "HTTP://127.0.0.1:7545"  # Ensure Ganache is running
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Load Smart Contract
contract_address = "0x383d4fbC4F33f3Df61f40c08dF6fFe026DEB83FE"  # Update with actual contract address
contract_abi = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "string",
          "name": "uhi",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        }
      ],
      "name": "StudentRegistered",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "string",
          "name": "uhi",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "bool",
          "name": "isValid",
          "type": "bool"
        }
      ],
      "name": "StudentVerified",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_instituteCode",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_uhi",
          "type": "string"
        }
      ],
      "name": "registerStudent",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_uhi",
          "type": "string"
        }
      ],
      "name": "verifyStudent",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)
web3.eth.default_account = web3.eth.accounts[0]  # Using first account from Ganache


@app.route('/register', methods=['POST'])
def register_student():
    data = request.json
    name = data.get("name")
    institute_code = data.get("instituteCode")
    uhi = data.get("uhi")

    try:
        tx_hash = contract.functions.registerStudent(name, institute_code, uhi).transact()
        web3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({"message": "Student registered successfully", "tx_hash": tx_hash.hex()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/verify', methods=['POST'])
def verify_student():
    data = request.json
    name = data.get("name")
    uhi = data.get("uhi")

    try:
        is_registered = contract.functions.verifyStudent(name, uhi).call()
        return jsonify({"isRegistered": is_registered}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
