// app.js intentionally empty
// React code is handled inside HTML with Babel
async function search() {
    const location = document.getElementById("loc").value;
    const min = document.getElementById("min").value;
    const max = document.getElementById("max").value;
  
    const res = await fetch(
      `/api/providers/search?location=${location}&min_price=${min}&max_price=${max}`
    );
  
    const data = await res.json();
    console.log(data);
  }
  