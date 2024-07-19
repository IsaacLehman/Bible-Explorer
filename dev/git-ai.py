"""
Bible Explorer - Automated Git Commit Message Generator

This script automates the process of generating descriptive commit messages for changes made to a Git repository. It leverages the OpenAI GPT-4 model to craft meaningful commit messages based on the modifications detected in the repository. 

Prerequisites:
- Python 3.x installed on your system.
- An active OpenAI account with an API key obtained from the OpenAI dashboard.
- The OpenAI Python library (`openai`) installed. You can install it via pip: `pip install openai`.
- Git must be installed and properly configured on your system.

Usage Instructions:
1. Ensure your OpenAI API key is stored as an environment variable named `OPENAI_API`.
2. Navigate to the directory containing this script in your command line interface.
3. Run the script by executing `python git-ai.py <path_to_directory> <optional_task_description>`. Replace `<path_to_directory>` with the path to the Git repository you wish to work with. Optionally, you can also provide a brief task description to help guide the AI in generating more relevant commit messages.

Example:
python git-ai.py C:\Projects\Web\Bible-Explorer "Added initial structure"
or from the projects root type:
cd dev & pushAll.cmd

Note: This script assumes that the current working directory is the root of your Git repository. Adjustments may be needed depending on your repository's structure and location.

Author: Gabe Ulrich
Date: 7/19/2024
"""


# Import necessary modules
import os

import subprocess
import sys
from openai import OpenAI

# Initialize the OpenAI client with the API key from the environment variables
client = OpenAI(api_key=os.getenv('OPENAI_API'))

# Define the system role for the chat completions
SYSTEM = "You are a developer, you create git commit messages."

# Example input and expected output format for generating commit messages
EXAMPLE = """
Input (Example):
diff --git a/file1.py b/file1.py
index 1234567..abcdef 100644
--- a/file1.py
+++ b/file1.py
@@ -1,5 +1,6 @@
 import os
+import logging
class MyClass:
    def my_method(self):
        pass

Expected Output (Example):
😸 Implemented logging in file1.py and added my_method to MyClass.

following code:
"""

# Function to generate responses from the OpenAI model
def getResp(text):
    try:
        # Create a chat completion with the system and user roles
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": text}
            ]
        )
        # Return the generated response
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        quit()

# Main function to process git changes and generate commit messages
def main(local_path):
    # Check if the local path exists
    if not os.path.exists(local_path):
        print(f"[ERROR] The specified path {local_path} does not exist.")
        return
    
    # Change the current working directory to the specified path
    try:
        os.chdir(local_path)
    except OSError as e:
        print(f"[ERROR] Failed to change directory to {local_path}. Error: {e}")
        return
    
    # Get the names of changed files
    result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True)
    changed_files = result.stdout.splitlines()
    
    # Extract changes for each file
    changes = []
    for file in changed_files:
        result = subprocess.run(['git', 'diff', file], capture_output=True, text=True)
        changes.append(result.stdout)
    
    # Generate a single description from all changes
    print(f"[INFO] Creating AI Git descriptions for {len(changed_files)} changed files...")
    description = "\n".join(getResp(EXAMPLE + change) for change in changes)
    
    # Add all new files
    subprocess.run(['git', 'add', '.'])
    
    # Commit the changes with the AI-generated message
    if len(sys.argv) == 3:
        subprocess.run(['git', 'commit', '-m', f"{sys.argv[2]} - {description}"])
    else:
        subprocess.run(['git', 'commit', '-m', f"{description}"])
    subprocess.run(['git', 'push'])

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print("[INFO] Usage: python script.py <path_to_directory> <task(s)>")
    else:
        main(sys.argv[1])