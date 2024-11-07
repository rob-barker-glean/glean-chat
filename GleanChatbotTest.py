import json
import sys
import requests


def process_message_fragment(message):
    """Function printing python version."""
    message_type = message['messageType']
    fragments = message.get('fragments', [])
    citations = message.get('citations', [])

    if message_type == 'CONTENT':
        if fragments:
            for fragment in fragments:
                text = fragment.get('text', '')
                print(text, end='', flush=True)
        if citations:
            print('\nSources:')
            for idx, citation in enumerate(citations):
                sourcedocument = citation.get('sourceDocument', {})
                if sourcedocument:
                  source = citation['sourceDocument']
                  print(f'Source {idx + 1}: Document title - {source["title"]}, url: {source["url"]}')
                sourceperson = citation.get('sourcePerson', {})
                if sourceperson:
                  source = citation['sourcePerson']
                  print(f'Source {idx + 1}: Person name - {source["name"]}')

def process_response_message_stream(response):
    for line in response.iter_lines():
        if line:
            line_json = json.loads(line)
            messages = line_json.get('messages', [])
            for message in messages:
                process_message_fragment(message)

#
# #AUTH_ENDPOINT = 'https://support-lab-be.glean.com/rest/api/v1/authenticate'
#API_KEY = 'ong6bNNqAF/re+uU2YJ5Pymdui3n2VdgiDJoM+X5xo0='
#CHATBOT_ENDPOINT = 'https://support-lab-be.glean.com/rest/api/v1/chat'
#

def main():
    url = 'https://support-lab-be.glean.com/rest/api/v1/chat'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ong6bNNqAF/re+uU2YJ5Pymdui3n2VdgiDJoM+X5xo0='
    }
    data = {
        "stream": False,
        "messages": [
            {
            "author": "USER",
            "fragments": [
                {
                "text": "What are the company holidays?"
                }
            ]
            }
        ]
    }

    try:
        with requests.post(url, headers=headers, json=data, stream=True, timeout=10) as response:
            if response.status_code == 200:
                process_response_message_stream(response)
            else:
                print(f'Status code: {response.status_code}, error: {response.text}')
                sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f'Request Exception: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()