import asyncio
import json

import openai
from neurons.miner import Miner
import template
from template.types.checker_chain import Product
from template.utils.checker_chain import fetch_product_data

# OpenAI API Key (ensure this is set in env variables or a secure place)
openai.api_key = "your_openai_api_key"


async def generate_review_score(product: Product):
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
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a product evaluation assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )

        review_data = json.loads(response['choices'][0]['message']['content'])
        return review_data
    except (json.JSONDecodeError, KeyError):
        return {"error": "Invalid response from AI"}


def get_overall_score(ai_response: object):
    breakdown = ai_response.get("Breakdown", {})

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

    overall_score = sum(float(scores[key]) * weights[key] for key in scores)

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

    # Extract overall scores safely
    predictions = [
        float(get_overall_score(res))
        for res in results
    ]

    synapse.response = predictions
    return synapse
