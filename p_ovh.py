__author__ = 'Michael'
import ovh
import requests
import hashlib
from urls import Url
from providers import generate_rsa


class Povh(object):
    applicationkey = None
    secretkey = None
    endpoint = None

    def __init__(self, applicationkey, secretkey, endpoint):
        self.applicationkey = applicationkey
        self.secretkey = secretkey
        self.endpoint = endpoint


def ovh_token(applicationkey, secretkey, endpoint):
    client = ovh.Client(application_key=applicationkey, application_secret=secretkey,
                        endpoint=endpoint)
    ck = client.new_consumer_key_request()
    consumerkey = (ck.request())['consumerKey']
    return consumerkey


def get_time():
    request = requests.get(Url.ROOT_URL_OVH + "auth/time")
    data = request.json()
    for _time in data.json():
        return _time


def service():
    s1 = hashlib.sha1()
    s1.update(
        "+".join(
            [Povh.applicationkey, ovh_token(Povh.applicationkey, Povh.secretkey, Povh.endpoint),
             "GET", Url.ROOT_URL_OVH + "cloud/project/",
             get_time]))
    sig = "$1$" + s1.hexdigest()
    queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time,
                    "X-Ovh-Consumer": ovh_token(Povh.applicationkey, Povh.secretkey, Povh.endpoint),
                    "X-Ovh-Signature": sig, "Content-type": "application/json"}
    _service = requests.post(Url.ROOT_URL_OVH + "cloud/project/", headers=queryheaders)
    return _service


class Images(Povh):
    osname = None

    def __init__(self, osname, applicationkey, secretkey, endpoint):
        super(Images, self).__init__(applicationkey, secretkey, endpoint)
        self.osname = osname

    @staticmethod
    def getimageid(osname):
        s1 = hashlib.sha1()
        s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                           Povh.secretkey,
                                                           Povh.endpoint),
                            "GET", Url.ROOT_URL_OVH + "cloud/project/%s/image" % service,
                            get_time]))
        sig = "$1$" + s1.hexdigest()
        queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time,
                        "X-Ovh-Consumer": ovh_token(Povh.applicationkey, Povh.secretkey, Povh.endpoint),
                        "X-Ovh-Signature": sig,
                        "Content-type": "application/json"}
        im = requests.get(Url.ROOT_URL_OVH + "cloud/project/%s/image"
                          % service, headers=queryheaders)
        for i in im:
            if osname in i['name']:
                imageid = i['id']
                return imageid


class Region(Povh):
    regname = None

    def __init__(self, regname, applicationkey, secretkey, endpoint):
        super(Region, self).__init__(applicationkey, secretkey, endpoint)
        self.regname = regname

    @staticmethod
    def getregionid(regname):
        city = "Beauharnois", "Gravelines", "Strasbourg"
        if list(regname)[0] not in list(city)[0]:
            raise Exception("Region Error")
        else:
            s1 = hashlib.sha1()
            s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                               Povh.secretkey,
                                                               Povh.endpoint), "GET",
                                Url.ROOT_URL_OVH + "/%s/region" % service,
                                get_time]))
            sig = "$1$" + s1.hexdigest()
            queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time,
                            "X-Ovh-Consumer": ovh_token(Povh.applicationkey, Povh.secretkey, Povh.endpoint),
                            "X-Ovh-Signature": sig,
                            "Content-type": "application/json"}
            region = requests.get(Url.ROOT_URL_OVH + "cloud/project/%s/region" % service,
                                  headers=queryheaders)
            for i in region:
                if list(regname)[0] in list(i)[0]:
                    regionid = i
                    return regionid


class Sizes(Povh):
    sizename = None

    def __init__(self, sizename, applicationkey, secretkey, endpoint):
        super(Sizes, self).__init__(applicationkey, secretkey, endpoint)
        self.sizename = sizename

    @staticmethod
    def getsizeid(sizename):
        s1 = hashlib.sha1()
        s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                           Povh.secretkey,
                                                           Povh.endpoint),
                            "GET", Url.ROOT_URL_OVH + "cloud/project/%s/flavor"
                            % service, get_time]))
        sig = "$1$" + s1.hexdigest()
        queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time,
                        "X-Ovh-Consumer": ovh_token(Povh.applicationkey,
                                                    Povh.secretkey,
                                                    Povh.endpoint), "X-Ovh-Signature": sig,
                        "Content-type": "application/json"}
        flavor = requests.get(Url.ROOT_URL_OVH + "cloud/project/%s/flavor"
                              % service, headers=queryheaders)
        for i in flavor:
            if sizename in i['name']:
                flavorid = i
                return flavorid


class Servers(Povh):
    servername = None
    size = None
    image = None
    region = None
    keyname = None
    serverid = None
    action = None

    def __init__(self, servername, size, image, region, keyname, serverid, action, applicationkey, secretkey,
                 endpoint):
        super(Servers, self).__init__(applicationkey, secretkey, endpoint)
        self.servername = servername
        self.size = size
        self.image = image
        self.region = region
        self.keyname = keyname
        self.serverid = serverid
        self.action = action

    @staticmethod
    def s_action(servername=None, size=None, image=None, region=None, keyname=None, serverid=None, **action):
        if action.get('Insert'):
            key = generate_rsa(bits=2048)
            s1 = hashlib.sha1()
            s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                               Povh.secretkey,
                                                               Povh.endpoint),
                                "POST", Url.ROOT_URL_OVH + "cloud/project/%s/instance"
                                % service(), get_time()]))
            sig = "$1$" + s1.hexdigest()
            queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time(),
                            "X-Ovh-Consumer": ovh_token(Povh.applicationkey,
                                                        Povh.secretkey,
                                                        Povh.endpoint),
                            "X-Ovh-Signature": sig, "Content-type": "application/json"}
            _body = '{"name": "%s","publicKey": "%s","region": "%s"}' % (keyname, key, region)
            data = requests.post(Url.ROOT_URL_OVH + "cloud/project/%s/sshkey" % service(),
                                 headers=queryheaders, body=_body)
            res = data.json()
            sshkey = res['id']

            if "Windows" not in image:
                _body = '{"flavorId": %s,"imageId": "%s","monthlyBilling": false,' \
                        '"name": "%s","region": "%s","sshKeyId": "%s}' \
                        % (Sizes.getsizeid(size), Images.getimageid(image),
                           servername, Region.getregionid(region), sshkey)

            else:
                _body = '{"flavorId": %s,"imageId": "%s","monthlyBilling": false,"name": "%s",' \
                        '"region": "%s"}' \
                        % (Sizes.getsizeid(size), Images.getimageid(image),
                           servername, Region.getregionid(region))

            s1 = hashlib.sha1()
            s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                               Povh.secretkey,
                                                               Povh.endpoint),
                                "POST", Url.ROOT_URL_OVH + "cloud/project/%s/instance"
                                % service(), get_time()]))
            sig = "$1$" + s1.hexdigest()
            queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time(),
                            "X-Ovh-Consumer": ovh_token(Povh.applicationkey,
                                                        Povh.secretkey,
                                                        Povh.endpoint),
                            "X-Ovh-Signature": sig, "Content-type": "application/json"}
            requests.post(Url.ROOT_URL_OVH + "cloud/project/%s/instance"
                          % service(), headers=queryheaders, body=_body)

        elif action.get('Reboot'):
            s1 = hashlib.sha1()
            s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                               Povh.secretkey,
                                                               Povh.endpoint),
                                "POST", Url.ROOT_URL_OVH + "cloud/project/%s/instance"
                                % service(), get_time()]))
            sig = "$1$" + s1.hexdigest()
            queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time(),
                            "X-Ovh-Consumer": ovh_token(Povh.applicationkey,
                                                        Povh.secretkey,
                                                        Povh.endpoint),
                            "X-Ovh-Signature": sig, "Content-type": "application/json"}
            requests.post(Url.ROOT_URL_OVH + "cloud/project/%s/instance/%s/reboot"
                          % (service(), serverid), headers=queryheaders)

        elif action.get('Remove'):
            s1 = hashlib.sha1()
            s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                               Povh.secretkey,
                                                               Povh.endpoint),
                                "DELETE", Url.ROOT_URL_OVH + "cloud/project/%s/instance"
                                % service(), get_time()]))
            sig = "$1$" + s1.hexdigest()
            queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time(),
                            "X-Ovh-Consumer": ovh_token(Povh.applicationkey,
                                                        Povh.secretkey,
                                                        Povh.endpoint),
                            "X-Ovh-Signature": sig, "Content-type": "application/json"}
            requests.delete(Url.ROOT_URL_OVH + "cloud/project/%s/instance/%s"
                            % (service(), serverid), headers=queryheaders)

        elif action.get('Rebuild'):
            s1 = hashlib.sha1()
            s1.update("+".join([Povh.applicationkey, ovh_token(Povh.applicationkey,
                                                               Povh.secretkey,
                                                               Povh.endpoint),
                                "POST", Url.ROOT_URL_OVH + "cloud/project/%s/instance"
                                % service(), get_time()]))
            sig = "$1$" + s1.hexdigest()
            queryheaders = {"X-Ovh-Application": Povh.applicationkey, "X-Ovh-Timestamp": get_time(),
                            "X-Ovh-Consumer": ovh_token(Povh.applicationkey,
                                                        Povh.secretkey,
                                                        Povh.endpoint),
                            "X-Ovh-Signature": sig, "Content-type": "application/json"}
            requests.post(Url.ROOT_URL_OVH + "cloud/project/%s/instance/%s/reinstall"
                          % (service(), serverid), headers=queryheaders)
