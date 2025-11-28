d:/projects/Doctor/
├── backend/
│   ├── .env
│   ├── .gitignore
│   ├── app.py
│   ├── middleware/
│   │   ├── auth_middleware.py
│   │   ├── cors_middleware.py
│   │   ├── logging_middleware.py
│   │   ├── rate_limit_middleware.py
│   │   └── __init__.py
│   ├── models.py
│   ├── package-lock.json
│   ├── requirements.txt
│   ├── routes/
│   │   ├── analytics_routes.py
│   │   ├── auth_routes.py
│   │   ├── billing_routes.py
│   │   ├── facilities_routes.py
│   │   ├── health_routes.py
│   │   ├── patients_routes.py
│   │   ├── payments_routes.py
│   │   ├── services_routes.py
│   │   ├── settlement_routes.py
│   │   ├── staff_routes.py
│   │   ├── users_routes.py
│   │   ├── __init__.py
│   │   └── __pycache__/
│   │       ├── health_routes.cpython-310.pyc
│   │       └── __init__.cpython-310.pyc
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── billing_service.py
│   │   ├── email_service.py
│   │   ├── settlement_service.py
│   │   ├── sms_service.py
│   │   └── __init__.py
│   ├── static/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   └── test_facilities.py
│   ├─] uploads/ (ignored)
│   ├── utils/
│   │   ├── decorators.py
│   │   ├── encryption.py
│   │   ├── helpers.py
│   │   ├── validators.py
│   │   └── __init__.py
│   ├─] venv/ (ignored)
│   ├── wsgi.py
│   └─] __pycache__/ (ignored)
└── frontend/
    ├── .gitignore
    ├── eslint.config.js
    ├── index.html
    ├─] node_modules/ (ignored)
    ├── package-lock.json
    ├── package.json
    ├── public/
    │   └── vite.svg
    ├── README.md
    ├── src/
    │   ├── App.css
    │   ├── App.jsx
    │   ├── assets/
    │   │   └── react.svg
    │   ├── components/
    │   │   ├── auth/
    │   │   │   └── ProtectedRoute.jsx
    │   │   ├── billing/
    │   │   │   ├── BillCard.jsx
    │   │   │   ├── BillForm.jsx
    │   │   │   └── PaymentForm.jsx
    │   │   ├── common/
    │   │   │   ├── Alert.jsx
    │   │   │   ├── Badge.jsx
    │   │   │   ├── Button.jsx
    │   │   │   ├── Card.jsx
    │   │   │   ├── Input.jsx
    │   │   │   ├── Loading.jsx
    │   │   │   ├── Modal.jsx
    │   │   │   └── Table.jsx
    │   │   ├── facilities/
    │   │   │   ├── FacilityCard.jsx
    │   │   │   ├── FacilityForm.jsx
    │   │   │   └── FacilityList.jsx
    │   │   ├── layout/
    │   │   │   ├── DashboardLayout.jsx
    │   │   │   ├── Footer.jsx
    │   │   │   ├── Header.jsx
    │   │   │   └── Sidebar.jsx
    │   │   └── patients/
    │   │       ├── PatientCard.jsx
    │   │       ├── PatientForm.jsx
    │   │       └── PatientList.jsx
    │   ├── config/
    │   │   └── api.config.js
    │   ├── context/
    │   │   ├── AuthContext.jsx
    │   │   └── ThemeContext.jsx
    │   ├── hooks/
    │   │   ├── useApi.js
    │   │   ├── useAuth.js
    │   │   ├── useDebounce.js
    │   │   └── useForm.js
    │   ├── index.css
    │   ├── main.jsx
    │   ├── pages/
    │   │   ├── auth/
    │   │   │   ├── Login.jsx
    │   │   │   └── Register.jsx
    │   │   ├── billing/
    │   │   │   ├── BillDetails.jsx
    │   │   │   ├── BillingPage.jsx
    │   │   │   └── CreateBill.jsx
    │   │   ├── ConnectionTest.jsx
    │   │   ├── dashboard/
    │   │   │   └── Dashboard.jsx
    │   │   ├── facilities/
    │   │   │   ├── CreateFacility.jsx
    │   │   │   ├── FacilitiesPage.jsx
    │   │   │   └── FacilityDetails.jsx
    │   │   ├── NotFound.jsx
    │   │   └── patients/
    │   │       ├── CreatePatient.jsx
    │   │       ├── PatientDetails.jsx
    │   │       └── PatientsPage.jsx
    │   ├── services/
    │   │   ├── api.service.js
    │   │   └── toast.service.js
    │   └── utils/
    │       ├── constants.js
    │       ├── formatters.js
    │       ├── helpers.js
    │       └── validators.js
    └── vite.config.js
