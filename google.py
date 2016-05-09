__author__ = 'Michael'
import requests
from urls import Url


class Google(object):
    token = None
    project = None

    def __init__(self, token, project):
        self.token = token
        self.project = project


class Images(Google):
    osname = None

    def __init__(self, osname, token, project):
        super(Images, self).__init__(token, project)
        self.osname = osname

    @staticmethod
    def getimageid(osname):
        os_dict = {'CENTOS_7', 'CENTOS_6', 'UBUNTU_16', 'UBUNTU_15', 'UBUNTU_14',
                   'UBUNTU_12', 'COREOS', 'DEBIAN_8', 'DEBIAN_7', 'SUSE_LINUX_11',
                   'SUSE_LINUX_12', 'REDHAT_6', 'REDHAT_7', 'OPENSUSE', 'WINDOWS_2012', 'WINDOWS_2008'}
        for _os_ in os_dict:
            image = _os_.lower().replace('_', ' ').split()[0]
            request = requests.get(
                Url.ROOT_URL_GO + "/%s/%s-cloud/global/images" % (Google.project, image),
                header={"Authorization": "Bearer %s" % Google.token})
            data = request.json()
            for i in data['items']:
                if osname in i['selfLink']:
                    imageid = i['selfLink'][-1]
                    return imageid


class Region(Google):
    regionname = None
    regionnum = None

    def __init__(self, regionname, regionnum, token, project):
        super(Region, self).__init__(token, project)
        self.regionname = regionname
        self.regionnum = regionnum

    @staticmethod
    def regionid(regionname, regionnum):
        global _region
        region_dict = {'ASIA_1', 'ASIA_2', 'ASIA_3', 'EUWE_1', 'EUWE_2', 'EUWE_4',
                       'USCE_1', 'USCE_2', 'USCE_3', 'USCE_6', 'USEA_2', 'USEA_3', 'USEA_4'}
        for _reg_ in region_dict:
            if regionname in _reg_.lower().replace('_', ' ').split()[0]:
                if "1" in regionnum:
                    return "a"
                elif "2" in regionnum:
                    return 'b'
                elif '3' in regionnum:
                    return 'c'
                elif '4' in regionnum:
                    return 'd'
                elif '5' in regionnum:
                    return 'e'
                elif '6' in regionnum:
                    return 'f'
                _region = _reg_.lower()+'*'+regionnum
                return _region
        request = requests.get(Url.ROOT_URL_GO + "/%s/regions" % Google.project,
                               header={"Authorization": "Bearer %s" % Google.token})
        data = request.json()
        for i in data['items']:
            if _region in i['items']:
                regionid = i['selfLink']
                return regionid


class Size(Google):
    sizename = None

    def __init__(self, sizename, token, project):
        super(Size, self).__init__(token, project)
        self.sizename = sizename

    @staticmethod
    def getsizeid(sizename):
        if sizename is None:
            sizeid = 'f1-micro'
        else:
            sizeid = 'n1-standard-1'

        request = requests.get(Url.ROOT_URL_GO + "/%s/zones/%s/machineType"
                               % (Google.project, Region.regionid(Region.regionname, Region.regionnum)),
                               header={"Authorization": "Bearer %s" % Google.token})
        data = request.json()
        for i in data['items']:
            if sizeid in i['items']:
                _sizeid = i['selfLink']
                return _sizeid


class Servers(Google):
    servername = None
    machinetype = None
    image = None
    serverid = None
    action = None
    region = None
    regionnum = None

    def __init__(self, servername, machinetype, image, serverid, action, region, regionnum, token, project):
        super(Servers, self).__init__(token, project)
        self.servername = servername
        self.machinetype = machinetype
        self.image = image
        self.serverid = serverid
        self.action = action
        self.region = region
        self.regionnum = regionnum

    @staticmethod
    def s_action(servername=None, machinetype=None, image=None, serverid=None, region=None, regionnum=None, **action):
        _imageid_ = Images.getimageid(image)
        _regionid_ = Region.regionid(region, regionnum)
        _sizeid_ = Size.getsizeid(machinetype)

        if action.get('Insert'):
            _body = '{"name": "%s","machineType": "%s","networkInterfaces": [{"accessConfigs": ' \
                    '[{"type": "ONE_TO_ONE_NAT","name": "External NAT"}],"network": "global/networks/default"}],' \
                    '"disks": [{"autoDelete": "true","boot": "true","type": "PERSISTENT","initializeParams": ' \
                    '{"sourceImage": "%s"}}]}' % (servername, _sizeid_, _imageid_)
            requests.post(
                Url.ROOT_URL_GO + "/%s/zones/%s/instances"
                % (Google.project, _regionid_),
                header={"Authorization": "Bearer %s" % Google.token}, data=_body)

        elif action.get('Remove'):
            requests.delete("https://www.googleapis.com/compute/v1/projects/%s/zones/%s/instances/%s"
                            % (Google.project, _regionid_, serverid),
                            header={"Authorization": "Bearer %s" % Google.token})

        elif action.get('Reboot'):
            requests.post("https://www.googleapis.com/compute/v1/projects/%s/zones/%s/instances/%s/reset"
                          % (Google.project, _regionid_, serverid),
                          header={"Authorization": "Bearer %s" % Google.token})


class Network(Google):
    netname = None
    regionname = None
    regionnum = None
    iprange = None
    attach = None
    boundto = None

    def __init__(self, project, netname, regionname, regionnum, iprange, attach, boundto, token):
        super(Network, self).__init__(token, project)
        self.netname = netname
        self.regionname = regionname
        self.regionnum = regionnum
        self.iprange = iprange
        self.attach = attach
        self.boundto = boundto

    def network(self, netname, iprange=None):
        _body = '{ "autoCreateSubnetworks": false, "name": "%s" }' % netname
        requests.post(Url.ROOT_URL_GO + "/%s/global/networks" % Google.project, data=_body)
        if iprange is not None:
            _body = '{"name": "%s","ipCidrRange": "%s","network": %s/%s/global/networks/%s"}' \
                    % (self.netname, self.iprange, Url.ROOT_URL_GO, Google.project, self.netname)
            requests.post(Url.ROOT_URL_GO + "/%s/regions/%s/subnetworks" % (Google.project,
                                                                            Region.regionid(self.regionname,
                                                                                            self.regionnum)),
                          data=_body)

    def external(self, netname, attach=None, boundto=None):
        _body = '{ "kind": "compute#address", "resourceType": "addresses", "name": "%s", "region": "%s" }' \
                % (netname, Region.regionid(self.regionname, self.regionnum))
        requests.post(Url.ROOT_URL_GO + "/%s/regions/%s/addresses" % (Google.project,
                                                                      Region.regionid(self.regionname,
                                                                                      self.regionnum)), data=_body)
        if attach is not None:
            _body = '{ "instanceName": "%s", "zone": "%s", "networkInterface": "nic0", ' \
                    '"accessConfigName": "External NAT", "kind": "compute#accessConfig", ' \
                    '"resourceType": "instances", ' \
                    '"address": "[IP address of newly created Static IP Address]" }' \
                    % (boundto, Region.regionid(self.regionname, self.regionnum))
            requests.post(Url.ROOT_URL_GO + "/%s/regions/%s/instances/%s"
                          % (Google.project, Region.regionid(self.regionname, self.regionnum), boundto), data=_body)


class Firewall(Google):
    ""