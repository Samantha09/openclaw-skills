# Java Style Guide

## General Principles

1. Follow existing project conventions
2. Use meaningful names
3. Keep methods small and focused
4. Prefer immutability
5. Document public APIs

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `UserService`, `OrderProcessor` |
| Methods | camelCase | `getUserById()`, `processOrder()` |
| Variables | camelCase | `userCount`, `orderList` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Packages | lowercase | `com.company.service` |

## Code Formatting

### Indentation
- Use 4 spaces (no tabs)
- Continuation indent: 8 spaces

### Braces
- Opening brace on same line
- Closing brace on new line

```java
if (condition) {
    doSomething();
} else {
    doSomethingElse();
}
```

### Line Length
- Maximum 120 characters
- Break long lines at logical points

## Imports

- No wildcard imports
- Group imports: java, javax, org, com
- Static imports last

```java
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.company.project.model.User;
```

## Documentation

### Javadoc

```java
/**
 * Brief description of the method.
 *
 * @param paramName description of parameter
 * @return description of return value
 * @throws ExceptionType when this exception occurs
 */
```

### TODO Comments

```java
// TODO: Brief description of what needs to be done
// TODO(author): Description with assignee
```

## Best Practices

1. **Null Safety**: Use Optional instead of null
2. **Collections**: Use interfaces (List, Set, Map) for declarations
3. **Streams**: Prefer Stream API for collection operations
4. **Exceptions**: Use checked exceptions for recoverable errors
5. **Logging**: Use SLF4J with appropriate log levels
