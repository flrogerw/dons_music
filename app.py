"""Don's Media Archive API.

This module defines the core REST API for managing a personal archive of physical music media
(CDs, Vinyl, Tape) for a user named Don. The API enables storage, retrieval, and search of
media metadata using a lightweight SQLite database and is exposed through documented HTTP endpoints.

Modules Used:
    - flask
    - flask_restx
    - sqlite3
    - pathlib

Key Components:
    - init_db(): Initialize the SQLite database and create the `media` table if it doesn't exist.
    - MediaList: Resource providing GET and POST operations for listing and adding media.
    - MediaSearch: Resource providing GET search functionality for media based on partial matches.
    - MediaResource: Resource for deleting a specific media by its ID.

Endpoints:
    - GET /media/              → List all media
    - POST /media/             → Add a new media
    - GET /media/search        → Search media by title, artist, location, or format
    - DELETE /media/{media_id} → Delete a media object.

Models:
    - media_model: Defines required media fields and format validation.
    - error_request_model: Standard bad request error response format.
    - error_internal_model: Standard internal server error.
    - error_404_model: Standard not found error.
    - post_model: Minimal response model for POST success.
    - delete_model: Minimal response model for DELETE success.

Example Usage:
    Run a Docker container:
        docker-compose up --build
    Run this script directly to start the API server:
        python app.py

Swagger UI:
    Available at http://localhost:3000/

Author:
    Don's BFF
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, render_template, request
from flask_restx import Api, Resource, fields

app = Flask(__name__, template_folder="templates", static_folder="static")
api = Api(app, title="Don's Media Archive API", version='1.1',
          description="Store and search media metadata from Don's collection")
ns = api.namespace('media', description='Media End Points')

DATABASE = 'data/media.db'
VALID_FORMATS = ['CD', 'Vinyl', 'Tape']

# Define the main Media model for creating/updating media records
media_model = api.model('Media', {
    'title': fields.String(
        required=True,
        description="Media title",
        example="Dark Side of the Moon"
    ),
    'artist': fields.String(
        required=True,
        description="Artist name",
        example="Pink Floyd"
    ),
    'location': fields.String(
        required=True,
        description="Storage location",
        example="Shelf Rock"
    ),
    'format': fields.String(
        required=True,
        enum=VALID_FORMATS,
        description="Media format",
        example="Vinyl"
    ),
})

# Model for generic internal/server errors (HTTP 500)
error_internal_model = api.model('Internal_Error', {
    'error': fields.String(
        description="Error message describing what went wrong",
        example="An unexpected error occurred",
    ),
    'code': fields.Integer(
        description="HTTP status code for the error",
        example=500,
    ),
})

# Model for “not found” errors (HTTP 404)
error_404_model = api.model('Not_Found_Error', {
    'error': fields.String(
        description="Error message when resource isn’t found",
        example="Media not found",
    ),
    'code': fields.Integer(
        description="HTTP status code for the error",
        example=404,
    ),
})

# Model for bad request errors (HTTP 400)
error_request_model = api.model('Request_Error', {
    'error': fields.String(
        description="Error message for invalid client input",
        example="Bad Request - Invalid input structure",
    ),
    'code': fields.Integer(
        description="HTTP status code for the error",
        example=400,
    ),
})

# Model for successful POST responses
post_model = api.model('Post', {
    'id': fields.Integer(
        required=True,
        description="Unique identifier of the newly created media record",
        example=1234,
    ),
})

# Model for successful DELETE responses
delete_model = api.model('Delete', {
    'message': fields.String(
        required=True,
        description="Confirmation message after deletion",
        example="Media {media_id} deleted successfully",
    ),
})

def init_db() -> None:
    """Initialize the SQLite database if it does not already exist.

    This function checks whether the database file defined by `DATABASE` exists.
    If it does not, it creates the file and defines the `media` table with the
    following schema:

        - id: Auto-incrementing primary key
        - title: Media title (TEXT, required)
        - artist: Artist name (TEXT, required)
        - location: Storage location (TEXT, required)
        - format: Media format (TEXT, required)

    The function safely closes the database connection after setup.

    """
    if not Path.exists(Path(DATABASE)):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                location TEXT NOT NULL,
                format TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()


@app.route('/custom-docs')
def custom_ui() -> str:
    """Serve the custom Swagger UI documentation page.

    This route overrides the default Flask-RESTX Swagger UI and renders a
    custom `swagger-ui.html` template that can include branding, layout adjustments,
    or additional customization such as logos and headers.

    Returns:
        str: Rendered HTML of the custom Swagger UI page.

    """
    return render_template("swagger-ui.html")


@ns.route('/')
class MediaList(Resource):
    """Resource for listing and adding media to Don's archive.

    Methods:
        get(): Returns a list of all media in the collection.
        post(): Accepts media data and adds a new record to the database.

    """

    @ns.doc(
        description="List all of Don's media.",
        responses={
            200: ("Don's kids college funds in vinyl.", [media_model]),
            400: ('Bad Request.', error_request_model),
            500: ('Internal server error.', error_internal_model),
        },
    )
    def get(self) -> tuple[list[dict], int] | tuple[dict, int]:
        """Retrieve all media stored in the archive.

        Returns:
            200: A list of all media in the collection as dictionaries.
            500: A structured error object if a database or unexpected server error occurs.

        Raises:
            sqlite3.OperationalError: If the database is locked, missing, or corrupted.
            sqlite3.Error: For general SQLite exceptions (e.g. bad SQL syntax).
            Exception: Catch-all for any other runtime errors.

        """
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row

            # Fetch all media from the table
            media = conn.execute('SELECT * FROM media').fetchall()

            # Clean up the connection
            conn.close()

            # Convert rows to dicts and return success
            return [dict(a) for a in media], 200

        except sqlite3.OperationalError as oe:
            # Handle database-related operational failures
            return {"error": f"Database operational error: {oe!s}", "code": 500}, 500

        except sqlite3.Error as db_error:
            # Handle general SQLite-related errors
            return {"error": f"SQLite error: {db_error!s}", "code": 500}, 500

        except Exception as e:
            # Fallback for unexpected exceptions
            print(f"Unexpected error: {e!s}")  # Replace with logging in production
            return {"error": "An unexpected error occurred", "code": 500}, 500

    @ns.doc(
        description="Add a new media to the archive.",
        responses={
            201: ('Media successfully added', post_model),
            400: ('Missing or invalid input fields', error_request_model),
            500: ('Internal server error', error_internal_model),
        },
    )
    @ns.expect(media_model)
    def post(self) -> tuple[dict, int]:
        """Accept a JSON payload to add a new media object to the database.

        Expected fields:
            - title: The media title (string)
            - artist: The artist name (string)
            - location: Physical location of the media (string)
            - format: Media format (must be one of: 'CD', 'Vinyl', 'Tape')

        Returns:
            201: JSON response with new record ID on success.
            400: If required fields are missing or 'format' is invalid.
            500: On database or server errors.

        """
        try:
            # Get and validate input JSON
            data: dict = request.get_json(force=True)

            # Check for valid format
            if data.get("format") not in VALID_FORMATS:
                return {
                    "error": f"Invalid format. Use one of: {', '.join(VALID_FORMATS)}",
                    "code": 400,
                }, 400

            # Insert into database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO media (title, artist, location, format)
                VALUES (?, ?, ?, ?)
            """, (
                data.get('title'),
                data.get('artist'),
                data.get('location'),
                data.get('format'),
            ))
            conn.commit()
            new_id: int = cursor.lastrowid
            conn.close()

        except (KeyError, TypeError) as e:
            print(str(e))  # Should be logged to a centralized logger
            return {
                "error": f"Invalid input structure: {e!s}",
                "code": 400,
            }, 400

        except sqlite3.IntegrityError as ie:
            print(str(ie))  # Should be logged to a centralized logger
            return {
                "error": f"Database integrity error: {ie!s}",
                "code": 500,
            }, 500

        except sqlite3.Error as db_error:
            print(str(db_error))  # Should be logged to a centralized logger
            return {
                "error": f"SQLite error: {db_error!s}",
                "code": 500,
            }, 500

        except Exception as e:
            print(str(e))  # Should be logged to a centralized logger
            return {
                "error": "An unexpected error occurred",
                "code": 500,
            }, 500
        else:
            return {"id": new_id}, 201


@ns.route('/<int:media_id>')
@ns.param('media_id', 'The unique ID of the media')
class MediaResource(Resource):
    """Resource for deleting a specific media by its ID.

    Methods:
        delete(): Deletes the media with the given ID from the archive.

    """

    @ns.doc(
        description="Delete an media by its ID.",
        responses={
            200: ("Deleted successfully", delete_model),
            404: ("Media not found.", error_404_model),
            500: ("Internal server error.", error_internal_model),
        },
    )
    def delete(self, media_id: int) -> tuple[dict, int]:
        """Delete a media by its unique ID.

        Args:
            media_id (int): The ID of the media to delete.

        Returns:
            200: If the media was successfully deleted.
            404: If no media was found with the given ID.
            500: On database or internal error.

        """
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM media WHERE id = ?", (media_id,))
            conn.commit()
            deleted_count = cursor.rowcount
            conn.close()

            if deleted_count == 0:
                return {"error": "Media not found", "code": 404}, 404

        except sqlite3.Error as db_error:
            return {"error": f"SQLite error: {db_error!s}", "code": 500}, 500

        except Exception as e:
            print(str(e))  # Consider logging this
            return {"error": "An unexpected error occurred", "code": 500}, 500
        else:
            return {"message": f"Media {media_id} deleted successfully"}, 200


@ns.route('/search')
class MediaSearch(Resource):
    """Resource for searching Don's music archive.

    Provides a GET endpoint that accepts a query parameter to search media by
    title, artist, location, or format using a case-insensitive partial match.

    Methods:
        get(): Handles search requests and returns matching media or error messages.

    """

    @ns.doc(
        description="Search media by title, artist, location, or format.",
        params={'query': 'Search term for title, artist, location, or format'},
        responses={
            200: ('Medias matching the search term', [media_model]),
            400: ('Missing or invalid query parameter', error_request_model),
            500: ('Internal server error', error_internal_model),
        },
    )
    def get(self) -> tuple[list[dict], int] | tuple[dict, int]:
        """Search Don's media archive using a case-insensitive partial match across the title, artist, location, and format fields.

        Query Parameters:
            - query (str): The search term.

        Returns:
            200: List of matching media.
            400: If the 'query' parameter is missing or invalid.
            500: If a database or server error occurs.

        """
        # Extract the 'query' parameter from the request
        query: str | None = request.args.get('query')

        if not query:
            return {"error": "Missing 'query' parameter", "code": 400}, 400

        like: str = f"%{query}%"

        try:
            # Connect to the database and run a parameterized query
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            results = conn.execute("""
                SELECT * FROM media
                WHERE title LIKE ? OR artist LIKE ? OR location LIKE ? OR format LIKE ?
            """, (like, like, like, like)).fetchall()
            conn.close()

            # Return list of matching results
            return [dict(r) for r in results], 200

        except sqlite3.OperationalError as oe:
            return {"error": f"Database error: {oe!s}", "code": 500}, 500

        except sqlite3.Error as db_error:
            return {"error": f"SQLite error: {db_error!s}", "code": 500}, 500

        except Exception as e:
            print(str(e))  # Ideally log this to a logger
            return {"error": "An unexpected error occurred", "code": 500}, 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3000, debug=False)
