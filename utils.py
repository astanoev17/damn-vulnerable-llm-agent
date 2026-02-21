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

def fetch_model_config(config_path: str = "config.yml") -> str:
    """
    Returns a provider-qualified model string for LiteLLM, e.g.
      - "openai/meta-llama/llama-3.1-8b-instruct"
      - "groq/llama-3.1-8b-instant"
    Supports selecting by friendly model_name via env var MODEL_NAME.
    """

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    models = cfg.get("models", []) or []
    if not models:
        raise ValueError("No models found in config.yml under 'models:'")

    # Build map: model_name -> provider model string
    model_map = {}
    for m in models:
        name = m.get("model_name")
        provider_model = m.get("model")
        if name and provider_model:
            model_map[name] = provider_model

    # Priority: explicit MODEL_NAME -> default_model -> first model
    selected_name = os.getenv("MODEL_NAME") or cfg.get("default_model")
    if selected_name and selected_name in model_map:
        return model_map[selected_name]

    if selected_name and selected_name not in model_map:
        raise ValueError(
            f"Selected model '{selected_name}' not found in config.yml model_name list: {list(model_map.keys())}"
        )

    # fallback
    first = next(iter(model_map.values()))
    return first
