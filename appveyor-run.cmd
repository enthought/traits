:: Execute etstool operation for every tookit in the argument list
:: Options
:: %1 -- operation
:: %2 -- runtime
::
::
SETLOCAL EnableDelayedExpansion

SET counter=0

FOR %%x IN (%*) DO (
SET /A counter=!counter! + 1
IF !counter! EQU 1 SET operation=%%x
IF !counter! EQU 2 SET runtime=%%x
IF !counter! GTR 2 CALL edm run -- python etstool.py !operation! --runtime=!runtime! || GOTO error
)
GOTO end

:error:
ENDLOCAL
EXIT /b %ERRORLEVEL%

:end:
ENDLOCAL
ECHO.Done
