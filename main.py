from langchain.chat_models import AzureChatOpenAI
from langchain.schema import AIMessage, HumanMessage
import os
import openai
import gradio as gr
import logging
import json
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

model = None

openai.api_type = "azure"
openai.api_version = "2023-05-15"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")

#log details
openai.log='debug'

def load_config():
    config = {
        "title": os.getenv("title", "Azure OpenAI App running in Azure Red Hat OpenShift"),
        "description": os.getenv("description", "Azure OpenAI App running in Azure Red Hat OpenShift"),
        "port": int(os.getenv("port", 8080)),
    }
    logging.info(f"Loaded configuration: {config}")
    return config

def load_model():
    global model  # Declare that you are using the global model variable
    try:
        # Callbacks support token-wise streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        logging.info(f"Preparing model")
        logging.info("API_BASE",openai.api_base)
        logging.info("API_KEY",openai.api_key)
        # Loading model directly using the specified path
        model = AzureChatOpenAI(
            openai_api_base=openai.api_base,
            openai_api_version="2023-05-15",
            deployment_name="gpt-35-turbo",
            openai_api_key=openai.api_key,
            openai_api_type="azure",
        )
        return model
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        raise

def predict(message, history):
    global model
    if model is None:
        load_model()
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))

    # Call Azure OpenAI API
    azure_response = model(history_langchain_format)

    return azure_response.content

# Define a run function that sets up an image and label for classification using the gr.Interface.
def run(port):
    try:
        logging.info(f"Starting Gradio interface on port {port}...")
        gr.ChatInterface(fn=predict, theme=gr.themes.Soft()).launch(debug=True, share=False)
        logging.info("Gradio interface launched.")

    except Exception as e:
        logging.error(f"Error running Gradio interface: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Load Config
        config = load_config()

        # Extract configuration variables
        title = config.get("title", "Azure OpenAI App running in Azure Red Hat OpenShift")
        description = config.get("description", "Azure OpenAI App running in Azure Red Hat OpenShift")
        port = config.get("port", 8080)

        load_model()

        # Execute Gradio App
        run(port)
    except KeyboardInterrupt:
        logging.info("Application terminated by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
