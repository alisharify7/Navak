async function get_projects_data(){
    // this function fetch data from server for chart's
    let response = await fetch("/admin/_get/projects/status/", {
        method:"GET",
        headers:{
            "X-CSRFToken": document.querySelector("#csrf_token").value
        }
    })

    if (response.status == 200) {
        let data = await response.json()
        return data
    }else{
        return null
    }
}


async function setup_charts(){
    let data = await get_projects_data()
    let project_type = data.ProjectType
    let project_status = data.ProjectStatus


    let chart = document.querySelector("#firstchart");
          new Chart(chart, {
            type: 'pie',
            data: {
                labels: [
                'تحقیقاتی',
                'تجاری',
                'نظامی',
                ],
                datasets: [{
                label: '',
                data: [project_type.research, project_type.commercial, project_type.military],
                backgroundColor: [
                    'rgb(255, 99, 70)',
                    'rgb(54, 162, 50)',
                    'rgb(255, 205, 15)',
                ],
                hoverOffset: 15
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });

      let secondchart = document.querySelector("#secondchart");
       new Chart(secondchart, {
            type: 'pie',
            data: {
                labels: [
                'در حال انجام',
                'متوقف شده',
                'اتمام یافته',
                ],
                datasets: [{
                label: '',
                data: [project_status.continued, project_status.stopped, project_status.ended],
                backgroundColor: [
                    'rgb(50, 150, 80)',
                    'rgb(34, 80, 195)',
                    'rgb(254, 20, 98)',
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

setup_charts()