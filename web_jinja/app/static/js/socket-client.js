const socket = io("ws://127.0.0.1", {
  path: "/api/socket.io",
});

socket.on("connect", () => {
  console.log("✅ Connected:", socket.id);
  document.getElementById("status").textContent = "Connected";

  if (user) {
    socket.emit("set_user", { user: user });
  }

});

socket.on("disconnect", () => {
  console.log("❌ Disconnected");
  document.getElementById("status").textContent = "Disconnected";
});

socket.on("my_messages", (data) => {
  const container = document.getElementById("my_messages");
  const { title, time, message } = data;

  if (!title) return;

  // Створюємо обгортку повідомлення
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("mb-2");

  msgDiv.innerHTML = `
    <div class="success success-info shadow-sm">
      <strong >🔔 ${title}</strong><br>
      <small class="text-muted">${time}</small><br>
      <span>${message}</span>
    </div>
  `;

  container.appendChild(msgDiv);

  // Видаляємо через 5 секунд
setTimeout(() => {
  msgDiv.classList.add("fade-out");
  setTimeout(() => msgDiv.remove(), 500); // після анімації
}, 5000);
});



document.getElementById("test_messages").onclick = () => {
  socket.emit("my_messages", {}, (response) => {
    console.log("my_messages:", response);
  });
};

socket.on("users_list", (data) => {
  const rawUsers = data["users_list"]; // або ["Список користувачів"]

  const users = Object.entries(rawUsers).map(([sid, userStr]) => ({
    sid,
    ...JSON.parse(userStr)
  }));

  console.log("Список користувачів:");
  users.forEach(user => {
    console.log(`SID: ${user.sid}, Name: ${user.name}, Email: ${user.email}`);
  });
});



