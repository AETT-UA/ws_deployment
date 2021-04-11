// Cookies
function setCookie(sKey, sValue, vEnd, sPath, sDomain, bSecure) {
    if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) {
        return false;
    }
    var sExpires = "";
    if (vEnd) {
        switch (vEnd.constructor) {
            case Number:
                sExpires =
                    vEnd === Infinity ?
                    "; expires=Fri, 31 Dec 9999 23:59:59 GMT" :
                    "; max-age=" + vEnd;
                break;
            case String:
                sExpires = "; expires=" + vEnd;
                break;
            case Date:
                sExpires = "; expires=" + vEnd.toUTCString();
                break;
        }
    }
    document.cookie =
        encodeURIComponent(sKey) +
        "=" +
        encodeURIComponent(sValue) +
        sExpires +
        (sDomain ? "; domain=" + sDomain : "") +
        (sPath ? "; path=" + sPath : "") +
        (bSecure ? "; secure" : "");
    return true;
}

function getCookie(name) {
    return (
        decodeURIComponent(
            document.cookie.replace(
                new RegExp(
                    "(?:(?:^|.*;)\\s*" +
                    encodeURIComponent(name).replace(
                        /[\-\.\+\*]/g,
                        "\\$&"
                    ) +
                    "\\s*\\=\\s*([^;]*).*$)|^.*$"
                ),
                "$1"
            )
        ) || null
    );
}

function deleteCookie(sKey, sPath, sDomain) {
    if (!sKey || !hasCookie(sKey)) {
        return false;
    }
    document.cookie =
        encodeURIComponent(sKey) +
        "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" +
        (sDomain ? "; domain=" + sDomain : "") +
        (sPath ? "; path=" + sPath : "");
    return true;
}

function hasCookie(sKey) {
    return new RegExp(
        "(?:^|;\\s*)" +
        encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") +
        "\\s*\\="
    ).test(document.cookie);
}

// Miscalleaneous
function navigateTo(url) {
    window.location.href = url;
}

function scrollTop(element = null) {
    let scrollTopValue =
        element === null ? 0 : $(element[0]).offset().top - 200;
    $("html,body").animate({
        scrollTop: scrollTopValue
    }, "slow");
}

function generateUrls() {
    let key;
    $("[url-to]").each(function () {
        key = $(this).attr("url-to");
        if (Object.keys(pages).includes(key)) {
            this.href = pages[key];
        }
        $(this).removeAttr("url-to");
    });
}

function updateUserNameTopBar() {
    $("#user_name_top_bar").text(getCookie("name"));
}

function getUrlParam(param) {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    return urlParams.get(param);
}

function timestampToDate(timestamp) {
    if (timestamp === null) {
        return "";
    }

    let date = new Date(timestamp);

    let minutes = (date.getMinutes() + "").length === 1 ? "0" + date.getMinutes() : date.getMinutes();
    let hours = (date.getHours() + "").length === 1 ? "0" + date.getHours() : date.getHours();

    return `${date.toLocaleDateString()} às ${hours}h${minutes}min`;
}

function generateQRCode(sheet_id) {
    // oncard
    $("#qr_code").empty();
    let qrcode = new QRCode("qr_code", {
        width: 1024,
        height: 1024,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });
    qrcode.makeCode(sheet_id);
    $("#qr_code").children().css("width", "50%");
    $("#qr_code").children().css("margin-left", "25%");
    $("#qr_code").children().css("cursor", "zoom-in");
    $("#qr_code").click(function () {
        openOverlayQRCode()
    });


    // fullscreen
    $("#qr_full_screen_div").empty();
    let qrcode_full = new QRCode("qr_full_screen_div", {
        width: 2048,
        height: 2048,
        colorDark: "#ffffff",
        colorLight: "#000000",
        correctLevel: QRCode.CorrectLevel.H
    });
    qrcode_full.makeCode(sheet_id);
    $("#qr_full_screen_div").children().css("width", "calc((100vh - 3.75rem)*0.65)");
    $("#qr_full_screen_div").children().css("margin-left", "calc((100% - (100vh - 3.75rem)*0.65)/2)");
    $("#qr_full_screen_div").children().css("cursor", "zoom-out");

    $("#qr_full_screen_div").click(function () {
        closeOverlayQRCode()
    });
}

function openOverlayQRCode() {
    $("#overlay_div").css("display", "block");
}

function closeOverlayQRCode() {
    $("#overlay_div").css("display", "none");
}

function checkUser() {
    if (!hasCookie("access_token") || !hasCookie("email") || !hasCookie("name")) {
        navigateTo(pages.login);
    }
}