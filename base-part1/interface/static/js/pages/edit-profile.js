let cache_auth_token = getCookie("access_token");
const cache_email = getCookie("email");

// On Load, load student info
window.onload = function () {
	checkUser();

	get_base_info();
};


function edit_base_info(form) {
	let errors = false;

	// clean GUI
	$("form :input").each(function () {
		$(this).removeClass("is-invalid");
	});
	// remove all errors
	$("#error_message_base_info").html("");

	// check name
	if ($("#first_name").val().length < 3) {
		errors = true;
		$("#first_name").addClass("is-invalid");
		$("#error_message_base_info").append("O Nome tem de conter, pelo menos, 3 caracteres!<br>");
	}
	// check surname
	if ($("#last_name").val().length < 3) {
		errors = true;
		$("#last_name").addClass("is-invalid");
		$("#error_message_base_info").append("O Apelido tem de conter, pelo menos, 3 caracteres!<br>");
	}

	// check if we can proceed
	if (errors) return false;

	// serialize the form data
	let data = $(form).serialize();

	// call rest api to update profile
	$.ajax({
			type: "PUT",
			url: rest_api.edit_base_info,
			data: data,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			},
		})
		.done(function (response) {
			// save info on cookies
			setCookie("name", `${response.data.first_name} ${response.data.last_name}`);

			updateUserNameTopBar();

			$("#successModalText").text("Informações atualizadas com sucesso!")
			$('#successModal').modal('show');
		})
		.fail(function (response) {
			(response.responseJSON.errors).forEach(element => {
				$("#error_message_base_info").append(element + "<br>");
			});
		})
		.always(function (response) {
			if (response.status !== 401) {
				setCookie("access_token", response.token);
			}
		});

	return false;
}

function edit_password(form) {
	let errors = false;

	// clean GUI
	$("form :input").each(function () {
		$(this).removeClass("is-invalid");
	});
	// remove all errors
	$("#error_message_password").html("");

	// check password
	if ($("#current_password").val().length < 8) {
		errors = true;
		$("#current_password").addClass("is-invalid");
		$("#error_message_password").append("A password tem de conter, pelo menos, 8 caracteres!<br>");
	}
	// check if passwords match
	if ($("#password").val() !== $("#password_confirm").val()) {
		errors = true;
		$("#password").addClass("is-invalid");
		$("#password_confirm").addClass("is-invalid");
		$("#error_message_password").append("As passwords são diferentes!<br>");
	}

	// check if we can proceed
	if (errors) return false;

	// serialize the form data
	let data = $(form).serialize();

	// call rest api to update password
	$.ajax({
			type: "PUT",
			url: rest_api.edit_password,
			data: data,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			},
		})
		.done(function () {
			$("#successModalText").text("Password atualizada com sucesso!")
			$('#successModal').modal('show');
			setCookie("access_token", response.token);
		})
		.fail(function (response) {
			$("#password").addClass("is-invalid");
			$("#password_confirm").addClass("is-invalid");
			$("#current_password").addClass("is-invalid");

			(response.responseJSON.errors).forEach(element => {
				$("#error_message_password").append(element + "<br>");
			});
		});

	return false;
}

function get_base_info() {
	$.ajax({
			type: "GET",
			url: rest_api.profile,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			},
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			load_base_info(response.data.first_name, response.data.last_name, response.data.email);
		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}
		});
}

function load_base_info(first_name, last_name, email) {
	$("#first_name").val(first_name);
	$("#last_name").val(last_name);
	$("#email").val(email);
}
