from flask import Flask, request, render_template, redirect, Response, json, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from dotenv import load_dotenv
from utils import save_to_json, get_user_id

import os
import logging

load_dotenv()

app = Flask(__name__)

# Replace 'YOUR_SLACK_CLIENT_ID' and 'YOUR_SLACK_CLIENT_SECRET' with your Slack app's credentials
slack_client_id = os.environ['SLACK_CLIENT_ID']
slack_client_secret = os.environ['SLACK_CLIENT_SECRET']

redirect_uri = 'https://localhost:5000/finish_auth'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/oauth_authorization')
def oauth_authorization():
    # Redirect to Slack authorization URL
    return redirect(f'https://slack.com/oauth/v2/authorize?client_id={slack_client_id}&redirect_uri={redirect_uri}&scope=app_mentions:read,channels:read,groups:read,im:read,mpim:read,team:read,users:read')

@app.route('/finish_auth', methods=["GET", "POST"])
def finish_auth():
    
    resp_body = {'errors': False, 'success': True, 'message': ''}
    
    auth_code = request.args.get('code')
    
    client = WebClient() 
    
    try:
        # Exchange authorization code for access token
        auth_response = client.oauth_v2_access(
            client_id=slack_client_id,
            client_secret=slack_client_secret,
            code=auth_code,
            redirect_uri=redirect_uri
        )

    except SlackApiError as e:
        resp_body['errors'] = True
        resp_body['success'] = False
        resp_body['message'] = f"Error: {e.response['error']}"
        return Response(json.dumps(resp_body), status=503, mimetype="application/json")

    # Store our token into environment variable
    os.environ['SLACK_ACCESS_TOKEN'] = auth_response['access_token'] 
    
    resp_body['message'] = 'Auth completed!'
    return Response(json.dumps(resp_body), status=200, mimetype="application/json")

@app.route('/get_users_data', methods=["GET"])
def get_users_data():
    resp_body = {
        'errors': False,
        'success': True,
        'message': ''
    }
    
    try:
        client = WebClient(token=os.environ['SLACK_ACCESS_TOKEN']) 
        us_list = client.users_list()
        
        members = us_list.get('members')
        
        resp_body['users_amount'] = len(members)
        resp_body['members'] = members
        
        save_to_json(resp_body, 'users_data.json')
        
        return Response(json.dumps(resp_body), status=200, mimetype="application/json")
    except SlackApiError as e:
        resp_body['errors'] = True
        resp_body['success'] = False
        resp_body['message'] = f"Error: {e.response['error']}"
        return Response(json.dumps(resp_body), status=503, mimetype="application/json")
           

@app.route('/send_message', methods=['POST'])
def send_message():
    # Get data from the incoming POST request
    data = request.get_json()
    logging.info(data)

    # Extract relevant data (channel and text) from the request
    channel = data.get('user')
    text = data.get('text')

    resp_body = {
        'errors': False,
        'success': True,
        'message': ''
    }

    try:
        client = WebClient(token=os.environ['SLACK_ACCESS_TOKEN']) 

        # Make the POST request to the Slack API
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        resp_body['errors'] = True
        resp_body['success'] = False
        resp_body['message'] = f"Error: {e.response['error']}"
        return Response(json.dumps(resp_body), status=503, mimetype="application/json")


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc') 
