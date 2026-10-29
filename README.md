# hasnaaain-GPT-4.2

A custom chatbot built with Streamlit and LangChain. It runs in your browser, asks for your own OpenAI API key when it starts, and keeps a history of your chats in a sidebar.

## Features

* Asks for your OpenAI API key on the first screen and checks it before opening the chat
* Chat history sidebar with a New chat button, the option to switch between chats, and a delete button for each one
* Chats are saved to a local file called `chat_history.json`, so they are still there after a restart
* Replies appear word by word as they are generated
* File upload from the paperclip in the message box: images, PDF files, and text or code files such as txt, md, py, csv and json
* Image questions, so you can ask about a picture you attached
* Regenerate and Retry buttons for the last reply
* Settings for the engine (gpt-4o-mini, gpt-4o, gpt-4.1-mini, gpt-4.1), creativity, personality presets and a custom system role
* Export the current chat as a markdown file
* A light theme with solid colours and slowly moving shapes in the background

## Requirements

* Python 3.9 or newer
* An OpenAI API key from https://platform.openai.com/api-keys
* Streamlit 1.43 or newer, which is needed for file upload inside the message box

## Setup

1. Clone the repository

```
git clone https://github.com/hasnaaain/hasnaaain-GPT-4.2.git
cd hasnaaain-GPT-4.2
```

2. Create a virtual environment (optional but recommended)

```
python -m venv venv
venv\Scripts\activate
```

On macOS or Linux, use `source venv/bin/activate` instead of the second line.

3. Install the packages

```
pip install -r requirements.txt
```

4. Start the app

```
streamlit run Chatgpt.py
```

The app opens at http://localhost:8501.

## Using the app

1. Paste your OpenAI API key on the first screen and press Continue.
2. Type a message at the bottom and press Enter.
3. Use the paperclip next to the message box to attach files. Text and PDF files are kept as context for the whole chat, and images are sent with your message.
4. Open Settings in the sidebar to change the engine, creativity or personality.
5. Press New chat to start a fresh conversation. Older chats stay in the History list.

## Using a .env file (optional)

If you do not want to paste your key every time, create a file named `.env` in the project folder:

```
OPENAI_API_KEY=your_key_here
```

The first screen will then show a button that uses this key. Do not upload the `.env` file to GitHub.

## Theme (optional)

For the intended colours, create a file at `.streamlit/config.toml` with this content:

```
[theme]
base = "light"
primaryColor = "#0F9D8F"
backgroundColor = "#F2FAF9"
secondaryBackgroundColor = "#D8F1EE"
textColor = "#12303B"
font = "sans serif"
```

The colour palette is deep teal for the main elements, coral for accents and sand yellow for highlights on a pale aqua background.

## Notes

* The name hasnaaain-GPT-4.2 is only the display name of the app. The model that answers is the engine you pick in Settings, and the default is gpt-4o-mini.
* Your API key is kept in the browser session only. It is not written to any file.
* `chat_history.json` stores chat text and the names of attached files. It does not store images or the API key.
* Each attached document is cut to 40,000 characters, and the last 30 messages of a chat are sent to the model.

## Files

| File | Purpose |
|---|---|
| `Chatgpt.py` | The whole application |
| `requirements.txt` | Python packages needed to run it |
