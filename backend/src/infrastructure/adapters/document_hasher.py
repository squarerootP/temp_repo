# Create a common hash utility
from hashlib import sha256


class DocumentHasher:
    @staticmethod
    def hash_file(file_path: str) -> str:
        hasher = sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def hash_content(content: str) -> str:
        return sha256(content.encode("utf-8")).hexdigest()
