# Create an instance of the client
client = DBClient()

# Authenticate a user
is_authenticated = client.authenticate(username="test_user", password="test_password")
print("Authenticated:", is_authenticated)

# Create a new user
client.new_user(username="new_user", password="new_password")

# Get a user's password (hashed)
hashed_password = client.get_password(username="new_user")
print("Hashed Password:", hashed_password)

# Create a new conversation
conversation_id = client.new_conversation(username="new_user", initial_conversation="Initial conversation message")
print("New Conversation ID:", conversation_id)

# Add a message to the conversation
client.add_to_conversation(
    conversation_id,
    {"speaker": "new_user", "audience": "all", "trigger_type": "response", "content": "Response message"}
)
