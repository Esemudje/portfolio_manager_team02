import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard.jsx';
import Portfolio from './components/Portfolio.jsx';
import Trading from './components/Trading.jsx';
import EnhancedTrading from './components/EnhancedTrading.jsx';
import StockDetail from './components/StockDetail.jsx';
import './App.css';
import ManageCash from './components/ManageCash.jsx';

function Navigation() {
  const location = useLocation();
  
  return (
    <header className="header">
      <div className="container">
        <h1>Wealthie</h1>
        <nav className="nav">
          <ul className="nav-list">
            <li>
              <Link 
                to="/" 
                className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
              >
                Dashboard
              </Link>
            </li>
            <li>
              <Link 
                to="/portfolio" 
                className={`nav-link ${location.pathname === '/portfolio' ? 'active' : ''}`}
              >
                Portfolio
              </Link>
            </li>
            <li>
              <Link 
                to="/trading" 
                className={`nav-link ${location.pathname === '/trading' ? 'active' : ''}`}
              >
                Trading
              </Link>
            </li>
            <li>
              <Link 
                to="/enhanced-trading" 
                className={`nav-link ${location.pathname === '/enhanced-trading' ? 'active' : ''}`}
              >
                Enhanced Trading
              </Link>
            </li>

            <li>
              <Link 
                to="/cash" 
                className={`nav-link ${location.pathname === '/cash' ? 'active' : ''}`}
              >
                Cash Management
              </Link>
            </li>            
          </ul>
        </nav>
      </div>
    </header>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        
        <main className="container" style={{ paddingTop: '2rem' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/trading" element={<Trading />} />
            <Route path="/enhanced-trading" element={<EnhancedTrading />} />
            <Route path="/stock/:symbol" element={<StockDetail />} />
            <Route path="/cash" element={<ManageCash/>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
