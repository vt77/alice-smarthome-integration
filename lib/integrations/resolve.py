from devices.actions import get_action_by_name


class ActionRequest:
    def __init__(self,action_name:str, params=None):
        self.action_name = action_name
        self.param = params['instance']
        self.value = params['value']

    def __iter__(self):
        yield 'action', self.action_name
        yield 'param',self.param
        yield 'value',self.value


class QueryRequest:
    def __init__(self,params):
        self.action_name = 'query'
        self.param = params['instance']

    def __iter__(self):
        yield 'action', self.action_name
        yield 'param',self.param
