__author__ = 'Michael'
import requests
from urls import Url


class Rackspace(object):
    username = None
    apikey = None
    tenantid = None

    def __init__(self, username, apikey, tenantid):
        self.username = username
        self.apikey = apikey
        self.tenantid = tenantid


def get_token():
    _body = '{"auth":{"RAX-KSKEY:apiKeyCredentials":{"username":"%s","apiKey":"%s"}}}' \
            % (Rackspace.username, Rackspace.apikey)
    request = requests.post("https://identity.api.rackspacecloud.com/v2/tokens", data=_body)
    data = request.json()
    token = data['access']['token']['id']
    return token


class Images(Rackspace):
    osname = None

    def __init__(self, osname, username, apikey, tenantid):
        super(Images, self).__init__(username, apikey, tenantid)
        self.osname = osname

    @staticmethod
    def get_imageid(osname):
        request = requests.get(Url.ROOT_URL_RS + "/%s/images" % Rackspace.tenantid,
                               headers={"Authorization": "Bearer %s" % get_token()})
        data = request.json()
        for i in (data['images']):
            if osname in i['name']:
                imageid = i['id']
                return imageid


class Sizes(Rackspace):
    sizename = None

    def __init__(self, sizename, username, apikey, tenantid):
        super(Sizes, self).__init__(username, apikey, tenantid)
        self.sizename = sizename

    @staticmethod
    def get_sizeid(sizename):
        request = requests.get(Url.ROOT_URL_RS + "/%s/flavors" % Rackspace.tenantid,
                               headers={"Authorization": "Bearer %s" % get_token()})
        data = request.json()
        for i in (data['flavors']):
            if sizename in i['name']:
                flavorid = i['id']
                return flavorid


class Servers(Rackspace):
    image = None
    flavor = None
    servername = None
    serverid = None
    action = None

    def __init__(self, image, flavor, servername, serverid, action, username, apikey, tenantid):
        super(Servers, self).__init__(username, apikey, tenantid)
        self.image = image
        self.flavor = flavor
        self.servername = servername
        self.serverid = serverid
        self.action = action

    @staticmethod
    def s_action(image=None, flavor=None, servername=None, serverid=None, **action):
        if action.get('Insert'):
            _body = '{"server": {"name": "%s","imageRef": "%s","flavorRef": "%s"}}' % (
                    servername, Images.get_imageid(image), Sizes.get_sizeid(flavor))
            requests.post(Url.ROOT_URL_RS + "/v2/%s/servers" % Rackspace.tenantid,
                          headers={"Authorization": "Bearer %s" % get_token()}, data=_body)

        elif action.get('Reboot'):
            _body = '{"reboot": {"type": "SOFT"}}'
            requests.post(Url.ROOT_URL_RS + "v2/%s/servers/%s/reboot" % (Rackspace.tenantid, serverid),
                          data=_body, headers={"Authorization": "Bearer %s" % get_token()})

        elif action.get('Rebuild'):
            _body = '{"server": {"flavorRef": %s,"imageRef": %s,"name": %s,"password_delivery": API}}' % (
                    Sizes.get_sizeid(flavor), Images.get_imageid(image), servername)
            requests.post(Url.ROOT_URL_RS + "v2/%s/servers/%s" % (Rackspace.tenantid, serverid),
                          data=_body, headers={"Authorization": "Bearer %s" % get_token()})

        elif action.get('Remove'):
            requests.delete(Url.ROOT_URL_RS + "v2/%s/servers/%s" % (Rackspace.tenantid, serverid),
                            headers={"Authorization": "Bearer %s" % get_token()})


class Network(Rackspace):
    cidr = None
    name = None

    def __init__(self, cidr, name, username, apikey, tenantid):
        super(Network, self).__init__(username, apikey, tenantid)
        self.cidr = cidr
        self.name = name

    @staticmethod
    def create(cidr, name):
        _body = '{"network":{"cidr": "%s","label": "%s"}}' % (cidr, name)
        requests.post(Url.ROOT_URL_RS + "v2/%s/os-networksv2" % Rackspace.tenantid,
                      data=_body, headers={"Authorization": "Bearer %s" % get_token()})

    @staticmethod
    def delete(name):
        global netid
        request = requests.get(Url.ROOT_URL_RS + "v2/%s/os-networksv2" % Rackspace.tenantid,
                               headers={"Authorization": "Bearer %s" % get_token()})
        data = request.json()
        for _data in data['networks']:
            if name in _data['label']:
                netid = _data['id']
        requests.delete(Url.ROOT_URL_RS + "v2/%s/os-networksv2/%s" % (Rackspace.tenantid, netid),
                        headers={"Authorization": "Bearer %s" % get_token()})

    @staticmethod
    def attach(servername, name):
        global serverid, netid
        request = requests.get(Url.ROOT_URL_RS + "v2/%s/os-networksv2" % Rackspace.tenantid,
                               headers={"Authorization": "Bearer %s" % get_token()})
        data = request.json()
        for _data in data['networks']:
            if name in _data['label']:
                netid = _data['id']

        request = requests.get(Url.ROOT_URL_RS + "v2/%s/servers" % Rackspace.tenantid,
                               headers={"Authorization": "Bearer %s" % get_token()})
        data = request.json()
        for _data in data['servers']:
            if servername in _data['name']:
                serverid = _data['id']

        _body = '{"virtual_interface": {"network_id": %s"}}' % netid
        requests.post(Url.ROOT_URL_RS + "v2/%s/servers/%s/os-virtual-interfacesv2" % (Rackspace.tenantid, serverid),
                      headers={"Authorization": "Bearer %s" % get_token()}, data=_body)
