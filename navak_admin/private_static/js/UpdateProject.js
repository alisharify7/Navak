var page = 1;
var selected = new Set();
var counter_selected_product = new Object()


window.addEventListener("DOMContentLoaded", async (e) => {
    loading_animation(2000)
    let products = document.querySelector("#ProjectProducts")
    let data = JSON.parse(products.value)
    for (let productKey in data) {
        let product = (await verify_product(productKey))
        product = JSON.stringify(product)
        selected.add(product)
        // convert product qty from 0/150 to 150
        console.log(data)
        counter_selected_product[product] = data[productKey].split("/")[1]
    }
    update_table_product_show()
    counter_product_tracker()
})

async function bring_store_product() {
    let headers = {
        "X-CSRFToken": document.querySelector("#csrf_token").value
    }
    let response = await fetch(`/store/_get/product/?page=${page}`, {
        method: "GET",
        headers: headers,
    })
    let data = await response.json()
    return data
}


let product_placeholder = document.querySelector("#store-product-placeholder")

function put_data_in_modal(data) {
    product_placeholder.innerHTML = "";
    Array.from(data).forEach((each) => {
        if (selected.has(JSON.stringify(each))) {
            temp = `    
                <div dir="rtl" class="col-lg-3 col-md-4 col-12 my-2">
                        <div class="border shadow-sm p-2">
                            <p class="m-0 border-bottom py-2">نام محصول: ${each.ProductName} </p>
                            <p class="m-0 border-bottom py-2">پارت نامبر: ${each.ProductPartNumber} </p>
                            <p class="m-0 border-bottom py-2">شماره انبار: ${each.ProductStoreId}</p>
                            <p class="m-0 border-bottom py-2">کارخانه سازنده: ${each.ProductManufacture}</p>
                            <p class="m-0 border-bottom py-2">نوع محصول: ${each.ProductType}</p>
                            <p class="m-0 py-2">انتخاب: <input type="checkbox" checked data-key="${each.ProductKey}" class="form-check-input"></p>
                        </div>
                </div>
                    `
            product_placeholder.innerHTML += temp
        } else {
            temp = `    
                    <div dir="rtl" class="col-lg-3 col-md-4 col-12 my-2">
                            <div class="border shadow-sm p-2">
                                <p class="m-0 border-bottom py-2">نام محصول: ${each.ProductName} </p>
                                <p class="m-0 border-bottom py-2">پارت نامبر: ${each.ProductPartNumber} </p>
                                <p class="m-0 border-bottom py-2">شماره انبار: ${each.ProductStoreId}</p>
                                <p class="m-0 border-bottom py-2">کارخانه سازنده: ${each.ProductManufacture}</p>
                                <p class="m-0 border-bottom py-2">نوع محصول: ${each.ProductType}</p>
                                <p class="m-0 py-2">انتخاب: <input type="checkbox"  data-key="${each.ProductKey}" class="form-check-input"></p>
                            </div>
                    </div>
                    `
            product_placeholder.innerHTML += temp
        }
    })
    add_tracker_input_product()
}


let modal_store = document.querySelector("#search-in-store-db")
modal_store.addEventListener("shown.bs.modal", async (e) => {
    let data = await bring_store_product(page = page)
    put_data_in_modal(data.data)
    page = data.current_page
    setup_pagination(data.pagination)
})
modal_store.addEventListener("hidden.bs.modal", (e) => {
    update_table_product_show()
    counter_product_tracker()
})


function counter_product_tracker() {
    let inputs = document.querySelectorAll("input[type='number']")
    inputs.forEach((each) => {
        each.addEventListener("keyup", (e) => {

            let key = e.currentTarget.dataset.key
            if (e.currentTarget.value < 0) {
                e.currentTarget.value = 1
            }
            selected.forEach((product) => {
                let obj = JSON.parse(product)
                if (obj.ProductKey == key) {
                    counter_selected_product[product] = e.currentTarget.value
                }
            })
        })

    })
}


function update_table_product_show() {
    let table = document.querySelector("#table-product-show")
    table.innerHTML = ""

    selected.forEach((each) => {
        let obj = JSON.parse(each)
        let count = 0;
        if (each in counter_selected_product) {
            count = counter_selected_product[each]
        } else {
            counter_selected_product[each] = 1
            count = 1
        }
        let temp = `
            <tr>
                <td>${obj.ProductName}</td>
                <td><input type="number" data-key="${obj.ProductKey}" value="${count}"></td>
            </tr>
        `
        table.innerHTML += temp
    })
}


function setup_pagination(pagination) {
    let pagination_container = document.querySelector("#pagination_container");
    pagination_container.innerHTML = "";

    Array.from(pagination).forEach((page_link) => {
        if (page_link == page) {
            temp = `<li className="page-item"><span class="page-link active  mouse-hover" onclick="next_page(${page_link});">${page_link}</span></li>`
            pagination_container.innerHTML += temp;
        } else {
            temp = `<li className="page-item"><span class="page-link mouse-hover" onclick="next_page(${page_link});">${page_link}</span></li>`
            pagination_container.innerHTML += temp;
        }
    })

}

function add_tracker_input_product() {
    let inputs = document.querySelectorAll("input[type='checkbox']")
    inputs.forEach((e) => {
        e.addEventListener("click", async (each) => {
            let server_db = await verify_product(each.currentTarget.dataset.key)

            // if admin un select product delete it from set
            if (!each.target.checked) {
                if (server_db) {
                    if (selected.has(JSON.stringify(server_db))) {
                        selected.delete(JSON.stringify(server_db))
                        each.target.checked = false;
                        return;
                    }
                }
            }


            if (!server_db) {
                alert("خطایی رخ داد")
                each.target.checked = false;
            } else {
                selected.add(JSON.stringify(server_db))
            }
        })
    })
}


async function next_page(p) {
    page = p
    let data = await bring_store_product(p)
    loading_animation(1500)
    page = data.current_page
    put_data_in_modal(data.data)
    setup_pagination(data.pagination)
}


function loading_animation(t) {
    let loader = document.querySelector(".loader")

    if (loader.classList.contains("d-none")) {
        loader.classList.remove("d-none")
    }
    if (!loader.classList.contains("show")) {
        loader.classList.add("show")
    }

    window.setTimeout((e) => {
        loader.classList.remove("show")
        loader.classList.add("d-none")

    }, t)
}


async function verify_product(key) {
    let headers = {
        "X-CSRFToken": document.querySelector("#csrf_token").value
    }
    let response = await fetch(`/store/verify/product/${key}`, {
        method: "GET",
        headers: headers,
    })
    if (response.status != 200) {
        return null
    } else {
        let data = await response.json()
        return data
    }
}

let form_project = document.querySelector("#form-project")
let ProjectProducts = document.querySelector("#ProjectProducts")
form_project.addEventListener("submit", (e) => {
    e.preventDefault()
    data = {}
    for (let temp of selected) {
        let obj = JSON.parse(temp)
        data[obj.ProductKey.toString()] = counter_selected_product[temp]
    }
    ProjectProducts.value = JSON.stringify(data)
    form_project.submit()
})