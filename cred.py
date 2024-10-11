#establish breeze connection
from breeze_connect import BreezeConnect
import json

class cred():

    PATH = "/Users/amitmhatre/Documents/BreezeCreds/"
    FILE = "credaparna"

    def __init__(self):
        super().__init__()
        self.session_token = None
        self.app_key = None
        self.secret_key = None
        self.breeze = None
        # load credentials from JSON file
        f = open (self.PATH+self.FILE+".json", "r")
        data = f.read()
        json_data = json.loads(data)
        f.close()
        self.session_token = json_data['session_token']
        self.app_key = json_data['app_key']
        self.secret_key = json_data['secret_key']
        cred.breeze_session = BreezeConnect(api_key=self.app_key)        

    def check_session(self):
        try:
            cred.breeze_session.generate_session(api_secret=self.secret_key, session_token=self.session_token)
            return 200
        except:
            return 400
        
    def get_session(self):
        return cred.breeze_session
    
    def reinitiate_session(self,session_token):
        json_data = {}
        try:
            cred.breeze_session.generate_session(api_secret=self.secret_key, session_token=session_token)
            print ("=======Breeze session Connected=======")
            json_data['session_token'] = session_token
            json_data['app_key'] = self.app_key
            json_data['secret_key'] = self.secret_key
            f = open(self.PATH+self.FILE+".json",'w')
            print(json.dumps(json_data),file=f)   
            f.close()         
            return 200
        except:
            print ("=======Breeze session FAILED!!!=======")
            return 400
