# replypilot-ai
A context-aware AI customer support response generator using Gemini, Streamlit, and real-world support conversations.

Project Overview

ReplyPilot AI is a simple Generative AI application designed to help customer support teams create fast, professional, and context-aware replies. The application retrieves similar historical customer-support conversations from a real-world dataset and provides them to the Gemini API as contextual examples. Gemini then generates a new response, which is presented through a Streamlit interface.

This project is being developed as an individual Generative AI application in the customer-support business domain.

Business Problem

Customer support agents frequently spend time answering repetitive questions about deliveries, accounts, payments, cancellations, refunds, and product issues. Slow or inconsistent replies can increase the support workload and reduce customer satisfaction.

ReplyPilot AI assists support agents by generating a suggested response that can be reviewed and edited before it is sent to the customer.

Proposed Workflow

flowchart LR
    A[Customer message] --> B[Retrieve similar cases]
    C[Support dataset] --> B
    B --> D[Gemini API prompt]
    D --> E[Generated reply]
    E --> F[Streamlit dashboard]

Planned Features

Accept a customer inquiry or complaint.

Retrieve similar historical customer-support conversations.

Generate a professional response using the Gemini API.

Allow the user to select a professional, friendly, or empathetic tone.

Display the retrieved examples and generated response.

Allow the generated response to be downloaded.

Remind users that AI-generated replies require human review.

Technologies

Python

Streamlit

Google Gemini API and google-genai

Pandas

Scikit-learn

TF-IDF vectorization and cosine similarity

Kaggle customer-support data

Dataset

The project uses the Customer Support on Twitter dataset. It contains real-world conversations between customers and support accounts from multiple companies.

For this demonstration, the original dataset is cleaned and converted into 1,000 customer-message and agent-response pairs. Usernames, URLs, duplicates, empty messages, and unsuitable records are removed during preprocessing.

The dataset is used for retrieval and contextual grounding. It is not used to train the Gemini model.

Retrieval and Generation Method

Convert historical customer messages into TF-IDF vectors.

Convert the new customer message into the same vector space.

Calculate cosine similarity.

Retrieve the most similar historical conversations.

Add the retrieved examples to the Gemini prompt.

Generate a new customer-support response.

This is a lightweight Retrieval-Augmented Generation style approach. It avoids training a new language model while still using the dataset in the response-generation process.

Current Project Structure

replypilot-ai/
├── data/
│   ├── raw/
│   │   └── twcs.csv
│   └── processed/
│       └── customer_support_pairs.csv
├── .streamlit/
│   └── secrets.toml
├── app.py
├── download_dataset.py
├── prepare_dataset.py
├── requirements.txt
├── .gitignore
└── README.md

Installation

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/replypilot-ai.git
cd replypilot-ai

2. Create a virtual environment

python -m venv .venv

Windows PowerShell:

.venv\Scripts\Activate.ps1

3. Install dependencies

pip install streamlit google-genai pandas scikit-learn requests

4. Download and prepare the dataset

python download_dataset.py
python prepare_dataset.py

5. Configure the Gemini API key

Create .streamlit/secrets.toml and add:

GEMINI_API_KEY = "YOUR_API_KEY_HERE"

Never commit secrets.toml or an API key to GitHub.

6. Run the application

streamlit run app.py

Expected Output

The user enters a customer message and selects a response tone. ReplyPilot AI retrieves relevant historical examples and generates a concise customer-support reply that acknowledges the issue and suggests a suitable next step.

Ethical Considerations

AI-generated replies must be reviewed by a human agent.

The application should not invent order, refund, payment, or delivery details.

Customer personal information should not be entered into the demonstration.

Public social-media data is cleaned to remove usernames and URLs.

The system is an agent-assistance tool, not a fully autonomous decision-maker.

Limitations

Retrieval quality depends on the available dataset sample.

The Gemini API requires an internet connection and an available API quota.

Generated responses may occasionally contain inaccurate information.

The current version primarily supports English customer messages.

Future Improvements

Automatic issue and intent classification

Sentiment detection

Multilingual support, including Sinhala

Company-specific policy documents

Conversation history and response analytics

Human-feedback-based response evaluation

Project Status

This project is currently under development. Dataset download and preprocessing are in progress. The retrieval module, Gemini integration, Streamlit dashboard, evaluation results, screenshots, and final report will be added in the next stages.
