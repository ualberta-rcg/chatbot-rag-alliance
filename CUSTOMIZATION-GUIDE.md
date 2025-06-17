<img src="https://www.ualberta.ca/en/toolkit/media-library/homepage-assets/ua_logo_green_rgb.png" alt="University of Alberta Logo" width="30%" />

# 🧩 Customization Guide – Helpy Chatbot Internals

This guide explains the customizable files in the `app/` directory. These control Helpy’s prompts, SEO metadata, personality, and behavior.

> These files are safe to edit and allow you to tailor the chatbot's responses, appearance, and tone without modifying core logic.



## 📁 `app/prompts/` – Prompt Templates

This folder defines the behavior of the chatbot through editable system prompts.

| File                                  | Purpose                                                                 |
|---------------------------------------|-------------------------------------------------------------------------|
| `chatbot_bio.txt`                     | Personality and identity text inserted into prompts                    |
| `generate_prompt_response_guidelines.txt` | Writing guidelines for the AI when forming answers                  |
| `generate_prompt_system_prompt.txt`  | Base system message that starts all conversations                     |
| `message_summary_system_prompt.txt`  | Prompt used to summarize older conversation history                   |
| `rag_search_query_system_prompt.txt` | Prompt to guide the AI in formulating keyword-style RAG search queries |

> ✏️ You can rewrite these in plain text — markdown and natural language are supported.



## 🧠 `app/profile.py` – Chatbot Persona Settings

This module defines key metadata for the chatbot's identity, language support, and prompt structure. It loads:

- The text content from `app/prompts/`
- The chatbot’s default bio and description
- Dual-language settings (English & French)
- Response structure guidelines

If you want to override how the bot introduces itself or change how responses are formatted, start here.



## 🌐 `app/seo.py` – SEO Metadata

This file injects values into templates for SEO and web crawlers.

| Field        | Description                                       |
|--------------|---------------------------------------------------|
| `title`      | `<title>` tag used in HTML pages                 |
| `description`| Meta description for search engines              |
| `keywords`   | Meta keywords for HTML head section              |
| `author`     | Optional field for ownership/credit info         |



## ⚙️ `app/config.py` – Runtime Config Class

This module defines all environment variables and runtime settings.

It handles:

- Flask secret keys
- AI provider/model configuration
- API keys (OpenAI, Groq, Anthropic, etc.)
- RAG integration settings
- SQLAlchemy DB URI and tracking
- Optional maintenance mode
- Google/Bing verification settings

> ✅ This class reads from environment variables at startup. You do not need to modify this file unless you're changing how configuration is loaded.



## 🧠 `app/utils/ai_utils.py` – AI Behavior Logic

This is where most of the AI logic happens. It handles how prompts are created, RAG results are retrieved, and responses are processed.

| Function                        | Purpose                                                                 |
|----------------------------------|-------------------------------------------------------------------------|
| `generate_prompt(...)`          | Builds the final prompt sent to the LLM using recent messages, RAG, etc. |
| `generate_rag_search_query(...)`| Uses AI_MODEL_B to extract search terms for RAG                         |
| `generate_message_summary(...)` | Summarizes earlier conversation history                                |
| `get_ragflow_results(...)`      | Performs document retrieval from RAGFlow                               |
| `get_ragie_results(...)`        | (Optional) Uses Ragie for fallback search                              |
| `get_llm(...)`                  | Instantiates the right LangChain LLM based on `AI_PROVIDER`            |
| `process_message(...)`          | Orchestrates everything: building prompt, calling the model, formatting response |

This is a great place to:
- Add logging for debug
- Change how search results are filtered or scored
- Insert additional checks (e.g., profanity filters, audit logs)

> 🧪 This is the most advanced area of customization and may require Python and LangChain familiarity.



## ✨ Customization Tips

- You can change the bot's name, tone, or audience by updating `chatbot_bio.txt` and `generate_prompt_system_prompt.txt`.
- Add French or bilingual behavior directly inside `profile.py` under `CHATBOT_BIO` and `CHATBOT_DESCRIPTION`.
- Want to customize how queries are answered? Check `process_message()` in `ai_utils.py`.
- For testing, restart the pod or redeploy to load changes from `prompts/`.

```bash
# Example: edit prompt and restart chatbot deployment
nano app/prompts/generate_prompt_system_prompt.txt
kubectl rollout restart deployment chatbot-rag-alliance-deployment -n chatbot-rag-alliance
```
