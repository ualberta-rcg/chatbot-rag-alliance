<img src="https://www.ualberta.ca/en/toolkit/media-library/homepage-assets/ua_logo_green_rgb.png" alt="University of Alberta Logo" width="50%" />

# Helpy – Alliance Cluster Concierge Chatbot

[![CI/CD](https://github.com/ualberta-rcg/chatbot-rag-alliance/actions/workflows/build-chatbot-rag-alliance.yml/badge.svg)](https://github.com/ualberta-rcg/chatbot-rag-alliance/actions/workflows/build-chatbot-rag-alliance.yml)
![Docker Pulls](https://img.shields.io/docker/pulls/rkhoja/chatbot-rag-alliance?style=flat-square)
![Docker Image Size](https://img.shields.io/docker/image-size/rkhoja/chatbot-rag-alliance/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

**Maintained by:** Rahim Khoja ([khoja1@ualberta.ca](mailto:khoja1@ualberta.ca)) 

## 🧰 Description

This repository contains the source code and Kubernetes deployment for Helpy — a containerized, Retrieval-Augmented Generation (RAG) chatbot built to support users on Digital Research Alliance of Canada HPC clusters.

Helpy answers user questions about Slurm job scheduling, software environments, module usage, and Alliance-specific documentation. It supports multiple large language model (LLM) providers including OpenAI, Anthropic, GroqCloud, Google AI, and Ollama, and retrieves knowledge from vector databases like RAGFlow and (soon) Google Agent.

The backend is Flask-based with optional WebSocket streaming and supports integration with Slack, Google Chat, and other future UIs through modular route extensions.

**Note:** *This project was initially developed and donated to the University of Alberta by Rahim Khoja.*

The image is automatically built and pushed to Docker Hub using GitHub Actions whenever changes are pushed to the `latest` branch.

**Docker Hub:** [rkhoja/chatbot-rag-alliance\:latest](https://hub.docker.com/r/rkhoja/chatbot-rag-alliance)

```bash
docker pull rkhoja/chatbot-rag-alliance:latest
```

### 🏗️ What's Inside

Update the contents list to reflect chatbot components:

This container includes:

* Flask + Flask-SocketIO web server with CSRF and session management
* LangChain integration with support for OpenAI, Groq, Anthropic, Ollama, and Google AI
* Vector search via RAGFlow (and optionally Ragie)
* Real-time chat interface using Markdown rendering and WebSocket streaming
* Prompt templating system with RAG integration and persona switching
* Future-ready route design for Slack bots, Google Chat bots, and others

## 📦 Requirements

To run Helpy, the following services or APIs must be available:

* At least one LLM provider:
  * OpenAI (ChatGPT)
  * GroqCloud
  * Anthropic
  * Google AI Studio
  * Ollama (self-hosted)
* A RAG source (vector database), such as:
  * RAGFlow (recommended)
  * Ragie (optional, alternative)
* Kubernetes cluster (any distribution) with:
  * Ingress controller (e.g. Traefik or NGINX)
  * cert-manager (for TLS certificates)
  * Secrets and ConfigMap support
* Docker registry (e.g. Docker Hub) for image hosting
* Optional: Slack or Google Chat for external UI integrations (coming soon)

> ℹ️ Your AI provider must be set up with an API key and accessible endpoint. Some providers (like Ollama) may require a self-hosted container.


## 🛠️ GitHub Actions - CI/CD Pipeline

This project includes a GitHub Actions workflow: `.github/workflows/build-chatbot-rag-alliance.yml`.

### 🔄 What It Does

* Builds the Docker image from the `Dockerfile`
* Logs into Docker Hub using stored GitHub Secrets
* Pushes the image tagged as the current branch (usually `latest`)

### ✅ Setting Up GitHub Secrets

To enable pushing to your Docker Hub:

1. Go to your fork's GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add the following:

   * `DOCKER_HUB_REPO` → your Docker Hub repo. In this case: *rkhoja/chatbot-rag-alliance* 
   * `DOCKER_HUB_USER` → your Docker Hub username
   * `DOCKER_HUB_TOKEN` → create a [Docker Hub access token](https://hub.docker.com/settings/security)

### 🚀 Manual Trigger & Auto-Build

* Manual: Run the workflow from the **Actions** tab with **Run workflow** (enabled via `workflow_dispatch`).
* Automatic: Any push to the `latest` branch triggers the CI/CD pipeline.

* **Recommended branching model:**
  * Work and test in `main`
  * Merge or fast-forward `main` to `latest` to trigger a production build

```bash
git checkout latest
git merge main
git push origin latest
```

## 🤝 Support

Many Bothans died to bring us this information. This project is provided as-is, but reasonable questions may be answered based on my coffee intake or mood. ;)

Feel free to open an issue or email **[khoja1@ualberta.ca](mailto:khoja1@ualberta.ca)** for U of A related deployments.

## 📜 License

This project is released under the **MIT License** - one of the most permissive open-source licenses available.

**What this means:**
- ✅ Use it for anything (personal, commercial, whatever)
- ✅ Modify it however you want
- ✅ Distribute it freely
- ✅ Include it in proprietary software

**The only requirement:** Keep the copyright notice somewhere in your project.

That's it! No other strings attached. The MIT License is trusted by major projects worldwide and removes virtually all legal barriers to using this code.

**Full license text:** [MIT License](./LICENSE)

## 🧠 About University of Alberta Research Computing

The [Research Computing Group](https://www.ualberta.ca/en/information-services-and-technology/research-computing/index.html) supports high-performance computing, data-intensive research, and advanced infrastructure for researchers at the University of Alberta and across Canada.

We help design and operate compute environments that power innovation — from AI training clusters to national research infrastructure.
