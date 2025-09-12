// Modern JavaScript for Manga Recommendation System

// DOM Content Loaded
document.addEventListener("DOMContentLoaded", () => {
  initializeApp()
})

function initializeApp() {
  // Initialize star ratings
  initializeStarRatings()

  // Initialize search form
  initializeSearchForm()

  // Initialize sample title clicks
  initializeSampleTitles()

  // Initialize animations
  initializeAnimations()
}

// Star Rating System
function initializeStarRatings() {
  const starContainers = document.querySelectorAll(".rating-stars")

  starContainers.forEach((container) => {
    const stars = container.querySelectorAll(".star")
    let currentRating = 0

    stars.forEach((star, index) => {
      star.addEventListener("mouseenter", () => {
        highlightStars(stars, index + 1)
      })

      star.addEventListener("mouseleave", () => {
        highlightStars(stars, currentRating)
      })

      star.addEventListener("click", () => {
        currentRating = index + 1
        highlightStars(stars, currentRating)
        container.dataset.rating = currentRating

        // Add visual feedback
        star.style.transform = "scale(1.3)"
        setTimeout(() => {
          star.style.transform = "scale(1)"
        }, 200)
      })
    })
  })
}

function highlightStars(stars, rating) {
  stars.forEach((star, index) => {
    if (index < rating) {
      star.classList.add("active")
    } else {
      star.classList.remove("active")
    }
  })
}

// Submit Rating Function
function submitRating(mangaId) {
  const ratingContainer = document.querySelector(`[data-manga-id="${mangaId}"]`)
  const rating = ratingContainer?.dataset.rating

  if (!rating) {
    showNotification("Please select a rating first!", "warning")
    return
  }

  const button = event.target
  const originalText = button.innerHTML

  // Show loading state
  button.innerHTML = '<span class="loading"></span> Rating...'
  button.disabled = true

  // Simulate API call (replace with actual endpoint)
  fetch("/api/rate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      manga_id: mangaId,
      rating: Number.parseInt(rating),
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showNotification("Rating submitted successfully!", "success")
        button.innerHTML = "✓ Rated"
        button.style.background = "var(--secondary)"
      } else {
        throw new Error(data.message || "Failed to submit rating")
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      showNotification("Failed to submit rating. Please try again.", "error")
      button.innerHTML = originalText
      button.disabled = false
    })
}

// Search Form Enhancement
function initializeSearchForm() {
  const searchForm = document.querySelector(".search-form")
  const searchInput = document.querySelector(".search-input")
  const searchBtn = document.querySelector(".search-btn")

  if (!searchForm) return

  searchForm.addEventListener("submit", (e) => {
    const btnText = searchBtn.querySelector(".btn-text")
    const loading = searchBtn.querySelector(".loading")

    if (btnText && loading) {
      btnText.style.display = "none"
      loading.style.display = "inline-block"
      searchBtn.disabled = true
    }
  })

  // Add search suggestions (if you have an endpoint for this)
  let searchTimeout
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      // Implement search suggestions here if needed
    }, 300)
  })
}

// Sample Title Interaction
function initializeSampleTitles() {
  const sampleTitles = document.querySelectorAll(".sample-title")

  sampleTitles.forEach((title) => {
    title.addEventListener("click", function () {
      const titleText = this.textContent
      fillSearchInput(titleText)
    })
  })
}

function fillSearchInput(title) {
  const searchInput = document.querySelector(".search-input")
  if (searchInput) {
    searchInput.value = title
    searchInput.focus()

    // Add visual feedback
    searchInput.style.borderColor = "var(--primary)"
    setTimeout(() => {
      searchInput.style.borderColor = "var(--border)"
    }, 1000)
  }
}

// Animation Utilities
function initializeAnimations() {
  // Intersection Observer for fade-in animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1"
        entry.target.style.transform = "translateY(0)"
      }
    })
  }, observerOptions)

  // Observe all cards for animation
  const cards = document.querySelectorAll(".card")
  cards.forEach((card, index) => {
    card.style.opacity = "0"
    card.style.transform = "translateY(30px)"
    card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`
    observer.observe(card)
  })
}

// Notification System
function showNotification(message, type = "info") {
  // Remove existing notifications
  const existingNotifications = document.querySelectorAll(".notification")
  existingNotifications.forEach((notification) => notification.remove())

  // Create notification element
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: inherit; font-size: 1.2rem; cursor: pointer; margin-left: 1rem;">&times;</button>
    `

  // Add styles
  Object.assign(notification.style, {
    position: "fixed",
    top: "20px",
    right: "20px",
    padding: "1rem 1.5rem",
    borderRadius: "var(--radius)",
    color: "white",
    fontWeight: "600",
    zIndex: "1000",
    display: "flex",
    alignItems: "center",
    maxWidth: "400px",
    boxShadow: "var(--shadow-lg)",
    animation: "slideInRight 0.3s ease",
  })

  // Set background color based on type
  const colors = {
    success: "var(--secondary)",
    error: "var(--destructive)",
    warning: "#f59e0b",
    info: "var(--primary)",
  }
  notification.style.background = colors[type] || colors.info

  // Add to DOM
  document.body.appendChild(notification)

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.style.animation = "slideOutRight 0.3s ease"
      setTimeout(() => notification.remove(), 300)
    }
  }, 5000)
}

// Add CSS animations for notifications
const style = document.createElement("style")
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`
document.head.appendChild(style)

// Utility Functions
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Theme Toggle (if you want to add dark mode later)
function toggleTheme() {
  document.body.classList.toggle("dark-theme")
  localStorage.setItem("theme", document.body.classList.contains("dark-theme") ? "dark" : "light")
}

// Load saved theme
function loadTheme() {
  const savedTheme = localStorage.getItem("theme")
  if (savedTheme === "dark") {
    document.body.classList.add("dark-theme")
  }
}

// Initialize theme on load
loadTheme()
