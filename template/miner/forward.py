import asyncio

from neurons.miner import Miner
import template
from template.miner.llm import ReviewScoreSchema, ScoreBreakdown, generate_review_score
from template.utils.checker_chain import fetch_product_data
import bittensor as bt


def get_overall_score(ai_response: ReviewScoreSchema):
    if (isinstance(ai_response, ReviewScoreSchema)):
        breakdown = ai_response.breakdown
    else:
        return None
    # Default weights (Modify these as needed)
    # Sum of Weights should always equal 10 for proper overall weight to be within 100
    weights = {
        "project": 1,
        "userbase": 1,
        "utility": 1,
        "security": 1.5,
        "team": 0.5,
        "tokenomics": 1,
        "marketing": 1.5,
        "roadmap": 1,
        "clarity": 0.5,
        "partnerships": 1
    }

    field_names = ScoreBreakdown.model_fields.keys()
    scores = {field: getattr(breakdown, field) for field in field_names}

    overall_score: float = sum(
        float(scores[key]) * weights[key] for key in scores)

    return round(overall_score, 2)  # Rounds the score to 2 decimal places


async def forward(self: Miner, synapse: template.protocol.CheckerChainSynapse):
    """
    Asynchronously fetch product data and generate review scores in parallel.
    """
    bt.logging.info(f"Received mine requests for products {synapse.query}")

    tasks = []
    for product_id in synapse.query:
        product = fetch_product_data(product_id)
        if product:
            tasks.append(generate_review_score(product))

    bt.logging.info(f"Got Product details")

    # Execute all API calls concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Extract overall scores safely, handling exceptions
    predictions = []
    for index, res in enumerate(results):
        try:
            if isinstance(res, Exception):
                raise res  # Re-raise exception to handle it below
            score = get_overall_score(res)
            predictions.append(score)
            bt.logging.info(
                f"Score for product {synapse.query[index]}: {score}")
        except Exception as e:
            print(f"Error processing result: {e}")
            predictions.append(None)  # Default value or handle differently

    synapse.response = predictions
    return synapse
