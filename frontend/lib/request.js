var backend_url = "http://localhost:8081/api/"
var media_url = backend_url + "media/"

function send_http_request(method, endpoint){
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest()

		if (method === "GET")
			xhr.open("GET", backend_url + endpoint, true)
		else
			xhr.open("POST", backend_url + endpoint)
		xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
		xhr.onreadystatechange = function() {
			if (this.readyState === XMLHttpRequest.DONE)
					resolve(this)
		}
		xhr.onerror = function() {
			reject(this)
		}
		xhr.send()
	});
}

export { send_http_request, backend_url, media_url }
