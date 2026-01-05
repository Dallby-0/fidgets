import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/auth';
import { useAuth } from '../hooks/useAuth';
import './AuthForm.css';

export const LoginForm = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const tokenData = await authService.login({
        username_or_email: usernameOrEmail,
        password,
        remember_me: rememberMe,
      });
      login(tokenData.access_token, tokenData.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card fade-in">
        <div className="auth-header">
          <h2>欢迎回来</h2>
          <p className="text-muted">登录您的账户以继续</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="usernameOrEmail">用户名或邮箱</label>
            <input
              id="usernameOrEmail"
              type="text"
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              required
              placeholder="请输入用户名或邮箱"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="请输入密码"
              disabled={loading}
            />
          </div>
          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading}
              />
              <span>记住我</span>
            </label>
          </div>
          {error && (
            <div className="error-message slide-in">
              {error}
            </div>
          )}
          <button type="submit" disabled={loading} className="btn-primary btn-full">
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                登录中...
              </>
            ) : (
              '登录'
            )}
          </button>
        </form>
        <div className="auth-footer">
          <p className="text-muted">
            还没有账户？{' '}
            <Link to="/register" className="auth-link">
              立即注册
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
