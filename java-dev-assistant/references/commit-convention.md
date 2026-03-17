# Conventional Commits Specification

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Description |
|------|-------------|
| **feat** | A new feature |
| **fix** | A bug fix |
| **docs** | Documentation only changes |
| **style** | Changes that don't affect code meaning (formatting, semicolons, etc) |
| **refactor** | Code change that neither fixes a bug nor adds a feature |
| **perf** | Performance improvement |
| **test** | Adding or correcting tests |
| **chore** | Changes to build process or auxiliary tools |

## Examples

### Feature
```
feat(user): add user authentication

Implement JWT-based authentication for user login.
Supports access token and refresh token.
```

### Bug Fix
```
fix(api): resolve null pointer exception in user service

Check for null before accessing user object.
Add null-safe operations.

Closes #123
```

### Breaking Change
```
feat(api): redesign response format

BREAKING CHANGE: Response format changed from XML to JSON.
Migration guide: docs/migration-v2.md
```

## Best Practices

1. Use present tense ("add feature" not "added feature")
2. Use imperative mood ("move cursor to..." not "moves cursor to...")
3. Don't capitalize first letter
4. No period at the end
5. Keep description under 72 characters
