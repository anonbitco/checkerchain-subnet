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

from template.protocol import CheckerChainSynapse
from template.utils.sqlite_utils import add_prediction, delete_a_product, get_predictions_for_product, get_products
from template.validator.reward import get_rewards
from template.utils.uids import get_random_uids
from neurons.validator import Validator
from template.utils.checker_chain import fetch_products


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
    miner_uids = [5]
    # The dendrite client queries the network.
    # define product id to get scores for

    data = fetch_products()
    queries = data.unmined_products  # get product ids from checker chain api
    if (len(queries) > 0):
        # if voting is closed or open
        responses: list = await self.dendrite(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            # Construct a dummy query. This simply contains a single integer.
            synapse=CheckerChainSynapse(query=queries),
            # All responses have the deserialize function called on them before returning.
            # You are encouraged to define your own deserialization function.
            deserialize=True,
        )
        # Log the results for monitoring purposes.
        bt.logging.info(f"Received responses: {responses}")
        # add all responses to database predictions table;
        for miner_uid, miner_predictions in zip(miner_uids, responses):
            # Since input is array of product_ids, response must be array of predictions
            for product_id, prediction in zip(queries, miner_predictions):
                add_prediction(product_id, miner_uid, prediction)

    # Get one product which has been reviewed and is ready to score.
    # Adjust the scores based on responses from miners.
    if (len(data.reward_items) > 0):
        reward_product = data.reward_items[0]
        product_predictions = get_predictions_for_product(reward_product._id)
        if not product_predictions:
            product_predictions = []
        predictions = [p["prediction"] for p in product_predictions]
        miner_ids = [p["miner_id"] for p in product_predictions]
        if reward_product:
            rewards = get_rewards(
                self,
                reward_product,
                responses=predictions,
            )
    else:
        rewards = np.zeros_like(miner_uids)

    bt.logging.info(f"Scored responses: {rewards}")
    self.update_scores(rewards, miner_ids)
    if reward_product:
        # Delete the product and predictions from the database since the product reward has been distributed
        delete_a_product(reward_product._id)
    # TODO: One minute until next validation ??
    time.sleep(60)
