# Third-party imports
import requests
from flask import Flask, request, session, jsonify, current_app
from flask_socketio import emit, disconnect, SocketIO
from ragie import Ragie
from markdown import markdown
from bs4 import BeautifulSoup
from ragflow_sdk import RAGFlow

from utils.handlers import SocketIOCallbackHandler

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks.manager import CallbackManager
from langchain_community.chat_models import ChatOllama

# Standard library imports
import os
import re
import sys
import time
import html
import string
import inspect
import logging

from profile import ProfileData


def strip_markdown(text):
    # Convert Markdown to HTML
    html = markdown(text)
    # Use BeautifulSoup to strip HTML tags
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def process_message(message, messages, socketio, callback_manager):
    current_app.logger.debug("Starting process_message")
        
    current_messages = messages[-3:]
    recent_messages = messages[-7:-3] 
    old_messages = messages[:-7]
    
    summary = None
    if old_messages:
        summary = generate_message_summary(old_messages)
        current_app.logger.error(f'Coversation Summary Created: {summary}')
        
    # Assign variables for the newest, second newest, and third newest messages
    newest_message = current_messages[-1] if len(current_messages) > 0 else None
    second_newest_message = current_messages[-2] if len(current_messages) > 1 else None
    rag_search_query =  generate_rag_search_query(message, second_newest_message, newest_message)

    current_app.logger.debug(f'RAG Search Query: {rag_search_query}')

    tp_k = 8
    if current_app.config['AI_PROVIDER'] == "GROQCLOUD":
        tp_k = 4
    
    try:
        rag_results = get_ragflow_results(rag_search_query, top_k=2048, max_chunks_per_document=tp_k)
    except Exception as e:
        current_app.logger.error(f"Error Getting rag_results: {str(e)}", exc_info=True)
        rag_results = None

    current_app.logger.error(f'RAG Search Results: {str(rag_results)}')
  
    llm_prompt = generate_prompt(summary, recent_messages, rag_results, current_messages, message) 

    current_app.logger.error(f'Prompt: {llm_prompt}')

    # Invoke the LLM
    #if current_app.config['AI_PROVIDER'] == "GOOGLE":
    #    llm = get_llm(ai_provider=current_app.config['AI_PROVIDER'], ai_model=current_app.config['AI_MODEL_A'])
    #else:
    #    llm = get_llm(ai_provider=current_app.config['AI_PROVIDER'], ai_model=current_app.config['AI_MODEL_A'], callback_manager=callback_manager, streaming=True)

    llm = get_llm(ai_provider=current_app.config['AI_PROVIDER'], ai_model=current_app.config['AI_MODEL_A'], callback_manager=callback_manager, streaming=True)

    # Set temperature if supported by the LLM class
    if llm and hasattr(llm, "temperature"):
        llm.temperature = float(current_app.config.get('AI_TEMPERATURE', 0.7))
    
    if llm:
        response_message = llm.invoke(llm_prompt)
        response_message_result = response_message.content.strip()
        current_app.logger.error(f"process_message response prompt: {response_message_result}")
        #if current_app.config['AI_PROVIDER'] == "GOOGLE":
        #    simulate_stream_string(callbacks, response_message_result)
    else:
        current_app.logger.error("process_message - RAG Results - Invalid LLM.")
        return False
        
    current_app.logger.debug(f"process_message Results: {response_message_result}")
    return response_message_result


def get_llm( callback_manager=None, streaming=False, max_tokens=1024, ai_provider=None, ai_model=None ):
    current_app.logger.debug("Starting get_llm")

    if ai_provider not in ["GROQCLOUD", "OPENAI", "ANTHROPIC", "GOOGLE", "OLLAMA"]:
        current_app.logger.error(f'Unsupported AI provider: {ai_provider}')
        return False

    # Logging the model selection
    current_app.logger.error(f'Langchain using LLM Provider: {ai_provider} with Model: {ai_model}')
    
    if ai_provider == "GROQCLOUD":
        return ChatGroq(
            api_key=current_app.config['GROQ_API_KEY'],
            model=ai_model,
            streaming=streaming,
            callback_manager=callback_manager,
            max_tokens=max_tokens,
        )
    elif ai_provider == "OPENAI":
        return ChatOpenAI(
            model=ai_model,
            streaming=streaming,
            callback_manager=callback_manager,
            #max_tokens=max_tokens,
        )
    elif ai_provider == "ANTHROPIC":
        return ChatAnthropic(
            api_key=current_app.config['ANTHROPIC_API_KEY'],
            model=ai_model,
            streaming=streaming,
            callback_manager=callback_manager,
            max_tokens=max_tokens,
        )
    elif ai_provider == "GOOGLE":
        return ChatGoogleGenerativeAI(
            api_key=current_app.config['GOOGLE_AI_API_KEY'],
            model=ai_model,
            streaming=streaming,
            callback_manager=callback_manager,
            #max_tokens=max_tokens,
        )
    elif ai_provider == "OLLAMA":
        return ChatOllama(
            base_url=current_app.config.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=ai_model,
            streaming=streaming,
            callback_manager=callback_manager,
        )

def generate_rag_search_query(user_message, user_message_2, ai_response):
    current_app.logger.debug("Starting generate_rag_search_query")

    system_message = ProfileData.RAG_SEARCH_QUERY_SYSTEM_PROMPT

    try:
        llm = get_llm(max_tokens=45, ai_provider=current_app.config['AI_PROVIDER'], ai_model=current_app.config['AI_MODEL_B'])

        # Build the prompt messages
        messages = [system_message]
        
        if ai_response:
            messages.append(f"ai: {html.escape(ai_response, quote=True)}\n")
        if user_message_2:
            messages.append(f"user_2: {html.escape(user_message_2, quote=True)}\n")
        
        # The primary user message is stated clearly
        messages.append(f"Current user query to base search terms on: {html.escape(user_message, quote=True)}")

        full_message = "\n".join(messages)
        
        current_app.logger.debug(f"Constructed prompt: {full_message}")
        
        # Invoke the LLM
        result = llm.invoke(full_message)

        # Extract and sanitize the result
        rag_query = result.content.strip()
        rag_query = strip_markdown(rag_query)

        current_app.logger.error(f"Generated RAG Query: {rag_query}")
        return rag_query+" "+str(user_message_2)

    except Exception as e:
        current_app.logger.error(f"Error generating RAG Query: {str(e)}", exc_info=True)
        if 'llm' not in locals() or llm is None:
            current_app.logger.error("generate_rag_search_query - Invalid LLM.")
        return None



def generate_message_summary(rest_of_messages):
    current_app.logger.debug(f"Starting generate_message_summary")

    # System message to provide context to the LLM for summarization
    system_message = ProfileData.MESSAGE_SUMMARY_SYSTEM_PROMPT

    try:
        # Select the correct model based on the primary AI provider
        llm = get_llm(ai_provider=current_app.config['AI_PROVIDER'], ai_model=current_app.config['AI_MODEL_B'] )
            
        # Prepare the conversation text from rest_of_messages
        conversation_text = ""
        for msg in rest_of_messages:
            # Append messages based on sender
             conversation_text += f"{msg}\n"

        # Combine the system message with the conversation content
        messages = f"""
        {system_message}

        {conversation_text}
        """

        current_app.logger.debug(f"Summerizing the following Messages: {messages}")
        
        # Invoke the LLM to generate the summary
        result = llm.invoke(messages)
        
        # Extract the content from the result
        summary = result.content.strip()
        
        current_app.logger.debug(f"Generated Summary: {summary}")
        return summary
    
    except Exception as e:
        current_app.logger.error(f"Error generating summary: {str(e)}", exc_info=True)
        if not llm:
            current_app.logger.error("generate_message_summary - Invalid LLM.")
        return None


def generate_prompt(summary, recent_messages, rag_results, current_messages, user_message):
    current_app.logger.debug("Starting generate_prompt")
    
    system_message = ProfileData.GENERATE_PROMPT_SYSTEM_PROMPT
    
    # Start with the system message
    prompt = system_message

    if ProfileData.CHATBOT_BIO:
        prompt += f"{ProfileData.CHATBOT_DESCRIPTION} This is your personal biography:\n{ProfileData.CHATBOT_BIO}"

    # Add history summary if it exists
    if summary:
        prompt += f"\n\nConversation context: {summary}"
    
    # Add recent messages
    if recent_messages:
        prompt += "\n\nPrevious discussion:"
        for msg in recent_messages:
            prompt += f"\n{msg}"
    
    # Add RAG results with career-focused instructions
    if rag_results:
        prompt += "\n\nRAG Results:"
        prompt += f"\n{rag_results}"
    
    # Add current conversation messages
    if current_messages:
        prompt += "\n\nCurrent conversation:"
        for msg in current_messages:
            prompt += f"\n{msg}"
    
    # Add the user's most recent message
    prompt += f"\n\nDigital Research Alliance of Canada User: {html.escape(user_message, quote=True)}"
    
    # Add response guidelines
    prompt += ProfileData.RESPONSE_GUIDELINES
    
    if not rag_results:
        prompt += """
        \n\nWhen information is limited:
        - Be transparent about what information is not available
        - Suggest what additional information might be helpful
        - Maintain professionalism while acknowledging limitations
        - Never invent or assume details about the user's experience
        """
    
    prompt += """
    \nDirect Contact Policy:
    - If a user asks something important that you cannot answer from the available documentation or RAG results, you should encourage them to contact the official support team at the Digital Research Alliance of Canada.
    - You may say: “It looks like this isn’t covered in the current documentation. I recommend reaching out to support@tech.alliancecan.ca for personalized assistance.”
    - You need to be mindfull to give only support that works on Allaince HPC Clusters. Much of the build in training is not quite right for us. 
    - NEVER suggest that you can file tickets, send emails, or contact humans on the user's behalf.
    - Remain professional and helpful when encouraging users to contact support directly.
    """

    current_app.logger.debug(f"Generated prompt: {prompt}")
    return prompt


def get_ragie_results(question, top_k=4, max_chunks_per_document=4):
    """
    Retrieves relevant documents using Ragie based on the question.
    
    :param question: The input question to retrieve documents for
    :param top_k: Number of top results to return
    :param max_chunks_per_document: Maximum number of chunks per document
    :return: Retrieved results or None if no results found
    """
    current_app.logger.debug(f"Starting get_ragie_results")
    # Initialize Ragie with API key from current app config
    s = Ragie(auth=current_app.config['RAGIE_API_KEY'])
    
    # Make the retrieval request
    res = s.retrievals.retrieve(request={
        "query": question,
        "top_k": top_k,
        "rerank": False,
        "max_chunks_per_document": max_chunks_per_document,
    })

    # Handle the response
    if res is not None:
        current_app.logger.error(f"Rag Results: {str(res)}")
        return res
    else:
        current_app.logger.debug(f"No Rag Results")
        return None


def get_ragflow_results(question, top_k=50, max_chunks_per_document=8):
    current_app.logger.debug(f"Starting get_ragflow_results")

    rag = RAGFlow(
        api_key=current_app.config['RAGFLOW_API_KEY'],
        base_url=current_app.config['RAGFLOW_API_URL']
    )

    datasets = rag.list_datasets(name="Alliance-Wiki-Api")
    if not datasets:
        current_app.logger.error("Dataset 'Alliance-Wiki-Api' not found")
        return None
    dataset = datasets[0]

    try:
        res = rag.retrieve(
            question=question,
            dataset_ids=[dataset.id],
            page=1,
            page_size=max_chunks_per_document,
            similarity_threshold=0.25,
            vector_similarity_weight=0.35,
            top_k=top_k,
            keyword=True
        )

        if not res:
            current_app.logger.warning("RAGFlow: No results returned")
            return None

        current_app.logger.info(f"RAGFlow: Retrieved {len(res)} chunks")
        return "\n\n".join(chunk.content.strip() for chunk in res if hasattr(chunk, "content"))

    except Exception as e:
        current_app.logger.error(f"RAGFlow retrieval failed: {e}", exc_info=True)
        return None

