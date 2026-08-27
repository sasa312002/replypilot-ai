import html
import re
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# 1. Locate the original dataset
# ---------------------------------------------------------

raw_data_directory = Path("data/raw")
csv_files = list(
    raw_data_directory.rglob("twcs.csv")
)

if not csv_files:
    raise FileNotFoundError(
        "twcs.csv was not found inside "
        "the data/raw folder."
    )

source_file = csv_files[0]

print(f"Reading dataset from: {source_file}")


# ---------------------------------------------------------
# 2. Load a manageable portion of the original dataset
# ---------------------------------------------------------

columns_to_load = [
    "tweet_id",
    "author_id",
    "inbound",
    "text",
    "in_response_to_tweet_id"
]

rows_to_load = 300_000

tweets = pd.read_csv(
    source_file,
    usecols=columns_to_load,
    nrows=rows_to_load,
    dtype="string",
    encoding_errors="replace",
    on_bad_lines="skip"
)

print(f"Rows loaded: {len(tweets):,}")


# Convert the inbound column to Boolean values
tweets["is_customer_message"] = (
    tweets["inbound"]
    .str.lower()
    .eq("true")
)


# ---------------------------------------------------------
# 3. Separate customer messages and agent responses
# ---------------------------------------------------------

customer_messages = tweets[
    tweets["is_customer_message"]
][
    [
        "tweet_id",
        "text"
    ]
].rename(
    columns={
        "tweet_id": "customer_tweet_id",
        "text": "customer_message"
    }
)


agent_responses = tweets[
    (~tweets["is_customer_message"])
    & tweets["in_response_to_tweet_id"].notna()
][
    [
        "in_response_to_tweet_id",
        "text",
        "author_id"
    ]
].rename(
    columns={
        "text": "agent_response",
        "author_id": "company"
    }
)


print(
    "Customer messages found: "
    f"{len(customer_messages):,}"
)

print(
    "Agent responses found: "
    f"{len(agent_responses):,}"
)


# ---------------------------------------------------------
# 4. Match each agent response with its customer message
# ---------------------------------------------------------

conversation_pairs = agent_responses.merge(
    customer_messages,
    left_on="in_response_to_tweet_id",
    right_on="customer_tweet_id",
    how="inner"
)

conversation_pairs = conversation_pairs[
    [
        "customer_message",
        "agent_response",
        "company"
    ]
]

print(
    "Matched conversation pairs before cleaning: "
    f"{len(conversation_pairs):,}"
)


# ---------------------------------------------------------
# 5. Text-cleaning function
# ---------------------------------------------------------

def clean_text(text):
    """
    Clean a customer message or support-agent response.
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # Convert HTML entities such as &amp;
    text = html.unescape(text)

    # Remove website links
    text = re.sub(
        r"https?://\S+|www\.\S+",
        "",
        text
    )

    # Remove Twitter usernames
    text = re.sub(
        r"@\w+",
        "",
        text
    )

    # Remove agent signatures such as:
    # ^AP, ^SH, 1/2^SH and 1/3^AP
    text = re.sub(
        r"\s*(?:\d+/\d+\s*)?"
        r"\^[A-Za-z]{1,5}\s*$",
        "",
        text
    )

    # Remove repeated punctuation
    text = re.sub(
        r"([!?.,])\1+",
        r"\1",
        text
    )

    # Remove unnecessary spaces before punctuation
    text = re.sub(
        r"\s+([,.!?])",
        r"\1",
        text
    )

    # Replace repeated spaces and line breaks
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# Clean both text columns
conversation_pairs["customer_message"] = (
    conversation_pairs["customer_message"]
    .apply(clean_text)
)

conversation_pairs["agent_response"] = (
    conversation_pairs["agent_response"]
    .apply(clean_text)
)


# ---------------------------------------------------------
# 6. Remove unsuitable records
# ---------------------------------------------------------

conversation_pairs = (
    conversation_pairs
    .dropna(
        subset=[
            "customer_message",
            "agent_response",
            "company"
        ]
    )
)


# Keep messages of a reasonable length
conversation_pairs = conversation_pairs[
    conversation_pairs["customer_message"]
    .str.len()
    .between(15, 500)
]

conversation_pairs = conversation_pairs[
    conversation_pairs["agent_response"]
    .str.len()
    .between(15, 700)
]


# Remove records that became empty after cleaning
conversation_pairs = conversation_pairs[
    conversation_pairs["customer_message"]
    .str.strip()
    .ne("")
]

conversation_pairs = conversation_pairs[
    conversation_pairs["agent_response"]
    .str.strip()
    .ne("")
]


# Remove duplicate conversations
conversation_pairs = (
    conversation_pairs
    .drop_duplicates(
        subset=[
            "customer_message",
            "agent_response"
        ]
    )
    .reset_index(drop=True)
)


print(
    "Conversation pairs after cleaning: "
    f"{len(conversation_pairs):,}"
)


# ---------------------------------------------------------
# 7. Select 5,000 records for the application
# ---------------------------------------------------------

sample_size = min(
    5000,
    len(conversation_pairs)
)

if sample_size == 0:
    raise ValueError(
        "No suitable customer-support "
        "conversation pairs were found."
    )


cleaned_dataset = conversation_pairs.sample(
    n=sample_size,
    random_state=42
).reset_index(drop=True)


# ---------------------------------------------------------
# 8. Save the cleaned dataset
# ---------------------------------------------------------

output_directory = Path(
    "data/processed"
)

output_directory.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    output_directory
    / "customer_support_pairs.csv"
)

cleaned_dataset.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)


# ---------------------------------------------------------
# 9. Display the final result
# ---------------------------------------------------------

print("\nDataset preparation completed!")

print(
    f"Records saved: "
    f"{len(cleaned_dataset):,}"
)

print(
    f"Output file: {output_file}"
)

print("\nFirst five records:")

print(
    cleaned_dataset
    .head()
    .to_string(index=False)
)