import os
import smtplib
import pandas as pd
from datetime import datetime
from pathlib import Path
from email.message import EmailMessage
from src.utilities import CONFIG, get_abs_path
from textwrap import dedent


BODY = dedent("""\
<html>
    <body>
        <p>
            <span style="color: rgb(0,0,0);">
                <h1>Status Report for {site}</h1>
            </span>
        </p>
        <p>
            {analysis}
        </p>
        <p>
            <h2>Current Sensor Readings</h2>
            {table}
        </p>
    </body>
</html>
""")


class NotificationHandler:

    def __init__(self):
        self.server_name = CONFIG.get("EMAIL", "smtp_server")
        self.server_port = CONFIG.getint("EMAIL", "smtp_server_port")
        self.server = smtplib.SMTP(self.server_name,
                                   self.server_port,
                                   timeout=10)
        self.from_addr = CONFIG.get("EMAIL", "email_from_address")
        self.to_addr = CONFIG.get("EMAIL", "email_to_address")
        self.env_data_path = get_abs_path("data", CONFIG.get("GENERAL", "env_data_file_name"))
        self.env_monitor_path = get_abs_path("figures", CONFIG.get("GENERAL", "monitor_file_name"))
        self.env_photo_path = get_abs_path("figures", CONFIG.get("GENERAL", "photo_file_name"))
        self.msg = EmailMessage()
        self.body = BODY
        self.analysis = ""
        self.tests_failed = 0

    def __del__(self):
        try:
            self.server.quit()
        except smtplib.SMTPException:
            pass

    def construct_headers(self, subject):
        self.msg["To"] = self.to_addr
        self.msg["From"] = self.from_addr
        self.msg["Subject"] = subject

    def construct_body(self):
        latest_data = self.__get_latest_readings()
        self.analysis += self.__get_analysis(latest_data)
        self.body = BODY.format(site=CONFIG.get("GENERAL", "site"),
                                analysis=self.analysis,
                                table=latest_data.to_html())

        # todo: add more checks and a rudimentary analysis of `latest_data
        self.msg.set_content(self.body, "html")

    def __get_analysis(self, data):
        out = "<p><h2>Freshness Tests</h2>"
        out += self.__check_freshness_access_date(self.env_monitor_path)
        out += self.__check_freshness_access_date(self.env_photo_path)
        out += self.__check_freshness_data(data)
        out += "</p>\n<p><h2>Sensor Tests</h2>"
        out += self.__check_sensors(data)
        out += "</p>\n<p><h2>Summary</h2>"
        out += self.__get_analysis_summary()
        out += "</p>"

        return out

    def __check_sensors(self, data):
        out = ""
        expected = {"BMP280": 3, "SCD30": 3, "DHT22": 2, "BH1750": 1}
        counts = data.reset_index().sensor.value_counts()

        for sensor, expectation in expected.items():
            if counts.get(sensor) != expected.get(sensor):
                self.tests_failed += 1
                out += f"<p>test {sensor} ... failed.</p>\n"
            else:
                out += f"<p>test {sensor} ... passed.</p>\n"
        return out

    def __get_analysis_summary(self):
        if not self.tests_failed:
            return f"<p>all systems nominal.</p>"
        elif self.tests_failed == 1:
            return f"<p>problems detected: 1 test failed.</p>"
        elif self.tests_failed > 1:
            return f"<p>problems detected: {self.tests_failed} tests failed.</p>"

    def __check_freshness_access_date(self, path):
        name = Path(path).name
        created = os.path.getctime(path)
        now = datetime.now().timestamp()
        # check if file is older than one day
        passed = (now - created) <= 24 * 60 * 60
        res = "passed" if passed else "failed"
        if not passed:
            self.tests_failed += 1
        return f"<p> freshness test for {name} ... {res}.</p>\n"

    def attach(self, attachment, maintype, subtype):
        filename = "-".join([Path(attachment).name.replace(f".{subtype}", ""),
                             datetime.now().strftime("%Y-%m-%d")]) + f".{subtype}"

        with open(attachment, 'rb') as fp:
            file = fp.read()
            self.msg.add_attachment(file, maintype, subtype, filename=filename)

    def __get_latest_readings(self):
        data = (pd.read_csv(self.env_data_path, parse_dates=["taken_at"])
                .groupby(["sensor", "variable", "unit"])
                .agg({"value": "last", "taken_at": "last"})
                .assign(taken_at=lambda x: x.taken_at.round("s"),
                        value=lambda x: x.value.round(2)))
        return data

    def login(self, password):
        self.server.connect(self.server_name, self.server_port)
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.from_addr, password)

    def send(self):
        try:
            self.server.sendmail(from_addr=self.from_addr,
                                 to_addrs=self.to_addr,
                                 msg=self.msg.as_string())
        except Exception as e:
            raise e
        finally:
            self.server.quit()

    def construct_attachments(self):
        self.attach(self.env_monitor_path, "image", "png")
        self.attach(self.env_photo_path, "image", "jpg")

    def __check_freshness_data(self, data):
        passed = pd.Timestamp.now() - data.taken_at.max() <= pd.Timedelta(days=1)
        name = Path(self.env_data_path).name
        res = "passed" if passed else "failed"
        if not passed:
            self.tests_failed += 1
        return f"<p> freshness test for {name} ... {res}.</p>\n"


def send_email():
    notification = NotificationHandler()
    notification.construct_headers("Status Report")
    notification.construct_body()
    notification.construct_attachments()
    notification.login(CONFIG.get("EMAIL", "email_password"))
    notification.send()


if __name__ == "__main__":
    send_email()

