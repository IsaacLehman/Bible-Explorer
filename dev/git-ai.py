# A quick and dirty Ai generation commit message tool.
# cd dev & pushAll.cmd
# OPENAI_API is a system environment variable.
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
Implemented logging in file1.py and added my_method to MyClass. 😸
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