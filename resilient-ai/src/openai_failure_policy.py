
from openai import APIConnectionError, APIStatusError


class OpenAIFailurePolicy:

    def should_count(self, error: Exception) -> bool:

        # Connection errors and timeouts
        if isinstance(error, APIConnectionError):
            return True

        # Server-side HTTP errors (5xx)
        if isinstance(error, APIStatusError):
            return error.status_code >= 500

        # Do not count client errors such as 400, 401 or 429
        return False
