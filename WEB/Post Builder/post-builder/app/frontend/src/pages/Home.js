import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

function Home() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get('/api/posts');
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading posts...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Welcome to Post Builder!</h1>
          <p className="card-subtitle">
            Create posts with custom layouts using JSON. Share them with the admin for review.
          </p>
        </div>
        <Link to="/create" className="btn btn-primary">
          ✨ Create Your First Post
        </Link>
      </div>

      {posts.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <h2 className="empty-state-title">No posts yet</h2>
            <p className="empty-state-text">
              Create your first post to get started!
            </p>
            <Link to="/create" className="btn btn-primary">
              Create Post
            </Link>
          </div>
        </div>
      ) : (
        <>
          <h2 style={{ color: 'white', marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: 700 }}>
            Your Posts
          </h2>
          <div className="posts-grid">
            {posts.map(post => (
              <Link key={post.id} to={`/post/${post.id}`} className="post-card">
                <div className="post-card-header">
                  <div>
                    <h3 className="post-title">{post.title}</h3>
                  </div>
                </div>
                <div className="post-date">
                  {formatDate(post.created_at)}
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default Home;
