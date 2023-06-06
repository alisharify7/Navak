const container_row = document.querySelector(".container_row")


async function status_of_now_traffic(){
    // this function get all employees that registered today
    let response = fetch("/gard/today/status/traffic/", {
        method:"POST",
        headers:{
            "X-CSRFToken": document.querySelector("#csrf_token").value
        }
    })
    return (await response).json()
}


async function get_all_employees(){
    //this function get all employee's for showing in table

    let response = await fetch("/gard/_get/employees/", {
        method:"POST",
        headers:{
            "X-CSRFToken":document.querySelector("#csrf_token").value
        },
    })

    if (response.status == 200)
    {
        let data = await  response.json()
        return data
    }
    else
    {
        Swal.fire({
            icon:"warning",
            text:"عملیات دریافت کارمندان ناموفق بود",
            title:"خطایی رخ داد"
        })
        return ;
    }
}



function put_employees(data, employees_status){
    // this function get list of all employees and status of today and
    // check if user have registered before mark their input

    let top = ""
    for(let each in data)
    {
        // loop over all employees
        let employees = "";
        for(let emp of data[each])
        {

            // loop over employees status
            // for finding this employee is register before or not
            let is_exited = false;
            let is_entered = false;
            for(let status of employees_status[each])
            {
                if(status.key == emp.key){
                    if(status.exit == 1){
                        is_exited = true;
                    }
                    if(status.enter == 1){
                        is_entered = true;
                    }
                }
            }

            employees += `
                <p class="m-0 my-2 p-2 border d-flex justify-content-between align-items-center">
                    <span>${emp.name.slice(0, 18)}</span>
                    <span class="ms-auto">
                    ورود    
                        <input ${is_entered? "checked"  : ""} data-employee_key="${emp.key}" class="form-check-input enter_input" type="checkbox"></input>
                    </span>
                    <span class="ms-3">
                    خروج  
                    <input ${is_exited? "checked"  : ""} data-employee_key="${emp.key}" class="form-check-input exit_input" type="checkbox"></input>
                    </span>
                </p>
                `
        }

        let temp = `
            <div class="col-lg-6 col-md-12 my-2">
            <div class="card shadow">
                <div class="card-header">
                    <p class="m-0 text-center">${each}</p>
                </div>
                <div class="card-body">
                    <p class="m-0 my-2">
                        <input type="text" dir="rtl" class="form-control" placeholder="جستجو ...">
                    </p>
                        <div class="employee_list overflow-auto">
                                ${employees}
                        </div>
                </div>
                <div class="card-footer"></div>
            </div>
        </div>
        `
        if (employees === ""){
            temp = `
             <div class="col-lg-6 col-md-12 my-2">
            <div class="card shadow">
                <div class="card-header">
                    <p class="m-0 text-center">${each}</p>
                </div>
                <div class="card-body">
                    <p class="m-0 my-2 text-center">
                        کارمندی یافت نشد
                    </p>
                        <div class="employee_list overflow-auto text-center">
                                ...
                        </div>
                </div>
                <div class="card-footer"></div>
            </div>
        </div>`
        container_row.innerHTML += temp;
        }
        else{
            top += temp
        }
    }

        // swap top employees to comes up for better ui
        const swap = container_row.innerHTML;
        container_row.innerHTML = "";
        container_row.innerHTML = top;
        container_row.innerHTML += swap;


}

function keep_on_search(all_inputs){
    // this function handle searching in employees name
        all_inputs.forEach((each)=>{
        each.addEventListener("keyup", e=>{
            const value = e.target.value
            all_ps = Array.from(e.target.parentElement.nextElementSibling.children)
            if (!value){
                all_ps.forEach((each)=>{
                    each.classList.remove("d-none")
                })
            }
            else{
                all_ps.forEach((each)=>{
                    if( !(each.children[0].textContent.startsWith(value)) ){
                        each.classList.add("d-none")
                    }else{
                        each.classList.remove("d-none")
                    }
                })
            }
        })
    })

}

async function register_traffic(key, status){
    let form = new FormData()
    form.append("key", key)
    form.append("status", status)
    let response = await fetch("/gard/register/employee/traffic/", {
        method:"POST",
        headers:{
            "X-CSRFToken":document.querySelector("#csrf_token").value
        },
        body:form
    })
    let data = await response.json()
    if (response.status == 200){
        if (data.status== "success"){
            const  Toast = Swal.mixin({
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
              icon: 'success',
              title: data.message
            })
        }
        else{
              const  Toast = Swal.mixin({
                  toast: true,
                  position: 'top-start',
                  showConfirmButton: false,
                  timer: 3000,
                  timerProgressBar: true,
                  didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                  }
                })

                Toast.fire({
                  icon: 'warning',
                  title: data.message
                })
                }
        }
    else{
        const  Toast = Swal.mixin({
          toast: true,
          position: 'top-start',
          showConfirmButton: false,
          timer: 3000,
          timerProgressBar: true,
          didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
          }
        })

        Toast.fire({
          icon: 'warning',
          title: data.message
        })

    }

}

async function exit_traffic(key, status){
    let form = new FormData()
    form.append("key", key)
    form.append("status", status)
    let response = await fetch("/gard/exit/employee/traffic/", {
        method:"POST",
        headers:{
            "X-CSRFToken":document.querySelector("#csrf_token").value
        },
        body:form
    })
    let data = await response.json()
    if (response.status == 200){
        if (data.status== "success"){
            const  Toast = Swal.mixin({
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
              icon: 'success',
              title: data.message
            })
        }
        else{
              const  Toast = Swal.mixin({
                  toast: true,
                  position: 'top-start',
                  showConfirmButton: false,
                  timer: 3000,
                  timerProgressBar: true,
                  didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                  }
                })

                Toast.fire({
                  icon: 'warning',
                  title: data.message
                })
                }
        }
    else{
        const  Toast = Swal.mixin({
          toast: true,
          position: 'top-start',
          showConfirmButton: false,
          timer: 3000,
          timerProgressBar: true,
          didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
          }
        })

        Toast.fire({
          icon: 'warning',
          title: data.message
        })

    }

}

function keep_register_traffic(){
    // this function handle register  for employees
    const all_inputs_check = document.querySelectorAll('.form-check-input.enter_input')
    all_inputs_check.forEach(each=>{
        each.addEventListener("click", e=>{
            const k = (e.currentTarget.dataset.employee_key)
            if(e.currentTarget.checked){
                register_traffic(key=k, status="ok")
            }else{
                register_traffic(key=k, status="cancel")

            }
        })
    })
}

async function keep_exit_traffic(){
  // this function handle exit for employees
    const all_inputs_check = document.querySelectorAll('.form-check-input.exit_input')
    all_inputs_check.forEach(each=>{
        each.addEventListener("click", e=>{
            const k = (e.currentTarget.dataset.employee_key)
            if(e.currentTarget.checked){
                exit_traffic(key=k, status="ok")
            }else{
                exit_traffic(key=k, status="cancel")

            }
        })
    })
}

async function setup(){
    const status_of_traffic = await status_of_now_traffic()

    let data = await get_all_employees()
    put_employees(data, status_of_traffic)

    const all_inputs = document.querySelectorAll("input[type='text']")
    keep_on_search(all_inputs)

    keep_register_traffic()
    keep_exit_traffic()
}

setup()