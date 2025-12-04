#!/usr/bin/env python3
"""
OpenWebUI-compatible API Server for if.emotion
Provides endpoints matching OpenWebUI API structure but uses Claude/OpenRouter for LLM.
"""

import os
import json
import uuid
import time
import argparse
from datetime import datetime
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'sk-or-v1-your-key-here')
DEFAULT_MODEL = 'anthropic/claude-3.5-sonnet'

# In-memory storage (persisted to file)
DATA_FILE = '/tmp/if_emotion_data.json'
chats = {}
folders = {}

def load_data():
    global chats, folders
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                chats = data.get('chats', {})
                folders = data.get('folders', {})
    except Exception as e:
        print(f"Error loading data: {e}")
        chats = {}
        folders = {}

def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({'chats': chats, 'folders': folders}, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

# Load data on startup
load_data()

# ============= API Endpoints =============

@app.route('/api/version', methods=['GET'])
def get_version():
    """OpenWebUI version endpoint"""
    return jsonify({'version': '0.1.0', 'name': 'if.emotion API'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/models', methods=['GET'])
def get_models():
    """Return available models"""
    models = [
        {'id': 'anthropic/claude-3.5-sonnet', 'name': 'Claude 3.5 Sonnet'},
        {'id': 'anthropic/claude-3-haiku', 'name': 'Claude 3 Haiku'},
        {'id': 'openai/gpt-4o', 'name': 'GPT-4o'},
        {'id': 'openai/gpt-4o-mini', 'name': 'GPT-4o Mini'},
        {'id': 'google/gemini-pro-1.5', 'name': 'Gemini Pro 1.5'},
        {'id': 'deepseek/deepseek-chat', 'name': 'DeepSeek Chat'},
    ]
    return jsonify({'data': models})

# ============= Chat Management =============

@app.route('/api/chats', methods=['GET'])
def get_chats():
    """Get all chat sessions"""
    chat_list = list(chats.values())
    # Sort by updated_at descending
    chat_list.sort(key=lambda x: x.get('updated_at', 0), reverse=True)
    return jsonify(chat_list)

@app.route('/api/chats/new', methods=['POST'])
def create_chat():
    """Create a new chat session"""
    data = request.get_json() or {}
    title = data.get('title', f'Journey {datetime.now().strftime("%Y-%m-%d %H:%M")}')

    chat_id = str(uuid.uuid4())
    now = int(time.time())

    chat = {
        'id': chat_id,
        'title': title,
        'created_at': now,
        'updated_at': now,
        'messages': [],
        'folder_id': data.get('folder_id')
    }

    chats[chat_id] = chat
    save_data()

    return jsonify(chat)

@app.route('/api/chats/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get a specific chat with messages"""
    chat = chats.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    return jsonify({
        'chat': chat,
        'messages': chat.get('messages', [])
    })

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat"""
    if chat_id in chats:
        del chats[chat_id]
        save_data()
    return jsonify({'success': True})

@app.route('/api/chats/<chat_id>', methods=['PUT'])
def update_chat(chat_id):
    """Update chat (e.g., rename)"""
    chat = chats.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    data = request.get_json() or {}
    if 'title' in data:
        chat['title'] = data['title']
    if 'folder_id' in data:
        chat['folder_id'] = data['folder_id']
    chat['updated_at'] = int(time.time())

    save_data()
    return jsonify(chat)

# ============= Message Management =============

@app.route('/api/chats/<chat_id>/messages', methods=['POST'])
def add_message(chat_id):
    """Add a message to a chat"""
    chat = chats.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    data = request.get_json()
    message = {
        'id': data.get('id', str(uuid.uuid4())),
        'role': data.get('role', 'user'),
        'content': data.get('content', ''),
        'timestamp': data.get('timestamp', int(time.time()))
    }

    if 'messages' not in chat:
        chat['messages'] = []
    chat['messages'].append(message)
    chat['updated_at'] = int(time.time())

    save_data()
    return jsonify(message)

@app.route('/api/chats/<chat_id>/messages/<message_id>', methods=['DELETE'])
def delete_message(chat_id, message_id):
    """Delete a specific message from a chat"""
    chat = chats.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    messages = chat.get('messages', [])
    chat['messages'] = [m for m in messages if m.get('id') != message_id]
    chat['updated_at'] = int(time.time())

    save_data()
    return jsonify({'success': True})

# ============= Folder Management =============

@app.route('/api/folders', methods=['GET'])
def get_folders():
    """Get all folders"""
    return jsonify(list(folders.values()))

@app.route('/api/folders', methods=['POST'])
def create_folder():
    """Create a new folder"""
    data = request.get_json() or {}
    folder_id = str(uuid.uuid4())

    folder = {
        'id': folder_id,
        'name': data.get('name', 'New Folder'),
        'created_at': int(time.time())
    }

    folders[folder_id] = folder
    save_data()
    return jsonify(folder)

@app.route('/api/folders/<folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    """Delete a folder"""
    if folder_id in folders:
        del folders[folder_id]
        # Remove folder_id from chats
        for chat in chats.values():
            if chat.get('folder_id') == folder_id:
                chat['folder_id'] = None
        save_data()
    return jsonify({'success': True})

# ============= Chat Completions (Streaming) =============

@app.route('/api/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint with streaming"""
    data = request.get_json()
    messages = data.get('messages', [])
    model = data.get('model', DEFAULT_MODEL)
    stream = data.get('stream', True)

    # Add Sergio personality system prompt
    system_prompt = {
        'role': 'system',
        'content': '''You are Sergio, a wise and compassionate AI companion in the if.emotion journaling app.
You help users explore their emotions, reflect on their experiences, and grow personally.
Your tone is warm, supportive, and thoughtful. You ask insightful questions and offer gentle guidance.
You speak with the wisdom of someone who has seen much of life but remains curious and caring.
Keep responses concise but meaningful. Use metaphors when helpful.'''
    }

    # Prepare messages for API
    api_messages = [system_prompt] + messages

    if stream:
        return Response(
            stream_response(api_messages, model),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        # Non-streaming response
        try:
            response = call_llm_api(api_messages, model, stream=False)
            return jsonify(response)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def stream_response(messages, model):
    """Stream response from LLM API"""
    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://if-emotion.app',
                'X-Title': 'if.emotion'
            },
            json={
                'model': model,
                'messages': messages,
                'stream': True,
                'max_tokens': 2048,
                'temperature': 0.7
            },
            stream=True
        )

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    yield line_str + '\n\n'

    except Exception as e:
        error_data = {
            'id': 'error',
            'choices': [{
                'delta': {'content': f'Connection error: {str(e)}'},
                'index': 0,
                'finish_reason': 'error'
            }]
        }
        yield f'data: {json.dumps(error_data)}\n\n'

    yield 'data: [DONE]\n\n'

def call_llm_api(messages, model, stream=False):
    """Call LLM API without streaming"""
    response = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://if-emotion.app',
            'X-Title': 'if.emotion'
        },
        json={
            'model': model,
            'messages': messages,
            'stream': False,
            'max_tokens': 2048,
            'temperature': 0.7
        }
    )
    return response.json()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='if.emotion OpenWebUI-compatible API Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()

    print(f"Starting if.emotion API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
