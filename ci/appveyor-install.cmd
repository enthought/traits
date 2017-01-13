"%sdkverpath%" -q -version:"%sdkver%"
call setenv /x64

pip install -r %REQUIREMENTS%
python setup.py develop
