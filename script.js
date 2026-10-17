const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('#site-nav');

if (menuButton && menu) {
  const closeMenu = () => {
    menu.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'افتح القائمة');
  };

  menuButton.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('is-open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'أغلق القائمة' : 'افتح القائمة');
  });

  menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });
}

const year = document.querySelector('#year');
if (year) year.textContent = String(new Date().getFullYear());

if (typeof HTMLDialogElement !== 'undefined' && document.querySelector('[data-lightbox]')) {
  const lightbox = document.createElement('dialog');
  lightbox.className = 'image-lightbox';
  lightbox.setAttribute('aria-label', 'عرض لقطة الشاشة بالحجم الكبير');
  lightbox.innerHTML = `
    <div class="image-lightbox-panel">
      <div class="image-lightbox-toolbar">
        <span>عرض الصورة بالحجم الكبير · اسحب لرؤية التفاصيل</span>
        <button type="button" class="image-lightbox-close" aria-label="إغلاق الصورة">×</button>
      </div>
      <div class="image-lightbox-scroll"><img alt=""></div>
    </div>`;
  document.body.append(lightbox);

  const closeButton = lightbox.querySelector('.image-lightbox-close');
  const fullImage = lightbox.querySelector('img');
  let opener = null;
  let previousOverflow = '';

  document.addEventListener('click', (event) => {
    const link = event.target.closest('[data-lightbox]');
    if (!link) return;
    event.preventDefault();
    opener = link;
    fullImage.src = link.href;
    fullImage.alt = link.querySelector('img')?.alt || 'صورة المقال';
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    lightbox.showModal();
    closeButton.focus();
  });

  closeButton.addEventListener('click', () => lightbox.close());
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) lightbox.close();
  });
  lightbox.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    fullImage.removeAttribute('src');
    opener?.focus();
  });
}
