from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, current_app, Response
from flask_socketio import emit, disconnect, SocketIO, ConnectionRefusedError
from langchain_core.callbacks.manager import CallbackManager
from flask_wtf.csrf import validate_csrf
from flask_sitemap import Sitemap
from models import db, Chat, Message
from datetime import datetime
from utils.utility import *
from utils.ai_utils import *
from utils.managers.handler_manager import HandlerManager
from utils.handlers import SocketIOCallbackHandler
from profile import ProfileData
from functools import wraps
import jwt
import json
from gevent import monkey
import markdown
from seo import Seo
monkey.patch_all()

def configure_routes(app, socketio):

    sitemap = Sitemap(app=app)

    @app.context_processor
    def inject_analytics():
        return dict(
            google_analytics_id=app.config['GOOGLE_ANALYTICS_ID'],
            google_site_verification=app.config['GOOGLE_SITE_VERIFICATION'],
            bing_site_verification=app.config['BING_SITE_VERIFICATION']
        )

    
    @app.after_request
    def add_header(response):
        # Ensure the endpoint is not None before checking its value
        if request.endpoint and 'static' not in request.endpoint:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    
    # Robots.txt route
    @app.route('/robots.txt')
    def robots_txt():
        base_url = request.url_root[:-1]  # Remove the trailing slash
        lines = [
            "User-Agent: *",
            "Allow: /",
            f"Sitemap: {base_url}/sitemap.xml"
        ]
        return Response("\n".join(lines), mimetype="text/plain")


    # Index page route
    @app.route('/', methods=['GET'])
    def index_page():
        # Retrieve chat_uuid from the session
        chat_uuid = session.get('chat_uuid')
    
        if chat_uuid:
            # Retrieve the chat using uuid
            chat = Chat.query.filter_by(uuid=chat_uuid).first()
            if chat and chat.messages.count() > 0:
                # If the chat exists and has messages, redirect to chat page
                return redirect(url_for('chat_page'))
            else:
                # If the chat exists but has no messages, you might want to remove the chat_uuid from the session
                session.pop('chat_uuid', None)
    
        # Render the initial chat page (index.html)
        return render_template('index.html', profileData=ProfileData, seometa=Seo, aiProvider=current_app.config['AI_PROVIDER'])
    

    @app.route('/chat', methods=['GET', 'POST'])
    def chat_page():
        chat_uuid = session.get('chat_uuid')
        
        if request.method == 'POST':
            # Handle incoming POST chat message
            message_content = request.form.get('message')
            
            if not message_content:
                # If no message content, redirect back or handle the error
                return redirect(url_for('index_page'))

            if not chat_uuid:
                # Create a new chat session
                chat = Chat()
                db.session.add(chat)
                db.session.commit()
                chat_uuid = chat.uuid
                session['chat_uuid'] = chat_uuid
            else:
                # Retrieve existing chat
                chat = Chat.query.filter_by(uuid=chat_uuid).first()
                if not chat:
                    # Chat ID in session is invalid, create a new chat
                    chat = Chat()
                    db.session.add(chat)
                    db.session.commit()
                    chat_uuid = chat.uuid
                    session['chat_uuid'] = chat_uuid

            session['chat_init_message'] = message_content
            return redirect(url_for('chat_page'))
        
        else:
            message_content = None
            # Handle GET request
            if not chat_uuid:
                # If no chat session exists, redirect to index page
                return redirect(url_for('index_page'))

            chat = Chat.query.filter_by(uuid=chat_uuid).first()
            if not chat:
                # If the chat doesn't exist, remove chat_id from session and redirect
                session.pop('chat_uuid', None)
                return redirect(url_for('index_page'))

            # Check if session['chat_init_message'] exists
            if 'chat_init_message' in session:
                # Get the message from the session
                message_content = session['chat_init_message']
                messages = []
            else:
                # Load messages for the chat session
                messages = chat.messages.all()

        # Render the chat page with existing messages
        return render_template('chat.html', profileData=ProfileData, messages=messages, message_content=message_content, seometa=Seo, aiProvider=current_app.config['AI_PROVIDER'])


    @app.route('/new', methods=['GET'])
    def new():
        # Clear the chat session variable
        session.pop('chat_uuid', None)
        # Redirect to the main (index) page
        return redirect(url_for('index_page'))

    
    @sitemap.register_generator
    def index():
        yield 'index_page', {}


    @socketio.on('connect')
    def handle_connect(auth):
        current_app.logger.error('New WebSocket connection attempt initiated')
        csrf_token = auth.get('csrf_token')  # Retrieve the CSRF token from the client

        try:
            # Validate the CSRF token
            validate_csrf(csrf_token)
            current_app.logger.info('Successfully established and initialized a connection')

            conversation_handler = current_app.handler_manager.get_handler(request.sid)
            
        except ConnectionRefusedError as e:
            current_app.logger.error(f'Connection refused: {str(e)}')
            raise
        except Exception as e:
            current_app.logger.error('Unexpected error during connection handling')
            raise ConnectionRefusedError(f'Connection failed: {str(e)}')

    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        current_app.logger.info('New Chat Message Received')
        message = data.get('message', '').strip()
    
        # Check if message is missing
        if not message:
            current_app.logger.error('Unexpected error: Missing message in the payload')
            emit('error', {'message': 'Unexpected error: Missing message'})
            disconnect()
            return

        # Get the chat UUID from the session
        chat_uuid = session.get('chat_uuid')
        if not chat_uuid:
            current_app.logger.error('No chat session found.')
            emit('error', {'message': 'No chat session found.'})
            disconnect()
            return

        # Add the user's new message to the DB
        user_msg = Message(chat_uuid=chat_uuid, sender='user', content=message)
        db.session.add(user_msg)
        db.session.commit()
        
        # Retrieve the chat
        chat = Chat.query.filter_by(uuid=chat_uuid).first()
        if not chat:
            current_app.logger.error('Invalid chat session.')
            emit('error', {'message': 'Invalid chat session.'})
            disconnect()
            return

        # Count messages in the chat to ensure it's a valid conversation
        message_count = Message.query.filter_by(chat_uuid=chat_uuid).count()
        if message_count < 1:
            current_app.logger.error('Chat does not have enough messages.')
            emit('error', {'message': 'Chat does not have enough messages.'})
            disconnect()
            return

        # Extract the messages so far
        chat_messages = extract_messages_from_chat(chat)

        # Process the message and generate an AI response
        # process_message should return a string response or None if it fails
        try:
            conversation_handler = current_app.handler_manager.get_handler(request.sid)
            callback_manager = CallbackManager([conversation_handler])
            ai_response = process_message(message, chat_messages, socketio=socketio, callback_manager=callback_manager)
            ai_response = markdown.markdown(ai_response)
        except Exception as e:
            current_app.logger.exception('Error generating AI response')
            emit('error', {'message': f'Error generating response: {str(e)}'})
            disconnect()
            return

        if not ai_response:
            current_app.logger.error('Could not generate a response.')
            emit('error', {'message': 'Could not generate a response.'})
            disconnect()
            return

        # Save the AI's response to the database
        ai_msg = Message(chat_uuid=chat_uuid, sender='ai', content=ai_response)
        db.session.add(ai_msg)
        db.session.commit()

    
    @socketio.on('init_conversation') 
    def handle_init_conversation():
        
        if 'chat_init_message' in session:
            emit('init_conversation_response', {'init': True}) 
            mgs = session['chat_init_message']
            
            chat_uuid = session.get('chat_uuid')
            if chat_uuid:
                chat = Chat.query.filter_by(uuid=chat_uuid).first()
                if chat:
                    # Add the user's message to DB
                    user_msg = Message(chat_uuid=chat_uuid, sender='user', content=mgs)
                    db.session.add(user_msg)
                    db.session.commit()

                    # Extract chat history and process the message
                    chat_messages = extract_messages_from_chat(chat)
                    conversation_handler = current_app.handler_manager.get_handler(request.sid)
                    callback_manager = CallbackManager([conversation_handler])
                        
                    try:
                        ai_response = process_message(mgs, chat_messages, socketio=socketio, callback_manager=callback_manager)
                        ai_response = markdown.markdown(ai_response)
                         
                        # Save the AI's response to the database
                        ai_msg = Message(chat_uuid=chat_uuid, sender='ai', content=ai_response)
                        db.session.add(ai_msg)
                        db.session.commit()

                        session.pop('chat_init_message', None)
                        session.modified = True  # Mark the session as modified
                        
                        # Force a session save
                        from flask import session as flask_session
                        flask_session.modified = True
                        
                    except Exception as e:
                        current_app.logger.exception('Error generating Init AI response')
                        emit('error', {'message': f'Error generating Init response: {str(e)}'})
        else:    
            current_app.logger.error("No chat_init_message found in init_conversation")
            emit('init_conversation_response', {'init': False})

    
    @socketio.on('stop_conversation') 
    def handle_stop_conversation():
        conversation_handler = current_app.handler_manager.stop_handler(request.sid)
        emit('stop_conversation_response', {'stopped': True})


    @socketio.on('disconnect')
    def handle_disconnect():
        current_app.handler_manager.remove_handler(request.sid)
        current_app.logger.info(f"Disconnected: {str(request.sid)}")
