menuitems = document.getElementsByClassName('navbar-nav')[0].getElementsByTagName('a')
for (var i = 0; menuitems.length > i; i++) {
    if (window.location.href == menuitems[i]) {
        menuitems[0].classList.add('active')
    }
}

function showalert(message, category, id = 'alertmsg') {
    var alertmsg = document.getElementById(id)
    if (category == 'success') {
        alertmsg.innerHTML = `<div class="alert alert-success fade show alert-dismissible d-flex align-items-center" role="alert">
          <svg aria-label="Success:" class="bi flex-shrink-0 me-2" height="24" role="img" width="24">
            <use xlink:href="#check-circle-fill">
            </use>
          </svg>
          <div>
            ${message}
            <button aria-label="Close" class="btn-close" data-bs-dismiss="alert" type="button">
            </button>
          </div>
        </div>`
    } else if (category == 'warning') {
        alertmsg.innerHTML = `<div class="alert alert-warning fade show alert-dismissible d-flex align-items-center" role="alert">
          <svg aria-label="Warning:" class="bi flex-shrink-0 me-2" height="24" role="img" width="24">
            <use xlink:href="#exclamation-triangle-fill">
            </use>
          </svg>
          <div>
            ${message}
            <button aria-label="Close" class="btn-close" data-bs-dismiss="alert" type="button">
            </button>
          </div>
        </div>`
    } else if (category == 'error') {
        alertmsg.innerHTML = `<div class="alert alert-danger fade show alert-dismissible d-flex align-items-center" role="alert">
          <svg aria-label="Danger:" class="bi flex-shrink-0 me-2" height="24" role="img" width="24">
            <use xlink:href="#exclamation-triangle-fill">
            </use>
          </svg>
          <div>
            ${message}
            <button aria-label="Close" class="btn-close" data-bs-dismiss="alert" type="button">
            </button>
          </div>
        </div>`
    }
}

function submitworkfunc() {
    document.getElementById('submitwork').addEventListener('click', () => {
        inputurl = document.getElementById('inputurl').value
        inputamount = document.getElementById('inputamount').value
        if (inputurl == '') {
            showalert('Please enter a valid url', 'warning')
            return
        } else if (inputamount == '') {
            showalert('Please enter a valid amount', 'warning')
            return
        }
        var submitbtn = document.getElementById('submitwork')
        submitbtn.setAttribute('disabled', 'true')
        var host = window.location.protocol + "//" + window.location.host;
        var url = host + "/add";
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                var status = xhr.status
                var text = JSON.parse(xhr.responseText)
                if (status == 200) {
                    if (text['success'] == true) {
                        submitbtn.removeAttribute('disabled')
                        showalert(text['message'], text['category'])
                        setTimeout(() => {
                            window.location.href = host + `/work?id=${text['id']}`
                        }, 1000)
                    } else {
                        submitbtn.removeAttribute('disabled')
                        showalert(text['message'], text['category'])
                    }
                } else {
                    submitbtn.removeAttribute('disabled')
                    showalert('Something went wrong! Please try again later', 'error')
                }
            }
        };
        var data = `url=${encodeURIComponent(inputurl)}&amount=${encodeURIComponent(inputamount)}`;
        xhr.send(data);
    })
}

function updateworkinfo(threadid, interval = null) {
    var host = window.location.protocol + "//" + window.location.host;
    var url = host + `/getwork`;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var status = xhr.status
            if (status == 200) {
                var text = JSON.parse(xhr.responseText)
                if (text['running'] == false) {
                    if (interval != null) {
                        $('#threadprogress').removeClass('progress-bar-striped')
                        clearInterval(interval)
                    }
                }
                if (text['running'] == false) {
                    text['running'] = 'no'
                }
                if (text['running'] == true) {
                    text['running'] = 'yes'
                }
                if (text['done'] == false) {
                    text['done'] = 'no'
                }
                if (text['done'] == true) {
                    text['done'] = 'yes'
                }
                $('#idno').text(text['id'])
                $('#views').text(text['views'])
                $('#percent').text(text['percent'] + '%')
                $('#isrunning').text(text['running'])
                $('#isdone').text(text['done'])
                $('#amount').text(text['amount'])
                $('#threadprogress').css('width', `${text['percent']}%`)
                $('#threadprogress').text(`${text['percent']}%`)
            }
        }
    };
    var data = `id=${threadid}`
    xhr.send(data);
}
