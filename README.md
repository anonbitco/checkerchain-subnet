<div align="center">

# CheckerChain SN__: Next-Gen AI-powered Trustless Crypto Review Platform <!-- omit in toc -->


Check our [Whitepaper](https://docs.checkerchain.com/whitepaper/checkerchain-whitepaper-v2.0) for in-depth study on tRCM protocol of CheckerChain.

[![CheckerChain](https://github.com/CheckerChain/CheckerChain-Asset/blob/4b0c738e6233ae019e772d24212a99800b4e1e84/CheckerChain-Twitter-Cover.png)](https://checkerchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

</div>

---
- [Overview](#overview)
- [Subnet Introduction](#subnet-introduction)
  - [Roadmap](#roadmap)
- [Miner](#miner)
  - [Requirements](#requirements)
  - [Running Miner](#running-miner)
- [Validator](#validator)
  - [Requirements](#requirements)
  - [Running Validator](#running-validator)
- [Game Theory on Subnet With tRCM](#game-theory-on-subnet-with-trcm)
- [Resources of CheckerChain](#resources-of-checkerchain)
- [Contributing](#contributing)
- [License](#license)

---
## Overview

CheckerChain is a next-gen AI-powered crypto review platform that powers a trustless review consensus mechanism (tRCM). In tRCM protocol, anyone can participate but the protocol selects the reviewers arbitrarily to review a product. Selected reviewers can only get reward for their work when their review score falls in consensus range. Closer the consensus, more the reward.

Reviewers have a higher probability to make their review closer to consensus only when they are honest. Any dishonest review by any reviewer falls outside of consensus. This generates no or least reward making dishonest reviews highly expensive to perform. This will eventually discourage such attackers from participating in the tRCM protocol.


---

## Subnet Introduction

CheckerChain subnet operates as a decentralized AI-powered prediction layer, continuously refining review scores through machine learning. It is structured into two key components: validators and miners. Validators play a crucial role in distributing product review tasks to miners and aggregating the Ground Truth ratings collected from the main platform. They evaluate miner-generated predictions, benchmarking them against the Ground Truth to ensure accuracy. By maintaining a competitive environment, validators score miners to optimize their models for better precision and efficiency.

Miners, on the other hand, are responsible for running AI models that predict review scores for listed products. These models evolve over time by learning from past predictions and adjusting their algorithms based on discrepancies with the Ground Truth. Through Reinforcement Learning from Human Feedback (RLHF), miners incorporate additional insights from validators and human reviewers, ensuring their models align more closely with real-world assessments. This continuous feedback loop allows the subnet to improve autonomously, reducing biases and increasing reliability in AI-driven ratings.

The subnet follows a decentralized learning and incentive structure, where AI models start with predefined datasets and historical review scores. Over time, miners fine-tune their models by comparing predictions with Ground Truth data, optimizing accuracy through RLHF. Validators play a key role in integrating tRCM-based human feedback into the training process, refining AI predictions iteratively. As a result, miners that consistently produce high-accuracy predictions receive higher benchmarks and greater rewards, creating a self-reinforcing cycle of improvement.

By combining tRCM human-decentralized ratings with AI-driven predictions, CheckerChain’s subnet evolves into a self-learning, decentralized, and transparent review system. The open participation model allows anyone to join as a miner or validator, contributing to an AI-enhanced ecosystem that continuously adapts to real-world opinions. This fusion of human intelligence and AI automation ensures a fair, scalable, and corruption-resistant review platform, setting a new standard for decentralized trust in product evaluations.

### Roadmap
**Phase 1:** 
- [x] Subnet launch 
- [ ] Leaderboard with scoring methods

**Phase 2:** 
- [ ] Integration of Subnet output with CheckerChain dApp
- [ ] Third-party widget release

**Phase 3:** 
- [ ] Optimization of subnet logic

---

## Miner

### Requirements
Before you proceed with the installation of the subnet, note the following: 


### Running Miner

- **Running locally**: Follow the step-by-step instructions described in this section: [Running Subnet Locally](./docs/running_on_staging.md).
- **Running on Bittensor testnet**: Follow the step-by-step instructions described in this section: [Running on the Test Network](./docs/running_on_testnet.md).
- **Running on Bittensor mainnet**: Follow the step-by-step instructions described in this section: [Running on the Main Network](./docs/running_on_mainnet.md).

---

## Validator

### Requirements
Before you proceed with the installation of the subnet, note the following:

### Running Validator

---

## Game Theory on Subnet With tRCM


## Resources of CheckerChain

## Contributing


## License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2025 CheckerChain

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
```
