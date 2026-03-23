# Test Credentials

## Admin
| Username | Password |
|----------|----------|
| admin | admin123 |
| eodenyire | eodenyire |

## Teachers (100 accounts)
| Username pattern | Password |
|-----------------|----------|
| teacher001 → teacher100 | Teacher@1234 |

## Students (100 accounts)
| Username pattern | Password |
|-----------------|----------|
| student001 → student100 | Student@1234 |

## Parents (20 accounts)
| Username pattern | Password |
|-----------------|----------|
| parent001 → parent020 | Parent@1234 |

## Staff (100 accounts)
| Username pattern | Password |
|-----------------|----------|
| staff001 → staff100 | Staff@1234 |

## URLs
- Login: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard
- API Docs: http://localhost:8000/api/docs

## Start the server
```powershell
$env:PYTHONPATH = "."; .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
