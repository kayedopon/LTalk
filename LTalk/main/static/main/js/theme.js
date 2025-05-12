// Theme management functionality
document.addEventListener('DOMContentLoaded', function() {
  // Create dark mode toggle button
  const darkModeToggle = document.createElement('button');
  darkModeToggle.classList.add('dark-mode-toggle');
  darkModeToggle.setAttribute('aria-label', 'Toggle dark mode');
  darkModeToggle.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>
    </svg>
  `;
  document.body.appendChild(darkModeToggle);

  // Check for saved theme preference only
  const savedTheme = localStorage.getItem('theme');
  
  // Default to light theme unless explicitly set to dark
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark');
    darkModeToggle.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="4"></circle>
        <path d="M12 2v2"></path>
        <path d="M12 20v2"></path>
        <path d="m4.93 4.93 1.41 1.41"></path>
        <path d="m17.66 17.66 1.41 1.41"></path>
        <path d="M2 12h2"></path>
        <path d="M20 12h2"></path>
        <path d="m6.34 17.66-1.41 1.41"></path>
        <path d="m19.07 4.93-1.41 1.41"></path>
      </svg>
    `;
  } else {
    // Ensure light theme is set explicitly
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }

  // Toggle dark mode on button click
  darkModeToggle.addEventListener('click', function() {
    document.documentElement.classList.toggle('dark');
    
    if (document.documentElement.classList.contains('dark')) {
      localStorage.setItem('theme', 'dark');
      darkModeToggle.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4"></circle>
          <path d="M12 2v2"></path>
          <path d="M12 20v2"></path>
          <path d="m4.93 4.93 1.41 1.41"></path>
          <path d="m17.66 17.66 1.41 1.41"></path>
          <path d="M2 12h2"></path>
          <path d="M20 12h2"></path>
          <path d="m6.34 17.66-1.41 1.41"></path>
          <path d="m19.07 4.93-1.41 1.41"></path>
        </svg>
      `;
    } else {
      localStorage.setItem('theme', 'light');
      darkModeToggle.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>
        </svg>
      `;
    }
  });
  
  // Add smooth transition class after initial load
  setTimeout(() => {
    document.body.classList.add('theme-transition-ready');
  }, 300);
}); 