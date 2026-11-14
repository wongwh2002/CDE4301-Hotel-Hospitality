const menu = document.querySelector('.menu');
const navigation = document.querySelector('.navlinks');

if (menu && navigation) {
  const setOpen = (open) => {
    navigation.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
  };

  menu.addEventListener('click', () => {
    setOpen(!navigation.classList.contains('open'));
  });

  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) setOpen(false);
  });

  document.addEventListener('click', (event) => {
    if (!navigation.contains(event.target) && !menu.contains(event.target)) {
      setOpen(false);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && navigation.classList.contains('open')) {
      setOpen(false);
      menu.focus();
    }
  });

  window.matchMedia('(max-width: 850px)').addEventListener('change', () => setOpen(false));
}

const links = [...document.querySelectorAll('.toc a[href^="#"]')];
if (links.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        links.forEach((link) => link.classList.toggle('current', link.hash === '#' + entry.target.id));
      }
    });
  }, { rootMargin: '-100px 0px -72% 0px' });

  links.forEach((link) => {
    const section = document.getElementById(link.hash.slice(1));
    if (section) observer.observe(section);
  });
}

document.querySelector('#toc-search')?.addEventListener('input', (event) => {
  const query = event.target.value.trim().toLowerCase();
  links.forEach((link) => {
    link.style.display = link.textContent.toLowerCase().includes(query) ? '' : 'none';
  });
});
