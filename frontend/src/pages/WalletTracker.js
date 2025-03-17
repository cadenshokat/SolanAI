// src/pages/WalletTracker.js
import React, { useState, useEffect } from 'react';
import './WalletTracker.css';
import { FiCopy } from "react-icons/fi";
import { IoMdCheckmark } from "react-icons/io";

function truncateAddress(address) {
  if (!address || address.length <= 8) return address;
  return address.substring(0, 4) + "..." + address.substring(address.length - 4);
}

function formatElapsedTime(block_time, currentTime) {
  const diff = currentTime - block_time;
  if (diff < 60) {
    return `${diff}s`;
  } else if (diff < 3600) {
    const minutes = Math.floor(diff / 60);
    return `${minutes}m`;
  } else {
    const hours = Math.floor(diff / 3600);
    return `${hours}hr`;
  }
}


const WalletTracker = () => {
  // State for wallet input and list.
  const [walletInput, setWalletInput] = useState('');
  const [copiedIcon, setCopiedIcon] = useState({}); // Track copied state per row for newCoins
  const [showMessage, setShowMessage] = useState(false);
  const [message, setMessage] = useState('');
  const [wallets, setWallets] = useState(() => {
    const saved = localStorage.getItem('trackedWallets');
    return saved ? JSON.parse(saved) : [];
  });

  // State for tracker data from the wallet tracker endpoint.
  // Expect keys: hot_buys, new_hot_buys, new_transfers.
  const [trackerData, setTrackerData] = useState({
    hot_buys: {},
    new_hot_buys: {},
    new_transfers: {}
  });

  // State for coin data (from get_coin_data).
  const [coinData, setCoinData] = useState({});

  // State for wallet overview metrics.
  const [overviewMetrics, setOverviewMetrics] = useState({});

  // Accumulated transactions for each wallet.
  // Format: { walletAddress: [transaction, ...] }
  const [allTransactions, setAllTransactions] = useState(() => {
    const saved = localStorage.getItem('allTransactions');
    return saved ? JSON.parse(saved) : {};
  });

  // State for hovered wallet (for highlighting)
  const [hoveredWallet, setHoveredWallet] = useState(null);

  const [currentTime, setCurrentTime] = useState(Math.floor(Date.now() / 1000));

  // Update current time every second.
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(Math.floor(Date.now() / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Persist wallets and allTransactions to localStorage.
  useEffect(() => {
    localStorage.setItem('trackedWallets', JSON.stringify(wallets));
  }, [wallets]);

  useEffect(() => {
    localStorage.setItem('allTransactions', JSON.stringify(allTransactions));
  }, [allTransactions]);

  // Poll wallet-tracker endpoint every 20 seconds.
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetch('http://localhost:5000/api/wallet-tracker')
        .then(res => res.json())
        .then(data => {
          setTrackerData(data);
          setAllTransactions(prev => {
            // Only keep transactions for currently tracked wallets.
            const updated = {};
            wallets.forEach(wallet => {
              if (prev[wallet]) {
                updated[wallet] = prev[wallet];
              }
            });
            if (data.new_transfers) {
              Object.entries(data.new_transfers).forEach(([wallet, newTxs]) => {
                if (wallets.includes(wallet)) {
                  if (!updated[wallet]) {
                    updated[wallet] = newTxs;
                  } else {
                    const existingIds = new Set(updated[wallet].map(tx => tx.transaction_id));
                    newTxs.forEach(tx => {
                      if (!existingIds.has(tx.transaction_id)) {
                        updated[wallet].push(tx);
                      }
                    });
                  }
                  // Sort transactions by block_time descending
                  updated[wallet].sort((a, b) => b.block_time - a.block_time);
                }
              });
            }
            return updated;
          });
        })
        .catch(err => console.error('Error fetching wallet tracker data:', err));
    }, 20000);
    return () => clearInterval(intervalId);
  }, [wallets]);

  // Poll wallet overview endpoint every 5 minutes.
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetch('http://localhost:5000/api/wallet-overview')
        .then(res => res.json())
        .then(data => {
          setOverviewMetrics(data);
        })
        .catch(err => console.error('Error fetching wallet overview data:', err));
    }, 300000);
    fetch('http://localhost:5000/api/wallet-overview')
      .then(res => res.json())
      .then(data => setOverviewMetrics(data))
      .catch(err => console.error('Error fetching wallet overview data:', err));
    return () => clearInterval(intervalId);
  }, []);

  // Poll coin data endpoint every 5 minutes.
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetch('http://localhost:5000/api/coin-data')
        .then(res => res.json())
        .then(data => setCoinData(data))
        .catch(err => console.error('Error fetching coin data:', err));
    }, 30000);
    fetch('http://localhost:5000/api/coin-data')
      .then(res => res.json())
      .then(data => setCoinData(data))
      .catch(err => console.error('Error fetching coin data:', err));
    return () => clearInterval(intervalId);
  }, []);

  // Function to update the backend with the current wallet list.
  const updateWalletsOnBackend = (updatedWallets) => {
    fetch('http://localhost:5000/api/update-wallets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wallets: updatedWallets })
    })
      .then(response => response.json())
      .then(data => console.log('Backend wallet tracker updated:', data))
      .catch(err => console.error('Error updating wallets:', err));
  };

  // Handler to add a wallet and update backend immediately.
  const handleAddWallet = () => {
    if (walletInput && wallets.length < 10) {
      const newWallet = walletInput.trim();
      const updatedWallets = [...wallets, newWallet];
      setWallets(updatedWallets);
      setWalletInput('');
      updateWalletsOnBackend(updatedWallets);
    }
  };

  // Handler to remove a wallet and update backend.
  const handleRemoveWallet = (walletToRemove) => {
    const updatedWallets = wallets.filter(wallet => wallet !== walletToRemove);
    setWallets(updatedWallets);
    setAllTransactions(prev => {
      const updated = { ...prev };
      delete updated[walletToRemove];
      return updated;
    });
    updateWalletsOnBackend(updatedWallets);
  };

  const handleCopy = (coinAddress, rowIndex, e) => {
    // Prevent row click from firing when clicking the icon
    e.stopPropagation();
    navigator.clipboard.writeText(coinAddress)
      .then(() => {
        setMessage('Wallet Address Copied!');
        setShowMessage(true);
        setCopiedIcon((prev) => ({ ...prev, [rowIndex]: true }));
        setTimeout(() => {
          setShowMessage(false);
          setCopiedIcon((prev) => ({ ...prev, [rowIndex]: false }));
        }, 2000);
      })
      .catch((err) => console.error('Failed to copy:', err));
  };

  // Prepare a flat array of all transactions with a wallet property.
  const flatTransactions = [];
  Object.entries(allTransactions).forEach(([wallet, txs]) => {
    txs.forEach(tx => {
      flatTransactions.push({ ...tx, wallet });
    });
  });
  // Sort flat transactions by block_time descending (newest first)
  flatTransactions.sort((a, b) => b.block_time - a.block_time);

  return (
      <div className="dashboard-container">
        {/* Left Panel: Wallet Management Table */}
        <div className="left-panel">
          <h2>Wallet Manager</h2>
          <div className="wallet-input">
            <input
                type="text"
                placeholder="Enter wallet address"
                value={walletInput}
                onChange={(e) => setWalletInput(e.target.value)}
            />
            <button onClick={handleAddWallet}>Add</button>
          </div>
          <table className="wallet-table">
            <thead>
            <tr>
              <th>Address</th>
              <th>7D PnL</th>
              <th>7D Volume</th>
              <th>Remove</th>
            </tr>
            </thead>
            <tbody>
            {wallets.map((wallet, idx) => (
                <tr
                    key={idx}
                    className={hoveredWallet === wallet ? "highlight" : ""}
                >
                  <td>{truncateAddress(wallet)}
                    <span
                        className="clipboard-icon"
                        onClick={(e) => handleCopy(wallet, idx, e)}
                        title="Copy wallet address"
                    >
                  {copiedIcon[idx] ? <IoMdCheckmark size={12}/> : <FiCopy size={12}/>}

                </span>

                  </td>
                  <td
                      className={
                        overviewMetrics[wallet] &&
                        overviewMetrics[wallet]["7d PnL"] &&
                        overviewMetrics[wallet]["7d PnL"].trim().startsWith("-")
                            ? "red-text"
                            : "green-text"
                      }
                  >
                    {overviewMetrics[wallet] && overviewMetrics[wallet]["7d PnL"]
                        ? overviewMetrics[wallet]["7d PnL"]
                        : 'N/A'}
                  </td>
                  <td>
                    {overviewMetrics[wallet] &&
                    overviewMetrics[wallet]["7d Volume"]
                        ? overviewMetrics[wallet]["7d Volume"]
                        : 'N/A'}
                  </td>
                  <td>
                    <button onClick={() => handleRemoveWallet(wallet)}>Remove</button>
                  </td>
                </tr>
            ))}
            </tbody>

          </table>
        </div>

        {/* Right Panel: Tracker Data Display */}
        <div className="right-panel">
          <div className="top-box">
            <h2>Recent Buys</h2>
            {flatTransactions.length === 0 ? (
                <p>No recent transactions</p>
            ) : (
                <table className="transactions-table">
                  <thead>
                  <tr>
                    <th>Coin</th>
                    <th>Name</th>
                    <th>Market Cap</th>
                    <th>Amount Bought</th>
                    <th>Age</th>
                  </tr>
                  </thead>
                  <tbody>
                  {flatTransactions.map((tx, idx) => {
                    // Use coinData to display coin info if available.
                    const coinInfo = coinData[tx.token_address];
                    return (
                        <tr
                            key={idx}
                            onMouseEnter={() => setHoveredWallet(tx.wallet)}
                            onMouseLeave={() => setHoveredWallet(null)}
                        >
                          <td>
                              {coinInfo && coinInfo.image ? (
                                  <img src={coinInfo.image} alt={coinInfo.name} className="coin-image"/>
                              ) : (
                                  <span>No Image</span>
                              )}</td>
                          <td>{coinInfo ? coinInfo.name : truncateAddress(tx.token_address)}</td>
                          <td>{coinInfo ? coinInfo.market_cap : 'N/A'}</td>
                          <td>{'$'}{tx.amount}</td>
                          <td>{formatElapsedTime(tx.block_time, currentTime)}</td>
                        </tr>
                    );
                  })}
                  </tbody>
                </table>
            )}
          </div>
          <div className="bottom-box">
            <h2>Popular Coins</h2>
            {trackerData && trackerData.hot_buys && Object.keys(trackerData.hot_buys).length > 0 ? (
                <ul className="popular-coins-list">
                  {Object.entries(trackerData.hot_buys).map(([token, count]) => (
                      <li key={token}>
                        <strong>Token:</strong> {token} | <strong>Wallets:</strong> {count}
                      </li>
                  ))}
                </ul>
            ) : (
                <p>No popular coins</p>
            )}
          </div>
        </div>
        <div className={`copy-message ${showMessage ? 'show' : ''}`}>
          {message}
        </div>
      </div>
  );
};

export default WalletTracker;
