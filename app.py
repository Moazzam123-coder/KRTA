import streamlit as st
import requests
from supabase import create_client

# Supabase setup
SUPABASE_URL = "https://ddjglolzfgrnegkmpyfw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkamdsb2x6ZmdybmVna21weWZ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5MTk0OTUsImV4cCI6MjA1NjQ5NTQ5NX0.W2wrjgXSBlGWOAbmfresB8pLqnQgZhe9TeKAXcK8CwI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# LLaMA API setup
LLAMA_API_URL = "https://api.llama-api.com/chat/completions"
LLAMA_API_TOKEN = "e0ceab0e-b85a-4e6c-b6db-ab526792bc0d"

# Streamlit UI
st.title("KREO Chatbot 🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask me anything about KREO products...")

if user_input:
    # Show user message in chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Fetch FAQ or product info from Supabase
    faq_response = supabase.table("faqs").select("*").ilike("tags", f"%{user_input}%").execute()
    product_response = supabase.table("products").select("*").ilike("name", f"%{user_input}%").execute()
    response_format_response = supabase.table("chatbot_formats").select("*").eq("response_type", "Text").execute()

    faqs = faq_response.data
    products = product_response.data
    response_format = response_format_response.data

    if faqs:
        response_text = response_format[0]["response_template"].format(question=faqs[0]["question"], answer=faqs[0]["answer"])
    elif products:
        response_text = response_format[0]["response_template"].format(name=products[0]["name"], category=products[0]["category"], features=products[0]["features"])
    else:
        response_text = "I couldn't find relevant information. Let me generate a response for you!"

    # Call LLaMA API
    llama_payload = {
        "model": "undefined",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant providing information about Kreo products."},
            {"role": "user", "content": response_text}
        ]
    }
    headers = {
        "Authorization": f"Bearer {LLAMA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    llama_response = requests.post(LLAMA_API_URL, json=llama_payload, headers=headers).json()
    bot_response = llama_response.get("choices", [{}])[0].get("message", {}).get("content", "Error generating response")

    # Show bot response in chat
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
