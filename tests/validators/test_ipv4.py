from util import case

valid_ipv4 = [
    "0.0.0.0", "9.9.9.9", "99.99.99.99",
    "29.29.29.29", "39.39.39.39",
    "255.255.255.255", "199.199.199.199",
    "192.168.191.1", "127.0.0.1"
]

invalid_ipv4 = [
    None, "", "127.0.0.", "127.0.0. ", ".0.0.1", " .0.0.1"
    "127.0.0.1 ", " 127.0.0.1", "127.0.0.", "127.0.0. 1"
    "x.1.1.1", "1.x.1.1", "1.1.x.1", "0.0.0.-",
    "256.0.0.0", "0.256.0.0", "0.0.256.0", "0.0.0.256",
    "001.001.001.001", "011.011.011.011", "01.01.01.01",
    "300.400.500.600", "00.00.00.00", "6.66.666.6666",
    "0.00.00.00", "0.0.0.00",
]


@case({
    "ipv4": {
        "valid": valid_ipv4,
        "invalid": invalid_ipv4
    }
})
def test_ipv4():
    pass
