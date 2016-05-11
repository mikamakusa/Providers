__author__ = 'Michael'
import json
from abc import ABCMeta
from collections import OrderedDict
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
                'IPAddress': connect().purchase_ip(),
                'ContactValue': self.contact,
                'BalanceType': self.algorithm,
                'Protocol': self.protocol,
                'LoadBalancerPort': self.lbport,
                'InstancePort': self.serverport
            }
        }