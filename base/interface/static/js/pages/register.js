function register(form) {
    let errors = false;

    // remove all errors
    $("form :input").each(function () {
        $(this).removeClass("is-invalid");
    });
    $("#error_message").html("");

    // check name
    if ($("#first_name").val().length < 3) {
        errors = true;
        $("#first_name").addClass("is-invalid");
        $("#error_message").append("O Nome tem de conter, pelo menos, 3 caracteres!<br>");
    }
    // check surname
    if ($("#last_name").val().length < 3) {
        errors = true;
        $("#last_name").addClass("is-invalid");
        $("#error_message").append("O Apelido tem de conter, pelo menos, 3 caracteres!<br>");
    }
    if (!(/\S+@\S+\.\S+/.test($("#email").val()))) {
        errors = true;
        $("#email").addClass("is-invalid");
        $("#error_message").append("Email inválido!<br>");
    }
    // check password
    if ($("#password").val().length < 8) {
        errors = true;
        $("#password").addClass("is-invalid");
        $("#error_message").append("A password tem de conter, pelo menos, 8 caracteres!<br>");
    }
    // check if passwords match
    if ($("#password").val() !== $("#password_confirm").val()) {
        errors = true;
        $("#password").addClass("is-invalid");
        $("#password_confirm").addClass("is-invalid");
        $("#error_message").append("As passwords são diferentes.<br>Confirme a sua password!<br>");
    }

    // check if we can proceed
    if (errors) return false;

    // serialize the form data
    let data = $(form).serialize();


    $.ajax({
            type: "POST",
            url: rest_api.register,
            data: data,
        })
        .done(function (response) {
            setCookie("access_token", response.token);
            setCookie("email", response.data.email);
            setCookie("name", `${response.data.first_name} ${response.data.last_name}`);

            // show success modal
            $('#successModal').modal('show');
        })
        .fail(function (response) {

            (response.responseJSON.errors).forEach(element => {
                $("#error_message").append(element + "<br>");
            });
        });

    return false;
}

$("#successModal").on('hidden.bs.modal', function () {
    navigateTo(pages.home);
});
