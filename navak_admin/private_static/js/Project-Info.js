let btn_open_modal_status = document.querySelector("#open_modal_status")
btn_open_modal_status.addEventListener("click", async (e) => {
    let key = e.currentTarget.dataset.pjk
    let data = await get_project_status_comment(key)
    put_data_in_modal(data.data)
})


async function get_project_status_comment(project_key) {
    let BodyRequest = new FormData();
    BodyRequest.append("ProjectKey", project_key)
    let response = await fetch("/admin/_project/comments/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("#csrf_token").value
        },
        body: BodyRequest,
    })
    if (response.status == 200) {
        let data = await response.json();
        return data;
    } else {
        return null;
    }
}


function put_data_in_modal(data) {
    let comment_container = document.querySelector("#comment_container")
    comment_container.innerHTML = "";
    for (let comment of data) {
        let temp = `
            <div class="alert alert-primary d-flex flex-column justify-content-center align-items-center">
                    <div class="w-100 pb-2" style="word-break: break-all">
                        ${comment.Comment}
                    </div>
                    <div class="w-100 d-flex justify-content-between align-items-center pt-2" style="border-top: #ccc 1px solid"> 
                        <p class="m-0">${comment.EngineerName}</p>
                        <p class="m-0">${comment.Time}</p>
                    </div>
            </div>
        `;
        comment_container.innerHTML += temp;
    }
}
