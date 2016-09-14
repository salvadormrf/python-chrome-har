import json


class DOM(object):
    command_id = 0

    def __init__(self, ws):
        self.ws = ws
        self.enable_dom()

    @property
    def next_command_id(self):
        self.command_id +=1
        return self.command_id

    def enable_dom(self):
        self.call_command(method='DOM.enable')
        print 'Enabled DOM'

    def query_selector(self, selector):
        doc = self.call_command(method='DOM.getDocument')

        # # for c in doc['result']['root']['children']
        # def get_node_id(root_node):
        #     for c in root_node.get('children', []):
        #         if c['nodeName'] == '#document':
        #             return c['nodeId']
        #         node_id = get_node_id(c)
        #         if node_id:
        #             return node_id

        # node_id = get_node_id(doc['result']['root']['nodeId'])
        # node_id = doc['result']['root']['nodeId']
        # print "#### node_id=", node_id, type(node_id)

        params = {'nodeId': doc['result']['root']['nodeId'], 'selector': selector}
        res = self.call_command(method='DOM.querySelectorAll', params=params)
        return res

    def get_dom(self):
        doc = self.call_command(method='DOM.getDocument')
        params = {'nodeId': doc['result']['root']['nodeId']}
        return self.call_command(method='DOM.getOuterHTML', params=params)

    # Not async
    def call_command(self, method, params={}, callback=None):
        msg = {'id': self.next_command_id, 'method': method, 'params': params}
        self.ws.send(json.dumps(msg))
        return json.loads(self.ws.recv())
