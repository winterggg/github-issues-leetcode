import os

__all__ = ["load_env"]

def load_env(file_path=".env"):
    if not os.path.exists(file_path):
        print(f"{file_path} not found. Skipping loading environment variables.")
        return

    with open(file_path) as f:
        for line in f:
            if line.strip():
                name, value = line.strip().split("=", 1)
                os.environ[name] = value
                print(f"Loaded {name} from {file_path}")