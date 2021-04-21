function login(form) {
	// serialize the form data
	let data = $(form).serialize();

	$.ajax({
			type: "POST",
			url: rest_api.login,
			data: data,
		})
		.done(function (response) {
			// save info on cookies
			setCookie("access_token", response.token);
			setCookie("email", response.data.user.email);
			setCookie("name", `${response.data.user.first_name} ${response.data.user.last_name}`);
			// redirecting
			navigateTo(pages.create_attendance_sheet);
		})
		.fail(function () {
			$("#password_input").addClass("is-invalid");
			$("#email_input").addClass("is-invalid");
			$("#error_message").css("display", "block");
		});

	return false;
}
