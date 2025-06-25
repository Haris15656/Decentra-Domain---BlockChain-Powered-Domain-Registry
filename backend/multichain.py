# MultiChain JSON-RPC API Library for Python
# Copyright (c) Coin Sciences Ltd - www.multichain.com
# All rights reserved under BSD 3-clause license

from urllib import request
from urllib import error
import base64 
import json
from collections import OrderedDict
import time
import ssl

default_error_code = 502

class MultiChainClient:
    def __init__(self, host, port, username, password, usessl=False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.usessl = usessl
        
        self.chainname = None
        self.verifyssl = True
        
        self.error_code = 0
        self.error_message = ""        

    def setoption(self, option, value):       
        if option == "chainname":        
            self.chainname = value
        if option == "verifyssl":        
            self.verifyssl = value
            
    def api_wrapper(self, method):
        def api_caller(*args):
            # Validate arguments aren't functions
            for arg in args:
                if callable(arg):
                    self.error_code = -1
                    self.error_message = "Function passed as argument where data expected"
                    return None
                    
            url = "https" if self.usessl else "http"                
            url += "://" + self.host + ":" + str(self.port)
            userpass64 = base64.b64encode((self.username + ":" + self.password).encode("ascii")).decode("ascii")
            
            headers = {
                "Content-Type": "application/json",
                "Connection": "close",
                "Authorization": "Basic " + userpass64
            }
                
            api_request = {
                "id": int(round(time.time() * 1000)),
                "method": method,
                "params": args
            }
            
            if self.chainname:
                api_request["chain_name"] = self.chainname
                
            try:
                payload = json.dumps(api_request)
            except TypeError as e:
                self.error_code = -1
                self.error_message = f"JSON serialization error: {str(e)}"
                return None
                
            headers["Content-Length"] = str(len(payload))
    
            try:
                data = payload.encode('utf-8')
                ureq = request.Request(url, data=data)
    
                for header, value in headers.items():
                    ureq.add_header(header, value)
    
                if self.verifyssl:
                    req = request.urlopen(ureq)
                else:
                    context = ssl._create_unverified_context()                    
                    req = request.urlopen(ureq, context=context)
    
            except error.HTTPError as e:
                self.error_code = e.getcode()      
                self.error_message = e.reason
                
                resp = e.read()                                      
                if resp:
                    try:
                        req_json = json.loads(resp.decode('utf-8'))
                        if req_json['error'] is not None:
                            self.error_code = req_json['error']['code']
                            self.error_message = req_json['error']['message']
                            if self.error_code == -1 and self.error_message.find("\n\n") >= 0:
                                self.error_message = "Wrong parameters. Usage:\n\n" + self.error_message
                    except:
                        pass
                return None
                
            except error.URLError as e:
                self.error_code = default_error_code
                self.error_message = str(e.reason)
                return None
                
            resp = req.read()      
            try:
                req_json = json.loads(resp.decode('utf-8'), object_pairs_hook=OrderedDict)
                return req_json['result']
            except:
                self.error_code = -1
                self.error_message = "Invalid JSON response"
                return None

        return api_caller
    
    def __getattr__(self, method):
        return self.api_wrapper(method)
    
    def errorcode(self):
        return self.error_code
        
    def errormessage(self):
        return str(self.error_message)  # Ensure string output
        
    def success(self):
        return self.error_code == 0