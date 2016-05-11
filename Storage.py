__author__ = 'Michael'
import json
from abc import ABCMeta
from collections import OrderedDict
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


class StorageCreator(Creator):
    def __init__(self, name, protocol, space, iqn, auth_obj):
        self.name = name
        self.protocol = protocol
        self.space = space
        self.iqn = iqn
        self.auth = auth_obj
        self.wcf_baseurl = 'https://api.dc%s.computing.cloud.it/WsEndUser/v2.6/WsEndUser.svc/json' % (str(Aruba.region))
        self.json_msg = {
            'ApplicationId': 'SetEnqueuePurchaseSharedStorage',
            'RequestId': 'SetEnqueuePurchaseSharedStorage',
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
