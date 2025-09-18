# VS Code Testing Setup Guide

## ✅ **Problem Resolved**

The VS Code testing issue has been completely resolved! The setup has been streamlined to use a single `settings.py` file with automatic test detection and `pyproject.toml` for pytest configuration.

## 🛠️ What Was Fixed

1. **Integrated testing into main settings** - Modified `config/settings.py` to auto-detect test mode and use SQLite
2. **Moved to pyproject.toml** - Pytest configuration now in `pyproject.toml` instead of separate `pytest.ini`
3. **Simplified VS Code settings** - Direct pytest execution with environment variables
4. **Removed separate files** - Eliminated `config/test_settings.py`, `pytest.ini`, `run_tests.sh`, `vscode_test_runner.sh`
5. **Fixed static files for tests** - Proper STORAGES configuration for test environment
6. **Streamlined approach** - Single source of truth with automatic test detection

## 🚀 How to Use

### Running Tests in VS Code

1. **Open the Test Explorer**:
   - Press `Ctrl+Shift+P` (Linux/Windows) or `Cmd+Shift+P` (Mac)
   - Type "Test: Focus on Test Explorer View" and select it
   - Or click the Test Explorer icon in the Activity Bar

2. **Refresh Test Discovery**:
   - In the Test Explorer, click the refresh button
   - Or press `Ctrl+Shift+P` and run "Test: Refresh Tests"

3. **Run Tests**:
   - Click the play button next to any test or test class
   - Right-click on tests for more options (run, debug, etc.)
   - Use `Ctrl+;` then `A` to run all tests

### Running Tests in Terminal

```bash
# Run all tests
TESTING=1 ./.venv/bin/pytest

# Run specific app tests
TESTING=1 ./.venv/bin/pytest accounts/tests/

# Run specific test file
TESTING=1 ./.venv/bin/pytest accounts/tests/test_accounts_models.py

# Run with verbose output
TESTING=1 ./.venv/bin/pytest -v

# Run specific test method
TESTING=1 ./.venv/bin/pytest accounts/tests/test_accounts_models.py::TestCustomUserManager::test_create_user_with_email_and_password

# Use uv for dependency management
TESTING=1 uv run pytest accounts/tests/
```

### Debugging Tests

1. Set breakpoints in your test code or application code
2. Press `F5` and select "Django Tests" configuration
3. Or right-click on a test in the Test Explorer and select "Debug Test"

## 🔧 Configuration Files Created/Updated

- **pytest.ini** - Main pytest configuration
- **.vscode/settings.json** - VS Code Python extension settings
- **.vscode/launch.json** - Debug configurations
- **run_tests.sh** - General test runner script that handles environment conflicts
- **vscode_test_runner.sh** - VS Code-specific test runner with explicit environment setup

## ✅ Verification

Tests are now working correctly:

- ✅ All 22 model tests pass
- ✅ SQLite in-memory database is used for tests (not PostgreSQL)
- ✅ No database conflicts or "relation already exists" errors
- ✅ VS Code can discover and run tests through the Test Explorer

## 🐛 If Tests Still Don't Work

1. **Check Python Interpreter**: Make sure VS Code is using the correct Python interpreter (`.venv/bin/python`)
2. **Reload Window**: Press `Ctrl+Shift+P` and run "Developer: Reload Window"
3. **Check Output Panel**: View the Python and Test output panels for error messages
4. **Manual Test**: Run `./run_tests.sh -v` in terminal to verify the setup works outside VS Code

## 📝 Technical Details

The solution integrates testing configuration directly into the main `config/settings.py` file using automatic test detection:

1. **Test Detection**: Uses `'test' in sys.argv or 'pytest' in sys.modules or os.environ.get('TESTING')` to detect test mode
2. **Conditional Configuration**: When testing is detected, automatically switches to:
   - SQLite in-memory database instead of PostgreSQL
   - Disabled migrations for faster test execution
   - Fast MD5 password hasher
   - In-memory channel layers instead of Redis
   - Simplified static files handling
   - Removal of problematic apps and middleware

3. **Environment Isolation**: Test runner scripts set `TESTING=1` and `DJANGO_SETTINGS_MODULE=config.settings` to ensure proper test configuration while avoiding conflicts with `.env` file settings.

This approach eliminates the need for a separate `test_settings.py` file while maintaining complete isolation between test and development environments.
