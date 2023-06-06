let btns = document.querySelectorAll("button.vacation")
btns.forEach((each)=>{
    each.addEventListener("click", async(e)=>{
        let Opration = e.currentTarget.dataset.opration;
        let vacationKey = e.currentTarget.dataset.vacationKey;
        let response =  await set_vacation_status(Opration, vacationKey);
        if (!response){
            return;
        }
        else if (response.status == "success"){
            Swal.fire(
            {
                title:"عملیات موفقیت آمیز بود",
                text:response.message,
                icon:"success"
            }).then(
                (e)=>{
                    if(e.isConfirmed){
                        window.setTimeout((e)=>{window.location.reload()}, 1000)
                    }
                }
            )
        }
        else
        {
            Swal.fire(
            {
                title:"عملیات موفقیت آمیز نبود",
                text:response.message,
                icon:"warning"
            }).then(
                (e)=>{
                    if(e.isConfirmed){
                        window.setTimeout((e)=>{window.location.reload()}, 1000)
                    }
                }
            )
        }

    })
})



async function set_vacation_status(op, key){
    let body = new FormData()
    if(!key){
        Swal.fire(
            {
                title:"عملیات ناموفقیت آمیز بود",
                text:"برخی موارد مقدار دهی نشده است",
                icon:"warning"
            }).then(
                (e)=>{
                    if(e.isConfirmed){
                        window.setTimeout((e)=>{window.location.reload()}, 1000)
                    }
                }
            )
        return null;
    }
    if(!op){
        Swal.fire(
            {
                title:"عملیات ناموفقیت آمیز بود",
                text:"برخی موارد مقدار دهی نشده است",
                icon:"warning"
            }).then(
                (e)=>{
                    if(e.isConfirmed){
                        window.setTimeout((e)=>{window.location.reload()}, 1000)
                    }
                }
            )
        return null;
    }

    body.append("opration", op);
    body.append("key", key);
    let response = await fetch("/engineer/set/vacation/", {
        method:"POST",
        headers: {
            "X-CSRFToken": document.querySelector("#csrf_token").value
        },
        body:body
    })

    let data = (await response).json();
    return data;
}