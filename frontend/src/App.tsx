import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import DashboardAdvanced from './components/DashboardAdvanced';
import Customers from './components/Customers';
import CustomersAdvanced from './components/CustomersAdvanced';
import Deals from './components/Deals';
import PipelineBoard from './components/PipelineBoard';
import Activities from './components/Activities';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <h2>CRM System</h2>
          </div>
          <ul className="nav-links">
            <li><Link to="/">Dashboard</Link></li>
            <li><Link to="/customers">Clientes</Link></li>
            <li><Link to="/pipeline">Pipeline</Link></li>
            <li><Link to="/activities">Atividades</Link></li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<DashboardAdvanced />} />
            <Route path="/customers" element={<CustomersAdvanced />} />
            <Route path="/pipeline" element={<PipelineBoard />} />
            <Route path="/deals" element={<Deals />} />
            <Route path="/activities" element={<Activities />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
