# Don’s Music Archive API

A simple RESTful API to help Don catalog and search his enormous collection of CDs and records — so you can finally play the right media when I visit.

---

## Problem Statement

Don is passionate about physical media and owns thousands of media in various formats: CDs, vinyl records, and cassettes. However, locating a specific media is a challenge due to the sheer size of his collection. For his birthday, you’re building him a personal archive system that:

- Stores media metadata (title, artist, location, format)
- Provides an easy-to-use API to add and search media
- Requires no SQL knowledge (Don is a frontend dev)
- Uses persistent storage
- Offers clear documentation for future use

---

## Solution Approach

I implemented a lightweight **Python Flask API** using:

| Tech Stack      | Reason for Choice |
|----------------|-------------------|
| **Python**      | Simple, readable, and powerful for quick prototyping and production-ready APIs |
| **Flask**       | Minimal, flexible microframework ideal for small-scale APIs |
| **Flask-RESTX** | Automatically generates Swagger UI documentation and enforces models/validation |
| **SQLite**      | File-based database requiring no server setup, perfect for local personal use |

This approach allows Don to call REST endpoints, search his collection, and even extend it later — all without needing a UI or SQL skills.
* Personally I would have used Node.js for this but you guys use Python, so I figured I should do it that way.
* Since it is only for my 'besty' Don, the only input 'cleansing' is done with the defined schema.  In the real world the input should be sanitized. 
* Since this is only for Don, Most non-critical errors I dump to the screen.  In a real world I would log them and return a generic error to the client.
* The search query is a very basic LIKE query against all the columns, but without a UI it could get messy.
---

## Sample Data
The database comes preloaded with 500 media objects for searching.

## Requirements

- Python 3.11+
- pip

> If using Docker (recommended), these are bundled automatically.

### Python Dependencies

All listed in `requirements.txt`:

```
aniso8601==10.0.1
attrs==25.3.0
blinker==1.9.0
click==8.1.8
Flask==3.1.0
flask-restx==1.3.0
importlib_metadata==8.7.0
importlib_resources==6.5.2
itsdangerous==2.2.0
Jinja2==3.1.6
jsonschema==4.23.0
jsonschema-specifications==2025.4.1
MarkupSafe==3.0.2
pytz==2025.2
referencing==0.36.2
rpds-py==0.24.0
ruff==0.11.8
typing_extensions==4.13.2
Werkzeug==3.1.3
zipp==3.21.0
```

---

## API Functions

### `GET /media/`
Return all media in the archive.
```json
[{
  "title": "The Wall",
  "artist": "Pink Floyd",
  "location": "SA3",
  "format": "Vinyl"
},
{
  "title": "Song Remains the Same",
  "artist": "Led Zepplin",
  "location": "Z2",
  "format": "Vinyl"
}]
```

### `POST /media/`
Add a new media. Requires:

```json
{
  "title": "The Wall",
  "artist": "Pink Floyd",
  "location": "Shelf A3",
  "format": "Vinyl"
}
```

Formats allowed: `CD`, `Vinyl`

### `GET /media/search?query=Floyd`
Search for media where the title, artist, location, or format match the given keyword.

---

## API Documentation

Swagger UI is automatically generated at:

```
http://localhost:3000/
```

You can test requests, view schemas, and see response codes here.

---

## How to Run

### Option 1: Using Docker (Recommended)

```bash
docker compose up --build
```

Then open: [http://localhost:3000](http://localhost:5000)

> All media data will be persisted in the `data/` folder.

### Option 2: Run Locally with Python

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:

   ```bash
   python app.py
   ```

---

## Example cURL

```bash
curl -X POST http://localhost:5000/media/ \
  -H "Content-Type: application/json" \
  -d '{"title":"OK Computer", "artist":"Radiohead", "location":"Shelf B2", "format":"CD"}'
```

---

## Folder Structure

```
don-archive/
├── app.py                # Flask application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image
├── docker-compose.yml    # Service and volume config
└── data/                 # Persistent SQLite storage (auto-created)
```

---

## Future Improvements

- Add Image-to-Image, Text-to Image-search
- Add more metadata (genre, condition, etc...)
- Provide optional image uploads for media covers
- Convert to Mobile app... oh wait I did already.

---

## License

MIT — free to use, hack, and remix.

---

Built with ❤️ for Don and his glorious music collection.
