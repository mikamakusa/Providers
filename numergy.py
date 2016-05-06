__author__ = 'Michael'
import requests
from urls import Url


class Numergy(object):
    accesskey = None
    secretkey = None
    tenantid = None

    def __init__(self, accesskey, secretkey, tenantid):
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.tenantid = tenantid


def version():
    request = requests.get(Url.ROOT_URL_NU)
    data = request.json()
    for i in (data['versions']['version']):
        if "CURRENT" in i['status']:
            _version = i['id']
            return _version


def token():
    body = '{"auth": {"apiAccessKeyCredentials": {"accessKey": "%s","secretKey": "%s" },"tenantId": "%s"}}' \
           % (Numergy.accesskey, Numergy.secretkey, Numergy.tenantid)
    request = requests.post(Url.ROOT_URL_NU + "/%s/tokens" % version, data=body)
    data = request.json()
    _token = (data['access']['token']['id'])
    return _token


class Images(Numergy):
    osname = None
    appname = None

    def __init__(self, osname, appname, accesskey, secretkey, tenantid):
        super(Images, self).__init__(accesskey, secretkey, tenantid)
        self.osname = osname
        self.appname = appname

    @staticmethod
    def getimageid(osname=None):
        global imgkey
        os_dict = {'WINDOWS_SERVER_2008_R2_ENT_64', 'WINDOWS_SERVER_2012_R2_STD_64', 'CENTOS_6_64', 'REDHAT_6_64',
                   'REDHAT_5_64', 'UBUNTU_14_04_64', 'UBUNTU_12_04_64', 'DEBIAN_7_64', 'DEBIAN_8_64'}
        for _os_ in os_dict:
            if osname in _os_:
                if 'Windows' in _os_:
                    imgkey = ''.join(list(((_os_.lower()).replace('_', ' ')).split()[0]))[:3] \
                             + (_os_.lower()).split()[1] + " " + \
                             (_os_.lower()).split()[2] + " " + (_os_.lower()).split()[3] \
                             + " " + (_os_.lower()).split()[4]
                else:
                    imgkey = ''.join(list(((_os_.lower()).replace('_', ' ')).split()[0]))[:3] + \
                             (_os_.lower().replace('_', ' ')).split()[1] + "_" + \
                             (_os_.lower().replace('_', ' ')).split()[2]
            else:
                raise Exception('Error')
            return imgkey

        request = requests.get(Url.ROOT_URL_NU + "/%s/%s/images" % (version, Numergy.tenantid),
                               headers={"X-Auth-Token": "%s" % token})
        data = request.json()
        for i in (data['images']):
            if imgkey in i['name']:
                imgid = i['id']
                return imgid

    @staticmethod
    def getappid(appname=None):
        global appkey
        app_dict = {'IIS', 'MSSQL', 'MSSQL_2014_STD', 'MSSQL_2014_WEB', 'REDHAT_MYSQL', 'UBUNTU_MYSQL',
                    'CENTOS_MYSQL', 'CENTOS_LAMP', 'REDHAT_LAMP', 'UBUNTU_LAMP'}
        for _app_ in app_dict:
            if appname in _app_.lower():
                if 'IIS'.lower():
                    appkey = 'Win2008 R2 IIS ENT 64'
                elif 'MSSQL'.lower():
                    appkey = 'Win2008 R2 MSSQL STD 64'
                elif 'MSSQL_2014_STD'.lower():
                    appkey = 'Win2012 R2 STD SQL 2014 STD 64'
                elif 'MSSQL_2014_WEB'.lower():
                    appkey = 'Win2012 R2 STD SQL 2014 WEB 64'
                elif 'REDHAT_MYSQL'.lower():
                    appkey = 'Red6 mysql 64'
                elif 'UBUNTU_MYSQL'.lower():
                    appkey = 'Ubu12 mysql 64'
                elif 'CENTOS_MYSQL'.lower():
                    appkey = 'Cen6 mysql 64'
                elif 'CENTOS_LAMP'.lower():
                    appkey = 'Cen6 LAMP 64'
                elif 'REDHAT_LAMP'.lower():
                    appkey = 'Red6 LAMP 64'
                elif 'UBUNTU_LAMP'.lower():
                    appkey = 'Ubu12 LAMP 64'
            return appkey

        request = requests.get(Url.ROOT_URL_NU + "/%s/%s/images" % (version, Numergy.tenantid),
                               headers={"X-Auth-Token": "%s" % token})
        data = request.json()
        for i in (data['images']):
            if appkey in i['name']:
                appid = i['id']
                return appid


class Sizes(Numergy):
    sizename = None

    def __init__(self, sizename, accesskey, secretkey, tenantid):
        super(Sizes, self).__init__(accesskey, secretkey, tenantid)
        self.sizename = sizename

    @staticmethod
    def getsizeid(sizename):
        global _size_
        size_dict = {'eXtraSmall', 'Small', 'Small+', 'Large', 'Large+', 'eXtraLarge'}
        for _size_ in size_dict:
            if sizename in _size_:
                request = requests.get(Url.ROOT_URL_NU + "/%s/%s/images" % (version, Numergy.tenantid),
                               headers={"X-Auth-Token": "%s" % token})
                data = request.json()
                for i in (data["flavors"]):
                    if _size_ in i["name"]:
                        flavorid = i['id']
                        return flavorid


class Servers(Numergy):
    action = None
    servername = None
    serverid = None
    size = None
    image = None
    appli = None

    def __init__(self, action, servername, serverid, size, image, appli, accesskey, secretkey, tenantid):
        super(Servers, self).__init__(accesskey, secretkey, tenantid)
        self.action = action
        self.servername = servername
        self.serverid = serverid
        self.size = size
        self.image = image
        self.appli = appli

    @staticmethod
    def s_actions(servername=None, size=None, image=None, appli=None, serverid=None, **action):
        global _imageid_
        if action.get('Insert'):
            _sizeid_ = Sizes.getsizeid(size)
            if appli is None:
                _imageid_ = Images.getimageid(image)
            else:
                _imageid_ = Images.getappid(appli)

            _body = '{"server": {"flavorRef": %s,"imageRef": %s,"name": %s,"password_delivery": API}}' \
                    % (_sizeid_, _imageid_, servername)
            requests.post(Url.ROOT_URL_NU + "/%s/%s/servers" % (version, Numergy.tenantid),
                          headers={"X-Auth-Token": "%s" % token}, data=_body)

        elif action.get('Reboot'):
            _body = '{"reboot": {"type": "SOFT"}}'
            requests.post(Url.ROOT_URL_NU + "/%s/%s/servers/%s/reboot"
                          % (version, Numergy.tenantid, serverid), data=_body, headers={"X-Auth-Token": "%s" % token})

        elif action.get('Rebuild'):
            _sizeid_ = Sizes.getsizeid(size)
            if appli is None:
                _imageid_ = Images.getimageid(image)
            else:
                _imageid_ = Images.getappid(appli)
            _body = '{"server": {"flavorRef": %s,"imageRef": %s,"name": %s,"password_delivery": API}}' % (
                    _sizeid_, _imageid_, servername)
            requests.post(Url.ROOT_URL_NU + "/%s/%s/servers/%s" % (version, Numergy.tenantid, serverid),
                          headers={"X-Auth-Token": "%s" % token}, data=_body)
