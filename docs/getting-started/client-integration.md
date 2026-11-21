# Client SDK Integration Guide

Because Aegis implements the standard OpenAI REST specification, migrating your applications requires **zero code rewrites**—simply redirect the API base URL to your Aegis instance (`http://localhost:8000/v1`).

---

## 1. Official OpenAI Python SDK

=== "OpenAI v1.0+"

    ```python
    import os
    from openai import OpenAI

    # Redirect client to Aegis Gateway
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key=os.getenv("OPENAI_API_KEY", "dummy-key-handled-by-aegis")
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful software architect."},
            {"role": "user", "content": "How do I configure Docker container networking?"}
        ]
    )

    print("Response:", response.choices[0].message.content)
    ```

=== "Async OpenAI Client"

    ```python
    import asyncio
    from openai import AsyncOpenAI

    async def main():
        client = AsyncOpenAI(
            base_url="http://localhost:8000/v1",
            api_key="dummy-key"
        )
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Explain B-tree database indexing."}]
        )
        print(response.choices[0].message.content)

    asyncio.run(main())
    ```

---

## 2. LangChain Integration

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_base="http://localhost:8000/v1",
    openai_api_key="dummy-key-handled-by-aegis",
    temperature=0.0
)

# Semantic caching works transparently across all chains and agents
result = llm.invoke("What are decorators in Python?")
print(result.content)
```

---

## 3. LlamaIndex Integration

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(
    model="gpt-4o-mini",
    api_base="http://localhost:8000/v1",
    api_key="dummy-key-handled-by-aegis"
)

response = llm.complete("Compare REST versus GraphQL architecture.")
print(response.text)
```

---

## 4. Node.js & TypeScript (OpenAI SDK)

```typescript
import OpenAI from "openai";

const openai = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "dummy-key",
});

async function run() {
  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: "How do I reset my account password?" }],
  });

  console.log(completion.choices[0].message.content);
}

run();
```

---

## 5. Raw HTTP (cURL)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "How do I reset my password?"}
    ]
  }' -i
```

Notice the response headers returned by Aegis:
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Aegis-Cache: HIT
X-Aegis-Provider: aegis_semantic_cache
X-Aegis-Latency-Ms: 0.18
```
