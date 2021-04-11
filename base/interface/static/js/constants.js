const in_prod = false;

// API URLs
let base_api = in_prod ? "https://api-registo-presencas.aettua.pt" : "http://localhost:9000";
let base_url = in_prod ? "https://registo-presencas.aettua.pt" : "http://localhost:8000";


const rest_api = {
    // auth
    register: `${base_api}/register`,
    login: `${base_api}/login`,
    loogut: `${base_api}/logout`,

    // profile
    profile: `${base_api}/profile`,
    edit_base_info: `${base_api}/profile/edit`,
    edit_password: `${base_api}/profile/password`,

    // depts
    depts: `${base_api}/department/all`,

    // course unit
    course_units: `${base_api}/course_units`,
    new_attendance_sheet: `${base_api}/attendance/sheet/new`,
    attendance_sheet: `${base_api}/attendance/sheet`,
    attendance_sheets: `${base_api}/attendance/sheets`,
};

// WEB URLs
let pages = {
    home: "index.html",
    login: "login.html",

    // accounts
    register: "register.html",
    edit_profile: "edit-profile.html",

    // attendances
    create_attendance_sheet: "index.html",
    attendance_sheet: "attendance-sheet.html",
    attendance_sheet_history: "attendance-sheet-history.html",
    attendance_registration: "reg.html"
};

if (in_prod) {
    Object.keys(pages).forEach(function (key) {
        if (key === "attendance_registration") {
            pages[key] = pages[key].slice(0, -11);
        } else {
            pages[key] = pages[key].slice(0, -5);
        }
    });
}

const numOfColumns = 5;