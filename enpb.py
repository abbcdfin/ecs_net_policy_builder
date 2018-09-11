#!/usr/bin/python

from datetime import datetime,timezone
import json
import argparse

# ecs network policy configuration, port range/protocol/in-out
net_policy = [
    "in, tcp, 80,443,8080,8443",
    "out, tcp, 22,443,2376,6443,8080,8443",
    "in, tcp, 2376,2379,2380,8472,9099,10250",
    "out, tcp, 443,2379,2380,6443,8472,9099",
    "in, tcp, 80,443,2376,6443,8472,9099,10250,10254,30000/32767",
    "out, tcp, 443,2379,2380,8472,9099,10250,10254",
    "in, tcp, 80,443,2376,8472,9099,10250,10254,30000/32767",
    "out, tcp, 443,6443,8472,9099,10254",
]

# internally needs to change to a structure
class EcsNetPolicy:

    def __init__(self, direction, protocol, portrange):

        default_properties = {"SourceCidrIp":"0.0.0.0/0","DestCidrIp":"","Description":"","NicType":"internet","DestGroupName":"","PortRange":"8080/8080","DestGroupId":"","Direction":"ingress","Priority":1,"IpProtocol\
":"TCP","SourcePortRange":"","SourceGroupOwnerAccount":"","Policy":"Accept","CreateTime":"2018-09-11T02:48:14Z","SourceGroupId":"","DestGroupOwnerAccount":"","SourceGroupName":""}
        
        self.properties = default_properties
        
        self.properties['Direction'] = "ingress"
        if (direction != "in"):
            self.properties['SourceCidrIp'] = ""
            self.properties['DestCidrIp'] = "0.0.0.0/0"
            self.properties['Direction'] = "egress"

        self.properties['IpProtocol'] = protocol.upper()

        self.properties['PortRange'] = portrange

        self.properties['CreateTime'] = datetime.now(
            timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
    def __eq__(self, other):
        if (self.properties['Direction'] == other.properties['Direction'] and
            self.properties['IpProtocol'] == other.properties['IpProtocol'] and 
            self.properties['PortRange'] == other.properties['PortRange']):
            return True
        
        return False 
        
class EcsNetPolicyGroup:
    def __init__(self):
        self.policies = []

    def find(self, policy):
        for i in self.policies:
            if policy == i:
                return True

        return False
        
    def add(self, config_line):
        items = config_line.split(',')
        direction = items[0].strip()
        protocol = items[1].strip()
        for portrange in items[2:]:
            portrange = portrange.strip()
            if not ('/' in portrange):
                portrange = "%s/%s" % (portrange, portrange)
            
            policy = EcsNetPolicy(direction, protocol, portrange)
            if not self.find(policy):
                self.policies.append(policy)

    def build_json_file(self, output_path):
        group = [];
        for p in self.policies:
            group.append(p.properties)

        fo = open(output_path, "w+t")
        fo.write(json.dumps(group));
        fo.close()

parser = argparse.ArgumentParser(description='ECS Network Policy Builder')
parser.add_argument('--output', '-o', dest='output_path', action='store')

args = parser.parse_args()


pg = EcsNetPolicyGroup()
for c in net_policy:
    pg.add(c)

pg.build_json_file(args.output_path)
