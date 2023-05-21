const mainNav = document.getElementById('main-nav');

setTimeout(() => {
  mainNav.classList.add('nav-hidden');
}, 2000);

mainNav.addEventListener('mouseover', () => {
  mainNav.classList.remove('nav-hidden');
});

mainNav.addEventListener('mouseout', () => {
  mainNav.classList.add('nav-hidden');
});