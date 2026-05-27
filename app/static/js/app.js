document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
      form.querySelectorAll("button[type='submit'], input[type='submit']").forEach(btn => btn.disabled = true);
    });
  });
});
