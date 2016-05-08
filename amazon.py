__author__ = 'Michael'
from boto.ec2.connection import EC2Connection


class Amazon(object):
    accesskey = None
    secretkey = None

    def __init__(self, accesskey, secretkey):
        self.accesskey = accesskey
        self.secretkey = secretkey


def connect(accesskey, secretkey):
    aws_connect = EC2Connection(aws_access_key_id=accesskey, aws_secret_access_key=secretkey)
    return aws_connect


class Servers(Amazon):
    keyname = None
    image = None
    number = None
    serverid = None
    action = None
    groupname = None
    instype = None

    def __init__(self, instype, keyname, image, number, serverid, action, groupname, accesskey, secretkey):
        super(Servers, self).__init__(accesskey, secretkey)
        self.keyname = keyname
        self.image = image
        self.number = number
        self.serverid = serverid
        self.action = action
        self.groupname = groupname
        self.instype = instype

    @staticmethod
    def s_action(keyname=None, image=None, number=None, serverid=None, groupname=None, instype=None, **action):
        group = connect(Amazon.accesskey, Amazon.secretkey).create_security_group(name=groupname, description="")
        group.authorize('tcp', 22, 22, '0.0.0.0/0')
        group.authorize('tcp', 3389, 3389, '0.0.0.0/0')
        connect(Amazon.accesskey, Amazon.secretkey).create_key_pair(key_name=keyname)
        if action.get('Insert'):
            if 'spot' not in instype:
                if 'Windows' in connect(Amazon.accesskey, Amazon.secretkey).get_image(image_id=image).platform:
                    connect(Amazon.accesskey, Amazon.secretkey).run_instances(image_id=image,
                                                                              min_count=1,
                                                                              max_count=number,
                                                                              instance_type='m1.small',
                                                                              security_groups=group,
                                                                              monitoring_enabled=True)
                else:
                    connect(Amazon.accesskey, Amazon.secretkey).run_instances(image_id=image,
                                                                              min_count=1,
                                                                              max_count=number,
                                                                              instance_type='m1.small',
                                                                              security_groups=group,
                                                                              key_name=keyname,
                                                                              monitoring_enabled=True)
            else:
                if 'Windows' in connect(Amazon.accesskey, Amazon.secretkey).get_image(image_id=image).platform:
                    connect(Amazon.accesskey, Amazon.secretkey).request_spot_instances(price="0.24",
                                                                                       security_groups=group,
                                                                                       monitoring_enabled=True,
                                                                                       type='one-time',
                                                                                       image_id=image,
                                                                                       instance_type='m1.micro')
                else:
                    connect(Amazon.accesskey, Amazon.secretkey).request_spot_instances(price="0.24",
                                                                                       security_groups=group,
                                                                                       monitoring_enabled=True,
                                                                                       type='one-time',
                                                                                       image_id=image,
                                                                                       instance_type='m1.micro',
                                                                                       key_name=keyname)

        elif action.get('Remove'):
            connect(Amazon.accesskey, Amazon.secretkey).terminate_instances(instance_ids=serverid)

        elif action.get('Stop'):
            connect(Amazon.accesskey, Amazon.secretkey).stop_instances(instance_ids=serverid)
