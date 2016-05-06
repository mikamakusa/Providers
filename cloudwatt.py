__author__ = 'Michael'
import requests
from urls import Url


class Cloudwatt(object):
    username = None
    password = None
    tenantid = None

    def __init__(self, username, password, tenantid):
        self.username = username
        self.password = password
        self.tenantid = tenantid


def token():
    _body = "<?xml version='1.0' encoding='UTF-8'?>" \
            "<auth xmlns='http://docs.openstack.org/identity/v2.0' tenantName='%s'>" \
            "<passwordCredentials username='%s' password='%s'/></auth>" \
            % (Cloudwatt.tenantid, Cloudwatt.username, Cloudwatt.password)
    request = requests.post("https://identity.fr1.cloudwatt.com/v2/tokens", data=_body)
    data = request.json()
    _token = data['access']['token']['id']
    return _token


class Images(Cloudwatt):
    osname = None
    appname = None

    def __init__(self, osname, appname, accesskey, secretkey, tenantid):
        super(Images, self).__init__(accesskey, secretkey, tenantid)
        self.osname = osname
        self.appname = appname

    @staticmethod
    def getimageid(osname=None):
        global imgkey
        os_dict = {'UBUNTU_14_04', 'UBUNTU_16_04', 'DEBIAN_7', 'DEBIAN_8', 'CENTOS_6_5', 'CENTOS_6_6',
                   'CENTOS_6_7', 'CENTOS_7_0', 'CENTOS_7_2', 'FEDORA_20', 'OPENSUSE', 'COREOS', 'SUSE_LINUX',
                   'WINDOWS_2012', 'WINDOWS_2008'}
        for _os_ in os_dict:
            if osname in _os_:
                if 'windows' in _os_.lower():
                    imgkey = _os_.capitalize().replace('_', ' ').split()[0] + ' Server ' + \
                             _os_.lower().replace('_', ' ').split()[-1] + ' R2'
                elif 'centos' in _os_.lower() and 'ubuntu' in _os_.lower():
                    imgkey = _os_.capitalize().replace('_', ' ').split()[0] + ' ' + _os_.replace('_', ' ').split()[1] + \
                             '.' + _os_.replace('_', ' ').split()[2]
                else:
                    imgkey = _os_.capitalize().replace('-', '')

        request = requests.get(Url.ROOT_URL_CW + "%s/images" % Cloudwatt.tenantid,
                               headers={"X-Auth-Token": "%s" % token})
        data = request.json()
        for i in (data['images']):
            if imgkey in i['name']:
                _imageid = i['id']
                return _imageid

    @staticmethod
    def getappid(appname=None):
        global appkey
        app_dict = {'PFSENSE', 'WEBMAIL', 'COZYCLOUD', 'DUPLICITY', 'DOCKER', 'ZABBIX',
                    'MEDIAWIKI', 'XONOTIC', 'MINECRAFT', 'STRONGSWAN', 'SHINKEN', 'GRAYLOG', 'LETSCHAT',
                    'DEVKIT', 'DOKUWIKI', 'JENKINS', 'LDAP', 'TOMCAT7', 'GITLAB', 'ETHERPAD', 'GHOST',
                    'POSTGRESQL', 'MEAN', 'WORDPRESS', 'LAMP'}

        for _app_ in app_dict:
            if appname in _app_.lower():
                appkey = _app_.lower()
        request = requests.get(Url.ROOT_URL_CW + "%s/images" % Cloudwatt.tenantid,
                               headers={"X-Auth-Token": "%s" % token})
        data = request.json()
        for i in (data['images']):
            if appkey in i['name']:
                appid = i['id']
                return appid


class Sizes(Cloudwatt):
    sizename = None

    def __init__(self, sizename, username, password, tenantid):
        super(Sizes, self).__init__(username, password, tenantid)
        self.sizename = sizename

    @staticmethod
    def getsizeid(sizename):
        global _size_
        size_dict = {'T1', 'S1', 'N1_CPU_2', 'N1_CPU_4', 'N1_CPU_8', 'N2_MEM_2', 'N2_MEM_4', 'N2_MEM_8'}
        for _size_ in size_dict:
            if sizename in _size_.lower().replace('_', ' '):
                request = requests.get(Url.ROOT_URL_CW + "%s/flavors" % Cloudwatt.tenantid,
                                       headers={"X-Auth-Token": "%s" % token})
                data = request.json()
                for i in (data['flavors']):
                    if _size_.lower().replace('_', ' ') in i['name']:
                        flavorid = i['id']
                        return flavorid


class Servers(Cloudwatt):
    action = None
    servername = None
    serverid = None
    size = None
    image = None
    appli = None
    number = None
    servpass = None

    def __init__(self, number, servpass, action, servername, serverid, size, image, appli, username, password,
                 tenantid):
        super(Servers, self).__init__(username, password, tenantid)
        self.action = action
        self.servername = servername
        self.serverid = serverid
        self.size = size
        self.image = image
        self.appli = appli
        self.number = number
        self.servpass = servpass

    @staticmethod
    def s_actions(servername=None, servpass=None, size=None, image=None, appli=None, number=None, serverid=None,
                  **action):
        global imageid, IP
        if action.get("insert"):
            # Get Security Group
            _body = '{"security_group":{"name":"Security","description":"SecGroup"}}'
            request = requests.post(Url.ROOT_URL_CW_NET + "security-groups",
                                    headers={"X-Auth-Token": "%s" % token}, data=_body)
            data = request.json()
            secgroup = data['security_group']['name']

            # Get Network Id
            _body = '{"network":{"name": "network1", "admin_state_up": true}}'
            request = requests.post(Url.ROOT_URL_CW_NET + "security-groups",
                                    headers={"X-Auth-Token": "%s" % token}, data=_body)
            data = request.json()
            netid = data['network']['id']
            _body = '{"subnet":{"network_id":"%s","ip_version":4,"cidr":"192.168.0.0/24"}}' % netid
            requests.post(Url.ROOT_URL_CW_NET + "security-groups",
                          headers={"X-Auth-Token": "%s" % token}, data=_body)

            # SSHKey & instance creation
            if image is not None:
                imageid = Images.getimageid(image)
            else:
                imageid = Images.getappid(appli)
            flavorid = Sizes.getsizeid(size)
            if imageid not in "Win":
                _body = '{"keypair":{"name":"cle"}}'
                request = requests.post("https://network.fr1.cloudwatt.com/v2/%s/os-keypairs",
                                        headers={"X-Auth-Token": "%s" % token}, data=_body)
                data = request.json()
                key = data['keypair']
                _body = '{"security_group_rule":{"direction":"ingress","port_range_min":"22",' \
                        '"ethertype":"IPv4","port_range_max":"22","protocol":"tcp","security_group_id":"%s"}}' \
                        % secgroup
                requests.post("https://network.fr1.cloudwatt.com/v2/security-group-rules",
                              headers={"X-Auth-Token": "%s" % token}, data=_body)
                _body = '{"server":{"name":"%s","key_name":"%s","imageRef":"%s","flavorRef":"%s",' \
                        '"max_count":%s,"min_count":1,"networks":[{"uuid":"%s"}],"metadata": {"admin_pass": "%s"},' \
                        '"security_groups":[{"name":"default"},{"name":"%s"}]}}' \
                        % (servername, key, imageid, flavorid, number, netid, servpass, secgroup)
                request = requests.post("https://compute.fr1.cloudwatt.com/v2/%s/servers" % Cloudwatt.tenantid,
                                        headers={"X-Auth-Token": "%s" % token}, data=_body)
                data = request.json()
                serverid = data['server']['id']
            else:
                _body = '{"security_group_rule":{"direction":"ingress","port_range_min":"3389",' \
                        '"ethertype":"IPv4","port_range_max":"3389","protocol":"tcp","security_group_id":"%s"}}' % (
                            secgroup)
                request = requests.post("https://compute.fr1.cloudwatt.com/v2/%s/servers" % Cloudwatt.tenantid,
                                        headers={"X-Auth-Token": "%s" % token}, data=_body)
                data = request.json()
                serverid = data['server']['id']

            # Public Network Interface Id
            request = requests.get("https://network.fr1.cloudwatt.com/v2/networks",
                                   headers={"X-Auth-Token": "%s" % token})
            data = request.json()
            for i in data['networks']:
                if "public" in i['name']:
                    netid = i['id']

            # Floatting IP
            _body = '{"floatingip":{"floating_network_id":"%s"}}' % netid
            request = requests.post("https://network.fr1.cloudwatt.com/v2/floatingips",
                                    headers={"X-Auth-Token": "%s" % token}, data=_body)
            data = request.json()
            IP = data['floatinip']['floating_ip_address']

            # Commit IP to Server
            _body = '{"addFloatingIp":{"address":"%s"}}' % IP
            requests.post("https://compute.fr1.cloudwatt.com/v2/%s/servers/%s/action" % (Cloudwatt.tenantid, serverid),
                          headers={"X-Auth-Token": "%s" % token}, data=_body)
        elif action.get("Remove"):
            requests.delete("https://compute.fr1.cloudwatt.com/v2/%s/servers/%s" % (Cloudwatt.tenantid, serverid),
                            headers={"X-Auth-Token": "%s" % token})
        elif action.get("Reboot"):
            requests.post("https://compute.fr1.cloudwatt.com/v2/%s/servers/%s/reboot" % (Cloudwatt.tenantid, serverid),
                          headers={"X-Auth-Token": "%s" % token})
        elif action.get("Rebuild"):
            request = requests.get(
                "https://compute.fr1.cloudwatt.com/v2/%s/servers/%s/detail" % (Cloudwatt.tenantid, serverid),
                headers={"X-Auth-Token": "%s" % token})
            data = request.json()
            for i in data['servers']:
                IP = i['addresses']['private']['addr']
                imageid = i['image']['id']
                servername = i['name']

            _body = '{"rebuild": {"imageRef": "%s","name": "%s","adminPass": "%s","accessIPv4": "%s"}}' % (
                imageid, servername, servpass, IP)
            requests.post("https://compute.fr1.cloudwatt.com/v2/%s/servers/%s/rebuild" % (Cloudwatt.tenantid, serverid),
                          headers={"X-Auth-Token": "%s" % token}, data=_body)