amountInput = document.getElementById("amount");
stockRemaining = document.getElementById("stock-remaining")
addButton = document.getElementById("add");
addButton.addEventListener("click", () => {
    if (isNaN(amountInput.value) || amountInput.value.includes(".") || amountInput.value.includes("-")) {
        return;
    } else {
        if (parseInt(amountInput.value) < parseInt(stockRemaining.innerHTML.slice(17))) {
            console.log("b");
            amountInput.value = parseInt(amountInput.value) + 1;
        }
    }
});

subtractButton = document.getElementById("subtract");
subtractButton.addEventListener("click", () => {
    if (isNaN(amountInput.value) || amountInput.value.includes(".") || amountInput.value.includes("-")) {
        return;
    } else {
        if (parseInt(amountInput.value) > 1) {
            amountInput.value = parseInt(amountInput.value) - 1;
        }
    }
});

document.addEventListener("click", (event) => {
    let id = event.target.id;
    if (id.includes("star")) {
        document.getElementById("rating").setAttribute("value", id.at(-1));
        for (i = 1; i <= parseInt(id.at(-1)); i++) {
            document.getElementById("star" + i).setAttribute("src", "/static/star_activated.png");
        }
        for (j = parseInt(id.at(-1)) + 1; j <= 5; j++) {
            document.getElementById("star" + j).setAttribute("src", "/static/star_deactivated.png");
        }
    }
});

document.addEventListener("mouseover", (event) => {
    let id = event.target.id;
    if (id.includes("star")) {
        for (i = 1; i <= parseInt(id.at(-1)); i++) {
            star = document.getElementById("star" + i);
            if (star.getAttribute("src") != "/static/star_activated.png") {
                star.setAttribute("src", "/static/star_highlighted.png");
            }
        }
        for (j = parseInt(id.at(-1)) + 1; j <= 5; j++) {
            star = document.getElementById("star" + j);
            if (star.getAttribute("src") != "/static/star_activated.png") {
                star.setAttribute("src", "/static/star_deactivated.png");
            }
        }
    } else {
        for (k = 1; k <= 5; k++) {
            star = document.getElementById("star" + k);
            if (star.getAttribute("src") != "/static/star_activated.png") {
                star.setAttribute("src", "/static/star_deactivated.png");
            }
        }
    }
});