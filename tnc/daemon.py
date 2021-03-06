#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 16:58:45 2020

@author: DJ2LS

"""


import argparse
import threading
import socketserver
import pyaudio
import time
import json
import subprocess
import os
import static

#PORT = 3001
#TNCPROCESS = 0
#TNCSTARTED = False

#p = pyaudio.PyAudio()
#info = p.get_host_api_info_by_index(0)
#numdevices = info.get('deviceCount')
#for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
#for i in range (0,numdevices):
#        if p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
#                print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'))#
#
#        if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
#                print("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'))

def start_daemon():

    try:
        print("SRV | STARTING TCP/IP SOCKET FOR CMD ON PORT: " + str(PORT))
        socketserver.TCPServer.allow_reuse_address = True  # https://stackoverflow.com/a/16641793
        daemon = socketserver.TCPServer(('0.0.0.0', PORT), CMDTCPRequestHandler)
        daemon.serve_forever()

    finally:
        daemon.server_close()
        
        
class CMDTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print("Client connected...")    
        
        # loop through socket buffer until timeout is reached. then close buffer
        socketTimeout = time.time() + 3
        while socketTimeout > time.time():

            time.sleep(0.01)
            encoding = 'utf-8'
            #data = str(self.request.recv(1024), 'utf-8')

            data = bytes()
            
            # we need to loop through buffer until end of chunk is reached or timeout occured
            while True and socketTimeout > time.time():
                chunk = self.request.recv(1024)  # .strip()
                data += chunk
                if chunk.endswith(b'\n'):
                    break
            data = data[:-1]  # remove b'\n'
            data = str(data, 'utf-8')
            #print(data)
            
            if len(data) > 0:
                socketTimeout = time.time() + 3
            
            # convert data to json object
            # we need to do some error handling in case of socket timeout
            
            try:
                received_json = json.loads(data)

            except:
                received_json = ''

            

            # GET COMMANDS
            # "command" : "..."
            
            # SET COMMANDS
            # "command" : "..."
            # "parameter" : " ..."
            
            # DATA COMMANDS
            # "command" : "..."
            # "type" : "..."
            # "dxcallsign" : "..."
            # "data" : "..."
            
            # print(received_json)
            #print(received_json["type"])
            #print(received_json["command"]) 
            try:
                print(static.TNCSTARTED)




                if received_json["type"] == 'SET' and received_json["command"] == 'STARTTNC' and not static.TNCSTARTED:
                    rx_audio = received_json["parameter"][0]["rx_audio"]
                    tx_audio = received_json["parameter"][0]["tx_audio"]
                    deviceid = received_json["parameter"][0]["deviceid"]
                    deviceport = received_json["parameter"][0]["deviceport"]
                    ptt = received_json["parameter"][0]["ptt"]
                    print("STARTING TNC !!!!!")
                    print(received_json["parameter"][0])
                    #os.system("python3 main.py --rx 3 --tx 3 --deviceport /dev/ttyUSB0 --deviceid 2028")
                    p = subprocess.Popen("exec python3 main.py --rx "+ str(rx_audio) +" --tx "+ str(tx_audio) +" --deviceport "+ str(deviceport) +" --deviceid "+ str(deviceid) + " --ptt "+ str(ptt), shell=True)
                    static.TNCPROCESS = p#.pid
                    #print(parameter)
                    # print(static.TNCPROCESS)
                    static.TNCSTARTED = True

                if received_json["type"] == 'SET' and received_json["command"] == 'STOPTNC':
                    parameter = received_json["parameter"]
                    static.TNCPROCESS.kill()
                    print("KILLING PROCESS ------------")
                    #os.kill(static.TNCPROCESS, signal.SIGKILL)
                    static.TNCSTARTED = False
                    
                if received_json["type"] == 'GET' and received_json["command"] == 'DAEMON_STATE':

                    data = {'COMMAND' : 'DAEMON_STATE', 'DAEMON_STATE' : [], 'INPUT_DEVICES': [], 'OUTPUT_DEVICES': []}

                    if static.TNCSTARTED:
                        data["DAEMON_STATE"].append({"STATUS": "running"})
                    else:
                        data["DAEMON_STATE"].append({"STATUS": "stopped"})

                    p = pyaudio.PyAudio()
                    for i in range(0, p.get_device_count()):
                        
                        maxInputChannels = p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')
                        maxOutputChannels = p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')
                        name = p.get_device_info_by_host_api_device_index(0,i).get('name')  
                        
                        if maxInputChannels > 0:                        
                            data["INPUT_DEVICES"].append({"ID": i, "NAME" : name})  
                        if maxOutputChannels > 0:                        
                            data["OUTPUT_DEVICES"].append({"ID": i, "NAME" : name})  
                          
          

                    #print(data)
                    jsondata = json.dumps(data)
                    self.request.sendall(bytes(jsondata, encoding))
                
              
            
            #exception, if JSON cant be decoded
            except Exception as e:
                print('PROGRAM ERROR: %s' %str(e))
                print("Wrong command") 

        print("Client disconnected...")


if __name__ == '__main__':


    # --------------------------------------------GET PARAMETER INPUTS
    PARSER = argparse.ArgumentParser(description='Simons TEST TNC')
    PARSER.add_argument('--port', dest="socket_port", default=3001, help="Socket port", type=int)

    ARGS = PARSER.parse_args()
    PORT = ARGS.socket_port

    # --------------------------------------------START CMD SERVER

    DAEMON_THREAD = threading.Thread(target=start_daemon, name="daemon")
    DAEMON_THREAD.start()
    
    
    
    
    

