
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');
    const header = document.getElementById('navbar');

    // Smooth scrolling
    navLinks.forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            target.scrollIntoView({ behavior: 'smooth' });
        });
    });

    // Change header color and highlight navigation links on scroll
    const changeHeaderAndHighlight = () => {
        const scrollPosition = window.scrollY;

        // Reset all active links
        navLinks.forEach(link => link.classList.remove('active'));

        // Highlight active link and change header background color
        for (let i = 0; i < sections.length; i++) {
            const sectionTop = sections[i].offsetTop - header.offsetHeight; // Use header height for accuracy
            const sectionBottom = sectionTop + sections[i].offsetHeight;

            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                navLinks[i].classList.add('active');
                navLinks[i].style.color = '#00C896'; // Highlight current section
            } else {
                navLinks[i].style.color = ''; // Reset color
            }
        }
    };

    // Apply on scroll and on load
    changeHeaderAndHighlight();
    window.addEventListener('scroll', changeHeaderAndHighlight);
    window.addEventListener('load', changeHeaderAndHighlight); // Ensure "Home" section highlights on load

    // Smooth scroll for Explore button
    const exploreButton = document.getElementById('exploreButton');
    const aboutSection = document.querySelector('#about');

    exploreButton.addEventListener('click', (event) => {
        event.preventDefault();
        aboutSection.scrollIntoView({ behavior: 'smooth' });
    });
});
