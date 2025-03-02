document.addEventListener("DOMContentLoaded", function () {
  const themeToggleBtn = document.getElementById("theme-toggle");
  const body = document.body;

  // Перевірка localStorage, чи вже збережена тема
  if (localStorage.getItem("theme") === "dark") {
      body.classList.add("dark-mode");
      themeToggleBtn.classList.replace("btn-dark", "btn-light");
      themeToggleBtn.innerHTML = "☀️";

      // Зміна класів для елементів з bg-light на bg-dark
      document.querySelectorAll('.bg-light').forEach(function(element) {
          element.classList.replace('bg-light', 'bg-dark');
      });

      // Зміна класів для елементів з dropdown-menu-light на dropdown-menu-dark
      document.querySelectorAll('.dropdown-menu-light').forEach(function(element) {
          element.classList.replace('dropdown-menu-light', 'dropdown-menu-dark');
      });
  }

  themeToggleBtn.addEventListener("click", function () {
      body.classList.toggle("dark-mode");

      // Перемикання класу кнопки
      if (body.classList.contains("dark-mode")) {
          localStorage.setItem("theme", "dark");
          themeToggleBtn.classList.replace("btn-dark", "btn-light");
          themeToggleBtn.innerHTML = "☀️";

          // Зміна класів для елементів з bg-light на bg-dark
          document.querySelectorAll('.bg-light').forEach(function(element) {
              element.classList.replace('bg-light', 'bg-dark');
          });

          // Зміна класів для елементів з dropdown-menu-light на dropdown-menu-dark
          document.querySelectorAll('.dropdown-menu-light').forEach(function(element) {
              element.classList.replace('dropdown-menu-light', 'dropdown-menu-dark');
          });
      } else {
          localStorage.setItem("theme", "light");
          themeToggleBtn.classList.replace("btn-light", "btn-dark");
          themeToggleBtn.innerHTML = "🌘";

          // Зміна класів для елементів з bg-dark на bg-light
          document.querySelectorAll('.bg-dark').forEach(function(element) {
              element.classList.replace('bg-dark', 'bg-light');
          });

          // Зміна класів для елементів з dropdown-menu-dark на dropdown-menu-light
          document.querySelectorAll('.dropdown-menu-dark').forEach(function(element) {
              element.classList.replace('dropdown-menu-dark', 'dropdown-menu-light');
          });
      }
  });
});
