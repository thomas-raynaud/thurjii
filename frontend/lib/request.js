const BACKEND_URL = "http://localhost:8081/api/"
const MEDIA_URL = BACKEND_URL + "media/"

const send_http_request = (method, endpoint, data={}) => {
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest()
		let data_rq = ""
		let keys = Object.keys(data)
		for (let key of keys) {
			data_rq += key + "=" + data[key] + "&"
		}
		xhr.open(method, BACKEND_URL + endpoint + "/", true)
		xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
		xhr.onreadystatechange = () => {
			if (xhr.readyState === XMLHttpRequest.DONE)
				resolve(xhr)
		}
		xhr.onerror = () => {
			reject(xhr)
		}
		xhr.send(data_rq)
	})
}

export { send_http_request, MEDIA_URL }