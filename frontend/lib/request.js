var mainUrl = "http://localhost:8081/api/"

function sendHttpRequest(typeOfRequest, endpoint){
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest();

		if (typeOfRequest === "GET")
			xhr.open("GET", mainUrl + endpoint, true)
		else
			xhr.open("POST", mainUrl + endpoint)
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

export { sendHttpRequest }
