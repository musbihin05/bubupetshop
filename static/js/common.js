// common.js - Shared JavaScript functionality for all pages

// Sticky Navbar Animation
const navbar = document.getElementById('navbar');
let lastScrollTop = 0;

window.addEventListener('scroll', () => {
  let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  if (scrollTop > 50) { // Add sticky class after scrolling 50px
    navbar.classList.add('navbar-sticky');
  } else {
    navbar.classList.remove('navbar-sticky');
  }
  lastScrollTop = scrollTop;
});

// Hamburger Menu Toggle for Mobile
const hamburger = document.getElementById('hamburger');
const navbarMenu = document.getElementById('navbar-menu');

if (hamburger && navbarMenu) {
  hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    navbarMenu.classList.toggle('active');
    console.log('Hamburger clicked');
  });
}

// Profile Dropdown Toggle for desktop
const profileButton = document.getElementById('profile-button');
const profileDropdown = document.getElementById('profile-dropdown');

if (profileButton && profileDropdown) {
  profileButton.addEventListener('click', (e) => {
    e.stopPropagation();
    profileDropdown.classList.toggle('hidden');
    profileDropdown.classList.toggle('show');
    console.log('Profile dropdown clicked');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!profileButton.contains(e.target) && !profileDropdown.contains(e.target)) {
      profileDropdown.classList.add('hidden');
      profileDropdown.classList.remove('show');
    }
  });
}

// Profile Dropdown Toggle for mobile
const profileButtonMobile = document.getElementById('profile-button-mobile');
const profileDropdownMobile = document.getElementById('profile-dropdown-mobile');

if (profileButtonMobile && profileDropdownMobile) {
  profileButtonMobile.addEventListener('click', (e) => {
    e.stopPropagation();
    profileDropdownMobile.classList.toggle('hidden');
    profileDropdownMobile.classList.toggle('show');
    console.log('Mobile profile dropdown clicked');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!profileButtonMobile.contains(e.target) && !profileDropdownMobile.contains(e.target)) {
      profileDropdownMobile.classList.add('hidden');
      profileDropdownMobile.classList.remove('show');
    }
  });
}

// Global document click handler for closing menus
document.addEventListener('click', (e) => {
  // Handle hamburger menu
  if (navbarMenu && !navbar.contains(e.target) && navbarMenu.classList.contains('active')) {
    navbarMenu.classList.remove('active');
  }

  // Both handlers below are now moved to their respective sections
});

// Handle window resize for responsive behavior
window.addEventListener('resize', () => {
  if (window.innerWidth > 768) {
    // Reset classes when transitioning to desktop
    if (navbarMenu) {
      navbarMenu.classList.remove('active');
    }
  }
});


const userDropdown = document.getElementById('user-dropdown');
const userDropdownMobile = document.getElementById('user-dropdown-mobile');

let isLoggedIn = false; // Initial state

function updateAuthUI() {
  // Only proceed if elements exist
  if (!loginButton || !userDropdown) return;

  // Handle desktop UI
  if (isLoggedIn) {
    loginButton.classList.add('hidden');
    userDropdown.classList.remove('hidden');

    // Handle mobile UI if elements exist
    if (loginButtonMobile && userDropdownMobile) {
      loginButtonMobile.classList.add('hidden');
      userDropdownMobile.classList.remove('hidden');
    }
  } else {
    loginButton.classList.remove('hidden');
    userDropdown.classList.add('hidden');

    // Handle mobile UI if elements exist
    if (loginButtonMobile && userDropdownMobile) {
      loginButtonMobile.classList.remove('hidden');
      userDropdownMobile.classList.add('hidden');
    }
  }
}

// Initialize mobile auth UI
function initializeMobileAuth() {
  if (!loginButtonMobile || !userDropdownMobile) return;

  if (isLoggedIn) {
    loginButtonMobile.classList.add('hidden');
    userDropdownMobile.classList.remove('hidden');
  } else {
    loginButtonMobile.classList.remove('hidden');
    userDropdownMobile.classList.add('hidden');
  }
}



// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
  console.log('DOM fully loaded');
  // Initialize auth UI
  initializeMobileAuth();
  updateAuthUI();

  // Re-initialize event listeners to ensure they're properly attached
  if (profileButton && profileDropdown) {
    console.log('Profile dropdown initialized');
  }

  if (profileButtonMobile && profileDropdownMobile) {
    console.log('Mobile profile dropdown initialized');
  }
});


// Scroll to Top functionality
const scrollToTopBtn = document.getElementById('scrollToTopBtn');
window.addEventListener('scroll', () => {
  if (window.scrollY > 300) {
    scrollToTopBtn.style.display = 'flex';
  } else {
    scrollToTopBtn.style.display = 'none';
  }
});
scrollToTopBtn.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Fix dropdown menu styles for mobile
document.addEventListener('DOMContentLoaded', function () {
  const profileDropdown = document.getElementById('profile-dropdown');
  const profileButton = document.getElementById('profile-button');

  // Ensure dropdown menu items have normal case and proper styling
  if (profileDropdown) {
    const links = profileDropdown.querySelectorAll('a, button');
    links.forEach(link => {
      link.style.textTransform = 'none';
      link.style.fontWeight = 'normal';
      link.style.fontSize = '0.875rem';
    });
  }

  // Fix mobile dropdown positioning
  function updateDropdownPosition() {
    if (window.innerWidth < 768 && profileDropdown) {
      // Center the dropdown on mobile
      if (profileButton && profileDropdown) {
        const buttonRect = profileButton.getBoundingClientRect();
        profileDropdown.style.left = '50%';
        profileDropdown.style.transform = 'translateX(-50%)';
      }
    } else if (profileDropdown) {
      // Reset to default on desktop
      profileDropdown.style.left = '';
      profileDropdown.style.right = '0';
      profileDropdown.style.transform = '';
    }
  }

  // Update on load and resize
  updateDropdownPosition();
  window.addEventListener('resize', updateDropdownPosition);
});
