let userToken = "";
let isLoggedIn = false;
let userdata = {};

document.addEventListener("DOMContentLoaded", () => {
    userToken = localStorage.getItem("token");

    if (userToken !== null){
        isLoggedIn = true;

        document.getElementById("account-name").innerHTML = "";
        document.getElementById("account-display-name").innerHTML = "";
        document.getElementById("me-icon").src = "";
    
        fetch(
            "/api/users/me",
            {
                method: "get",
                headers: {
                    "Authorization": userToken
                }
            }
        ).then((response) => {
            response.json().then((json) => {
                userdata = json;
                console.log("userdata fetched", userdata);
                reloadMeDetail();
            });
        });
    }else{
        isLoggedIn = false;
    }

    consoleWarning();
});

function reloadMeDetail() {
    username = userdata['name'];
    if (userdata['display_name'] == null){
        displayName = username;
    }else{
        displayName = userdata['display_name'];
    }
    if (userdata['icon_url'] == null){
        displayAvatar = "/static/default_icon.png";
    }else{
        displayAvatar = userdata['icon_url'];
    }

    document.getElementById("account-name").innerHTML = `@${username}`;
    document.getElementById("account-display-name").innerHTML = `${displayName}`;
    document.getElementById("me-icon").src = displayAvatar;
}

function consoleWarning() {
    console.log(
        "%cちょっと待ってくれ！",
        "font-size: 400%; color: red;"
    )
    
    console.log(
        "%cここに%c”変な文字列”%cを書くと、あなたのアカウントが乗っ取られてしまうかもしれません...",
        "font-size: 200%; color: red;",
        "font-size: 240%; color: orange;",
        "font-size: 200%; color: red;"
    )
    
    console.log(
        "%c試しに「console.log(userToken)」と書いてEnterを押してみてください。あなたのトークンが表示されます",
        "font-size: 1%; display: hidden;",
    )
    
    console.log(
        "%cもしあなたがシステムエンジニアあるいはその類の猫で、Nyantterに貢献したいなら、こちらへプルリクエストをどうぞ...！ → https://github.com/nennneko5787/Nyantter",
        "font-size: 200%; color: yellow;",
    )
    
    console.log(
        "え？console.log()で色をつけられるのかって？ → https://dev.classmethod.jp/articles/console-log-css/"
    )
}
