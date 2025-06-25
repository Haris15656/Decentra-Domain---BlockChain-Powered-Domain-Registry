from multichain import MultiChainClient
import json
import os

class MultiChainDomainClient(MultiChainClient):
    def __init__(self, host, port, username, password, usessl=False):
        super().__init__(host, port, username, password, usessl)
        self.stream_name = "dn_stream"
        self.log_file = "domain_stream_log.json"
        self._initialize_log_file()

    def _initialize_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump({}, f, indent=4)
    
    def getallitems(self):
        return self.liststreamitems(self.stream_name)
    
    def create_stream_if_not_exists(self):
        try:
            # Check if the stream exists
            existing_streams = self.liststreams(self.stream_name)
            
            # If stream doesn't exist, create it
            if not existing_streams:
                stream_txid = self.create(
                    stream=self.stream_name,
                    open=True,
                    details={"purpose": "Domain name registration system"}
                )
                return f"Created stream {self.stream_name}: {stream_txid}"
            
            return f"Stream {self.stream_name} already exists"
        except Exception as e:
            return f"Error creating stream: {str(e)}"
    
    def _update_log_file(self):
        try:
            # Check if the stream exists
            existing_stream = self.liststreams(self.stream_name)
            if not existing_stream:
                print(f"Stream '{self.stream_name}' does not exist.")
                return  # Exit the method if the stream doesn't exist

            # Fetch all items from the stream
            all_items = self.liststreamitems(self.stream_name)
            print(all_items)
            # If no items, initialize empty
            if not all_items:
                with open(self.log_file, "w") as f:
                    json.dump({}, f, indent=4)
                return

            # Process items and organize by domain name (key)
            domains = {}
            for item in all_items:
                key = item.get('keys', [None])[0]  # Get the domain name
                if key:
                    if key not in domains:
                        domains[key] = []
                    domains[key].append({
                        'txid': item.get('txid', ''),
                        'owner': item.get('data', {}).get('json', {}).get('owner', 'Unknown'),
                        'ip': item.get('data', {}).get('json', {}).get('ip', 'N/A'),
                        'status': item.get('data', {}).get('json', {}).get('status', 'active'),
                        'timestamp': item.get('blocktime', 0)
                    })

            # Write updated data to log file
            with open(self.log_file, "w") as f:
                json.dump(domains, f, indent=4)

        except Exception as e:
            print(f"Error updating log file: {str(e)}")

    def get_domain_history(self, domain_name):
        """
        Gets the complete transaction history for a specific domain name
        """
        try:
            # Get all transactions for this domain from the stream
            raw_history = self.liststreamkeyitems(self.stream_name, domain_name)
            
            # Format the history records for frontend consumption
            history = []
            for item in raw_history:
                data = item.get('data', {})
                if isinstance(data, str):
                    try:
                        import json
                        data = json.loads(data)
                    except:
                        data = {}

                history.append({
                    'txid': item.get('txid', ''),
                    'timestamp': item.get('blocktime', 0),
                    'blockheight': item.get('blockheight', 'N/A'),
                    'confirmations': item.get('confirmations', 0),
                    'action': data.get('action', 'register'),
                    'owner': data.get('owner', 'Unknown'),
                    'ip': data.get('ip', 'N/A'),
                    'status': data.get('status', 'active'),
                    'previous_owner': data.get('previous_owner', None),
                    'new_owner': data.get('new_owner', None)
                })
            
            # Sort by timestamp (newest first)
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            return history
            
        except Exception as e:
            print(f"Error getting domain history: {e}")
            return []