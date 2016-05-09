__author__ = 'Michael'
import json
from abc import ABCMeta
from collections import OrderedDict
from ArubaCloud.base import JsonInterfaceBase
from ArubaCloud.base import Auth
from aruba import Aruba, connect


class Creator(object):
    __metaclass__ = ABCMeta
    json_msg = OrderedDict()

    def get_raw(self):
        return self.json_msg

    def get_json(self):
        return json.dumps(self.json_msg)

    def commit(self, url, debug=False):
        from ArubaCloud.helper import Http
        url = '{}/{}'.format(url, 'SetEnqueueLoadBalancerCreation')
        headers = {'Content-Type': 'application/json', 'Content-Length': len(self.get_json())}
        response = Http.post(url=url, data=self.get_json(), headers=headers)
        parsed_response = json.loads(response.content)
        if debug is True:
            print(parsed_response)
        if parsed_response["Success"]:
            return True
        return False


class LoadBalancer(JsonInterfaceBase):
    def __init__(self):
        super(LoadBalancer, self).__init__()
        self.wcf_baseurl = 'https://api.dc%s.computing.cloud.it/WsEndUser/v2.6/WsEndUser.svc/json' % (str(Aruba.region))

    @property
    def _name(self):
        return self._name

    def get(self):
        scheme = self.gen_def_json_scheme('GetLoadBalancers')
        json_obj = self.call_method_post('GetLoadbalancers', json_scheme=scheme)
        self.raw = json_obj['Value'][0]

    def login(self, username, password):
        self.auth = Auth(username, password)

    def enable(self):
        scheme = self.gen_def_json_scheme('SetEnqueueLoadBalancerStart')
        json_obj = self.call_method_post('SetEnqueueLoadBalancerStart', json_scheme=scheme)
        self.raw = json_obj

    def disable(self):
        scheme = self.gen_def_json_scheme('SetEnqueueLoadBalancerPowerOff')
        json_obj = self.call_method_post('SetEnqueueLoadBalancerPowerOff', json_scheme=scheme)
        self.raw = json_obj

    def delete(self):
        scheme = self.gen_def_json_scheme('SetEnqueueLoadBalancerDeletion')
        json_obj = self.call_method_post('SetEnqueueLoadBalancerDeletion', json_scheme=scheme)
        self.raw = json_obj

    def getstats(self):
        scheme = self.gen_def_json_scheme('GetLoadBalancerRuleStatistics')
        json_obj = self.call_method_post('GetLoadBalancerRuleStatistics', json_scheme=scheme)
        self.raw = json_obj

    def getloads(self):
        scheme = self.gen_def_json_scheme('GetLoadBalancerLoads')
        json_obj = self.call_method_post('GetLoadBalancerLoads', json_scheme=scheme)
        self.raw = json_obj

    def getnotifs(self):
        scheme = self.gen_def_json_scheme('GetLoadBalancerNotifications')
        json_obj = self.call_method_post('GetLoadBalancerNotifications', json_scheme=scheme)
        self.raw = json_obj


class LoadBalancerCreator(Creator):
    def __init__(self, name, serverid, algorithm, protocol, lbport, serverport, contact, auth_obj):
        self.name = name
        self.serverid = serverid
        self.algorithm = algorithm
        self.protocol = protocol
        self.lbport = lbport
        self.serverport = serverport
        self.contact = contact
        self.auth = auth_obj
        self.wcf_baseurl = 'https://api.dc%s.computing.cloud.it/WsEndUser/v2.6/WsEndUser.svc/json' % (str(Aruba.region))
        self.json_msg = {
            'ApplicationId': 'SetEnqueueLoadBalancerCreation',
            'RequestId': 'SetEnqueueLoadBalancerCreation',
            'SessionId': '',
            'Password': auth_obj.password,
            'Username': self.auth.username,
            'LoadBalancer': {
                'Name': self.name,
                'LoadBalancerInstance': [{'IPAddress': connect().purchase_ip()}],
                'NotificationContacts': [{'NotificationContact': [{'ContactValue': self.contact}]}],
                'Rules': [{'LoadBalancerRule': [{'BalanceType': self.algorithm,
                                                 'Protocol': self.protocol,
                                                 'LoadBalancerPort': self.lbport,
                                                 'InstancePort': serverport}]}]
            }
        }