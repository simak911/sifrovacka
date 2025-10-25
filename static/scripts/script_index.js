document.getElementById("loginbutton").addEventListener("click", function() {
    // Get the values from the input fields
    const teamid = document.getElementById("teamid").value;
    const baseurl = window.location.origin;

    // Construct the URL based on the input values
    if (teamid) {
      const url = `${baseurl}/main?tname=${teamid}`;
      window.open(url, "_self");  // Navigate to the constructed URL
    } 
    else {
      alert("Please fill in team id.");
    }
  });