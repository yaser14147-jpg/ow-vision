Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' --- [1] GET BASE PATH DYNAMICALLY ---
StrPath = fso.GetParentFolderName(WScript.ScriptFullName)
MainPyPath = fso.BuildPath(StrPath, "ow-vision\scripts\main.py")
PathFile = fso.BuildPath(StrPath, "python_path.txt")

' --- [2] FIND PYTHONW.EXE (ULTIMATE DEEP SEARCH v8.0) ---
Sub FindPythonW()
    On Error Resume Next
    FoundPy = ""
    
    ' Priority 1: Check if INSTALL_LIBRARIES saved a working path
    If fso.FileExists(PathFile) Then
        Set objFile = fso.OpenTextFile(PathFile, 1)
        SavedPath = Trim(objFile.ReadLine)
        objFile.Close
        ' Remove any quotes if they accidentally got saved
        SavedPath = Replace(SavedPath, """", "")
        If fso.FileExists(SavedPath) Then
            FoundPy = SavedPath
            Exit Sub
        End If
    End If

    ' Priority 2: Check if 'pythonw.exe' is in PATH (Universal)
    Err.Clear
    WshShell.Run "pythonw.exe --version", 0, True
    If Err.Number = 0 Then FoundPy = "pythonw.exe": Exit Sub

    ' Priority 3: Check common manual locations (Recursive Discovery)
    Dim CommonPaths
    CommonPaths = Array("C:\Program Files\Python312", "C:\Program Files\Python313", "C:\Program Files\Python314", _
                        WshShell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python"), _
                        WshShell.ExpandEnvironmentStrings("%LocalAppData%\Python"), _
                        "C:\Python312", "C:\Python311")
    
    For Each RootPath In CommonPaths
        If fso.FolderExists(RootPath) Then
            ' Check main folder
            If fso.FileExists(fso.BuildPath(RootPath, "pythonw.exe")) Then 
                FoundPy = fso.BuildPath(RootPath, "pythonw.exe")
                Exit Sub
            End If
            ' Scan subfolders
            Set RootFolder = fso.GetFolder(RootPath)
            For Each SubF In RootFolder.SubFolders
                TestFile = fso.BuildPath(SubF.Path, "pythonw.exe")
                If fso.FileExists(TestFile) Then
                    FoundPy = TestFile
                    Exit Sub
                End If
            Next
        End If
    Next
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
    ' Force use of FoundPy as the absolute runner
    WshShell.Run """" & FoundPy & """ """ & MainPyPath & """", 0, False
Else
    MsgBox "Fatal Error: Could not find Python (pythonw.exe)!" & vbCrLf & _
           "Your system seems to have a custom Python installation." & vbCrLf & _
           "Please run INSTALL_LIBRARIES.bat as Administrator once to repair your environment.", 16, "Fatal Environment Error"
End If
