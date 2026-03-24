import { useLocation, useNavigate } from 'react-router-dom';

export default function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { path: '/home', label: 'Home' },
    { path: '/match', label: 'Match' },
    { path: '/friends', label: 'Friends' },
    { path: '/posts', label: 'Posts' },
    { path: '/feed', label: 'Feed' },
  ];

  function isActive(path) {
    if (path === '/home') return location.pathname === '/home';
    return location.pathname.startsWith(path);
  }

  return (
    <nav className="top-navbar">
      <div className="navbar-brand" onClick={() => navigate('/home')}>
        <div className="navbar-logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
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
