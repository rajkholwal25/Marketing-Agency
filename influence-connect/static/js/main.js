document.addEventListener("DOMContentLoaded", () => {
  // Auto-hide flash messages
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => el.remove(), 4500);
  });

  // Stagger category cards animation delay
  document.querySelectorAll(".category-grid .category-card").forEach((card, i) => {
    card.style.animationDelay = `${0.05 * i}s`;
  });

  document.querySelectorAll(".cards-grid .profile-card").forEach((card, i) => {
    card.style.animationDelay = `${0.08 * i}s`;
  });

  // Role tab switching on auth pages
  document.querySelectorAll(".role-tab").forEach((tab) => {
    tab.addEventListener("click", (e) => {
      const role = tab.dataset.role;
      if (role) {
        const url = new URL(window.location);
        url.searchParams.set("role", role);
        window.location.href = url.toString();
      }
    });
  });
});
