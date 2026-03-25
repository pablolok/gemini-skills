# Conductor Compliance Audit Skill (Avalonia UI)

A specialized Gemini skill for Avalonia UI compliance reviews.

## What It Checks

- Avalonia MVVM boundaries and view-model discipline
- XAML, bindings, converters, and code-behind maintainability
- theming, styling, accessibility, and cross-platform desktop expectations
- UI responsiveness, threading safety, and resource organization
- automated testing and verification gates for desktop UI changes

## Typical Trigger

Use this when a phase changes Avalonia UI files such as:

- `.axaml` or `.xaml` views and resource dictionaries
- view model or code-behind `.cs` files
- styling, theme, converter, or control files
- Avalonia project files and packaged UI assets

especially when the project contains Avalonia markers like `Avalonia`, `FluentTheme`, `App.axaml`, or `Styles.axaml`.
