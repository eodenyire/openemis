# mobile — Flutter Companion App (v1)

A Flutter mobile application that connects to the openEMIS v1 FastAPI backend. Designed for student-facing features — attendance, results, fees, timetable, and announcements.

## Tech Stack

- Flutter (Dart)
- HTTP client via `api_client.dart`
- Provider-based state management

## Structure

```
mobile/
├── lib/
│   ├── main.dart               # App entry point
│   ├── api_client.dart         # HTTP client wrapping the v1 REST API
│   ├── auth_provider.dart      # Authentication state management
│   ├── router.dart             # App navigation/routing
│   ├── theme.dart              # App theme and styling
│   ├── models/                 # Data models
│   │   ├── student.dart
│   │   ├── attendance.dart
│   │   ├── exam_result.dart
│   │   └── fee_invoice.dart
│   ├── screens/                # UI screens
│   │   ├── login_screen.dart
│   │   ├── home_screen.dart
│   │   ├── students_screen.dart
│   │   ├── student_detail_screen.dart
│   │   ├── attendance_screen.dart
│   │   ├── results_screen.dart
│   │   ├── fees_screen.dart
│   │   ├── timetable_screen.dart
│   │   ├── announcements_screen.dart
│   │   └── profile_screen.dart
│   └── widgets/                # Reusable UI components
│       ├── stat_card.dart
│       ├── loading_widget.dart
│       └── error_widget.dart
└── pubspec.yaml
```

## Features

- JWT authentication against the v1 API
- Student profile and dashboard
- Attendance history
- Exam results and report cards
- Fee invoices and payment status
- Class timetable
- School announcements

## Setup

```bash
flutter pub get
flutter run
```

Configure the API base URL in `api_client.dart` to point to your running v1 backend.
