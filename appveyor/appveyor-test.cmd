mkdir testrun
copy .coveragerc testrun
cd testrun
coverage run -m nose.core -v traits --exe
if %errorlevel% neq 0 exit /b %errorlevel%
coverage report
