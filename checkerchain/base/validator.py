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


import copy
import numpy as np
import asyncio
import argparse
import threading
import bittensor as bt

from typing import List, Union
from traceback import print_exception

from checkerchain.base.neuron import BaseNeuron
from checkerchain.base.utils.weight_utils import (
    process_weights_for_netuid,
    convert_weights_and_uids_for_emit,
)  # TODO: Replace when bittensor switches to numpy
from checkerchain.mock import MockDendrite
from checkerchain.utils.config import add_validator_args


class BaseValidatorNeuron(BaseNeuron):
    """
    Base class for Bittensor validators. Your validator should inherit from this class.
    """

    neuron_type: str = "ValidatorNeuron"

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        super().add_args(parser)
        add_validator_args(cls, parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        # Save a copy of the hotkeys to local memory.
        self.hotkeys = copy.deepcopy(self.metagraph.hotkeys)

        # Dendrite lets us send messages to other nodes (axons) in the network.
        if self.config.mock:
            self.dendrite = MockDendrite(wallet=self.wallet)
        else:
            self.dendrite = bt.dendrite(wallet=self.wallet)
        bt.logging.info(f"Dendrite: {self.dendrite}")

        # Set up initial scoring weights for validation
        bt.logging.info("Building validation weights.")
        self.scores = np.zeros(self.metagraph.n, dtype=np.float32)
        self.last_scores = np.zeros(self.metagraph.n, dtype=np.float32)
        self.latest_miner_performance = {} # Initialize this attribute

        # Init sync with the network. Updates the metagraph.
        try:
            self.load_state()
        except FileNotFoundError:
            bt.logging.warning("No state found. Initializing new state.")

        self.step = 0

        self.sync()

        # --- UID Check ---
        # TODO: Make TARGET_UID configurable (e.g., via config or environment variable)
        TARGET_UID = 249
        if hasattr(self, 'uid'):
            if self.uid == TARGET_UID:
                bt.logging.info(f"Validator confirmed to be running with target UID: {self.uid}.")
            else:
                bt.logging.error(f"Validator UID is {self.uid}, but expected {TARGET_UID}. Please ensure the correct hotkey is configured.")
        else:
            # This case should ideally not happen if sync() is called and works correctly.
            bt.logging.error("Validator UID (self.uid) not found after sync. Cannot perform target UID check.")
        # --- End UID Check ---

        # Serve axon to enable external connections.
        if not self.config.neuron.axon_off:
            self.serve_axon()
        else:
            bt.logging.warning("axon off, not serving ip to chain.")

        # Create asyncio event loop to manage async tasks.
        self.loop = asyncio.get_event_loop()

        # Instantiate runners
        self.should_exit: bool = False
        self.is_running: bool = False
        self.thread: Union[threading.Thread, None] = None
        self.lock = asyncio.Lock()

    def serve_axon(self):
        """Serve axon to enable external connections."""

        bt.logging.info("serving ip to chain...")
        try:
            self.axon = bt.axon(wallet=self.wallet, config=self.config)

            try:
                self.subtensor.serve_axon(
                    netuid=self.config.netuid,
                    axon=self.axon,
                )
                bt.logging.info(
                    f"Running validator {self.axon} on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
                )
            except Exception as e:
                bt.logging.error(f"Failed to serve Axon with exception: {e}")
                pass

        except Exception as e:
            bt.logging.error(f"Failed to create Axon initialize with exception: {e}")
            pass

    async def concurrent_forward(self):
        coroutines = [
            self.forward() for _ in range(self.config.neuron.num_concurrent_forwards)
        ]
        await asyncio.gather(*coroutines)

    def run(self):
        """
        Initiates and manages the main loop for the miner on the Bittensor network. The main loop handles graceful shutdown on keyboard interrupts and logs unforeseen errors.

        This function performs the following primary tasks:
        1. Check for registration on the Bittensor network.
        2. Continuously forwards queries to the miners on the network, rewarding their responses and updating the scores accordingly.
        3. Periodically resynchronizes with the chain; updating the metagraph with the latest network state and setting weights.

        The essence of the validator's operations is in the forward function, which is called every step. The forward function is responsible for querying the network and scoring the responses.

        Note:
            - The function leverages the global configurations set during the initialization of the miner.
            - The miner's axon serves as its interface to the Bittensor network, handling incoming and outgoing requests.

        Raises:
            KeyboardInterrupt: If the miner is stopped by a manual interruption.
            Exception: For unforeseen errors during the miner's operation, which are logged for diagnosis.
        """

        # Check that validator is registered on the network.
        self.sync()

        bt.logging.info(f"Validator starting at block: {self.block}")

        # This loop maintains the validator's operations until intentionally stopped.
        try:
            while True:
                bt.logging.info(f"step({self.step}) block({self.block})")

                # Run multiple forwards concurrently.
                self.loop.run_until_complete(self.concurrent_forward())

                # Check if we should exit.
                if self.should_exit:
                    break

                # Sync metagraph and potentially set weights.
                self.sync()

                self.step += 1

        # If someone intentionally stops the validator, it'll safely terminate operations.
        except KeyboardInterrupt:
            self.axon.stop()
            bt.logging.success("Validator killed by keyboard interrupt.")
            exit()

        # In case of unforeseen errors, the validator will log the error and continue operations.
        except Exception as err:
            bt.logging.error(f"Error during validation: {str(err)}")
            bt.logging.debug(str(print_exception(type(err), err, err.__traceback__)))

    def run_in_background_thread(self):
        """
        Starts the validator's operations in a background thread upon entering the context.
        This method facilitates the use of the validator in a 'with' statement.
        """
        if not self.is_running:
            bt.logging.debug("Starting validator in background thread.")
            self.should_exit = False
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.is_running = True
            bt.logging.debug("Started")

    def stop_run_thread(self):
        """
        Stops the validator's operations that are running in the background thread.
        """
        if self.is_running:
            bt.logging.debug("Stopping validator in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def __enter__(self):
        self.run_in_background_thread()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the validator's background operations upon exiting the context.
        This method facilitates the use of the validator in a 'with' statement.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
                      None if the context was exited without an exception.
            exc_value: The instance of the exception that caused the context to be exited.
                       None if the context was exited without an exception.
            traceback: A traceback object encoding the stack trace.
                       None if the context was exited without an exception.
        """
        if self.is_running:
            bt.logging.debug("Stopping validator in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def set_weights(self):
        """
        Sets the validator weights to the metagraph hotkeys based on the scores it has received from the miners. The weights determine the trust and incentive level the validator assigns to miner nodes on the network.
        """
        # Initialize ranked_scores array.
        ranked_scores = np.zeros(self.metagraph.n, dtype=np.float32)
        bt.logging.info("Starting set_weights operation.")

        if not hasattr(self, 'latest_miner_performance') or not self.latest_miner_performance:
            bt.logging.warning("No latest_miner_performance data available. Skipping rank-based weight setting. Setting all weights to zero.")
            # ranked_scores is already initialized to zeros.
        else:
            bt.logging.info(f"Using latest_miner_performance (first 5 items): {dict(list(self.latest_miner_performance.items())[:5])}...")
            bt.logging.debug(f"Full latest_miner_performance: {self.latest_miner_performance}")

            # Rank miners based on accuracy_score.
            # Sort by accuracy_score in descending order.
            # self.latest_miner_performance is {uid: accuracy_score}
            sorted_miners = sorted(self.latest_miner_performance.items(), key=lambda item: item[1], reverse=True)
            
            num_ranked_miners = len(sorted_miners)
            bt.logging.info(f"Ranking {num_ranked_miners} miners based on performance.")
            for rank, (uid, accuracy_score) in enumerate(sorted_miners):
                if uid < self.metagraph.n: # Ensure UID is valid for the current metagraph
                    # Assign weight based on rank: N - rank
                    ranked_scores[uid] = num_ranked_miners - rank
                else:
                    bt.logging.warning(f"UID {uid} from latest_miner_performance is out of bounds for metagraph (size {self.metagraph.n}). Skipping.")
            
            initial_ranked_scores_summary = {uid: score for uid, score in enumerate(ranked_scores) if score > 0}
            bt.logging.info(f"Initial ranked scores (before dividend check) summary: {initial_ranked_scores_summary}")
            bt.logging.debug(f"Full initial ranked_scores before dividend check: {ranked_scores.tolist()}")

        # Dividend Check: Iterate through all UIDs and zero out scores for those with dividends > 0.
        # This must happen *after* initial rank-based weights are assigned.
        uids_actively_zeroed_by_dividend = []
        uids_already_zero_with_dividend = []

        for uid_check in self.metagraph.uids:
            # Ensure uid_check is within the bounds of ranked_scores and metagraph.dividends
            if uid_check < len(ranked_scores) and uid_check < len(self.metagraph.dividends):
                if self.metagraph.dividends[uid_check] > 0:
                    current_score = ranked_scores[uid_check]
                    if current_score > 0:
                        bt.logging.info(f"UID {uid_check} (score: {current_score}) has non-zero dividends ({self.metagraph.dividends[uid_check]}). Actively setting its ranked_score to 0.")
                        ranked_scores[uid_check] = 0
                        uids_actively_zeroed_by_dividend.append(uid_check)
                    else:
                        # Score was already zero, but has dividend. Just log this fact.
                        bt.logging.info(f"UID {uid_check} (score: {current_score}) has non-zero dividends ({self.metagraph.dividends[uid_check]}). Score was already 0.")
                        uids_already_zero_with_dividend.append(uid_check)
            else:
                bt.logging.warning(f"UID {uid_check} is out of bounds for ranked_scores or metagraph.dividends during dividend check. Metagraph size: {self.metagraph.n}")

        if uids_actively_zeroed_by_dividend:
            bt.logging.info(f"UIDs actively zeroed out due to dividends: {uids_actively_zeroed_by_dividend}")
        else:
            bt.logging.info("No UIDs had their scores actively changed from non-zero to zero due to dividends this round.")
        
        if uids_already_zero_with_dividend:
            bt.logging.info(f"UIDs that already had zero score but possess non-zero dividends: {uids_already_zero_with_dividend}")
        
        final_ranked_scores_summary = {uid: score for uid, score in enumerate(ranked_scores) if score > 0}
        bt.logging.info(f"Ranked scores (after dividend check) summary: {final_ranked_scores_summary}")
        bt.logging.debug(f"Full ranked_scores after dividend check: {ranked_scores.tolist()}")

        # Check if ranked_scores contains any NaN values and log a warning if it does.
        # This shouldn't happen with the current rank-based logic unless latest_miner_performance contained NaNs.
        if np.isnan(ranked_scores).any():
            bt.logging.warning(
                f"Ranked scores contain NaN values. This may indicate an issue with accuracy_score data."
            )
            ranked_scores = np.nan_to_num(ranked_scores, nan=0.0) # Replace NaNs with 0

        # Compute the norm of the ranked_scores
        norm = np.linalg.norm(ranked_scores, ord=1, axis=0, keepdims=True)

        # Check if the norm is zero or contains NaN values
        if np.any(norm == 0) or np.isnan(norm).any():
            bt.logging.warning("Norm of ranked_scores is zero or NaN. All miner scores might be zero or no miners participated/ranked.")
            if np.any(norm == 0): # More specific check for zero norm
                 raw_weights = np.zeros_like(ranked_scores, dtype=float)
            else: # Handles NaN case by previous logic or could be more specific
                 norm = np.ones_like(norm) # Fallback for NaN to prevent division error
                 raw_weights = ranked_scores / norm
        else:
            raw_weights = ranked_scores / norm
        
        raw_weights_summary = {uid: weight for uid, weight in enumerate(raw_weights) if weight > 0}
        bt.logging.info(f"Raw weights (before processing) summary: {raw_weights_summary}")
        bt.logging.debug(f"Full raw_weights: {raw_weights.tolist()}")
        bt.logging.debug(f"UIDs for raw_weights (metagraph.uids): {str(self.metagraph.uids.tolist())}")

        # NEW CONDITIONAL BLOCK STARTS HERE
        if np.all(raw_weights == 0):
            bt.logging.info("All raw_weights are zero. Preparing to set no weights on chain (processed_weights will be empty).")
            processed_weight_uids = np.array([])
            processed_weights = np.array([])
        else:
            # Process the raw weights to final_weights via subtensor limitations.
            (
                processed_weight_uids,
                processed_weights,
            ) = process_weights_for_netuid(
                uids=self.metagraph.uids,
                weights=raw_weights,
                netuid=self.config.netuid,
                subtensor=self.subtensor,
                metagraph=self.metagraph,
            )
        # NEW CONDITIONAL BLOCK ENDS HERE
        
        bt.logging.info(f"Processed weight UIDs (first 10): {processed_weight_uids.tolist()[:10]}...")
        bt.logging.info(f"Processed weights (first 10): {processed_weights.tolist()[:10]}...")
        bt.logging.debug(f"Full processed_weight_uids: {processed_weight_uids.tolist()}")
        bt.logging.debug(f"Full processed_weights: {processed_weights.tolist()}")

        # Convert to uint16 weights and uids.
        (
            uint_uids,
            uint_weights,
        ) = convert_weights_and_uids_for_emit(
            uids=processed_weight_uids, weights=processed_weights
        )
        bt.logging.debug(f"uint_weights for emission: {uint_weights}")
        bt.logging.debug(f"uint_uids for emission: {uint_uids}")

        # Check if there are any non-zero weights to set.
        # convert_weights_and_uids_for_emit returns empty lists if all weights were zero or below threshold.
        if not uint_weights:  # This implies uint_uids will also be empty
            bt.logging.info("No non-zero weights to set for this round. Skipping chain submission.")
        else:
            # Set the weights on chain via our subtensor connection.
            bt.logging.info(f"Attempting to set {len(uint_weights)} non-zero weights on chain.")
            result, msg = self.subtensor.set_weights(
                wallet=self.wallet,
                netuid=self.config.netuid,
                uids=uint_uids,
                weights=uint_weights,
                wait_for_finalization=False,
                wait_for_inclusion=False,
                version_key=self.spec_version,
            )
            if result is True:
                bt.logging.info("set_weights on chain successfully!")
            else:
                bt.logging.error(f"set_weights failed: {msg}")
        
        bt.logging.info("Finished set_weights operation.")

    def resync_metagraph(self):
        """Resyncs the metagraph and updates the hotkeys and moving averages based on the new metagraph."""
        bt.logging.info("resync_metagraph()")

        # Copies state of metagraph before syncing.
        previous_metagraph = copy.deepcopy(self.metagraph)

        # Sync the metagraph.
        self.metagraph.sync(subtensor=self.subtensor)

        # Check if the metagraph axon info has changed.
        if previous_metagraph.axons == self.metagraph.axons:
            return

        bt.logging.info(
            "Metagraph updated, re-syncing hotkeys, dendrite pool and moving averages"
        )
        # Zero out all hotkeys that have been replaced.
        for uid, hotkey in enumerate(self.hotkeys):
            if hotkey != self.metagraph.hotkeys[uid]:
                self.scores[uid] = 0  # hotkey has been replaced

        # Check to see if the metagraph has changed size.
        # If so, we need to add new hotkeys and moving averages.
        if len(self.hotkeys) < len(self.metagraph.hotkeys):
            # Update the size of the moving average scores.
            new_moving_average = np.zeros((self.metagraph.n))
            min_len = min(len(self.hotkeys), len(self.scores))
            new_moving_average[:min_len] = self.scores[:min_len]
            self.scores = new_moving_average

        # Update the hotkeys.
        self.hotkeys = copy.deepcopy(self.metagraph.hotkeys)

    def update_scores(self, rewards: np.ndarray, uids: List[int]):
        """Performs exponential moving average on the scores based on the rewards received from the miners."""

        # Handle edge case: If either rewards or uids_array is empty.
        if not len(rewards) or not len(uids):
            bt.logging.warning("No rewards or uids provided. Skipping update.")
            return

        # Check if rewards contains NaN values.
        if np.isnan(rewards).any():
            bt.logging.warning(f"NaN values detected in rewards: {rewards}")
            # Replace any NaN values in rewards with 0.
            rewards = np.nan_to_num(rewards, nan=0)

        # Ensure rewards is a numpy array.
        rewards = np.asarray(rewards)

        # Check if `uids` is already a numpy array and copy it to avoid the warning.
        uids_array = uids
        if not isinstance(uids, np.ndarray):
            uids_array = np.array(uids)
        else:
            uids_array = uids.copy()

        # Check if sizes of rewards and uids_array match.
        if len(rewards) != len(uids_array):
            raise ValueError(
                f"Shape mismatch: rewards array of shape {rewards.shape} "
                f"cannot be broadcast to uids array of shape {uids_array.shape}"
            )

        max_uid = np.max(uids_array)
        if max_uid >= len(self.scores):
            old_size = len(self.scores)
            new_size = max_uid + 1
            bt.logging.info(
                f"Expanding scores from {old_size} to {new_size} to include new uids."
            )

            # Preserve previous scores and add zeros for new users
            new_scores = np.zeros(new_size)
            new_scores[:old_size] = self.scores
            self.scores = new_scores

        # Compute forward pass rewards, assumes uids are mutually exclusive.
        # shape: [ metagraph.n ]
        scattered_rewards: np.ndarray = np.zeros_like(self.scores)
        scattered_rewards[uids_array] = rewards
        bt.logging.debug(f"Scattered rewards: {rewards}")

        # Update scores with rewards produced by this step.
        # shape: [ metagraph.n ]
        alpha: float = self.config.neuron.moving_average_alpha
        self.scores: np.ndarray = alpha * scattered_rewards + (1 - alpha) * self.scores
        self.last_scores = copy.deepcopy(self.scores)
        bt.logging.debug(f"Updated moving avg scores: {self.scores}")

    def update_to_last_scores(self):
        """Updates the last scores to the current scores."""
        bt.logging.info("Falling back to last scores.")
        self.scores = copy.deepcopy(self.last_scores)

    def save_state(self):
        """Saves the state of the validator to a file."""
        bt.logging.info("Saving validator state.")

        # Save the state of the validator to file.
        np.savez(
            self.config.neuron.full_path + "/state.npz",
            step=self.step,
            scores=self.scores,
            hotkeys=self.hotkeys,
            last_scores=self.last_scores,
        )

    def load_state(self):
        """Loads the state of the validator from a file."""
        bt.logging.info("Loading validator state.")

        # Load the state of the validator from file.
        state = np.load(self.config.neuron.full_path + "/state.npz")
        self.step = state["step"]
        self.scores = state["scores"]
        self.hotkeys = state["hotkeys"]
        self.last_scores = state["last_scores"]
