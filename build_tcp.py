import sys, json
import sim

# Let's craft tcp.man with precise grid coordinates
man_code = """
+-+      +-+
|I|      |O|
+-+      +-+
 v        ^
 v        ^
+------------------------+       +----+
|@                       |>----->|@rsv|
|                        |<-----<|^sr<|
+------------------------+       +----+
"""

