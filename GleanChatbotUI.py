import sys
import requests
import json
import markdown
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextBrowser, QPushButton, QComboBox

#AUTH_ENDPOINT = 'https://support-lab-be.glean.com/rest/api/v1/authenticate'
API_KEY = 'ong6bNNqAF/re+uU2YJ5Pymdui3n2VdgiDJoM+X5xo0='
CHATBOT_ENDPOINT = 'https://support-lab-be.glean.com/rest/api/v1/chat'

def authenticate():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    response = requests.post(CHATBOT_ENDPOINT, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('token')
    else:
        response.raise_for_status()

def send_chatbot_request(message):
    # token = authenticate()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    payload = {
        'stream': False, # Set to False to toggle off streaming mode
        'messages': [{
            'author': 'USER',
            'fragments': [{'text': message}]
        }],
    }
    
    print("Headers:", headers)
    print("Payload:", json.dumps(payload, indent=2))
    
    response = requests.post(CHATBOT_ENDPOINT, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.content)
        response.raise_for_status()

def process_message_fragment(message):
    message_type = message['messageType']
    fragments = message.get('fragments', [])
    citations = message.get('citations', [])

    result = ""
    if message_type == 'CONTENT':
        if fragments:
            for fragment in fragments:
                text = fragment.get('text', '')
                result += text
        if citations:
            result += '\nSources:\n'
            for idx, citation in enumerate(citations):
                sourceDocument = citation.get('sourceDocument', {})
                if sourceDocument:
                    source = citation['sourceDocument']
                    result += f'Source {idx + 1}: Document title - {source["title"]}, url: <a href="{source["url"]}">{source["url"]}</a>\n'
                sourcePerson = citation.get('sourcePerson', {})
                if sourcePerson:
                    source = citation['sourcePerson']
                    result += f'Source {idx + 1}: Person name - {source["name"]}\n'
    return result

class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Glean Chat API Helper')
        
        layout = QVBoxLayout()
        
        self.message_label = QLabel('How can I help you?')
        layout.addWidget(self.message_label)
        
        self.message_input = QLineEdit()
        layout.addWidget(self.message_input)
        
        self.send_button = QPushButton('Ask Glean')
        self.send_button.clicked.connect(self.on_send)
        layout.addWidget(self.send_button)
        
        self.response_text = QTextBrowser()
        self.response_text.setOpenExternalLinks(True)  # Enable clickable links
        layout.addWidget(self.response_text)
        
        self.history_label = QLabel('What questions have I asked?')
        layout.addWidget(self.history_label)
        
        self.message_history = QComboBox()
        self.message_history.currentIndexChanged.connect(self.on_history_selected)
        layout.addWidget(self.message_history)
        
        self.setLayout(layout)
    
    def on_send(self):
        user_message = self.message_input.text().strip()
        if user_message:
            try:
                response = send_chatbot_request(user_message)
                messages = response.get('messages', [])
                result = ""
                for message in messages:
                    result += process_message_fragment(message)
                self.response_text.append(f"<b>You:</b> {user_message}<br>")
                self.response_text.append(f"<h3>Glean Assistant</h3> {markdown.markdown(result)}<br><hr>")  # Convert Markdown to HTML
                self.message_input.clear()
                self.message_history.addItem(user_message)  # Add message to history
            except Exception as e:
                self.response_text.append(f"<b>Error:</b> {str(e)}<br><hr>")
    
    def on_history_selected(self, index):
        if index >= 0:
            selected_message = self.message_history.itemText(index)
            self.message_input.setText(selected_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ChatbotGUI()
    gui.show()
    sys.exit(app.exec_())