#!/usr/bin/env python3
import socket
import urllib.request
import json
import argparse
import warnings
import datetime
from ipwhois import IPWhois


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
        self.whois = IPWhois
        self.data = None

    def resolve(self, ip_addr):
        '''
        resolves whois info
        returns name and cleaned dictionary data.
        To return not cleaned keys just remove self.clean()
        '''
        obj = self.whois(ip_addr)
        self.data = obj.lookup_whois()
        cleaned_data = self.clean()
        return {"Whois Info": cleaned_data}

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
        self.info = self.socket.gethostbyaddr(ip_addr)
        self.info = self.clean()
        return {"DNS reverse Info": self.info}

    def clean(self):
        '''
        Cleans gethostbyaddr list
        '''
        # TODO return whole list or just one thing?
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
        self.arguments.add_argument("--ip", type=str, dest="ip_addr",
                                    action='store', required=True,
                                    help="Specifies ip address which \
                                    should be resolved.")

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
        for instance in self.info:
            info = instance.resolve(self.arguments.ip_addr)
            info_list.append(info)
        ip_dict = {"information": info_list}
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
    result = reverse.perform()
    return result


if __name__ == '__main__':
    RESULT = set_information()
    print(json.dumps(RESULT, indent=4))
