import os
import streamlit as st

from utils.agent import BedrockAgent
from utils.image import ImageRenderer
from utils.session import generate_session_id
from utils.ui import UiConfig
from utils.auth import Auth
from config_file import Config

ui_conf = UiConfig()


# Streamlit App Layout
st.set_page_config(
    page_title="Bedrock Agent",
    page_icon="���",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title('HR Assistant')
st.info(ui_conf.disclaimer)
st.markdown(ui_conf.custom_css, unsafe_allow_html=True)
# initialise agent
bedrock_agent = BedrockAgent(region='us-east-1',
                             agent_id=os.environ['BEDROCK_AGENT_ID'],
                             agent_alias_id=os.environ['BEDROCK_AGENT_ALIAS_ID'])
image_renderer = ImageRenderer('us-east-1')
authenticator = Auth.get_authenticator(Config.SECRETS_MANAGER_ID)


def logout():
    authenticator.logout()


def main():
    # Authenticate user, and stop here if not logged in
    is_logged_in = authenticator.login()
    if not is_logged_in:
        st.stop()
    with st.sidebar:
        st.text(f"Welcome,\n{authenticator.get_username()}")
        st.button("Logout", "logout_btn", on_click=logout)

    # Initialize chat history
    turn_counter = 0
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"], unsafe_allow_html=True)
        image_renderer.render_s3_image(message["content"], st)

    # Accept user input
    if prompt := st.chat_input("Enter prompt here"):
        turn_counter = turn_counter+1
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": ui_conf.current_time()})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.write(prompt, unsafe_allow_html=True)

        if "session_id" not in st.session_state:
            st.session_state["session_id"] = generate_session_id()
        session_id = st.session_state["session_id"]

        with st.spinner("Agent is researching..."):
            agent_response, ref = bedrock_agent.invoke(prompt, session_id)

        agent_current_time = ui_conf.current_time()
        with st.chat_message("assistant"):
            if ref is not None and turn_counter < 2:
                agent_response += f'[[1]]({ImageRenderer.get_s3_url_from_ref(ref)})'
            st.write(agent_response, unsafe_allow_html=True)
        image_renderer.render_s3_image(agent_response, st)
        st.session_state.messages.append({"role": "assistant",
                                          "content": agent_response, "timestamp": agent_current_time})


# Call the main function to run the app
if __name__ == "__main__":
    main()
