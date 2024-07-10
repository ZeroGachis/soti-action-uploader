# Github Action Soti Apk Uploader

## Inputs

### `soti-api-url`:

**Required** 'Soti api url'

### `apk-path`:

**Required** 'path of Apk'

### `soti-api-key`:

**Required** 'Soti api key'

### `soti-api-secret`:

**Required** 'Soti api secret'

### `soti-username`:

**Required** 'Soti username'

### `soti-password`:

**Required** 'Soti password'

### `auto-update`:

**Optional** _boolean -> default false_ 'auto update apk version on profile and install it on device link'

### `soti-profile-id`:

**Optional Requiered if `auto-update` is true** 'soti profile name'

### `package-name`:

**Optional Requiered if `auto-update` is true** 'package name'

## Example usage

```yaml
uses: ZeroGachis/github-action-soti-apk-uploader@main
with:
  soti-api-url: "Soti api url"
  apk-path: "Apk path"
  soti-api-key: "Soti api key"
  soti-api-secret: "Soti api secret"
  soti-username: "Soti username"
  soti-password: "Soti password"
  //optional
  auto-update: true
  soti-profile-id: "Soti profile id"
  package-name: "Package name"
```
