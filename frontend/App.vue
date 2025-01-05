<template>
    <div id="app">
        <div class="topnav">
            <router-link to="/">
                <div>
                    <img src="./images/icon_white.ico" width="18px">
                    <p>Home</p>
                </div>
            </router-link>
            <router-link to="/map-sandbox">
                <div>
                    <p>Carte</p>
                </div>
            </router-link>
            <router-link to="/about">
                <div>
                    <p>A propos</p>
                </div>
            </router-link>
        </div>
        <router-view />
    </div>
</template>