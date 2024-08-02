import pandas as pd
import re

# Load the dataframe (assuming the file is a CSV for example purposes)
df = pd.read_csv("path_to_your_dataframe.csv")

# Load the keywords from the provided text file
with open("satd_features.txt", "r") as file:
    keywords = [line.strip() for line in file.readlines()]


# Preprocess comments: tokenizing, converting text to lowercase, and stripping special characters
def preprocess_comment(comment):
    # Convert to lowercase
    comment = comment.lower()
    # Remove special characters
    comment = re.sub(r"[^a-z0-9\s]", "", comment)
    # Tokenize (split by whitespace)
    tokens = comment.split()
    return " ".join(tokens)


df["processed_comment"] = df["comment"].apply(preprocess_comment)


# Function to check if any keyword is in the comment
def contains_keyword(comment):
    for keyword in keywords:
        # Match the keyword exactly, but ignore case
        if re.search(rf"\b{keyword}\b", comment):
            return True
    return False


# Filter the dataframe for rows containing any of the keywords
filtered_df = df[df["processed_comment"].apply(contains_keyword)]

# Save the filtered dataframe to a CSV file
filtered_df.to_csv("filtered_comments.csv", index=False)
