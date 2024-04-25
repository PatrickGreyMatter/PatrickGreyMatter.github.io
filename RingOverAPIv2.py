import requests
import json
import time

API_KEY = "b08cf718eebe03c9b705e14a66747436f3e22295" 
BASE_URL = "https://public-api.ringover.com/v2"


def filter_conversation_data(conversation):
    filtered_conversation = {
        'conversation_id': conversation.get('conversation_id'),
        'contacts': []
    }

    for target in conversation.get('external', []):
        if 'contact' in target and target['contact']:
            filtered_conversation['contacts'].append({
                'id': target['contact'].get('id'),
                'firstname': target['contact'].get('firstname'),
                'lastname': target['contact'].get('lastname'),
                'company': target['contact'].get('company'),
                'concat_name': target['contact'].get('concat_name')
            })

    return filtered_conversation


def filter_contact_data(contact):
    filtered_contact = {
        'contact_id': contact.get('contact_id'),
        'firstname': contact.get('firstname'),
        'lastname': contact.get('lastname'),
        'company': contact.get('company'),
        'creation_date': contact.get('creation_date'),
        'emails': contact.get('emails'),
        'numbers': []
    }

    for number in contact.get('numbers', []):
        filtered_number = {
            'number': number.get('number'),
            'type': number.get('type'),
            'format': {
                'country': number.get('format', {}).get('country'),
                'national': number.get('format', {}).get('national'),
                'international': number.get('format', {}).get('international')
            }
        }
        filtered_contact['numbers'].append(filtered_number)

    return filtered_contact


def save_content_to_json(content, filename):
    try:
        with open(filename, 'r+', encoding='utf-8') as json_file:
            # Load existing data
            file_data = json.load(json_file)
            # Append new content
            file_data.extend(content)
            # Move the pointer to the beginning of the file and overwrite
            json_file.seek(0)
            json.dump(file_data, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        # If file does not exist, create it and write the content
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(content, json_file, ensure_ascii=False, indent=4)


def make_ringover_get_request(endpoint, params=None):
    url = f'{BASE_URL}/{endpoint}'
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json',
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()  # Return the whole JSON response
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")
        return None


def get_all_contacts():
    limit_count = 500
    limit_offset = 0
    all_contacts = []
    while True:
        response = make_ringover_get_request('contacts', params={'limit_count': limit_count, 'limit_offset': limit_offset})
        if response is None or 'contact_list' not in response:
            break

        contacts = [filter_contact_data(contact) for contact in response.get('contact_list', [])]
        save_content_to_json(contacts, 'contacts.json')
        all_contacts.extend(contacts)

        if len(contacts) < limit_count:
            break
        limit_offset += limit_count
        print(f"Fetched {len(all_contacts)} contacts")

    return all_contacts


def get_all_conversations():
    limit_count = 500
    limit_offset = 0
    all_conversations = []

    while True:
        response = make_ringover_get_request('conversations', params={'limit_count': limit_count, 'limit_offset': limit_offset})
        if response is None or 'conversation_list' not in response:
            break

        conversations = [filter_conversation_data(conversation) for conversation in response.get('conversation_list', [])]
        save_content_to_json(conversations, 'conversations.json')
        all_conversations.extend(conversations)

        if len(conversations) < limit_count:
            break
        limit_offset += limit_count
        print(f"Fetched {len(all_conversations)} conversations")
    return all_conversations


def get_and_extract_message_info(contacts, conversations):
    for conversation in conversations:
        conversation_id = conversation['conversation_id']

        # Fetch messages for this conversation
        messages_response = make_ringover_get_request(f'conversations/{conversation_id}/messages')

        if messages_response and messages_response.get('message_list') is not None:
            # Extract relevant information from each message
            simplified_messages = []
            for message in messages_response['message_list']:
                # Determine the key name based on the user_id
                key_name = 'Eric Molina' if (message.get('user') and message['user'].get('user_id') == 72138) else 'buffer'

                simplified_message = {
                    key_name: message['buffer'],
                    'creation_date': message['creation_date']
                }
                simplified_messages.append(simplified_message)

            # Append the simplified messages to the corresponding contacts
            for contact_info in conversation['contacts']:
                contact_id = contact_info['id']
                for contact in contacts:
                    if contact['contact_id'] == contact_id:
                        if 'messages' not in contact:
                            contact['messages'] = []
                        contact['messages'].extend(simplified_messages)

        print(f"Fetching conv: {conversation_id} conversations")
        time.sleep(1)  # Respect API rate limits

    # Save the updated contacts with messages to 'contacts.json'
    save_content_to_json(contacts, 'contacts_messages_Cyril_CIEM.json')

# Assuming all_contacts and all_conversations are already fetched
all_contacts = get_all_contacts()
all_conversations = get_all_conversations()

# Extract and organize message information with rate limiting
get_and_extract_message_info(all_contacts, all_conversations)

