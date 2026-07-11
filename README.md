# Study Shark Dev

This workspace contains the Study Shark web project and a generated Pygbag build for the `study.shark.games` app.

## Project structure

- `study.shark.html` - main HTML page for the Study Shark app
- `index.js` - site JavaScript
- `style.css` - main stylesheet
- `study.shark.games/` - generated Pygbag build directory
  - `build/web/` - browser deployable web app

## Opening the Pygbag web build locally

The generated Pygbag app must be served over HTTP because the runtime uses `fetch()` internally. Open a terminal and run:

```powershell
cd "{root}\study.shark.games\build\web"
python -m http.server 8000
```

Then open in your browser:

```text
http://localhost:8000/index.html
```

## Running the Pygame app locally

To run the `study.shark.games` Pygame app on your machine:

1. Open a terminal.
2. Change into the game directory:

```powershell
cd "{root}\study.shark.games"
```

3. Install Pygame if needed:

```powershell
python -m pip install pygame
```

4. Run the game:

```powershell
python main.py
```

If you are using a virtual environment, activate it before installing or running the game.

## Offline/local support

A local copy of `pythons.js` and `empty.html` has been configured in `study.shark.games/build/web`. The app is now set up to avoid some remote CDN dependencies.

If you need to update or rebuild the Pygbag web package, re-run your Pygbag export or bundler and then verify the local asset paths in `study.shark.games/build/web/index.html`.

## Notes

- `study.shark.games/build/web/index.html` is the main generated page for the Pygbag build
- `study.shark.games/build/web/study.shark.games.apk` and `.tar.gz` are the packaged app archives
- A local HTTP server is required for the app to run correctly
