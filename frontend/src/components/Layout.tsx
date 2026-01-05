import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/', label: '任务列表' },
    { path: '/submit-task', label: '提交任务' },
    { path: '/datasets', label: '数据集' },
    { path: '/models', label: '模型' },
    { path: '/chat', label: '对话' },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="logo">模型微调平台</h1>
          </div>
          <nav className="nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="header-right">
            <span className="user-info">欢迎，{user?.username}</span>
            <button onClick={logout} className="btn-secondary btn-sm">
              退出
            </button>
          </div>
        </div>
      </header>
      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  );
};

