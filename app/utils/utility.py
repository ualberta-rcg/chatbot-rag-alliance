# Standard library imports
import json
import os
import re
import sys
import time
from datetime import datetime

# Third-party imports
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, current_app
from flask_sqlalchemy import SQLAlchemy
from regex import regex

# Local application/library specific imports
from models import db, chat, message 


def extract_messages_from_chat(chat):
    """Extracts messages from a chat and formats them for further processing."""
    formatted_messages = []

    # messages are already ordered by created timestamp due to the relationship definition
    chat_messages = chat.messages.all()  

    # Loop through each message and format it based on the sender (user or AI)
    for msg in chat_messages:
        if msg.sender == 'user':
            formatted_messages.append(f"User: {msg.content}")
        else:
            formatted_messages.append(f"AI: {msg.content}")

    return formatted_messages
