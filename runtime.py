import json


class Runtime(object):
    command_id = 0

    def __init__(self, ws):
        self.ws = ws
        self.enable_runtime()

    @property
    def next_command_id(self):
        self.command_id += 1
        return self.command_id

    def enable_runtime(self):
        self.call_command(method='Runtime.enable')
        print 'Enabled Runtime.'

    # def evaluate(self, expression):
    #     params = {"expression": expression}
    #     res = self.call_command(method='Runtime.evaluate', params=params)

    # Not async
    def call_command(self, method, params={}, callback=None):
        msg = {'id': self.next_command_id, 'method': method, 'params': params}
        self.ws.send(json.dumps(msg))
        return json.loads(self.ws.recv())
