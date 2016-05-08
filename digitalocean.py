__author__ = 'Michael'
import requests
from urls import Url
from providers import generate_rsa


class DigitalOcean(object):
    token = None

    def __init__(self, token):
        self.token = token


class Images(DigitalOcean):
    osname = None
    appname = None

    def __init__(self, osname, appname, token):
        super(Images, self).__init__(token)
        self.osname = osname
        self.appname = appname

    @staticmethod
    def getimageid(osname=None):
        global imgkey
        os_dict = {'COREOS', 'CENTOS_5_8', 'FREEBSD_10_1', 'FEDORA_22', 'FREEBSD_10_2', 'FEDORA_23', 'CENTOS_6_5',
                   'DEBIAN_8', 'UBUNTU_15_10', 'UBUNTU_12_04', 'UBUNTU_14_04', 'CENTOS_7_0'}
        for _os_ in os_dict:
            if osname in _os_:
                imgkey = (_os_.lower()).replace("_", "-")+'-x64'
            else:
                raise Exception('Error')
            return imgkey

        request = requests.get(Url.ROOT_URL_DO + "/images",
                               headers={"Authorization": "Bearer %s" % DigitalOcean.token})
        data = request.json()
        for i in data['images']:
            if imgkey in i['slug']:
                imageid = i['id']
                return imageid

    @staticmethod
    def getappid(appname=None):
        global appkey
        app_dict = {'ELIXIR', 'PHPMYADMIN', 'ELK', 'MUMBLE', 'RUBY_ON_RAILS', 'DJANGO',
                    'DRUPAL', 'REDIS', 'CASSANDRA', 'MONGODB', 'MEDIAWIKI', 'WORDPRESS', 'LEMP',
                    'LAMP', 'MAGENTO', 'OWNCLOUD', 'DRONE', 'DISCOURSE', 'NODE', 'GHOST', 'JOOMLA',
                    'DOCKER', 'MEAN', 'DOKKU', 'GITLAB', 'REDMINE'}

        for _app_ in app_dict:
            if appname.lower() in _app_.lower():
                appkey = _app_.lower()
                request = requests.get(Url.ROOT_URL_DO + "/images?page=1&per_page=100&type=application",
                                       headers={"Authorization": "Bearer %s" % DigitalOcean.token})
                data = request.json()
                for i in data['images']:
                    if appkey in i['slug']:
                        appid = i['id']
                        return appid


class Sizes(DigitalOcean):
    sizename = None

    def __init__(self, sizename, token):
        super(Sizes, self).__init__(token)
        self.sizename = sizename

    @staticmethod
    def getsizeid(sizename):
        global sizekey
        size_dict = {'RAM_512MB', 'RAM_1024MB', 'RAM_2048MB', 'RAM_4096MB', 'RAM_8192MB',
                     'RAM_16384MB', 'RAM_32768MB', 'RAM_65536MB'}
        for _size_ in size_dict:
            if sizename.lower() in ((_size_.lower()).replace("_", " ")).split()[1]:
                sizekey = ((_size_.lower()).replace("_", " ")).split()[1]
                return sizekey

        request = requests.get(Url.ROOT_URL_DO + "/sizes",
                               headers={"Authorization": "Bearer %s" % DigitalOcean.token})
        data = request.json()
        for i in data['sizes']:
            if sizekey in i['slug'] and "True" in i['available']:
                sizeid = i['slug']
                return sizeid


class Regions(DigitalOcean):
    regionname = None
    number = None

    def __init__(self, regionname, number, token):
        super(Regions, self).__init__(token)
        self.regionname = regionname
        self.number = number

    @staticmethod
    def getregionid(regionname, number):
        global _reg_
        region_dict = {'AMS2', 'AMS3', 'LON1', 'NYC2', 'NYC3', 'SFO1', 'SGP1', 'FRA1', 'TOR1'}
        for _reg_ in region_dict:
            if regionname[:3] in _reg_.lower()[:3] and number in _reg_.lower()[-1]:
                request = requests.get(Url.ROOT_URL_DO + "/regions",
                                       headers={"Authorization": "Bearer %s" % DigitalOcean.token})
                data = request.json()
                for i in data['regions']:
                    if _reg_ in i['slug'] and "True" in i['available']:
                        regionid = i['slug']
                        return regionid


class Servers(DigitalOcean):
    action = None
    servername = None
    servernum = None
    serverid = None
    size = None
    image = None
    appli = None
    region = None
    regionnum = None
    network = 'null'

    def __init__(self, servername, servernum, serverid, size, image, appli, region, regionnum, action, network, token):
        super(Servers, self).__init__(token)
        self.action = action
        self.servername = servername
        self.servernum = servernum
        self.serverid = serverid
        self.size = size
        self.image = image
        self.appli = appli
        self.region = region
        self.regionnum = regionnum
        self.network = network

    @staticmethod
    def s_actions(network='null', servername=None, servernum=None, size=None, image=None, appli=None,
                  serverid=None, region=None, regionnum=None, **action):
        global _imageid_, _body, keyid
        key = generate_rsa(bits=2048)
        _body = '{"name": "My SSH Public Key","public_key": "%s"}' % key
        request = requests.post(Url.ROOT_URL_DO + "/account/keys",
                                headers={"Authorization": "Bearer %s" % DigitalOcean.token},
                                data=_body)
        data = request.json()
        for _data_ in data['ssh_key']:
            keyid = _data_['id']
        if appli is None:
            _imageid_ = Images.getimageid(image)
        else:
            _imageid_ = Images.getappid(appli)
        _regionid = Regions.getregionid(region, str(regionnum))
        _size = Sizes.getsizeid(size)
        if network is not 'null':
            return 'yes'
        if action.get("insert"):
            if servernum is None:
                _body = '{"name": "%s","region": "%s","size": "%s","image": "%s","ssh_keys": "%s","backups": false,' \
                        '"ipv6": true,"user_data": null,"private_networking": %s}' \
                        % (servername, _regionid, _size, _imageid_, keyid, network)
            else:
                i = 0
                n1 = ""
                while i != (int(servernum)-1):
                    n1 += '"'+servername + str(i)+'"'+", "
                    _body = '{"name": [%s, "%s"],"region": "%s","size": "%s","image": "%s","ssh_keys": "%s",' \
                        '"backups": false,"ipv6": ' \
                        'true,"user_data": null,"private_networking": %s}' \
                        % (n1, servername+str(i+1), _regionid, _size, _imageid_, keyid, network)
            requests.post(Url.ROOT_URL_DO + "/droplets",
                          headers={"Authorization": "Bearer %s" % DigitalOcean.token},
                          data=_body)

        if action.get('reboot'):
            _body = '{"type":"reboot"}'
            requests.post(Url.ROOT_URL_DO + "/droplets/%s" % serverid,
                          headers={"Authorization": "Bearer %s" % DigitalOcean.token}, data=_body)

        if action.get('remove'):
            requests.delete(Url.ROOT_URL_DO + "/droplets/%s" % serverid,
                            headers={"Authorization": "Bearer %s" % DigitalOcean.token})

        if action.get('rebuild'):
            global _imageid_
            if appli is None:
                _imageid_ = Images.getimageid(image)
            else:
                _imageid_ = Images.getappid(appli)
            _body = '{"type":"rebuild","image":"%s"}' % _imageid_
            requests.post(Url.ROOT_URL_DO + "/droplets/%s/actions" % serverid,
                          headers={"Authorization": "Bearer %s" % DigitalOcean.token}, data=_body)
