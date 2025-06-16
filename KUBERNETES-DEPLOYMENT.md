<img src="https://www.ualberta.ca/en/toolkit/media-library/homepage-assets/ua_logo_green_rgb.png" alt="University of Alberta Logo" width="30%" />

# ☸️ Kubernetes Deployment – Helpy Chatbot

This guide documents how to deploy the **Helpy – Alliance Cluster Concierge Chatbot** to a Kubernetes environment.

Helpy is a Flask-based, RAG-powered chatbot designed for Alliance HPC clusters. It supports multiple LLM providers (OpenAI, Anthropic, GroqCloud, Ollama, Google AI) and retrieves content from vector databases like RAGFlow.

This guide includes manifests for Secrets, Deployments, Services, TLS certificates, and Ingress configuration.

> **Maintainer:** Rahim Khoja · [khoja1@ualberta.ca](mailto:khoja1@ualberta.ca)  
> **Docker Image:** [`rkhoja/chatbot-rag-alliance:latest`](https://hub.docker.com/r/rkhoja/chatbot-rag-alliance)

## ☸️ Kubernetes Deployment Guide

This guide describes how to deploy the Helpy chatbot on a Kubernetes cluster.

### 📦 1. Prerequisites

Ensure you have:

- A Kubernetes cluster (e.g. RKE2, k3s, GKE, etc.)
- `kubectl` configured to access the cluster
- A working **Ingress controller** (e.g., Traefik or NGINX)
- **Cert-Manager** installed if you're using TLS
- A domain name pointing to your Ingress controller
- Docker Hub credentials stored as GitHub secrets (for CI/CD)

---

### 📁 2. Namespace and Secrets

Start by creating a dedicated namespace and Kubernetes Secret containing your API keys:

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: chatbot-rag-alliance
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: chatbot-rag-alliance
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key"
  GOOGLE_AI_API_KEY: "your-google-api-key"
  ANTHROPIC_API_KEY: "your-anthropic-api-key"
  GROQ_API_KEY: "your-groq-api-key"
  OPENAI_API_KEY: "your-openai-api-key"
  RAGIE_API_KEY: "your-ragie-api-key"
  RAGFLOW_API_KEY: "your-ragflow-api-key"
```

---

### 🚀 3. Deployment

This deployment will run the chatbot using the Docker image built and pushed by GitHub Actions.

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-rag-alliance-deployment
  namespace: chatbot-rag-alliance
  labels:
    app: chatbot-rag-alliance
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chatbot-rag-alliance
  template:
    metadata:
      labels:
        app: chatbot-rag-alliance
    spec:
      containers:
      - name: chatbot-rag-alliance
        image: rkhoja/chatbot-rag-alliance:latest
        imagePullPolicy: Always
        env:
          - name: AI_PROVIDER
            value: "OLLAMA" # [OLLAMA, OPENAI, GROQCLOUD, ANTHROPIC, GOOGLE]
          - name: AI_MODEL_A
            value: "deepseek-r1:671b"
          - name: AI_MODEL_B
            value: "command-r-plus:latest"
          - name: RAGFLOW_API_URL
            value: "https://your-ragflow-endpoint"
          - name: SECRET_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: SECRET_KEY
          - name: GOOGLE_AI_API_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: GOOGLE_AI_API_KEY
          - name: ANTHROPIC_API_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: ANTHROPIC_API_KEY
          - name: GROQ_API_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: GROQ_API_KEY
          - name: OPENAI_API_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: OPENAI_API_KEY
          - name: RAGIE_API_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: RAGIE_API_KEY
          - name: RAGFLOW_API_KEY
            valueFrom:
              secretKeyRef:
                name: app-secrets
                key: RAGFLOW_API_KEY
        ports:
        - containerPort: 8000
```

---

### 🌐 4. Internal Service

Expose the chatbot internally:

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: chatbot-rag-alliance-service
  namespace: chatbot-rag-alliance
spec:
  selector:
    app: chatbot-rag-alliance
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  type: ClusterIP
```

---

### 🔐 5. TLS Certificate (Optional but Recommended)

Use this only if you’ve configured **cert-manager** with a working ClusterIssuer.

```yaml
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: chat-cluster-paice-ua-com
  namespace: chatbot-rag-alliance
spec:
  secretName: chat-cluster-paice-ua-com-tls
  issuerRef:
    name: letsencrypt-dns # or letsencrypt-prod if using HTTP challenge
    kind: ClusterIssuer
  commonName: chat.cluster.paice-ua.com
  dnsNames:
    - chat.cluster.paice-ua.com
```

---

### 🌍 6. Ingress (Public Access)

```yaml
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: chatbot-rag-alliance-ingress
  namespace: chatbot-rag-alliance
  annotations:
    traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  ingressClassName: traefik
  tls:
  - hosts:
    - chat.cluster.paice-ua.com
    secretName: chat-cluster-paice-ua-com-tls
  rules:
  - host: chat.cluster.paice-ua.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: chatbot-rag-alliance-service
            port:
              number: 8000
```

---

### ✅ 7. Apply Everything

```bash
kubectl apply -f your-deployment.yaml
kubectl get pods -n chatbot-rag-alliance
```

---

### 💡 8. Notes

- Use `kubectl logs` to debug if the pod doesn't start.
- Use `kubectl port-forward` for local testing: `kubectl port-forward svc/chatbot-rag-alliance-service 8000:8000 -n chatbot-rag-alliance`
- Confirm TLS certs via `kubectl describe certificate` if using cert-manager.
- Chat logs are stored in SQLite unless you configure another database.

```bash
# Optional local testing
curl http://localhost:8000
```

--- 

```bash
# If you need to redeploy
kubectl rollout restart deployment chatbot-rag-alliance-deployment -n chatbot-rag-alliance
```
