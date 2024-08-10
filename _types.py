from typing import Self
from urllib.parse import urlparse, urlunparse, quote, ParseResult

class URL:
    """A class to represent a URL."""
    def __init__(self, url: str) -> None:
        """Initialize a URL object.
        
        Args:
        url (str): The URL to be parsed.
        """

        self.parts: ParseResult = urlparse(url)

    def __str__(self) -> str:
        """
        Return a string representation of the URL.

        Returns:
        str: A string representation of the URL.
        """

        return urlunparse(self.parts)

    def __repr__(self) -> str:
        """
        Return a string representation of the URL object.

        Returns:
        str: A string representation of the URL object.
        """

        return f'{self.__class__.__name__}({repr(str(self))})'

    def __truediv__(self, other: Self | str) -> Self:
        """
        Return a new URL object with the path and query strings updated.

        Args:
        other (Self | str): The URL to be joined with the current URL.

        Returns:
        Self: A new URL object with the path and query strings updated.
        """

        if isinstance(other, str):
            new_path = '/'.join([self.parts.path.removesuffix('/'), URL(other).parts.path.removeprefix('/')])
            new_query = '&'.join([self.parts.query, URL(other).parts.query])
        elif isinstance(other, URL):
            new_path = '/'.join([self.parts.path.removesuffix('/'), other.parts.path.removeprefix('/')])
            new_query = '&'.join([self.parts.query, other.parts.query])

        return self.__class__(urlunparse((
            self.parts.scheme,
            self.parts.netloc,
            new_path,
            self.parts.params,
            new_query,
            self.parts.fragment,
        )))
    
    @staticmethod
    def escape(url: str) -> "URL":
        """Escape a string with URL escape sequences and create a new URL object from that string.

        Args:
        url (str): The string to be escaped. "/" will be escaped in "%2F", use "\\/" if you want to have the normal behavior of "/" inthe URL.

        Returns:
        Self: A new URL object with the escaped string.
        """

        return URL(quote(url, safe='\\').replace('\\%2F', '/').replace('\\', '%5C'))