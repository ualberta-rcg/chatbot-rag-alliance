<img src="https://www.ualberta.ca/en/toolkit/media-library/homepage-assets/ua_logo_green_rgb.png" alt="University of Alberta Logo" width="30%" />

# 🧪 Environment Variables – Helpy Chatbot

This document lists all environment variables used by **Helpy**, the Alliance Cluster Concierge Chatbot.

Variables are loaded via Kubernetes secrets, `.env` files, or GitHub Actions secrets, depending on your deployment environment.

> **Maintainer:** Rahim Khoja · [khoja1@ualberta.ca](mailto:khoja1@ualberta.ca)

---

| Variable                 | Description                                                                 | Required | Default / Notes                                     |
|--------------------------|-----------------------------------------------------------------------------|----------|------------------------------------------------------|
| `SECRET_KEY`             | Flask secret key for session signing                                        | ✅ Yes   | Auto-generates session encryption                   |
| `LOG_LEVEL`              | Logging verbosity                                                           | ❌ No    | `DEBUG`                                              |
| `SQLALCHEMY_DATABASE_URI`| SQLAlchemy DB connection string                                              | ❌ No    | `sqlite:///./chat.db`                               |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | SQLAlchemy setting for change tracking                                  | ❌ No    | `False`                                              |
| `SYSTEM_MAINTENANCE_MODE`| Enables system maintenance banner (e.g. “Down for updates”)                | ❌ No    | `False`                                              |

---

### 🔑 API Keys

| Variable             | Description                                       | Required | Default / Notes                         |
|----------------------|---------------------------------------------------|----------|------------------------------------------|
| `OPENAI_API_KEY`     | OpenAI API key for GPT models                     | ✅ Yes   | Needed when `AI_PROVIDER=OPENAI`        |
| `GROQ_API_KEY`       | GroqCloud API key                                 | ✅ Yes   | Needed when `AI_PROVIDER=GROQCLOUD`     |
| `ANTHROPIC_API_KEY`  | Claude API key                                    | ✅ Yes   | Needed when `AI_PROVIDER=ANTHROPIC`     |
| `GOOGLE_AI_API_KEY`  | Gemini / Google AI Studio API key                | ✅ Yes   | Needed when `AI_PROVIDER=GOOGLE`        |
| `RAGIE_API_KEY`      | Ragie vector search API key                       | ❌ No    | Optional if RAGie is used               |
| `RAGFLOW_API_KEY`    | RAGFlow API key for vector search                 | ✅ Yes   | Used by default                         |
| `RAGFLOW_API_URL`    | Base URL for RAGFlow API                          | ✅ Yes   | Example: `https://ragflow.example/api`  |
| `OLLAMA_BASE_URL`    | Base URL for local Ollama server                 | ❌ No    | Defaults to `http://64.181.202.213:11434` |

---

### 🧠 AI Model & Provider

| Variable         | Description                                                | Required | Notes                                  |
|------------------|------------------------------------------------------------|----------|-----------------------------------------|
| `AI_PROVIDER`    | The LLM backend to use                                     | ✅ Yes   | Options: `OLLAMA`, `OPENAI`, `GROQCLOUD`, `ANTHROPIC`, `GOOGLE` |
| `AI_MODEL_A`     | Primary model for generating answers                       | ✅ Yes   | Example: `deepseek-r1:671b`             |
| `AI_MODEL_B`     | Secondary model used for RAG search queries or summaries   | ✅ Yes   | Example: `command-r-plus:latest`        |

---

### 📈 Analytics & SEO (Optional)

| Variable                     | Description                              | Required | Notes                              |
|------------------------------|------------------------------------------|----------|-------------------------------------|
| `GOOGLE_ANALYTICS_ID`        | Google Analytics tracking ID             | ❌ No    | e.g., `G-XXXXXXX`                   |
| `GOOGLE_SITE_VERIFICATION`   | Meta tag value for Google Search Console | ❌ No    |                                    |
| `BING_SITE_VERIFICATION`     | Meta tag value for Bing Webmaster Tools  | ❌ No    |                                    |

---

### 💡 Tips

- You can override environment variables via Helm, Kubernetes secrets, `.env`, or a CI/CD system.
- Use `None` (case-insensitive) to disable optional analytics fields.
- Models `AI_MODEL_A` and `AI_MODEL_B` should match the capabilities of your selected `AI_PROVIDER`.

---

### Example `.env` file (for local dev)

```env
SECRET_KEY=mysecretkey123
AI_PROVIDER=OPENAI
AI_MODEL_A=gpt-4
AI_MODEL_B=gpt-3.5-turbo
OPENAI_API_KEY=sk-...
RAGFLOW_API_KEY=rfk-...
RAGFLOW_API_URL=https://ragflow.example.com
```

---

For Kubernetes-based deployments, see [`KUBERNETES-DEPLOYMENT.md`](./KUBERNETES-DEPLOYMENT.md).

```bash
# Validate current environment
env | grep -i ai
```
