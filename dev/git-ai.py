
import os
import subprocess
import sys
import requests
import json
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API'))
SYSTEM = "You are a developer, you create git commit messages."
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

The Following code:
"""


def getResp(text):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": EXAMPLE}
    ]
    )
    print(completion.choices[0].message)
    if "message" in completion['choices'][0] and completion['choices'][0]['message']:
        return completion['choices'][0]['message']['content']
    else:
        print("[ERROR] generating response for:", text)
        return ""

def main(local_path):
    if not os.path.exists(local_path):
        print(f"[ERROR] The specified path {local_path} does not exist.")
        return

    try:
        os.chdir(local_path)
    except OSError as e:
        print(f"[ERROR] Failed to change directory to {local_path}. Error: {e}")
        return

    result = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True)
    changed_files = result.stdout.splitlines()

    # Extract changes for each file
    changes = []
    for file in changed_files:
        result = subprocess.run(['git', 'diff', file], capture_output=True, text=True)
        changes.append(result.stdout)

    # Generate a single description from all changes
    print(f"[INFO] Creating AI Git descriptions for {len(changed_files)} changed files...")
    description = "\n".join(getResp(AI_INSERT + change) for change in changes)
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

