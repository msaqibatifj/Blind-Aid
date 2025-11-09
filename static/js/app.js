async function fetchStats(){
  try{
    const res = await fetch('/api/stats');
    if(!res.ok) throw new Error('no stats');
    const j = await res.json();
    document.getElementById('frames').innerText = j.frames_processed ?? 0;
    document.getElementById('detcount').innerText = j.last_detection_count ?? 0;
    document.getElementById('statusText').innerText = 'running';
  }catch(e){
    document.getElementById('statusText').innerText = 'unavailable';
  }
}

async function detectorStatus(){
  try{
    const res = await fetch('/detector/status');
    if(!res.ok) throw new Error('no status');
    const j = await res.json();
    document.getElementById('det-run').innerText = j.running ? 'Yes' : 'No';
  }catch(e){
    document.getElementById('det-run').innerText = 'unknown';
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

document.addEventListener('DOMContentLoaded', function(){
  fetchStats();
  detectorStatus();
  setInterval(fetchStats, 1000);
  setInterval(detectorStatus, 3000);
  const stopBtn = document.getElementById('stop-detector');
  if(stopBtn) stopBtn.addEventListener('click', stopDetector);
  // Recording UI removed — no client-side recording actions required.
  // SSE-driven detection announcements — maintain a master-known set fetched on connect
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
      const pending = new Set(); // labels pending or playing
      const queueTTS = [];
      let speaking = false;

      function speakNext(){
        if(queueTTS.length === 0){ speaking = false; return }
        speaking = true;
        const label = queueTTS.shift();
        try{
          const utter = new SpeechSynthesisUtterance(label);
          utter.onend = () => {
            // after playback, mark as known and remove from pending
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
