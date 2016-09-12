import six
import chrome_remote_shell, json

shell = chrome_remote_shell.Shell(host='localhost', port=9222)
shell.connect(0)



# import pdb; pdb.set_trace()

url = 'https://www.doubleclickbygoogle.com/articles/bt-sport-dynamic-ad-insertion-google/'

# navcom = json.dumps({"id":0, "method":"Page.navigate", "params":{"url":url}})

# shell.soc.send(navcom)

# response = json.loads(shell.soc.recv())
# print response


# chrome.send('Network.enable');
# chrome.send('Page.navigate', {'url': 'chrome://newtab/'});

# chrome.Page.enable();
# chrome.Network.enable();
# chrome.Network.setCacheDisabled({'cacheDisabled': true});

# chrome.Network.setUserAgentOverride({'userAgent': options.userAgent});

# 
# response = json.loads(shell.soc.recv())
# print response




#################################

navcom = json.dumps({"id": 0, "method": "Page.enable"})
shell.soc.send(navcom)

navcom = json.dumps({"id": 0, "method": "Network.enable"})
shell.soc.send(navcom)

navcom = json.dumps({"id":0, "method": "Network.setCacheDisabled", "params": {"cacheDisabled": True}})
shell.soc.send(navcom)

navcom = json.dumps({"id":0, "method": "Page.navigate", "params": {"url": url}})
shell.soc.send(navcom)

navcom = json.dumps({"id": 0, "method": "Page.getResourceTree"})
shell.soc.send(navcom)

navcom = json.dumps({"id": 0, "method": "Page.captureScreenshot"})
shell.soc.send(navcom)


# navcom = json.dumps({"id": 0, "method": "Network.getResponseBody"}) TODO: needs request ID





class Page(object):
    pass

class Network(object):
    pass





response = json.loads(shell.soc.recv())
print response

#################################


# import argparse
# import code
# import sys
# import threading
# import time

# import six
# from six.moves.urllib.parse import urlparse

# import websocket

# try:
#     import readline
# except ImportError:
#     pass


# def get_encoding():
#     encoding = getattr(sys.stdin, "encoding", "")
#     if not encoding:
#         return "utf-8"
#     else:
#         return encoding.lower()


# OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)
# ENCODING = get_encoding()



# ws = shell.soc

# def recv():
#     try:
#         frame = ws.recv_frame()
#     except websocket.WebSocketException:
#         return websocket.ABNF.OPCODE_CLOSE, None
#     if not frame:
#         raise websocket.WebSocketException("Not a valid frame %s" % frame)
#     elif frame.opcode in OPCODE_DATA:
#         return frame.opcode, frame.data
#     elif frame.opcode == websocket.ABNF.OPCODE_CLOSE:
#         ws.send_close()
#         return frame.opcode, None
#     elif frame.opcode == websocket.ABNF.OPCODE_PING:
#         ws.pong(frame.data)
#         return frame.opcode, frame.data

#     return frame.opcode, frame.data



# def recv_ws():
#     while True:
#         opcode, data = recv()
#         msg = None
#         if six.PY3 and opcode == websocket.ABNF.OPCODE_TEXT and isinstance(data, bytes):
#             data = str(data, "utf-8")
#         if not args.verbose and opcode in OPCODE_DATA:
#             msg = data
#         elif args.verbose:
#             msg = "%s: %s" % (websocket.ABNF.OPCODE_MAP.get(opcode), data)

#         if msg is not None:
#             if args.timings:
#                 console.write(str(time.time() - start_time) + ": " + msg)
#             else:
#                 console.write(msg)

#         if opcode == websocket.ABNF.OPCODE_CLOSE:
#             break











# def main():
#     thread = threading.Thread(target=recv_ws)
#     thread.daemon = True
#     thread.start()


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(e)

#     navcom = json.dumps({"id": 0, "method": "Page.enable"})
#     shell.soc.send(navcom)

#     navcom = json.dumps({"id": 0, "method": "Network.enable"})
#     shell.soc.send(navcom)

#     navcom = json.dumps({"id":0, "method": "Network.setCacheDisabled", "params": {"cacheDisabled": True}})
#     shell.soc.send(navcom)

#     navcom = json.dumps({"id":0, "method": "Page.navigate", "params": {"url": url}})
#     shell.soc.send(navcom)


#     navcom = json.dumps({"id": 0, "method": "Page.getResourceTree"})
#     shell.soc.send(navcom)