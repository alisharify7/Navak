async function get_user_work_report(){
    let response = await fetch("/employee/_get/report/work/30/", {
        method:"POST",
        headers:{
            "X-CSRFToken": document.querySelector("#csrf_token").value
        }
    });
    let data = await response.json();
    return data;
}


function get_tr_listiner(){
    let td = document.querySelectorAll("td.data-tr")
    td.forEach((each)=>{
        each.addEventListener("click", (e)=>{
            let status = e.currentTarget.dataset.status;
            let short = e.currentTarget.dataset.shortText;
            let large = e.currentTarget.dataset.largeText;
            if(status === "short")
            {
                each.textContent = large;
                e.currentTarget.dataset.status = "large";
            }
            else{
                each.textContent = short;
                e.currentTarget.dataset.status = "short";
            }

        })
    })
}

async function setup(){
    let data = await get_user_work_report()
    set_up_chart(data)
    get_tr_listiner()

}


function set_up_chart(data){

let chart = document.querySelector("#my-month-report");
          new Chart(chart, {
            type: 'bar',
            data: {
                labels:data.dates
                ,
                datasets: [{
                label: 'گزارش وضعیت',
                data:data.datas,
                backgroundColor: [
                    'rgba(255, 99, 70,0.5)',
                    'rgba(54, 162, 50,0.5)',
                    'rgba(255, 205, 15,0.5)',
                    'rgba(55, 98, 98,0.5)',
                    'rgba(255, 55, 15,0.5)',
                    'rgba(15, 64, 80,0.5)',
                    'rgba(68, 80, 255,0.5)',
                ],
                hoverOffset: 15
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
}



setup()