import os

def process_file(file_path):
    # VIOLATION: Hardcoded path with backslashes (Rule 2)
    # This will fail on Linux/macOS
    base_path = "C:\\data\\files"
    target_file = base_path + "\\" + file_path
    
    # VIOLATION: Raw print instead of logging (Rule 8)
    print(f"Processing non-compliant path: {target_file}")
    
    if os.path.exists(target_file):
        print("File exists.")
    else:
        print("File not found.")

if __name__ == "__main__":
    process_file("sample.txt")
