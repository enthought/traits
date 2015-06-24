"%sdkverpath%" -q -version:"%sdkver%"
call setenv /x64

rem install python packages
pip install --cache-dir c:/egg_cache nose
pip install --cache-dir c:/egg_cache coverage

rem install mayavi
python setup.py develop
