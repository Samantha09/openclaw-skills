# Java Testing Guide

## Testing Framework

Use JUnit 5 (Jupiter) for unit tests.

## Test Structure

```java
@Test
@DisplayName("Descriptive test name")
void methodName_scenario_expectedResult() {
    // Arrange - Set up test data and mocks
    
    // Act - Execute the method under test
    
    // Assert - Verify the results
}
```

## Test Naming Convention

Format: `methodName_scenario_expectedResult`

Examples:
- `calculatePrice_validInput_returnsCorrectTotal`
- `processOrder_nullOrder_throwsIllegalArgumentException`
- `getUser_nonExistentUser_returnsEmptyOptional`

## Test Categories

### 1. Positive Tests
- Valid inputs
- Normal operation flow
- Expected successful outcomes

### 2. Edge Cases
- Null inputs
- Empty collections
- Boundary values (Integer.MAX_VALUE, empty strings)

### 3. Exception Tests
- Invalid inputs
- Error conditions
- Expected exceptions

### 4. Integration Points
- External service calls
- Database interactions
- File I/O operations

## Mocking

Use Mockito for mocking dependencies:

```java
@Mock
private UserRepository userRepository;

@BeforeEach
void setUp() {
    MockitoAnnotations.openMocks(this);
}

@Test
void findUser_existingUser_returnsUser() {
    when(userRepository.findById(1L)).thenReturn(Optional.of(user));
    
    User result = service.findUser(1L);
    
    assertEquals(user, result);
    verify(userRepository).findById(1L);
}
```

## Assertions

Use AssertJ for fluent assertions:

```java
import static org.assertj.core.api.Assertions.*;

assertThat(result)
    .isNotNull()
    .hasSize(3)
    .containsExactlyInAnyOrder("a", "b", "c");

assertThatThrownBy(() -> service.process(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessageContaining("input cannot be null");
```

## Coverage Goals

- Line coverage: >= 80%
- Branch coverage: >= 70%
- Critical paths: 100%
