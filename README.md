# ip_detail

This project should give information about ip from tools like whois, geolocation
and gethostbyname. Result is in json format and can be redisigned easily.

### Getting Started
To run this program you need prerequisites.

### Problems to be solved
```
1. This implementation is very slow on bigger data set of ip's. So there is an
appeal to rework IpWhois implementation. On 6000 ip's it takes about 30 minutes
to solve Timestamp(primitive), GeoLocation and DNS Reverse Resolution.
```
Maybe solution -
2. Currently working on rust variant, which I think should be faster than python
variant.

### To Contribute
Maybe refactor some not obvious parts, but this is mostly very simple client
so there is not that much work. I would appreciate when someone contribute to
make this implementation faster. Thanks a lot.

### Prerequisites
To run this application you need python3.6, Ipwhois package installed by pip.
```
pip3.6 install ipwhois --user
```
Another option is to donwload it from python packaging website. Used version is
1.0.0.

### Example output
Output should looks like this after entering command:
```
./ip_detail --ip 147.229.216.41
or
python3.6 ip_detail --ip 147.229.216.41
```

Output:
```
{
    "information": [
        {
            "DNS reverse Info": "a04-0911b.kn.vutbr.cz"
        },
        {
            "Timestamp Info": "2018-03-23 12:49:00PM ()"
        },
        {
            "Whois Info": {
                "asn_registry": "ripencc",
                "asn": "197451",
                "asn_cidr": "147.229.192.0/19",
                "asn_country_code": "CZ",
                "asn_date": "1993-01-11",
                "asn_description": "VUTBR-AS, CZ",
                "query": "147.229.216.41",
                "nets": [
                    {
                        "cidr": "147.229.0.0/17, 147.229.128.0/18,
                        		147.229.192.0/19, 147.229.224.0/20,
                        		147.229.240.0/21, 147.229.248.0/22,
                        		147.229.252.0/23, 147.229.254.0/24",
                        "name": "VUTBRNET",
                        "handle": "CA6319-RIPE",
                        "range": "147.229.0.0 - 147.229.254.255",
                        "description": "Brno University of Technology",
                        "country": "CZ",
                        "address": "Brno University of Technology\nAntoninska 1\n601 90 Brno\nThe Czech Republic",
                        "emails": [
                            "abuse@vutbr.cz"
                        ],
                        "created": "2014-11-19T08:23:45Z",
                        "updated": "2015-01-30T08:37:07Z"
                    },
                    {
                        "cidr": "147.229.192.0/19",
                        "range": "147.229.192.0 - 147.229.223.255",
                        "description": "VUTBR-NET3",
                        "created": "2014-12-04T19:08:46Z",
                        "updated": "2014-12-04T19:08:46Z"
                    }
                ]
            }
        },
        {
            "GeoLocation Info": {
                "ip": "147.229.216.41",
                "country_code": "CZ",
                "country_name": "Czechia",
                "time_zone": "Europe/Prague",
                "latitude": 50.0848,
                "longitude": 14.4112,
                "metro_code": 0
            }
        }
    ]
}
```

## Built With

* [Fedora 26](https://getfedora.org/) - Distribution on which was tool developed
* [Python3.6](https://www.python.org/) - Programming language which is used to run
