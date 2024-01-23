# workspace_buddy

This is a basic implementation of the API integration. For this task SlackAPI was used.

Current implementation provides: OAuth authentication and two API methods: 

> /get_users_data

Which return information of all users of the workspace and saves this data into JSON file for later operations.

> /send_message

Uses information from previously retrieved data to send message to a specific user


To test this project we need to set the necessary keys for our app in the .env file and start <b>main.py</b>.
