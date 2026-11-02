from openai import OpenAI

from .config  import get_required_setting
from .prompts import TICKET_TRIAGE_INSTRUCTIONS
from .models  import TicketTriage

def main() -> None:
    
    client = OpenAI(
        api_key=get_required_setting("LLM_API_KEY"),
        # this line is important. Without baseurl, the package will calls OpenAI's server
        base_url=get_required_setting("LLM_BASE_URL"), 
    )
    model = get_required_setting("LLM_MODEL")
    

    ticket = """
    Since this morning, I receive an error whenever I open the reporting
    dashboard. I have tried a different browser and the error remains.
    My team cannot prepare the monthly report.
    """

    # API invocation
    response = client.chat.completions.parse(
        model=model,
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
        ],
        response_format=TicketTriage,
    )

    #print(response.choices[0].message.content)
    triage = response.choices[0].message
    
    if triage.parsed is None:
        raise RuntimeError("The model did not return a parseable triage result.")
    
    message = triage.parsed
    
    print("Category:", message.category)
    print("Priority:", message.priority)
    print("Summary:", message.summary)
    print("Human Review:", message.requires_human_review)
    print("Confidence:", message.confidence)
    print("Reason:", message.reason)
        


if __name__ == "__main__":
    main()

