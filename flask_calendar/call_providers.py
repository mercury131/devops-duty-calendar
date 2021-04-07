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
    session.starttls() #enable security
    
    if 'smtp_login' in locals():
        session.login(smtp_login, smtp_password) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()