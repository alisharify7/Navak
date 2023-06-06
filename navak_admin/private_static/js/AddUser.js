let employee_form = document.querySelector("#add-new-employee-form")
let users_form = document.querySelector("#add-new-user-form")
let employee = document.querySelector("#employee")
let others = document.querySelector("#others")


employee.addEventListener("click", (e) => {
    if (!users_form.classList.contains("d-none")) {
        users_form.classList.add("d-none")
    }
    employee_form.classList.remove("d-none")
})

others.addEventListener("click", (e) => {
    if (!employee_form.classList.contains("d-none")) {
        employee_form.classList.add("d-none")
    }
    users_form.classList.remove("d-none")
})
