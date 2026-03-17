Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- [1] GET BASE PATH DYNAMICALLY ---
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")

' --- [2] FIND PYTHONW.EXE LOCALLY IF NOT IN PATH ---
Sub FindPythonW()
    On Error Resume Next
    ' Try common locations
    Locations = Array("pythonw.exe", _
                      "C:\Program Files\Python312\pythonw.exe", _
                      "C:\Program Files\Python311\pythonw.exe", _
                      WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python312\pythonw.exe"), _
                      WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python311\pythonw.exe"))
    
    FoundPy = ""
    For Each Loc In Locations
        If Loc = "pythonw.exe" Then
            ' Check if it's in PATH
            Err.Clear
            WshShell.Run Loc & " --version", 0, True
            If Err.Number = 0 Then FoundPy = Loc: Exit For
        Else
            If fso.FileExists(Loc) Then FoundPy = Loc: Exit For
        End If
    Next
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
    MsgBox "Error: pythonw.exe not found! Please run INSTALL_LIBRARIES.bat first.", 16, "Environment Error"
End If
