function getTeamName(){
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tname');
}

async function getHintTimes(){
  const baseurl = window.location.origin;
  const teamname = getTeamName();
  const url = `${baseurl}/get-hinttimes?tname=${teamname}`;
  const response = await fetch(url);
  const json = await response.json();
  const status = json.status
  if (status === 'valid') {
    const htime = json.htime;
    const hnumber = json.hnumber;
    if (hnumber !== 0){
      document.getElementById("hintlabel").innerHTML = `Time for the ${hnumber}. hint:`;
      document.getElementById("hinttime").innerHTML = `${htime}`;
    }
    else {
      document.getElementById("hintlabel").innerHTML = '';
      document.getElementById("hinttime").innerHTML = '';
    }
  }
}

document.getElementById("confirm").addEventListener("click", function() {
    const teamname = getTeamName();
    const levelcode = document.getElementById("levelcode").value;
    const baseurl = window.location.origin;
    if (teamname && levelcode) {
      const url = `${baseurl}/entered?code=${levelcode}&tname=${teamname}`;
      window.open(url, "_self");
    } else {
      alert("Please fill in level code.");
    }
  });

document.getElementById("showimg").addEventListener("click", function(){
    const teamname = getTeamName();
    url = window.location.origin + '/get-img' + `?tname=${teamname}`;
    window.open(url, "_blank");
});

document.getElementById("showhint").addEventListener("click", function(){
    const teamname = getTeamName();
    url = window.location.origin + '/get-hint' + `?tname=${teamname}`;
    window.open(url, "_blank");
});

getHintTimes();
setInterval(getHintTimes, 500);