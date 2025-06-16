import os

class ProfileData:

    try:
        with open("user_bio.txt", "r") as f:
            USER_BIO = f.read()
    except FileNotFoundError:
        print("Error: user_bio.txt not found. Exiting.")
        exit(1)  
    
    FIRST_NAME = os.getenv('PROFILE_FIRST_NAME', "Helpy")
    LAST_NAME = os.getenv('PROFILE_LAST_NAME', "Concierge")
    IMAGE_FILE = os.path.join("images", os.getenv('PROFILE_IMAGE_FILE', "drac.png"))
    PROMPT1 = os.getenv('PROFILE_PROMPT_1', "How can I get started with Alliance HPC resources?")
    PROMPT2 = os.getenv('PROFILE_PROMPT_2', "What are the steps to request an Alliance account?")
    PROMPT3 = os.getenv('PROFILE_PROMPT_3', "How does Fairshare work in Slurm scheduling?")
