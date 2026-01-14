document.addEventListener('DOMContentLoaded', function(){
  const goBtn = document.getElementById('go-to-app');
  const scrollContainer = document.querySelector('.scroll-container');
  const sections = document.querySelectorAll('.section');
  const navDots = document.querySelectorAll('.nav-dot');
  
  // Update active nav dot on scroll
  if(scrollContainer && navDots.length > 0){
    scrollContainer.addEventListener('scroll', function(){
      const scrollPos = scrollContainer.scrollTop;
      const windowHeight = window.innerHeight;
      
      sections.forEach((section, index) => {
        const sectionTop = section.offsetTop;
        const sectionBottom = sectionTop + section.offsetHeight;
        
        if(scrollPos >= sectionTop - windowHeight/2 && scrollPos < sectionBottom - windowHeight/2){
          navDots.forEach(dot => dot.classList.remove('active'));
          navDots[index].classList.add('active');
        }
      });
    });
    
    // Click on nav dots to scroll to section
    navDots.forEach((dot, index) => {
      dot.addEventListener('click', function(){
        sections[index].scrollIntoView({ behavior: 'smooth' });
      });
    });
  }
  
  // App button with ripple effect
  if(goBtn){
    goBtn.addEventListener('click', function(e){
      e.preventDefault();
      
      // Create ripple effect
      const ripple = document.createElement('span');
      ripple.style.cssText = `
        position:absolute;
        border-radius:50%;
        background:rgba(255,255,255,0.6);
        width:20px;
        height:20px;
        animation: ripple 0.6s ease-out;
        pointer-events:none;
      `;
      
      // Position ripple at click location
      const rect = goBtn.getBoundingClientRect();
      ripple.style.left = (e.clientX - rect.left - 10) + 'px';
      ripple.style.top = (e.clientY - rect.top - 10) + 'px';
      goBtn.appendChild(ripple);
      
      // Navigate after animation
      setTimeout(() => {
        window.location.href = '/app';
      }, 300);
      
      // Clean up ripple element
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  }
  
  // Animate elements when they come into view
  const observerOptions = {
    root: scrollContainer,
    threshold: 0.3
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);
  
  // Observe all section content for animations
  document.querySelectorAll('.section-content').forEach(content => {
    content.style.opacity = '0';
    content.style.transform = 'translateY(30px)';
    content.style.transition = 'all 0.8s ease-out';
    observer.observe(content);
  });
  
  // Make first section visible immediately
  const firstContent = document.querySelector('.section-welcome .section-content');
  if(firstContent){
    firstContent.style.opacity = '1';
    firstContent.style.transform = 'translateY(0)';
  }
});