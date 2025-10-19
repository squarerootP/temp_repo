from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Author:
    author_id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    biography: Optional[str] = None
    # reference by ISBNs to avoid ORM-level object ties
    book_isbns: List[str] = field(default_factory=list)