const maxload = 30
var last_call = Date.now();
var last_call_2 = Date.now();
const navType = performance.getEntriesByType("navigation")[0].type;

function getTeamName(){
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tname');
}

async function updateHintData() {
  const baseurl = window.location.origin;
  const teamname = getTeamName();
  const resp = await fetch (`${baseurl}/get-hint?tname=${teamname}`);
  const json = await resp.json()
  const msg = json.msg
  const suc = json.suc
  const elem = document.getElementById('textinfo');
  elem.innerHTML = msg
  elem.classList = [suc]
  }


async function init() {
  const baseurl = window.location.origin;
  const url = `${baseurl}/getconfig`;
  const response = await fetch(url);
  const json = await response.json(); 
  const speed = json.speed;
  const wait_time = Math.floor(maxload / speed);
  setInterval(updateHintData, wait_time * 1000);
  if (sessionStorage.getItem("pageLoaded") || (navType == "reload")) {}
  else {
    last_call_2 = Date.now() - 2000 * maxload;
    sessionStorage.setItem("pageLoaded", "true");
    updateHintData();  
  }
  setListeners(wait_time);
}

function setListeners(wait_time){
  document.getElementById("confirm").addEventListener("click", function() {
      const cooldown = (Date.now() - last_call_2);
      if (cooldown > wait_time * 1000) {
      last_call_2 = Date.now();
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
      }
      else {
      const staystill = Math.floor(wait_time - cooldown / 1000)
      alert(`Prosím počkej ${staystill} sekund a pak klikni.`)
    }  
  });

  document.getElementById("refreshbut").addEventListener("click", function() {
    const cooldown = (Date.now() - last_call);
    if (cooldown > wait_time * 1000) {
      last_call = Date.now();
      updateHintData()
    }
    else {
      const staystill = Math.floor(wait_time - cooldown / 1000)
      alert(`Prosím počkej ${staystill} sekund a pak klikni.`)
    }
  })
}

init()