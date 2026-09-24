# 🤖 LLM-and-ODC
Evaluation of Large Language Models (LLMs) to classify software vulnerability fixes using Orthogonal Defect Classification (ODC).

## 📚 Required Python Libraries
It is highly recommended to use a virtual environment to manage dependencies.

**1. Create the virtual environment:**
In your terminal, run:
`python -m venv .venv`

**2. Activate the virtual environment:**
*   On **Windows**:
    `.venv\Scripts\activate`
*   On **macOS/Linux**:
    `source .venv/bin/activate`

**3. Install dependencies:**
Once the environment is active, run:
`pip install -r requirements.txt`

This command will install all necessary libraries in their respective versions.

## ⚙️ Environment Configuration (.env)
This project connects to a remote API endpoint to access the language models, meaning no local LLM installation is required. 

Create a `.env` file in the root directory of your project to configure the connection and your GitHub token. Here is an example:

```env
GITHUB_TOKEN=github_pat_41552dfhag351
CHAT_ENDPOINT=http://10.20.11.151:80/api/chat
CHAT_API_NAME=johndoe
CHAT_API_PASSWORD=password
```