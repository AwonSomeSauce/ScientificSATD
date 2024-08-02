import os
import re
import json
import pandas as pd
from tqdm import tqdm
from openai import OpenAI


def initialize_openai_client():
    """
    Initialize the OpenAI API client with the API key from the environment variable.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")


def preprocess_description(description):
    """
    Preprocess the issue description by converting to lower case, stripping whitespace,
    replacing multiple whitespaces with a single space, and removing sequences of 3 or
    more non-alphanumeric characters.
    """
    if not isinstance(description, str):
        return ""

    description = description.lower().strip()
    description = re.sub(r"\s+", " ", description)
    description = re.sub(r"[^a-zA-Z0-9\s]{3,}", "", description)

    return description


def write_requests_to_jsonl(filtered_df, jsonl_file):
    """
    Write the processed issues to a JSONL file for batch processing.
    """
    with open(jsonl_file, "w") as file:
        for index, row in tqdm(
            filtered_df.iterrows(), total=filtered_df.shape[0], desc="Writing JSONL"
        ):
            custom_id = row["Custom_ID"]
            title = row["title"]
            description = row["processed_description"]

            system_message = (
                "You are a highly experienced research software engineer with expertise in the Community Earth System Model (CESM). "
                "Your task is to evaluate the provided title and description of a GitHub issue to determine if the issue pertains to a scientific matter "
                "or something else. This includes identifying whether the issue involves scientific algorithms, models, data processing methods, or other components "
                "that directly influence scientific results. "
                "If the issue is about a scientific matter, respond with 'yes'. "
                "If the issue is about something else, respond with 'no'. "
                "Please provide your response only in JSON format with a single key 'impacts_science' and its value as either 'yes' or 'no'."
            )
            user_message = f"Title: {title}\nDescription: {description}"

            json_object = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 500,
                },
            }

            json.dump(json_object, file)
            file.write("\n")


def process_issues_and_save_predictions(input_csv, output_csv):
    """
    Process issues from the input CSV file, get GPT predictions, and save the results to the output CSV file.
    """
    df = pd.read_csv(input_csv)
    df["processed_description"] = df["body"].apply(preprocess_description)

    write_requests_to_jsonl(df, "requests.jsonl")

    client = OpenAI(organization="org-t0BfEZys25Afw0bMxsVMwPDD")

    with open("requests.jsonl", "rb") as jsonl_file:
        batch_input_file = client.files.create(file=jsonl_file, purpose="batch")

    batch_input_file_id = batch_input_file.id

    response = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "PR patches labelling job"},
    )

    print(f"Batch process initiated with ID: {response.id}")


# Main function to run the script
def main():
    initialize_openai_client()

    input_csv = "closed_issues.csv"  # Input CSV file with issues
    output_csv = "issues_with_predictions.csv"  # Output CSV file with predictions

    process_issues_and_save_predictions(input_csv, output_csv)


if __name__ == "__main__":
    main()
