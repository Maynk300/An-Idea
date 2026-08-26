# An_Idea — Modern Blogging Platform

> A full-featured Django blogging platform where writers share ideas, stories, and insights.

---

## Features

### Core Blogging
- **Create & Edit Posts** — Rich text editor (CKEditor) with code snippet support
- **Auto-Generated Unique Slugs** — Titles automatically become SEO-friendly URLs; duplicates get `-2`, `-3` suffixes
- **Categories & Tags** — Organize content with categories and flexible tagging
- **Draft/Published Workflow** — Write drafts, publish when ready, unpublish anytime
- **Featured Posts** — Highlight important content on the homepage
- **Reading Time & SEO** — Meta tags, Open Graph, Twitter Cards, sitemap.xml, robots.txt

### Engagement
- **Comments** — Authenticated users can comment on published posts
- **Likes** — Toggle likes on posts with real-time count
- **Search** — Full-text search across titles, content, categories, and tags

### User Experience
- **Dark/Light Theme** — Persisted in localStorage with system preference fallback
- **Responsive Design** — Mobile-first, works on all screen sizes
- **Profile Pages** — Public author profiles with published post history
- **Avatar Upload** — Profile pictures with drag-and-drop preview

### Dashboard (Author Panel)
- **My Blogs** — Paginated list of your posts with status badges
- **Create/Edit/Delete** — Full CRUD for your content
- **Publish/Unpublish** — One-click status toggles
- **Categories Management** — View category counts

### Security
- **CSRF Protection** — All forms protected
- **XSS Prevention** — HTML sanitization via Bleach (allowlist-based)
- **Image Validation** — File type and size validation (5MB max, JPEG/PNG/WebP/GIF)
- **Authentication** — Login required for dashboard, comments, likes
- **Authorization** — Users can only edit/delete their own content
- **Secure Defaults** — Production security headers when `DEBUG=False`

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 6.0+ |
| Database | SQLite (development) |
| Frontend | Bootstrap 5.3 (utilities only), Custom CSS |
| Rich Text | django-ckeditor 6.7+ |
| Forms | django-crispy-forms + crispy-bootstrap4 |
| Sanitization | Bleach 6.1+ |
| Image Processing | Pillow 12+ |
| Testing | Django Test Framework (200 tests) |

---

## Project Structure

```
An_Idea/
├── accounts/              # User profiles, authentication
│   ├── models.py          # Profile model (avatar, bio)
│   ├── views.py           # Profile view/edit
│   ├── forms.py           # ProfileForm
│   ├── signals.py         # Auto-create Profile on User creation
│   └── tests.py
├── assignments/           # Static content models
│   ├── models.py          # About, SocialLinks
│   └── admin.py
├── blogs/                 # Core blogging app
│   ├── models.py          # Blog, Category, Tag, Comment, Like
│   ├── views.py           # Public views (list, detail, search, comments, likes)
│   ├── forms.py           # BlogForm, CommentForm, HTML sanitization
│   ├── sitemaps.py        # SEO sitemaps
│   ├── context_processors.py  # Global template context
│   ├── admin.py           # Custom admin with prepopulated slug
│   └── tests.py           # 93 tests
├── dashboards/            # Author dashboard
│   ├── views.py           # CRUD for blogs, publish/unpublish
│   ├── urls.py
│   └── tests.py           # 43 tests
├── Blog_main/             # Project settings
│   ├── settings.py        # Environment-based config
│   ├── urls.py            # Root URLconf
│   ├── views.py           # Home, auth (register/login/logout)
│   └── forms.py           # RegistrationForm
├── templates/             # All templates
│   ├── base.html          # Layout with theme toggle, navbar, footer
│   ├── dashboard/         # Dashboard templates
│   ├── accounts/          # Profile templates
│   └── blogs/             # Comment edit template
├── static/                # Static assets
│   ├── css/blog.css       # Custom design system
│   └── images/
├── media/                 # User uploads (ignored by git)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .gitignore
└── manage.py
```

---

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd An_Idea

# 2. Create and activate virtual environment
python -m venv env
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your values (see Environment Variables below)

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (optional, for admin access)
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

---

## Environment Variables

Create a `.env` file from `.env.example`:

```env
# Django Settings
# Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=your-secret-key-here

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=True

# Comma-separated list of allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Optional: Comma-separated list of CSRF trusted origins for production
# CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Production Checklist (when `DEBUG=False`)
- Set a strong `SECRET_KEY`
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS` for your domain
- Set `CSRF_TRUSTED_ORIGINS` if using HTTPS
- Use a production database (PostgreSQL recommended)
- Configure static/media file serving (nginx, cloud storage)
- Use HTTPS with valid certificates

---

## Database Migrations

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check for pending migrations
python manage.py makemigrations --check --dry-run
```

---

## Running Locally

```bash
# Development server with auto-reload
python manage.py runserver

# Custom port
python manage.py runserver 8001

# Access from network (use with caution)
python manage.py runserver 0.0.0.0:8000
```

---

## Running Tests

```bash
# All tests (200 tests)
python manage.py test

# Specific app
python manage.py test blogs.tests
python manage.py test dashboards.tests
python manage.py test accounts.tests

# Specific test class
python manage.py test blogs.tests.BlogModelTest

# Specific test method
python manage.py test blogs.tests.BlogModelTest.test_blog_auto_generate_slug_from_title

# Verbose output
python manage.py test -v 2
```

---

## Screenshots

<!-- Add screenshots here -->
| Home Page | Dashboard | Blog Detail |
|-----------|-----------|-------------|
| ![Home](docs/screenshots/home.png) | ![Dashboard](docs/screenshots/dashboard.png) | ![Blog Detail](docs/screenshots/blog-detail.png) |

---

## Known Limitations

- **django-ckeditor Warning**: The project uses `django-ckeditor>=6.7.3` which bundles CKEditor 4.22.1. Django's system check shows a warning that CKEditor 4 is no longer supported and has unfixed security issues. This is a known limitation; migration to CKEditor 5 (via `django-ckeditor-5`) is planned for a future release.
- **SQLite Only**: Currently configured for SQLite. Production deployments should switch to PostgreSQL.
- **Single-Process**: No async support, Celery, or Redis integration.

---

## Future Improvements

- [ ] Migrate to CKEditor 5 / django-ckeditor-5
- [ ] Add PostgreSQL support with docker-compose for local dev
- [ ] Implement email notifications for comments/likes
- [ ] Add RSS/Atom feed generation
- [ ] Implement post series/collections
- [ ] Add Markdown support alongside rich text
- [ ] Image optimization (WebP conversion, thumbnails)
- [ ] Add view counting and analytics
- [ ] Implement draft auto-save
- [ ] Add collaborative editing support

---

## License

This project is licensed under the MIT License.

---

## Author

**Mayank Saini** — [GitHub](https://github.com/mayanksaini) • [LinkedIn](https://linkedin.com/in/mayanksaini)

Built with ❤️ using Django.