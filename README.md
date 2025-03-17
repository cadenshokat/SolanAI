# SolanAI

SolanAI is a real-time analytics platform that collects on-chain data from the Solana blockchain—such as new coin listings, wallet tracking, liquidity events, and more—and merges it with off-chain social sentiment (e.g., trending Twitter topics). By providing holistic, data-driven insights, SolanAI aims to help users discover potentially profitable opportunities in the fast-moving world of Solana meme coins and beyond.

---

## Table of Contents

1. [Features](#features)  
2. [Project Structure](#project-structure)  
3. [Installation & Setup](#installation--setup)  
4. [Usage](#usage)  
5. [Roadmap](#roadmap)  
6. [Contributing](#contributing)  
7. [License](#license)  
8. [Contact](#contact)

---

## Features

- **New Coin & Bonding Curve Tracking**  
  - Reverse-engineers APIs to identify newly listed coins and those about to graduate bonding curves.  
  - Provides key financial metrics and status indicators for each coin.

- **Whale Transactions**  
  - Monitors high-value Solana transactions in real time.  
  - Flags token buys above a specified threshold (e.g., \$1,000) to detect potential market movers.

- **Wallet Tracker**  
  - Gathers recent transactions from specified wallet addresses.  
  - Aggregates and highlights when multiple wallets buy the same token simultaneously.

- **Liquidity Add Listener**  
  - Uses Flask, Serveo, and Helium webhooks to detect liquidity-adding transactions on AMMs like Raydium and Meteora.  
  - Records relevant data (e.g., token, timestamp, volume) for analysis.

- **Twitter Scraper & Sentiment Analysis**  
  - Scrapes Twitter for coin mentions, engagement metrics, and sentiment scores.  
  - Identifies spikes in social sentiment that may correlate with price action.

- **React Front End**  
  - Displays aggregated data in a clean, modern interface.  
  - Offers quick insights via charts, tables, and live updates.

- **(Planned) Machine Learning Integration**  
  - Aims to correlate historical data (price, sentiment, liquidity, transactions) to predict optimal entry points for trades.

---

## Project Structure


- **frontend/**  
  Contains the React application responsible for the user interface and data visualization.

- **src/**  
  Houses Python scripts and modules that gather, filter, and process on-chain and off-chain data.

- **ml_liquidity_detector/**  
  (Placeholder for future ML integration) Includes scripts, notebooks, or pipelines for machine learning experiments and model training.

---

## Installation & Setup

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/cadenskelaot/SolanAI.git
   cd SolanAI
