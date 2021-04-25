let cache_auth_token = getCookie("access_token");

const attendance_id = getUrlParam("id");

let intervalId = null;
let attendanceSheetIsActive = null;

let table = $("#students_table").DataTable({
	dom: "Bfrtip",
	paging: false,
	info: false,
	searching: false,
	responsive: true,
	buttons: [{
		extend: "csv",
		text: "Download CSV",
		className: "exportButton"
	}],
	columns: [{
		title: "Timestamp",
		data: "timestamp"
	}, {
		title: "Nº Mecanográfico",
		data: "nmec"
	}, {
		title: "Nome",
		data: "name"
	}, ],
});

// On Load, load attendance sheet info
window.onload = function () {
	checkUser();
	loadInfo();
	loadAttendanceStudents();
};

function loadInfo() {
	$("#professor").text(getCookie("name"));

	let url = `${base_url}/${pages.attendance_registration}?id=${attendance_id}`;
	generateQRCode(url);
	$("#studentRegisterUrl").text(url);
	$("#studentRegisterUrlFullScreen").text(url);

	$.ajax({
			type: "GET",
			url: `${rest_api.attendance_sheet}/${attendance_id}`,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			let data = response.data;
			attendanceSheetIsActive = data.is_active;

			toggleLoadStudentsCronjob(attendanceSheetIsActive);

			$("#aula_nome").text(data.course_unit_name);
			$("#nr_aula").text(`Aula de ${data.course_unit_name}`);
			$("#timestamp").text(timestampToDate(data.timestamp));

			toggleAttendanceSheetButton();

		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}
		});
}

function loadAttendanceStudents() {
	cache_auth_token = getCookie("access_token");

	$.ajax({
			type: "GET",
			url: `${rest_api.attendance_sheet}/${attendance_id}/students`,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			let students = response.data;

			students.forEach(function (student) {
				student.timestamp = timestampToDate(student.timestamp);
			})

			table.clear();
			table.rows.add(students).draw(false);

			$("#total_students").text(`Total: ${students.length} alunos`);
		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}
		});
}

function toggleLoadStudentsCronjob(start = true) {
	if (start) {
		intervalId = setInterval(loadAttendanceStudents, 15000);
	} else {
		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}
	}
}

function removeStudents() {
	let trs = $(".selectedStudentCell");

	let studentsToDelete = trs.map(function () {
		let nmecTd = $(this).children()[1];
		return $(nmecTd).text();
	}).get();

	let data = {
		nmecs: studentsToDelete
	};

	$.ajax({
			type: "DELETE",
			url: `${rest_api.attendance_sheet}/${attendance_id}/student/deletion`,
			data: JSON.stringify(data),
			dataType: 'json',
			contentType: 'application/json',
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			toggleStudentsRemoval(false);
			loadAttendanceStudents();
		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}
		});
}

function toggleStudentsRemoval(active = true) {
	// toggle recurrent refresh
	toggleLoadStudentsCronjob(!active);

	// toggle CSS to td
	let trs = $("#students_table tbody tr");

	if (active) {
		trs.addClass("activeStudentCell");
		trs.on("click", function () {
			this.classList.toggle("activeStudentCell");
			this.classList.toggle("selectedStudentCell");
		});
	} else {
		trs.removeClass("activeStudentCell");
		trs.removeClass("selectedStudentCell");
		trs.unbind('click');
	}

	// toogle button
	$("#selectStudentsBtn").prop("disabled", active);

	$("#selectHelp").prop("hidden", !active);
	$("#selectButtons").prop("hidden", !active);
}

function toggleAttendanceSheet() {
	let data = {
		status: !attendanceSheetIsActive
	};

	$.ajax({
			type: "POST",
			url: `${rest_api.attendance_sheet}/${attendance_id}/status`,
			data: JSON.stringify(data),
			dataType: 'json',
			contentType: 'application/json',
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			let message = attendanceSheetIsActive ? "fechada" : "aberta";
			$("#successModalText").text(`Folha de registos ${message} com sucesso!`)
			$('#successModal').modal('show');

			attendanceSheetIsActive = !attendanceSheetIsActive;

			toggleLoadStudentsCronjob(attendanceSheetIsActive);
			loadAttendanceStudents();

			toggleAttendanceSheetButton();
		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}
		});
}

function toggleAttendanceSheetButton() {
	let text = attendanceSheetIsActive ? "Fechar Registo de Presenças" : "Abrir Registo de Presenças";
	let button = $("#attendanceSheetBtn");
	button.text(text);
	button.toggleClass("btn-warning", attendanceSheetIsActive);
	button.toggleClass("btn-success", !attendanceSheetIsActive);
}

function openRegisterStudentModal() {
	$("#registerStudentModal").modal("show");
	$("#nmec").val("");
	$('#successDiv').prop("hidden", true);
	$("#registrationErrorMessage").text("");
	$("#nmec").removeClass("is-invalid");
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

function registerStudent() {
	ache_auth_token = getCookie("access_token");
	let errors = false;

	// remove all errors
	$("#nmec").removeClass("is-invalid");
	$("#name").removeClass("is-invalid");
	$("#registrationErrorMessage").empty();

	// check nmec
	if ($("#nmec").val().length === 0) {
		$("#registrationErrorMessage").append("Introduza o número mecanográfico!<br>");
		errors = true;
	}
	// check name
	if ($("#name").val().length < 5) {
		$("#name").addClass("is-invalid");
		$("#registrationErrorMessage").append("O Nome tem de conter, pelo menos, 5 caracteres!<br>");
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
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			$("#nmec").val("");
			$("#name").val("");
			$('#successDiv').prop("hidden", false);

			loadAttendanceStudents();
		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}

			(response.responseJSON.errors).forEach(element => {
				$("#registrationErrorMessage").append(element + "<br>");
			});
		});

	return false;
}
