function add_links_tr() {
    // this function handle when user click on a row
    // redirect user to message page
    let trs = document.querySelectorAll("tr.data-tr");
    trs.forEach((e) => {
        e.addEventListener("click", (element) => {

            window.location.href = "/message/show/" + (element.currentTarget.dataset.mailKey);
        })
        e.addEventListener("mouseover", e => {
            e.target.style.cursor = "pointer";
        })
    })
}

add_links_tr()