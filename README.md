asyncdl
=======

Asyncdl is a tiny library for downloading multipule files asyncronously.

```python
>>> from asyncdl import download_files
>>>
>>> download_files(
>>>     ("https://example.com/file_1", "local/file_1")
>>>     ("https://example.com/file_2", "local/file_2")
>>>     ("https://example.com/file_3", "local/file_3")
>>> )
https://example.com/file_1 [============             ]  113216/242262 B
https://example.com/file_2 [=======                  ]   16508/484524 B
https://example.com/file_3 [====================     ]   96904/121131 B
````
