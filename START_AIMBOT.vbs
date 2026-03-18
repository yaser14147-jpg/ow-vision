Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- [1] GET BASE PATH DYNAMICALLY ---
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")
PathFile = fso.BuildPath(StrPath, "python_path.txt")

' --- [2] FIND PYTHONW.EXE (REFINED BRUTE FORCE) ---
Sub FindPythonW()
    On Error Resume Next
    FoundPy = ""
    
    ' Priority 1: Check if INSTALL_LIBRARIES saved a working path
    If fso.FileExists(PathFile) Then
        Set objFile = fso.OpenTextFile(PathFile, 1)
        SavedPath = Trim(objFile.ReadLine)
        objFile.Close
        If fso.FileExists(SavedPath) Then
            FoundPy = SavedPath
            Exit Sub
        End If
    End If

    ' Priority 2: Check if in PATH directly
    Err.Clear
    WshShell.Run "pythonw.exe --version", 0, True
    If Err.Number = 0 Then FoundPy = "pythonw.exe": Exit Sub

    ' Priority 3: Check common locations (Brute Force)
    Locations = Array("C:\Program Files\Python312\pythonw.exe", _
                      "C:\Program Files\Python311\pythonw.exe", _
                      WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python312\pythonw.exe"), _
                      WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python311\pythonw.exe"), _
                      WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Python\pythoncore-3.14-64\pythonw.exe"), _
                      "C:\Python312\pythonw.exe", _
                      "C:\Python311\pythonw.exe")
    
    For Each Loc In Locations
        If fso.FileExists(Loc) Then FoundPy = Loc: Exit Sub
    Next
    
    ' Priority 4: Try 'pyw.exe' (Official Python Launcher)
    Err.Clear
    WshShell.Run "pyw.exe --version", 0, True
    If Err.Number = 0 Then FoundPy = "pyw.exe": Exit Sub
End Sub

' --- [3] RUN THE SCRIPT ---
If Not fso.FileExists(MainPyPath) Then
    MsgBox "Error: main.py not found at: " & MainPyPath & vbCrLf & _
           "Please extract the zip file correctly.", 16, "File Error"
    WScript.Quit
End If

FindPythonW

If FoundPy <> "" Then
    ' Run main.py hidden
    ' Using double quotes for both python and main.py path
    WshShell.Run """" & FoundPy & """ """ & MainPyPath & """", 0, False
Else
    MsgBox "Could not find Python (pythonw.exe)!" & vbCrLf & _
           "Please run INSTALL_LIBRARIES.bat as Administrator first." & vbCrLf & _
           "Your system seems to have a custom Python installation." & vbCrLf & _
           "Tried common paths but failed.", 16, "Fatal Environment Error"
End If
