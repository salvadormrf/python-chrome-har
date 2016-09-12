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


class ChromeRDPWebsocket(object):

    # def __init__(self, url, target_url, device_configuration, should_reload, user_agent_str, screen_size_config, callback):
    def __init__(self, url, target_url, device_configuration, should_reload, callback):
        '''
        Initialize the object. 
        url - the websocket url
        target_url - the url to navigate to
        '''
        # websocket.enableTrace(True)       

        # Conditions for a page to finish loading.
        self.originalRequestMs = None
        self.domContentEventFiredMs = None
        self.loadEventFiredMs = None
        self.tracingCollectionCompleted = False

        self.network_messages = []      # A list containing all the messages.
        self.timeline_messages = []     # A list containing all the timeline messages.
        self.response_body = dict()
        self.request_id_to_url = dict()
        self.outstanding_response_body_request = dict()
        self.url = target_url       # The URL to navigate to.
        self.callback = callback    # The callback method
        self.device_configuration = device_configuration # The device configuration
        self.should_reload = should_reload
        self.debugging_url = url
        # self.user_agent = user_agent_str
        # self.screen_size_config = screen_size_config
        self.ws = websocket.WebSocketApp(url,\
                                        on_message = self.on_message,\
                                        on_error = self.on_error,\
                                        on_close = self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever() # start running this socket.

    def on_message(self, ws, message):
        '''
        Handle each message.
        '''
        message_obj = json.loads(message)
        # print "## Got message", message_obj

        # self.tracingCollectionCompleted = True
        if METHOD in message_obj and message_obj[METHOD].startswith('Network'):
            if message_obj[METHOD] == 'Network.requestWillBeSent' and \
                message_obj[PARAMS]['initiator']['type'] == 'other':
                self.originalRequestMs = message_obj[PARAMS][TIMESTAMP] * 1000
                if escape_page(message_obj[PARAMS]['request']['url']) == escape_page(self.url):
                    self.page_index_request_id = message_obj[PARAMS]['requestId']
            elif message_obj[METHOD] == 'Network.responseReceived':
                request_id = message_obj[PARAMS]['requestId']
                self.request_id_to_url[request_id] = message_obj[PARAMS]['response']['url']
            elif message_obj[METHOD] == 'Network.loadingFinished':
                request_id = message_obj[PARAMS]['requestId']
                body_request_id = navigation_utils.get_request_body(self.ws, request_id)
                self.outstanding_response_body_request[body_request_id] = request_id
            self.network_messages.append(message)
        elif METHOD in message_obj and message_obj[METHOD].startswith('Page'):
            if message_obj[METHOD] == 'Page.domContentEventFired':
                self.domContentEventFiredMs = message_obj[PARAMS][TIMESTAMP] * 1000
            elif message_obj[METHOD] == 'Page.loadEventFired':
                self.loadEventFiredMs = message_obj[PARAMS][TIMESTAMP] * 1000
            # elif message_obj[METHOD] == 'Page.javascriptDialogOpening':
            #     if message_obj[PARAMS]['type'] == 'alert' or \
            #         message_obj[PARAMS]['type'] == 'beforeunload':
            #         navigation_utils.handle_js_dialog(self.ws)
            #     elif message_obj[PARAMS]['type'] == 'confirm' or \
            #         message_obj[PARAMS]['type'] == 'prompt':
                    # navigation_utils.handle_js_dialog(self.ws, accept=False)
        elif METHOD in message_obj and message_obj[METHOD] == 'Tracing.dataCollected':
            # Data collected.
            self.timeline_messages.extend(message_obj[PARAMS]['value'])
        elif METHOD in message_obj and message_obj[METHOD] == 'Tracing.tracingComplete':
            # Tracing completed
            self.tracingCollectionCompleted = True
        elif METHOD in message_obj and message_obj[METHOD].startswith('Emulate'):
            # print message
            pass
        elif METHOD not in message_obj:
            if 'result' in message_obj and 'id' in message_obj and \
                message_obj['id'] in self.outstanding_response_body_request:
                request_id = self.outstanding_response_body_request[message_obj['id']]
                if 'base64Encoded' in message_obj['result'] and not message_obj['result']['base64Encoded']:
                    is_page_index_request = request_id == self.page_index_request_id
                    self.response_body[request_id] = (request_id, self.request_id_to_url[request_id], message_obj['result']['body'].encode('ascii', 'ignore'), is_page_index_request)
                del self.outstanding_response_body_request[message_obj['id']]
            elif 'error' in message_obj and 'id' in message_obj and \
                message_obj['id'] in self.outstanding_response_body_request:
                del self.outstanding_response_body_request[message_obj['id']]
        if self.originalRequestMs is not None and \
            self.domContentEventFiredMs is not None and \
            self.loadEventFiredMs is not None and \
            not self.tracingCollectionCompleted:
            self.stop_trace_collection(self.ws)
       
        if self.tracingCollectionCompleted:
            # A page is considerd loaded if all of these three conditions are met.
            print 'Start time {0}, Load completed: {1}'.format(self.originalRequestMs, self.loadEventFiredMs)
            # self.callback(self, self.network_messages, self.timeline_messages, self.device_configuration)

        if self.originalRequestMs is not None and \
            self.domContentEventFiredMs is not None and \
            self.loadEventFiredMs is not None and \
            len(self.outstanding_response_body_request) == 0:
            self.disable_network_tracking(self.ws)
            self.disable_page_tracking(self.ws)
            print 'Start time {0}, Load completed: {1}'.format(self.originalRequestMs, self.loadEventFiredMs)
            self.callback(self, self.network_messages, self.timeline_messages, self.originalRequestMs, self.loadEventFiredMs, self.response_body, self.device_configuration)

    def on_error(self, ws, error):
        '''
        Handle the error.
        '''
        print error
    
    def on_close(self, ws):
        '''
        Handle when socket is closed
        '''
        print 'Socket for {0} is closed.'.format(self.url)

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
        navigate_to_page(self.ws, self.url)

    def close_connection(self):
        self.ws.close()
        print 'Connection closed'

    def get_navigation_url(self):
        return self.url

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





def callback_on_page_done(debugging_socket, network_messages, timeline_messages, original_request_ts, 
    load_event_ts, request_ids, device_configuration):
    '''
    Sets up the call back once the page is done loading.
    '''
    print 'Page load done. len(request_ids): ' + str(len(request_ids))
    # First, close the connection.
    debugging_socket.close_connection()

    import pdb; pdb.set_trace()


    # url = debugging_socket.get_navigation_url()
    # debugging_url = debugging_socket.get_debugging_url()
    # final_url = common_module.escape_page(url)
    # base_dir = create_output_directory_for_url(url)
    
    # debugging_websocket = websocket.create_connection(debugging_url)

    # if args.record_content:
    #     output_dir = os.path.join(base_dir, 'response_body')
    #     if not os.path.exists(output_dir):
    #         os.mkdir(output_dir)
    #     output_response_body(debugging_websocket, request_ids, output_dir)
    #     modified_html = navigation_utils.get_modified_html(debugging_websocket)
    #     modified_html_filename = os.path.join(output_dir, 'modified_html.html')
    #     with open(modified_html_filename, 'wb') as output_file:
    #         output_file.write(beautify_html(modified_html))

    # # Get the start and end time of the execution
    # start_time, end_time = navigation_utils.get_start_end_time_with_socket(debugging_websocket)
    # # print 'output dir: ' + base_dir
    # write_page_start_end_time(final_url, base_dir, start_time, end_time, original_request_ts, load_event_ts)
    
    # network_filename = os.path.join(base_dir, 'network_' + final_url)
    # timeline_filename = os.path.join(base_dir, 'timeline_' + final_url)
    # with open(network_filename, 'wb') as output_file:
    #     for message in network_messages:
    #         output_file.write('{0}\n'.format(json.dumps(message)))
    # # Output timeline objects
    # if len(timeline_messages) > 0:
    #     with open(timeline_filename, 'wb') as output_file:
    #         for message in timeline_messages:
    #             output_file.write('{0}\n'.format(json.dumps(message)))
    # # get_resource_tree(debugging_url)

    # chrome_utils.close_tab(debugging_socket.device_configuration, debugging_socket.device_configuration['page_id'])



















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

    debugging_socket = ChromeRDPWebsocket(
        wsdurl,
        'https://www.doubleclickbygoogle.com/articles/mobile-speed-matters/',
        {},
        False,
        callback_on_page_done,
    )