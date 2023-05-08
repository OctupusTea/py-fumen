# py-fumen-py

More Python-ish Python implementation of [Knewjade's tetris-fumen](https://github.com/knewjade/tetris-fumen)

Original project: [hsohliyt105's py-fumen](https://github.com/hsohliyt105/py-fumen)

## Usage
```python
from py_fumen_py import *
```

### Module

* **`bold names`** are automatically imported with `from py_fumen_py import *`

|Name|Description|Importable Names|
|:-|:-|:-|
|`action`|Codec for action in a fumen string|`Action`, `ActionCodec`|
|`comment`|Codec for comment in a fumen string |`CommentCodec`|
|`constant`|Constants used in the project|**`FieldConstants`**, `FieldConstants110`, **`FumenStringConstants`**|
|`field`|Playing field object|**`Field`**|
|`fumen_buffer`|Buffer objects for saved data|`FumenBuffer`, `FumenBufferReader`, `FumenBufferWriter`|
|`fumen_codec`|The Fumen codec|**`decode`**, **`encode`**|
|`js_escape`|`escape()` ported from JavaScript|`escape`, `unescape`, `escaped_compare`|
|`operation`|Tetrimino placement object|**`Mino`**, **` Rotation`**, **`Operation`**|
|`page`|Page object|**`Flags`**, **`Refs`**, **`Page`**|
|`quiz`|Quiz object|`Quiz`|

### Example

- Decoding
```python
from py_fumen_py import *

pages = decode('v115@9gQ4EeAtBewhR4CeBtBewhg0Q4CeAtglRpwhi0Aeil?RpwhJeAgWSANxiSASowNE1oo2AzyBUAT5AAA')

for i, page in enumerate(pages):
	print(i)
	print(page.field)
```

- Encoding
```python
from py_fumen_py import *

field = Field(
	field='\n'.join([
		'S_____Z__I',
		'SS___ZZ__I',
		'JS___ZLOOI',
		'JJJ_LLLOOI',
	]),
	garbage='__________'
)
pages = [Page(
	field=field,
	operation=None,
	comment='MKO you say?',
	flags=Flags(),
	refs=Refs())
]
print(encode(pages))
```

## Difference Compared with `tetris-fumen` and `py-fumen`

- Action encoding and decoding are moved to `action`
- Comment encoding and decoding are moved to `comment`
- Added `FieldConstants110` to `constant` to accomodate for Fumen version `110`
- `decoder` and `encoder` are combined into one `fumen-codec` module
- `field` and `inner_field` are combined into one `field` module
- Action, comment and field reading/writing are moved to `fumen_buffer`
- Placement tetrimino `enum` objects are moved to `operation`
- `quiz` works completely differently (based on [this editor](fumen.zui.jp) instead of `tetris-fumen`)
