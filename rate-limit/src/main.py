from openai import OpenAI, RateLimitError

from .config  import get_required_setting
from .prompts import TICKET_TRIAGE_INSTRUCTIONS
from .models  import TicketTriage
from .ratelimiter import RateLimiter

def main() -> None:
    
    #API client
    client = OpenAI(
        api_key=get_required_setting("LLM_API_KEY"),
        # this line is important. Without baseurl, the package will calls OpenAI's server
        base_url=get_required_setting("LLM_BASE_URL"), 
        max_retries=2, # Handle provider-side rate-limit errors 
    )
    model = get_required_setting("LLM_MODEL")
    
    # Initialize rate limiter
    rate_limiter = RateLimiter (max_requests=5, window_seconds=60)
    
    #prepare support ticket
    ticket = """
    Since this morning, I receive an error whenever I open the reporting
    dashboard. I have tried a different browser and the error remains.
    My team cannot prepare the monthly report.
    """
    
    #prepare message
    messages=[
        {
            "role": "system",
            "content": TICKET_TRIAGE_INSTRUCTIONS 
                + "\nReturn only valid JSON matching the required fields.",
        },
        {
            "role": "user",
            "content": f"Support ticket:\n{ticket}",
        },
    ]

    # Check rate limit before sending request
    rate_limiter.acquire()
    
    print("Sending ticket to LLM...")
    
    try:
        
        # API invocation
        response = client.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=TicketTriage,
        )

        triage = response.choices[0].message
    
        if triage.parsed is None:
            raise RuntimeError("The model did not return a parseable triage result.")
    
        message = triage.parsed
    
        # 8. Display classification
        print("\nTicket Classification")
        print("---------------------")
        print("Category:", message.category)
        print("Priority:", message.priority)
        print("Summary:", message.summary)
        print("Human Review:", message.requires_human_review)
        print("Confidence:", message.confidence)
        print("Reason:", message.reason)
        
    except RateLimitError as exc:
        print("Provider rate limit exceeded after retries.")
        print(exc)
        

if __name__ == "__main__":
    main()

