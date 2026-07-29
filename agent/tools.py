import os

def list_files(root_path: str) -> list[str]:
    """Recursively list all files under the given root path, returning their relative paths."""
    files_list = []
    try:
        abs_root = os.path.abspath(root_path)
        for root, dirs, files in os.walk(abs_root):
            # Prune .git, node_modules, build, and dist directories in-place
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "build", "dist")]
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, abs_root)
                # Convert backslashes to forward slashes for consistency
                files_list.append(rel_path.replace("\\", "/"))
    except Exception as e:
        print(f"Error listing files in {root_path}: {e}")
        return [f"Error: {e}"]
    return files_list

def read_file(path: str) -> str:
    """Read and return the contents of the file at the given path, with a 50KB size limit."""
    try:
        target_path = path
        # If the path is relative and doesn't exist directly, try resolving it under target-repo
        if not os.path.isabs(target_path) and not os.path.exists(target_path):
            alt_path = os.path.join("target-repo", target_path)
            if os.path.exists(alt_path):
                target_path = alt_path
            else:
                return f"Error: File '{path}' not found."

        # Size guard (50KB)
        file_size = os.path.getsize(target_path)
        if file_size > 50 * 1024:
            return f"Error: File is too large ({file_size / 1024:.1f}KB). Limit is 50KB."

        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return f"Error: Could not read file '{path}'. Detail: {e}"

def search_code(keyword: str, root_path: str) -> list[dict]:
    """Search for a keyword in files under root_path, returning matches with relative paths and line numbers."""
    matches = []
    try:
        abs_root = os.path.abspath(root_path)
        for root, dirs, files in os.walk(abs_root):
            # Prune directories in-place
            dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "build", "dist")]
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, abs_root).replace("\\", "/")
                
                try:
                    # Skip files larger than 100KB for safety during searching
                    if os.path.getsize(full_path) > 100 * 1024:
                        continue
                    
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if keyword.lower() in line.lower():
                                matches.append({
                                    "file": rel_path,
                                    "line": line_num,
                                    "content": line.strip()
                                })
                except Exception:
                    # Skip files that fail to read (e.g. binary or special files)
                    continue
    except Exception as e:
        print(f"Error searching code for '{keyword}' under {root_path}: {e}")
        return [{"error": f"Search failed: {e}"}]
    return matches

def write_file(path: str, content: str) -> str:
    """Write or overwrite content to a file, creating parent directories if necessary."""
    try:
        target_path = path
        # If the path is relative, doesn't start with target-repo, and target-repo exists, resolve under target-repo
        if not os.path.isabs(target_path) and not target_path.startswith("target-repo") and os.path.exists("target-repo"):
            target_path = os.path.join("target-repo", target_path)

        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(target_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Unescape double-escaped newlines and tabs from LLM output
        if isinstance(content, str):
            content = content.replace("\\n", "\n").replace("\\t", "\t")

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        confirm_path = os.path.relpath(target_path).replace("\\", "/")
        return f"Success: Wrote file to {confirm_path}"
    except Exception as e:
        print(f"Error writing file {path}: {e}")
        return f"Error: Could not write file '{path}'. Detail: {e}"
