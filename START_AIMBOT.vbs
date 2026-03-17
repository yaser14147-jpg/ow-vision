Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the base path dynamically from the script folder location
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Ensure we are using the correct relative path to main.py
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")

' Check if main.py exists
If fso.FileExists(MainPyPath) Then
    ' Run with pythonw.exe (no window)
    ' Using double quotes for file paths containing spaces
    WshShell.Run "pythonw.exe """ & MainPyPath & """", 0, False
Else
    MsgBox "Error: Could not find main.py at: " & MainPyPath, 16, "File Not Found"
End If
