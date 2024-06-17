const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById("password");

function login() {
    data = {
        "name": usernameInput.value,
        "password": passwordInput.value,
    }
    
    fetch(
        "/api/auth/login",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }
    ).then((response) => {
        response.json().then((json) => {
            console.log(json);
            if (json["detail"] == "Logged in"){
                localStorage.setItem("token", json["token"]);
                window.location = "/home";
            }else{
                document.getElementById("failed").innerHTML = `<span style="color: red;">ログインできませんでした: ${json["detail"]}</span>`;
                console.log(json);
            }
        });
    });
}
