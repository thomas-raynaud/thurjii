const BACKEND_URL = "http://localhost:8081/api/"
const MEDIA_URL = BACKEND_URL + "media/"

const send_api = (method, endpoint, data={}) => {
	return new Promise((resolve, reject) => {
		let xhr = new XMLHttpRequest()
		let data_rq = JSON.stringify(data)
		xhr.open(method, BACKEND_URL + endpoint + "/", true)
		xhr.setRequestHeader("Content-Type", "application/json")
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

export { send_api, MEDIA_URL }