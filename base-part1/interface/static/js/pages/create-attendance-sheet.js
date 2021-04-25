let cache_auth_token = getCookie("access_token");
const cache_email = getCookie("email");

// On Load, load CUs
window.onload = function () {
	// re-select default DEPT value
	$('#depts_select').val("default");

    checkUser();
    getDepts();
};

function getDepts() {
    // call rest api to update the course units
    $.ajax({
            type: "GET",
            url: rest_api.depts,
        })
        .done(function (response) {
            (response.data).forEach(cu => {
                $('#depts_select').append(`<option value="${cu.id}">${cu.name}</option>`);
            });
        })
        .fail(function (response) {
            (response.responseJSON.errors).forEach(element => {
                $("#error_message_depts").text("Não foi possível carregar os departamentos.");
            });
        });
}

function getCourseUnitsForDept(dept_id) {
    // call rest api to update the course units
    $.ajax({
            type: "GET",
            url: `${base_api}/department/${dept_id}/course_units`,
        })
        .done(function (response) {
            // show desc_div
            $('#desc_div').css("display", "block");
            $('#summary').empty();
            // show cus div and add options
            $('#cus_div').css("display", "block");
            $('#cus_select').empty();
            $('#cus_select').append(`<option value="default">Escolha uma aula</option>`);
            (response.data).forEach(cu => {
                $('#cus_select').append(`<option value="${cu.id}">${cu.name}</option>`);
            });
        })
        .fail(function (response) {
            (response.responseJSON.errors).forEach(element => {
                $("#error_message").text("Não foi possível carregar as unidades curriculares.");
            });
        });
}

function chooseCurricularUnit() {
    let cu_id = $("#cus_select").val();
    let summary = $("#summary").val();

    // check if a curricular unit has been selected
    if (cu_id === null) {
        //GUI
        $("#cus_select").addClass("is-invalid");
        $("#error_message").text("Por favor, selecione uma unidade curricular.");
    } else {
        // GUI
        $("#cus_select").removeClass("is-invalid");
        $("#error_message").text();

        // Create attendance sheet
        createAttendanceSheet(cu_id, summary);
    }
}

function createAttendanceSheet(cu_id, summary) {

    let data = {
        course_unit: cu_id,
        is_active: true
    };

    if (summary !== '')
        data['summary'] = summary.toUpperCase();;

    $.ajax({
            type: "POST",
            url: rest_api.new_attendance_sheet,
            data: data,
            headers: {
                Authorization: `Token ${cache_auth_token}`,
            }
        })
        .done(function (response) {
            setCookie("access_token", response.token);

            navigateTo(`${pages.attendance_sheet}?id=${response.data.attendance_id}`);
        })
        .fail(function (response) {
            if (response.status === 401) {
                navigateTo(pages.login);
            }
        });
}
