let attendance_id = getUrlParam("id");

window.onload = function () {
	if (attendance_id) {
		loadAttendanceSheetInfo();
		$("#sheetInfo").prop("hidden", false);
		$("#registrationForm").prop("hidden", false);
	} else {
		$("#fetchAttendanceSheet").prop("hidden", false);
	}
};

function timestampToDate(timestamp) {
	let date = new Date(timestamp);
	return `${date.toLocaleDateString()} às ${date.getHours()}h${date.getMinutes()}min`;
}

function loadAttendanceSheetInfo() {
	$("#closedMessage").prop("hidden", true);
	$("#attendance_error_message").empty();

	$.ajax({
			type: "GET",
			url: `${rest_api.attendance_sheet}/${attendance_id}`,
		})
		.done(function (response) {
			const timestamp = timestampToDate(response.data.timestamp);
			const course_unit_name = response.data.course_unit_name;
			const name = response.data.creator_name;

			$("#course_unit_name").text(course_unit_name);
			$("#teacher_name").text(name);
			$("#timestamp").text(timestamp);

			$("#sheetInfo").prop("hidden", false);

			if (response.data.is_active) {
				$("#fetchAttendanceSheet").prop("hidden", true);
				$("#registrationForm").prop("hidden", false);
			} else {
				$("#registrationForm").prop("hidden", true);
				$("#closedMessage").prop("hidden", false);
			}
		})
		.fail(function (response) {
			$("#sheetInfo").prop("hidden", true);
			$("#registrationForm").prop("hidden", true);
			(response.responseJSON.errors).forEach(element => {
				$("#attendance_error_message").append(element + "<br>");
			});
		});
}


function attendance_registration() {
	let errors = false;

	// remove all errors
	$("#nmec").removeClass("is-invalid");
	$("#name").removeClass("is-invalid");
	$("#registration_error_message").empty();

	// check nmec
	if ($("#nmec").val().length === 0) {
		$("#registration_error_message").append("Introduza o número mecanográfico!<br>");
		errors = true;
	}
	// check name
	if ($("#name").val().length < 5) {
		$("#name").addClass("is-invalid");
		$("#registration_error_message").append("O Nome tem de conter, pelo menos, 5 caracteres!<br>");
		errors = true;
	}
	// check if we can proceed
	if (errors) return false;

	let data = {
		nmec: $("#nmec").val(),
		name: $("#name").val()
	};

	$.ajax({
			type: "POST",
			data: JSON.stringify(data),
			dataType: 'json',
			contentType: 'application/json',
			url: `${rest_api.attendance_sheet}/${attendance_id}/student/registration`,
		})
		.done(function (response) {
			$('#successModal').modal('show');
		})
		.fail(function (response) {
			(response.responseJSON.errors).forEach(element => {
				$("#registration_error_message").append(element + "<br>");
			});
		});

	return false;
}

function fetchAttendanceSheet() {
	let errors = false;

	// remove all errors
	$("#aulaId").removeClass("is-invalid");
	$("#registration_error_message").empty();

	// check aula ID
	if ($("#aulaId").val().length < 6) {
		$("#aulaId").addClass("is-invalid");
		$("#registration_error_message").append("O ID da aula tem de conter, pelo menos, 6 caracteres!<br>");
		errors = true;
	}
	// check if we can proceed
	if (errors) return false;

	attendance_id = $("#aulaId").val();

	loadAttendanceSheetInfo();
}
