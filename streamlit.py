import streamlit as st
import replicate
import os

# Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to the DMV chatbot. How may I assist you today?"}]

st.set_page_config(page_title="🚗 DMV Llama 2 Chatbot")
st.title('🚗 DMV Llama 2 Chatbot')

# Replicate Credentials and settings
with st.sidebar:
    st.title('Settings')
    st.write('This DMV chatbot is powered by the Llama 2 LLM model from Meta.')

    # API token input
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
        st.success('API key already provided!', icon='✅')
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if replicate_api:
            os.environ['REPLICATE_API_TOKEN'] = replicate_api
            st.success('Credentials accepted. You can now use the chatbot.', icon='👍')
    
    # Model and parameters selection
    st.subheader('Models and parameters')
    selected_model = st.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    temperature = st.slider('Temperature', 0.01, 5.0, 0.1, 0.01)
    top_p = st.slider('Top P', 0.01, 1.0, 0.9, 0.01)
    max_length = st.slider('Max Length', 32, 512, 120, 8)
    st.markdown('📖 Learn more about this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

    # Button to clear chat history
    if st.button('Clear Chat History'):
        st.session_state.messages = [{"role": "assistant", "content": "Chat history cleared. How may I assist you?"}]

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful DMV assistant. Respond to queries accurately. \n\n"
    for dict_message in st.session_state.messages:
        string_dialogue += f"{dict_message['role'].capitalize()}: {dict_message['content']}\n\n"
    
    # Replace with actual model endpoint
    model_endpoint = 'a16z-infra/llama7b-v2-chat:actual_endpoint' if selected_model == 'Llama2-7B' else 'a16z-infra/llama13b-v2-chat:actual_endpoint'
    output = replicate.run(model_endpoint, 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature": temperature, "top_p": top_p, "max_length": max_length, "repetition_penalty": 1})
    return output

# User-provided prompt
if prompt := st.text_input('Ask a question:'):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = generate_llama2_response(prompt)
    response_text = ''.join(response) if response else "Sorry, I couldn't generate a response."
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Display the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
