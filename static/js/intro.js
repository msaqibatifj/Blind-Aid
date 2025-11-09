document.addEventListener('DOMContentLoaded', function(){
  const goBtn = document.getElementById('go-to-app');
  if(goBtn){
    goBtn.addEventListener('click', function(e){
      e.preventDefault();
      window.location.href = '/app';
    });
  }
});
