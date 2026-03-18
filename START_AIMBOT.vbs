Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- [1] GET BASE PATH DYNAMICALLY ---
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")
PathFile = fso.BuildPath(StrPath, "python_path.txt")

' --- [2] FIND ANY WORKING PYTHON (v10.0 ULTIMATE) ---
Sub FindPythonRunner()
    On Error Resume Next
    FoundPy = ""
    
    ' Priority 1: Check if environment locked a path
    If fso.FileExists(PathFile) Then
        Set objFile = fso.OpenTextFile(PathFile, 1)
        SavedPath = Trim(objFile.ReadLine)
        objFile.Close
        SavedPath = Replace(SavedPath, """", "")
        If fso.FileExists(SavedPath) Then FoundPy = SavedPath : Exit Sub
    End If

    ' Priority 2: Try 'pythonw.exe' in PATH (Best Choice)
    Err.Clear
    WshShell.Run "pythonw.exe --version", 0, True
    If Err.Number = 0 Then FoundPy = "pythonw.exe" : Exit Sub

    ' Priority 3: Fallback to 'python.exe' in PATH (If pythonw is missing)
    Err.Clear
    WshShell.Run "python.exe --version", 0, True
    If Err.Number = 0 Then FoundPy = "python.exe" : Exit Sub

    ' Priority 4: Common Brute Force Scan
    Common = Array("C:\Program Files\Python312", "C:\Program Files\Python313", "C:\Program Files\Python314", _
                   WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python"), _
                   WshShell.ExpandEnvironmentStrings("%LocalAppData%\Python"))
    
    For Each P In Common
        Set Folder = fso.GetFolder(P)
        If Err.Number = 0 Then
            ' Check Root and Subfolders
            CheckFile P & "\pythonw.exe"
            If FoundPy <> "" Then Exit Sub
            CheckFile P & "\python.exe"
            If FoundPy <> "" Then Exit Sub
            
            For Each SubF In Folder.SubFolders
                CheckFile SubF.Path & "\pythonw.exe"
                If FoundPy <> "" Then Exit Sub
                CheckFile SubF.Path & "\python.exe"
                If FoundPy <> "" Then Exit Sub
            Next
        End If
        Err.Clear
    Next
End Sub

Sub CheckFile(Path)
    If fso.FileExists(Path) Then FoundPy = Path
End Sub

' --- [3] LAUNCH ---
FindPythonRunner

If FoundPy <> "" Then
    ' Run main.py hidden if using pythonw, or visible if fallback to python
    WshShell.Run """" & FoundPy & """ """ & MainPyPath & """", 0, False
Else
    MsgBox "Fatal: Python Not Found!" & vbCrLf & "Please run INSTALL_LIBRARIES.bat as Admin.", 16, "Environment Error"
End If
