def greet(name="World"):
    """
    A simple greeting function.
    
    Args:
        name (str): The name to greet. Defaults to "World".
    
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"


# Example usage
if __name__ == "__main__":
    print(greet())  # Hello, World!
    print(greet("Alice"))  # Hello, Alice!