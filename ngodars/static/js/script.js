document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');
    const header = document.getElementById('navbar');
    const animatedItems = document.querySelectorAll('.animate-on-scroll');

    // Smooth scrolling for internal links
    navLinks.forEach(link => {
        if (link.getAttribute('href').startsWith('#')) {
            link.addEventListener('click', event => {
                event.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                target.scrollIntoView({ behavior: 'smooth' });
            });
        }
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
    window.addEventListener('load', changeHeaderAndHighlight);

    // Smooth scroll for Explore button
    const exploreButton = document.getElementById('exploreButton');
    const aboutSection = document.querySelector('#about');

    exploreButton.addEventListener('click', (event) => {
        event.preventDefault();
        aboutSection.scrollIntoView({ behavior: 'smooth' });
    });

    // Intersection Observer for pop-up animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('opacity-100', 'scale-100');
                entry.target.classList.remove('opacity-0', 'scale-90');
            }
        });
    }, {
        threshold: 0.2 // Trigger when 20% of the item is visible
    });

    animatedItems.forEach(item => {
        observer.observe(item);
    });
});
