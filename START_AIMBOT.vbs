Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- [1] GET BASE PATH DYNAMICALLY ---
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")
PathFile = fso.BuildPath(StrPath, "python_path.txt")
InstallerPath = fso.BuildPath(StrPath, "INSTALL_LIBRARIES.bat")

' --- [2] FIND PYTHON (v11.5 SMART REPAIR) ---
Sub FindAndLaunch()
    On Error Resume Next
    FoundPy = ""
    
    ' Priority 1: Check Locked Path
    If fso.FileExists(PathFile) Then
        Set objFile = fso.OpenTextFile(PathFile, 1)
        SavedPath = Replace(Trim(objFile.ReadLine), """", "")
        objFile.Close
        If fso.FileExists(SavedPath) Then FoundPy = SavedPath
    End If

    ' Priority 2: Try standard command
    If FoundPy = "" Then
        Err.Clear
        WshShell.Run "pythonw.exe --version", 0, True
        If Err.Number = 0 Then FoundPy = "pythonw.exe"
    End If

    ' Priority 3: Try fallback
    If FoundPy = "" Then
        Err.Clear
        WshShell.Run "python.exe --version", 0, True
        If Err.Number = 0 Then FoundPy = "python.exe"
    End If

    ' --- [3] LAUNCH OR REPAIR ---
    If FoundPy <> "" Then
        WshShell.Run """" & FoundPy & """ """ & MainPyPath & """", 0, False
    Else
        Ans = MsgBox("Fatal: Python not detected!" & vbCrLf & _
                     "Would you like to run the Auto-Repair Tool (Installer) now?", 36, "Environment Error")
        If Ans = 6 Then ' If Yes
            WshShell.Run "cmd /c """ & InstallerPath & """", 1, False
        End If
    End If
End Sub

' --- START ---
If Not fso.FileExists(MainPyPath) Then
    MsgBox "Error: main.py not found!", 16, "File Error"
    WScript.Quit
End If

FindAndLaunch
