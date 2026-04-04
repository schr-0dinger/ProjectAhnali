---
tags: [ahnali, capabilities, deep-linking]
---

# Deep Linking

> [!abstract] Handle launch URIs
> Read the URI that launched your app and respond accordingly.

## Getting the launch URI

```python
uri = deep_link_get("https://default.example.com")
uri = get_deep_link("https://default.example.com")  # alias
```

Maps to `DeepLinkHelper.getLaunchUri(Activity, String) → String`. Returns the launch URI, or the fallback if the app wasn't launched via a deep link.

## Error surface

```python
error = deep_link_error()
error = get_deep_link_error()  # alias
```

Maps to `DeepLinkHelper.getLaunchUriError(Activity) → int`.

## Capability

```python
app_config(uses=[Caps.DeepLinking])
```

Aliases: `Caps.DeepLink`, `Caps.Deep Links`. No manifest permissions needed — deep link handling is configured through intent filters in the manifest.

## Learn more

- Capabilities overview: [[40 - Capabilities/01 - Overview]]
- Sharing and intents: [[40 - Capabilities/07 - Sharing and Intents]]
