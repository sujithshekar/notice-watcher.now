import os

print("🔍 DEBUG: ENVIRONMENT VARIABLES")
for key, value in os.environ.items():
    print(f"{key} = {value}")

