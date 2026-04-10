@echo off

REM Step 1: Convert OSM to NET
netconvert --osm-files kolkata.osm ^
--tls.guess ^
--tls.discard-simple ^
--junctions.join ^
--roundabouts.guess ^
--output-file kolkata.net.xml

REM Step 2: Generate Traffic Routes
python "%SUMO_HOME%\tools\randomTrips.py" ^
-n kolkata.net.xml ^
-r kolkata.rou.xml ^
-e 3600 ^
--period 3 ^
--validate

echo Done!
pause