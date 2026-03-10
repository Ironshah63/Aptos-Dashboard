from flask import Flask, request, jsonify
from aptos_sdk.account import Account
from aptos_sdk.client import FaucetClient, RestClient

app = Flask(__name__)

SHELBY_FAUCET_URL = "https://faucet.testnet.aptoslabs.com"
SHELBY_NODE_URL = "https://fullnode.shelby.aptoslabs.com"

# Initialize Aptos clients
faucet_client = FaucetClient(SHELBY_FAUCET_URL)
rest_client = RestClient(SHELBY_NODE_URL)

# Endpoint to create a new wallet/account
@app.route('/create-account', methods=['POST'])
def create_account():
    account = Account.generate()  # Generate a new Aptos account
    return jsonify({
        'public_key': account.public_key(),
        'private_key': account.private_key(),
        'address': account.address()
    })

# Endpoint to fund account with Shelby Testnet faucet
@app.route('/fund-account', methods=['POST'])
def fund_account():
    data = request.json
    address = data.get('address')

    if not address:
        return jsonify({'error': 'Address is required'}), 400
    
    try:
        # Fund the account via the Shelby faucet
        faucet_client.fund_account(address, 100_000_000)  # Fund 100 APT test tokens
        return jsonify({'message': f'Account {address} funded successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get account balance
@app.route('/account-balance', methods=['GET'])
def account_balance():
    address = request.args.get('address')

    if not address:
        return jsonify({'error': 'Address is required'}), 400
    
    try:
        # Fetch the balance from the Shelby testnet
        resources = rest_client.get_account_resources(address)
        for resource in resources:
            if resource['type'] == "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>":
                balance = resource['data']['coin']['value']
                return jsonify({'address': address, 'balance': balance})
        return jsonify({'address': address, 'balance': 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to send a transaction
@app.route('/send-transaction', methods=['POST'])
def send_transaction():
    data = request.json
    sender_private_key = data.get('sender_private_key')
    receiver_address = data.get('receiver_address')
    amount = data.get('amount')

    if not sender_private_key or not receiver_address or not amount:
        return jsonify({'error': 'Sender private key, receiver address, and amount are required'}), 400
    
    try:
        sender = Account.load_key(sender_private_key)
        txn_hash = rest_client.transfer(sender, receiver_address, int(amount))
        return jsonify({'transaction_hash': txn_hash})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)