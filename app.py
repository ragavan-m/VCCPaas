import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd

# MongoDB connection (replace with your actual MongoDB Atlas connection string)
client = MongoClient("mongodb+srv://mragavan0700:9cytmFi5OpWZOpoX@cluster0.wj2bb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['polling_system_db']

# Admin Authentication
ADMIN_PASSWORD = "admin123"  # Set the admin password here

# Initialize session state for authentication and user info
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

def authenticate(password):
    """Check if entered password matches the admin password."""
    return password == ADMIN_PASSWORD

# Function to create a new poll
def create_poll(question, options):
    """Create a new poll in the MongoDB collection."""
    poll_data = {
        "question": question,
        "options": options,
        "votes": {option: 0 for option in options}
    }
    db.polls.insert_one(poll_data)

# Function to retrieve all polls
def get_polls():
    """Fetch all available polls from the MongoDB collection."""
    return list(db.polls.find())

# Function to vote on a poll
def vote_poll(poll_id, option, user_name):
    """Register a vote for a given option in a poll, including user name."""
    # Store who voted for which option (optional)
    db.polls.update_one({"_id": ObjectId(poll_id)}, {"$inc": {f"votes.{option}": 1}})
    db.polls.update_one({"_id": ObjectId(poll_id)}, {"$addToSet": {"voters": user_name}})

# Main Home Page
def show_home_page():
    st.title("Online Polling System")

    # Navigation bar
    nav_option = st.selectbox("Navigate to:", ["Home", "Vote on a Poll", "Admin - Create a Poll"], index=0)

    if nav_option == "Vote on a Poll":
        if st.session_state.user_name:
            show_vote_page()
        else:
            request_user_name()
    elif nav_option == "Admin - Create a Poll":
        if st.session_state.authenticated:
            show_create_poll_page()
        else:
            show_admin_login_page()
    else:
        st.header("Welcome to the Online Polling System!")

def request_user_name():
    """Request the user's name before voting."""
    st.header("User Information")
    name = st.text_input("Enter your name:")
    if st.button("Submit"):
        if name:
            st.session_state.user_name = name
            st.success(f"Welcome, {name}! You can now vote.")
            # Redirect to voting page immediately after name submission
            show_vote_page()  # Call the voting page directly
        else:
            st.error("Please enter your name.")

# Poll Creation Page (Admin)
def show_create_poll_page():
    st.header("Create a New Poll")

    # Use st.form to prevent page refresh issues
    with st.form(key="create_poll_form"):
        poll_question = st.text_input("Enter the poll question:")
        poll_options = st.text_area("Enter the poll options (one option per line)").split("\n")
        
        # Form submit button
        submit_button = st.form_submit_button(label="Create Poll")
        
        if submit_button:
            if poll_question and poll_options:
                create_poll(poll_question, poll_options)
                st.success("Poll created successfully!")
            else:
                st.error("Please enter both a question and options.")

# Poll Voting Page
def show_vote_page():
    st.header("Vote on a Poll")

    # Fetch available polls from the database
    polls = get_polls()

    if polls:
        poll_names = [poll['question'] for poll in polls]
        selected_poll_name = st.selectbox("Select a poll to vote on:", poll_names)

        if selected_poll_name:
            # Find selected poll from the database
            selected_poll = next(poll for poll in polls if poll['question'] == selected_poll_name)
            
            # Show poll options for voting
            option = st.radio("Options:", selected_poll['options'])
            
            if st.button("Vote"):
                vote_poll(selected_poll["_id"], option, st.session_state.user_name)
                st.success(f"Vote cast successfully for option: {option}")

        # Poll results section
        st.header("Poll Results")
        selected_poll_name = st.selectbox("Select a poll to view results:", poll_names, key='results_poll')
        
        if selected_poll_name:
            # Find the poll from the database
            selected_poll = next(poll for poll in polls if poll['question'] == selected_poll_name)
            results = selected_poll["votes"]

            # Display results
            st.write(f"Results for: {selected_poll['question']}")
            df = pd.DataFrame(results.items(), columns=["Option", "Votes"])
            st.bar_chart(df.set_index('Option'))
    else:
        st.write("No polls available.")

# Admin Login Page
def show_admin_login_page():
    st.header("Admin Login")

    password = st.text_input("Enter the admin password:", type="password")

    if st.button("Login"):
        if authenticate(password):
            st.session_state.authenticated = True
            st.success("Login successful!")
            show_create_poll_page()
        else:
            st.error("Incorrect password!")

# Run the app
if __name__ == "__main__":
    show_home_page()
