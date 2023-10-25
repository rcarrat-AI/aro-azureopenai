from langchain.chat_models import AzureChatOpenAI
from langchain.schema import AIMessage, HumanMessage
import os
import openai
import gradio as gr
import logging
import json
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Model Global Variable
model = None

# Only for development
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
        "deployment_name": os.getenv("deployment_name", "gpt-35-turbo"),
        "api_type": os.getenv("api_type", "azure"),
        "api_version": os.getenv("api_version", "2023-05-15"),
        "api_base": os.getenv("api_base", "https://exampleapi.com"),
        "api_key": os.getenv("api_key", "this_needs_to_be_replaced_with_azureopenai_key")
    }
    logging.info(f"Loaded configuration: {config}")
    return config

# Load the Azure OpenAI Model using LangChain
def load_model(api_type, api_version, api_base, api_key, deployment_name):
    global model  # Declare that you are using the global model variable
    try:
        # Callbacks support token-wise streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        logging.info(f"Preparing model")
        # Checking if openai.api_base and openai.api_key are defined and not empty
        if hasattr(openai, 'api_base') and openai.api_base and hasattr(openai, 'api_key') and openai.api_key:
            model = AzureChatOpenAI(
                openai_api_base=openai.api_base,
                openai_api_version=api_version,
                deployment_name=deployment_name,
                openai_api_key=openai.api_key,
                openai_api_type=api_type,
            )
        else:
            # If openai.api_base or openai.api_key is not defined or empty, use api_base and api_key variables
            model = AzureChatOpenAI(
                openai_api_base=api_base,
                openai_api_version=api_version,
                deployment_name=deployment_name,
                openai_api_key=api_key,
                openai_api_type=api_type,
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

if __name__ == "__main__":
    try:
        # Load Config
        config = load_config()

        # Extract configuration variables
        title = config.get("title", "Azure OpenAI App running in Azure Red Hat OpenShift")
        description = config.get("description", "Azure OpenAI App running in Azure Red Hat OpenShift")
        port = config.get("port", 8080)
        deployment_name = config.get("deployment_name", "gpt-35-turbo")
        api_type = config.get("api_type", "azure")
        api_version = config.get("api_version", "2023-05-15")
        api_base =  config.get("api_base", "https://exampleapi.com"),
        api_key = config.get("api_key", "this_needs_to_be_replaced_with_azureopenai_key")

        # Load the Azure OpenAI Model using LangChain
        load_model(api_type, api_version, api_base, api_key, deployment_name)

        # Execute Gradio App
        run(port)
    except KeyboardInterrupt:
        logging.info("Application terminated by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
