import unittest
from src.utilities import CONFIG


class TestConfig(unittest.TestCase):
    def test_sections(self):
        for section in ["GENERAL", "SENSORS", "DATABASE"]:
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
                
    def test_controller_section(self):
        controller_sections = [k for k in CONFIG.keys() if "CONTROLLER_" in k]
        req_parameters = ["var", "relays", "active_low", "delay", "active_min", "active_max", "unit"]

        for section in controller_sections:
            for param in req_parameters:
                with self.subTest("check if all parameters are specified", section=section, param=param):
                    self.assertIn(param, CONFIG[section])

    def test_database_section(self):
        for entry in "database", "port", "host", "user", "password":
            with self.subTest("check if database section is specified"):
                self.assertFalse(CONFIG["DATABASE"][entry] == "")


if __name__ == '__main__':
    unittest.main()
