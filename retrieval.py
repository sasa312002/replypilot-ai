from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ConversationRetriever:
    """
    Retrieves historical customer-support conversations
    that are similar to a new customer message.
    """

    def __init__(
        self,
        dataset_path="data/processed/customer_support_pairs.csv"
    ):
        self.dataset_path = Path(dataset_path)

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path}"
            )

        # Load the cleaned customer-support dataset
        self.dataset = pd.read_csv(
            self.dataset_path
        )

        required_columns = [
            "customer_message",
            "agent_response",
            "company"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in self.dataset.columns
        ]

        if missing_columns:
            raise ValueError(
                "Dataset is missing these columns: "
                f"{missing_columns}"
            )

        # Remove records containing empty messages
        self.dataset = self.dataset.dropna(
            subset=[
                "customer_message",
                "agent_response"
            ]
        ).reset_index(drop=True)

        self.dataset["customer_message"] = (
            self.dataset["customer_message"]
            .astype(str)
        )

        self.dataset["agent_response"] = (
            self.dataset["agent_response"]
            .astype(str)
        )

        # Create the TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=15_000,
            lowercase=True
        )

        # Convert historical customer messages into vectors
        self.message_vectors = (
            self.vectorizer.fit_transform(
                self.dataset["customer_message"]
            )
        )

        print(
            "Conversation retriever initialized with "
            f"{len(self.dataset):,} records."
        )

    def retrieve_similar_conversations(
        self,
        customer_message,
        top_k=3
    ):
        """
        Return the top-k historical conversations that are
        most similar to the provided customer message.
        """

        if not customer_message.strip():
            return []

        # Convert the new message into a TF-IDF vector
        query_vector = self.vectorizer.transform(
            [customer_message]
        )

        # Calculate similarity with every dataset message
        similarity_scores = cosine_similarity(
            query_vector,
            self.message_vectors
        ).flatten()

        # Get the indices of the highest similarity scores
        top_indices = similarity_scores.argsort()[
            -top_k:
        ][::-1]

        results = []

        for index in top_indices:
            record = self.dataset.iloc[index]

            results.append(
                {
                    "customer_message": (
                        record["customer_message"]
                    ),
                    "agent_response": (
                        record["agent_response"]
                    ),
                    "company": record["company"],
                    "similarity_score": round(
                        float(similarity_scores[index]),
                        4
                    )
                }
            )

        return results


# Test the retrieval module when this file is run directly
if __name__ == "__main__":

    retriever = ConversationRetriever()

    test_message = (
        "My order has not arrived yet and "
        "I want to know the delivery status."
    )

    print("\nTest customer message:")
    print(test_message)

    similar_conversations = (
        retriever.retrieve_similar_conversations(
            customer_message=test_message,
            top_k=3
        )
    )

    print("\nTop three similar conversations:")

    for number, conversation in enumerate(
        similar_conversations,
        start=1
    ):
        print(f"\n--- Result {number} ---")

        print(
            "Historical customer message:",
            conversation["customer_message"]
        )

        print(
            "Historical agent response:",
            conversation["agent_response"]
        )

        print(
            "Company:",
            conversation["company"]
        )

        print(
            "Similarity score:",
            conversation["similarity_score"]
        )