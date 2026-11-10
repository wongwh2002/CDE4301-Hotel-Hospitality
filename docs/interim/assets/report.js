(() => {
  const toggle = document.querySelector('.menu-toggle');
  const rail = document.querySelector('.rail');
  if (toggle && rail) {
    toggle.addEventListener('click', () => {
      const open = rail.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    rail.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      rail.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }));
  }
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
  const progress = document.querySelector('.progress span');
  const updateProgress = () => {
    if (!progress) return;
    const available = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = `${available > 0 ? Math.min(100, scrollY / available * 100) : 100}%`;
  };
  addEventListener('scroll', updateProgress, {passive: true});
  addEventListener('resize', updateProgress);
  updateProgress();
  const headings = [...document.querySelectorAll('article > h2[id]')];
  const navLinks = [...document.querySelectorAll('.rail nav a')];
  if (headings.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(e => e.isIntersecting).sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (!visible.length) return;
      const id = visible[0].target.id;
      navLinks.forEach(link => {
        const active = link.getAttribute('href') === '#' + id;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, {rootMargin: '-10% 0px -65% 0px'});
    headings.forEach(h => observer.observe(h));
  }
  const search = document.querySelector('#transcript-search');
  const entries = [...document.querySelectorAll('.transcript-entry')];
  const count = document.querySelector('#search-count');
  const noResults = document.querySelector('#no-results');
  if (search) search.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase();
    let matches = 0;
    entries.forEach(entry => {
      const match = !query || entry.textContent.toLocaleLowerCase().includes(query);
      entry.hidden = !match;
      if (match) matches++;
    });
    if (count) count.textContent = `${matches} of ${entries.length} passages`;
    if (noResults) noResults.hidden = matches > 0;
  });
  const video = document.querySelector('#recording');
  document.querySelectorAll('[data-seek]').forEach(link => link.addEventListener('click', event => {
    if (!video) return;
    event.preventDefault();
    const time = Number(link.dataset.seek);
    if (video.readyState > 0) video.currentTime = time;
    else video.addEventListener('loadedmetadata', () => {video.currentTime = time;}, {once:true});
    video.play().catch(() => {});
  }));
})();
