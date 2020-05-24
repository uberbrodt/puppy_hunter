import smtplib
import puppy_hunter.db
import os
from email.message import EmailMessage
from datetime import datetime

"""
Send out updated puppies since unix time
"""


def updated_puppies_since(time, db_name):
    now = datetime.now()
    now_s = now.strftime("%b-%d %H:%M")
    puppies = puppy_hunter.db.get_updated_since(db_name, time)

    smtp_user = os.environ.get("PUPPYHUNTER_SMTP_USER")
    smtp_passwd = os.environ.get("PUPPYHUNTER_SMTP_PASSWD")
    # expected to be a string of email addresses seperated by ","
    sendto = os.environ.get("PUPPYHUNTER_SENDTO").split(",")

    msg_content = ""

    for pupper in puppies:

        msg_content += f"""
        -------------------------------------------
        id: {pupper['id']}
        name: {pupper['name']}
        detail_link: {pupper['detail_link']}
        sex: {pupper['sex']}
        breed: {pupper['breed']}
        size: {pupper['size']}
        stage: {pupper['stage']}
        updated_at: {pupper['updated_at']}
        -------------------------------------------
        """
    if msg_content != "":
        print("Got PUPdates! Sending notifications")
        msg = EmailMessage()
        msg.set_content(msg_content)

        msg["Subject"] = f"Puppy Hunter PUPdate! - {now_s}"
        msg["From"] = "puppyhunter@uberbrodt.net"

        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(smtp_user, smtp_passwd)
        smtp.send_message(msg, to_addrs=sendto)


