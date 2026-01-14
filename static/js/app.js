// Scroll navigation and animations
document.addEventListener('DOMContentLoaded', function(){
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
          if(navDots[index]) navDots[index].classList.add('active');
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

  // Detection functionality
  fetchStats();
  detectorStatus();
  setInterval(fetchStats, 1000);
  setInterval(detectorStatus, 3000);
  
  const stopBtn = document.getElementById('stop-detector');
  if(stopBtn) stopBtn.addEventListener('click', stopDetector);
  
  const refreshBtn = document.getElementById('refresh-status');
  if(refreshBtn) refreshBtn.addEventListener('click', function(){
    fetchStats();
    detectorStatus();
  });

  // SSE-driven detection announcements
  (async function(){
    let known = new Set();
    try{
      const all = await fetch('/detections/all');
      if(all.ok){
        const j = await all.json();
        if(Array.isArray(j.seen)) j.seen.forEach(s=>known.add(s));
      }
    }catch(e){ console.warn('Could not fetch initial detections', e); }

    try{
      const es = new EventSource('/detections/stream');
      const pending = new Set();
      const queueTTS = [];
      let speaking = false;

      function speakNext(){
        if(queueTTS.length === 0){ speaking = false; return }
        speaking = true;
        const label = queueTTS.shift();
        try{
          const utter = new SpeechSynthesisUtterance(label);
          utter.onend = () => {
            pending.delete(label);
            known.add(label);
            setTimeout(speakNext, 120);
          };
          window.speechSynthesis.speak(utter);
        }catch(e){
          console.warn('TTS error', e);
          pending.delete(label);
          setTimeout(speakNext, 100);
        }
      }

      es.onmessage = function(evt){
        try{
          const data = JSON.parse(evt.data);
          if(data && data.label){
            const label = data.label;
            if(!known.has(label) && !pending.has(label)){
              pending.add(label);
              queueTTS.push(label);
              if(!speaking) speakNext();
            }
          }
        }catch(e){ console.warn('SSE parse error', e); }
      };
      es.onerror = function(e){ /* silent reconnect */ };
    }catch(e){ console.warn('EventSource not supported', e); }
  })();
});

async function fetchStats(){
  try{
    const res = await fetch('/api/stats');
    if(!res.ok) throw new Error('no stats');
    const j = await res.json();
    document.getElementById('frames').innerText = j.frames_processed ?? 0;
    document.getElementById('detcount').innerText = j.last_detection_count ?? 0;
    document.getElementById('statusText').innerText = 'Running';
  }catch(e){
    document.getElementById('statusText').innerText = 'Unavailable';
  }
}

async function detectorStatus(){
  try{
    const res = await fetch('/detector/status');
    if(!res.ok) throw new Error('no status');
    const j = await res.json();
    document.getElementById('det-run').innerText = j.running ? 'Active' : 'Stopped';
  }catch(e){
    document.getElementById('det-run').innerText = 'Unknown';
  }
}

async function stopDetector(){
  try{
    const res = await fetch('/detector/stop', {method:'POST'});
    if(!res.ok) throw new Error('stop failed');
    const j = await res.json();
    alert('Stopped: ' + j.stopped);
  }catch(e){
    alert('Stop endpoint not available');
  }
}
