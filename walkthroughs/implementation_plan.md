# Plan: Add Comprehensive Application Tests

Add a robust suite of unit and logic tests to ensure application stability, covering database management, utilities, and core services.

## Proposed Changes

### Tests Component

Summary: Adding new test files to the `tests/` directory to cover previously untested areas.

#### [NEW] [test_config_manager_logic.py](file:///e:/NimaTechVibeCoding/NimaStartUpSocial/tests/test_config_manager_logic.py)

- Test `ConfigManager.load()` with missing files.
- Test `ConfigManager.save()` and verify JSON content.
- Test `ConfigManager.export_shortcuts()` and `import_shortcuts()`.

#### [NEW] [test_path_utils_robust.py](file:///e:/NimaTechVibeCoding/NimaStartUpSocial/tests/test_path_utils_robust.py)

- Test `PathUtils.get_data_dir()` behavior in dev vs frozen mode (mocking).
- Test path normalization.

#### [NEW] [test_strings_logic.py](file:///e:/NimaTechVibeCoding/NimaStartUpSocial/tests/test_strings_logic.py)

- Test `Strings.get()` with various keys.
- Test Arabic/English toggle logic if applicable.

#### [NEW] [test_catalog_logic.py](file:///e:/NimaTechVibeCoding/NimaStartUpSocial/tests/test_catalog_logic.py)

- Test `SiteCatalog.normalize()` for various URLs and names.
- Test shortcut categorization logic.

#### [NEW] [test_browser_logic.py](file:///e:/NimaTechVibeCoding/NimaStartUpSocial/tests/test_browser_logic.py)

- Test browser detection logic (mocking `os.path.exists`).

## Verification Plan

### Automated Tests

- Run `python -m unittest discover tests` to execute all tests.
- Individual tests can be run via `python tests/test_filename.py`.

### Manual Verification

- None required for pure logic tests.
