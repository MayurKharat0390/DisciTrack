# build_files.sh
echo "--- Build Started ---"
python3.12 -m pip install -r requirements.txt
python3.12 manage.py collectstatic --noinput --clear
python3.12 manage.py migrate --noinput
echo "--- Build Successful ---"
