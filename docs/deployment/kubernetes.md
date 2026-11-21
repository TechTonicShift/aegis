# Kubernetes Production Deployment

For enterprise production deployments, Aegis can be deployed as an internal reverse proxy microservice across a Kubernetes cluster.

---

## 1. Complete Production Manifest (`k8s-aegis.yaml`)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aegis-system

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: aegis-config
  namespace: aegis-system
data:
  PORT: "8000"
  SIMILARITY_THRESHOLD: "0.85"
  EMBEDDER_TYPE: "gemini"
  CACHE_ENABLED: "true"

---
apiVersion: v1
kind: Secret
metadata:
  name: aegis-secrets
  namespace: aegis-system
type: Opaque
stringData:
  GEMINI_API_KEY: "your-gemini-api-key"
  OPENAI_API_KEY: "your-openai-api-key"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aegis-gateway
  namespace: aegis-system
  labels:
    app.kubernetes.io/name: aegis-gateway
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: aegis-gateway
  template:
    metadata:
      labels:
        app.kubernetes.io/name: aegis-gateway
    spec:
      containers:
        - name: gateway
          image: techtonicshift/aegis:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
              name: http
          envFrom:
            - configMapRef:
                name: aegis-config
            - secretRef:
                name: aegis-secrets
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1536Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 5
            timeoutSeconds: 2

---
apiVersion: v1
kind: Service
metadata:
  name: aegis-service
  namespace: aegis-system
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8000
      name: http
  selector:
    app.kubernetes.io/name: aegis-gateway

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aegis-hpa
  namespace: aegis-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aegis-gateway
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 2. Deploying to the Cluster

Apply the configuration manifest:

```bash
kubectl apply -f k8s-aegis.yaml
```

Verify pod health:

```bash
kubectl get pods -n aegis-system
```

Internal cluster services can now route all OpenAI SDK traffic to:
```text
http://aegis-service.aegis-system.svc.cluster.local/v1
```
