import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function CreatePost() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [layoutJson, setLayoutJson] = useState(JSON.stringify([
    {
      wrapper: 'div',
      children: ['Hello World!']
    }
  ], null, 2));
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const layout = JSON.parse(layoutJson);
      const response = await axios.post('/api/posts', { title, layout });
      navigate(`/post/${response.data.id}`);
    } catch (err) {
      if (err.name === 'SyntaxError') {
        setError('Invalid JSON format');
      } else {
        setError(err.response?.data?.error || 'Failed to create post');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Create New Post</h1>
          <p className="card-subtitle">
            Design your post layout using JSON
          </p>
        </div>

        {error && (
          <div className="alert alert-error">{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title" className="form-label">
              Title
            </label>
            <input
              id="title"
              type="text"
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter post title"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="layout" className="form-label">
              Layout (JSON)
            </label>
            <textarea
              id="layout"
              className="form-textarea"
              value={layoutJson}
              onChange={(e) => setLayoutJson(e.target.value)}
              placeholder="Enter layout JSON"
              rows={15}
              required
            />
            <div className="form-hint">
              Define your post layout using JSON. Each element can have a wrapper type and children.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ flex: 1 }}
            >
              {loading ? 'Creating...' : '✨ Create Post'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreatePost;
