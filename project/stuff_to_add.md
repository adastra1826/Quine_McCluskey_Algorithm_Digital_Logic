Input like this:
Minterm = 0,1,2,5,6,7,8,9,10,14
DontCare =
Variable = a,b,c,d,e

"""
Starting data:
[[0, '', 0, '', 0, '', 1],
 [0, '', 0, '', 1, '', 0],
 [0, '', 1, '', 0, '', 'x'],
 [0, '', 1, '', 1, '', 1],
 [1, '', 0, '', 0, '', 'x'],
 [1, '', 0, '', 1, '', 0],
 [1, '', 1, '', 0, '', 1],
 [1, '', 1, '', 1, '', 0]]

Traceback (most recent call last):
  File "/Users/admin/Library/Mobile Documents/com~apple~CloudDocs/Documents/VSC/Projects/Quine_McCluskey_Algorithm_Digital_Logic/project/./quine_mccluskey.py", line 214, in <module>
    parse_options()
    ~~~~~~~~~~~~~^^
  File "/Users/admin/Library/Mobile Documents/com~apple~CloudDocs/Documents/VSC/Projects/Quine_McCluskey_Algorithm_Digital_Logic/project/./quine_mccluskey.py", line 60, in parse_options
    inputData: List[List[Any]] = sanitize_input(inputFilePath)
                                 ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/Users/admin/Library/Mobile Documents/com~apple~CloudDocs/Documents/VSC/Projects/Quine_McCluskey_Algorithm_Digital_Logic/project/sanitize_qm_input.py", line 54, in sanitize_input
    raise ValueError(f"DEBUG: Too many input rows.")
ValueError: DEBUG: Too many input rows.
admin@MBA project % 

ADD SPACE HANDLING
"""