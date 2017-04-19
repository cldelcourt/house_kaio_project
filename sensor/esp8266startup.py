try:
    import usocket as socket
except:
    import socket
import os
#import network 

CONFIG_PATH = "wifi.cfg"
WIFI_SSID = ""
WIFI_PASSWORD = ""
MQTT_HOST = "192.168.1.168"
SENSOR_NAME = "security001"
SENSOR_TOPIC = "security"
CONFIG = dict()

index = '''HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n
<html>
    <head>
    </head>
    <body>
        <form action="/" method="POST" form="espForm">
            WIFI SSID:<br>
            <input type="text" name="ssid"><br>
            <p>WIFI Password:<p>
            <input type="text" name="wifiPassword">
            <p>Sensor Name:<p>
            <input type="text" name="sensorName">
            <p>Sensor Topic:<p>
            <input type="text" name="sensorTopic">
            <p>MQTT Host:<p>
            <input type="text" name="mqttHost">
            <br>
            <button type="submit">post</button>
        </form>
    </body>
</html>
'''
HTML_TO_CONFIG = dict()
HTML_TO_CONFIG["ssid"] = "WIFI_SSID"
HTML_TO_CONFIG["wifiPassword"] = "WIFI_PASSWORD"
HTML_TO_CONFIG["mqttHost"] = "MQTT_HOST"
HTML_TO_CONFIG["sensorTopic"] = "SENSOR_TOPIC"
HTML_TO_CONFIG["sensorName"] = "SENSOR_NAME"

def configInit():
	CONFIG["CONFIG_PATH"] = CONFIG_PATH
	CONFIG["WIFI_SSID"] = WIFI_SSID
	CONFIG["WIFI_PASSWORD"] = WIFI_PASSWORD
	CONFIG["MQTT_HOST"] = MQTT_HOST
	CONFIG["SENSOR_NAME"] = SENSOR_NAME
	CONFIG["SENSOR_TOPIC"] = SENSOR_TOPIC
	return

def startAccessPoint():
	print("Starting up Access Point Mode")
	ap_if = network.WLAN(network.AP_IF)
	ap_if.active(True)
	return

def startWifi():
	print("Starting up Wifi connection")
	print("SSID: %s")%WIFI_SSID
	return

def startMqtt():
	print("Starting up MQTT Connection...")
	print("MQTT Server: %s")%MQTT_IP
	print("MQTT Port: %s")%MQTT_Port
	return

def writeConfig(configFile, htmlConfig):
	print("Writting new config to file...")
	os.remove(configFile)
	f = open(configFile, "w+")
	print("%s")%htmlConfig
	for key, value in htmlConfig.items():
		f.write(HTML_TO_CONFIG[key]+":"+value+"\n")
	f.close()
	return

def readConfig(configFile):
	if os.path.exists(configFile):
		f = open(configFile, 'r')
		for line in f:
			configList = line.strip().split(":")
			if len(configList) == 2:
				key = configList[0]
				value = configList[1]
				if key in CONFIG:
					CONFIG[key] = value
				else:
					print("Error in parsing network config, back to AP mode")
					print("%s")%line
					f.close()
					return
			else:
				print("Error in parsing network config, back to AP mode")
				print("%s")%line
				f.close()
				return
		f.close()
	return

def startHTTPServer(micropython_optimize=False):
    s = socket.socket()

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    #print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    #print("Listening, connect your browser to http://<this_host>:8080/")

    counter = 0
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        req=client_sock.recv(4096)
        processed_request=inRequest(req)
        #print(processed_request)
        # TODO write output of processPOST to file
	htmlDict = processPOST(processed_request)
	if htmlDict:
		writeConfig(CONFIG_PATH, htmlDict)
		return
	print("%s")%CONFIG

        if not micropython_optimize:
            # To read line-oriented protocol (like HTTP) from a socket (and
            # avoid short read problem), it must be wrapped in a stream (aka
            # file-like) object. That's how you do it in CPython:
            #print('not optimize')
            client_stream = client_sock.makefile("rwb")
        else:
            # .. but MicroPython socket objects support stream interface
            # directly, so calling .makefile() method is not required. If
            # you develop application which will run only on MicroPython,
            # especially on a resource-constrained embedded device, you
            # may take this shortcut to save resources.
            client_stream = client_sock

        client_stream.write(index)

        client_stream.close()
        if not micropython_optimize:
            client_sock.close()
        counter += 1
        #print()

def inRequest(text):
   content=''
   if text[0:3]=='GET':
      method='GET'
   else:
      method='POST'
      k=len(text)-1
      while k>0 and text[k]!='\n' and text[k]!='\r':
         k=k-1
      content=text[k+1:]
   text=text[text.index(' ')+1:]
   url=text[:text.index(' ')]
   return {"method":method,"url":url,"content":content}

def processPOST(response_dict):
    '''
    input is diction from inRequest
    outputs dictionary of content from POST request
    '''
    response_content = response_dict['content']
    response_param_list= response_content.split('&')
    param_dict = {}
    if response_dict['method'] != 'POST':
        return
    for ele in response_param_list:
        #TODO make the following code parse in a pythonic way
        # this is not pythonic
        key_value_pair = ele.split('=')
        param_dict[key_value_pair[0]] = key_value_pair[1]
    return param_dict

def apInit():
	startAccessPoint()
	startHTTPServer()

def main():
	configInit()
	if not os.path.exists(configFile):
		# start apInit
		# wait for new config file to be returned.
	# we have a config file	
	# start the main loop
	# start WIFI - try 3 times, if fails, next main loop should go to AP mode again.
	# if successfull, start the MQTT broker - if failure : TBD
	# if MQTT broker connection success: send data
	return
main()