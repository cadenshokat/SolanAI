// src/components/Header.js
import React from 'react';
import './Header.css';
import { Link } from 'react-router-dom';
import logo from '../assets/cashcow_logo4.png'; // Adjust path as needed

const Header = () => {
  return (
      <header className="header">
      <div className="logo">
        <Link to ="/"><img src={logo} alt="Cash Cow logo" /></Link>
      </div>
      <nav className="nav">
        <Link to="/walletTracker">Wallet Tracker</Link>
        <Link to="/underground">New Coins</Link>
        <Link to="/strong">Prime Picks</Link>
        <Link to="/socials">Hot on Socials</Link>
      </nav>

      <div className="map-key-container">
          <div className="map-key-button">
              Map/Key
            <div className="dropdown">
                <ul>
                    <li>Symbol A: Meaning A</li>
                    <li>Symbol B: Meaning B</li>
                    <li>Symbol C: Meaning C</li>
                </ul>
            </div>
          </div>
      </div>
    </header>
    );
};

export default Header;  // Make sure this is here
