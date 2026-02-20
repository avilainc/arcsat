import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <h1>Dashboard CRM</h1>
      <div className="dashboard-grid">
        <Link to="/customers" className="dashboard-card">
          <h2>Clientes</h2>
          <p>Gerencie seus clientes</p>
        </Link>
        <Link to="/deals" className="dashboard-card">
          <h2>Negócios</h2>
          <p>Acompanhe oportunidades</p>
        </Link>
        <Link to="/activities" className="dashboard-card">
          <h2>Atividades</h2>
          <p>Organize suas tarefas</p>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
