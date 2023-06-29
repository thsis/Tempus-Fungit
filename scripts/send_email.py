import smtplib
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid
from src.utilities import CONFIG, get_abs_path
#%%
server = smtplib.SMTP('smtp.ionos.de', 25, timeout=10)

attachment = get_abs_path("figures", CONFIG.get("GENERAL", "monitor_file_name"))
to_addr = CONFIG.get("EMAIL", "email_to_address")
from_addr = CONFIG.get("EMAIL", "email_from_address")

msg = EmailMessage()
msg["To"] = to_addr
msg["From"] = from_addr
msg["Subject"] = "this is a test"

body = """\
                    <html>
                        <body>
                            <p><span style="color: rgb(0,0,0);">Dear Thomas,</span></p>
                            <p>
                                blablablabla
                            </p>
                            <p>Kind Regards,<br />
                            The Other Thomas
                            </p>
                        </body>
                    </html>
                    """

attachment_cid = make_msgid()
msg.set_content(
    '<b>%s</b><br/><img src="cid:%s"/><br/>' % (
        body, attachment_cid[1:-1]), 'html')

with open(attachment, 'rb') as fp:
    fp.file_name = "-".join([CONFIG.get("GENERAL", "monitor_file_name").replace(".png", ""),
                             datetime.now().strftime("%Y-%m-%d")]) + ".png"
    msg.add_related(
        fp.read(), 'image', 'png', cid=attachment_cid)

try:
    server.connect('smtp.ionos.de', 25)
    server.starttls()
    server.ehlo()
    server.login("kontakt@tempus-fungit.de", "fqb9JsGz$&WE")
    server.sendmail(from_addr=from_addr, to_addrs=to_addr, msg=msg.as_string())
except Exception as e:
    raise e
finally:
    server.quit()

