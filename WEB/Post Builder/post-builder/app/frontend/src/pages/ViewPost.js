import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import LayoutRenderer from '../components/LayoutRenderer';

function ViewPost({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [deleting, setDeleting] = useState(false);

  const fetchPost = useCallback(async () => {
    try {
      const response = await axios.get(`/api/posts/${id}`);
      setPost(response.data);
    } catch (error) {
      console.error('Error fetching post:', error);
      setMessage('Post not found');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchPost();
  }, [fetchPost]);

  const handleReport = async () => {
    setMessage('');
    try {
      const response = await axios.post('/api/report', { postId: id });
      setMessage(response.data.message);
    } catch (err) {
      setMessage('Error: ' + (err.response?.data?.error || 'Failed to report post'));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this post?')) {
      return;
    }

    setDeleting(true);
    try {
      await axios.delete(`/api/posts/${id}`);
      navigate('/');
    } catch (err) {
      setMessage('Error: ' + (err.response?.data?.error || 'Failed to delete post'));
      setDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading post...</p>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="container">
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">❌</div>
            <h2 className="empty-state-title">Post Not Found</h2>
            <p className="empty-state-text">{message}</p>
            <button onClick={() => navigate('/')} className="btn btn-primary">
              Go Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <div style={{ marginBottom: '2rem' }}>
          <h1 className="card-title">{post.title}</h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'var(--gray)', fontSize: '0.95rem' }}>
            <span>👤 {post.author}</span>
            <span>•</span>
            <span>📅 {formatDate(post.created_at)}</span>
          </div>
        </div>

        <div className="post-content">
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem', fontWeight: 600, color: 'var(--dark)' }}>
            Post Content:
          </h3>
          <LayoutRenderer layout={post.layout} />
        </div>

        <div className="post-actions">
          <button onClick={handleReport} className="btn btn-danger">
            🚩 Report to Admin
          </button>
          {post.author === user.username && (
            <button
              onClick={handleDelete}
              className="btn btn-secondary"
              disabled={deleting}
            >
              {deleting ? 'Deleting...' : '🗑️ Delete Post'}
            </button>
          )}
        </div>

        {message && (
          <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`} style={{ marginTop: '1.5rem' }}>
            {message}
          </div>
        )}

        <details style={{ marginTop: '2rem' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 600, color: 'var(--gray)', padding: '0.5rem' }}>
            📋 View Layout JSON
          </summary>
          <pre className="code-block" style={{ marginTop: '1rem' }}>
            {JSON.stringify(post.layout, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}

export default ViewPost;
