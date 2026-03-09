import React from 'react';
import { Link } from 'react-router-dom';

function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-brand">
          📝 Post Builder
        </Link>
        <div className="navbar-menu">
          <Link to="/" className="navbar-link">Home</Link>
          <Link to="/create" className="navbar-link">Create Post</Link>
        </div>
        <div className="navbar-user">
          <div className="user-avatar">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <span style={{ color: 'var(--dark)', fontWeight: 500 }}>
            {user.username}
          </span>
          <button onClick={onLogout} className="btn btn-sm btn-secondary">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
