import sys
import os

# Add workspace directory to path to easily import tools
WORKSPACE_DIR = r"f:\Scoutr"
sys.path.insert(0, WORKSPACE_DIR)

from agent.tools import list_files, read_file, search_code, write_file

def run_tests():
    print("=== Testing list_files ===")
    target_repo = os.path.join(WORKSPACE_DIR, "target-repo")
    files = list_files(target_repo)
    print(f"Total files found in target-repo: {len(files)}")
    print("Full list of files found:")
    for f in sorted(files):
        print(f"  - {f}")
    # Verify relative path check
    for f in files:
        if os.path.isabs(f):
            print(f"FAIL: Absolute path found: {f}")
            return
        parts = f.replace("\\", "/").split("/")
        if ".git" in parts or "node_modules" in parts or "build" in parts or "dist" in parts:
            print(f"FAIL: Ignored folder file leaked: {f}")
            return
    print("PASS: list_files returns relative paths and skips ignored directories.")

    print("\n=== Testing search_code ===")
    search_keyword = "express"
    matches = search_code(search_keyword, target_repo)
    print(f"Matches found for keyword '{search_keyword}': {len(matches)}")
    print(f"Sample matches (up to 3): {matches[:3]}")
    if len(matches) == 0:
        print("FAIL: Expected to find matches for 'express', but found none.")
        return
    for m in matches:
        if "error" in m:
            print(f"FAIL: Search encountered an error: {m['error']}")
            return
        if os.path.isabs(m["file"]):
            print(f"FAIL: Absolute path in search_code match: {m['file']}")
            return
    print("PASS: search_code matches check passed.")

    print("\n=== Testing write_file ===")
    test_write_path = "test_temp_file.txt"
    test_content = "Hello from automated tools test!"
    result = write_file(test_write_path, test_content)
    print(f"Write Result: {result}")
    
    # Check if file was written relative to target-repo (i.e. target-repo/test_temp_file.txt)
    expected_full_path = os.path.join(target_repo, test_write_path)
    if not os.path.exists(expected_full_path):
        print(f"FAIL: File was not created at expected path: {expected_full_path}")
        return
    print("PASS: write_file successfully wrote file relative to target-repo.")

    print("\n=== Testing read_file ===")
    # 1. Read the newly created test file
    read_content = read_file(test_write_path)
    print(f"Read Content from '{test_write_path}': {read_content}")
    if read_content != test_content:
        print(f"FAIL: Read content mismatch. Expected: '{test_content}', got: '{read_content}'")
        return
    print("PASS: read_file read content correctly.")

    # 2. Test size guard (create a temporary large file >50KB)
    large_write_path = "test_large_file.txt"
    large_content = "X" * (55 * 1024) # 55 KB
    write_file(large_write_path, large_content)
    read_large_result = read_file(large_write_path)
    print(f"Read Large File Result: {read_large_result[:100]}")
    if "Error: File is too large" not in read_large_result:
        print("FAIL: read_file did not block large file (>50KB).")
        return
    print("PASS: read_file successfully blocked file size > 50KB.")

    # Clean up test files
    try:
        os.remove(expected_full_path)
        os.remove(os.path.join(target_repo, large_write_path))
        print("\nCleaned up temporary test files.")
    except Exception as e:
        print(f"\nWarning during cleanup: {e}")

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    run_tests()
