import asyncio
import json

import openai
from neurons.miner import Miner
import template
from template.types.checker_chain import UnreviewedProduct
from template.utils.checker_chain import fetch_product_data

# OpenAI API Key (ensure this is set in env variables or a secure place)
OPENAI_API_KEY = "your_openai_api_key"


async def generate_review_score(product: UnreviewedProduct):
    """
    Generate review scores for a product using OpenAI's GPT.
    """
    prompt = f"""
    You are an expert evaluator analyzing products based on multiple key factors. Given the following product details, provide a **review score out of 100** based on the specified evaluation criteria.

    **Product Details:**
    - Name: {product.name}
    - Description: {product.description}
    - Category: {product.category}
    - URL: {product.url}
    - Location: {product.location}
    - Network: {product.network}
    - Team: {len(product.teams)} members
    - Marketing & Social Presence: {product.twitterProfile}
    - Current Review Cycle: {product.currentReviewCycle}

    **Evaluation Criteria (Score each aspect fairly, with an overall score out of 100):**
    1. **Project (Innovation/Technology)**
    2. **Userbase/Adoption**
    3. **Utility Value**
    4. **Security**
    5. **Team**
    6. **Price/Revenue/Tokenomics**
    7. **Marketing & Social Presence**
    8. **Roadmap**
    9. **Clarity & Confidence**
    10. **Partnerships (Collabs, VCs, Exchanges)**

    **Output Format (Example JSON):**
    {{
      "Product": "{product.name}",
      "Overall Score": 85,
      "Breakdown": {{
        "Project (Innovation/Technology)": 9,
        "Userbase/Adoption": 7,
        "Utility Value": 8,
        "Security": 9,
        "Team": 9,
        "Price/Revenue/Tokenomics": 7,
        "Marketing & Social Presence": 8,
        "Roadmap": 8,
        "Clarity & Confidence": 9,
        "Partnerships": 8
      }}
    }}

    Provide the final score and breakdown in the above JSON format.
    """

    try:
        # Initialize OpenAI client
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        # Get API_KEY from environment variable
        # client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Use env variable for security

        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product evaluation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        response_content = response.choices[0].message.content.strip()

        review_data = json.loads(response_content)

        return review_data
    except (json.JSONDecodeError, KeyError):
        return {"error": "Invalid response from AI"}
    except KeyError:
        return {"error": "Unexpected API response format"}


def get_overall_score(ai_response: object):
    if (isinstance(ai_response, dict)):
        breakdown = ai_response.get("Breakdown", {})
    else:
        return None
    # Default weights (Modify these as needed)
    # Sum of Weights should always equal 10 for proper overall weight to be within 100
    weights = {
        "Project (Innovation/Technology)": 1,
        "Userbase/Adoption": 1,
        "Utility Value": 1,
        "Security": 1.5,
        "Team": 0.5,
        "Price/Revenue/Tokenomics": 1,
        "Marketing & Social Presence": 1.5,
        "Roadmap": 1,
        "Clarity & Confidence": 0.5,
        "Partnerships": 1
    }

    scores = {key: breakdown.get(key, 0) for key in weights.keys()}

    overall_score: float = sum(
        float(scores[key]) * weights[key] for key in scores)

    return round(overall_score, 2)  # Rounds the score to 2 decimal places


async def forward(self: Miner, synapse: template.protocol.CheckerChainSynapse):
    """
    Asynchronously fetch product data and generate review scores in parallel.
    """
    tasks = []
    for product_id in synapse.query:
        product = fetch_product_data(product_id)
        if product:
            tasks.append(generate_review_score(product))

    # Execute all API calls concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Extract overall scores safely, handling exceptions
    predictions = []
    for res in results:
        try:
            if isinstance(res, Exception):
                raise res  # Re-raise exception to handle it below
            score = get_overall_score(res)
            predictions.append(score)
        except Exception as e:
            print(f"Error processing result: {e}")
            predictions.append(None)  # Default value or handle differently

    synapse.response = predictions
    return synapse
