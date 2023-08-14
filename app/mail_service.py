import requests
import os
from fastapi import HTTPException


def get_email_list(cur):
    email_list = []
    cur.execute("SELECT * FROM Email;")
    result = cur.fetchall()
    for email in result:
        email_list.append(email[1])
    return email_list


def send_email(product_name, cur):
    email_list = get_email_list(cur)
    if not email_list:
        return HTTPException(
            status_code=500, detail='Attempt to send email is failed. Please provide your email.')
    else:
        send_low_stock_email(product_name, email_list)


def send_low_stock_email(product_name, list_of_emails):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxd8bd24e6b50f4d96b0963bc097418800.mailgun.org/messages",
        auth=("api", os.environ["MAILGUN_API_KEY"]),
        data={"from": "Stock control APP <mailgun@sandboxd8bd24e6b50f4d96b0963bc097418800.mailgun.org>",
              "to": list_of_emails,
              "subject": "Stock status",
              "text": f"Stock for {product_name} is low. Time for refill."})
