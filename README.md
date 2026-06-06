# WhatsApp Bulk Message Sender (Excel Integration)

A production-grade, asynchronous automation tool designed to streamline commercial communication by broadcasting personalized messages straight from an Excel database. Built with a modern user interface and engineered for stability and human-like execution.

## 🚀 Key Features
- **Modern Desktop GUI:** Built using `CustomTkinter` for a seamless and responsive user experience.
- **Dynamic Excel Processing:** Powered by `pandas` to read, track, and update delivery logs in real-time.
- **Resilient Web Automation:** Leverages `Selenium WebDriver` with explicit dynamic waits to handle delayed loading or unexpected popups gracefully.
- **Smart Session Persistence:** Uses localized user data directory caching so users only scan the QR code once.
- **Anti-Ban Architecture:** Implements floating randomized delays and hidden automation flags to closely mimic human typing and navigation behavior.
- **Standalone Distribution:** Formatted for instant standalone execution on vanilla Windows environments without requiring Python dependencies.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Libraries:** Selenium, Pandas, Openpyxl, CustomTkinter, Webdriver-Manager
- **Packaging:** Compiled via PyInstaller & Bundled through Inno Setup Pro
