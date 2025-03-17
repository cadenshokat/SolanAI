// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import NewCoins from './pages/NewCoins';
import Header from './components/Header';
import WalletTracker from './pages/WalletTracker'

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/WalletTracker" element={<WalletTracker />} />
        <Route path="/underground" element={<NewCoins />} />
        {/* Other routes */}
      </Routes>
    </Router>
  );
}

export default App;
