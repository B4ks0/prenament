// PRENAMENT JavaScript - Single Page Interactions
// Mobile-first interactions for 390px Android viewport

class PrenamentApp {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.registerServiceWorker();
    this.initPWA();
  }

  setupEventListeners() {
    // Bottom navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        e.currentTarget.classList.add('active');
      });
    });

    // Form submissions
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', (e) => {
        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.innerHTML = '<span class="loading"></span> Sedang Memproses...';
        }
      });
    });

    // Checkbox toggle
    document.querySelectorAll('.checkbox-item input[type="checkbox"]').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const form = e.target.closest('form');
        if (form) form.submit();
      });
    });
  }

  registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/static/js/sw.js').catch(err => {
        console.log('SW registration failed:', err);
      });
    }
  }

  initPWA() {
    if ('standalone' in navigator && navigator.standalone === false) {
      // Show install prompt
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        // Store event for later use
        window.deferredPrompt = e;
      });
    }
  }

  // Chart helpers
  static createChart(element, data) {
    if (!element) return;
    const ctx = element.getContext('2d');
    if (!ctx) return;
    
    // Simple bar chart implementation
    const height = element.height;
    const width = element.width;
    const maxValue = Math.max(...data);
    const barWidth = width / data.length;
    
    data.forEach((value, index) => {
      const barHeight = (value / maxValue) * height;
      ctx.fillStyle = '#3b82f6';
      ctx.fillRect(
        index * barWidth,
        height - barHeight,
        barWidth - 2,
        barHeight
      );
    });
  }

  // Audio player
  static initAudioPlayer() {
    document.querySelectorAll('.audio-item').forEach(item => {
      const playBtn = item.querySelector('.play-btn');
      const audio = item.querySelector('audio');
      
      if (playBtn && audio) {
        playBtn.addEventListener('click', () => {
          if (audio.paused) {
            audio.play();
            playBtn.textContent = '⏸';
          } else {
            audio.pause();
            playBtn.textContent = '▶';
          }
        });
      }
    });
  }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  new PrenamentApp();
});
