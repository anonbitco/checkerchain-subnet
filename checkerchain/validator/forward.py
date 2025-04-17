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

import time
import bittensor as bt
import numpy as np

from checkerchain.protocol import CheckerChainSynapse
from checkerchain.utils.sqlite_utils import (
    add_prediction,
    delete_a_product,
    get_predictions_for_product,
    get_products,
)
from checkerchain.validator.reward import get_rewards
from checkerchain.utils.uids import get_random_uids
from neurons.validator import Validator
from checkerchain.utils.checker_chain import fetch_products


async def forward(self: Validator):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """
    # TODO(developer): Define how the validator selects a miner to query, how often, etc.
    # get_random_uids is an example method, but you can replace it with your own.
    # miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)
    # miner_uids = [5]
    miner_uids = self.metagraph.uids.tolist()
    # The dendrite client queries the network.
    # define product id to get scores for

    # Fetch product data
    data = fetch_products()

    bt.logging.info(f"Products to send to miners: {data.unmined_products}")
    if len(data.reward_items):
        bt.logging.info(
            f"Products to score: {[r._id for r in data.reward_items]}")
    else:
        bt.logging.info(f"No products to score")

    queries = data.unmined_products  # Get product IDs from CheckerChain API

    responses = []
    # Query the miners if there are unmined products
    if queries:
        responses = await self.dendrite(
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            synapse=CheckerChainSynapse(query=queries),
            deserialize=True,
        )
        bt.logging.info(f"Received responses: {responses}")

        # Add all responses to the database predictions table
        for miner_uid, miner_predictions in zip(miner_uids, responses):
            for product_id, prediction in zip(queries, miner_predictions):
                add_prediction(product_id, miner_uid, prediction)

    # Get one product which has been reviewed and is ready to score.
    # Adjust the scores based on responses from miners.
    reward_product = None
    predictions = []
    miner_ids = miner_uids
    rewards = np.zeros_like(miner_uids, dtype=float)

    if data.reward_items:
        for reward_product in data.reward_items:
            product_predictions = get_predictions_for_product(
                reward_product._id) or []
            if not product_predictions:
                continue

            predictions = [p["prediction"] for p in product_predictions]
            prediction_miners = [p["miner_id"] for p in product_predictions]

            _rewards = get_rewards(self, reward_product, responses=predictions)
            print("Product ID: ", reward_product._id)
            print("Miners: ", prediction_miners)
            print("Rewards: ", _rewards)
            for miner_id, reward in zip(prediction_miners, _rewards):
                try:
                    rewards[miner_id] += reward
                except IndexError:
                    continue

    bt.logging.info(f"Scored responses: {rewards}")
    bt.logging.info(f"Score ids: {miner_ids}")
    # Ensure update_scores is always called with valid values
    self.update_scores(rewards, miner_ids)

    # If a product was processed, delete it from the database
    if data.reward_items:
        for reward_product in data.reward_items:
            delete_a_product(reward_product._id)

    # TODO: One hour until next validation ??
    time.sleep(1 * 60 * 60)
