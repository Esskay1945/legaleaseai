(function () {
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  // Enhanced notification system
  window.showNotification = function (message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    // Safely wrap the message
    const safeMessage = typeof message === 'string' ? window.utils.escapeHTML(message) : message;

    notification.innerHTML = `
      <div class="notification-content">
        <span>${safeMessage}</span>
        <button onclick="this.parentElement.parentElement.remove()" style="background:none;border:none;color:inherit;cursor:pointer;font-size:1.2rem;padding:0 0 0 10px;">×</button>
      </div>
    `;

    // Add styles with enhanced animations
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
      padding: 12px 16px;
      border-radius: 8px;
      color: white;
      font-size: 14px;
      max-width: 350px;
      animation: slideIn 0.3s ease-out;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      ${type === 'error' ? 'background: linear-gradient(135deg, #ff4757, #ff3742);' : ''}
      ${type === 'success' ? 'background: linear-gradient(135deg, #2ed573, #1e90ff);' : ''}
      ${type === 'info' ? 'background: linear-gradient(135deg, #6a5cff, #1ea7ff);' : ''}
      ${type === 'warning' ? 'background: linear-gradient(135deg, #ffa502, #ff6348);' : ''}
    `;

    document.body.appendChild(notification);

    // Auto remove after 4 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
      }
    }, 4000);
  };

  // Add enhanced CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { 
        transform: translateX(100%); 
        opacity: 0; 
      }
      to { 
        transform: translateX(0); 
        opacity: 1; 
      }
    }
    @keyframes slideOut {
      from { 
        transform: translateX(0); 
        opacity: 1; 
      }
      to { 
        transform: translateX(100%); 
        opacity: 0; 
      }
    }
    .notification-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .notification button:hover {
      opacity: 0.8;
    }
  `;
  document.head.appendChild(style);

  // Override alert function with enhanced message parsing
  window.alert = function (message) {
    if (message.includes('✅')) {
      showNotification(message.replace('✅ ', ''), 'success');
    } else if (message.includes('❌') || message.includes('⌐')) {
      showNotification(message.replace(/[❌⌐] /, ''), 'error');
    } else if (message.includes('⚠️')) {
      showNotification(message.replace('⚠️ ', ''), 'warning');
    } else {
      showNotification(message, 'info');
    }
  };

  // Icons collection
  const Icons = {
    layout: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/></svg>`,
    file: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10,9 9,9 8,9"/></svg>`,
    search: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>`,
    chat: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
    user: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
    logout: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
    scale: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 11V7a4 4 0 0 0-8 0v4M5 9h14l1 12H4L5 9z"/><path d="M9 9V7a3 3 0 0 1 6 0v2"/></svg>`
  };
  window.Icons = Icons;

  // Enhanced layout renderer with improved navigation
  window.renderLayout = function (contentHTML, activeKey) {
    const app = document.getElementById('app');
    const nav = [
      { key: '/', href: 'index.html', name: 'Dashboard', icon: Icons.layout },
      { key: '/contracts', href: 'contracts.html', name: 'Contract Generator', icon: Icons.file },
      { key: '/research', href: 'research.html', name: 'Case Research', icon: Icons.search },
      { key: '/chat', href: 'chat.html', name: 'LegalEase AI', icon: Icons.chat }
    ];

    const user = JSON.parse(localStorage.getItem("user") || "{}");

    app.innerHTML = `
    <div class="app">
      <aside class="sidebar glass-nav" id="sidebar">
        <div class="sidebar-inner">
          <div class="brand">
            <div class="brand-id">
              <div class="brand-logo bg-gradient-primary shadow-neon-primary"><span class="icon">${Icons.scale}</span></div>
              <div class="brand-title text-gradient">LegalEase</div>
            </div>
          </div>
          <nav class="nav">
            ${nav.map(n => `<a href="${n.href}" class="${n.key === activeKey ? 'active' : ''}"><span class="icon">${n.icon}</span><span>${n.name}</span></a>`).join('')}
          </nav>
          <div class="sidebar-footer">
            <a class="btn" href="#" onclick="logout()"><span class="icon">${Icons.logout}</span><span>Sign Out</span></a>
          </div>
        </div>
      </aside>
      <div class="main">
        <header class="header glass-nav banner-header">
          <div class="header-inner">
            <div class="header-title">
              <h1 class="text-gradient">⚖️ Welcome to LegalEase Dashboard</h1>
              <p class="text-muted small">Your smart legal assistant at your fingertips</p>
            </div>
            <div class="dropdown" id="profileDropdown">
              <button class="btn" id="profileBtn"><span class="icon">${Icons.user}</span></button>
              <div class="dropdown-menu">
                <div style="padding:.5rem .7rem; font-size:.9rem; border-bottom:1px solid var(--border);">
                  <strong>${window.utils.escapeHTML(user.name || "User")}</strong><br>
                  <span class="text-muted small">${window.utils.escapeHTML(user.email || "")}</span>
                </div>
                <a href="profile.html" id="myProfile">My Profile</a>
                <a href="change-password.html" id="changePassword">Change Password</a>
                <button onclick="logout()">Sign Out</button>
              </div>
            </div>
          </div>
        </header>
        <main><div class="container" id="pageContainer">${contentHTML}</div></main>
      </div>
    </div>`;

    // Enhanced profile dropdown functionality
    const profileBtn = document.getElementById("profileBtn");
    const dropdown = document.getElementById("profileDropdown");

    profileBtn.onclick = (e) => {
      e.stopPropagation();
      dropdown.classList.toggle("open");
    };

    document.addEventListener("click", (e) => {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
      }
    });

    // Add smooth transitions to navigation
    $$('.nav a').forEach(link => {
      link.addEventListener('click', function (e) {
        // Add loading state for visual feedback
        if (!this.classList.contains('active')) {
          showNotification('Loading page...', 'info');
        }
      });
    });
  };

  // Enhanced authentication helpers
  window.attachAuth = function () {
    $$('.toggle-pass').forEach(btn => {
      btn.onclick = () => {
        const input = btn.previousElementSibling;
        const isPassword = input.type === "password";
        input.type = isPassword ? "text" : "password";
        btn.innerHTML = isPassword ? "👁️" : "🔒";
      }
    });

    // Add form validation helpers
    $$('form').forEach(form => {
      form.addEventListener('submit', function (e) {
        const requiredFields = this.querySelectorAll('input[required]');
        let isValid = true;

        requiredFields.forEach(field => {
          if (!field.value.trim()) {
            field.style.borderColor = '#ff4757';
            isValid = false;
          } else {
            field.style.borderColor = '';
          }
        });

        if (!isValid) {
          e.preventDefault();
          showNotification('Please fill in all required fields', 'error');
        }
      });
    });
  };

  // Enhanced logout with confirmation
  window.logout = function () {
    if (confirm('Are you sure you want to sign out?')) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      showNotification('Successfully signed out', 'success');
      setTimeout(() => {
        window.location.href = "login.html";
      }, 1000);
    }
  };

  // Add utility functions
  window.utils = {
    formatDate: (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },

    escapeHTML: (str) => {
      if (!str) return '';
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    },

    copyToClipboard: (text) => {
      navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
      }).catch(() => {
        showNotification('Failed to copy to clipboard', 'error');
      });
    },

    downloadFile: (content, filename, contentType = 'text/plain') => {
      const blob = new Blob([content], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      showNotification(`Downloaded ${filename}`, 'success');
    }
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      console.log('LegalEase script initialized');
    });
  } else {
    console.log('LegalEase script initialized');
  }

})();