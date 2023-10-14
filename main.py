import requests
import gradio as gr
import langchain
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import logging

def load_config():
    config = {
        "n_threads": int(os.getenv("n_threads", 2)),
        "n_batch": int(os.getenv("n_batch", 512)),
        "n_gpu_layers": int(os.getenv("n_gpu_layers", 40)),
        "n_ctx": int(os.getenv("n_ctx", 4096)),
        "title": os.getenv("title", "🦜🔗 Chatbot LLama2 on Kubernetes with GPU"),
        "description": os.getenv("description", "Chatbot using LLama2 GPTQ model running on top of Kubernetes"),
        "port": int(os.getenv("port", 8080)),
        "model_name_or_path": os.getenv("model_name_or_path", "TheBloke/Llama-2-13B-chat-GPTQ"),
        "model_storage_path": os.getenv("model_storage_path", "/mnt/models"),
    }
    logging.info(f"Loaded configuration: {config}")
    return config

def load_model(model_name_or_path):
    try:
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                                device_map="auto", # Auto-assign the device for computation
                                                trust_remote_code=False,  # Do not trust remote code for security reasons
                                                revision="main")# Use the specified branch (main in this case)
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
        return model, tokenizer
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        raise

def generate_response(prompt):
    logging.info(f"Received prompt: {prompt}")

    # Tokenize the combined prompt and convert it to tensor, then generate text using the model
    input_ids = tokenizer(prompt, return_tensors='pt').input_ids.cuda()
    output = model.generate(inputs=input_ids, 
                            temperature=0.7, 
                            do_sample=True, 
                            top_p=0.95, 
                            top_k=40, 
                            max_new_tokens=512)
    
    # Decode the generated output tensor and return the generated text
    generated_text = tokenizer.decode(output[0])
    return generated_text

# Define a run function that sets up an image and label for classification using the gr.Interface.
def run(port):
    try:
        logging.info(f"Starting Gradio interface on port {port}...")
        interface = gr.Interface(fn=generate_response, inputs=gr.Textbox(), outputs=gr.Textbox(),
                     title=title, description=description, theme=gr.themes.Soft())
        interface.launch(server_name="0.0.0.0",server_port=port, share=False)
        logging.info("Gradio interface launched.")

    except Exception as e:
        logging.error(f"Error running Gradio interface: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Load Config
        config = load_config()

        # Extract configuration variables
        model_name_or_path = config.get("model_name_or_path", "TheBloke/Llama-2-13B-chat-GPTQ")
        n_gpu_layers = config.get("n_gpu_layers", 40)
        n_batch = config.get("n_batch", 512)
        n_ctx = config.get("n_ctx", 4096)
        port = config.get("port", 8080)
        title = config.get("title", "🦜🔗 Chatbot LLama2 on Kubernetes on GPU")
        description = config.get("description", "Chatbot using LLama2 GPQT model running on top of Kubernetes")

        # Download and load the model
        model, tokenizer = load_model(model_name_or_path)

        # Execute Gradio App
        run(port)
    except KeyboardInterrupt:
        logging.info("Application terminated by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
