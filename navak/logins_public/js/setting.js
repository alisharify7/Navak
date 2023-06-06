async function bring_user_data() {
    // this function bring user data
    let response = await fetch("/setting/_user/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("#csrf_token").value
        }
    })
    if (response.status == 200) {
        let data = await response.json()
        return data
    } else {
        return false
    }

}

async function put_user_info() {
    let user_data = await bring_user_data()
    if (user_data) {
        let user_tag = document.querySelector("#user_tag")
        let user_group = document.querySelector("#group-user")
        let username = document.querySelector("#username-user")
        user_tag.textContent = "@" + user_data.data.user_tag
        username.textContent = user_data.data.username
        user_group.textContent = user_data.data.group
    } else {

        const Toast = Swal.mixin({
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 3000,
          timerProgressBar: true,
          didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
          }
        })

        Toast.fire({
          icon: 'error',
          title: 'خطایی رخ داد'
        })

    }
}

put_user_info()


const user_tag_reg = /^[\w_]{4,128}$/
let user_tag_input = document.querySelector("#user-tag");
user_tag_input.addEventListener("keyup", (e) => {
    let value = e.target.value
    if (user_tag_reg.test(value)) {
        user_tag_input.classList.add("is-valid")
        user_tag_input.classList.remove("is-invalid")
    } else {
        user_tag_input.classList.remove("is-valid")
        user_tag_input.classList.add("is-invalid")

    }
})
let user_change_tag_form = document.querySelector("#change-user-tag-form");
user_change_tag_form.addEventListener("submit", (e) => {
    e.preventDefault()
    if (user_tag_reg.test(user_tag_input.value)) {
        user_change_tag_form.submit();
    } else {
        window.alert("مقدار شناسه کاربری به درستی وارد نشده است")
    }
})