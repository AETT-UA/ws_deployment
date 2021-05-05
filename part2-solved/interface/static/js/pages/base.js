$(function () {
    //load footer
    $.get("footer.html", function (data) {
        $("#footer").replaceWith(data);
    });
});

$(window).on("load", () => {
    generateUrls();
    updateUserNameTopBar();
});

function logout() {
    const cache_auth_token = getCookie("access_token");

    $.ajax({
            type: "GET",
            url: rest_api.loogut,
            headers: {
                Authorization: `Token ${cache_auth_token}`,
            }
        })
        .done(function () {
            // delete saved cookies
            deleteCookie("access_token");
            deleteCookie("email");
            deleteCookie("name");

            // redirecting
            navigateTo(pages.login);
        })
        .fail(function (response) {
            if (response.status === 401) {
                navigateTo(pages.login);
            }
        });
}