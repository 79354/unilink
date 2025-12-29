## 📁 Project Structure

```
unilink-backend/
├── pyproject.toml       # UV dependency management
├── .env.example         # Environment variables template
├── Dockerfile           # Docker configuration
├── app/
│   ├── main.py          # FastAPI app entry
│   ├── core/
│   │   ├── config.py    # Settings
│   │   ├── database.py  # MongoDB connection
│   │   ├── redis_client.py
│   │   └── security.py  # Auth & JWT
│   ├── models/
│   │   ├── user.py
│   │   ├── post.py
│   │   └── otp.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   ├── s3.py
│   │   ├── otp.py
│   │   └── captions.py
│   └── utils/
│       ├── s3_utils.py
│       └── email_service.py
└── .venv/               # Virtual environment (created by UV)
```