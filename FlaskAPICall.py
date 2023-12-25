from asyncio.log import logger
from cgitb import text
from http.client import HTTPResponse
from logging import Logger
import os
import time
import requests
import openai
import os
from flask import Flask, abort, request, jsonify
import flask
import hashlib
import hmac
import json
import pdb

ENV_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = ENV_PATH + r'/.env'

token = os.getenv('OPENAI_API_KEY')


app = Flask(__name__)

@app.route('/whatsappApi', methods=['GET'])
def smt():

	VERIFY_TOKEN = 'passKey' 
	# Endpoint to handle Facebook webhook verification
	challenge = request.args.get("hub.challenge")

	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
		return challenge
	else:
		print(challenge)
		return jsonify({'status': 'error', 'message': 'Invalid verify token'}), 403


def send_message(msg):
   headers = {
	   'Authorization': 'Bearer EAAKsmcqkbScBACTrsiEIubV2e6daJHEu3ol0Cle8gCGPhuHCIsZCBhc1NHMl6zNGlk9jTZB44xUoFL66tNrNRswXf7cyGIbd5nUH5ffIZCOcy0t6SWhHIvUxHnst6XTAbdRuLOsz7VZChoopM9UIyZCwvcZA1amuN8zKKYYgryb4cW0wobfow4vaQYWgfAYOjhFqiWh9lC4gZDZD',
   }
   json_data = {
				'messaging_product': 'whatsapp',
				"recipient_type": "individual",
				'to': '918828480007',
				"type": "text", 
				"text": { 
						"body": msg
					}
				}
   response = requests.post('https://graph.facebook.com/v16.0/118524904540889/messages', headers=headers, json=json_data)
   print(response.text)


@app.route('/whatsappApi', methods=['POST'])
def receive_message():
	print(request)

	data = request.get_json()
	print('Incoming WhatsApp request data:', data)
	logger.info(data)
	message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
	data = message
	Qn = "Write a reply to this message: "
	prompt = f"Q: {Qn+data}\nA:"
	# Make a request to the OpenAI API
	response = requests.post(
		'https://api.openai.com/v1/engines/text-davinci-002/completions',
		headers={
			'Content-Type': 'application/json',
			'Authorization': token
		},
		json={'prompt':prompt,'temperature':0.7,'max_tokens':100,'n':1,'stop':None})

	# Extract the response text from the OpenAI API response
	response_data = response.json()
	choices = response_data.get('choices')
	if choices and len(choices) > 0:
		response_text = choices[0].get('text', '').strip()
	else:
		response_text = "Sorry, I could not generate a response for your query."

	send_message(response_text)

	return 'OK', 200

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5003)