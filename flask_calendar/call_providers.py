import telebot
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events
import os
from slack import WebClient
from slack.errors import SlackApiError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
  
def send_to_telegram(phone,message,api_id,api_hash,token):
    # get your api_id, api_hash, token
    # from telegram as described above
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # creating a telegram session and assigning
    # it to a variable client
    client = TelegramClient('session', api_id, api_hash, loop=loop)
    
    # connecting and building the session
    client.connect()
    try:
        # receiver user_id and access_hash, use
        # my user_id and access_hash for reference
        #receiver = InputPeerUser('user_id', 'user_hash')
        #receiver = InputPeerUser('user_id', 'user_hash')
    
        # sending message using telegram client
        #client.send_message(receiver, message, parse_mode='html')
        client.send_message(phone, message, parse_mode='html')
    except Exception as e:
        
        # there may be many error coming in while like peer
        # error, wwrong access_hash, flood_error, etc
        print(e);
    
    # disconnecting the telegram session 
    client.disconnect()

def auth_telegram(phone,message,api_id,api_hash,token):
    # get your api_id, api_hash, token
    # from telegram as described above

    # creating a telegram session and assigning
    # it to a variable client
    client = TelegramClient('session', api_id, api_hash)
    
    # connecting and building the session
    client.connect()
    
    # in case of script ran first time it will
    # ask either to input token or otp sent to
    # number or sent or your telegram id 
    if not client.is_user_authorized():
    
        client.send_code_request(phone)
        
        # signing in the client
        client.sign_in(phone, input('Enter the code: '))
    
    
    try:
        # receiver user_id and access_hash, use
        # my user_id and access_hash for reference
        #receiver = InputPeerUser('user_id', 'user_hash')
        #receiver = InputPeerUser('user_id', 'user_hash')
    
        # sending message using telegram client
        #client.send_message(receiver, message, parse_mode='html')
        client.send_message(phone, message, parse_mode='html')
    except Exception as e:
        
        # there may be many error coming in while like peer
        # error, wwrong access_hash, flood_error, etc
        print(e);
    
    # disconnecting the telegram session 
    client.disconnect()


def send_to_slack(duty,message,slackchannel,apitoken):

    client = WebClient(token=apitoken)

    user = ("<@" + duty + '>')
    allmessage = (user + ' ' +  message)

    try:
        response = client.chat_postMessage(
            channel=('#' + slackchannel),
            text=allmessage)
        response["message"]["text"] == allmessage
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

def send_email(subject,text,receiver_address,smtp_server,smtp_port,sender_address, *args, **kwargs):

    try:

        smtp_login = kwargs.get('smtp_login', None)
        smtp_password = kwargs.get('smtp_password', None)
        mail_content = text 
        #The mail addresses and password
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] =  subject  #The subject line
        message['X-Priority'] = '1'
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP(smtp_server, smtp_port) #use gmail with port
        if int(smtp_port) == 587 or int(smtp_port) == 2525:
            session.starttls() #enable security
        
        if 'smtp_login' in locals() and smtp_login is not None :
            session.login(smtp_login, smtp_password) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
    except Exception as e:
        print(e)

def send_rest1(duty1,duty2,project,email1,email2,url,method,auth,user,password,arg1,arg2,arg3,arg4):

    url=url.replace('<DUTY1>',duty1).replace('<DUTY2>',duty2).replace('<PROJECT>',project).replace('<EMAIL1>',email1).replace('<EMAIL2>',email2).replace('<ARG1>',arg1).replace('<ARG2>',arg2).replace('<ARG3>',arg3).replace('<ARG4>',arg4)
    
    if auth == 'yes':
        if method == 'POST':
            resp = requests.post(url, data={}, auth=(user, password))
        else:
            resp = requests.get(url, data={}, auth=(user, password))
    else:
        if method == 'POST':
            resp = requests.post(url, data={})
        else:
            resp = requests.get(url, data={})
    
    if resp.ok:
        return resp
    else:
        raise MyError('REST Request is not 200!')
        


