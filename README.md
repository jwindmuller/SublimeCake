# SublimeCake – Run CakePHP 2.x tests inside of Sublime Text 2

This SublimeText 2 plugin  allows you to run the tests defined in the current open file.

## Setup
To be able to run the tests from Sublime Text, you need to tell Sublime where the path to the PHP executable via settings:

    "php_binary_path" : "/usr/local/bin/php"

## Usage

Activate via context menu or using the menu *Tools* → *SublimeCake*

Two keyboard shortcuts are available:

- Control+Option+t = Run current test function (based on current selection).
- Control+Option+Shift+t = Run all tests in the current file.


## TODO

- **Add Other OS support:**
  - Keyboard shortcuts
  - Test
- **Run all app tests:** allow a shortcut to run all tests files at once.

