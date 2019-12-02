import mysql
import random
import json
import http.client
import http.server
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import base64

from http.server import BaseHTTPRequestHandler, HTTPServer



#USING GOJEK UNOFFICIAL WRAPPER
from account import *
from payment import *
from config import (set_token, get_token)

#import utk parsing url path
from urllib.parse import urlparse



def getProfile():
    options = {
        'method' : 'GET'
    }
    return request(options, 'wallet/profile')

def getHistory():
    #HISTORY 100 TRANSAKSI TERAKHIR
    options = {
        'method' : 'GET'
    }
    return request(options, 'wallet/history?page=1&limit=100')

login_token = None
login_data = None
atoken = config.get_token()
qr_trf = '5a56128c-59e1-4fd5-9b6b-df2e764b9f57' #Punya Jason Alfian
class RequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
      """ Sets headers required for CORS """
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
      self.send_header("Access-Control-Allow-Headers", "X-Requested.With")

    def send_dict_response(self, d):
        """ Sends a dictionary (JSON) back to the client """
        self.wfile.write(bytes(dumps(d), "utf8"))


    def do_POST(self):
        global login_token
        global login_data
        parsed_query = urlparse(self.path)
        path = parsed_query.path
        query = parsed_query.query
        query_components = dict(qc.split("=") for qc in urlparse(self.path).query.split("&"))
        if path == '/login' :
            if query == '' :
                #penangan request tanpa query
                print('No Query')
                self.send_response(422) #Unprocessable Entity
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error":true,"message":"no query."}')
                return None
            else :
                #penanganan request dengan query ID
                param = query.split('=')[0]
                if param == 'phone':
                    print('IN: Parameter \'phone\'')

                    #login with phone Number
                    phone = query_components.get('phone')
                    countryCode = '+62'
                    phoneNum = countryCode + phone[1:]
                    login_data = login_with_phone(phoneNum)

                    #jika no hp tidak terdaftar
                    if (login_data.get("data") == None):
                        self.send_response(401)
                        self._send_cors_headers()
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b'{"error":true,"message":user is not registered"' )
                        return None
                    else: #no hp terdaftar
                        self.send_response(200)
                        self._send_cors_headers()
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        login_token = login_data.get("data").get("login_token")
                        login_data = json.dumps(login_data)

                        #Login Log
                        f = open("output_login_log.json", "w")
                        print(f.write(login_data))
                        print(f.write("\n"))
                        self.wfile.write(login_data.encode('utf-8'))
                        f.close()

                    print(login_data)
                    
                else :
                    print('Failed to Enter param \'phone\'')
                    self.send_response(422) #Unprocessable Entity
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error":true,"message":"no parameter."}')
                    return None
                
        elif path == '/loginOTP':
            if query == '' :
                #penangan request tanpa query
                print('No Query')
                self.send_response(415) #Unsupported Media type
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error":true,"message":"no query."}')
                return None
            else:
                global atoken
                param = query.split('=')[0]
                if param == 'otp':
                    print('IN: Parameter \'otp\'')
                    
                    #Assign OTP dari SMS (manual)
                    otp = query_components.get('otp')
                    
                    #input OTP
                    self.send_response(200)
                    self._send_cors_headers()
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    customer_data = generater_costumer_token(otp, login_token)
                    print(customer_data)
                    
                    if (customer_data == None):
                        print("Login Gagal")
                        exit()
                    else:
                        atoken = customer_data.get("data").get("access_token")
                        config.set_token(atoken)
                        print("acc token: ", atoken)
                        print('Login Berhasil')
                else :
                    print('Failed to Enter param \'otp\'')
                    self.send_response(422) #Unprocessable Entity
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error":true,"message":"no parameter."}')
                    return None    
        elif path == '/transfer':
        #akan transfer ke rekening GOPAY qr_trf
            if query == '' :
                #penangan request tanpa query
                print('No Query')
                self.send_response(415) #Unsupported Media type
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error":true,"message":"no query."}')
                return None
            else :
                #cek status login
                if (atoken == None): #tidak ada akun login
                    print("Tidak ada akun")
                    exit()
                else: #akun sudah login
                    print("acc token: ", atoken)
                    print('Akun siap transfer')
                    amount = query_components.get('amount') 
                    pin = query_components.get('pin')

                    if (amount == None or pin == None):
                        #error
                        print('No Transfer Parameter')
                        self.send_response(422) #Unprocessable Entity
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(b'{"error":true,"message":"no parameter."}')
                        return None
                    else:
                        #transfer
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()

                        description = 'Transfer sebesar ' + amount
                        trf_gopay = transfer_gopay(qr_trf, amount, description, pin)        
                        
                        print('Transfer Sukses')

        else:
            self.send_response(404) #Not found
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":true,"message":"no such path."}')
            return None

    def do_GET(self):
        parsed_query = urlparse(self.path)
        path = parsed_query.path
        query = parsed_query.query
        if path == '/balance' :
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            myProfile = getProfile()
            myProfile = json.dumps(myProfile)
            self.wfile.write(myProfile.encode('utf-8'))
        elif path == '/history' :
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            myHistory = getHistory()
            myHistory = json.dumps(myHistory)
            self.wfile.write(myHistory.encode('utf-8'))

            f = open("output_history.json", "w")
            print(f.write(myHistory))
            print(f.write("\n"))
            self.wfile.write(myHistory.encode('utf-8'))
            f.close()
        else:
            self.send_response(404) #Not found
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":true,"message":"no such path."}')
            return None

    def do_DELETE(self):
        global atoken
        parsed_query = urlparse(self.path)
        path = parsed_query.path
        query = parsed_query.query
        #query_components = dict(qc.split("=") for qc in query.split("&"))
        if path == '/logout' :
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            logout_data = logout()
            print(logout_data)
            config.set_token('')
            print("Berhasil Logout")
        else:
            self.send_response(404) #Not found
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":true,"message":"no such path."}')
            return None

    def do_OPTIONS(self):
        self.send_response(200)
        # self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS,DELETE")
        self.send_header("Access-Control-Allow-Headers","X-Requested-With, Content-Type")
        self.end_headers()
        
    
port = 9977
with HTTPServer(("",port), RequestHandler) as httpd:
    try:
        # httpd.socket = ssl.wrap_socket(httpd.socket, 
        #                             keyfile = "privateKey.key", 
        #                             certfile = "certificate.crt", 
        #                             server_side=True)
        print("serving at port ",port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("CTRL+C Pressed")
        httpd.socket.close()
