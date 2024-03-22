# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/madreher/Godrick/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                               |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------- | -------: | -------: | ------: | --------: |
| python/godrick/\_\_init\_\_.py     |        0 |        0 |    100% |           |
| python/godrick/communicator.py     |      102 |       10 |     90% |69, 99, 114, 120, 123-129 |
| python/godrick/computeResources.py |      198 |       17 |     91% |9, 12, 23, 25, 30, 35-39, 117, 161, 182, 195, 198, 205, 216 |
| python/godrick/launcher.py         |      187 |        8 |     96% |22, 36, 39, 42, 136, 149, 176, 204 |
| python/godrick/port.py             |       21 |        3 |     86% | 11-12, 21 |
| python/godrick/task.py             |       98 |        8 |     92% |58, 63, 68, 73, 78, 82, 86, 131 |
| python/godrick/workflow.py         |       58 |        8 |     86% |16, 22, 26, 28, 37, 55, 61, 66 |
|                          **TOTAL** |  **664** |   **54** | **92%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/madreher/Godrick/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/madreher/Godrick/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/madreher/Godrick/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/madreher/Godrick/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmadreher%2FGodrick%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/madreher/Godrick/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.