from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

class Database:
    def __init__(self):
        """Initialize the database connection."""
        self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/InfoLytix"))
        self.db = self.client["InfoLytix"]
        self.users_collection = self.db["users"]
        self.conversations_collection = self.db["conversations"]

    def save_user(self, username, email, password):
        """Save a new user with hashed password."""
        if self.users_collection.find_one({"email": email}):
            return {"status": False, "message": "Email already exists!"}

        hashed_password = generate_password_hash(password)
        self.users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })
        return {"status": True, "message": "Signup successful!"}

    def load_user(self, email, password):
        """Load user details for login."""
        user = self.users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            return {"status": True, "user": user}
        return {"status": False, "message": "Invalid email or password!"}


    def save_chat(self, user_email, convo_id, title, user_msg, bot_msg):
        """Saves user and bot messages to MongoDB along with convo title."""

        current_time = datetime.utcnow()

        message = {
            "user": user_msg,
            "bot": bot_msg,
            "timestamp": current_time
        }

        existing_convo = self.conversations_collection.find_one({"user_email": user_email, "convo_id": convo_id})

        if existing_convo:
            self.conversations_collection.update_one(
                {"user_email": user_email, "convo_id": convo_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": current_time}
                }
            )
        else:
            conversation = {
                "user_email": user_email,
                "convo_id": convo_id,
                "title": title,
                "messages": [message],
                "created_at": current_time,
                "updated_at": current_time
            }
            self.conversations_collection.insert_one(conversation)

        print(f"Saved chat for {user_email} - {convo_id} ✅")

    
    def get_chat_history(self, user_email, convo_id):
        """Retrieve the entire chat history for a particular conversation ID of a specific user."""
        conversation = self.conversations_collection.find_one(
            {"user_email": user_email, "convo_id": convo_id},
            {"_id": 0, "messages": 1}  # Only return messages
        )
        if conversation:
            return {"status": True, "messages": conversation["messages"]}
        return {"status": False, "message": "Conversation not found!"}


    def get_chat_titles(self, user_email):
        """Retrieve all chat titles for a specific user."""
        conversations = self.conversations_collection.find(
            {"user_email": user_email},
            {"_id": 0, "convo_id": 1, "title": 1, "updated_at": 1, "messages": {"$slice": 1}}  # Return only convo_id and title
        ).sort("updated_at", -1)

        chat_titles = list(conversations)
        if chat_titles:
            return {"status": True, "titles": chat_titles}
        return {"status": False, "message": "No conversations found!"}


    def update_conversation_title(self, user_email, convo_id, new_title):
        """Update the title of a specific conversation."""
        result = self.conversations_collection.update_one(
            {"user_email": user_email, "convo_id": convo_id},
            {"$set": {"title": new_title}}
        )
        if result.matched_count:
            return {"status": True, "message": "Title updated successfully!"}
        return {"status": False, "message": "Conversation not found!"}


    def delete_conversation(self, user_email, convo_id):
        """Delete a specific conversation for a user.
        
        Args:
            user_email (str): Email of the user
            convo_id (str): ID of the conversation to delete
            
        Returns:
            dict: Status and message of the operation
        """
        try:
            result = self.conversations_collection.delete_one({
                "user_email": user_email,
                "convo_id": convo_id
            })
            
            if result.deleted_count:
                return {"status": True, "message": "Conversation deleted successfully"}
            return {"status": False, "message": "Conversation not found"}
            
        except Exception as e:
            print(f"Error deleting conversation: {str(e)}")
            return {"status": False, "message": f"Failed to delete conversation: {str(e)}"}

    def get_user_details(self, email):
        """Retrieve user details by email."""
        user = self.users_collection.find_one({"email": email}, {"_id": 0, "password": 0})  # Exclude password
        if user:
            return {"status": True, "user": user}
        return {"status": False, "message": "User not found!"}

    def update_user(self, email, update_data):
        """Update user details (e.g., username, preferences, etc.)."""
        result = self.users_collection.update_one({"email": email}, {"$set": update_data})
        if result.matched_count:
            return {"status": True, "message": "User updated successfully!"}
        return {"status": False, "message": "User not found or update failed!"}

    def delete_user(self, email):
        """Delete a user from the database."""
        result = self.users_collection.delete_one({"email": email})
        if result.deleted_count:
            return {"status": True, "message": "User deleted successfully!"}
        return {"status": False, "message": "User not found!"}

