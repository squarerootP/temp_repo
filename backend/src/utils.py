import requests

def get_isbn13(book_title: str) -> str | None:
    """
    Fetch the ISBN-13 of a book using the Google Books API.
    
    Args:
        book_title (str): The title of the book.
        
    Returns:
        str | None: The ISBN-13 if found, otherwise None.
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}"
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    if "items" not in data or not data["items"]:
        return None
    
    # Look through results for ISBN_13
    for item in data["items"]:
        identifiers = item.get("volumeInfo", {}).get("industryIdentifiers", [])
        for identifier in identifiers:
            if identifier.get("type") == "ISBN_13":
                return identifier.get("identifier")
    
    return None

