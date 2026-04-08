import streamlit as st
from group_chat import user, manager, notification_agent
import random
import string
import re # <-- Added for script extraction

# Page config — must be first Streamlit call
st.set_page_config(page_title="MTOR - Intelligent, Script-Driven Support", page_icon="🤖", layout="centered")

# Ticket generator
def generate_ticket_id(prefix="TKT", length=6):
    """Generate a random alphanumeric ticket ID."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}-{suffix}"

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title and subtitle block
st.markdown("""
<div class="title-container">
    <h1>🤖 MTOR - Intelligent, Script-Driven Support</h1>
</div>
<div class="subtitle">Your Personalized AI IT Support Assistant</div>
<div class="description"><em>Facing a tech issue? Describe it below and let MTOR handle it for you.</em></div>
""", unsafe_allow_html=True)

# Session state setup
if "final_response" not in st.session_state:
    st.session_state.final_response = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "awaiting_feedback" not in st.session_state:
    st.session_state.awaiting_feedback = False
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

# Input section
st.markdown('<div class="input-label">💬 <strong>Describe your IT issue:</strong></div>', unsafe_allow_html=True)
user_input = st.text_area("", value=st.session_state.user_input, height=150, placeholder="e.g. My VPN keeps disconnecting every 10 minutes...")

# Submit logic
if st.button("🚀 Resolve Now") and user_input.strip():
    with st.spinner("MTOR is resolving your issue..."):
        st.session_state.user_input = user_input
        responses = []

        original_receive = user.receive

        def receive_and_capture(*args, **kwargs):
            if len(args) >= 2:
                message = args[0]
                if isinstance(message, dict):
                    content = message.get("content", "")
                    if content:
                        responses.append(content)
            return original_receive(*args, **kwargs)

        user.receive = receive_and_capture
        user.initiate_chat(recipient=manager, message=user_input)
        user.receive = original_receive

        if responses:
            final = responses[-1]
            st.session_state.final_response = final
            st.session_state.awaiting_feedback = True
            st.session_state.feedback_given = False
            
            st.success("✅ **AI Response:**")
            
            # Use Regex to remove the tags from the displayed text so they are hidden from the user
            display_text = re.sub(r'<SCRIPT_BAT>.*?</SCRIPT_BAT>', '', final, flags=re.DOTALL)
            display_text = re.sub(r'<SCRIPT_SH>.*?</SCRIPT_SH>', '', display_text, flags=re.DOTALL)
            st.markdown(display_text.strip())

            # --- SCRIPT EXTRACTION & DOWNLOAD BUTTONS ---
            # Check for Windows Batch script
            bat_match = re.search(r'<SCRIPT_BAT>(.*?)</SCRIPT_BAT>', final, re.DOTALL)
            if bat_match:
                script_content = bat_match.group(1).strip()
                st.info("⚡ **Auto-Fix Script Available!** Download and run this file to fix your issue automatically.")
                st.download_button(
                    label="⬇️ Download Windows Fix (.bat)",
                    data=script_content,
                    file_name="supportx_autofix.bat",
                    mime="text/plain"
                )

            # Check for Mac/Linux Shell script
            sh_match = re.search(r'<SCRIPT_SH>(.*?)</SCRIPT_SH>', final, re.DOTALL)
            if sh_match:
                script_content = sh_match.group(1).strip()
                st.info("⚡ **Auto-Fix Script Available!** Download and run this file in your terminal to fix your issue automatically.")
                st.download_button(
                    label="⬇️ Download Mac/Linux Fix (.sh)",
                    data=script_content,
                    file_name="supportx_autofix.sh",
                    mime="text/plain"
                )
            # --------------------------------------------

        else:
            st.warning("⚠️ No response received from the agents.")

# Feedback section
if st.session_state.awaiting_feedback and st.session_state.final_response and not st.session_state.feedback_given:
    # Open the glassmorphism feedback container
    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
    
    st.markdown("### 🙋 Was this solution helpful?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, issue resolved"):
            st.session_state.feedback_given = True
            st.session_state.awaiting_feedback = False
            st.success("🎉 Great! We're glad your issue is resolved. Thank you!")

    with col2:
        if st.button("❌ No, not helpful"):
            st.session_state.feedback_given = True
            st.session_state.awaiting_feedback = False
            ticket_id = generate_ticket_id()
            
            st.warning("⚠️ We're escalating this issue to IT support.")
            st.markdown(f"<div class='ticket-id'>📄 Ticket Created: {ticket_id}</div>", unsafe_allow_html=True)

            # Compose escalation message
            notification_message = (
                f"🚨 Unresolved IT Issue\n\n"
                f"User reported: '{st.session_state.user_input}'\n"
                f"📄 Ticket ID: {ticket_id}"
            )

            reply = notification_agent.generate_reply(
                messages=[{"role": "user", "content": notification_message}],
                sender=user
            )

            final_reply = reply.get("content") if isinstance(reply, dict) else str(reply)
            st.info(f"📨 **Notification Agent Response:**\n\n{final_reply}")
            
    # Close the glassmorphism feedback container
    st.markdown('</div>', unsafe_allow_html=True)