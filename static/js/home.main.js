let userToken = "";
let isLoggedIn = false;
let userdata = {};
let nowPage = 0;
let isLoading = true;

console.log(
    "%cNyantter %cby %cnennneko5787",
    "font-size: 400%; color: #ee82ee;",
    "font-size: 100%; color: #aaa;",
    "font-size: 200%; color: #7fffd4;"
);

document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById('navbar-profile').addEventListener('click', function() {
        document.getElementById('menu').classList.toggle('show');
    });

    userToken = localStorage.getItem("token");

    if (userToken !== null) {
        isLoggedIn = true;

        // Creating elements for the menu
        let menu = document.getElementById("menu");

        let profileElement = document.createElement("div");
        profileElement.className = "navbar-btn";
        profileElement.innerHTML = "プロフィール";
        profileElement.id = "profile-router";
        menu.appendChild(profileElement);

        let settingElement = document.createElement("div");
        settingElement.innerHTML = "設定";
        settingElement.className = "navbar-btn";
        settingElement.id = "setting-router";
        menu.appendChild(settingElement);

        menu.appendChild(document.createElement("hr"));

        let logoutElement = document.createElement("div");
        logoutElement.innerHTML = "ログアウト";
        logoutElement.className = "navbar-btn";
        logoutElement.onclick = async function () {
            let response = await fetch(
                "/api/auth/logout",
                {
                    method: "DELETE",
                    headers: {
                        "Authorization": userToken,
                    }
                }
            )

            localStorage.clear();
            window.location.href = "/";
            return;
        }
        menu.appendChild(logoutElement);

        // Fetch user data using async/await
        try {
            const response = await fetch("/api/users/me", {
                method: "get",
                headers: {
                    "Authorization": userToken
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const json = await response.json();
            userdata = json;
            console.log("userdata fetched", userdata);
            reloadMeDetail();
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    } else {
        isLoggedIn = false;

        document.getElementById("account-name").innerHTML = "書き込むためにはログインしてください";
        document.getElementById("account-display-name").innerHTML = "非ログインユーザー";
        document.getElementById("me-icon").src = "/static/default_icon.png";
        
        let loginElement = document.createElement("div");
        loginElement.innerHTML = "ログイン";
        loginElement.className = "navbar-btn";
        loginElement.onclick = () => window.location.href = '/login';
        menu.appendChild(loginElement);

        let registerElement = document.createElement("div");
        registerElement.innerHTML = "登録";
        registerElement.className = "navbar-btn";
        registerElement.onclick = () => window.location.href = '/register';
        menu.appendChild(registerElement);
    }

    let navbar = document.querySelector('.navbar');
    navbar.classList.remove('hidden');

    if (isLoggedIn) {
        const postbtn = document.querySelector('.post-button');
        const overlay = document.getElementById('overlay');
        const modal = document.getElementById('modal');
        const closeButton = document.getElementById('close');
        const postContentButton = document.getElementById('postContentButton');

        postbtn.classList.remove('hidden');
        postbtn.addEventListener('click', function() {
            overlay.style.display = 'block';
            modal.style.display = 'block';
        });

        closeButton.addEventListener('click', function() {
            overlay.style.display = 'none';
            modal.style.display = 'none';
        });
    
        // オーバーレイをクリックしてもモーダルを閉じる
        overlay.addEventListener('click', function() {
            overlay.style.display = 'none';
            modal.style.display = 'none';
        });
        
        postContentButton.addEventListener('click', async function() {
            await postContent();
        })
    }

    let loading = document.querySelector('.loading');
    loading.style = "display: none;";

    document.getElementById('homeButton').addEventListener('click', async () => {
        await showHomeTimeLine(); // 非同期関数を呼び出し
    });

    await showHomeTimeLine();

    consoleWarning();
});

$(window).on('scroll', function(){
    var docHeight = $(document).innerHeight(), //ドキュメントの高さ
        windowHeight = $(window).innerHeight(), //ウィンドウの高さ
        pageBottom = docHeight - windowHeight; //ドキュメントの高さ - ウィンドウの高さ
    if(pageBottom <= $(window).scrollTop() && isLoading == false) {
      nowPage += 1;
      showHomeTimeLine(nowPage, true)
    }
});

function reloadMeDetail() {
    let username = userdata['name'];
    let displayName = userdata['display_name'] || username;
    let displayAvatar = userdata['icon_url'] || "/static/default_icon.png";

    document.getElementById("account-name").innerHTML = `@${username}`;
    document.getElementById("account-display-name").innerHTML = `${displayName}`;
    document.getElementById("me-icon").src = displayAvatar;
}

function consoleWarning() {
    console.log(
        "%cちょっと待ってくれ！",
        "font-size: 400%; color: red;"
    );
    
    console.log(
        "%cここに%c”変な文字列”%cを書くと、あなたのアカウントが乗っ取られてしまうかもしれません...",
        "font-size: 200%; color: red;",
        "font-size: 240%; color: orange;",
        "font-size: 200%; color: red;"
    );
    
    console.log(
        "%c試しに「console.log(userToken)」と書いてEnterを押してみてください。あなたのトークンが表示されます",
        "font-size: 1px; display: hidden;"
    );
    
    console.log(
        "%cもしあなたがシステムエンジニアあるいはその類の猫で、Nyantterに貢献したいなら、こちらへプルリクエストをどうぞ...！ → https://github.com/nennneko5787/Nyantter",
        "font-size: 200%; color: yellow;"
    );
    
    console.log(
        "え？console.log()で色をつけられるのかって？ → https://dev.classmethod.jp/articles/console-log-css/"
    );
}

// Paging
async function showHomeTimeLine(page = 0, notReplace = false) {
    let userCache = {};
    isLoading = true;

    try {
        window.history.pushState({}, "", "/home");

        const response = await fetch("/api/letters/timeline/latest?page="+page, {
            method: "get",
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const json = await response.json();
        const letters = json["letters"];
        console.log(letters);
        const lettersElement = document.getElementById("letters");
        if (!notReplace) lettersElement.innerHTML = ""; // Clear previous elements

        for (const letter of letters) {
            let userData; // Variable to hold user data

            // Check if user data exists in cache
            if (userCache[letter.userid]) {
                userData = userCache[letter.userid];
            } else {
                // Fetch user data if not found in cache
                const userResponse = await fetch(`/api/users/${letter.userid}`, {
                    method: "get",
                });

                if (!userResponse.ok) {
                    throw new Error(`Failed to fetch user data for user ID ${letter.userid}`);
                }

                userData = await userResponse.json();
                // Store fetched user data in cache
                userCache[letter.userid] = userData;
            }

            // Create elements and display user data
            const letterElement = document.createElement("div");
            letterElement.className = "letter";
            const letterProfile = document.createElement("div");
            letterProfile.className = "letter-profile";

            // Icon
            const iconDiv = document.createElement('div');
            iconDiv.className = 'icon';
            const iconImg = document.createElement('img');
            iconImg.className = 'icon_img';
            iconImg.src = userData.icon_url || '/static/default_icon.png';
            iconImg.width = 48;
            iconImg.height = 48;
            iconDiv.appendChild(iconImg);
            letterProfile.appendChild(iconDiv);

            // User name
            const letterNameDiv = document.createElement('div');
            letterNameDiv.className = 'letter-name';
            const displayNameDiv = document.createElement('div');
            displayNameDiv.className = 'account-display-name';
            displayNameDiv.textContent = userData.display_name || userData.name;
            const accountNameDiv = document.createElement('div');
            accountNameDiv.className = 'account-name';
            accountNameDiv.textContent = `@${userData.name}`;
            letterNameDiv.appendChild(displayNameDiv);
            letterNameDiv.appendChild(accountNameDiv);

            const letterDate = document.createElement("div");
            letterDate.className = "letter-date";
            const pastDate = new Date(letter.created_at)
            letterDate.innerHTML = timeAgo(pastDate);

            letterProfile.appendChild(letterNameDiv);
            letterProfile.appendChild(letterDate);

            // Letter content
            const letterContent = document.createElement("div");
            letterContent.className = "letter-content";
            letterContent.innerHTML = letter.content;

            const letterHR = document.createElement("hr");
            letterHR.className = "letter-hr";

            letterElement.appendChild(letterProfile);
            letterElement.appendChild(letterContent);
            letterElement.appendChild(letterHR);
            lettersElement.appendChild(letterElement);
        }
    } catch (error) {
        console.error('Error fetching letters:', error);
    }
    isLoading = false;
}

async function showUserProfile(userid) {
    const response = await fetch(`/api/users/${userid}`, {
        method: "get",
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    const json = await response.json();
    const letters = json["letters"];
    const lettersElement = document.getElementById("letters");
    lettersElement.innerHTML = ""; // 要素をクリア
}

// 各種処理
function timeAgo(date) {
    const seconds = Math.floor((Date.now() - date) / 1000);
    
    const intervals = [
        { label: '年', seconds: 31536000 },
        { label: 'ヶ月', seconds: 2592000 },
        { label: '日', seconds: 86400 },
        { label: '時間', seconds: 3600 },
        { label: '分', seconds: 60 },
        { label: '秒', seconds: 1 }
    ];

    for (let i = 0; i < intervals.length; i++) {
        const interval = intervals[i];
        const count = Math.floor(seconds / interval.seconds);
        if (count >= 1) {
            return count + interval.label + '前';
        }
    }

    return 'たった今';
}

async function postContent(replyed_to = null, relettered_to = null) {
    try{
        if (document.getElementById('postContentButton').ariaDisabled){
            return
        }

        let postContentElement = document.getElementById("postContent");
        let postContentValue = postContentElement.value;
        postContentElement.readOnly = true;
        document.getElementById('postContentButton').ariaDisabled = true;

        body = {
            content: postContentValue,
            replyed_to: replyed_to,
            relettered_to: relettered_to
        }

        let response = await fetch(
            "/api/letters",
            {
                method: "POST",
                headers: {
                    "Authorization": userToken,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(body)
            }
        )

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        overlay.style.display = 'none';
        modal.style.display = 'none';
        showSnackBar("レターをポストしました。")
        postContentElement.readOnly = false;
        document.getElementById('postContentButton').ariaDisabled = false;
        postContentElement.value = "";
        await showHomeTimeLine();
        return;
    } catch (error) {
        postContentElement.readOnly = false;
        document.getElementById('postContentButton').ariaDisabled = false;
        console.error('Error fetching letters:', error);
    }
}

function showSnackBar(text) {
    // Get the snackbar DIV
    let x = document.createElement("div")

    x.id = "snackbar";
    x.innerHTML = text;

    document.body.appendChild(x);

    // Add the "show" class to DIV
    x.className = "show";

    // After 3 seconds, remove the show class from DIV
    setTimeout(() => {
        x.className = x.className.replace("show", "");
        x.remove();
    }, 3000);
}
