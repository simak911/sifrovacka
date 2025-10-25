function getTeamName(){
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tname');
}

document.getElementById("resetbutton").addEventListener("click", function() {
    const teamname = getTeamName();
    const baseurl = window.location.origin;
    const resetname = document.getElementById("teamid").value;
    if (teamname && resetname) {
      const url = `${baseurl}/reset-game?rname=${resetname}&tname=${teamname}`;
      window.open(url, "_self");
    } else {
      alert("Please fill in team id.");
    }
  });

document.getElementById("statsbutton").addEventListener("click", function() {
    const teamname = getTeamName();
    const baseurl = window.location.origin;
    const url = `${baseurl}/get-stats?tname=${teamname}`;
    window.open(url, "_blank");
  });