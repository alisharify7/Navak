let trs = document.querySelectorAll("tr")
trs.forEach((element) => {
    element.addEventListener("click", (e) => {
        let key = e.currentTarget.dataset.rowKey;
        window.location.href = "/store/product/info/" + key
    })
    element.addEventListener("mouseenter", (e) => {
        e.currentTarget.style.cursor = "pointer"
    })
})