# GenAI
This repo is only related to the GenAI project

This is the basic model.I have not used structured output as defined in the models.py file.

summary:
main.py is coordinating a task:
- config.py tells it where to connect and which model to use.
- prompts.py tells the LLM what it should do.
- The ticket variable provides the actual customer problem.
- The OpenAI SDK communicates with the configured API.
- The LLM processes the instructions and ticket.
- main.py extracts and displays the result.