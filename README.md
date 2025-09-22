# The LanceApp

This app is made for a certain individual... Marcus Lance Matienzo.
Happy Birthday!

## Run the app

### Flet

Run as a desktop app:

```flet
flet run
```

Run as a web app:

```flet
flet run --web
```

### uv

Run as a desktop app:

```cmd
uv run flet run
```

Run as a web app:

```cmd
uv run flet run --web
```

### Poetry

Install dependencies from `pyproject.toml`:

```cmd
poetry install
```

Run as a desktop app:

```cmd
poetry run flet run
```

Run as a web app:

```cmd
poetry run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/getting-started/).

## Build the app

### Android

```cmd
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```cmd
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```cmd
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```cmd
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```cmd
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).
