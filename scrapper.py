import os
import json
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage,SystemMessage,HumanMessage
from dotenv import load_dotenv
load_dotenv()



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

    # JSON file name
    json_file = "user_data.json"

    # Load existing data or initialize a new list
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            data_store = json.load(file)
    else:
        data_store = []

    # Append the new data mapped to the user ID
    data_store.append({"user_id": user_id, "role":"system" ,"content": f"Scarpped data for {link}\n\nDATA:\n{content}"})

    # Save back to the JSON file
    with open(json_file, "w") as file:
        json.dump(data_store, file, indent=4)



PROMPT = """You are a chatbot that will do Question answering and other tasks for the data that has been scrapped.
Check previous chats for this information 
"""
messages = [SystemMessage(PROMPT)]
model = ChatOpenAI(model='gpt-4o-mini')


def chat(user_id,question):
    # JSON file name
    json_file = "user_data.json"

    # Load existing data or initialize a new list
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            data_store = json.load(file)
    else:
        data_store = []

    # Find user by user_id
    if data_store:

        for chat in reversed(data_store):
            if chat["user_id"] == user_id:
                if chat["role"] == "assitant":
                    messages.append(AIMessage(chat["content"]))
                elif chat["role"] == "user":
                    messages.append(HumanMessage(chat["content"]))
                elif chat["role"] == "system":
                    messages.append(SystemMessage(chat["content"]))

    messages.append(HumanMessage(question))

    response =  model.invoke(messages).content

    data_store.append({"user_id": user_id, "role":"user" ,"content": question})
    
    data_store.append({"user_id": user_id, "role":"assitant" ,"content": response})

    # Save back to the JSON file
    with open(json_file, "w") as file:
        json.dump(data_store, file, indent=4)

    return response
