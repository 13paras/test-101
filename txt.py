"""
Text utility module for file operations.
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


def append_text_file(filepath, content):
    """
    Append content to a text file.
    
    Args:
        filepath (str): Path to the text file
        content (str): Content to append
    """
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)


def count_lines(filepath):
    """
    Count the number of lines in a text file.
    
    Args:
        filepath (str): Path to the text file
        
    Returns:
        int: Number of lines in the file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return len(f.readlines())


def count_words(filepath):
    """
    Count the number of words in a text file.
    
    Args:
        filepath (str): Path to the text file
        
    Returns:
        int: Number of words in the file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        return len(content.split())


if __name__ == "__main__":
    # Example usage
    print("Text utility module loaded successfully!")
