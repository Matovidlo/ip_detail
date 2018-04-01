#!/usr/bin/env python3
import socket
import urllib.request
import json
import argparse
import warnings
import datetime
import re
from telnetlib import Telnet
# from IPy import IP

def primitive_clean(dictionary, condition):
    '''
    This is used to clean None values inside dict with given condition
    '''
    clean_result = {}
    for key, value in dictionary.items():
        if value != condition:
            clean_result[key] = value
    return clean_result


class WhoisInfo:
    '''
    This class should initialize arguments and resolve Whois informations
    '''
    def __init__(self):
        self.option = "-w"
        self.argument = "whois"
        self.help = "When specified, whois information is not printed"
        self.input_whois = json.load(open("./registrar/ipv4_ASR.json"))
        self.data = None
        self.resolution = None

    def get_hostname(self, ip_addr):
        '''
        Gets whois server hostname from iana ipv4 address space register
        which is stored inside ./registrar/ipv4_ASR.json.
        '''
        record = self.input_whois["record"]
        index = ip_addr.index(".")
        resolve = ip_addr[:index]
        while len(resolve) != 3:
            resolve = '0' + resolve
        for item in record:
            compare_value = item["prefix"][:-2]
            if compare_value == resolve:
                return item["whois"]

    def convert_to_json(self, referral):
        '''
        Serialize whois response message to json. This is just for nice format
        of output stream.
        '''
        try:
            index = self.resolution.index("inetnum")
        except ValueError:
            return {"Whois Info": "not found"}
        json_result = {"Whois Info": referral}
        old_key = None
        for items in self.resolution[index::].splitlines():
            try:
                index = items.index(":")
            except ValueError:
                continue
            if old_key == items[:index]:
                # create list from it
                json_key = json_result[items[:index]]
                if isinstance(json_key, str):
                    json_result[items[:index]] = json_key.splitlines()
                json_result[items[:index]].append((items[index + 1:].strip()))
            else:
                json_result[items[:index]] = items[index + 1:].strip()
            old_key = items[:index]
        return json_result


    def get_answer(self, hostname, message, port=43):
        '''
        Send message request to given hostname. Read response and decode it
        with different decodes.
        '''
        # DEBUG
        print("hostname: {} port: {}".format(hostname, port))
        with Telnet(hostname, port) as telnet:
            telnet.write(message.encode())
            try:
                data = telnet.read_all()
            except ConnectionResetError:
                self.resolution = ""
                return
        try:
            self.resolution = data.decode("utf-8")
        except UnicodeDecodeError:
            self.resolution = data.decode("latin-1")


    def resolve(self, ip_addr):
        '''
        resolves whois info
        returns name and cleaned dictionary data.
        To return not cleaned keys just remove self.clean()
        '''
        hostname = self.get_hostname(ip_addr)
        message = ip_addr + "\r\n"
        try:
            self.get_answer(hostname, message)
        except TimeoutError:
            self.resolution = ""

        # get refferal if whois server has no answer
        try:
            index = self.resolution.index("ReferralServer")
        except ValueError:
            return self.convert_to_json(hostname)
        # get refferal, splitlines, get first referral with port
        # and get its value
        referral = re.search(r"(\w+[\.:]){2,}", self.resolution[index::])
        referral = referral.group(0)[:-1]
        # add '.net' when is absent
        if referral[-4::] == ".net" or referral[-4::] == ".com":
            pass
        else:
            referral = referral + ".net"

        referral_port = re.search(r"\:\d+", self.resolution[index::])
        if referral_port is not None:
            referral_port = referral_port.group(0)[1::]
        else:
            referral_port = 43

        # send packet to referral
        try:
            self.get_answer(referral, message, referral_port)
        # except socket.gaierror:
        #     referral = re.search(r"(\w+[\.]){2,}.*", self.resolution[index::])
        #     self.get_answer(referral.group(0), message, referral_port)
        except TimeoutError:
            self.resolution = ""
        return self.convert_to_json(referral)

    def clean(self):
        '''
        This function cleans None values inside whois json dictionary.
        There is loop to get names of None keys and second to delete those keys.
        Returns new clean dictionary
        '''
        result = primitive_clean(self.data, None)
        # Lets prepare list
        item_names = []
        for values in self.data.values():
            if isinstance(values, list):
                for index, list_value in enumerate(values):
                    item_names.append(index)
                    for key, value in list_value.items():
                        if value is None:
                            item_names.append(key)

        # clean exact keys
        for items in item_names:
            if isinstance(items, int):
                index = items
            else:
                del result["nets"][index][items]
        return result


class DNSReverseInfo:
    '''
    This class should initialize arguments and resolve DNS reverse record.
    '''
    def __init__(self):
        self.option = "-r"
        self.argument = "reverse"
        self.help = "When specified, reverse dns is not resolved and \
        not printed in output"
        self.socket = socket
        self.info = None

    def resolve(self, ip_addr):
        '''
        resolve dns record
        returns dictionary with name and informations.
        '''
        try:
            self.info = self.socket.gethostbyaddr(ip_addr)
        except socket.herror:
            return {"DNS reverse Info": "Not Found"}
        self.info = self.clean()
        return {"DNS reverse Info": self.info}

    def clean(self):
        '''
        Cleans gethostbyaddr list
        '''
        return self.info[0]

class GeoLocationInfo:
    '''
    Class which translates ip address to geo location.
    '''
    def __init__(self):
        self.option = "-g"
        self.argument = "geolocation"
        self.help = "When specified, geolocation is not translated"
        self.geolocation = urllib.request
        self.location_info = None

    def resolve(self, ip_addr):
        '''
        method which trasnalte ip address with help of freegeoip site
        returns dict with name and location info
        '''
        url_of_location = "http://www.freegeoip.net/json/{}".format(ip_addr)
        self.location_info = json.loads(self.geolocation.urlopen(url_of_location)
                                        .read())
        # Clean empty values
        self.location_info = self.clean()
        return {"GeoLocation Info": self.location_info}

    def clean(self):
        '''
        cleans None fields from location info
        '''
        result = primitive_clean(self.location_info, '')
        return result


class UnixTimestamp:
    '''
    Class which procudes unix timestamp
    '''
    def __init__(self):
        self.option = "-t"
        self.argument = "timestamp"
        self.help = "When specified, no unix timestamp is written to output."
        self.timestamp = datetime.datetime.now()

    def resolve(self, timestamp=None):
        '''
        returns timestamp info in dict name and string.
        '''
        # %Z is for timezone. Could be removed
        self.timestamp = datetime.datetime.now()
        info = self.format_timestamp("%Y-%m-%d %I:%M:%S%p (%Z)")
        return {"Timestamp Info": info}


    def format_timestamp(self, date_format):
        '''
        formats timestamp with given date_format.
        returns formated date.
        '''
        return self.timestamp.strftime(date_format)

class Reverse:
    '''
    Class which is responsible of parsing command line arguments.
    '''
    def __init__(self):
        self.arguments = argparse.ArgumentParser()
        self.query = []
        self.info = []
        self.arguments.add_argument("--ip", dest="ip_addr",
                                    action='store', required=True,
                                    help="Specifies ip address which \
                                    should be resolved.")
        self.ip_set = set()

    def parse_if_file(self):
        '''
        parses file with infohash{ip_address,port}, takes ip_address
        and perform class actions.
        '''
        try:
            data = json.load(open(self.arguments.ip_addr))
        except FileNotFoundError:
            return
        except json.decoder.JSONDecodeError:
            print("File is not in json format.")
            exit(1)
        for value in data.values():
            self.ip_set.add(value[0][0])

    def add_args(self, info):
        '''
        Adds argument and class object in info list.
        Used later to resolve state.
        Strict to have info.argument info.option and info.help to add argument.
        '''
        self.info.append(info)
        self.query.append(info.option)
        self.arguments.add_argument(info.option, dest=info.argument,
                                    action='store_const', const=info.option,
                                    help=info.help)

    def change_query_information(self):
        '''
        Changes query list based on given parameters. When given then
        class object is not resolved.
        '''
        self.arguments = self.arguments.parse_args()
        for option in vars(self.arguments):
            # Ip_address option is required
            if option == "ip_addr":
                continue
            attribute = getattr(self.arguments, option)
            if attribute is not None:
                index = self.query.index(attribute)
                del self.query[index]
                del self.info[index]

    def perform(self):
        '''
        perform resolve action of all instances.
        Strict to have resolve method in class
        '''
        info_list = []
        ip_dict = {}

        if self.ip_set != set():
            for ip_address in self.ip_set:
                for instance in self.info:
                    info = instance.resolve(ip_address)
                    info_list.append(info)
                    # if len(info_list) > 50:
                        # info_list = []
            ip_dict["Information"] = info_list
            return ip_dict
        else:
            for instance in self.info:
                info = instance.resolve(self.arguments.ip_addr)
                info_list.append(info)
            ip_dict["Information"] = info_list
        return ip_dict


def set_information():
    '''
    Sets all class information, adds arguments. Edition is easy.
    Just add new class with new infomation about ip-address.
    '''
    warnings.filterwarnings("ignore")
    reverse = Reverse()

    info = DNSReverseInfo()
    reverse.add_args(info)
    info = UnixTimestamp()
    reverse.add_args(info)
    info = WhoisInfo()
    reverse.add_args(info)
    info = GeoLocationInfo()
    reverse.add_args(info)

    reverse.change_query_information()
    reverse.parse_if_file()
    result = reverse.perform()
    return result


if __name__ == '__main__':
    RESULT = set_information()
    print(json.dumps(RESULT, indent=4))
