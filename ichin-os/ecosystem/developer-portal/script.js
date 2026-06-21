document.addEventListener('DOMContentLoaded', () => {
  const navLinks = document.querySelectorAll('.nav-list a[data-section]')
  const sections = document.querySelectorAll('.section')

  function activateSection(id) {
    sections.forEach(s => s.classList.remove('active'))
    const target = document.getElementById(id)
    if (target) target.classList.add('active')

    navLinks.forEach(l => l.classList.remove('active'))
    const link = document.querySelector(`.nav-list a[data-section="${id}"]`)
    if (link) link.classList.add('active')
  }

  navLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault()
      const id = link.getAttribute('data-section')
      activateSection(id)
      history.pushState(null, '', `#${id}`)
    })
  })

  const hash = window.location.hash.slice(1)
  if (hash && document.getElementById(hash)) {
    activateSection(hash)
  } else {
    activateSection('getting-started')
  }

  window.addEventListener('hashchange', () => {
    const id = window.location.hash.slice(1)
    if (id && document.getElementById(id)) activateSection(id)
  })
})
