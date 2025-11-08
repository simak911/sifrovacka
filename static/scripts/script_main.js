var last_call = Date.now();

function getTeamName(){
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tname');
}

async function init() {
  const baseurl = window.location.origin;
  const url = `${baseurl}/getconfig`;
  const response = await fetch(url);
  const json = await response.json(); 
  const speed = json.speed;
  const wait_time = Math.floor(20 / speed);
  setListeners(wait_time);
}

function setListeners(wait_time){
  document.getElementById("confirm").addEventListener("click", function() {   
      last_call = Date.now();
      const teamname = getTeamName();
      const levelcode = document.getElementById("levelcode").value;
      const baseurl = window.location.origin;
      if (teamname && levelcode) {
        const url = `${baseurl}/entered?code=${levelcode}&tname=${teamname}`;
        window.open(url, "_self");
      } 
      else {
        alert("Vyplň kód stanoviště.");
      }
  });

  document.getElementById("refreshbut").addEventListener("click", function() {
    const cooldown = (Date.now() - last_call);
    if (cooldown > wait_time * 1000) {
      const baseurl = window.location.origin;
      const teamname = getTeamName();
      if (teamname) {
        const url = `${baseurl}/get-hint?tname=${teamname}`;
        window.open(url, "_self")
      }
    }
    else {
      const staystill = Math.floor(wait_time - cooldown / 1000)
      alert(`Prosím počkej ${staystill} sekund a pak klikni.`)
    }
  })
}

init()