document.addEventListener("DOMContentLoaded", function () {
  const themeToggleBtn = document.getElementById("theme-toggle");
  const body = document.body;

  // Перевірка localStorage, чи вже збережена тема
  if (localStorage.getItem("theme") === "dark") {
      body.classList.add("dark-mode");
      themeToggleBtn.classList.replace("btn-dark", "btn-light");
      themeToggleBtn.innerHTML = "☀️";
  }

  themeToggleBtn.addEventListener("click", function () {
      body.classList.toggle("dark-mode");

      // Перемикання класу кнопки
      if (body.classList.contains("dark-mode")) {
          localStorage.setItem("theme", "dark");
          themeToggleBtn.classList.replace("btn-dark", "btn-light");
          themeToggleBtn.innerHTML = "☀️";
      } else {
          localStorage.setItem("theme", "light");
          themeToggleBtn.classList.replace("btn-light", "btn-outline-secondary");
          themeToggleBtn.innerHTML = "🌘";
      }
  });
});
