from flask import Flask, request, jsonify
from flask_cors import CORS
from mcdns import MultiChainDomainClient
import os

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize the MultiChain client
rpchost = '127.0.0.1'
rpcport = 4384
rpcuser = 'multichainrpc'
rpcpassword = "4k9JWfdcci31RmSxoki79LPj9STZMMa1Gw56QYuL5Aer"
usessl = False

client = MultiChainDomainClient(rpchost, rpcport, rpcuser, rpcpassword)
client.setoption("chainname", "dns")

# Ensure stream exists on startup
@app.before_first_request
def initialize_stream():
    client.create_stream_if_not_exists()

@app.route('/api/domains', methods=['GET'])
def get_all_domains():
    try:
        items = client.getallitems()
        
        # Fix: Properly structure domain data
        domains = []
        domain_dict = {}
        
        for item in items:
            key = item.get('keys', [None])[0]  # Get the first key (domain name)
            if key:
                # Check if we've already processed this domain
                if key not in domain_dict:
                    # If this is the first record for this domain, use the latest data
                    domain_data = {
                        'domain': key,
                        'owner': item.get('data', {}).get('json', {}).get('owner', 'Unknown'),
                        'ip': item.get('data', {}).get('json', {}).get('ip', 'N/A'),
                        'status': item.get('data', {}).get('json', {}).get('status', 'active'),
                        'txid': item.get('txid', ''),
                        'timestamp': item.get('blocktime', 0)
                    }
                    domain_dict[key] = domain_data
                    domains.append(domain_data)
                else:
                    # If we have already seen this domain, update if this record is newer
                    if item.get('blocktime', 0) > domain_dict[key]['timestamp']:
                        domain_dict[key]['owner'] = item.get('data', {}).get('json', {}).get('owner', 'Unknown')
                        domain_dict[key]['ip'] = item.get('data', {}).get('json', {}).get('ip', 'N/A')
                        domain_dict[key]['status'] = item.get('data', {}).get('json', {}).get('status', 'active')
                        domain_dict[key]['txid'] = item.get('txid', '')
                        domain_dict[key]['timestamp'] = item.get('blocktime', 0)
        
        return jsonify({"status": "success", "domains": list(domain_dict.values())})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/domains/<domain_name>', methods=['GET'])
def get_domain_info(domain_name):
    try:
        items = client.liststreamkeyitems(client.stream_name, domain_name)
        
        if not items:
            return jsonify({"status": "error", "message": "Domain not found"}), 404
        
        # Get the most recent item (latest state of the domain)
        latest_item = max(items, key=lambda x: x['blocktime'])
        
        domain_info = {
            'domain': domain_name,
            'owner': latest_item.get('data', {}).get('json', {}).get('owner', 'Unknown'),
            'ip': latest_item.get('data', {}).get('json', {}).get('ip', 'N/A'),
            'status': latest_item.get('data', {}).get('json', {}).get('status', 'active'),
            'txid': latest_item.get('txid', ''),
            'timestamp': latest_item.get('blocktime', 0),
            'history': [
                {
                    'owner': item.get('data', {}).get('json', {}).get('owner', 'Unknown'),
                    'ip': item.get('data', {}).get('json', {}).get('ip', 'N/A'),
                    'status': item.get('data', {}).get('json', {}).get('status', 'active'),
                    'txid': item.get('txid', ''),
                    'timestamp': item.get('blocktime', 0)
                }
                for item in items
            ]
        }
        
        return jsonify({"status": "success", "domain_info": domain_info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/domains', methods=['POST'])
def register_domain():
    try:
        data = request.json
        domain_name = data.get('domain')
        owner = data.get('owner')
        ip = data.get('ip', 'N/A')
        
        if not domain_name or not owner:
            return jsonify({"status": "error", "message": "Domain name and owner are required"}), 400
        
        # Check if domain already exists
        existing_items = client.liststreamkeyitems(client.stream_name, domain_name)
        
        if existing_items:
            return jsonify({"status": "error", "message": "Domain already registered"}), 409
        
        # Register the domain with action and new_owner
        txid = client.publish(
            client.stream_name,
            domain_name,
            {"json": {"owner": owner, "ip": ip, "status": "active", "action": "register", "new_owner": owner}}
        )
        
        return jsonify({"status": "success", "txid": txid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/domains/<domain_name>/transfer', methods=['POST'])
def transfer_domain(domain_name):
    try:
        data = request.json
        new_owner = data.get('new_owner')
        current_owner = data.get('current_owner')
        
        if not new_owner:
            return jsonify({"status": "error", "message": "New owner is required"}), 400
        
        # Check if domain exists and get current owner
        existing_items = client.liststreamkeyitems(client.stream_name, domain_name)
        
        if not existing_items:
            return jsonify({"status": "error", "message": "Domain not found"}), 404
        
        latest_item = max(existing_items, key=lambda x: x['blocktime'])
        domain_owner = latest_item.get('data', {}).get('json', {}).get('owner', '')
        ip = latest_item.get('data', {}).get('json', {}).get('ip', 'N/A')
        
        if current_owner != domain_owner:
            return jsonify({"status": "error", "message": "You are not the owner of this domain"}), 403
        
        # Transfer the domain with action, previous_owner, and new_owner
        txid = client.publish(
            client.stream_name,
            domain_name,
            {"json": {"owner": new_owner, "ip": ip, "status": "active", "action": "transfer", "previous_owner": current_owner, "new_owner": new_owner}}
        )
        
        return jsonify({"status": "success", "txid": txid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/domains/<domain_name>/history', methods=['GET'])
def get_domain_history(domain_name):
    try:
        history = client.get_domain_history(domain_name)
        return jsonify({
            'status': 'success',
            'domain': domain_name,
            'history': history
        })
    except Exception as e:
        print(f"Error in get_domain_history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)