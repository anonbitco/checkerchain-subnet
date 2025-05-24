# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
import numpy as np
from typing import List
import bittensor as bt
from typing import List, Dict

from checkerchain.types.checker_chain import ReviewedProduct


# def normalize(value: float, min_val: float, max_val: float) -> float:
#     """Normalize deviation so that 0 deviation gives a score of 1, and larger deviations get lower scores."""
#     if min_val == max_val:
#         return 1.0  # If no deviation, return full score
#     return 1 - ((value - min_val) / (max_val - min_val))


# def compare_and_normalize(
#     predictions: List[Dict[str, float]], actuals: List[Dict[str, float]]
# ) -> Dict[str, float]:
#     """Compare predictions and actual scores, compute variations, sum them up, and return a normalized score."""
#     variations = []

#     for act in actuals:
#         _id = act["_id"]
#         actual_score = act["trustScore"]
#         predicted_score = next(
#             (pred["prediction"] for pred in predictions if pred["_id"] == _id), 0
#         )
#         variations.append(abs(actual_score - predicted_score))
#     total_variation = sum(variations)
#     normalized_variation = normalize(
#         total_variation, min(variations, default=0), max(variations, default=1)
#     )

#     return normalized_variation


# def reward(
#     predictions: List[Dict[str, float]], actuals: List[Dict[str, float]]
# ) -> float:
#     """
#     Reward the miner response to the dummy request. This method returns a reward
#     value for the miner, which is used to update the miner's score.

#     Returns:
#     - float: The reward value for the miner.
#     """
#     if not predictions:
#         score = 0
#     else:
#         score = compare_and_normalize(predictions, actuals)
#     bt.logging.info(f"In rewards,rewards val: {score}")
#     return score


# def get_rewards(
#     self,
#     last_epoch_reviewed_products: List[Dict[str, int | str]],
#     responses: List[List[Dict[str, int | str]]],
# ) -> np.ndarray:
#     """
#     Returns an array of rewards for the given query and responses.

#     Args:
#     - query (int): The query sent to the miner.
#     - responses (List[float]): A list of responses from the miner.

#     Returns:
#     - np.ndarray: An array of rewards for the given query and responses.
#     """
#     # Get all the reward results by iteratively calling your reward() function.

#     return np.array(
#         [reward(response, last_epoch_reviewed_products) for response in responses]
#     )


def reward(prediction: float | None, actual: float) -> float:
    """
    Reward the miner response to the dummy request. This method returns a reward
    value for the miner, which is used to update the miner's score.

    Returns:
    - float: The reward value for the miner.
    """
    score = 0
    if prediction:
        score = 100 - abs(prediction - actual)
    return score


def get_rewards(
    self,
    reviewed_product: ReviewedProduct,
    responses: List[float | None],
) -> np.ndarray:
    """
    Returns an array of rewards for the given query and responses.

    Args:
    - query (int): The query sent to the miner.
    - responses (List[float]): A list of responses from the miner.

    Returns:
    - np.ndarray: An array of rewards for the given query and responses.
    """
    if reviewed_product.trustScore == 0:
        return np.zeros(len(responses), dtype=np.float32)

    rewards_dict = {
        i: reward(r, reviewed_product.trustScore)
        for i, r in enumerate(responses)
    }

    # Get all the reward results by iteratively calling your reward() function.
    final_rewards = [rewards_dict.get(i, 0.0) for i in range(len(responses))]
    return np.array(final_rewards, dtype=np.float32)
