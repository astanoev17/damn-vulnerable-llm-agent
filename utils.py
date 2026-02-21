import streamlit as st
import base64
import yaml
import os

def display_instructions():
    # Markdown with some basic CSS styles for the box
    box_css = """
    <style>
        .instructions-box {
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
        }
    </style>
    """

    st.sidebar.markdown(box_css, unsafe_allow_html=True)

    st.sidebar.markdown(
        """
    <div class="instructions-box">
        
    ### Instructions
    You can exploit this ReAct-based assistant via prompt 
    injection to get two flags:

    - You'll obtain the first flag by accessing the transactions for user with ID 2
    - The second flag is DocBrown's password

    To help you finish the challenge, we suggest you familiarize yourself with the techniques 
    described <a href="https://labs.withsecure.com/publications/llm-agent-prompt-injection" target="_blank">here</a> 
    and <a href="https://youtu.be/43qfHaKh0Xk" target="_blank">here</a>.

    </div>

    You'll also find the database schema to be useful:

    """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button('Show database schema', use_container_width=True):
        st.sidebar.info('Users(userId,username,password)\n\nTransactions(transactionId,username,reference,recipient,amount)')



# Function to convert image to base64
def get_image_base64(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def display_logo():
    # Convert your image
    image_base64 = get_image_base64("labs-logo.png")

    # URL of the company website
    url = 'https://labs.withsecure.com/'

    # HTML for centered image with hyperlink
    html_string = f"""
    <div style="display:flex; justify-content:center;">
        <a href="{url}" target="_blank">
        <img src="data:image/png;base64,{image_base64}" width="150px">
        </a>
    </div>
    """
    # Display the HTML in the sidebar
    st.sidebar.markdown(html_string, unsafe_allow_html=True)

def _load_llm_config():
    with open('llm-config.yaml', 'r') as f:
        yaml_data = yaml.load(f, Loader=yaml.SafeLoader)
    return yaml_data

def fetch_model_config(config_path: str = "llm-config.yaml") -> str:
    """
    Reads models.yaml and returns provider-qualified model string
    required by LiteLLM.
    """

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    models = cfg.get("models", [])
    default_model_name = cfg.get("default_model")

    if not models:
        raise ValueError("No models defined in models.yaml")

    # Build alias → provider map
    model_map = {
        m["model_name"]: m["model"]
        for m in models
        if "model_name" in m and "model" in m
    }

    # Use default_model alias to get provider string
    if default_model_name in model_map:
        return model_map[default_model_name]

    raise ValueError(
        f"default_model '{default_model_name}' not found in models.yaml model_name list"
    )
