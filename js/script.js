// Fetch metadata and render portfolio
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('../metadata.json');
        const data = await response.json();
        
        // Render About Section
        renderAbout(data.about);
        
        // Render Social Media Links
        renderSocialLinks(data.socialMedia);
        
        // Render Experience
        renderExperience(data.experience);
        
        // Render Projects
        renderProjects(data.projects);
        
        // Render Education
        renderEducation(data.education);
        
        // Setup Navigation
        setupNavigation();
        
    } catch (error) {
        console.error('Error fetching metadata:', error);
    }
});

// Render About Section
function renderAbout(about) {
    document.getElementById('name').textContent = about.name;
    document.getElementById('title').textContent = about.title;
    document.getElementById('description').textContent = about.description;
    const profileImg = document.getElementById('profile-photo');
    profileImg.src = about.profilePhoto;
    profileImg.onerror = function() {
        // Fallback if image doesn't load
        this.style.display = 'none';
    };
}

// Render Social Media Links
function renderSocialLinks(socialMedia) {
    const socialLinksContainer = document.getElementById('social-links');
    socialLinksContainer.innerHTML = '';
    
    const socialLinks = [
        { name: 'LinkedIn', url: socialMedia.linkedin, icon: 'fab fa-linkedin' },
        { name: 'GitHub', url: socialMedia.github, icon: 'fab fa-github' },
        { name: 'Instagram', url: socialMedia.instagram, icon: 'fab fa-instagram' },
        { name: 'Twitter', url: socialMedia.twitter, icon: 'fab fa-twitter' }
    ];
    
    socialLinks.forEach(link => {
        const a = document.createElement('a');
        a.href = link.url.startsWith('http') ? link.url : `https://${link.url}`;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.setAttribute('aria-label', link.name);
        
        const i = document.createElement('i');
        i.className = link.icon;
        
        a.appendChild(i);
        socialLinksContainer.appendChild(a);
    });
}

// Render Experience Section
function renderExperience(experience) {
    const experienceContainer = document.getElementById('experience-list');
    experienceContainer.innerHTML = '';
    
    experience.forEach(exp => {
        const experienceItem = document.createElement('div');
        experienceItem.className = 'experience-item';
        
        experienceItem.innerHTML = `
            <h3>${exp.title}</h3>
            <div class="company">${exp.company}</div>
            <div class="duration">${exp.duration}</div>
            <p class="description">${exp.description}</p>
        `;
        
        experienceContainer.appendChild(experienceItem);
    });
}

// Render Projects Section
function renderProjects(projects) {
    const projectsContainer = document.getElementById('projects-list');
    projectsContainer.innerHTML = '';
    
    projects.forEach(project => {
        const projectCard = document.createElement('div');
        projectCard.className = 'project-card';
        
        // Create tech stack tags
        const techStackHTML = project.techStack.map(tech => 
            `<span class="tech-tag">${tech}</span>`
        ).join('');
        
        projectCard.innerHTML = `
            <h3>${project.name}</h3>
            <p class="description">${project.description}</p>
            <div class="tech-stack">
                ${techStackHTML}
            </div>
        `;
        
        // Add click event to navigate to GitHub
        projectCard.addEventListener('click', () => {
            window.open(project.githubLink, '_blank', 'noopener,noreferrer');
        });
        
        projectsContainer.appendChild(projectCard);
    });
}

// Render Education Section
function renderEducation(education) {
    const educationContainer = document.getElementById('education-list');
    educationContainer.innerHTML = '';
    
    education.forEach(edu => {
        const educationItem = document.createElement('div');
        educationItem.className = 'education-item';
        
        const detailsHTML = [];
        if (edu.cgpa) {
            detailsHTML.push(`CGPA: ${edu.cgpa}`);
        }
        if (edu.percentage) {
            detailsHTML.push(`Percentage: ${edu.percentage}`);
        }
        
        educationItem.innerHTML = `
            <h3>${edu.institution}</h3>
            <div class="degree">${edu.degree}</div>
            ${detailsHTML.length > 0 ? `<div class="details">${detailsHTML.join(' · ')}</div>` : ''}
            <div class="duration">${edu.duration}</div>
            <div class="location">${edu.location}</div>
        `;
        
        educationContainer.appendChild(educationItem);
    });
}

// Setup Navigation
function setupNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    // Mobile menu toggle
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile menu if open
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                }
            }
        });
    });
    
    // Add active class to current section in navigation
    window.addEventListener('scroll', () => {
        let current = '';
        const sections = document.querySelectorAll('section[id]');
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

