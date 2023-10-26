# Azure OpenAI ARO Application

Repository for Deploy A Gradio App with Azure OpenAI as a backend LLM within Azure Red Hat OpenShift (ARO) cluster.

![Azure OpenAI App within ARO Cluster](./assets/aro-azureopenai.png)

## Add Azure OpenAI credentials into Kubernetes secrets

* First, set your environment variables with the plain text values in your terminal:

```md
export base_url="https://MY_FANCY_URL.openai.azure.com/"
export api_key="your-api-key"
export namespace="aro-azureopenai"
```

* create a Secret YAML file with base64-encoded values using echo and base64:

```md
echo -n "$BASE_URL" | base64
echo -n "$API_KEY" | base64
```

* Deploy the secret in the namespace

```md
cat <<EOF | kubectl apply -n $NAMESPACE -f -
apiVersion: v1
kind: Secret
metadata:
  name: azure-openai
type: Opaque
data:
  base_url: $(echo -n "$base_url" | base64)
  api_key: $(echo -n "$api_key" | base64)
EOF
```

## Local Development

* Export OPENAI_API_BASE and OPEN_API_KEY:

```md
export OPENAI_API_BASE="xxx"
export OPENAI_API_KEY="xxx"
```

* Run the main python program:

```md
python main.py
```