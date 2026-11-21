# Cloud Hosting & Deployment

Aegis can be deployed across modern serverless, PaaS, and container platforms.

---

## 1. 1-Click Deploy to Render

Aegis includes a pre-configured `render.yaml` Blueprint for Render's 100% free web service tier.

1. Fork or clone [TechTonicShift/aegis](https://github.com/TechTonicShift/aegis).
2. Click the Deploy button:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/TechTonicShift/aegis)

Render automatically builds the repository and hosts the web service with HTTPS enabled.

---

## 2. Cloudflare Quick Tunnels (Instant Public Demo)

For temporary live demos and public URL exposure without configuring cloud servers:

```bash
# Start Aegis Gateway
aegis start --port 8000 &

# Start Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8000
```

Cloudflare generates an instant globally routed HTTPS URL:
```text
https://<random-subdomain>.trycloudflare.com/dashboard
```

---

## 3. Kubernetes Helm / Manifest Deployment

Deploy Aegis as an internal ingress proxy inside a Kubernetes cluster:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aegis-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aegis
  template:
    metadata:
      labels:
        app: aegis
    spec:
      containers:
        - name: gateway
          image: techtonicshift/aegis:latest
          ports:
            - containerPort: 8000
          env:
            - name: SIMILARITY_THRESHOLD
              value: "0.85"
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: aegis-secrets
                  key: gemini-api-key
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```
