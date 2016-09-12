
class Page(object):

    def __init__(self, _id, url, wsapp, fetch_content=False):
        # '''
        # TODO:
        # Initialize the object. 
        # url - the websocket url
        # target_url - the url to navigate to
        # '''
        self.id = _id
        self.url = url
        # self.chrome = chrome
        self.fetch_content = fetch_content
        self.failed = False
        self.original_request_id = None
        self.original_request_ms = None
        self.dom_content_event_fired_ms = None
        self.load_event_fired_ms = None
        self.objects = {}

    @property
    def finished(self):
        # TODO
        # // a page is considered "finished" either when is failed or when all these
        # // three messages arrived: a reply to the original request
        return self.failed or (self.original_request_ms is not None \
            and self.dom_content_event_fired_ms is not None \
            and self.load_event_fired_ms is not None)

    # @property
    # def failed(self):
    #     return self.failed

    def process_message(self, message):
        # print "## on process_message", message, type(message)
        method = message['method']
        domain = method.split('.')[0]
        if method == 'Page.domContentEventFired':
            self.dom_content_event_fired_ms = message['params']['timestamp'] * 1000
        elif method == 'Page.loadEventFired':
            self.load_event_fired_ms = message['params']['timestamp'] * 1000
        elif domain == 'Network':
            request_id = message['params']['requestId']
            if method == 'Network.requestWillBeSent':
                # // the first is the original request
                if self.original_request_id is None and  message['params']['initiator']['type'] == 'other':
                    self.original_request_ms = message['params']['timestamp'] * 1000
                    self.original_request_id = request_id

                self.objects[request_id] = {
                    'requestMessage': message['params'],
                    'responseMessage': None,
                    'responseLength': 0,
                    'encodedResponseLength': 0,
                    'responseFinished': None,
                    'responseBody': None,
                    'responseBodyIsBase64': None
                }
            elif method == 'Network.dataReceived':
                if request_id in self.objects:
                    self.objects[request_id]['responseLength'] += message['responseLength']['params']['dataLength']
                    self.objects[request_id]['encodedResponseLength'] += message['params']['encodedDataLength']
            elif method == 'Network.responseReceived':
                if request_id in self.objects:
                    self.objects[request_id]['responseMessage'] = message['params']
            elif method == 'Network.loadingFinished':
                if request_id in self.objects:
                    self.objects[request_id]['responseFinished'] = message['params']['timestamp']
                    # // asynchronously fetch the request body (no check is
                    # // performed to really ensure that the fetching is over
                    # // before finishing this page processing because there is
                    # // the PAGE_DELAY timeout anyway; it should not be a problem...)
                    # if (self.fetchContent) {
                    #     self.chrome.Network.getResponseBody({'requestId': id}, function (error, response) {
                    #         if (!error) {
                    #             self.objects[id].responseBody = response.body;
                    #             self.objects[id].responseBodyIsBase64 = response.base64Encoded;
                    #         }
                    #     });
                    # }
            elif method == 'Network.loadingFailed':
                # // failure of the original request aborts the whole page
                if request_id == self.original_request_id:
                    self.failed = True

            # // verbose dump
            if request_id is None:
                print('<-- ' + method + ': ' + self.url)
            else:
                print('<-- ' + '[' + request_id + '] ' + method)




# https://chromium.googlesource.com/chromium/blink.git/+/master/Source/devtools/front_end/sdk/HAREntry.js
