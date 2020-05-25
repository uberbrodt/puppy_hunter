import smtplib
import puppy_hunter.db
import puppy_hunter.log
import os
from email.message import EmailMessage
from datetime import datetime
from twilio.rest import Client

"""
Send out updated puppies since unix time
"""

logger = puppy_hunter.log.get_logger()


def send_updated_notifications(db_name):
    now = datetime.now()
    now_s = now.strftime("%b-%d %H:%M")
    puppies = puppy_hunter.db.get_unnotified_puppies(db_name)

    smtp_user = os.environ.get("PUPPYHUNTER_SMTP_USER")
    smtp_passwd = os.environ.get("PUPPYHUNTER_SMTP_PASSWD")
    # expected to be a string of email addresses seperated by ","
    sendto = os.environ.get("PUPPYHUNTER_SENDTO").split(",")

    msg_content = ""

    puppy_cnt = 0
    puppy_ids = []
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
        puppy_cnt += 1
        puppy_ids.append(pupper["id"])

    logger.info(f"found {puppy_cnt} to be sent in notifications")
    if msg_content != "":
        logger.info(f"Got PUPdates! Sending notifications to {sendto}")
        msg = EmailMessage()
        msg.set_content(msg_content)

        msg["Subject"] = f"Puppy Hunter PUPdate! - {now_s}"
        msg["From"] = "puppyhunter@uberbrodt.net"

        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login(smtp_user, smtp_passwd)
        smtp.send_message(msg, to_addrs=sendto)
        send_twilio_notification()

    puppy_hunter.db.mark_puppies_notified(db_name, puppy_ids)
    puppies.close()


def send_twilio_notification():
    account_sid = os.environ.get("PUPPYHUNTER_TWILIO_SID")
    auth_token = os.environ.get("PUPPYHUNTER_TWILIO_AUTH")
    smsto = os.environ.get("PUPPYHUNTER_SMSTO").split(",")
    smsfrom = os.environ.get("PUPPYHUNTER_SMSFROM")
    client = Client(account_sid, auth_token)

    for phone_num in smsto:
        client.messages.create(
            body="You have a PUPdate from PuppyHunter! Check your email",
            to=phone_num,
            from_=smsfrom,
        )

    logger.info(f"Sent SMS messages to {smsto}")
