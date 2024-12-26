<template>
    <div id="app">
        <div class="topnav">
            <router-link to="/">
                <div id="home-topnav">
                    <img src="./images/icon_white.ico" width="18px">
                    <p>Home</p>
                </div>
            </router-link>
            <router-link to="/map">
                <div id="map-topnav">
                    <p>Carte</p>
                </div>
            </router-link>
            <router-link to="/about">
                <div id="about-topnav">
                    <p>A propos</p>
                </div>
            </router-link>
        </div>
        <router-view />
    </div>
</template>