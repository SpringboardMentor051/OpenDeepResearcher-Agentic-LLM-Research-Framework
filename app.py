import streamlit as st
import uuid
from opensearch.planner import Planner
from opensearch.searcher import Searcher
from opensearch.writer import Writer

# Configure the Streamlit page
st.set_page_config(page_title="OpenDeepResearcher", page_icon="🔍", layout="wide")

# --- 1. Session State Initialization ---
# Store all conversations in a dictionary. 
# Format: { "chat_id": {"title": "Chat Title", "messages": [ {role, content, sources} ]} }
if "all_chats" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state.all_chats = {initial_id: {"title": "New Chat", "messages": []}}
    st.session_state.current_chat_id = initial_id

# Grab the current active chat to display
current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
messages = current_chat["messages"]

# --- 2. Sidebar: Chat History & New Chat ---
with st.sidebar:
    st.title("🔍 OpenDeepResearcher")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        # Create a fresh chat and set it as current
        st.session_state.all_chats[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.divider()
    st.markdown("### Past Chats")
    
    # Display buttons for all past chats (Reversed so newest is at the top)
    for chat_id, chat_data in reversed(st.session_state.all_chats.items()):
        # Add a green circle to indicate which chat is currently active
        is_active = chat_id == st.session_state.current_chat_id
        btn_label = f"🟢 {chat_data['title']}" if is_active else f"💬 {chat_data['title']}"
        
        if st.button(btn_label, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun() # Refresh screen to load the clicked chat

# --- 3. Main Chat Area ---
# Change the main title based on the chat name
st.title(current_chat["title"] if current_chat["title"] != "New Chat" else "Research Chat")

# Display current chat's history
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("View Raw Sources"):
                for idx, res in enumerate(message["sources"]):
                    st.markdown(f"**{idx+1}. {res.get('title', 'Untitled')}**")
                    st.write(f"🔗 {res.get('url', 'No URL')}")
                    st.caption(res.get('content', '')[:200] + "...")

# --- 4. Chat Input & Processing ---
if topic := st.chat_input("Enter a research topic (e.g., Latest advancements in quantum computing)"):
    
    # Automatically rename "New Chat" to the first query you type
    if current_chat["title"] == "New Chat":
        # Keep the title short for the sidebar (max 30 characters)
        new_title = topic[:30] + "..." if len(topic) > 30 else topic
        st.session_state.all_chats[st.session_state.current_chat_id]["title"] = new_title

    # Display user message
    st.chat_message("user").markdown(topic)
    messages.append({"role": "user", "content": topic})

    # Generate Assistant response
    with st.chat_message("assistant"):
        with st.status("Running Research Agents...", expanded=True) as status:
            
            st.write("🤖 Initializing agents...")
            planner = Planner()
            searcher = Searcher()
            writer = Writer()

            st.write("🧠 Generating search queries...")
            queries = planner.plan(topic)
            for q in queries:
                st.markdown(f"- *{q}*")

            st.write("🌐 Searching the web (Tavily)...")
            search_results = searcher.search_many(queries)
            st.write(f"✅ Found {len(search_results)} relevant sources.")

            st.write("✍️ Drafting summary...")
            summary = writer.summarize(topic, search_results)
            
            status.update(label="Research Complete!", state="complete", expanded=False)

        # Display final summary
        st.markdown(summary)
        
        # Display sources
        
        with st.expander("View Raw Sources"):
            for idx, res in enumerate(search_results): # (or message["sources"] for the top one)
                st.markdown(f"**{idx+1}. {res.get('title', 'Untitled')}**")
                st.write(f"🔗 {res.get('url', 'No URL')}")
                st.write(res.get('content', 'No content available.'))

        # Save assistant message
        messages.append({
            "role": "assistant", 
            "content": summary,
            "sources": search_results
        })
        
        # Sync the updated messages back into the main dictionary
        st.session_state.all_chats[st.session_state.current_chat_id]["messages"] = messages
        
        # Rerun to update the sidebar title immediately
        st.rerun()