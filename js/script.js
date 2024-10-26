// ملف JavaScript بسيط لتفعيل الوضع الليلي
const toggleDarkMode = document.querySelector('.dark-mode-toggle input');

toggleDarkMode.addEventListener('change', () => {
  document.body.classList.toggle('dark-mode');
});
