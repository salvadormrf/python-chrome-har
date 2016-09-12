# var events = require('events');
# var util = require('util');
# var Chrome = require('chrome-remote-interface');
# var common = require('./common.js');
# var Page = require('./page.js');
# var har = require('./har.js');

NEUTRAL_URL = 'about:blank'

# var CLEANUP_SCRIPT =
#     'chrome.benchmarking.clearCache();' +
#     'chrome.benchmarking.clearHostResolverCache();' +
#     'chrome.benchmarking.clearPredictorCache();' +
#     'chrome.benchmarking.closeConnections();';

# var PAGE_DELAY = 1000;

import simplejson as json
import websocket
import threading

from time import sleep







import simplejson as json
import websocket
import threading

from time import sleep

# from utils import navigation_utils

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
TIMESTAMP = 'timestamp'

WAIT = 1.0

HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'


def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')


def navigate_to_page(debug_connection, url):
    '''
    Navigates to the url.
    '''
    navigate_to_page = json.dumps({ "id": 0, "method": "Page.navigate", "params": { "url": url }})
    debug_connection.send(navigate_to_page)
    sleep(1.0)


























from har import HAR
from page import Page






class ChromeRDPWebsocket(object):
    fetch_content = False
    # options.onLoadDelay = options.onLoadDelay || 0;

    def __init__(self, url, target_url):
        self.debugging_url = url
        self.url = target_url
        self.page = None

        # websocket.enableTrace(True)

        self.ws = websocket.WebSocketApp(url,\
                                        on_message = self.on_message,\
                                        on_error = self.on_error,\
                                        on_close = self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever() # start running this socket.

    def load_url(self, url):
        # pass
        # var page = new Page(index, url, chrome, options.fetchContent);
        index = 0
        chrome = None
        self.page = Page(index, url, chrome, False);


        # print "############### HERE load_url", url, self.page


        # navigate_to_page = json.dumps({ "id": 0, "method": "Page.navigate", "params": { "url": url }})
        # self.ws.send(navigate_to_page)
        # sleep(1.0)

        # print "## HERE", url
        navigate_to_page(self.ws, url)

    def on_message(self, ws, message):
        '''
        Handle each message.
        '''
        message_obj = json.loads(message)
        # print "## Got message", message_obj

        # print "@@@@ self.page", self.page

        

        # method = message_obj['method']
        # if method == 'Page.frameStoppedLoading':
        #     print "### END ###"

        if self.page:
            self.page.process_message(message_obj)
            if self.page.finished:
                print "### END ###"
                self.close_connection()




    def on_error(self, ws, error):
        '''
        Handle the error.
        '''
        print error
    
    def on_close(self, ws):
        '''
        Handle when socket is closed
        '''
        print 'Socket for {0} is closed.'.format(self.debugging_url)

    def on_open(self, ws):
        '''
        Initialization logic goes here.
        '''
        self.enable_network_tracking(self.ws)
        self.enable_page_tracking(self.ws)

        # if self.user_agent is not None:
        #     navigation_utils.set_user_agent(self.ws, self.user_agent)

        # if self.screen_size_config is not None:
        #     navigation_utils.set_device_screen_size(self.ws, self.screen_size_config, self.device_configuration['page_id'])

        self.clear_cache(self.ws)
        
        # self.enable_trace_collection(self.ws)
        # print 'navigating to url: ' + str(self.url)
        # if self.should_reload:
        #     navigation_utils.reload_page(self.ws)
        # else:
        #     navigation_utils.navigate_to_page(self.ws, self.url)
        
        # url = 'https://www.google.com'
        # print 'navigating to url: ' + str(url)
        # navigate_to_page(self.ws, url)
        self.load_url(self.url)

    def close_connection(self):
        self.ws.close()
        print 'Connection closed'

    # def get_navigation_url(self):
    #     return self.url

    def clear_cache(self, debug_connection):
        clear_cache = { "id": 4, "method": "Network.clearBrowserCache" }
        debug_connection.send(json.dumps(clear_cache))
        print 'Cleared browser cache'
        sleep(WAIT)

    def can_clear_cache(self, debug_connection):
        '''
        Clears the cache in the browser
        '''
        clear_cache = { "id": 4, "method": "Network.canClearBrowserCache" }
        debug_connection.send(json.dumps(clear_cache))
        print 'Cleared browser cache'
        sleep(WAIT)

    def disable_network_tracking(self, debug_connection):
        '''
        Disable Network tracking in Chrome.
        '''
        disable_network = { "id": 1, "method": "Network.disable" }
        debug_connection.send(json.dumps(disable_network))
        print 'Disable network tracking.'
        sleep(WAIT)

    def disable_page_tracking(self, debug_connection):
        '''
        Disable Page tracking in Chrome.
        '''
        disable_page = { 'id': 3, 'method': 'Page.disable' }
        debug_connection.send(json.dumps(disable_page))
        print 'Disable page tracking.'
        sleep(WAIT)

    def enable_network_tracking(self, debug_connection):
        '''
        Enables Network tracking in Chrome.
        '''
        enable_network = { "id": 1, "method": "Network.enable" }
        debug_connection.send(json.dumps(enable_network))
        print 'Enabled network tracking.'
        sleep(WAIT)
        disable_cache = { "id": 10, "method": "Network.setCacheDisabled", "params": { "cacheDisabled": True } }
        debug_connection.send(json.dumps(disable_cache))
        print 'Disable debugging connection.'
        sleep(WAIT)

    def enable_page_tracking(self, debug_connection):
        '''
        Enables Page tracking in Chrome.
        '''
        enable_page = { 'id': 3, 'method': 'Page.enable' }
        debug_connection.send(json.dumps(enable_page))
        print 'Enabled page tracking.'
        sleep(WAIT)

    
    def enable_runtime(self, debug_connection):
        '''
        Enables Runtime in Chrome.
        '''
        enable_page = { 'id': 3, 'method': 'Runtime.enable' }
        debug_connection.send(json.dumps(enable_page))
        print 'Enabled Runtime.'
        sleep(WAIT)

    def enable_trace_collection(self, debug_connection):
        '''
        Enables the tracing collection.
        '''
        enable_trace_collection = { 'id': 4, 'method': 'Tracing.start' }
        debug_connection.send(json.dumps(enable_trace_collection))
        print 'Enabled trace collection'
        sleep(WAIT)

    def stop_trace_collection(self, debug_connection):
        '''
        Enables the tracing collection.
        '''
        enable_trace_collection = { 'id': 4, 'method': 'Tracing.end' }
        debug_connection.send(json.dumps(enable_trace_collection))
        # print 'Disables trace collection'
        sleep(WAIT)

    def get_debugging_url(self):
        '''
        Returns the debugging url.
        '''
        return self.debugging_url





import requests


if __name__ == '__main__':
    host = 'localhost'
    port = '9222'

    # find websocket endpoint
    response = requests.get("http://%s:%s/json" % (host, port))
    tablist = json.loads(response.text)
    # return self.tablist
    # import pdb; pdb.set_trace()
    
    wsdurl = tablist[0]['webSocketDebuggerUrl']

    client = ChromeRDPWebsocket(
        wsdurl,
        'https://github.com/'
    )

    print wsdurl
    print client.page

    # import pdb; pdb.set_trace()

    har = HAR()
    
    har.from_page(client.page)

    # json_ = JSON.stringify(har, null, 4);
    
    f = open('/tmp/test.har', 'w')
    f.write(json.dumps(har.har)) # indent=4
    f.close()
