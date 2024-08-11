from pathlib import Path
import inspect
import sys

class ErrorMeta(type):
    _error_code_ranges = {
        'NetworkError': (0x1000, 0x1FFF),
        'PackageError': (0x2000, 0x2FFF),
        'DependencyError': (0x3000, 0x3FFF),
        'FilesystemError': (0x4000, 0x4FFF),
        'UserError': (0x5000, 0x5FFF),
        'InternalError': (0x6000, 0x6FFF),
        'SystemError': (0x7000, 0x7FFF),
    }
    _next_code = {} # type: ignore

    def __new__(cls, name, bases, class_dict):
        if bases and bases[0] == Error:
            if name in cls._error_code_ranges:
                start, _ = cls._error_code_ranges[name]
                class_dict['code'] = start
                cls._next_code[name] = start + 1
        elif bases and bases[0].__name__ in cls._error_code_ranges:
            parent = bases[0].__name__
            start, end = cls._error_code_ranges[parent]
            if parent not in cls._next_code:
                cls._next_code[parent] = start + 1

            code = cls._next_code[parent]
            if code > end:
                raise ValueError(f"No more codes available for {parent}")
            class_dict['code'] = code
            cls._next_code[parent] += 1

        return super().__new__(cls, name, bases, class_dict)

class Error(metaclass=ErrorMeta):
    """Base class for errors."""

    def __init__(self, message: str) -> None:
        """Initialize an error.

        Args:
        message (str): The error message.
        """

        self.message = self.format_message(message)
        self.type = self.__class__.__name__
        self.stacktrace = self._generate_stacktrace()

    @staticmethod
    def format_message(message: str) -> str:
        """Format the error message to spend max. 80 characters per line.
        
        Args:
        message (str): The error message.

        Returns:
        str: The formatted error message.
        """

        result = []

        for line in message.splitlines():
            if len(line) > 80:
                result.append(line[:80] + "\n" + line[80:])
            else:
                result.append(line)

        return "\n".join(result)

    def _generate_stacktrace(self) -> str:
        """Generates a custom stack trace for the error."""
        
        stack = inspect.stack()

        # Skip the first two frames:
        # - The current frame (Error.__init__)
        # - The frame that called Error.__init__ (the subclass's __init__)

        stack = stack[2:]
        lines = [f"  File \"{frame.filename}\", line {frame.lineno}, in {frame.function}" for frame in stack]
        return "\n".join(lines)

    def __repr__(self) -> str:
        """Return a string representation of the error."""

        return f"{self.type} (Error code: {hex(self.code)} [{self.code}]):\n    {self.message}\n\n{self.stacktrace}" # type: ignore

# Error codes categories:
# 0x1000 - 0x1FFF: Network errors
# 0x2000 - 0x2FFF: Package errors
# 0x3000 - 0x3FFF: Dependency errors
# 0x4000 - 0x4FFF: Filesystem errors
# 0x5000 - 0x5FFF: User errors
# 0x6000 - 0x6FFF: Internal errors
# 0x7000 - 0x7FFF: System errors

class NetworkError(Error):
    """Package errors."""

    def __init__(self, message: str) -> None:
        """Initialize a package error.

        Args:
        message (str): The error message.
        """

        super().__init__(message)

class PackageError(Error):
    """Package errors."""

    def __init__(self, message: str) -> None:
        """Initialize a package error.

        Args:
        message (str): The error message.
        """

        super().__init__(message)

class DependencyError(Error):
    """Dependency errors."""

    def __init__(self, message: str) -> None:
        """Initialize a dependency error.

        Args:
        message (str): The error message.
        """

        super().__init__(message)

class FilesystemError(Error):
    """Filesystem errors."""

    def __init__(self, message: str) -> None:
        """Initialize a filesystem error.

        Args:
        message (str): The error message.
        """

        super().__init__(message)

class UserError(Error):
    """User errors."""

    def __init__(self, message: str) -> None:
        """Initialize a user error.

        Args:
        message (str): The error message.
        """

        super().__init__(message)

class InternalError(Error):
    """Internal errors."""

    def __init__(self, message: str) -> None:
        """Initialize an internal error.

        Args:
        message (str): The error message.
        """

        super().__init__(message)

class SystemError(Error):
    """System errors."""

    def __init__(self, message: str) -> None:
        """Initialize a system error.

        Args:
        message (str): The error message.
        """

        super().__init__(message)

# NetworkError

class HTTPError(NetworkError):
    """HTTP errors."""

    def __init__(self, status_code: int) -> None:
        """Initialize an HTTP error.

        Args:
        status_code (int): The HTTP status code.
        """

        http_error_message: dict[int, str] = {
            100: "Continue",
            101: "Switching Protocols",
            102: "Processing",
            103: "Early Hints",
            200: "OK",
            201: "Created",
            202: "Accepted",
            203: "Non-Authoritative Information",
            204: "No Content",
            205: "Reset Content",
            206: "Partial Content",
            207: "Multi-Status",
            208: "Already Reported",
            226: "IM Used",
            300: "Multiple Choices",
            301: "Moved Permanently",
            302: "Found",
            303: "See Other",
            304: "Not Modified",
            305: "Use Proxy Obsolète",
            306: "unused",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            402: "Payment Required Expérimental",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "Not Acceptable",
            407: "Proxy Authentication Required",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            411: "Length Required",
            412: "Precondition Failed",
            413: "Payload Too Large",
            414: "URI Too Long",
            415: "Unsupported Media Type",
            416: "Range Not Satisfiable",
            417: "Expectation Failed",
            418: "I'm a teapot",
            421: "Misdirected Request",
            422: "Unprocessable Entity",
            423: "Locked",
            424: "Failed Dependency",
            425: "Too Early Expérimental",
            426: "Upgrade Required",
            428: "Precondition Required",
            429: "Too Many Requests",
            431: "Request Header Fields Too Large",
            451: "Unavailable For Legal Reasons",
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
            505: "HTTP Version Not Supported",
            506: "Variant Also Negotiates",
            507: "Insufficient Storage",
            508: "Loop Detected",
            510: "Not Extended",
            511: "Network Authentication Required"
        }

        super().__init__(f'HTTP status code {status_code}: {http_error_message[status_code]}.')

# PackageError

class PackageNotFoundError(PackageError):
    """Raised when a package is not found."""

    def __init__(self, package_name: str, state: str | None = None) -> None:
        """Initialize a package not found error.

        Args:
        package_name (str): The name of the package.
        state (str | None): The state of the package. Defaults to None.
        code (int): The error code. Defaults to 1.
        """

        super().__init__(f'Could not localize the {state if state else '\b'} package "{package_name}".')

class PackageMetadataNotFoundError(PackageError):
    """Raised when a package is not installed."""

    def __init__(self, package_name: str) -> None:
        """Initialize a package not installed error.

        Args:
        package_name (str): The name of the package.
        code (int): The error code. Defaults to 1.
        """

        super().__init__(f'Could not localize metadata for the "{package_name}" package.')

# UserError

class InvalidCommandError(UserError):
    """Raised when a command is invalid."""

    def __init__(self, command: str) -> None:
        """Initialize an invalid command error.

        Args:
        command (str): The invalid command.
        """

        super().__init__(f'Invalid command: "{command}".')

class InvalidArgumentsError(UserError):
    """Raised when the arguments of a command are invalid."""

    def __init__(self, *arguments: str) -> None:
        """Initialize an invalid arguments error.

        Args:
        *arguments (str): The invalid arguments.
        """

        super().__init__(f'Invalid argument: "{'", "'.join(arguments)}".')

# SystemError

class InstallationNotFoundError(SystemError):
    """Raised when the MathScript installation is not found."""

    def __init__(self) -> None:
        """Initialize an installation not found error."""

        super().__init__("MathScript installation not found.")

class FileOrDirectoryNotFoundError(SystemError):
    """Raised when a file/directory don't exist."""

    def __init__(self, path: Path | str) -> None:
        """Initialize a file or directory not found error.

        Args:
        path (Path | str): The path to the file/directory.
        """

        if not isinstance(path, Path):
            path = Path(path)

        super().__init__(f'Could not find the "{path}" {'directory' if path.is_dir() else 'file'}.')

class AccesDeniedError(SystemError):
    """Raised when the access to directory/file is denied."""

    def __init__(self, path: Path | str) -> None:
        """Initialize an access denied error.

        Args:
        path (Path | str): The path to the directory/file.
        """

        if not isinstance(path, Path):
            path = Path(path)

        super().__init__(f'The access to the {'directory' if path.is_dir() else 'file'} "{path}" is denied.')