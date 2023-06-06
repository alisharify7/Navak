// set date in header
let date_now = new Date()
let dt = gregorian_to_jalali(date_now.getFullYear(), date_now.getMonth() + 1, date_now.getDate())
let day = String(dt[2]).length >= 2 ? dt[2] : "0" + String(dt[2])
let month = String(dt[1]).length >= 2 ? dt[1] : "0" + String(dt[1])
document.querySelector(".persian-date-now").textContent = `${String(dt[0])}-${String(month)}-${String(day)}`


// set time in header
window.setInterval(
    (e) => {
        let time_now = new Date()
        let time = `${time_now.getHours()}:${time_now.getMinutes()}:${time_now.getSeconds()} `
        document.querySelector(".persian-time-now").textContent = time
    }, 1000
)


// side menu navbar


let btn_close_menu = document.querySelector('.btn-close-menu')
// side bar menu
btn_close_menu.addEventListener("click", (e) => {
    btn_close_menu.classList.toggle("closed")
    if (btn_close_menu.children[0].className == "bi bi-arrow-right") {
        btn_close_menu.children[0].className = "bi bi-arrow-left"
    } else {
        btn_close_menu.children[0].className = "bi bi-arrow-right"
    }
    document.querySelector(".menu-container").classList.toggle("close")
    // document.querySelector(".menu-bottons-aside").classList.add("d-none")
    document.querySelectorAll(".hidden-btn-menu").forEach(each => {
        each.classList.toggle("d-none")
    })
    document.querySelector(".navak-menu-icon").classList.toggle("d-none")
    document.querySelector(".navak-aside-header-img").classList.toggle("d-none")
    document.querySelector(".left-column").classList.toggle("open")
    document.querySelector(".left-column").classList.toggle("col-md-8")
    document.querySelector(".left-column").classList.toggle("col-lg-10")
})


// in mobile size aside nav menu closed automaticlly
window.addEventListener("DOMContentLoaded", (e) => {

    window.addEventListener("resize", (e) => {
        if (window.innerWidth <= 1163) {
            if (!document.querySelector(".btn-close-menu").classList.contains("closed")) {
                document.querySelector(".btn-close-menu").click()
            }
        }
        if (window.innerWidth >= 1163) {
            // if size is ok automaticlly open size navbar
            if (document.querySelector(".btn-close-menu").classList.contains("closed")) {
                document.querySelector(".btn-close-menu").click()
            }
        }
    })

    if (window.innerWidth <= 1163) {
        if (!document.querySelector(".btn-close-menu").classList.contains("closed")) {
            document.querySelector(".btn-close-menu").click()
        }
    }
    if (window.innerWidth >= 1163) {
// if size is ok automaticlly open size navbar
        if (document.querySelector(".btn-close-menu").classList.contains("closed")) {
            document.querySelector(".btn-close-menu").click()
        }
    }

})


// alert wia js
function show_alert(message, category) {
    let alert_container = document.querySelector("#alert-container-js");
    if (!alert_container) {
        return;
    }

    let alert_status = null;
    if (category == "success") {
        alert_status = "عملیات با موفقیت انجام شد"
    }
    if (category == "info") {
        alert_status = "توجه"
    }
    if (category == "danger") {
        alert_status = "خطایی رخ داد"
    }

    if (category == "warning") {
        alert_status = "هشدار توجه کنید"
    }

    let template_alert = `
<div style="z-index: 2000;" class="alert p-3 m-2 alert-dismissible show fade alert-${category} d-flex flex-column position-fixed top-0 end-0 m-3"
 style="max-width:300px !important ;">
    <div class="alert-heading d-flex justify-content-between align-items-center">
        <a role="button" class="btn btn-close" data-bs-dismiss="alert"></a>
        <p class="me-5">${alert_status}</p>
    </div>
    <hr class="m-0 p-0">
    <div class="alert-body text-end overflow-auto p-2 text-center" style="max-height: 120px !important;">
        <p class="text-break m-0">${message}</p>
    </div>
</div>
`
    alert_container.innerHTML = template_alert;
}


async function get_new_messages(){
    let response = fetch("/message/_get/new/messages/", {
        method:"POST",
        headers:{
            "X-CSRFToken":document.querySelector("#csrf_token").value
        }
    })
    return (await response).json()
}

async function show_unseen_messages(){
    let menus = document.querySelectorAll(".menu-bottons-aside a")
    let messages = await get_new_messages();

    menus.forEach((e)=>{
        if(messages.UnseenMessages == 0){
            return;
        }
        console.log(e.children[1])
        if(e.children[0].innerHTML.trim().includes("مکاتبات")){
            e.children[0].textContent = "مکاتبات" +"  +" + messages.UnseenMessages.toString()
        }
    })

}
show_unseen_messages()
setInterval(show_unseen_messages, 8000)