import os

class ProfileData:
    
    FIRST_NAME = os.getenv('PROFILE_FIRST_NAME', "Helpy")
    LAST_NAME = os.getenv('PROFILE_LAST_NAME', "Concierge")
    IMAGE_FILE = os.path.join("images", os.getenv('PROFILE_IMAGE_FILE', "drac.png"))
    PROMPT1 = os.getenv('PROFILE_PROMPT_1', "How can I get started with Alliance HPC resources?")
    PROMPT2 = os.getenv('PROFILE_PROMPT_2', "What are the steps to request an Alliance account?")
    PROMPT3 = os.getenv('PROFILE_PROMPT_3', "How does Fairshare work in Slurm scheduling?")
    CHATBOT_BIO = ""
    RESPONSE_GUIDELINES = ""
    GENERATE_PROMPT_SYSTEM_PROMPT = ""
    MESSAGE_SUMMARY_SYSTEM_PROMPT = ""
    RAG_SEARCH_QUERY_SYSTEM_PROMPT = ""

    # Load ChatBot Bio
    try:
        with open("prompts/chatbot_bio.txt", "r") as f:
            CHATBOT_BIO = f.read()
    except FileNotFoundError:
        print("Error: chatbot_bio.txt not found. Exiting.")
        exit(1)  

    # Load Chat Bot Response Guidelines
    try:
        with open("prompts/generate_prompt_response_guidelines.txt", "r") as f:
            RESPONSE_GUIDELINES = f.read()
    except FileNotFoundError:
        print("Error: generate_prompt_response_guidelines.txt not found. Exiting.")
        exit(1)    

    # Load System Prompt for Generate Prompt Function
    try:
        with open("prompts/generate_prompt_system_prompt.txt", "r") as f:
            GENERATE_PROMPT_SYSTEM_PROMPT = f.read()
    except FileNotFoundError:
        print("Error: generate_prompt_system_prompt.txt not found. Exiting.")
        exit(1)   

    # Load System Prompt for Message Summary Function
    try:
        with open("prompts/message_summary_system_prompt.txt", "r") as f:
            MESSAGE_SUMMARY_SYSTEM_PROMPT = f.read()
    except FileNotFoundError:
        print("Error: message_summary_system_prompt.txt not found. Exiting.")
        exit(1)   

    # Load System Prompt for Rag Search Query Function
    try:
        with open("prompts/rag_search_query_system_prompt.txt", "r") as f:
            RAG_SEARCH_QUERY_SYSTEM_PROMPT = f.read()
    except FileNotFoundError:
        print("Error: rag_search_query_system_prompt.txt not found. Exiting.")
        exit(1) 
