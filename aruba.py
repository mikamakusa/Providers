__author__ = 'Michael'
from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.objects import SmartVmCreator, ProVmCreator
import time


class Aruba(object):
    region = None
    username = None
    password = None

    def __init__(self, dc, username, password):
        self.dc = dc
        self.username = username
        self.password = password


def connect():
    dc_dict = {1: 'Italy1', 2: 'Italy2', 3: 'Czech', 4: 'France', 5: 'Germany', 6: 'UK'}
    dc = dc_dict.keys()[dc_dict.values().index(Aruba.region)]
    token = CloudInterface(dc=dc)
    return token


class Images(Aruba):
    imgname = None
    pack = None

    def __init__(self, imgname, pack, dc, username, password):
        super(Images, self).__init__(dc, username, password)
        self.imgname = imgname
        self.pack = pack

    @staticmethod
    def getpack(pack):
        pack_dict = {1: 'smart', 2: 'lowcost', 3: 'hyperv', 4: 'vmware'}
        packid = pack_dict.keys()[pack_dict.values().index(pack)]
        return packid

    @staticmethod
    def getimageid(imgname):
        region = connect()
        templ = region.find_template(hv=Images.getpack(Images.pack))
        for t in templ:
            if imgname in t.id_code and "True" in t.enabled:
                imageid = t.template_id
                return imageid


class Sizes(Aruba):
    sizename = None

    def __init__(self, sizename, dc, username, password):
        super(Sizes, self).__init__(dc, username, password)
        self.sizename = sizename

    @staticmethod
    def getsizeid(sizename):
        size = {"small", 'medium', 'large', 'extra large'}
        for i in size:
            if sizename not in i:
                Exception("size error")
            else:
                return i


class Servers(Aruba):
    servername = None
    servpass = None
    number = None
    cpu = None
    ram = None
    disk = None
    action = None
    serverid = None
    size = None
    pack = None
    image = None
    disknumber = None

    def __init__(self, size, pack, image, serverid, action, servername, servpass, number,  cpu, ram, disk,
                 disknumber, username, password, region):
        super(Servers, self).__init__(username, password, region)
        self.servername = servername
        self.servpass = servpass
        self.number = number
        self.cpu = cpu
        self.ram = ram
        self.disk = disk
        self.action = action
        self.serverid = serverid
        self.pack = pack
        self.image = image
        self.size = size
        self.disknumber = disknumber

    @staticmethod
    def s_action(servername=None, servpass=None, serverid=None, number=None,
                 cpu=None, ram=None, disk=None, pack=None, image=None, size=None, disknumber=None, **action):
        connect().login(username=Aruba.username, password=Aruba.password, load=True)
        if action.get('Insert'):
            if 'smart' in Images.getpack(pack):
                if number is None:
                    c = SmartVmCreator(name=servername,
                                       admin_password=servpass,
                                       template_id=Images.getimageid(image),
                                       auth_obj=connect().auth)
                    c.set_type(size=Sizes.getsizeid(size))
                    c.commit(url=connect().wcf_baseurl, debug=True)
                else:
                    i = 0
                    while i < int(number):
                        i += 1
                        c = SmartVmCreator(name=servername + i,
                                           admin_password=servpass,
                                           template_id=Images.getimageid(image),
                                           auth_obj=connect().auth)
                        c.set_type(size=Sizes.getsizeid(size))
                        c.commit(url=connect().wcf_baseurl, debug=True)
                        time.sleep(60)
            else:
                if number is None:
                    ip = connect().purchase_ip()
                    pvm = ProVmCreator(name=servername,
                                       admin_password=servpass,
                                       template_id=Images.getimageid(image),
                                       auth_obj=connect().auth)
                    pvm.set_cpu_qty(int(cpu))
                    pvm.set_ram_qty(int(ram))
                    pvm.add_public_ip(public_ip_address_resource_id=ip.resid, primary_ip_address=True)
                    pvm.add_virtual_disk(int(disk))
                    pvm.commit(url=connect().wcf_baseurl, debug=True)
                else:
                    i = 0
                    while i < int(number):
                        i += 1
                        ip = connect().purchase_ip()
                        pvm = ProVmCreator(name=servername + i,
                                           admin_password=servpass,
                                           template_id=Images.getimageid(image),
                                           auth_obj=connect().auth)
                        pvm.set_cpu_qty(int(cpu))
                        pvm.set_ram_qty(int(ram))
                        pvm.add_public_ip(public_ip_address_resource_id=ip.resid, primary_ip_address=True)
                        pvm.add_virtual_disk(int(disk))
                        pvm.commit(url=connect().wcf_baseurl, debug=True)
                        time.sleep(60)
        if 'smart' not in Images.getpack(pack):
            if action.get('Reboot'):
                connect().login(username=Aruba.username, password=Aruba.password, load=True)
                connect().poweroff_server(server_id=serverid)
                time.sleep(60)
                connect().poweron_server(server_id=serverid)
            elif action.get('Remove'):
                connect().login(username=Aruba.username, password=Aruba.password, load=True)
                connect().poweroff_server(server_id=serverid)
                time.sleep(60)
                connect().delete_vm(server_id=serverid)
            elif action.get('Remove Disk'):
                vm = connect().get_vm(pattern=servername)[0]
                vm.poweroff()
                vm.remove_virtual_disk(virtual_disk_id=disknumber)
                time.sleep(60)
                connect().poweron_server(server_id=serverid)
            elif action.get('Add disk'):
                vm = connect().get_vm(pattern=servername)[0]
                vm.poweroff()
                vm.add_virtual_disk(size=int(disk))
                time.sleep(60)
                connect().poweron_server(server_id=serverid)
            elif action.get('Add Ram'):
                vm = connect().get_vm(pattern=servername)[0]
                vm.poweroff()
                vm.set_cpu_qty(ram)
                time.sleep(60)
                vm.poweron_server()
            elif action.get('Add Cpu'):
                vm = connect().get_vm(pattern=servername)[0]
                vm.poweroff()
                vm.set_cpu_qty(cpu)
                time.sleep(60)
                vm.poweron_server()               
        else:
            if action.get('Rebuild'):
                for vm in (connect()).get_vm(pattern=serverid):
                    vm.poweroff()
                    time.sleep(60)
                    vm.reinitialize(admin_password=servpass)


class Network(Aruba):
    netname = None
    servername = None

    def __init__(self, netname, servername, dc, username, password):
        super(Network, self).__init__(dc, username, password)
        self.netname = netname
        self.servername = servername

    @staticmethod
    def netcreate(netname):
        connect().purchase_vlan(vlan_name=netname)

    @staticmethod
    def netattach(netname, servername):
        vlan = connect().get_vlan(vlan_name=netname)
        vmid = connect().vmlist.find(servername)[0]
        netif = connect().get_server_detail(vmid)['NetworkAdapters'][1]
        connect().attach_vlan(network_adapter_id=netif['id'], vlan_resource_id=vlan.resource_id)

    @staticmethod
    def netdetach(netname, servername):
        vlan = connect().get_vlan(vlan_name=netname)
        vmid = connect().vmlist.find(servername)[0]
        netif = connect().get_server_detail(vmid)['NetworkAdapters'][1]
        connect().detach_vlan(network_adapter_id=netif, vlan_resource_id=vlan)

    @staticmethod
    def netremove(netname):
        vlan = connect().get_vlan(vlan_name=netname)
        connect().remove_vlan(vlan_resource_id=vlan)
