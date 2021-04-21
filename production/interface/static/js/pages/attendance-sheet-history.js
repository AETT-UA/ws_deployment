let cache_auth_token = getCookie("access_token");

let intervalId = null;
let attendanceSheetIsActive = null;
let attendanceId = null;

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

// On Load, load CUs
window.onload = function () {
	checkUser();

	loadCourseUnits();
};

function loadCourseUnits() {
	// call rest api to update the course units
	$.ajax({
			type: "GET",
			url: `${rest_api.course_units}/my`,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			(response.data).forEach(cu => {
				$('#cuSelect').append(`<option value="${cu.id}">${cu.name}</option>`);
			});
		})
		.fail(function (response) {
			(response.responseJSON.errors).forEach(() => {
				$("#cuSelectErrorMessage").text("Não foi possível carregar as unidades curriculares.");
			});
		});
}

function chooseCurricularUnit() {
	let cuId = $("#cuSelect").val();

	// check if a curricular unit has been selected
	if (cuId === null) {
		//GUI
		$("#cuSelectErrorMessage").addClass("is-invalid");
	} else {
		// GUI
		$("#cuSelect").removeClass("is-invalid");
		$("#cuSelectErrorMessage").text();

		loadAttendanceSheetsSchedules(cuId);
	}
}

function loadAttendanceSheetsSchedules(cuId) {
	// call rest api to update the course units
	$.ajax({
			type: "GET",
			url: `${rest_api.attendance_sheets}/${cuId}`,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			let attendances = response.data.attendances;

			$("#scheduleSelect").empty();

			if (attendances.length === 0) {
				$("#emptyMessage").prop("hidden", false);
				$("#scheduleSelect").prop("hidden", true);
				$("#fetchAttendanceSheetBtn").prop("hidden", true);
			} else {
				$("#emptyMessage").prop("hidden", true);
				$("#scheduleSelect").prop("hidden", false);
				$("#fetchAttendanceSheetBtn").prop("hidden", false);
			}

			$("#scheduleSelect").append(`<option value="default" disabled selected>
                Escolha o horário em que a aula foi lecionada.
            </option>`);

			attendances.sort((a, b) => (a.summary > b.summary) ? 1 : ((b.summary > a.summary) ? -1 : 0));

			let summary;
			attendances.forEach(cu => {
				summary = cu.summary === null ? '' : cu.summary + ' |';

				$('#scheduleSelect').append(`<option value="${cu.id}"> ${summary} ${timestampToDate(cu.register_timestamp)}</option>`);
			});
		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}

			(response.responseJSON.errors).forEach(() => {
				$("#cuSelectErrorMessage").text("Não foi possível carregar as unidades curriculares.");
			});
		});

	// show select and choose button
	$("#scheduleDiv").prop("hidden", false);
}

function chooseAttendanceSheet() {
	attendanceId = $("#scheduleSelect").val();

	// check if a curricular unit has been selected
	if (attendanceId === null) {
		//GUI
		$("#scheduleSelectErrorMessage").prop("hidden", false);
		$("#scheduleSelect").addClass("is-invalid");
	} else {
		// GUI
		$("#scheduleSelect").removeClass("is-invalid");
		$("#scheduleSelectErrorMessage").text();

		fetchAttendanceSheet();
	}
}

function fetchAttendanceSheet() {
	// delete previous cronjob
	toggleLoadStudentsCronjob(false);

	loadAttendanceSheetBasicInfo();

	$("#studentsDiv").prop("hidden", false);
	loadAttendanceStudents();
}

function loadAttendanceSheetBasicInfo() {
	// generate QRCode
	let url = `${base_url}/${pages.attendance_registration}?id=${attendanceId}`;
	generateQRCode(url);
	$("#studentRegisterUrl").text(url);
	$("#studentRegisterUrlFullScreen").text(url);

	// show basic info div
	$("#basicInfoDiv").prop("hidden", false);


	$.ajax({
			type: "GET",
			url: `${rest_api.attendance_sheet}/${attendanceId}`,
			headers: {
				Authorization: `Token ${cache_auth_token}`,
			}
		})
		.done(function (response) {
			setCookie("access_token", response.token);

			let data = response.data;
			attendanceSheetIsActive = data.is_active;

			toggleLoadStudentsCronjob(attendanceSheetIsActive);

			toggleAttendanceSheetButton();

		})
		.fail(function (response) {
			if (response.status === 401) {
				navigateTo(pages.login);
			}
		});
}

function toggleAttendanceSheet() {
	let data = {
		status: !attendanceSheetIsActive
	};

	$.ajax({
			type: "POST",
			url: `${rest_api.attendance_sheet}/${attendanceId}/status`,
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

	let status = attendanceSheetIsActive ? "aberto" : "fechado";
	let statusColor = attendanceSheetIsActive ? "green" : "red";
	$("#attendanceStatus").text(status);
	$("#attendanceStatus").css("color", statusColor);
}

function loadAttendanceStudents() {
	cache_auth_token = getCookie("access_token");

	$.ajax({
			type: "GET",
			url: `${rest_api.attendance_sheet}/${attendanceId}/students`,
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
			url: `${rest_api.attendance_sheet}/${attendanceId}/student/deletion`,
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

function openRegisterStudentModal() {
	$("#registerStudentModal").modal("show");
	$("#nmec").val("");
	$('#successDiv').prop("hidden", true);
	$("#registrationErrorMessage").text("");
	$("#nmec").removeClass("is-invalid");
}

function registerStudent() {
	cache_auth_token = getCookie("access_token");
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
			url: `${rest_api.attendance_sheet}/${attendanceId}/student/registration`,
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
