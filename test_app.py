from gradio_client import Client
import argparse

# Set up argparse to accept a command-line argument for the client IP address
parser = argparse.ArgumentParser(description="Gradio Client")
parser.add_argument("--url", type=str, required=True, help="URL of the Gradio App")
parser.add_argument("--prompt", type=str, required=True, help="Input Prompt of the user")
args = parser.parse_args()

# Create a Gradio client with the provided IP address
client = Client(args.url)
result = client.predict(
				args.prompt,
				api_name="/predict"
)
print(result)