<template>
    <div>
        <div class="row">
            <div class="leftcolumn" style="width: 75%;">
                <div class="card">
                    <h2>Les parcelles</h2>
                </div>
            </div>
            <div class="rightcolumn" style="width: 25%;">
                <div class="card">
                    <h2>Rappels</h2>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import { sendHttpRequest } from '../lib/request'

export default {
    name: "home",
    mounted() {
        sendHttpRequest("GET", "parcelles").then((response) => {
            //let data = JSON.parse(response.response)
            console.log("success")
            console.log(response)
        }).catch((error) => {
            console.log("error")
            console.log(error)
        })
    }
}
</script>