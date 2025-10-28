from langchain.tools import tool

@tool("multiply")
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b
@tool("add")
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b
