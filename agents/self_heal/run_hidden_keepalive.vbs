Set sh = CreateObject("WScript.Shell")
cmd = """" & WScript.Arguments(0) & """ -NoProfile -ExecutionPolicy Bypass -File """ & WScript.Arguments(1) & """"
sh.Run cmd, 0, False  '0: hidden
