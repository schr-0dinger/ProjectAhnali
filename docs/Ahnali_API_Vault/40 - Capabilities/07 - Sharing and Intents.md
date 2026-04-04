---
tags: [ahnali, capabilities, sharing, intents]
---

# Sharing and Intents

> [!abstract] Share content and open external apps
> Share text and files through the Android share sheet, or open URIs in external apps.

## Sharing text

```python
share_text("Check this out!", chooser_title="Share via")
share("Check this out!", chooser_title="Share via")  # alias
result = share_text_result(text, chooser_title="Share via")
error = share_text_error(text, chooser_title="Share via")
```

## Sharing files

```python
share_file("/path/to/file.pdf", "application/pdf", chooser_title="Share")
result = share_file_result(path, mime_type, chooser_title)
error = share_file_error(path, mime_type, chooser_title)
```

## Opening URIs

```python
open_external("https://example.com")
open_uri("https://example.com")  # alias
result = open_external_result(uri)
error = open_external_error(uri)
```

## Capability

```python
app_config(uses=[Caps.Sharing])
```

Aliases: `Caps.Intents`, `Caps.Share`. No manifest permissions needed — the share sheet and intent system handle access control.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Clipboard: [[40 - Capabilities/08 - Clipboard]]
- Deep linking: [[40 - Capabilities/10 - Deep Linking]]
