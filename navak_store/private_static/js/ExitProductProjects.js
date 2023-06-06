let inputs = document.querySelectorAll("input.product-exit-qt")

inputs.forEach((each) => {
    if (each.value < 0 || !each.value) {
        each.value = 0;
    }
    each.addEventListener("keyup", (e) => {
        if (e.currentTarget.value < 0 || !e.currentTarget.value) {
            e.currentTarget.value = 0;
        }
    })
})


let ProductsProject = document.querySelector("#productsProject")
let FormExitProduct = document.querySelector("#FormExitProduct")
FormExitProduct.addEventListener("submit", (e) => {
    data = {}

    let zeros = 0;
    for (let each of inputs) {
        let ProductKey = (each.dataset.productKey);
        let Value = each.value;
        if (each.value == "0") {
            zeros++;
        }
        data[ProductKey] = Value;
    }

    if (zeros == inputs.length) {
        e.preventDefault()
        Swal.fire({
            title:"اخطار",
            text:"امکان ثبت گزارش وجود ندارد",
            icon:"warning"
        })
    } else {
        ProductsProject.value = JSON.stringify(data);
        FormExitProduct.submit();
    }
})