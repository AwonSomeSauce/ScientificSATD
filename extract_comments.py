import re


def clean_comment(comment):
    return comment.replace("\n", " ").strip()


def extract_python_comments(file_path):
    comments = []
    in_comment_block = False
    comment_block = ""
    single_line_comment = ""
    in_single_line_comment_block = False

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Iterate through each line
        for line in lines:
            stripped_line = line.strip()
            # Check for inline comment
            inline_comment_index = line.find("#")
            if (
                inline_comment_index != -1
                and not in_comment_block
                and not stripped_line.startswith("#")
            ):
                # Extract and append the inline comment
                inline_comment = line[inline_comment_index + 1 :].strip()
                comments.append(clean_comment(inline_comment))
                continue

            # Handle single-line comments
            if stripped_line.startswith("#") and not in_comment_block:
                if in_single_line_comment_block:
                    # If already in a block of single-line comments, append the line
                    single_line_comment += "\n" + stripped_line[1:].strip()
                else:
                    # Start of a new block of single-line comments
                    in_single_line_comment_block = True
                    single_line_comment = stripped_line[1:].strip()
            else:
                # Not a single-line comment
                if in_single_line_comment_block:
                    # End of a block of single-line comments
                    comments.append(clean_comment(single_line_comment))
                    in_single_line_comment_block = False
                    single_line_comment = ""

                # Handle multi-line comments
                if '"""' in stripped_line or "'''" in stripped_line:
                    quote_count = stripped_line.count('"""') + stripped_line.count(
                        "'''"
                    )
                    if not in_comment_block:
                        in_comment_block = True
                        comment_block = stripped_line
                        if quote_count == 2:
                            comments.append(
                                clean_comment(
                                    comment_block.replace('"""', "")
                                    .replace("'''", "")
                                    .strip()
                                )
                            )
                            in_comment_block = False
                            comment_block = ""
                    else:
                        in_comment_block = False
                        comment_block += "\n" + stripped_line
                        comments.append(
                            clean_comment(
                                comment_block.replace('"""', "")
                                .replace("'''", "")
                                .strip()
                            )
                        )
                        comment_block = ""
                elif in_comment_block:
                    comment_block += "\n" + stripped_line

        # Check for any remaining single-line comments
        if in_single_line_comment_block:
            comments.append(clean_comment(single_line_comment))
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    return comments


def extract_cpp_comments(file_path):
    comments = []
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        line_number = 0
        multi_line_comment = []
        consecutive_single_line_comments = []

        # Iterate through each line
        for index, line in enumerate(lines):
            line = line.strip()

            # Handling multi-line comments
            if line.startswith("/*"):
                if consecutive_single_line_comments:
                    comments.append(" ".join(consecutive_single_line_comments))

                    consecutive_single_line_comments = []
                # End of multi-line comment
                if line.endswith("*/"):
                    multi_line_comment.append(line)
                    comments.append(
                        " ".join(multi_line_comment)
                        .replace("/*", "")
                        .replace("*/", "")
                        .strip()
                    )
                    multi_line_comment = []
                # Start of multi-line comment or mid-section
                else:
                    multi_line_comment.append(line.replace("/*", "").strip())
                    line_number = index + 1
            elif line.endswith("*/") and multi_line_comment:
                multi_line_comment.append(line.replace("*/", "").strip())
                comments.append(" ".join(multi_line_comment))
                multi_line_comment = []
            elif multi_line_comment:
                multi_line_comment.append(line.strip())
            # Not in a multi-line comment
            elif not multi_line_comment:
                single_line_comment_match = re.search(r"//(.*)", line)
                if single_line_comment_match:
                    if line.startswith("//"):
                        # If we encounter consecutive single-line comments
                        if consecutive_single_line_comments:
                            consecutive_single_line_comments.append(
                                single_line_comment_match.group(1).strip()
                            )
                        else:
                            consecutive_single_line_comments = [
                                single_line_comment_match.group(1).strip()
                            ]
                            line_number = index + 1
                    else:
                        comments.append(single_line_comment_match.group(1).strip())
                # Not a consecutive single-line comment
                else:
                    if consecutive_single_line_comments:
                        comments.append(" ".join(consecutive_single_line_comments))
                        consecutive_single_line_comments = []

        if consecutive_single_line_comments:
            comments.append(" ".join(consecutive_single_line_comments))
            consecutive_single_line_comments = []
    except UnicodeDecodeError:
        print(f"UnicodeDecodeError: Unable to read {file_path}")

    return comments


def extract_fortran_comments(file_path):
    comments = []
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

            comment_block = ""
            in_comment_block = False

            for line in lines:
                line = line.strip()
                comment_index = line.find("!")

                # Check if the line is a full-line comment
                if line.startswith("!"):
                    if in_comment_block:
                        # Append to existing comment block
                        comment_block += "\n" + line[1:].strip()
                    else:
                        # Start a new comment block
                        in_comment_block = True
                        comment_block = line[1:].strip()
                elif comment_index != -1:
                    # Handle inline comment
                    # Add any existing comment block before adding the inline comment
                    if in_comment_block:
                        comments.append(comment_block)
                        in_comment_block = False
                        comment_block = ""

                    # Add the inline comment as a separate comment
                    comments.append(clean_comment(line[comment_index + 1 :].strip()))
                else:
                    # End of a comment block
                    if in_comment_block:
                        comments.append(clean_comment(comment_block))
                        in_comment_block = False
                        comment_block = ""

            # Check for any remaining comment block at the end of file
            if in_comment_block:
                comments.append(clean_comment(comment_block))

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    return comments
