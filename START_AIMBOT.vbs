Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- [1] GET BASE PATH DYNAMICALLY ---
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")

' --- [2] FIND PYTHONW.EXE (REFINED BRUTE FORCE) ---
Sub FindPythonW()
    On Error Resume Next
    FoundPy = ""
    
    ' Priority 1: Check if in PATH directly
    Err.Clear
    WshShell.Run "pythonw.exe --version", 0, True
    If Err.Number = 0 Then FoundPy = "pythonw.exe": Exit Sub

    ' Priority 2: Check common locations
    Locations = Array("C:\Program Files\Python312\pythonw.exe", _
                      "C:\Program Files\Python311\pythonw.exe", _
                      "C:\Program Files\Python310\pythonw.exe", _
                      WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python312\pythonw.exe"), _
                      WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python311\pythonw.exe"), _
                      WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python310\pythonw.exe"), _
                      "C:\Python312\pythonw.exe", _
                      "C:\Python311\pythonw.exe")
    
    For Each Loc In Locations
        If fso.FileExists(Loc) Then FoundPy = Loc: Exit Sub
    Next
    
    ' Priority 3: Try 'pyw.exe' (Python Launcher)
    Err.Clear
    WshShell.Run "pyw.exe --version", 0, True
    If Err.Number = 0 Then FoundPy = "pyw.exe": Exit Sub
End Sub

' --- [3] RUN THE SCRIPT ---
If Not fso.FileExists(MainPyPath) Then
    MsgBox "Error: main.py not found at: " & MainPyPath, 16, "File Error"
    WScript.Quit
End If

FindPythonW

If FoundPy <> "" Then
    ' Run main.py hidden
    ' Using double quotes for both python and main.py path
    WshShell.Run """" & FoundPy & """ """ & MainPyPath & """", 0, False
Else
    MsgBox "Python was not found on your system!" & vbCrLf & _
           "Please run INSTALL_LIBRARIES.bat as Administrator first." & vbCrLf & _
           "If you already did, restart your PC and try again.", 16, "Python Not Found"
End If
