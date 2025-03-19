function showAlert(message, status) {
    let alertBox = document.createElement("div");
    alertBox.className = `alert alert-${status} alert-dismissible fade show`;
    alertBox.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(alertBox);
    
    setTimeout(() => {
        alertBox.remove();
    }, 3000);
}

async function handleFormSubmit(event, endpoint, redirect = null) {
    event.preventDefault();
    let formData = new FormData(event.target);
    let jsonData = Object.fromEntries(formData.entries());

    let response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jsonData)
    });

    let data = await response.json();
    showAlert(data.message, data.status);

    if (data.redirect) {
        setTimeout(() => {
            window.location.href = data.redirect;
        }, 2000);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    let forms = document.querySelectorAll("form[data-ajax]");
    forms.forEach(form => {
        form.addEventListener("submit", (event) => {
            let endpoint = form.getAttribute("action");
            handleFormSubmit(event, endpoint);
        });
    });
});
