
from openai import (
    OpenAI,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

from .config import get_required_setting
from .prompts import TICKET_TRIAGE_INSTRUCTIONS
from .models import TicketTriage
from .ratelimiter import RateLimiter
from .circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
)
from .openai_failure_policy import OpenAIFailurePolicy


def main() -> None:
    
    # 1. Initialize OpenAI client
    client = OpenAI(
        api_key=get_required_setting("LLM_API_KEY"),
        base_url=get_required_setting("LLM_BASE_URL"),
        timeout=30.0,
        max_retries=2,
    )

    model = get_required_setting("LLM_MODEL")
    
    # 2. Initialize Rate Limiter
    rate_limiter = RateLimiter(
        max_requests=5,
        window_seconds=60,
    )

    # 3. Initialize Circuit Breaker
    circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30,
        failure_policy=OpenAIFailurePolicy(),
    )
    
    # 4. Prepare support ticket
    ticket = """
    Since this morning, I receive an error whenever I open the reporting
    dashboard. I have tried a different browser and the error remains.
    My team cannot prepare the monthly report.
    """
    
    messages = [
        {
            "role": "system",
            "content": TICKET_TRIAGE_INSTRUCTIONS,
        },
        {
            "role": "user",
            "content": f"Support ticket:\n{ticket}",
        },
    ]

    # 5. Define provider operation
    def call_provider():
        
        # Check rate limit before calling provider
        rate_limiter.acquire()
        
        return client.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=TicketTriage,
        )
        
    # 6. Execute through Circuit Breaker
    try:

        response = circuit_breaker.execute(call_provider)

        message = response.choices[0].message

        if message.parsed is None:
            raise ValueError(
                "Provider returned no structured ticket classification."
            )

        triage = message.parsed
        
        # 7. Display structured result
        print("\nTicket Classification Result:")
        print(triage.model_dump_json(indent=2))

    except CircuitOpenError as error:
        print(f"Circuit breaker rejected request: {error}")

    except APITimeoutError:
        print("LLM provider request timed out.")

    except APIConnectionError:
        print("Unable to establish connection with LLM provider.")

    except APIStatusError as error:
        print(
            f"LLM provider returned HTTP error: "
            f"{error.status_code}"
        )

    except ValueError as error:
        print(f"Invalid provider response: {error}")
        
if __name__ == "__main__":
    main()