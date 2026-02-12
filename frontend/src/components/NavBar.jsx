import { useLocation, useNavigate } from 'react-router-dom';

export default function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { path: '/dashboard', label: 'Profile', icon: '♪' },
    { path: '/discover', label: 'Discover', icon: '♡' },
    { path: '/matches', label: 'Matches', icon: '★' },
  ];

  return (
    <nav className="navbar">
      {tabs.map((tab) => (
        <button
          key={tab.path}
          className={`nav-tab ${location.pathname === tab.path ? 'active' : ''}`}
          onClick={() => navigate(tab.path)}
        >
          <span className="nav-icon">{tab.icon}</span>
          <span className="nav-label">{tab.label}</span>
        </button>
      ))}
    </nav>
  );
}
