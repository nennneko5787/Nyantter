let turnstileToken = "";

const usernameInput = document.getElementById('username');
let typingTimer; // タイピングのタイマー
const doneTypingInterval = 500; // 500ミリ秒（0.5秒）入力が止まったら判定を行う

usernameInput.addEventListener('input', function() {
    clearTimeout(typingTimer); // 入力が行われるたびに前回のタイマーをクリア

    typingTimer = setTimeout(() => {
        let usernameinvalid = document.getElementById('usernameinvalid');

        if ((this.value.length < 1) || (this.value.length > 14)) {
            usernameInput.setCustomValidity('ユーザー名は1文字以上14文字以下である必要があります');
            usernameinvalid.innerHTML = '<span style="color: red;">ユーザー名は1文字以上14文字以下である必要があります</span>';
            return;
        } else if (hasNonAllowedCharacters(this.value)) {
            usernameInput.setCustomValidity('ユーザー名には[a-zA-Z0-9_.-]以外を使用することはできません');
            usernameinvalid.innerHTML = '<span style="color: red;">ユーザー名には[a-zA-Z0-9_.-]以外を使用することはできません</span>';
            return;
        }

        usernameinvalid.innerHTML = "Now loading...";

        try {
            fetch(`/api/users/@${this.value}`).then(response => {
                response.json().then(userdata => {
                    if (userdata["detail"] !== "failed") {
                        usernameInput.setCustomValidity('そのユーザー名はすでに使用されています');
                        usernameinvalid.innerHTML = '<span style="color: red;">そのユーザー名はすでに使用されています</span>';
                    } else {
                        usernameInput.setCustomValidity('');
                        usernameinvalid.innerHTML = '<span style="color: green;">そのユーザー名は使用可能です！おめでとうございます🎉</span>';
                    }
                });
            });
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    }, doneTypingInterval);
});

const passwordInput = document.getElementById("password");
const passwordConfirmInput = document.getElementById("password_confirm");

function hasNonAllowedCharacters(input) {
    // 許可する文字の正規表現（英数字と._-）
    let allowedRegex = /^[a-zA-Z0-9_.-]*$/;
    
    // inputに許可されていない文字が含まれているか確認
    return !allowedRegex.test(input);
}

function javascriptCallback(token) {
    turnstileToken = token;
    console.log(turnstileToken);
    document.getElementById("q.e.d").innerHTML = '<span style="color: green;">人間としての証明完了 Q.E.D</span>';
    document.getElementById("registerButton").disabled = false;
}

window.addEventListener("message", function (e) {
    if (e.data.event !== 'init') {
        if ((Object.keys(e.data).indexOf('token') !== -1) === true) {
            javascriptCallback(e.data.token);
        }
        return;
    }

    let turnstileIframe = document.getElementById('cf-chl-widget-' + e.data.widgetId);
    if (!turnstileIframe) {
        return;
    }

    turnstileIframe.style.width = "100%";
    turnstileIframe.style.paddingBottom = "10px";
    turnstileIframe.style.marginBottom = "10px";
    turnstileIframe.style.display = "";
    e.stopImmediatePropagation();
});

function register() {
    if (usernameInput.validity.valid != true) {
        return;
    }

    if (passwordInput.value != passwordConfirmInput.value) {
        passwordInput.setCustomValidity('パスワードが一致しません');
        passwordConfirmInput.setCustomValidity('パスワードが一致しません');
        document.getElementById("password_confirm_invalid").innerHTML = '<span style="color: red;">パスワードが一致しません</span>';
    }else{
        passwordInput.setCustomValidity('');
        passwordConfirmInput.setCustomValidity('');
        document.getElementById("password_confirm_invalid").innerHTML = '';
    }

    if (document.getElementById("password").validity.valid != true) {
        return;
    }

    if (document.getElementById("password_confirm").validity.valid != true) {
        return;
    }

    if (turnstileToken == "") {
        document.getElementById("q.e.d").innerHTML = '<span style="color: red;">人間としての証明を完了させてください</span>';
        return;
    }

    data = {
        "name": usernameInput.value,
        "password": passwordInput.value,
        "password_confirm": passwordConfirmInput.value,
        "turnstile": turnstileToken,
    }
    
    fetch(
        "/api/auth/register",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }
    ).then((response) => {
        response.json().then((json) => {
            if (json["detail"] == "Registered"){
                localStorage.setItem("token", json["token"]);
                window.location = "/home";
            }else{
                document.getElementById("failed").innerHTML = `<span style="color: red;">登録できませんでした: ${json["detail"]}</span>`;
                console.log(json);
            }
        });
    });
}
