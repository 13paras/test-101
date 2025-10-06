"""
Text file utility module.
"""


def read_text_file(filepath):
    """
    Read and return the contents of a text file.
    
    Args:
        filepath (str): Path to the text file
        
    Returns:
        str: Contents of the file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_text_file(filepath, content):
    """
    Write content to a text file.
    
    Args:
        filepath (str): Path to the text file
        content (str): Content to write
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def append_to_file(filepath, content):
    """
    Append content to a text file.
    
    Args:
        filepath (str): Path to the text file
        content (str): Content to append
    """
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    # Example usage
    print("Text file utility module")
