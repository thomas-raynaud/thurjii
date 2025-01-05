const BACKEND_URL = "http://localhost:8081/api/"
const MEDIA_URL = BACKEND_URL + "media/"

const send_http_request = (method, endpoint) => {
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest()
		if (method === "GET")
			xhr.open("GET", BACKEND_URL + endpoint, true)
		else
			xhr.open("POST", BACKEND_URL + endpoint)
		xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
		xhr.onreadystatechange = () => {
			if (xhr.readyState === XMLHttpRequest.DONE)
				resolve(xhr)
		}
		xhr.onerror = () => {
			reject(xhr)
		}
		xhr.send()
	})
}

export { send_http_request, MEDIA_URL }
