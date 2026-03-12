import { useLocation, useNavigate } from 'react-router-dom';

export default function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { path: '/', label: 'Home' },
    { path: '/match', label: 'Match' },
    { path: '/friends', label: 'Friends' },
    { path: '/posts', label: 'Posts' },
    { path: '/feed', label: 'Feed' },
  ];

  function isActive(path) {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  }

  return (
    <nav className="top-navbar">
      <div className="navbar-brand" onClick={() => navigate('/')}>
        <div className="navbar-logo">
          <span>♪</span>
        </div>
        <span className="navbar-title">MusicMate</span>
      </div>
      <div className="navbar-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.path}
            className={`nav-tab ${isActive(tab.path) ? 'active' : ''}`}
            onClick={() => navigate(tab.path)}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </nav>
  );
}
