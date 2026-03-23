# assets — Frontend Assets (v4 Legacy PHP/CI Layer)

Static frontend assets for the legacy CodeIgniter/PHP layer of the v4 system.

## Structure

```
assets/
├── css/        # Bootstrap and custom stylesheets
├── fonts/      # Web fonts (Font Awesome, Google Fonts)
├── images/     # UI images, icons, backgrounds
├── js/         # jQuery plugins, Bootstrap JS, custom scripts
├── login/      # Login page specific assets
├── install/    # Installation wizard assets
└── *.js        # amCharts, export, pie/serial chart libraries
```

## Chart Libraries

- `amcharts.js` — amCharts core for dashboard visualisations
- `pie.js` / `serial.js` — Pie and serial chart types
- `export.js` / `export.css` — Chart export functionality

## Note

These assets belong to the legacy PHP/CodeIgniter frontend that was part of the original open-source school management system. The Django REST API layer (the main v4 codebase) serves a separate modern frontend. These files are retained for reference and backward compatibility.
