"""HTTP module."""

from requests import Session

HTTP_METHODS = {
    "GET",
    "HEAD",
    "OPTIONS",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "PATCH",
}


class HTTPSession(Session):
    """An HTTP session with origin."""

    def __init__(self, origin, timeout=60, **kwargs):
        super().__init__(**kwargs)
        self.origin = origin
        self.timeout = timeout

    @classmethod
    def with_origin(cls, origin: str):
        """Make sure the origin has a single trailing slash."""
        return cls(origin.rstrip("/") + "/")

    def request(self, method: str, path: str, **kwargs):
        """Send an HTTP request.

        :param method: Method for the request.
        :param path: Path joined to the URL.
        :param \\**kwargs: Optional keyword arguments passed to the session.
        """
        url = str(self.origin) + path
        kwargs.setdefault("timeout", self.timeout)
        response = super().request(method, url, **kwargs)
        response.raise_for_status()

        return response
