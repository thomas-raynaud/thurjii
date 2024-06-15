<template>
    <div id="app">
        <div class="header">
            <h1>Thurjii</h1>
            <p>Gestion du travail dans les vignes</p>
        </div>
        <div class="topnav">
            <router-link to="/">
                <div id="home-topnav">
                    <p>Home</p>
                </div>
            </router-link>
            <router-link to="/planning">
                <div id="planning-topnav">
                    <p>Planning</p>
                </div>
            </router-link>
        </div>
        <router-view />
    </div>
</template>