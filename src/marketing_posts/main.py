import sys
from marketing_posts.crew import MarketingPostsCrew
import neatlogs
import os
from dotenv import load_dotenv

load_dotenv()

neatlogs.init(api_key=os.getenv('NEATLOGS_API_KEY'), tags=['testing', 'openai']
              )


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'customer_domain': 'openai.com',
        'project_description': """
OpenAI, a leading provider of artificial intelligence research and deployment, aims to revolutionize AI accessibility for its enterprise clients. This project involves developing an innovative marketing strategy to showcase OpenAI's advanced AI models and solutions, emphasizing safety, capability, and integration possibilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of OpenAI's platform.

Customer Domain: AI Research and Development
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of OpenAI's services among enterprise clients.
"""
    }
    MarketingPostsCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'customer_domain': 'openai.com',
        'project_description': """
OpenAI, a leading provider of artificial intelligence research and deployment, aims to revolutionize AI accessibility for its enterprise clients. This project involves developing an innovative marketing strategy to showcase OpenAI's advanced AI models and solutions, emphasizing safety, capability, and integration possibilities. The campaign will target tech-savvy decision-makers in medium to large enterprises, highlighting success stories and the transformative potential of OpenAI's platform.

Customer Domain: AI Research and Development
Project Overview: Creating a comprehensive marketing campaign to boost awareness and adoption of OpenAI's services among enterprise clients.
"""
    }
    try:
        MarketingPostsCrew().crew().train(
            n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
