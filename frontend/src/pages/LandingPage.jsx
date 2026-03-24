import { Link } from 'react-router-dom';
import './LandingPage.css';

export default function LandingPage() {
  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="landing-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
          <span className="landing-title">MusicMate</span>
        </div>
        <div className="landing-nav-links">
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
        </div>
        <Link to="/login" className="landing-btn-primary">
          Enter Application
        </Link>
      </nav>

      <section className="hero-section" id="how-it-works">
        <h1>Get started in minutes</h1>
        <p className="hero-subtitle">Three simple steps to start your music journey.</p>
        
        <div className="steps-container">
          <div className="step-card">
            <div className="step-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            </div>
            <div className="step-number">1</div>
            <h3>Join</h3>
            <p>Sign up with your university email to join MusicMate.</p>
          </div>
          
          <div className="step-card">
            <div className="step-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            </div>
            <div className="step-number">2</div>
            <h3>Discover & Listen</h3>
            <p>Connect with Spotify, follow friends, and track your music.</p>
          </div>
          
          <div className="step-card">
            <div className="step-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            <div className="step-number">3</div>
            <h3>Match & Socialize</h3>
            <p>Find friends with similar music taste and climb the leaderboard.</p>
          </div>
        </div>
      </section>

      <section className="feature-section left-content" id="features">
        <div className="feature-text">
          <div className="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
          </div>
          <h2>Find your Music Mate</h2>
          <p>Discover students at UoM who share your exact music vibe. Compare top artists, track listen times, and connect over shared sounds.</p>
        </div>
        <div className="feature-mockup mockup-right">
          <div className="mockup-placeholder">
            <div className="mockup-header">Match Preview</div>
            <div className="mockup-body mockup-no-pad">
              <div className="swipe-card-new mockup-scale-match">
                <div className="swipe-card-photo-placeholder" style={{ background: 'var(--primary)', color: 'white' }}>
                  A
                </div>
                <div className="swipe-card-body">
                  <div className="swipe-card-name-age">Alex Johnson, 20</div>
                  <div className="swipe-card-course">Computer Science • Year 2</div>
                  <div className="swipe-card-bio">"Always looking for new indie artists to listen to!"</div>
                  <div className="swipe-card-tags">
                    <span className="swipe-card-tag">Indie Rock</span>
                    <span className="swipe-card-tag">Alternative</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="feature-section right-content">
        <div className="feature-mockup mockup-left">
          <div className="mockup-placeholder">
            <div className="mockup-header">Leaderboard</div>
            <div className="mockup-body p-1">
              <div className="top50-list mockup-scale-list">
                <div className="top50-item">
                  <div className="top50-rank gold">1</div>
                  <div className="top50-img" style={{background: 'var(--primary-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', borderRadius: 4}}>♪</div>
                  <div className="top50-info">
                    <div className="top50-song">Not Like Us</div>
                    <div className="top50-artist">Kendrick Lamar</div>
                  </div>
                </div>
                <div className="top50-item">
                  <div className="top50-rank silver">2</div>
                  <div className="top50-img" style={{background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', borderRadius: 4}}>♪</div>
                  <div className="top50-info">
                    <div className="top50-song">Espresso</div>
                    <div className="top50-artist">Sabrina Carpenter</div>
                  </div>
                </div>
                <div className="top50-item">
                  <div className="top50-rank bronze">3</div>
                  <div className="top50-img" style={{background: '#8b5cf6', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', borderRadius: 4}}>♪</div>
                  <div className="top50-info">
                    <div className="top50-song">A Bar Song (Tipsy)</div>
                    <div className="top50-artist">Shaboozey</div>
                  </div>
                </div>
                <div className="top50-item">
                  <div className="top50-rank">4</div>
                  <div className="top50-img" style={{background: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', borderRadius: 4}}>♪</div>
                  <div className="top50-info">
                    <div className="top50-song">Good Luck, Babe!</div>
                    <div className="top50-artist">Chappell Roan</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="feature-text">
          <div className="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>
          </div>
          <h2>Climb the Ranks</h2>
          <p>Compete on listening leaderboards with friends. Prove you are the biggest fan of your favorite artist on campus.</p>
        </div>
      </section>

      <section className="feature-section left-content">
        <div className="feature-text">
          <div className="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
          </div>
          <h2>Join the Conversation</h2>
          <p>Share what you're listening to and discover new music from your friends' live feeds. Drop thoughts, build playlists together, and vibe.</p>
        </div>
        <div className="feature-mockup mockup-right">
          <div className="mockup-placeholder">
            <div className="mockup-header">Feed</div>
            <div className="mockup-body p-1 feed-body">
              <div className="post-card mockup-scale-post">
                <div className="post-card-header">
                  <div className="post-avatar" style={{background: '#ef4444', color: 'white'}}>E</div>
                  <div className="post-user-info">
                    <h4>Emma W.</h4>
                    <div className="post-time">2h ago</div>
                  </div>
                </div>
                
                <div className="post-text-content" style={{fontSize: '0.85rem', marginBottom: '0.75rem', color: 'var(--text)'}}>
                  Can't stop listening to this new album! Anyone else? 🔥
                </div>

                <div className="post-song-card pt-0">
                  <div className="post-song-icon">♪</div>
                  <div className="post-song-info">
                    <div className="post-song-name">Midnight Dreams</div>
                    <div className="post-song-artist">The Midnight</div>
                  </div>
                </div>
                
                <div className="post-actions" style={{marginTop: '0.5rem'}}>
                  <button className="post-action-btn liked"><span>♥</span><span>12</span></button>
                </div>
              </div>
              
              <div className="post-card mockup-scale-post">
                <div className="post-card-header">
                  <div className="post-avatar" style={{background: '#3b82f6', color: 'white'}}>J</div>
                  <div className="post-user-info">
                    <h4>James T.</h4>
                    <div className="post-time">5h ago</div>
                  </div>
                </div>
                
                <div className="post-text-content" style={{fontSize: '0.85rem', marginBottom: '0.75rem', color: 'var(--text)'}}>
                  Vibing to some classics today 🎸
                </div>

                <div className="post-song-card pt-0">
                  <div className="post-song-icon">♪</div>
                  <div className="post-song-info">
                    <div className="post-song-name">Hotel California</div>
                    <div className="post-song-artist">Eagles</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <h2>Ready to start your music journey?</h2>
        <p>Join MusicMate for free and build a community of friends who are learning, discovering, and listening together.</p>
        <div className="cta-buttons">
          <Link to="/login" className="landing-btn-primary cta-btn">
            Enter Application
          </Link>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="landing-logo">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              <span className="landing-title">MusicMate</span>
            </div>
            <p className="footer-subtitle">Making music sharing accessible, social, and fun for everyone.</p>
            <p className="footer-contact">support@musicmate.com</p>
          </div>
          <div className="footer-links">
            <div className="footer-column">
              <h4>PRODUCT</h4>
              <a href="#features">Features</a>
              <a href="#how-it-works">How It Works</a>
              <Link to="/login">Enter Application</Link>
            </div>
            <div className="footer-column">
              <h4>COMPANY</h4>
              <a href="#">About</a>
              <a href="#">Careers</a>
              <a href="#">Contact</a>
            </div>
            <div className="footer-column">
              <h4>LEGAL</h4>
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
