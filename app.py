import html

import pandas as pd
import streamlit as st

from gemini_service import CustomerSupportGenerator


# ---------------------------------------------------------
# 1. Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="ReplyPilot AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# 2. Custom page styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0;
        }

        .sub-title {
            color: #667085;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }

        .response-box {
            background-color: #f6f8fa;
            border-left: 5px solid #4f46e5;
            border-radius: 8px;
            padding: 20px;
            color: #1f2937;
            font-size: 1rem;
            line-height: 1.7;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# 3. Load and cache the Gemini + retrieval service
# ---------------------------------------------------------

@st.cache_resource
def load_response_generator():
    """
    Load the Gemini client and conversation retriever once.
    """

    api_key = st.secrets["GEMINI_API_KEY"]

    return CustomerSupportGenerator(
        api_key=api_key
    )


try:
    response_generator = (
        load_response_generator()
    )

except KeyError:
    st.error(
        "GEMINI_API_KEY was not found. "
        "Add it to .streamlit/secrets.toml."
    )
    st.stop()

except Exception as error:
    st.error(
        "The application could not initialize."
    )

    with st.expander(
        "Technical error details"
    ):
        st.write(error)

    st.stop()


# ---------------------------------------------------------
# 4. Initialize session state
# ---------------------------------------------------------

if "generation_result" not in st.session_state:
    st.session_state.generation_result = None

if "submitted_message" not in st.session_state:
    st.session_state.submitted_message = ""


# ---------------------------------------------------------
# 5. Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.title("💬 ReplyPilot AI")

    st.write(
        "An AI-assisted customer-support "
        "response generator."
    )

    st.divider()

    st.subheader("How it works")

    st.markdown(
        """
        1. Enter a customer message.
        2. Retrieve similar support cases.
        3. Send contextual examples to Gemini.
        4. Generate a suggested reply.
        5. Review the response before sending.
        """
    )

    st.divider()

    st.subheader("Technology")

    st.write(
        "**Interface:** Streamlit"
    )

    st.write(
        "**LLM:** Gemini 3.1 Flash-Lite"
    )

    st.write(
        "**Retrieval:** TF-IDF"
    )

    st.write(
        "**Similarity:** Cosine similarity"
    )

    st.write(
        "**Dataset:** Real support conversations"
    )

    st.divider()

    st.warning(
        "AI-generated responses must be reviewed "
        "by a human support agent."
    )


# ---------------------------------------------------------
# 6. Main heading
# ---------------------------------------------------------

st.markdown(
    '<p class="main-title">ReplyPilot AI</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class="sub-title">
        Generate professional and context-aware
        customer-support replies using real historical
        conversations and Gemini.
    </p>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# 7. Dashboard metrics
# ---------------------------------------------------------

metric_one, metric_two, metric_three = (
    st.columns(3)
)


with metric_one:
    dataset_record_count = len(
        response_generator.retriever.dataset
    )

    st.metric(
        label="Dataset Records",
        value=f"{dataset_record_count:,}"
    )


with metric_two:
    st.metric(
        label="Examples Retrieved",
        value="3"
    )


with metric_three:
    st.metric(
        label="Generative Model",
        value="Gemini Flash-Lite"
    )


st.divider()


# ---------------------------------------------------------
# 8. Customer-message input form
# ---------------------------------------------------------

st.subheader(
    "Generate a Support Response"
)


with st.form(
    "customer_support_form"
):
    tone = st.selectbox(
        "Response tone",
        options=[
            "Professional",
            "Friendly",
            "Empathetic"
        ],
        help=(
            "Select the communication style "
            "for the generated response."
        )
    )

    customer_message = st.text_area(
        "Customer message",
        height=180,
        placeholder=(
            "Example: My order should have "
            "arrived five days ago, but I still "
            "have not received it."
        ),
        help=(
            "Do not enter real customer names, "
            "email addresses, phone numbers or "
            "payment information."
        )
    )

    submitted = st.form_submit_button(
        "Generate AI Response",
        type="primary",
        use_container_width=True
    )


# ---------------------------------------------------------
# 9. Generate the customer-support response
# ---------------------------------------------------------

if submitted:

    cleaned_customer_message = (
        customer_message.strip()
    )

    if not cleaned_customer_message:
        st.warning(
            "Please enter a customer message."
        )

    elif len(cleaned_customer_message) < 10:
        st.warning(
            "Please enter a more detailed "
            "customer message."
        )

    else:
        try:
            with st.spinner(
                "Retrieving similar cases and "
                "generating a response..."
            ):
                result = (
                    response_generator
                    .generate_response(
                        customer_message=(
                            cleaned_customer_message
                        ),
                        tone=tone
                    )
                )

            st.session_state.generation_result = (
                result
            )

            st.session_state.submitted_message = (
                cleaned_customer_message
            )

        except Exception as error:
            st.error(
                "The response could not be generated. "
                "Please check the API connection "
                "and try again."
            )

            with st.expander(
                "Technical error details"
            ):
                st.write(error)


# ---------------------------------------------------------
# 10. Display the generation result
# ---------------------------------------------------------

result = st.session_state.generation_result


if result:
    st.divider()

    st.subheader(
        "Generation Result"
    )

    (
        response_tab,
        evidence_tab,
        details_tab
    ) = st.tabs(
        [
            "Generated Response",
            "Retrieved Examples",
            "Technical Details"
        ]
    )


    # -----------------------------------------------------
    # Generated-response tab
    # -----------------------------------------------------

    with response_tab:
        safe_generated_response = html.escape(
            result["generated_response"]
        ).replace(
            "\n",
            "<br>"
        )

        st.markdown(
            f"""
            <div class="response-box">
                {safe_generated_response}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Review and edit this response before "
            "sending it to a customer."
        )

        st.download_button(
            label="Download Response",
            data=result["generated_response"],
            file_name=(
                "replypilot_generated_response.txt"
            ),
            mime="text/plain",
            use_container_width=True
        )


    # -----------------------------------------------------
    # Retrieved-examples tab
    # -----------------------------------------------------

    with evidence_tab:
        st.info(
            "These historical conversations were "
            "retrieved from the dataset and supplied "
            "to Gemini as contextual examples."
        )

        retrieved_examples = (
            result["retrieved_examples"]
        )

        evidence_rows = []

        for number, example in enumerate(
            retrieved_examples,
            start=1
        ):
            evidence_rows.append(
                {
                    "Rank": number,
                    "Customer Message": (
                        example["customer_message"]
                    ),
                    "Agent Response": (
                        example["agent_response"]
                    ),
                    "Company": (
                        example["company"]
                    ),
                    "Similarity": (
                        example["similarity_score"]
                    )
                }
            )

        evidence_dataframe = pd.DataFrame(
            evidence_rows
        )

        st.dataframe(
            evidence_dataframe,
            use_container_width=True,
            hide_index=True
        )

        for number, example in enumerate(
            retrieved_examples,
            start=1
        ):
            similarity_score = (
                example["similarity_score"]
            )

            with st.expander(
                f"Retrieved example {number} "
                f"— similarity {similarity_score}"
            ):
                st.write(
                    "**Historical customer message**"
                )

                st.write(
                    example["customer_message"]
                )

                st.write(
                    "**Human agent response**"
                )

                st.write(
                    example["agent_response"]
                )

                st.write(
                    f"**Support account:** "
                    f"{example['company']}"
                )


    # -----------------------------------------------------
    # Technical-details tab
    # -----------------------------------------------------

    with details_tab:
        detail_one, detail_two = (
            st.columns(2)
        )

        with detail_one:
            st.write("**Model**")

            st.code(
                result["model"]
            )

            st.write("**Selected tone**")

            st.code(
                result["tone"]
            )

        with detail_two:
            st.write(
                "**Retrieval method**"
            )

            st.code(
                "TF-IDF"
            )

            st.write(
                "**Similarity method**"
            )

            st.code(
                "Cosine similarity"
            )

        st.write(
            "**Submitted customer message**"
        )

        st.write(
            st.session_state.submitted_message
        )

        st.info(
            "The dataset provides contextual examples. "
            "Gemini generates the final response. "
            "The Gemini model is not trained or "
            "fine-tuned by this application."
        )


# ---------------------------------------------------------
# 11. Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "ReplyPilot AI • Generative AI "
    "Customer Support Application"
)