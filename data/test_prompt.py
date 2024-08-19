from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
prompt = hub.pull("hwchase17/structured-chat-agent")

template = ChatPromptTemplate([
    ("system", "You are a helpful AI bot. Your name is {name}."),
    ("human", "Hello, how are you doing?"),
    ("ai", "I'm doing well, thanks!"),
    ("human", "{user_input}"),
])
prompt_value = template.invoke(
    {
        "name": "Bob",
        "user_input": "What is your name?"
    }
)
breakpoint()