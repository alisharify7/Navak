


async function verify_product_partnumber(partnumber){
    // this function take a product partnumber and verify its valid partnumber ot not

    let body = new FormData()
    body.append("partnumber", partnumber)

    let response = await fetch("/store/_verify/product/partnumber/", {
        method:"POST",
        headers:{
            "X-CSRFToken": document.querySelector("#csrf_token").value
        },
        body:body,
    })

    if (response.status == 200){
        let data = await response.json()
        return data
    }else{
        return false
    }
}

let products_table_container = document.querySelector("#products-container")
function add_to_row(){

    let tr = document.createElement("tr")
    let td1 = document.createElement("td")
    let td2 = document.createElement("td")
    let td3 = document.createElement("td")
    let td4 = document.createElement("td")
    let input1 = document.createElement("input")
    let input2 = document.createElement("input")

    input1.setAttribute("type", "text")
    input1.setAttribute("class", "form-control partnumber")
    input1.setAttribute("placeholder", "پارت نامبر")
    td1.appendChild(input1)

    td2.textContent = "-"

    input2.setAttribute("type", "number")
    input2.setAttribute("class", "form-control partnumber-values")
    input2.setAttribute("value", "0")
    input2.setAttribute("placeholder", "تعداد خروج")

    td3.appendChild(input2)


    td4.innerHTML = `<i class="bi bi-x-circle text-danger fs-5 delete-btn fw-bold cursor-pointer"></i>`

    tr.appendChild(td1)
    tr.appendChild(td2)
    tr.appendChild(td3)
    tr.appendChild(td4)

    products_table_container.appendChild(tr)
}


let add_new_row_btn = document.querySelector("#add-new-row")
add_new_row_btn.addEventListener("click", (e)=>{
    add_to_row();
    track_inputs_partnumber();
})



function track_inputs_partnumber(){
    let inputs = document.querySelectorAll("input.partnumber")

    inputs.forEach((each)=>{
        each.addEventListener("keyup", async(e)=>{
            if(e.currentTarget.value){
                let response = await verify_product_partnumber(e.currentTarget.value)
                if(response){
                    let productName = response.ProductName
                    let productKey = response.ProductKey
                    let product_exit_qty = e.target.parentElement.parentElement.children[2].children[0]
                    let product_name_field = e.target.parentElement.parentElement.children[1]
                    product_exit_qty.setAttribute("data-product-key", productKey)
                    product_name_field.textContent = productName
                    e.target.classList.add("is-valid")
                    e.target.classList.remove("is-invalid")
                }
                else{
                    e.target.classList.add("is-invalid")
                    e.target.classList.remove("is-valid")
                    let product_exit_qty = e.target.parentElement.parentElement.children[2].children[0]
                    let product_name_field = e.target.parentElement.parentElement.children[1]
                    product_exit_qty.setAttribute("data-product-key","")
                    product_name_field.textContent = "-"
                }
            }
            else{
                e.target.classList.remove("is-valid")
                e.target.classList.remove("is-invalid")
            }
        })
    })

    let delete_btns = document.querySelectorAll(".delete-btn")
    delete_btns.forEach((each)=>{
        each.addEventListener("click", (e)=>{
             // when store staff click on delete btn delete row
            e.currentTarget.parentElement.parentElement.remove()
        })
    })


    let input_values = document.querySelectorAll("input.partnumber-values")
    input_values.forEach((each)=>{
        each.addEventListener("keyup", (e)=>{
            if(e.currentTarget.value <0){
                e.currentTarget.value = 0;
            }
        })
    })

}


let FormExitProductPerson = document.querySelector("#FormExitProductPerson")
FormExitProductPerson.addEventListener("submit", (e)=>{
    let inputs = document.querySelectorAll("input.partnumber-values")
    data = {}
    inputs.forEach((each)=>{
        let key = each.dataset.productKey
        let value = each.value
        if (!key || !value){
            Swal.fire(
                {
                    icon:"warning",
                    text:"برخی موارد مقدار دهی نشده است"
                }
            )
            e.preventDefault()
            return null;
        }
        if(key in data){
            let keyvalue = parseInt(data[key])
            data[key] = (parseInt(value) + keyvalue).toString()

        }else{

            data[key] = value
        }
    })

    let inputform= document.querySelector("#productsPerson")
    inputform.value = JSON.stringify(data)
    if (inputform.value.length <= 2){
           Swal.fire(
                {
                    icon:"warning",
                    text:"محصولی برای خروجی انتخاب نشده است"
                }
            )
        e.preventDefault()
        return null;
    }
})
