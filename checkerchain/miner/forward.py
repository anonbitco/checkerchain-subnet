import asyncio

from neurons.miner import Miner
import checkerchain
from checkerchain.miner.llm import (
    ReviewScoreSchema,
    ScoreBreakdown,
    generate_review_score,
)
from checkerchain.utils.checker_chain import fetch_product_data
import bittensor as bt

miner_preds = {}


def get_overall_score(ai_response: ReviewScoreSchema):
    if isinstance(ai_response, ReviewScoreSchema):
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
        "partnerships": 1,
    }

    field_names = ScoreBreakdown.model_fields.keys()
    scores = {field: getattr(breakdown, field) for field in field_names}

    overall_score: float = sum(float(scores[key]) * weights[key] for key in scores)

    return round(overall_score, 2)  # Rounds the score to 2 decimal places


async def forward(self: Miner, synapse: checkerchain.protocol.CheckerChainSynapse):
    """
    Asynchronously fetch product data and generate review scores in parallel.
    Uses caching to avoid redundant OpenAI requests.
    """
    bt.logging.info(f"Received mine requests for products {synapse.query}")

    tasks = []
    product_ids = []
    predictions = [None] * len(synapse.query)  # Placeholder for responses

    for i, product_id in enumerate(synapse.query):
        if product_id in miner_preds:
            bt.logging.info(
                f"Using cached prediction for {product_id}: {miner_preds[product_id]}"
            )
            predictions[i] = miner_preds[product_id]
        else:
            product = fetch_product_data(product_id)
            if product:
                product_ids.append((i, product_id))  # To map back later
                tasks.append(generate_review_score(product))
            else:
                bt.logging.warning(f"Product not found for {product_id}")
                predictions[i] = None

    bt.logging.info("Running OpenAI scoring tasks...")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for task_index, result in enumerate(results):
        i, product_id = product_ids[task_index]
        try:
            if isinstance(result, Exception):
                raise result
            score = get_overall_score(result)
            predictions[i] = score
            miner_preds[product_id] = score  # Save to cache
            bt.logging.info(f"Score for product {product_id}: {score}")
        except Exception as e:
            bt.logging.error(f"Error scoring product {product_id}: {e}")
            predictions[i] = None

    synapse.response = predictions
    return synapse
