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
Miner is responsible for LLM-based evaluation of products to generate and submit the prediction of Trust Score for each reviewed product.  

### **Steps to Generate Predictions:**  
1. **Loop through product IDs** to fetch product details.  
2. Use any reasoning AI-models.
- OpenAI Models (including `gpt-4`)
- Anthropic Models (including `claude-3-5-sonnet-20241022`)
**Construct a ChatGPT prompt** with relevant product parameters.
3. **Generate AI-based scores**, including:  
   - **Overall Score (out of 100)**  
   - **Breakdown Scores** for key evaluation criteria.  
4. **Calculate the final Trust Score** using a weighted aggregation function.  
5. **Return the Trust Score** to the Validator for processing.  

✅ Customizable Weighting System – Allows different importance levels for various scoring parameters.  


### Requirements
Before you proceed with the installation of the subnet, note the following: 


### Running Miner

- **Running locally**: Follow the step-by-step instructions described in this section: [Running Subnet Locally](./docs/running_on_staging.md).
- **Running on Bittensor testnet**: Follow the step-by-step instructions described in this section: [Running on the Test Network](./docs/running_on_testnet.md).
- **Running on Bittensor mainnet**: Follow the step-by-step instructions described in this section: [Running on the Main Network](./docs/running_on_mainnet.md).

---

## Validator
Validator is responsible for fetching products from CheckerChain dApp, distributing review tasks to miners, tracking their review status, storing miner predictions, and distributing rewards based on accuracy.  

### **Step 1: Fetch Products**  
- Retrieves products from the **CheckerChain**.  
- If a product has **status = "published"** and **is not in the database**, it is added to the **unmined list** and stored in the database.  
- If a product has **status = "reviewed"** and **is already in the database**, it is added to the **reward list** for further processing.  

### **Step 2: Store Miner Predictions**  
- Fetches predictions from **all miners** for products in the **unmined list**.  
- Stores predictions in the **prediction table**, including:  
  - **Miner UID**  
  - **Product ID**  
  - **Predicted Score**  

### **Step 3: Scoring Mechanism**  
- Implements the scoring mechanism to rank miners and provide weights
- Miners are ranking based on cummulative average of the absolute error between the predicted trust score and the actual trust score at the evaluation time.
- Miner with lowest error ranks best and assigned the best weight.  


### **Step 4: Reward Distribution**  
- If the **reward list is empty**, initialize an array of zeros (length = number of miners) and update rewards accordingly.  
- Otherwise:  
  - Select **one product** from the **reward list**.  
  - Retrieve **all miner predictions** for that product.  
  - Compute **scores based on the difference between predicted scores and the actual trust score**.  
  - Update miner rewards accordingly.  
  - Remove the product from the database after processing.

✅ Dynamic Database

---

### Requirements
Before you proceed with the installation of the subnet, note the following: 

### Running Validator

---

## Game Theory on Subnet With tRCM
Subnet works on Reinforcement Learning Through Human Feedback (RLHF) on ground truths of tRCM. tRCM is an acronym for trustless Review Consensus Mechanism. It is the core protocol utilized on CheckerChain to make reviews trustless.

tRCM is based on 2 assumptions for a review to hold any authentic value:
- reviews are performed in zero-knowledge proofs without any control of either the poster or the reviewer.
- honest reviewers in the protocol always establish a majority

In tRCM protocol, anyone can participate but the protocol selects the reviewers arbitrarily to review a product. Selected reviewers can only get reward for their work when their review score falls in consensus range. Closer the consensus, more the reward. Reviewers have a higher probability to make their review closer to consensus only when they are honest. Any dishonest review by any reviewer falls outside of consensus. This generates no or least reward making dishonest reviews highly expensive to perform. This will eventually discourage such attackers from participating in the tRCM protocol. 

These scores are vital parameters to derive incentives for each contribution.

- Trust Score: This is an atomic data of a product calculated from reviewer's task. It represents rating of a product in the range of 0 to 100.
- Normalized Trust Score: This is a derived data of a product calculated from Trust score to determine the impact on reward.
- Rating Score: This is a derived data of a product calculated as Trust score out of 5 and processed with Bayesian Average.

When a product gets listed on CheckerChain, tRCM protocol enacts on 30+ parameters of 10 categories to generate these vital scores. And subnet miners need to optimize their AI model to predict the best possible matching trust score.

## Resources of CheckerChain
|  | Links    | Notes    |
| :---:   | :---: | :---: |
| Application | https://checkerchain.com   | Mainnet is Live   |
| Leaderboard |  |  |


## Contributing
Create a PR to this repo. At least 1 reviewer approval required.

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
