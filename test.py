def greet(name="World"):
    """
    A simple greeting function.
    
    Args:
        name (str): The name to greet. Defaults to "World".
    
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    # Test the greet function
    print(greet())
    print(greet("Alice"))
    print(greet("Bob"))