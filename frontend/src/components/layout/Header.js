"use client";

import Link from 'next/link';
import { useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { useRouter } from 'next/navigation';

export default function Header() {
  const { user, logout } = useContext(AuthContext);
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <header className="glass-header">
      <div className="header-content">
        <Link href="/" className="logo">
          GovFlow AI
        </Link>
        <nav className="nav-links">
          <Link href="/services">Services</Link>
          <Link href="/">AI Assistant</Link>
          <Link href="/about">About</Link>
          
          {user ? (
            <>
              <Link href="/history">My History</Link>
              <button 
                onClick={handleLogout}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontFamily: 'inherit',
                  padding: 0
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <Link href="/login" className="login-btn" style={{
              background: 'var(--primary)',
              padding: '0.4rem 1rem',
              borderRadius: '99px',
              color: 'white'
            }}>
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
