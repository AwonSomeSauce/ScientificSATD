import os
import json
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from openai import OpenAI


def initialize_openai_client():
    """
    Initialize the OpenAI API client with the API key from the environment variable.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")


def retrieve_gpt_responses(response_id):
    """
    Retrieve the GPT responses from the batch output file.
    """
    client = OpenAI(organization="org-t0BfEZys25Afw0bMxsVMwPDD")
    output_file_id = client.batches.retrieve(response_id).output_file_id
    content = client.files.content(output_file_id)

    with open("requests_output.jsonl", "wb") as file:
        file.write(content.content)


def load_jsonl_data(jsonl_file):
    """
    Load data from a JSONL file.
    """
    data = []
    with open(jsonl_file, "r") as file:
        for line in file:
            data.append(json.loads(line))
    return data


def parse_content(content):
    """
    Clean and parse the content from the markdown code block.
    """
    try:
        clean_content = content.replace("```json\n", "").replace("\n```", "").strip()
        return json.loads(clean_content)
    except json.JSONDecodeError:
        return {}


def update_dataframe_with_predictions(data, df):
    """
    Update the DataFrame with GPT predictions.
    """
    for item in data:
        custom_id = item["custom_id"]
        content = parse_content(
            item["response"]["body"]["choices"][0]["message"]["content"]
        )
        if custom_id in df["Custom_ID"].values:
            df.loc[df["Custom_ID"] == custom_id, "gpt_prediction"] = (
                json.dumps(content["impacts_science"]) if content else None
            )
        else:
            print("Custom_ID not found in DataFrame.")

    df["gpt_prediction"] = df["gpt_prediction"].str.replace('"', "")
    df.to_csv("ctsm_issues_labelled.csv", index=False)


def calculate_metrics(df):
    """
    Calculate and print accuracy, precision, recall, and F1 score.
    """
    accuracy = accuracy_score(df["impacts_science"], df["gpt_prediction"])
    precision = precision_score(
        df["impacts_science"], df["gpt_prediction"], pos_label="yes"
    )
    recall = recall_score(df["impacts_science"], df["gpt_prediction"], pos_label="yes")
    f1 = f1_score(df["impacts_science"], df["gpt_prediction"], pos_label="yes")

    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")


def main():
    initialize_openai_client()

    response_id = "get_response_id"  # replace with your actual response ID
    retrieve_gpt_responses(response_id)

    data = load_jsonl_data("requests_output.jsonl")

    # Assuming 'filtered_df' is available. Load it if necessary.
    df = pd.read_csv("filtered_df.csv")

    update_dataframe_with_predictions(data, df)
    calculate_metrics(df)


if __name__ == "__main__":
    main()
