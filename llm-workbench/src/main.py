from openai import OpenAI

from .config import get_required_setting
from .prompts import TICKET_TRIAGE_INSTRUCTIONS

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
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": TICKET_TRIAGE_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": f"Support ticket:\n{ticket}",
            },
        ],
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()

