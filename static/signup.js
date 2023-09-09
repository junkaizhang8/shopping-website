const countryList = document.getElementById("countries");
const userCountry = document.getElementById("country");
userCountry.addEventListener("input", () => {
    let innerScript = "";
    let numOfCountries = 0;
    for (const country of countries) {
        if (country.slice(0, userCountry.value.length).toLowerCase() == userCountry.value.toLowerCase() && userCountry.value != "") {
            numOfCountries++;
            innerScript = innerScript.concat("<li class='list-group-item' id='country" + numOfCountries + "'>" + country + "</li>");
        }
    }
    countryList.innerHTML = innerScript;
});

document.addEventListener("mouseover", (event) => {
  let id = event.target.id;
  if (id.includes("country")) {
    let element = document.getElementById(id);
    element.classList.add("active");
  }
});

document.addEventListener("mouseout", (event) => {
  let id = event.target.id;
  if (id.includes("country")) {
    let element = document.getElementById(id);
    element.classList.remove("active")
  }
});

document.addEventListener("click", (event) => {
  let id = event.target.id;
  if (id.includes("country") && id !== "country") {
    let element = document.getElementById(id);
    userCountry.value = element.innerHTML;
    countryList.innerHTML = "";
  }
});