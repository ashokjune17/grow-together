import csv
import smtplib, ssl
from datetime import date


# build report (simple text here, can be fancy HTML)
report = "Daily Stock Report\n\n"

# send email
sender = "your-email@example.com"
receiver = "you@example.com"
password = "EMAIL_PASS"  # from secrets

smtp_server = "smtp.gmail.com"
port = 465

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender, password)
    server.sendmail(sender, receiver, report)
