async function setup() {
    //set up function for bring data from server and put in table

    // pars page number in url
    const urlParams = new URLSearchParams(window.location.search);
    let page = urlParams.get('page');

    if (!page) {
        page = 1;
    } else {
        if (parseInt(page) == "NaN") {
            page = 1;
        } else {
            page = parseInt(page)
        }
    }

    let data = await get_messages(page)
    if (data.data) {
        await replace_table_data(data)
        setup_pagination(data.pagination, page, data.total_pagination)
        add_links_tr()
    }
}

function add_links_tr() {
    // this function handle when user click on a row
    // redirect user to message page
    let trs = document.querySelectorAll("tr");
    trs.forEach((e) => {
        e.addEventListener("click", (element) => {

            window.location.href = "/message/show/" + (element.currentTarget.dataset.mailKey);
        })
        e.addEventListener("mouseover", e => {
            e.target.style.cursor = "pointer";
        })
    })
}

function setup_pagination(data, page, total_pagination) {
    // this function handle pagination of messages
    let pagination_link = document.querySelector("#pagination-link");
    pagination_link.innerHTML = "";
    let pagination_container = document.querySelector("#pagination-container");


    if (page - 1 > 0) {
        pagination_link.innerHTML += `<li class="page-item">
              <a class="page-link" href="${window.location.pathname + "?page=" + (page - 1).toString()}" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
              </a>
        </li> `
    }

    data.forEach((link) => {
        if (link == page) {
            pagination_link.innerHTML += `
                <li class="page-item"><a class="page-link active" href="${window.location.pathname + "?page=" + link.toString()}">${link}</a></li>`
        } else {
            pagination_link.innerHTML += `
                <li class="page-item"><a class="page-link" href="${window.location.pathname + "?page=" + link.toString()}">${link}</a></li>
            `
        }
    })

    if (page + 1 < total_pagination) {
        pagination_link.innerHTML += `<li class="page-item">
              <a class="page-link" href="${window.location.pathname + "?page=" + (page + 1).toString()}" aria-label="Previous">
                <span aria-hidden="true">&raquo;</span>
              </a>
        </li> `
    }

}



async function get_messages(page) {
    // this function send a json request to server for getting messages
    let body = {
        page: page
    }
    let header = {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("#csrf_token").value
    }
    let response = await fetch("/message/", {
        method: "POST",
        body: JSON.stringify(body),
        headers: header,
    });

    if (response.status == 200) {
        let data = await response.json();
        return data
    } else {
        return null
    }
}


async function replace_table_data(data) {
    // data = messages from server
    // this function get a data and put data in data
    let message_table_body = document.querySelector("#message-table-body");
    message_table_body.innerHTML = "";

    Array.from(data.data).forEach((element) => {
        let tr = document.createElement("tr");
        let title = document.createElement("td");
        let time = document.createElement("td");
        let from = document.createElement("td");
        let to = document.createElement("td");
        let attach = document.createElement("td");
        tr.setAttribute("data-mail-key", element.MailKey)
        title.textContent = (!element.IsWatched ? "*  " : "") + element.MailTitle
        from.textContent = element.From
        to.textContent = element.To
        attach.textContent = element.MailTime == 0 ? "دارد" : "دارد"
        time.textContent = element.MailTime
        tr.appendChild(title)
        tr.appendChild(from)
        tr.appendChild(to)
        tr.appendChild(attach)
        tr.appendChild(time)
        message_table_body.appendChild(tr)
    })

}

setup()
