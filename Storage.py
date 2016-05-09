__author__ = 'Michael'
import json
from abc import ABCMeta
from collections import OrderedDict
from ArubaCloud.base import JsonInterfaceBase
from ArubaCloud.base import Auth
from aruba import Aruba


class Creator(object):
    __metaclass__ = ABCMeta
    json_msg = OrderedDict()

    def get_raw(self):
        return self.json_msg

    def get_json(self):
        return json.dumps(self.json_msg)

    def commit(self, url, debug=False):
        from ArubaCloud.helper import Http
        url = '{}/{}'.format(url, 'SetEnqueuePurchaseSharedStorage')
        headers = {'Content-Type': 'application/json', 'Content-Length': len(self.get_json())}
        response = Http.post(url=url, data=self.get_json(), headers=headers)
        parsed_response = json.loads(response.content)
        if debug is True:
            print(parsed_response)
        if parsed_response["Success"]:
            return True
        return False


class Storage(JsonInterfaceBase):
    def __init__(self):
        super(Storage, self).__init__()
        self.wcf_baseurl = 'https://api.dc%s.computing.cloud.it/WsEndUser/v2.6/WsEndUser.svc/json' % (str(Aruba.region))

    def get(self):
        scheme = self.gen_def_json_scheme('GetSharedStorages')
        json_obj = self.call_method_post('GetSharedStorages', json_scheme=scheme)
        self.raw = json_obj

    def login(self, username, password):
        self.auth = Auth(username, password)

    def remove(self):
        scheme = self.gen_def_json_scheme('SetEnqueueRemoveSharedStorage')
        json_obj = self.call_method_post('SetEnqueueRemoveSharedStorage', json_scheme=scheme)
        self.raw = json_obj


class StorageCreator(Creator):
    def __init__(self, name, protocol, space, iqn, auth_obj):
        self.name = name
        self.protocol = protocol
        self.space = space
        self.iqn = iqn
        self.auth = auth_obj
        self.wcf_baseurl = 'https://api.dc%s.computing.cloud.it/WsEndUser/v2.6/WsEndUser.svc/json' % (str(Aruba.region))
        self.json_msg = {
            'ApplicationId': 'SetEnqueueLoadBalancerCreation',
            'RequestId': 'SetEnqueueLoadBalancerCreation',
            'SessionId': '',
            'Password': auth_obj.password,
            'Username': self.auth.username,
            'SharedStorage': {
                'Quantity': space,
                'SharedStorageIQN': [{'Value': iqn}],
                'SharedStorageName': name,
                'SharedStorageProtocolType': protocol
            }
            }
