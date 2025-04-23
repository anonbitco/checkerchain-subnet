# Running Miner/Validator on CheckerChain Subnet

## Prerequisites

Before proceeding further, make sure that you have installed Bittensor. See the below instructions:

- [Install `bittensor`](https://github.com/opentensor/bittensor#install).

After installing `bittensor`, proceed as below:

## 1. Install Checker Chain Subnet

`cd` into your project directory and clone the checkerchain-subnet repo:

```bash
git clone https://github.com/CheckerChain/checkerchain-subnet.git
```

Next, `cd` into checkerchain-subnet repo directory:

```bash
cd checkerchain-subnet # Enter the
```

### Manual steps:

#### Create Python Virtual Environment:

```bash
python -m venv .venv

```

#### Activate venv:

```bash
source .venv/bin/activate  #use wsl2 for windows
```

#### Install the checkerchain-subnet package:

```bash
python -m pip install -e .
```

## Using Scripts (It will delete checker_db.db file):

#### Validator

```bash
chmod +x scripts/setup_vali.sh
./scripts/setup_vali.sh
```

#### Miner

```bash
chmod +x scripts/setup_miner.sh
./scripts/setup_miner.sh
```

#### Activate Venv

```bash
source .venv/bin/activate
```

## 2. Create wallets

Create wallets subnet validator or subnet miner.

This step creates local coldkey and hotkey pairs for either subnet validator or subnet miner.
The validator or miner will be registered to the subnet

Create a coldkey and hotkey for miner wallet:

```bash
btcli wallet new_coldkey --wallet.name miner
```

and

```bash
btcli wallet new_hotkey --wallet.name miner --wallet.hotkey default
```

Create a coldkey and hotkey for validator wallet:

```bash
btcli wallet new_coldkey --wallet.name validator
```

and

```bash
btcli wallet new_hotkey --wallet.name validator --wallet.hotkey default
```

## 3. (Optional) Get faucet tokens

Faucet is disabled on the testnet. Hence, if you don't have sufficient faucet tokens, ask the [Bittensor Discord community](https://discord.com/channels/799672011265015819/830068283314929684) for faucet tokens.

## 4. Register keys

**_Testnet NETUID: `315`_** \
**_Mainnet NETUID: `87`_**

#### Registering Miner

This step registers subnet miner key to the subnet.

Copy `.env.example` to `.env` and update your `OPENAI_API_KEY`

Register your miner key to the subnet:\
\***\*Add `--subtensor.network test` for testnet\*\***

```bash
btcli subnet register --netuid 87 --wallet.name miner --wallet.hotkey default
```

Follow the below prompts:

```bash
>> Enter netuid [1] (1): # Enter netuid depending upon the network you want to register for
>> Continue Registration?
  hotkey:     ...
  coldkey:    ...
  network:    finney [y/n]: # Select yes (y)
>> ✅ Registered
```

#### Registering Validator

This step registers subnet validator key to the subnet.

Register your validator key to the subnet:\
\***\*Add `--subtensor.network test` for testnet\*\***

```bash
btcli subnet register --netuid 87 --wallet.name validator --wallet.hotkey default
```

Follow the prompts:

```bash
>> Enter netuid [1] (1): # Enter netuid depending upon the network you want to register for
>> Continue Registration?
  hotkey:     ...
  coldkey:    ...
  network:    finney [y/n]: # Select yes (y)
>> ✅ Registered
```

## 5. Check that your keys have been registered

\***\*Add `--subtensor.network test` for testnet\*\***

This step returns information about your registered keys.

Check that your validator key has been registered:

```bash
btcli wallet overview --wallet.name validator
```

The above command will display the below:

```bash
Subnet: 315
COLDKEY  HOTKEY   UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58
miner    default  0      True   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000                14  none  5GTFrsEQfvTsh3WjiEVFeKzFTc2xcf…
1        1        2            τ0.00000  0.00000  0.00000    0.00000    0.00000    0.00000           ρ0  0.00000
                                                                          Wallet balance: τ0.0
```

Check that your miner has been registered:

```bash
btcli wallet overview --wallet.name miner
```

The above command will display the below:

```bash
Subnet: 315
COLDKEY  HOTKEY   UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58
miner    default  1      True   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000                14  none  5GTFrsEQfvTsh3WjiEVFeKzFTc2xcf…
1        1        2            τ0.00000  0.00000  0.00000    0.00000    0.00000    0.00000           ρ0  0.00000
                                                                          Wallet balance: τ0.0
```

## 6. Run subnet miner Or subnet validator

Run the subnet miner:

```bash
python neurons/miner.py --netuid 87 --wallet.name miner --wallet.hotkey default --logging.debug
```

Next, run the subnet validator:

```bash
python neurons/validator.py --netuid 87 --wallet.name validator --wallet.hotkey default --logging.debug
```

## 7. Stopping your nodes

To stop your nodes, press CTRL + C in the terminal where the nodes are running.

Sure! Here's a more detailed and well-formatted section for a **GitHub `README.md`** to help miners troubleshoot and ensure their setup is correct:

---

# 🛠️ Troubleshooting: Not Receiving Mine Requests?

If your miner is not receiving mine requests while others are, it's likely an issue on your end. Here's a step-by-step checklist to help you diagnose and resolve it:

### ✅ 1. Check if Your IP and Port Are Publicly Accessible

Your miner must be reachable from the public internet. To verify:

- Open a browser and navigate to your miner’s IP and port:

  ```
  http://<your-ip>:<your-port>
  ```

  For example:

  ```
  http://65.109.76.55:8091
  ```

- If it's working correctly, you should see a response like this:

  ```json
  {
    "message": "Synapse name '' not found. Available synapses ['Synapse', 'CheckerChainSynapse']"
  }
  ```

> 🔒 **Tip:** If you see a "connection refused" or "timeout" error, your port is likely closed. Check your firewall rules and VPS provider’s network configuration.

---

### 🚀 2. Ensure Miner Is Running in Background

If your miner isn't running persistently, it won't handle any incoming requests. Use **PM2**, a production-grade process manager for Node.js and Python apps, to keep your miner alive and restart on failure or reboot.

#### 🔧 PM2 Installation & Usage

```bash
# Install PM2 globally
npm install -g pm2

# Navigate to your miner directory
cd /path/to/miner

# Start the miner with PM2
PYTHONPATH=. pm2 start neurons/miner.py   --interpreter /checkerchain/checkerchain-subnet/.venv/bin/python   --name miner   --   --netuid 87   --wallet.name miner-wallet  --wallet.hotkey default --axon.port 8091   --logging.debug

# Save the process list to start on boot
pm2 save
pm2 startup
```

> 🧠 You can view logs using:
>
> ```bash
> pm2 logs miner
> ```

> 📌 To stop or restart:
>
> ```bash
> pm2 stop miner
> pm2 restart miner
> ```

---

### 🧪 3. Final Checklist

- [ ] Is your `ip:port` reachable from a browser?
- [ ] Is your firewall or VPS provider allowing inbound traffic on that port?
- [ ] Is your miner process running in the background (PM2 recommended)?
- [ ] Are you using the correct netuid and wallet keys?

### Topic: How can Miner Compete?

In the CheckerChain subnet, miners play a crucial role in evaluating and scoring products based on trust signals. Here's how miners can effectively compete and contribute:

#### ✅ Phase 1 Reward Distribution

- **90% of miners will be rewarded** based on the quality of their responses.
- Emphasis is on **accuracy**.

#### 🧠 Model Strategy

- Miners have two main paths:
  - **Train their own AI models** tailored to predict trust scores.
  - **Leverage robust existing models** (like GPT, Claude, etc.) for reliable outputs.

#### 📝 Prompt Engineering

- Miners can **design their own prompts** to extract high-quality, relevant insights.
- Prompt creativity can lead to predictions that closely match the **actual trust score**.
- Iterative refinement of prompts improves score alignment over time.

#### 🔐 Reliability and Uptime

- Ensure miner nodes are **always available and responsive**.
- Use tools like `pm2` or Docker for stability in production environments.

#### 🧪 Experiment and Iterate

- Regularly test new scoring strategies, datasets, or prompt variations.
- Use the testing environment to **benchmark changes** before deploying them live.

---

> 🚀 The goal is to be consistently close to the validator-approved trust scores. Those who optimize both **model accuracy** and **prompt quality** will thrive in the competition.
