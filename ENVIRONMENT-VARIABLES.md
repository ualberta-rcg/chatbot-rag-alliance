<img src="https://www.ualberta.ca/en/toolkit/media-library/homepage-assets/ua_logo_green_rgb.png" alt="University of Alberta Logo" width="30%" />

# 🧪 Environment Variables – Helpy Chatbot

This document lists all environment variables used by **Helpy**, the Alliance Cluster Concierge Chatbot.

Helpy uses a Retrieval-Augmented Generation (RAG) backend and supports a variety of LLM providers. You must define:

✅ Exactly **one** AI provider  
✅ Two models (`AI_MODEL_A` and `AI_MODEL_B`) — regardless of provider  
✅ The corresponding API key(s) and URL(s) for your selected provider  

> **Maintainer:** Rahim Khoja · [khoja1@ualberta.ca](mailto:khoja1@ualberta.ca)

---

## ✅ Required Variables

| Variable         | Description                                      | Required | Example                      |
|------------------|--------------------------------------------------|----------|------------------------------|
| `AI_PROVIDER`    | The LLM backend to use                           | ✅ Yes   | `OPENAI`                     |
| `AI_MODEL_A`     | Primary model for generating responses           | ✅ Yes   | `gpt-4`                      |
| `AI_MODEL_B`     | Secondary model for summaries or search queries  | ✅ Yes   | `gpt-4o-mini`                |
| `SECRET_KEY`     | Flask secret key for session signing             | ✅ Yes   | `a-long-secret-key`          |

---

## 🔑 Provider-Specific API Keys

You only need to define the keys for the **AI_PROVIDER** you choose.

| Variable             | Description                       | Required if `AI_PROVIDER` = | Notes                             |
|----------------------|-----------------------------------|------------------------------|-----------------------------------|
| `OPENAI_API_KEY`     | OpenAI API key                    | `OPENAI`                     | Required for GPT-4, GPT-4o        |
| `GROQ_API_KEY`       | GroqCloud API key                 | `GROQCLOUD`                  | Required for Mixtral, etc.        |
| `ANTHROPIC_API_KEY`  | Anthropic Claude API key          | `ANTHROPIC`                  | Required for Claude 3             |
| `GOOGLE_AI_API_KEY`  | Google Gemini API key             | `GOOGLE`                     | Required for Gemini Pro           |
| `OLLAMA_BASE_URL`    | Base URL for your Ollama instance | `OLLAMA`                     | e.g., `http://localhost:11434`    |

---

## 📡 RAG Integration (Required)

| Variable             | Description                            | Required | Example                                 |
|----------------------|----------------------------------------|----------|-----------------------------------------|
| `RAGFLOW_API_KEY`    | API key for RAGFlow vector search      | ✅ Yes   | `rfk-...`                                |
| `RAGFLOW_API_URL`    | Base URL for RAGFlow API               | ✅ Yes   | `https://ragflow.example.com`           |
| `RAGIE_API_KEY`      | API key for https://www.ragie.ai/      |           | `tnt_...`                              |

> 🔍 You do **not** need `RAGIE_API_KEY` unless you're using Ragie (optional).

---

## ⚙️ Optional Runtime Settings

| Variable                     | Description                              | Default        |
|------------------------------|------------------------------------------|----------------|
| `LOG_LEVEL`                  | Logging verbosity                        | `DEBUG`        |
| `SQLALCHEMY_DATABASE_URI`    | DB connection URI                        | `sqlite:///./chat.db` |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | SQLAlchemy setting for change tracking | `False`        |
| `SYSTEM_MAINTENANCE_MODE`    | Show maintenance banner                  | `False`        |

---

## 📈 SEO & Analytics (Optional)

| Variable                     | Description                              | Notes                      |
|------------------------------|------------------------------------------|-----------------------------|
| `GOOGLE_ANALYTICS_ID`        | Google Analytics tracking ID             | e.g., `G-XXXXXXX`           |
| `GOOGLE_SITE_VERIFICATION`   | Meta tag for Google Search Console       | Use `NONE` to disable       |
| `BING_SITE_VERIFICATION`     | Meta tag for Bing Webmaster Tools        | Use `NONE` to disable       |

---

## 📄 Example: `.env` for OpenAI

```env
# Required
SECRET_KEY=supersecret123
AI_PROVIDER=OPENAI
AI_MODEL_A=gpt-4
AI_MODEL_B=gpt-4o-mini

# OpenAI API
OPENAI_API_KEY=sk-...

# RAGFlow
RAGFLOW_API_KEY=rfk-...
RAGFLOW_API_URL=https://ragflow.example.com
```

## 📄 Example: `.env` for Ollama

```env
# Required
SECRET_KEY=supersecret123
AI_PROVIDER=OLLAMA
AI_MODEL_A=llama3
AI_MODEL_B=mistral

# Ollama (self-hosted or remote)
OLLAMA_BASE_URL=http://ollama.myserver.local:11434

# RAGFlow
RAGFLOW_API_KEY=rfk-...
RAGFLOW_API_URL=https://ragflow.example.com
```

---

For Kubernetes-based deployments, see [`KUBERNETES-DEPLOYMENT.md`](./KUBERNETES-DEPLOYMENT.md).

```bash
# Validate current environment
env | grep -i ai
```
