import os
import openai
import gradio as gr
import logging
import json
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import AIMessage, HumanMessage

# Model Global Variable
model = None

# Grab OpenAI API Base and API Key
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")

#log details
openai.log='debug'

# Load Config
def load_config():
    config = {
        "title": os.getenv("title", "Azure OpenAI App running in Azure Red Hat OpenShift"),
        "description": os.getenv("description", "Azure OpenAI App running in Azure Red Hat OpenShift"),
        "port": int(os.getenv("port", 8080)),
        "deployment_name": os.getenv("deployment_name", "gpt-35-turbo"),
        "api_type": os.getenv("api_type", "azure"),
        "api_version": os.getenv("api_version", "2023-05-15")
    }
    logging.info(f"Loaded configuration: {config}")
    return config

# Load the Azure OpenAI Model using LangChain
# TODO: Add variable to control temperature, max_tokens, top_p, and frequency_penalty
def load_model(api_type, api_version, deployment_name):
    global model  # Declare that you are using the global model variable
    try:
        # Callbacks support token-wise streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        logging.info(f"Preparing model")
        # Loading model directly using the specified path
        model = AzureChatOpenAI(
            openai_api_base=openai.api_base,
            openai_api_version=api_version,
            deployment_name=deployment_name,
            openai_api_key=openai.api_key,
            openai_api_type=api_type,
        )
        return model
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        raise

# Create a predict function that takes in a message as input and outputs a prediction.
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
        chat_interface = gr.ChatInterface(
            fn=predict, 
            theme=gr.themes.Soft(),
            title=title,
            description=description
        )

        chat_interface.launch(
            debug=True, 
            share=False, 
            server_name="0.0.0.0", 
            server_port=port
        )
        logging.info("Gradio interface launched.")

    except Exception as e:
        logging.error(f"Error running Gradio interface: {str(e)}")
        raise

# Main
if __name__ == "__main__":
    try:
        # Load Config
        config = load_config()

        # Extract configuration variables
        title = config.get("title", "Azure OpenAI App running in Azure Red Hat OpenShift")
        description = config.get("description", "Created & Maintained by Roberto Carratalá @ Red Hat")
        port = config.get("port", 8080)
        deployment_name = config.get("deployment_name", "gpt-35-turbo")
        api_type = config.get("api_type", "azure")
        api_version = config.get("api_version", "2023-05-15")

        # Load the Azure OpenAI Model using LangChain
        load_model(api_type, api_version, deployment_name)

        # Execute Gradio App
        run(port)
    except KeyboardInterrupt:
        logging.info("Application terminated by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")