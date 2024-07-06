"""
Type: Shared module
Description: This module contains the secret keys for the application.
"""
import os, json

secret_path = os.path.join(os.path.dirname(__file__), 'env.json')
secrets = json.load(open(secret_path))

def get_secret(key):
    return secrets[key]