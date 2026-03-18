Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- [1] GET BASE PATH DYNAMICALLY ---
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")
PathFile = fso.BuildPath(StrPath, "python_path.txt")
InstallerPath = fso.BuildPath(StrPath, "INSTALL_LIBRARIES.bat")

' --- [2] FIND PYTHON (v12.0 MASTER ULTIMATE) ---
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

    ' Priority 2: Check in PATH directly
    If FoundPy = "" Then
        Err.Clear
        WshShell.Run "pythonw.exe --version", 0, True
        If Err.Number = 0 Then FoundPy = "pythonw.exe"
    End If

    ' Priority 3: Fallback check
    If FoundPy = "" Then
        Err.Clear
        WshShell.Run "python.exe --version", 0, True
        If Err.Number = 0 Then FoundPy = "python.exe"
    End If

    ' --- [3] LAUNCH OR REPAIR ---
    If FoundPy <> "" Then
        ' Force the working directory (CWD) to the script path
        ' This ensures FOV and external configs/models are loaded properly
        WshShell.CurrentDirectory = StrPath
        WshShell.Run """" & FoundPy & """ """ & MainPyPath & """", 0, False
    Else
        Ans = MsgBox("Fatal: Python not found!" & vbCrLf & _
                     "Run Auto-Repair Tool (Installer) v12.0 now?", 36, "Environment Error")
        If Ans = 6 Then ' If Yes
            WshShell.Run "cmd /c """ & InstallerPath & """", 1, False
        End If
    End If
End Sub

' Start everything
If Not fso.FileExists(MainPyPath) Then
    MsgBox "Error: main.py missing at: " & MainPyPath, 16, "File Error"
    WScript.Quit
End If

FindAndLaunch
