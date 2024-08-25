from sqlalchemy import Column, Integer, String, JSON, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import NoResultFound
import bcrypt
import datetime
import logging
import uuid

# Database setup
DATABASE_URL = "sqlite:///./data/records.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
logger = logging.getLogger(__name__)

# Models
class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    user_id = Column(String, index=True)
    thread_id = Column(String, index=True)
    date_time = Column(Integer)  # Adjust the type as needed
    conversation = Column(JSON)  # Storing the conversation as JSON

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    email=Column(String)
    password = Column(String)  # Using String for hashed passwords

# Create tables
Base.metadata.create_all(bind=engine)

# DBClient class
class DBClient:
    def __init__(self):
        self.db: Session = SessionLocal()
        if not self.get_all_users():
            self.new_user(username="guest", password="", email="")

    def authenticate(self, username: str, password: str) -> bool:
        try:
            user = self.db.query(User).filter(User.username == username).one()
            return bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
        except NoResultFound:
            return False
        
    def generate_user_id(self) -> int:
        all_users = self.get_all_users()
        return len(all_users) + 1

    def get_all_users(self) -> list[User]:
        return self.db.query(User).all()
    
    def new_user(self, username: str, password: str, email: str) -> bool:
        user_id = self.generate_user_id()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, user_id=user_id, password=hashed_password.decode('utf-8'), email=email)
        self.db.add(new_user)
        self.db.commit()
        return True

    def generate_thread_id(self) -> str:
        return str(uuid.uuid4())
    
    def get_password(self, username: str) -> str:
        try:
            user = self.db.query(User).filter(User.username == username).one()
            return user.password
        except NoResultFound:
            return None
        
    def get_user_id_by_username(self, username:str) -> int:
        try:
            user = self.db.query(User).filter(User.username == username).one()
            return int(user.user_id)
        except NoResultFound:
            return None
    
    def get_username_by_user_id(self, user_id:int) -> str:
        try:
            user = self.db.query(User).filter(User.user_id == user_id).one()
            return user.username
        except NoResultFound:
            return None
    
    def is_conversation_by_thread_id(self, thread_id: str) -> bool:
        try:
            self.db.query(Conversation).filter(Conversation.thread_id == thread_id).one()
            return True
        except:
            return False
    def get_conversation_by_thread_id(self, thread_id:str) -> Conversation:
        try:
            conversation = self.db.query(Conversation).filter(Conversation.thread_id == thread_id).one()
            return conversation
        except NoResultFound:
            return None   
    
    def new_conversation(self, username: str, initial_conversation: str, thread_id:str, user_id: int) -> int:
        if self.is_conversation_by_thread_id(thread_id=thread_id):
            return
        new_conversation = Conversation(
            username=username,
            user_id=user_id,  # This would typically be set based on user data
            thread_id=thread_id,  # You might need to generate or set this
            date_time=int(datetime.datetime.now().timestamp()),
            conversation=[{"speaker": username, "audience": "all", "trigger_type": "initial", "content": initial_conversation}]
        )
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)
        return new_conversation.id
    def update_conversation_by_thread_id(self, thread_id: str, message_list:list[dict]) -> None:
        try:
            conversation = self.db.query(Conversation).filter(Conversation.thread_id == thread_id).one()
            conversation.conversation = message_list
            self.db.commit()
        except NoResultFound:
            print("Conversation not found")
    def add_to_conversation_by_thread_id(self, thread_id: str, new_message: dict) -> None:
        try:
            conversation = self.db.query(Conversation).filter(Conversation.thread_id == thread_id).one()
            conversation.conversation.append(new_message)
            self.db.commit()
        except NoResultFound:
            print("Conversation not found")
            
    def add_to_conversation_by_conversation_id(self, conversation_id: int, new_message: dict) -> None:
        try:
            conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).one()
            conversation.conversation.append(new_message)
            self.db.commit()
        except NoResultFound:
            print("Conversation not found")
    
    def delete_all_users(self) -> None:
        self.db.query(User).delete()
        self.db.commit()

    def delete_all_conversations(self) -> None:
        self.db.query(Conversation).delete()
        self.db.commit()


if __name__ == "__main__":
    # Create an instance of the client
    client = DBClient()
    # Authenticate a user
    client.delete_all_users()
    client.delete_all_conversations()

    client = DBClient()
    
    # Create a new user
    client.new_user(username="new_user", password="new_password", email="user@email.com")
    # create a new thread id
    thread_id = client.generate_thread_id()
    # get user_id from user
    user_id = client.get_user_id_by_username(username="new_user")
    # Create a new conversation
    conversation_id = client.new_conversation(
        username="new_user", 
        initial_conversation=[
            {"speaker":"aiko_robertson","audience":"all","trigger_type":"initial","content":"Oh man, it looks like we are stuck here in this elevator, wow this is bad timing"},
            {"speaker":"user","audience":"all","trigger_type":"initial","content":"Oh no, I have a job interview in 10 minutes, if I don't let them know, then I will for sure loose this job"},
            {"speaker":"martin_orchard","audience":"joseph_enriquez","trigger_type":"initial","content":"hey joseph, are you ok? you don't look so well!"},
        ], 
        thread_id = thread_id,
        user_id = user_id
    )
    print("New Conversation ID:", conversation_id)
    # Add a message to the conversation
    client.add_to_conversation_by_conversation_id(
        conversation_id,
        {"speaker": "user", "audience": "all", "trigger_type": "response", "content": "does anyone have a phone?"}
    )