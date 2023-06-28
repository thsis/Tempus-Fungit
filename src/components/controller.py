import logging
import time
from logdecorator import log_on_start, log_on_end, log_exception
from src.components import Relay
from src.utilities import CONFIG, EXIT_EVENT

logger = logging.getLogger(__name__)



class Controller:
    def __init__(self):
        self.rules = {}
        self.relays = {}
        self.relay_configs = {}

    def add(self, section):
        var, options, relays = self._parse_section(section)
        self.rules[var] = options
        for relay in relays:
            if relay not in self.relays:
                self.relays[relay] = Relay(relay, options["active_low"])

    def _parse_section(self, section):
        options = dict(CONFIG[section])
        var = options.pop("var")
        relays = [int(i) for i in options.pop("relays").split(",")]
        options["relays"] = relays
        options["active_low"] = options["active_low"] == "True"
        for key in "upper", "lower":
            options[key] = float(options[key])
        self._sanity_check_options()
        return var, options, relays

    def _sanity_check_options(self):
        for var, options in self.rules.items():
            for relay in options["relays"]:
                if relay not in self.relay_configs.keys():
                    self.relay_configs[relay] = options["active_low"]
                else:
                    assert self.relay_configs[relay] == options["active_low"], f"Relay {relay} is misconfigured."

    def _get_initial_decisions(self, state):
        arm_relays = {key: False for key in self.relays.keys()}
        for var, rule in self.rules.items():
            current_state = state[var]
            if rule["check"] == "between" and (rule["lower"] <= current_state <= rule["upper"]):
                for relay in rule["relays"]:
                    arm_relays[relay] = True
            if rule["check"] == "lower" and current_state < rule["lower"]:
                for relay in rule["relays"]:
                    arm_relays[relay] = True
            if rule["check"] == "upper" and current_state > rule["upper"]:
                for relay in rule["relays"]:
                    arm_relays[relay] = True
        return arm_relays

    def control(self, state):
        decisions = self._get_initial_decisions(state)
        for pin, relay in self.relays.items():
            if decisions[pin]:
                relay.arm()
            else:
                relay.disarm()


if __name__ == "__main__":
    import signal
    from src.components import SensorArray, setup_sensors
    from src.utilities import CONFIG, get_abs_path, interrupt_handler, get_logger


    def main():
        sensors = setup_sensors(CONFIG)
        sensor_array = SensorArray(sensors, retries=3, delay=2)
        controller = Controller()
        controller.add("CONTROLLER_CO2")
        controller.add("CONTROLLER_HUMIDITY")
        controller.add("CONTROLLER_LIGHTS")

        while True:
            state = sensor_array.get_state()
            controller.control(state)
            time.sleep(50)

    rootLogger = get_logger(logging.DEBUG, get_abs_path("logs", "controller_demo.log"))

    rootLogger.debug("Debug logging test...")
    signal.signal(signal.SIGINT, interrupt_handler)
    main()
