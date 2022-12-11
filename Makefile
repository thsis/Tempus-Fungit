install:
	scripts/install.sh

clean:
	scripts/clean.sh

co2_control:
	python scripts/control_environment.py co2 950 26 --unit minutes --delay 300 --active-min 5 --active-max 15 --log-file co2_controller.log --log-level info --track-csv co2_controller.csv

humidity_control:
	python scripts/control_environment.py humidity 92 6 22 --increases --margin 0.05 --unit minutes --delay 300 --active-min 1 --active-max 5 --log-file humidity_control.log --log-level info --track-csv humidity_control.csv