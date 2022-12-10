import unittest
from utilities import CONFIG


class TestConfig(unittest.TestCase):
    def test_sections(self):
        for section in ["GENERAL", "SENSORS", "RELAYS", "DATABASE"]:
            with self.subTest("check if section exists", section=section):
                self.assertIn(section, CONFIG.sections())

    def test_general_section(self):
        self.assertFalse(CONFIG["GENERAL"]["site"] == "")

    def test_sensors_section(self):
        for sensor in CONFIG["SENSORS"].keys():
            with self.subTest("check if sensor addresses are set", sensor=sensor):
                address = CONFIG["SENSORS"][sensor]
                # todo: make second part of expression more robust --> current behavior is prone to failure
                self.assertTrue(address.isnumeric() or address[:2] == "0x")
                
    def test_relay_section(self):
        relay_section = CONFIG["RELAYS"]
        addresses = [entry for entry in relay_section.keys() if "address" in entry]
        relay_types = [entry for entry in relay_section.keys() if "type" in entry]

        for address in addresses:
            with self.subTest("check if relay addresses are set", address=address):
                self.assertTrue(relay_section[address].isnumeric())
                
        for relay_type in relay_types:
            with self.subTest("check if relay type is correctly specified", relay_type=relay_type):
                self.assertIn(relay_section[relay_type], ["True", "False"])

    def test_database_section(self):
        for entry in "database", "port", "host", "user", "password":
            with self.subTest("check if database section is specified"):
                self.assertFalse(CONFIG["DATABASE"][entry] == "")


if __name__ == '__main__':
    unittest.main()
