var main_url = "http://localhost:8081/api/"

function send_http_request(method, endpoint){
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest()

		if (method === "GET")
			xhr.open("GET", main_url + endpoint, true)
		else
			xhr.open("POST", main_url + endpoint)
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

export { send_http_request }
