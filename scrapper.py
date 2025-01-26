import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://hammadhayat16:Silveraqua6602@cluster0.rawks.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "chatbot_db"
COLLECTION_NAME = "user_chats"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def web_database(user_id, link):
    pages = [link]
    docs = []

    # Load data from the web page
    for data in pages:
        loader = WebBaseLoader(data)
        for doc in loader.load():
            docs.append(doc)

    # Combine the page content
    content = " ".join([page.page_content for page in docs])

    # Store the scrapped data in MongoDB
    scrapped_data = {
        "user_id": user_id,
        "role": "system",
        "content": f"Scrapped data for {link}\n\nDATA:\n{content}"
    }
    collection.insert_one(scrapped_data)


PROMPT = """You are a chatbot that will do Question answering and other tasks for the data that has been scrapped.
Check previous chats for this information 
"""
messages = [SystemMessage(PROMPT)]
model = ChatOpenAI(model='gpt-4o-mini')


def chat(user_id, question):
    # Retrieve user chat history from MongoDB
    chat_history = collection.find({"user_id": user_id}).sort("timestamp", 1)

    for chat in chat_history:
        if chat["role"] == "assistant":
            messages.append(AIMessage(chat["content"]))
        elif chat["role"] == "user":
            messages.append(HumanMessage(chat["content"]))
        elif chat["role"] == "system":
            messages.append(SystemMessage(chat["content"]))

    # Add the user's current question
    messages.append(HumanMessage(question))

    # Get response from the model
    response = model.invoke(messages).content

    # Store the user's question and model's response in MongoDB
    collection.insert_one({"user_id": user_id, "role": "user", "content": question,"timestamp": datetime.now()})
    collection.insert_one({"user_id": user_id, "role": "assistant", "content": response,"timestamp": datetime.now()})

    return response
