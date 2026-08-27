from pathlib import Path
import tomllib

from google import genai

from retrieval import ConversationRetriever


MODEL_NAME = "gemini-3.1-flash-lite"


class CustomerSupportGenerator:
    """
    Retrieves similar historical conversations and uses
    Gemini to generate a new customer-support response.
    """

    def __init__(
        self,
        api_key,
        dataset_path=(
            "data/processed/"
            "customer_support_pairs.csv"
        )
    ):
        if not api_key:
            raise ValueError(
                "A Gemini API key is required."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.retriever = ConversationRetriever(
            dataset_path=dataset_path
        )

    @staticmethod
    def format_examples(examples):
        """
        Convert retrieved conversations into text that
        can be included in the Gemini prompt.
        """

        formatted_examples = []

        for number, example in enumerate(
            examples,
            start=1
        ):
            formatted_example = f"""
Example {number}

Customer message:
{example["customer_message"]}

Human agent response:
{example["agent_response"]}
"""

            formatted_examples.append(
                formatted_example.strip()
            )

        return "\n\n".join(formatted_examples)

    def generate_response(
        self,
        customer_message,
        tone="Professional"
    ):
        """
        Generate a customer-support response using retrieved
        examples and the Gemini API.
        """

        if not customer_message.strip():
            raise ValueError(
                "The customer message cannot be empty."
            )

        allowed_tones = [
            "Professional",
            "Friendly",
            "Empathetic"
        ]

        if tone not in allowed_tones:
            tone = "Professional"

        similar_conversations = (
            self.retriever
            .retrieve_similar_conversations(
                customer_message=customer_message,
                top_k=3
            )
        )

        historical_examples = self.format_examples(
            similar_conversations
        )

        prompt = f"""
You are a professional customer-support assistant.

Your task is to draft a response to a new customer message.

New customer message:
{customer_message}

Required tone:
{tone}

Relevant historical customer-support examples:
{historical_examples}

Instructions:
1. Acknowledge the customer's concern.
2. Use a {tone.lower()} and helpful tone.
3. Provide a practical next step.
4. Do not invent order numbers, delivery dates, refunds,
   payment details, company policies, or completed actions.
5. Do not mention Twitter, historical examples, retrieval,
   datasets, AI, or Gemini.
6. Do not copy personal details or company-specific promises
   from the historical examples.
7. If more information is required, politely ask the customer
   for the necessary details.
8. Keep the response between 50 and 120 words.
9. Return only the response that should be sent to the customer.
"""

        interaction = self.client.interactions.create(
            model=MODEL_NAME,
            input=prompt
        )

        generated_response = (
            interaction.output_text.strip()
        )

        if not generated_response:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return {
            "generated_response": generated_response,
            "retrieved_examples": similar_conversations,
            "model": MODEL_NAME,
            "tone": tone
        }


def load_local_api_key():
    """
    Load the API key from the local Streamlit secrets file.
    This function is used only for local testing.
    """

    secrets_path = Path(
        ".streamlit/secrets.toml"
    )

    if not secrets_path.exists():
        raise FileNotFoundError(
            "The .streamlit/secrets.toml file "
            "was not found."
        )

    with secrets_path.open("rb") as secrets_file:
        secrets = tomllib.load(secrets_file)

    api_key = secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found in "
            ".streamlit/secrets.toml."
        )

    return api_key


# Run a local Gemini test
if __name__ == "__main__":

    print("Loading the Gemini API key...")

    local_api_key = load_local_api_key()

    print("Initializing ReplyPilot AI...")

    generator = CustomerSupportGenerator(
        api_key=local_api_key
    )

    test_customer_message = (
        "My order should have arrived five days ago, "
        "but I still have not received it. "
        "I am very disappointed."
    )

    print("\nCustomer message:")
    print(test_customer_message)

    print("\nGenerating a response...")

    result = generator.generate_response(
        customer_message=test_customer_message,
        tone="Empathetic"
    )

    print("\nGenerated response:")
    print(result["generated_response"])

    print("\nModel used:")
    print(result["model"])

    print("\nRetrieved examples:")

    for number, example in enumerate(
        result["retrieved_examples"],
        start=1
    ):
        print(
            f"{number}. "
            f"{example['customer_message']} "
            f"(score: {example['similarity_score']})"
        )