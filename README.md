# ciscodiffableconfig

CiscoDiffableConfig implements an order-insensitive but order-preserving diff for Cisco-style network device configs. It has no dependencies outside of the Python standard library. I've used it on Python 3.11, YMMV on older versions.

I've used this for the past year or so to diff running-configurations with new machine-generated configs and it's been very useful.

## Usage

```python
from ciscodiff import CiscoDiffableConfig

stored_config_str = "…"
running_config_str = "…"

stored_config = CiscoDiffableConfig(stored_config_str)
running_config = CiscoDiffableConfig(running_config_str)
print(running_config.concise_diff(stored_config))
```

`concise_diff()` outputs the changed lines as well as their parent/ancestor lines in the hierarchy, like so:

```
-ip as-path access-list no_hurricane_electric deny ^6939,
-ip as-path access-list no_hurricane_electric deny ^6939$
-ip as-path access-list no_hurricane_electric permit .*
 interface ethernet1/1/1:1
+ mtu 9032
 interface ethernet1/1/3:1
- shutdown
+ no shutdown
+ ip access-group nordic_ingress_v4 in
+ ipv6 access-group nordic_ingress_v6 in
 interface ethernet1/1/4:1
- no shutdown
- no switchport
+ shutdown
+ switchport access vlan 1
```

I recommend just copying this over to your project for now, but let me know in the issues if you'd like it on PyPI.
