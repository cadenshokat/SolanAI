// src/pages/CoinsTables.js
import React, { useEffect, useState } from 'react';
import './NewCoins.css'; // We'll add some CSS for table styling
import { FiCopy } from "react-icons/fi";
import { IoMdCheckmark } from "react-icons/io";

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

const CoinsTables = () => {
  const [newCoins, setNewCoins] = useState([]);
  const [almostCoins, setAlmostCoins] = useState([]);
  const [copiedIcon, setCopiedIcon] = useState({}); // Track copied state per row for newCoins
  const [showMessage, setShowMessage] = useState(false);
  const [message, setMessage] = useState('');

  const [currentTime, setCurrentTime] = useState(Math.floor(Date.now() / 1000));

  const ProgressBar = ({ progress }) => {
  return (
    <div className="progress-bar">
      <div className="progress" style={{ width: `${progress}%` }}></div>
    </div>
  );
};

  // Update current time every second.
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(Math.floor(Date.now() / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch new coins data
  useEffect(() => {
    fetch('http://localhost:5000/api/new-coins')
      .then((response) => response.json())
      .then((data) => {
        setNewCoins(data.coins);
      })
      .catch((error) => console.error('Error fetching new coins:', error));
  }, []);

  // Fetch almost graduated coins data
  useEffect(() => {
    fetch('http://localhost:5000/api/almost-graduated-coins')
      .then((response) => response.json())
      .then((data) => {
        setAlmostCoins(data.coins);
      })
      .catch((error) => console.error('Error fetching almost graduated coins:', error));
  }, []);

  // Helper to copy coin address
  const handleCopy = (coinAddress, rowIndex, e) => {
    // Prevent row click from firing when clicking the icon
    e.stopPropagation();
    navigator.clipboard.writeText(coinAddress)
      .then(() => {
        setMessage('Coin Address Copied!');
        setShowMessage(true);
        setCopiedIcon((prev) => ({ ...prev, [rowIndex]: true }));
        setTimeout(() => {
          setShowMessage(false);
          setCopiedIcon((prev) => ({ ...prev, [rowIndex]: false }));
        }, 2000);
      })
      .catch((err) => console.error('Failed to copy:', err));
  };

  // Open DexScreener in a new tab when row is clicked
  const handleRowClick = (coin) => {
    window.open(`https://dexscreener.com/solana/${coin.address}`, "_blank");
  };

  // Render a table for a list of coins with a title
  // src/pages/CoinsTables.js (excerpt)
  const renderTable = (coinsList, title, isAlmostGraduated = false) => (
      <div className="table-section">
        <h2>{title}</h2>
        <table className="coins-table">
          <thead>
            <tr>
              <th>Coin</th>
              <th>Name</th>
              <th>Ticker</th>
              <th>Market Cap</th>
              <th>Volume</th>
              <th>Holders</th>
              <th>Age</th>
              {isAlmostGraduated && <th>Bonding Curve</th>}
              <th>Red Flag</th>
            </tr>
          </thead>
          <tbody>
            {coinsList.map((coin, index) => (
                <tr key={index} onClick={() => handleRowClick(coin)}>
                    <td>
                        {coin.image ? (
                            <img
                                src={coin.image}
                                alt={`${coin.name} logo`}
                                className="coin-logo"
                            />
                        ) : (
                            'No Image'
                        )}
                    </td>
                    <td>
                        {coin.name}
                        {' '}

                        {/* Clipboard or Checkmark Icon */}
                        <span
                            className="clipboard-icon"
                            onClick={(e) => handleCopy(coin.address, index, e)}
                            title="Copy coin address"
                        >
                  {copiedIcon[index] ? <IoMdCheckmark size={12}/> : <FiCopy size={12}/>}

                </span>
                    </td>
                    <td>{coin.ticker}</td>
                    <td>{coin.market_cap}</td>
                    <td>{coin.volume}</td>
                    <td>{coin.holders}</td>
                    <td>{<td>{formatElapsedTime(coin.age, currentTime)}</td>}</td>
                    {isAlmostGraduated &&
                      <td>
                        {coin.bonding_curve !== undefined ? (
                            <div title={`${coin.bonding_curve}%`}>
                                <ProgressBar progress={coin.bonding_curve} />
                            </div>
                        ) : ('N/A')}
                      </td>
                    }
                    <td>{coin.red_flag ? <span className="red-flag">Yes</span> : 'No'}</td>
                </tr>
            ))}
          </tbody>
        </table>
      </div>
  );


    return (
        <div className="coins-tables-container">
            {renderTable(almostCoins, "Almost Graduated Coins", true)}
            {renderTable(newCoins, "New Coins")}
            <div className={`copy-message ${showMessage ? 'show' : ''}`}>
                {message}
            </div>
        </div>
    );
};

export default CoinsTables;
