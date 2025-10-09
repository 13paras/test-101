# AI Crew for Job Posting
## Introduction
This project demonstrates the use of the CrewAI framework to automate the creation of job posting. CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.

By [@joaomdmoura](https://x.com/joaomdmoura)

- [CrewAI Framework](#crewai-framework)
- [Key Features](#key-features)
- [Running the script](#running-the-script)
- [Details & Explanation](#details--explanation)
- [Contributing](#contributing)
- [Support and Contact](#support-and-contact)
- [License](#license)

## CrewAI Framework
CrewAI is designed to facilitate the collaboration of role-playing AI agents. In this example, these agents work together to analyze company culture and identify role requirements to create comprehensive job postings and industry analysis.

## Key Features
This job posting system is designed with **accessibility and diversity** in mind:

- **Simple, Clear Language**: Uses plain language that anyone can understand, regardless of educational background
- **Jargon-Free Writing**: Avoids industry jargon and technical terms that might confuse or intimidate candidates
- **Diversity Analysis**: Includes dedicated agents to evaluate how well the posting will attract diverse candidates
- **Feedback Simulation**: Simulates feedback from potential applicants with varying backgrounds to ensure clarity
- **Inclusive Tone**: Maintains a professional yet friendly, approachable tone with personal touches
- **Accessibility Focus**: Ensures content is welcoming to candidates from non-traditional career paths

The system automatically enforces these principles through specialized AI agents that review, gather feedback, and analyze the diversity impact of every job posting.

## Running the Script
It uses GPT-4o by default so you should have access to that to run it.

***Disclaimer:** This will use gpt-4o unless you change it to use a different model, and by doing so it may incur in different costs.*

- **Configure Environment**: Copy `.env.example` and set up the environment variables for [OpenAI](https://platform.openai.com/api-keys) and other tools as needed, like [Serper](serper.dev).
- **Install Dependencies**: Run `poetry lock && poetry install`.
- **Customize**: Modify `src/job_posting/main.py` to add custom inputs for your agents and tasks.
- **Customize Further**: Check `src/job_posting/config/agents.yaml` to update your agents and `src/job_posting/config/tasks.yaml` to update your tasks.
- **Execute the Script**: Run `poetry run job_posting` and input your project details.

## Details & Explanation
- **Running the Script**: Execute `poetry run job_posting`. The script will leverage the CrewAI framework to generate a detailed job posting.
- **Key Components**:
  - `src/job_posting/main.py`: Main script file.
  - `src/job_posting/crew.py`: Main crew file where agents and tasks come together, and the main logic is executed.
  - `src/job_posting/config/agents.yaml`: Configuration file for defining agents.
  - `src/job_posting/config/tasks.yaml`: Configuration file for defining tasks.
  - `src/job_posting/tools`: Contains tool classes used by the agents.

### AI Agents
The system includes specialized agents for creating accessible, diverse job postings:
- **Research Analyst**: Analyzes company culture and values
- **Job Description Writer**: Creates engaging, accessible job postings using simple language
- **Review and Editing Specialist**: Ensures clarity, accuracy, and simplicity
- **Candidate Feedback Analyst**: Simulates feedback from diverse applicants
- **Diversity and Inclusion Specialist**: Evaluates diversity impact and accessibility

### Language Guidelines
The system automatically enforces these language principles:
- Uses phrases like "helping the team with daily production activities and tasks" instead of complex operational language
- Replaces technical descriptions like "support the production team in video editing tasks using Adobe Premiere" with "assisting the team in editing videos to create fantastic content"
- Maintains an 8th-grade reading level or below for maximum accessibility
- Includes personal touches about company culture and day-to-day work experience
- Avoids unnecessary barriers that might discourage diverse candidates

## License
This project is released under the MIT License.
