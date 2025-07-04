# YT-Downloader-Pro

YT-Downloader-Pro is a simple, easy-to-use YouTube downloader application for macOS. It allows you to download videos and playlists in both MP4 and MP3 formats.

## Features

- Download single videos or entire playlists.
- Choose between MP4 (video) and MP3 (audio) formats.
- Simple and intuitive user interface.
- Progress bar to monitor download status.
- Built-in error handling.

## Installation

To use YT-Downloader-Pro, you can download the latest release from the [releases page](https://github.com/your-username/yt-dl/releases). Once downloaded, simply move the `YT-Downloader-Pro.app` file to your `Applications` folder.

## How to Use

1.  Launch the YT-Downloader-Pro application.
2.  Copy the URL of the YouTube video or playlist you want to download.
3.  Paste the URL into the input field.
4.  Click "Browse" to select a download location (defaults to your Downloads folder).
5.  Click "Download MP4" or "Download MP3" to start the download.

## Development

To contribute to YT-Downloader-Pro or run it from the source, follow these steps:

### Prerequisites

- Python 3
- `pip` (Python package installer)

### Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/yt-dl.git
    cd yt-dl
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: A `requirements.txt` file does not currently exist. You will need to create one with the following content:)*

    ```
    ttkbootstrap
    yt-dlp
    ```

4.  **Run the application:**

    ```bash
    python downloader_nannipy.py
    ```

### Building the Application

To build the `.app` bundle, you will need to install `pyinstaller`:

```bash
pip install pyinstaller
```

Then, run the following command:

```bash
pyinstaller YT-Downloader-Pro.spec
```

The bundled application will be located in the `dist` directory.

## Future Updates

Here are some ideas for future updates:

-   **Video Quality Selection:** Allow users to choose the video quality (e.g., 720p, 1080p, 4K).
-   **Download Queue:** Implement a queue to manage multiple downloads.
-   **Thumbnail Preview:** Display a thumbnail of the video before downloading.
-   **Localization:** Add support for multiple languages.
-   **Cross-Platform Support:** Make the application available for Windows and Linux.